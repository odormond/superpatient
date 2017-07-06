#! /usr/bin/env python2
# coding:UTF-8

import os
import sys
import datetime
import traceback
import mailcap

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
    from bp_model import Patient, Consultation
except:
    tkMessageBox.showwarning("Missing file", "bp_model.py is missing")
    sys.exit()

try:
    import bp_custo
    from bp_custo import windows_title, errors_text, buttons_text, menus_text, labels_text
    from bp_custo import normalize_filename
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
    import bp_factures
except:
    tkMessageBox.showwarning("Missing file", "bp_factures.py is missing")
    sys.exit()

try:
    from bp_bvr import gen_bvr_ref
except:
    tkMessageBox.showwarning(u"Missing file", u"bp_bvr.py is missing")
    sys.exit()

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


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        if (sys.platform != 'win32') and hasattr(sys, 'frozen'):
            self.tk.call('console', 'hide')

        self.option_add('*font', 'Helvetica -15')
        self.title(windows_title.encaissement)

        menubar = tk.Menu(self)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=menus_text.about, command=lambda: apropos(self))
        helpmenu.add_command(label=menus_text.licence, command=lambda: licence(self))

        menubar.add_cascade(label=menus_text.help, menu=helpmenu)
        self.config(menu=menubar)

        # Tpo block: list display
        tk.Label(self, font=bp_custo.LISTBOX_DEFAULT,
                 text="Sex     Nom                             Prénom                          Thérapeute  Heure    Prix  Paye par   ").grid(row=0, column=0, columnspan=4, sticky=tk.W)
        self.list_format = "%-6s  %-30s  %-30s  %-10s  %5s  %6.2f  %8s"
        self.list = ListboxWidget(self, 'consultations', 1, 0, columnspan=4)
        self.selected_idx = None
        self.list.bind('<<ListboxSelect>>', self.select_item)
        self.nom = EntryWidget(self, 'nom', 2, 0, readonly=True, side_by_side=False)
        self.prenom = EntryWidget(self, 'prenom', 2, 1, readonly=True, side_by_side=False)
        self.therapeute = EntryWidget(self, 'therapeute', 2, 2, readonly=True, side_by_side=False)
        self.prix = EntryWidget(self, 'prix', 2, 3, readonly=True, side_by_side=False)

        # Bottom block: available action on selected items
        self.paye_par, self.paye_par_widget = OptionWidget(self, 'paye_par', 4, 0, options=bp_custo.MOYEN_DE_PAYEMENT[:-1], want_widget=True)
        self.paye_par.trace('w', self.confirm_ready)
        self.btn_pay = tk.Button(self, text=buttons_text.validate, command=self.validate, state=tk.DISABLED)
        self.btn_pay.grid(row=4, column=2, sticky=tk.W)
        self.btn_print = tk.Button(self, text=buttons_text.change_pay_method_and_print, command=self.change_pay_method_and_print, state=tk.DISABLED)
        self.btn_print.grid(row=4, column=3, sticky=tk.EW)
        tk.Button(self, text=buttons_text.refresh, command=self.update_list).grid(row=5, column=0, columnspan=4, sticky=tk.EW)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.update_list()

    def select_item(self, *args):
        selected = self.list.curselection()
        if selected:
            self.selected_idx, = selected
            id_consult, sex, nom, prenom, therapeute, heure_consult, prix_total_cts, paye_par = self.data[self.selected_idx]
            self.nom.set(nom)
            self.prenom.set(prenom)
            self.therapeute.set(therapeute)
            self.prix.set('%6.2f CHF' % (prix_total_cts/100.))
            self.paye_par_widget.config(state=tk.NORMAL)
        else:
            self.selected_idx = None
            self.nom.set('')
            self.prenom.set('')
            self.therapeute.set('')
            self.prix.set('')
            self.paye_par.set('')
            self.paye_par_widget.config(state=tk.DISABLED)

    def confirm_ready(self, *args):
        if self.selected_idx is not None and self.paye_par.get() == self.data[self.selected_idx][-1]:
            self.btn_pay.config(state=tk.NORMAL)
            self.btn_print.config(state=tk.DISABLED)
        else:
            self.btn_pay.config(state=tk.DISABLED)
            self.btn_print.config(state=tk.NORMAL)

    def update_list(self, *args):
        self.list.delete(0, tk.END)
        self.list.selection_clear(0, tk.END)
        self.nom.set('')
        self.prenom.set('')
        self.therapeute.set('')
        self.prix.set('')
        self.paye_par.set('')
        self.paye_par_widget.config(state=tk.DISABLED)
        self.btn_pay.config(state=tk.DISABLED)
        self.btn_print.config(state=tk.DISABLED)
        self.data = []
        try:
            cursor.execute("""SELECT consultations.id_consult, sex, nom, prenom, COALESCE(consultations.therapeute, patients.therapeute), heure_consult, prix_cts + majoration_cts + frais_admin_cts, paye_par
                                FROM consultations INNER JOIN patients ON consultations.id = patients.id
                               WHERE date_consult = CURDATE() AND (status = 'O' OR status = 'I' AND paye_par = 'BVR')
                               ORDER BY heure_consult""")
            today = datetime.datetime.combine(datetime.date.today(), datetime.time())
            self.data = [(id_consult, sex, nom, prenom, therapeute, (today + (heure_consult or datetime.timedelta(0))).time(), prix_cts, paye_par) for id_consult, sex, nom, prenom, therapeute, heure_consult, prix_cts, paye_par in cursor]
            for id_consult, sex, nom, prenom, therapeute, heure_consult, prix_total_cts, paye_par in self.data:
                self.list.insert(tk.END, self.list_format % (sex, nom[:30], prenom[:30], therapeute, heure_consult.strftime(u'%H:%M'), prix_total_cts/100., paye_par))
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)

    def change_pay_method_and_print(self):
        id_consult = self.data[self.selected_idx][0]
        consult = Consultation.load(cursor, id_consult)
        if self.paye_par.get() == u'BVR':
            if not tkMessageBox.askyesno(windows_title.confirm_change, labels_text.ask_confirm_payment_method_change_to_BVR):
                return
            patient = Patient.load(cursor, consult.id)
            consult.bv_ref = gen_bvr_ref(cursor, patient.prenom, patient.nom, consult.date_consult)
        else:
            consult.bv_ref = None
        consult.paye_par = self.paye_par.get()
        consult.save(cursor)
        filename_consult = normalize_filename(datetime.datetime.now().strftime('consultation_%F_%Hh%Mm%Ss.pdf'))
        bp_factures.consultations(filename_consult, cursor, [consult])
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_consult)
        os.system(cmd + '&')
        self.real_validate()
        self.update_list()

    def validate(self):
        if self.paye_par.get() == u'BVR':
            id_consult = self.data[self.selected_idx][0]
            consult = Consultation.load(cursor, id_consult)
            if consult.status == bp_custo.STATUS_OPENED:
                filename_consult = normalize_filename(datetime.datetime.now().strftime('consultation_%F_%Hh%Mm%Ss.pdf'))
                bp_factures.consultations(filename_consult, cursor, [consult])
                cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_consult)
                os.system(cmd + '&')
        self.real_validate()
        self.update_list()

    def real_validate(self):
        id_consult = self.data[self.selected_idx][0]
        try:
            if self.paye_par.get() == u'BVR':
                cursor.execute("""UPDATE consultations SET status = 'E' WHERE id_consult = %s""", [id_consult])
            elif self.paye_par.get() not in (u'Dû', u'PVPE'):
                cursor.execute("""UPDATE consultations SET paye_le = CURDATE(), status = 'P' WHERE id_consult = %s""", [id_consult])
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)


app = Application()
app.mainloop()
