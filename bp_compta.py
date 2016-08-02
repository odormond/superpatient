#! /usr/bin/env python2
# coding:UTF-8

import os
import sys
import datetime
import traceback
import calendar

sys.path.insert(0, os.path.dirname(__file__))

try:
    import Tkinter as tk
    import tkMessageBox
    import tkFileDialog

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
    from bp_custo import windows_title, errors_text, buttons_text, menus_text, labels_text, DATE_FMT
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
    from bp_factures import facture
except:
    tkMessageBox.showwarning("Missing file", "bp_factures.py is missing")
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

db.autocommit(True)
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


def sum_found(positions):
    return sum(p[7] for p in positions) / 100.0


def sum_notfound(positions):
    return sum(p[3] for p in positions) / 100.0


def normalize_filename(filename):
    for char in '\'"/`!$[]{}':
        filename = filename.replace(char, '-')
    return os.path.join(bp_custo.PDF_DIR, filename).encode('UTF-8')


class Statistics(bp_Dialog.Dialog):
    def __init__(self, parent):
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text=buttons_text.ok, command=self.cancel).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def body(self, master):
        self.title(windows_title.compta_statistics)
        cursor.execute("SELECT DISTINCT COALESCE(consultations.therapeute, patients.therapeute) FROM consultations RIGHT OUTER JOIN patients ON consultations.id = patients.id")
        self.therapeutes = [t for t, in cursor]
        cursor.execute("SELECT DISTINCT YEAR(date_consult) FROM consultations")
        self.years = [y for y, in cursor]
        self.months = [u'tout', u'janvier', u'février', u'mars', u'avril', u'mai', u'juin', u'juillet', u'août', u'septembre', u'octobre', u'novembre', u'décembre']

        selector_frame = tk.Frame(master)
        selector_frame.grid(row=0, column=1, sticky=tk.EW)
        self.yearVar = tk.StringVar()
        self.yearVar.set('tout')
        self.yearWidget = tk.OptionMenu(selector_frame, self.yearVar, *(['tout'] + [str(y) for y in self.years]))
        self.yearWidget.grid(row=0, column=0, sticky=tk.EW)
        self.yearVar.trace('w', self.update_display)

        self.monthVar = tk.StringVar()
        self.monthVar.set('tout')
        self.monthWidget = tk.OptionMenu(selector_frame, self.monthVar, *self.months)
        self.monthWidget.grid(row=0, column=1, sticky=tk.EW)
        self.monthVar.trace('w', self.update_display)
        self.monthWidget.config(state=tk.DISABLED)
        selector_frame.grid_columnconfigure(0, weight=1)
        selector_frame.grid_columnconfigure(1, weight=1)

        self.modeVar = tk.StringVar()
        self.modeVar.set('# Consultations')
        self.modeWidget = tk.OptionMenu(master, self.modeVar, '# Consultations', 'CHF Consultations', 'CHF Majorations', 'CHF Total')
        self.modeWidget.grid(row=0, column=2, sticky=tk.EW)
        self.modeVar.trace('w', self.update_display)

        self.totals = {}
        tk.Label(master).grid(row=1, column=0)  # Spacer
        tk.Label(master).grid(row=2, column=0)  # Spacer
        for i, therapeute in enumerate(self.therapeutes):
            tk.Label(master, text=therapeute, anchor=tk.SE, borderwidth=1, relief=tk.RIDGE).grid(row=2+i, column=0, sticky=tk.EW+tk.S)
            self.totals[therapeute] = widget = tk.Label(master, anchor=tk.SE, borderwidth=1, relief=tk.RIDGE)
            widget.grid(row=2+i, column=2, sticky=tk.EW+tk.S)
        tk.Label(master, text="Total", anchor=tk.NE).grid(row=2+len(self.therapeutes), column=1, sticky=tk.NE)
        self.total = tk.Label(master, anchor=tk.NE, borderwidth=1, relief=tk.RIDGE)
        self.total.grid(row=2+len(self.therapeutes), column=2, sticky=tk.EW+tk.N)

        master.grid_columnconfigure(0, weight=0)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=0)

        self.master = master

        self.update_display()

    def update_display(self, *args):
        year = self.yearVar.get()
        month = self.monthVar.get()
        if year != 'tout':
            month_state = tk.NORMAL
            year = int(year)
        else:
            month_state = tk.DISABLED
        self.monthWidget.config(state=month_state)
        self.cleanup()
        if year != 'tout' and month != 'tout':
            month = self.months.index(month)
            self.setup_month_view(year, month)
        elif year != 'tout':
            self.setup_year_view(year)
        else:
            self.setup_full_view()

    def cleanup(self):
        self.table_frame = tk.Frame(self.master)
        self.table_frame.grid(row=1, rowspan=len(self.therapeutes)+1, column=1, sticky=tk.NSEW)
        for label in self.totals.values():
            label.config(text='')
        self.total.config(text='')

    def setup_full_view(self):
        totals = {}
        total = 0
        mode = self.modeVar.get()
        format = '%d' if mode == '# Consultations' else '%0.2f'
        for c, year in enumerate(self.years):
            cursor.execute("""SELECT COALESCE(consultations.therapeute, patients.therapeute) AS therapeute, count(*), CAST(SUM(prix_cts) AS SIGNED), CAST(SUM(majoration_cts) AS SIGNED)
                                FROM consultations INNER JOIN patients ON consultations.id = patients.id
                               WHERE YEAR(date_consult) = %s
                               GROUP BY therapeute
                               ORDER BY therapeute""", [year])
            tk.Label(self.table_frame, text=str(year), anchor=tk.CENTER, borderwidth=1, relief=tk.RIDGE).grid(row=0, column=c, sticky=tk.EW)
            for therapeute, count, prix_cts, majoration_cts in cursor:
                if mode == '# Consultations':
                    value = count
                elif mode == 'CHF Consultations':
                    value = prix_cts/100.
                elif mode == 'CHF Majorations':
                    value = majoration_cts/100.
                else:
                    value = (prix_cts + majoration_cts)/100.
                tk.Label(self.table_frame, text=(format % value), anchor=tk.SE, borderwidth=1, relief=tk.RIDGE).grid(row=1+self.therapeutes.index(therapeute), column=c, sticky=tk.EW)
                totals[therapeute] = totals.get(therapeute, 0) + value
                total += value
            self.table_frame.grid_columnconfigure(c, weight=1)
        for therapeute, label in self.totals.items():
            if therapeute in totals:
                label.config(text=(format % totals[therapeute]))
        self.total.config(text=(format % total))

    def setup_year_view(self, year):
        totals = {}
        total = 0
        mode = self.modeVar.get()
        format = '%d' if mode == '# Consultations' else '%0.2f'
        for month in range(1, 13):
            cursor.execute("""SELECT COALESCE(consultations.therapeute, patients.therapeute) AS therapeute, count(*), CAST(SUM(prix_cts) AS SIGNED), CAST(SUM(majoration_cts) AS SIGNED)
                                FROM consultations INNER JOIN patients ON consultations.id = patients.id
                               WHERE YEAR(date_consult) = %s AND MONTH(date_consult) = %s
                               GROUP BY therapeute
                               ORDER BY therapeute""", [year, month])
            c = month - 1
            tk.Label(self.table_frame, text=self.months[month], anchor=tk.CENTER, borderwidth=1, relief=tk.RIDGE).grid(row=0, column=c, sticky=tk.EW)
            for therapeute, count, prix_cts, majoration_cts in cursor:
                if mode == '# Consultations':
                    value = count
                elif mode == 'CHF Consultations':
                    value = prix_cts/100.
                elif mode == 'CHF Majorations':
                    value = majoration_cts/100.
                else:
                    value = (prix_cts + majoration_cts)/100.
                tk.Label(self.table_frame, text=(format % value), anchor=tk.SE, borderwidth=1, relief=tk.RIDGE).grid(row=1+self.therapeutes.index(therapeute), column=c, sticky=tk.EW)
                totals[therapeute] = totals.get(therapeute, 0) + value
                total += value
            self.table_frame.grid_columnconfigure(c, weight=1)
        for therapeute, label in self.totals.items():
            if therapeute in totals:
                label.config(text=(format % totals[therapeute]))
        self.total.config(text=(format % total))

    def setup_month_view(self, year, month):
        totals = {}
        total = 0
        mode = self.modeVar.get()
        format = '%d' if mode == '# Consultations' else '%0.2f'
        for day in range(1, calendar.mdays[month]+1):
            cursor.execute("""SELECT COALESCE(consultations.therapeute, patients.therapeute) AS therapeute, count(*), CAST(SUM(prix_cts) AS SIGNED), CAST(SUM(majoration_cts) AS SIGNED)
                                FROM consultations INNER JOIN patients ON consultations.id = patients.id
                               WHERE YEAR(date_consult) = %s AND MONTH(date_consult) = %s AND DAY(date_consult) = %s
                               GROUP BY therapeute
                               ORDER BY therapeute""", [year, month, day])
            c = day - 1
            tk.Label(self.table_frame, text=str(day), anchor=tk.CENTER, borderwidth=1, relief=tk.RIDGE).grid(row=0, column=c, sticky=tk.EW)
            for therapeute, count, prix_cts, majoration_cts in cursor:
                if mode == '# Consultations':
                    value = count
                elif mode == 'CHF Consultations':
                    value = prix_cts/100.
                elif mode == 'CHF Majorations':
                    value = majoration_cts/100.
                else:
                    value = (prix_cts + majoration_cts)/100.
                tk.Label(self.table_frame, text=(format % value), anchor=tk.SE, borderwidth=1, relief=tk.RIDGE).grid(row=1+self.therapeutes.index(therapeute), column=c, sticky=tk.EW)
                totals[therapeute] = totals.get(therapeute, 0) + value
                total += value
            self.table_frame.grid_columnconfigure(c, weight=1)
        for therapeute, label in self.totals.items():
            if therapeute in totals:
                label.config(text=(format % totals[therapeute]))
        self.total.config(text=(format % total))


