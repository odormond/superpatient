#! /usr/bin/env python2
# coding:UTF-8

import os
import sys
import datetime
import traceback

sys.path.insert(0, os.path.dirname(__file__))

try:
    import Tkinter as tk
    import tkMessageBox

except:
    tkMessageBox.showwarning("Error", "Tkinter is not correctly installed !")
    sys.exit()

try:
    import bp_connect
except:
    tkMessageBox.showwarning("Missing file", "bp_connect.py is missing")
    sys.exit()

try:
    import bp_custo
    from bp_custo import windows_title, errors_text, buttons_text, menus_text, labels_text
except:
    tkMessageBox.showwarning("Missing file", "bp_custo.py is missing")
    sys.exit()

try:
    import bp_Dialog
except:
    tkMessageBox.showwarning("Missing file", "bp_Dialog.py is missing")
    sys.exit()

try:
    from bp_widgets import ListboxWidget, EntryWidget, OptionWidget
except:
    tkMessageBox.showwarning("Missing file", "bp_widgets.py is missing")
    sys.exit()

try:
    from dateutil.parser import parse as du_parse, parserinfo
except:
    tkMessageBox.showwarning(u"Missing dependency", u"The dateutil module is missing")
    sys.exit()


class FrenchParserInfo(parserinfo):
    MONTHS = [(u'jan', u'janvier'), (u'fév', u'février'), (u'mar', u'mars'), (u'avr', u'avril'), (u'mai', u'mai'), (u'jui', u'juin'), (u'jul', u'juillet'), (u'aoû', u'août'), (u'sep', u'septembre'), (u'oct', u'octobre'), (u'nov', u'novembre'), (u'déc', u'décembre')]
    WEEKDAYS = [(u'Lun', u'Lundi'), (u'Mar', u'Mardi'), (u'Mer', u'Mercredi'), (u'Jeu', u'Jeudi'), (u'Ven', u'Vendredi'), (u'Sam', u'Samedi'), (u'Dim', u'Dimanche')]
    HMS = [(u'h', u'heure', u'heures'), (u'm', u'minute', u'minutes'), (u's', u'seconde', u'secondes')]
    JUMP = [u' ', u'.', u',', u';', u'-', u'/', u"'", u"le", u"er", u"ième"]

datesFR = FrenchParserInfo(dayfirst=True)
MIN_DATE = datetime.date(1900, 1, 1)  # Cannot strftime before that date


def parse_date(s):
    d = du_parse(s, parserinfo=datesFR).date()
    if d < MIN_DATE:
        raise ValueError("Date too old")
    return d

try:
    import MySQLdb
except:
    tkMessageBox.showwarning("Error", "Module mysqldb is not correctly installed !")
    sys.exit()

try:
    db = MySQLdb.connect(host=bp_connect.serveur, user=bp_connect.identifiant, passwd=bp_connect.secret, db=bp_connect.base, charset='latin1')
except:
    tkMessageBox.showwarning("MySQL", "Cannot connect to database")
    sys.exit()

cursor = db.cursor()


class apropos(bp_Dialog.Dialog):
    def body(self, master):
        self.title(windows_title.apropos)
        self.geometry('+350+250')
        tk.Label(master, text=labels_text.apropos_description, font=("Helvetica", 13, 'bold')).grid(row=0, column=0, sticky=tk.W)