class GererRappels(bp_Dialog.Dialog):
    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text=buttons_text.output_recalls, command=self.output_recalls).pack(side=tk.LEFT)
        tk.Button(box, text=buttons_text.cancel, command=self.cancel).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def body(self, master):
        self.title(windows_title.manage_recalls)
        self.upto, w_upto = EntryWidget(master, 'consult_upto', 0, 0, want_widget=True)
        self.upto.set(str(datetime.date.today() - datetime.timedelta(days=30)))
        w_upto.bind('<KeyRelease-Return>', self.update_list)
        tk.Button(master, text=u"\U0001f4c5".encode('UTF-8'), command=lambda: self.popup_calendar(self.upto, w_upto), borderwidth=0, relief=tk.FLAT).grid(row=0, column=2)
        tk.Label(master, font=bp_custo.LISTBOX_DEFAULT,
                 text="       Nom                            Prénom                    Consultation du   Prix  Rappel le  #").grid(row=1, column=0, columnspan=3, sticky=tk.W)
        self.list_format = "%-6s %-30s %-30s %s %6.2f  %10s %d"
        self.list = ListboxWidget(master, 'consultations', 2, 0, columnspan=3)
        self.list.config(selectmode=tk.MULTIPLE)
        self.list.bind('<<ListboxSelect>>', self.update_selection)
        self.total = EntryWidget(master, 'total', 3, 0, readonly=True, justify=tk.RIGHT)

        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_rowconfigure(2, weight=1)

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
            self.update_list()

    def update_list(self, *args):
        upto = parse_date(self.upto.get().strip())
        self.list.delete(0, tk.END)
        self.list.selection_clear(0, tk.END)
        self.total.set('')
        self.data = []
        try:
            cursor.execute("""SELECT consultations.id_consult, date_consult, prix_cts, majoration_cts, sex, nom, prenom, COALESCE(CAST(SUM(rappel_cts) AS SIGNED), 0), count(date_rappel), max(date_rappel)
                                FROM consultations INNER JOIN patients ON consultations.id = patients.id
                                LEFT OUTER JOIN rappels ON consultations.id_consult = rappels.id_consult
                               WHERE paye_le IS NULL AND bv_ref IS NOT NULL AND bv_ref != '' AND date_consult <= %s
                               GROUP BY consultations.id_consult, date_consult, prix_cts, majoration_cts, sex, nom, prenom
                               ORDER BY date_consult""", [upto])
            for id_consult, date_consult, prix_cts, majoration_cts, sex, nom, prenom, rappel_cts, rappel_cnt, rappel_last in cursor:
                if rappel_last is None:
                    rappel_last = ''
                elif rappel_last > upto:
                    continue
                self.list.insert(tk.END, self.list_format % (sex, nom, prenom, date_consult, (prix_cts+majoration_cts+rappel_cts)/100., rappel_last, rappel_cnt))
                if rappel_cnt == 1:
                    self.list.itemconfig(tk.END, foreground='#400')
                elif rappel_cnt > 1:
                    self.list.itemconfig(tk.END, foreground='#800')
                self.data.append((id_consult, (prix_cts+majoration_cts+rappel_cts), sex, nom, prenom, date_consult, rappel_cnt, prix_cts, majoration_cts, rappel_cts))
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
        self.list.selection_set(0, tk.END)
        self.update_selection()

    def update_selection(self, *args):
        total = 0
        for idx in self.list.curselection():
            total += self.data[idx][1]
        self.total.set('%0.2f CHF' % (total/100.))

    def output_recalls(self, *args):
        for idx in self.list.curselection():
            id_consult, _, sex, nom, prenom, date_consult, rappel_cnt, prix_cts, majoration_cts, rappel_cts = self.data[idx]

            ts = datetime.datetime.now().strftime('%H')
            filename = normalize_filename(u'rappel_%d_%s_%s_%s_%s_%sh.pdf' % (rappel_cnt+1, nom, prenom, sex, date_consult, ts))

            cursor.execute("""SELECT COALESCE(consultations.therapeute, patients.therapeute), patients.id, MC_accident, date_naiss, bv_ref
                                FROM consultations INNER JOIN patients ON consultations.id = patients.id
                               WHERE id_consult = %s""",
                           [id_consult])
            therapeute, id_patient, mc_accident, date_naiss, bv_ref = cursor.fetchone()

            cursor.execute("""SELECT entete FROM therapeutes WHERE therapeute = %s""", [therapeute])
            entete_therapeute, = cursor.fetchone()
            adresse_therapeute = entete_therapeute + u'\n\n' + labels_text.adresse_pog

            cursor.execute("""SELECT adresse FROM patients WHERE id = %s""", [id_patient])
            adresse_patient, = cursor.fetchone()
            titre = {u'Mr': u'Monsieur', u'Mme': u'Madame', u'Enfant': u'Aux parents de'}[sex]
            if len(u' '.join((prenom, nom))) < 25:
                identite = [u' '.join((prenom, nom))]
            else:
                identite = [prenom, nom]
            patient_bv = u'\n'.join(identite + [adresse_patient])
            adresse_patient = u'\n'.join([titre] + identite + [adresse_patient, "", date_naiss.strftime(DATE_FMT)])

            cursor.execute("SELECT description FROM tarifs WHERE prix_cts = %s", [prix_cts])
            if cursor.rowcount != 0:
                description_prix, = cursor.fetchone()
            else:
                description_prix = ''

            cursor.execute("SELECT description FROM majorations WHERE prix_cts = %s", [majoration_cts])
            if cursor.rowcount != 0:
                description_majoration, = cursor.fetchone()
            else:
                description_majoration = ''

            cursor.execute("""INSERT INTO rappels (id_consult, rappel_cts, date_rappel)
                                   VALUES (%s, %s, %s)""",
                           [id_consult, bp_custo.MONTANT_RAPPEL_CTS, datetime.date.today()])
            rappel_cost = rappel_cts + bp_custo.MONTANT_RAPPEL_CTS

            facture(filename, adresse_therapeute, adresse_patient, description_prix, mc_accident, prix_cts, description_majoration, majoration_cts, date_consult, patient_bv, bv_ref, rappel_cost)
        self.cancel()


class SummariesImport(bp_Dialog.Dialog):
    def __init__(self, parent, ok, ko, doubled, not_found, ignored):
        self.ok = ok
        self.ko = ko
        self.doubled = doubled
        self.not_found = not_found
        self.ignored = ignored
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text=buttons_text.valider_import, command=self.validate).pack(side=tk.LEFT)
        tk.Button(box, text=buttons_text.cancel, command=self.cancel).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def validate(self):
        try:
            for payment in self.ok:
                id_consult = payment[0]
                credit_date = payment[10]
                if id_consult >= 0:
                    cursor.execute("UPDATE consultations SET paye_le = %s WHERE id_consult = %s", [credit_date, id_consult])
                else:
                    cursor.execute("UPDATE factures_manuelles SET paye_le = %s WHERE id = %s", [credit_date, -id_consult])
            self.cancel()
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)

    def body(self, master):
        self.title(windows_title.summaries_import)
        tk.Label(master, text=u"Volume").grid(row=0, column=1)
        tk.Label(master, text=u"Revenu").grid(row=0, column=2)

        tk.Label(master, text=u"Payements en ordre").grid(row=1, column=0)
        tk.Label(master, text=str(len(self.ok))).grid(row=1, column=1)
        tk.Label(master, text=u"%0.2f CHF" % sum_found(self.ok)).grid(row=1, column=2, sticky=tk.E)
        if self.ok:
            tk.Button(master, text=buttons_text.details, command=lambda: Details(self, self.ok)).grid(row=1, column=3, sticky=tk.W)

        tk.Label(master, text=u"Payements ne correspondant pas au montant attendu").grid(row=2, column=0)
        tk.Label(master, text=str(len(self.ko))).grid(row=2, column=1)
        tk.Label(master, text=u"Payements déjà encaissés").grid(row=3, column=0)
        tk.Label(master, text=str(len(self.doubled))).grid(row=3, column=1)
        tk.Label(master, text=u"%0.2f CHF" % sum_found(self.doubled)).grid(row=3, column=2, sticky=tk.E)
        if self.doubled:
            tk.Button(master, text=buttons_text.details, command=lambda: Details(self, self.doubled)).grid(row=3, column=3, sticky=tk.W)

        tk.Label(master, text=u"Payements non trouvés").grid(row=4, column=0)
        tk.Label(master, text=str(len(self.not_found))).grid(row=4, column=1)
        tk.Label(master, text=u"%0.2f CHF" % sum_notfound(self.not_found)).grid(row=4, column=2, sticky=tk.E)
        if self.not_found:
            tk.Button(master, text=buttons_text.details, command=lambda: Details(self, self.not_found)).grid(row=4, column=3, sticky=tk.W)

        tk.Label(master, text=u"Ordres ignorés").grid(row=5, column=0)
        tk.Label(master, text=str(len(self.ignored))).grid(row=5, column=1)
        if self.ignored:
            tk.Button(master, text=buttons_text.details, command=lambda: Details(self, self.ignored)).grid(row=5, column=3, sticky=tk.W)

        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)