class licence(bp_Dialog.Dialog):
    def body(self, master):
        self.title(windows_title.licence)
        self.geometry('+350+250')
        tk.Label(master, text=labels_text.licence_description, font=("Helvetica", 13, 'bold')).grid(row=0, column=0, sticky=tk.W)


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        if (sys.platform != 'win32') and hasattr(sys, 'frozen'):
            self.tk.call('console', 'hide')

        self.option_add('*font', 'Helvetica -15')
        self.title(windows_title.compta)

        menubar = tk.Menu(self)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=menus_text.about, command=lambda: apropos(self))
        helpmenu.add_command(label=menus_text.licence, command=lambda: licence(self))

        menubar.add_cascade(label=menus_text.help, menu=helpmenu)
        self.config(menu=menubar)

        try:
            cursor.execute("SELECT therapeute FROM therapeutes ORDER BY therapeute")
            therapeutes = ['Tous'] + [t for t, in cursor]
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            sys.exit(1)

        # Top block: select what to display
        today = datetime.date.today()
        month_end = datetime.date(today.year, today.month, 1) - datetime.timedelta(days=1)
        last_month = datetime.date(month_end.year, month_end.month, 1)
        self.therapeute = OptionWidget(self, 'therapeute', 0, 0, therapeutes, value='Tous')
        self.paye_par = OptionWidget(self, 'paye_par', 1, 0, [''] + bp_custo.MOYEN_DE_PAYEMENT, value='')
        self.date_du, w_date_du = EntryWidget(self, 'date_du', 0, 2, value=last_month, want_widget=True)
        self.date_au, w_date_au = EntryWidget(self, 'date_au', 1, 2, want_widget=True)
        self.etat = OptionWidget(self, 'etat_payement', 2, 0, bp_custo.ETAT_PAYEMENT, value='Tous')
        self.therapeute.trace('w', self.update_list)
        self.paye_par.trace('w', self.update_list)
        w_date_du.bind('<KeyRelease-Return>', self.date_du_changed)
        w_date_au.bind('<KeyRelease-Return>', self.update_list)
        self.etat.trace('w', self.update_list)
        tk.Button(self, text="📅", command=lambda:self.popup_calendar(self.date_du, w_date_du), borderwidth=0, relief=tk.FLAT).grid(row=0, column=4)
        tk.Button(self, text="📅", command=lambda:self.popup_calendar(self.date_au, w_date_au), borderwidth=0, relief=tk.FLAT).grid(row=1, column=4)

        # Middle block: list display
        tk.Label(self, font=bp_custo.LISTBOX_DEFAULT,
                 text="       Nom                            Prénom                    Consultation du   Prix Payé le").grid(row=3, column=0, columnspan=4, sticky=tk.W)
        self.list_format = "%-6s %-30s %-30s %s %6.2f %s"
        self.list = ListboxWidget(self, 'consultations', 4, 0, columnspan=5)
        self.list.config(selectmode=tk.MULTIPLE)
        self.total = EntryWidget(self, 'total', 5, 2, readonly=True)

        # Bottom block: available action on selected items
        self.paye_le = EntryWidget(self, 'paye_le', 6, 0, value=today)
        tk.Button(self, text=buttons_text.mark_paye, command=self.mark_paid).grid(row=6, column=2, sticky=tk.W)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=2)
        self.update_list()

    def date_du_changed(self, *args):
        self.date_au.set(self.date_du.get().strip())
        self.update_list()

    def update_list(self, *args):
        therapeute = self.therapeute.get()
        paye_par = self.paye_par.get()
        date_du = parse_date(self.date_du.get().strip())
        date_au = parse_date(self.date_au.get().strip())
        etat = self.etat.get().encode('UTF-8')
        conditions = ['TRUE']
        args = []
        if therapeute != 'Tous':
            conditions.append('consultations.therapeute = %s')
            args.append(therapeute)
        if paye_par != '':
            conditions.append('paye_par = %s')
            args.append(paye_par)
        if date_du:
            conditions.append('date_consult >= %s')
            args.append(date_du)
        if date_au:
            conditions.append('date_consult < %s')
            args.append(date_au + datetime.timedelta(days=1))
        if etat == 'Comptabilisé':
            conditions.append('paye_le IS NOT NULL')
        elif etat == 'Non-comptabilisé':
            conditions.append('paye_le IS NULL')
        self.list.delete(0, tk.END)
        self.list.selection_clear(0, tk.END)
        self.total.set('')
        self.data = []
        total = 0
        try:
            cursor.execute("""SELECT id_consult, date_consult, paye_le, prix_cts, majoration_cts, sex, nom, prenom
                                FROM consultations INNER JOIN patients ON consultations.id = patients.id
                               WHERE %s""" % ' AND '.join(conditions), args)
            for id_consult, date_consult, paye_le, prix_cts, majoration_cts, sex, nom, prenom in cursor:
                self.list.insert(tk.END, self.list_format % (sex, nom, prenom, date_consult, (prix_cts+majoration_cts)/100., paye_le))
                self.data.append(id_consult)
                total += prix_cts + majoration_cts
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
        self.total.set('%0.2f CHF' % (total/100.))

    def mark_paid(self, *args):
        paye_le = parse_date(self.paye_le.get())
        ids = [id_consult for i, id_consult in enumerate(self.data) if self.list.selection_includes(i)]
        try:
            if len(ids) > 1:
                cursor.execute("""UPDATE consultations SET paye_le = %s
                                WHERE paye_le IS NULL AND id_consult IN %s""",
                               [paye_le, tuple(ids)])
            elif len(ids) == 1:
                cursor.execute("""UPDATE consultations SET paye_le = %s WHERE id_consult = %s""", [paye_le, ids[0]])
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)
        self.update_list()

    def popup_calendar(self, var, widget):
        import ttkcalendar
        geometry = widget.winfo_geometry()
        geometry = geometry[geometry.find('+'):]
        win = tk.Toplevel(self)
        win.geometry(geometry)
        win.title("Date")
        win.transient(self)
        date = parse_date(var.get())
        ttkcal = ttkcalendar.Calendar(win, locale="fr_CH.UTF-8", year=date.year, month=date.month)
        ttkcal.pack(expand=1, fill='both')
        win.update()
        win.wait_window()
        if ttkcal.selection:
            var.set(ttkcal.selection.strftime("%Y-%m-%d"))
            if var == self.date_du:
                self.date_au.set(self.date_du.get())
            self.update_list()


app = Application()
app.mainloop()