class Details(bp_Dialog.Dialog):
    transaction_types = {
        '002': u'Crédit B préimp', '005': u'Extourne B préimp', '008': u'Correction B préimp',
        '012': u'Crédit P préimp', '015': u'Extourne P préimp', '018': u'Correction P préimp',
        '102': u'Crédit B', '105': u'Extourne B', '108': u'Correction B',
        '112': u'Crédit P', '115': u'Extourne P', '118': u'Correction P',
    }

    def __init__(self, parent, positions):
        self.positions = positions
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        self.bind("<Escape>", self.cancel)
        return tk.Button(self, text=buttons_text.done, command=self.cancel)

    def body(self, master):
        hscroll = tk.Scrollbar(master, orient=tk.HORIZONTAL)
        vscroll = tk.Scrollbar(master, orient=tk.VERTICAL)
        self.list_box = tk.Listbox(master, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, font=(bp_custo.FIXED_FONT_NAME, 10))
        hscroll.config(command=self.list_box.xview)
        vscroll.config(command=self.list_box.yview)
        self.list_box.grid(row=0, column=0, sticky=tk.NSEW)
        hscroll.grid(row=1, column=0, sticky=tk.EW)
        vscroll.grid(row=0, column=1, sticky=tk.NS)
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        if len(self.positions[0]) == 15:
            self.populate_found()
        else:
            self.populate_notfound()

    def format_date(self, date):
        if date is None:
            return u''
        elif isinstance(date, basestring):
            return u'20' + date[:2] + u'-' + date[2:4] + u'-' + date[4:]
        return unicode(date)

    def format_ref(self, ref):
        ref = list(ref)
        for pos in (2, 8, 14, 20, 26):
            ref.insert(pos, ' ')
        return ''.join(ref)

    def populate_found(self):
        self.list_box.delete(0, tk.END)
        data = []
        columns = [u"Sex", u"Nom", u"Prénom", u"Naissance", u"Consultation du", u"Facturé CHF", u"Payé CHF", u"Rappel", u"Crédité le", u"Comtabilisé le", u"Numéro de référence"]
        widths = [len(c) for c in columns]
        for id_consult, prix_cts, majoration_cts, rappel_cts, transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts in self.positions:
            if id_consult >= 0:
                cursor.execute("""SELECT sex, nom, prenom, date_naiss, date_consult, paye_le, COALESCE(CAST(SUM(rappel_cts) AS SIGNED), 0)
                                    FROM consultations INNER JOIN patients ON patients.id = consultations.id
                                                       LEFT OUTER JOIN rappels ON consultations.id_consult = rappels.id_consult
                                   WHERE consultations.id_consult = %s
                                   GROUP BY sex, nom, prenom, date_naiss, date_consult, paye_le""",
                               [id_consult])
            else:
                cursor.execute("SELECT '-', identifiant, '', '', date, paye_le, 0 FROM factures_manuelles WHERE id = %s", [-id_consult])
            sex, nom, prenom, date_naiss, date_consult, paye_le, fact_rappel_cts = cursor.fetchone()
            fact_rappel_cts = int(fact_rappel_cts)
            if fact_rappel_cts == 0:
                rappel = ''
            else:
                rappel = '%3.0f%%' % (rappel_cts * 100 / fact_rappel_cts)
            data.append((sex, nom, prenom, date_naiss, date_consult, u'%0.2f' % ((prix_cts+majoration_cts+fact_rappel_cts)/100.), u'%0.2f' % (amount_cts/100.), rappel, self.format_date(credit_date), self.format_date(paye_le), self.format_ref(ref_no)))
            widths = [max(a, len(unicode(b))) for a, b in zip(widths, data[-1])]
        self.list_box.config(width=min(120, sum(widths)+2*10))
        widths[5] *= -1
        widths[6] *= -1

        self.list_box.insert(tk.END, u"  ".join(u"%*s" % (-w, c) for w, c in zip(widths, columns)))
        for values in data:
            self.list_box.insert(tk.END, u"  ".join(u"%*s" % (-w, unicode(v)) for w, v in zip(widths, values)))

    def populate_notfound(self):
        self.list_box.delete(0, tk.END)
        data = []
        columns = [u"Type de transaction", u"Payé CHF", u"Crédité le", u"Numéro de référence"]
        widths = [len(c) for c in columns]
        for transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts in self.positions:
            data.append((self.transaction_types.get(transaction_type, transaction_type), u'%0.2f' % (amount_cts/100.), self.format_date(credit_date), self.format_ref(ref_no)))
            widths = [max(a, len(unicode(b))) for a, b in zip(widths, data[-1])]
        self.list_box.config(width=sum(widths)+2*3)
        widths[1] *= -1

        self.list_box.insert(tk.END, u"  ".join(u"%*s" % (-w, c) for w, c in zip(widths, columns)))
        for values in data:
            self.list_box.insert(tk.END, u"  ".join(u"%*s" % (-w, unicode(v)) for w, v in zip(widths, values)))


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        if (sys.platform != 'win32') and hasattr(sys, 'frozen'):
            self.tk.call('console', 'hide')

        self.option_add('*font', 'Helvetica -15')
        self.title(windows_title.compta)

        menubar = tk.Menu(self)

        bvrmenu = tk.Menu(menubar, tearoff=0)
        bvrmenu.add_command(label=menus_text.import_bvr, command=self.import_bvr)
        bvrmenu.add_command(label=menus_text.manage_recalls, command=lambda: GererRappels(self))

        menubar.add_cascade(label=menus_text.payments, menu=bvrmenu)

        statmenu = tk.Menu(menubar, tearoff=0)
        statmenu.add_command(label=menus_text.show_stats, command=self.show_stats)

        menubar.add_cascade(label=menus_text.show_stats, menu=statmenu)

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
        self.paye_par = OptionWidget(self, 'paye_par', 1, 0, [''] + bp_custo.MOYEN_DE_PAYEMENT + bp_custo.ANCIEN_MOYEN_DE_PAYEMENT, value='')
        self.date_du, w_date_du = EntryWidget(self, 'date_du', 0, 2, value=last_month, want_widget=True)
        self.date_au, w_date_au = EntryWidget(self, 'date_au', 1, 2, want_widget=True)
        self.etat = OptionWidget(self, 'etat_payement', 2, 0, bp_custo.ETAT_PAYEMENT, value='Tous')
        self.therapeute.trace('w', self.update_list)
        self.paye_par.trace('w', self.update_list)
        w_date_du.bind('<KeyRelease-Return>', self.date_du_changed)
        w_date_au.bind('<KeyRelease-Return>', self.update_list)
        self.etat.trace('w', self.update_list)
        tk.Button(self, text=u"\U0001f4c5".encode('UTF-8'), command=lambda: self.popup_calendar(self.date_du, w_date_du), borderwidth=0, relief=tk.FLAT).grid(row=0, column=4)
        tk.Button(self, text=u"\U0001f4c5".encode('UTF-8'), command=lambda: self.popup_calendar(self.date_au, w_date_au), borderwidth=0, relief=tk.FLAT).grid(row=1, column=4)
        self.nom, widget = EntryWidget(self, 'nom', 3, 0, want_widget=True)
        widget.bind('<Return>', self.update_list)
        self.prenom, widget = EntryWidget(self, 'prenom', 3, 2, want_widget=True)
        widget.bind('<Return>', self.update_list)
        tk.Button(self, text=u"\U0001f50e".encode('UTF-8'), command=self.update_list, borderwidth=0, relief=tk.FLAT).grid(row=3, column=4)

        # Middle block: list display
        tk.Label(self, font=bp_custo.LISTBOX_DEFAULT,
                 text="       Nom                            Prénom                    Consultation du   Prix Payé le").grid(row=4, column=0, columnspan=4, sticky=tk.W)
        self.list_format = "%-6s %-30s %-30s %s %6.2f %s"
        self.list = ListboxWidget(self, 'consultations', 5, 0, columnspan=5)
        self.list.config(selectmode=tk.MULTIPLE)
        self.count = EntryWidget(self, 'count', 6, 0, readonly=True)
        self.total_consultation = EntryWidget(self, 'total_consultation', 6, 2, readonly=True, justify=tk.RIGHT)
        self.total_majoration = EntryWidget(self, 'total_majoration', 7, 2, readonly=True, justify=tk.RIGHT)
        self.total_rappel = EntryWidget(self, 'total_rappel', 8, 2, readonly=True, justify=tk.RIGHT)
        self.total = EntryWidget(self, 'total', 9, 2, readonly=True, justify=tk.RIGHT)

        # Bottom block: available action on selected items
        self.paye_le = EntryWidget(self, 'paye_le', 10, 0, value=today)
        tk.Button(self, text=buttons_text.mark_paye, command=self.mark_paid).grid(row=10, column=2, sticky=tk.W)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(5, weight=2)
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
        prenom = self.prenom.get().strip()
        nom = self.nom.get().strip()
        conditions = ['TRUE']
        args = []
        manual_bills_conditions = ['TRUE']
        manual_bills_args = []
        if therapeute != 'Tous':
            conditions.append('consultations.therapeute = %s')
            args.append(therapeute)
            manual_bills_conditions.append('therapeute = %s')
            manual_bills_args.append(therapeute)
        if paye_par != '':
            conditions.append('paye_par = %s')
            args.append(paye_par)
        if date_du:
            conditions.append('date_consult >= %s')
            args.append(date_du)
            manual_bills_conditions.append('date >= %s')
            manual_bills_args.append(date_du)
        if date_au:
            conditions.append('date_consult < %s')
            args.append(date_au + datetime.timedelta(days=1))
            manual_bills_conditions.append('date < %s')
            manual_bills_args.append(date_au + datetime.timedelta(days=1))
        if etat == 'Comptabilisé':
            conditions.append('paye_le IS NOT NULL')
            manual_bills_conditions.append('paye_le IS NOT NULL')
        elif etat == 'Non-comptabilisé':
            conditions.append('paye_le IS NULL')
            manual_bills_conditions.append('paye_le IS NULL')
        if prenom:
            conditions.append('prenom LIKE %s')
            args.append(prenom.replace('*', '%'))
        if nom:
            conditions.append('nom LIKE %s')
            args.append(nom.replace('*', '%'))
            manual_bills_conditions.append('destinataire LIKE %s')
            manual_bills_args.append(nom.replace('*', '%'))
        self.list.delete(0, tk.END)
        self.list.selection_clear(0, tk.END)
        self.count.set('')
        self.total_consultation.set('')
        self.total_majoration.set('')
        self.total_rappel.set('')
        self.total.set('')
        self.data = []
        count = 0
        total_consultation = 0
        total_majoration = 0
        total_rappel = 0
        try:
            cursor.execute("""SELECT consultations.id_consult, date_consult, paye_le, prix_cts, majoration_cts, sex, nom, prenom, COALESCE(CAST(SUM(rappel_cts) AS SIGNED), 0), count(date_rappel)
                                FROM consultations INNER JOIN patients ON consultations.id = patients.id
                                LEFT OUTER JOIN rappels ON consultations.id_consult = rappels.id_consult
                               WHERE %s
                               GROUP BY consultations.id_consult, date_consult, paye_le, prix_cts, majoration_cts, sex, nom, prenom
                               ORDER BY date_consult""" % ' AND '.join(conditions), args)
            data = list(cursor)
            if paye_par in ('', 'BVR'):
                cursor.execute("""SELECT -id, date, paye_le, montant_cts, 0, '-', identifiant, '', 0, 0
                                    FROM factures_manuelles
                                   WHERE %s
                                   ORDER BY date""" % ' AND '.join(manual_bills_conditions), manual_bills_args)
                data += list(cursor)
            for id_consult, date_consult, paye_le, prix_cts, majoration_cts, sex, nom, prenom, rappel_cts, rappel_cnt in data:
                self.list.insert(tk.END, self.list_format % (sex, nom, prenom, date_consult, (prix_cts+majoration_cts+rappel_cts)/100., paye_le))
                if rappel_cnt == 1:
                    self.list.itemconfig(self.list.size()-1, foreground='#400')
                elif rappel_cnt > 1:
                    self.list.itemconfig(self.list.size()-1, foreground='#800')
                self.data.append(id_consult)
                total_consultation += prix_cts
                total_majoration += majoration_cts
                total_rappel += rappel_cts
                count += 1
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
        self.count.set(str(count))
        self.total_consultation.set('%0.2f CHF' % (total_consultation/100.))
        self.total_majoration.set('%0.2f CHF' % (total_majoration/100.))
        self.total_rappel.set('%0.2f CHF' % (total_rappel/100.))
        self.total.set('%0.2f CHF' % ((total_consultation + total_majoration + total_rappel)/100.))

    def mark_paid(self, *args):
        paye_le = parse_date(self.paye_le.get())
        consult_ids = [id for i, id in enumerate(self.data) if self.list.selection_includes(i) and id >= 0]
        manual_bills_ids = [-id for i, id in enumerate(self.data) if self.list.selection_includes(i) and id < 0]
        try:
            if len(consult_ids) > 1:
                cursor.execute("""UPDATE consultations SET paye_le = %s
                                WHERE paye_le IS NULL AND id_consult IN %s""",
                               [paye_le, tuple(consult_ids)])
            elif len(consult_ids) == 1:
                cursor.execute("""UPDATE consultations SET paye_le = %s WHERE id_consult = %s""", [paye_le, consult_ids[0]])
            if len(manual_bills_ids) > 1:
                cursor.execute("""UPDATE factures_manuelles SET paye_le = %s
                                WHERE paye_le IS NULL AND id IN %s""",
                               [paye_le, tuple(manual_bills_ids)])
            elif len(manual_bills_ids) == 1:
                cursor.execute("""UPDATE factures_manuelles SET paye_le = %s WHERE id = %s""", [paye_le, manual_bills_ids[0]])
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

    def import_bvr(self):
        filename = tkFileDialog.askopenfilename(title=menus_text.import_bvr)
        if not filename:
            return
        records = []
        total_line = None
        with open(filename) as f:
            try:
                line_no = 0
                for line in f:
                    line_no += 1
                    transaction_type, line = line[:3], line[3:]
                    bvr_client_no, line = line[:9], line[9:]
                    ref_no, line = line[:27], line[27:]
                    if transaction_type[0] in '01' and transaction_type[1] in '01' and transaction_type[2] in '258':
                        amount_cts, line = int(line[:10]), line[10:]
                        if transaction_type[2] == '5':
                            amount_cts = -amount_cts
                        depot_ref, line = line[:10], line[10:]
                        depot_date, line = line[:6], line[6:]
                        processing_date, line = line[:6], line[6:]
                        credit_date, line = line[:6], line[6:]
                        microfilm_no, line = line[:9], line[9:]
                        reject_code, line = line[:1], line[1:]
                        zeros, line = line[:9], line[9:]
                        postal_fee_cts, line = int(line[:4]), line[4:].strip()
                        records.append((transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts))
                    elif transaction_type in ('995', '999'):
                        total_cts, line = int(line[:12]), line[12:]
                        if transaction_type == '995':
                            total_cts = -total_cts
                        count, line = int(line[:12]), line[12:]
                        date, line = line[:6], line[6:]
                        postal_fees_cts, line = int(line[:9]), line[9:]
                        hw_postal_fees_cts, line = int(line[:9]), line[9:]
                        reserved, line = line[:13], line[13:].strip()
                        assert total_line is None, "Multiple total line found"
                        total_line = (transaction_type, bvr_client_no, ref_no, total_cts, count, date, postal_fees_cts, hw_postal_fees_cts)
                    assert line in ('', '\n'), "Garbage at end of line %d" % line_no
                assert total_line is not None and len(records) == count, "Records count does not match total line indication"
            except Exception, e:
                print e
                tkMessageBox.showerror("Fichier corrompu", "Une erreur s'est produite lors de la lecture du fichier de payement.\n%r" % e.args)
                return
        ignored = []
        not_found = []
        ok = []
        ko = []
        doubled = []
        for transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts in records:
            if transaction_type[2] != '2':
                ignored.append((transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts))
                continue
            l = None
            rappel_cts = 0
            cursor.execute("SELECT id_consult, prix_cts, majoration_cts, paye_le FROM consultations WHERE bv_ref = %s", [ref_no])
            if cursor.rowcount != 0:
                id_consult, prix_cts, majoration_cts, paye_le = cursor.fetchone()
                cursor.execute("SELECT rappel_cts FROM rappels WHERE id_consult = %s ORDER BY date_rappel", [id_consult])
                a_payer_cts = prix_cts + majoration_cts
                for r in [0] + [r for r, in cursor]:
                    rappel_cts += r
                    if a_payer_cts + rappel_cts == amount_cts:
                        if paye_le is None:
                            l = ok
                        else:
                            l = doubled
                        break
                else:
                    l = ko
            else:
                cursor.execute("SELECT id, montant_cts, paye_le FROM factures_manuelles WHERE bv_ref = %s", [ref_no])
                if cursor.rowcount != 0:
                    id, montant_cts, paye_le = cursor.fetchone()
                    id_consult = -id
                    prix_cts, majoration_cts = montant_cts, 0
                    if montant_cts != amount_cts:
                        l = ko
                    elif paye_le is None:
                        l = ok
                    else:
                        l = doubled
            if l is not None:
                l.append((id_consult, prix_cts, majoration_cts, rappel_cts, transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts))
            else:
                not_found.append((transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts))

        SummariesImport(self, ok, ko, doubled, not_found, ignored)
        self.update_list()

    def show_stats(self):
        Statistics(self)


app = Application()
app.mainloop()
#! /usr/bin/env python2
# coding:UTF-8

import os
