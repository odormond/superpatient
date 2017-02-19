#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

# File: bp.py

#    Copyright 2006 Tibor Csernay

#    This file is part of SuperPatient.

#    SuperPatient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    SuperPatient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with SuperPatient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
import pwd
import mailcap
import datetime
import traceback

LOGIN = pwd.getpwuid(os.geteuid())[0]

sys.path.insert(0, os.path.dirname(__file__))

try:
    import Tkinter as tk
    import tkMessageBox
    import tkFileDialog

except:
    tkMessageBox.showwarning(u"Error", u"Tkinter is not correctly installed !")
    sys.exit()

try:
    import bp_Dialog
except:
    tkMessageBox.showwarning(u"Missing file", u"bp_Dialog.py is missing")
    sys.exit()

try:
    import bp_custo
    from bp_custo import buttons_text, menus_text, labels_text, labels_font
    from bp_custo import windows_title, errors_text, fields_font, fields_height
    from bp_custo import bvr, DATE_FMT
    from bp_custo import normalize_filename
    from bp_custo import STATUS_OPENED, STATUS_PAYED, STATUS_ABANDONED
except:
    tkMessageBox.showwarning(u"Missing file", u"bp_custo.py is missing")
    sys.exit()

try:
    if not os.path.exists(bp_custo.PDF_DIR):
        os.mkdir(bp_custo.PDF_DIR)
    elif not os.path.isdir(bp_custo.PDF_DIR) or not os.access(bp_custo.PDF_DIR, os.W_OK):
        raise ValueError()
except:
    tkMessageBox.showwarning(u"Wrong directory", u"Cannot store PDFs in " + bp_custo.PDF_DIR)
    sys.exit()

try:
    from bp_widgets import RadioWidget, EntryWidget, OptionWidget, TextWidget, ListboxWidget
except:
    tkMessageBox.showwarning(u"Missing file", u"bp_widgets.py is missing")
    sys.exit()

try:
    import bp_connect
except:
    tkMessageBox.showwarning(u"Missing file", u"bp_connect.py is missing")
    sys.exit()

try:
    from bp_model import Patient as PatientModel
    from bp_model import Consultation as ConsultationModel
except:
    tkMessageBox.showwarning(u"Missing file", u"bp_model.py is missing")
    sys.exit()

try:
    import reportlab
    reportlab
except:
    tkMessageBox.showwarning(u"Missing dependency", u"The reportlab library is missing")
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
    import bp_factures
except:
    tkMessageBox.showwarning(u"Missing file", u"bp_factures.py is missing")
    sys.exit()


try:
    from bp_bvr import bvr_checksum
except:
    tkMessageBox.showwarning(u"Missing file", u"bp_bvr.py is missing")
    sys.exit()


try:
    import MySQLdb
except:
    tkMessageBox.showwarning(u"Error", u"Module mysqldb is not correctly installed !")
    sys.exit()

try:
    db = MySQLdb.connect(host=bp_connect.serveur, user=bp_connect.identifiant, passwd=bp_connect.secret, db=bp_connect.base, charset='latin1')
except:
    tkMessageBox.showwarning(u"MySQL", u"Cannot connect to database")
    sys.exit()

db.autocommit(True)

cursor = db.cursor()


def MCWidget(parent, key, row, column, rowspan=1, columnspan=1, value=None, accident=False, readonly=False, side_by_side=True, fg='black', field_fg='black'):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    frame = tk.Frame(parent)
    tk.Label(frame, text=labels_text[key], font=labels_font[key], fg=fg).pack(side=tk.LEFT)
    radiovar = tk.BooleanVar()
    radiovar.set(accident)
    maladie = tk.Radiobutton(frame, text=labels_text.maladie, variable=radiovar, value=False, font=fields_font[key], disabledforeground='black')
    accident = tk.Radiobutton(frame, text=labels_text.accident, variable=radiovar, value=True, font=fields_font[key], disabledforeground='black')
    if readonly:
        maladie.config(state=tk.DISABLED)
        accident.config(state=tk.DISABLED)
    accident.pack(side=tk.RIGHT, padx=20)
    maladie.pack(side=tk.RIGHT)
    frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=tk.NSEW)

    frame = tk.Frame(parent)
    scroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
    var = tk.Text(frame, yscrollcommand=scroll.set, relief=tk.SUNKEN, borderwidth=1, width=60, height=fields_height[key], font=fields_font[key], wrap=tk.WORD, fg=field_fg)
    scroll.config(command=var.yview)
    var.grid(row=0, column=0, sticky=tk.NSEW)
    scroll.grid(row=0, column=1, pady=3, sticky=tk.N+tk.S)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid(row=row+rowshift, column=column+colshift, rowspan=rowspan, columnspan=columnspan, sticky=tk.NSEW)
    if value:
        var.insert(1.0, value.replace('\n\n', '\n').strip())
    if readonly:
        var['state'] = tk.DISABLED
    return var, radiovar


def TarifWidget(parent, table, key, row, column, optional=True, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black', want_widget=False):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=labels_text[key], font=labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    try:
        cursor.execute("""SELECT description, prix_cts FROM %s ORDER BY prix_cts""" % table)
        tarifs = [(0, '', 'Aucun(e)')] if optional else []
        for description, prix_cts in cursor:
            label = u'%s : %0.2f CHF' % (description, prix_cts/100.)
            tarifs.append((prix_cts, description, label))
    except:
        traceback.print_exc()
        tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
        tarifs = [u"-- ERREUR --"]
    var = tk.StringVar()
    try:
        if value is None and optional is True:
            idx = 0
        else:
            idx = [(p, d) for p, d, l in tarifs].index(value)
        var.set(tarifs[idx][2])
    except ValueError:
        pass

    widget = tk.OptionMenu(parent, var, *[l for p, d, l in tarifs])
    if readonly:
        widget.config(state=tk.DISABLED)
    widget.grid(row=row+rowshift, column=column+colshift, sticky=tk.W+tk.E)
    if want_widget:
        return var, widget
    return var


class Patient(bp_Dialog.Dialog):
    def __init__(self, parent, id_patient=None, readonly=False):
        self.patient = PatientModel.load(cursor, id_patient) if id_patient is not None else PatientModel()
        self.readonly = readonly and self.patient
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        if not self.patient:
            tk.Button(box, text=buttons_text.ok_new_consult, command=self.add_1ere_Consult).pack(side=tk.LEFT)
            tk.Button(box, text=buttons_text.save_close, command=self.addEntry).pack(side=tk.LEFT)
        elif not self.readonly:
            tk.Button(box, text=buttons_text.change, command=self.updateEntry).pack(side=tk.LEFT)
        tk.Button(box, text=buttons_text.cancel, command=self.cancel).pack(side=tk.LEFT)

        self.bind("<Escape>", self.cancel)

        box.pack()

    def set_patient_fields(self):
        patient = self.patient
        patient.date_naiss = parse_date(self.date_naissVar.get().strip())
        patient.date_ouverture = parse_date(self.date_ouvVar.get().strip())
        patient.therapeute = self.therapeuteVar.get()
        patient.sex = self.sexVar.get()
        patient.nom = self.nomVar.get().strip()
        patient.prenom = self.prenomVar.get().strip()
        patient.ATCD_perso = getattr(patient, 'ATCD_perso', u"")
        patient.ATCD_fam = getattr(patient, 'ATCD_fam', u"")
        patient.medecin = self.medecinVar.get(1.0, tk.END).strip()
        patient.autre_medecin = self.autre_medecinVar.get(1.0, tk.END).strip()
        patient.phone = self.phoneVar.get().strip()
        patient.portable = self.portableVar.get().strip()
        patient.profes_phone = self.profes_phoneVar.get().strip()
        patient.mail = self.mailVar.get().strip()
        patient.adresse = self.adresseVar.get(1.0, tk.END).strip()
        patient.ass_compl = self.ass_complVar.get().strip()
        patient.profes = self.profesVar.get().strip()
        patient.etat = self.etatVar.get().strip()
        patient.envoye = self.envoyeVar.get().strip()
        patient.divers = self.diversVar.get(1.0, tk.END).strip()
        patient.important = self.importantVar.get(1.0, tk.END).strip()

    def addEntry(self, avec_anamnese=False):
        patient = self.patient
        try:
            parse_date(self.date_naissVar.get().strip())
            parse_date(self.date_ouvVar.get().strip())
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.invalid_error, errors_text.invalid_date)
            return
        if not self.sexVar.get() or not self.therapeuteVar.get() or not self.nomVar.get().strip() or not self.prenomVar.get().strip():
            tkMessageBox.showwarning(windows_title.invalid_error, errors_text.missing_data)
            return
        try:
            self.set_patient_fields()
            self.patient.save(cursor)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_insert)
            return
        self.cancel()
        if avec_anamnese:
            Consultation(self.parent, patient.id)

    def updateEntry(self):
        try:
            self.set_patient_fields()
            self.patient.save(cursor)
            self.cancel()
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)

    def add_1ere_Consult(self):
        self.addEntry(avec_anamnese=True)

    def body(self, master):
        if self.patient:
            title = windows_title.patient
        else:
            title = windows_title.new_patient
        self.title(title)
        self.geometry('+200+5')
        # self.geometry("1024x710")

        patient = self.patient
        if patient.date_ouverture is None:
            patient.date_ouverture = datetime.date.today()

        try:
            cursor.execute("""SELECT therapeute, login FROM therapeutes""")
            therapeutes = []
            for t, login in cursor:
                therapeutes.append(t)
                if login == LOGIN and patient.therapeute is None:
                    patient.therapeute = t
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

        def mandatory(value):
            if value:
                return 'black'
            return 'red'

        if patient:
            EntryWidget(master, key='id', row=0, column=2, value=patient.id, readonly=True)
        self.sexVar, focus_widget = RadioWidget(master, key='sexe', row=0, column=0, fg=mandatory(patient.sex), options=[(u'Mme', u'F'), (u'Mr', u'M'), (u'Enfant', u'E')], value=patient.sex, readonly=self.readonly, want_widget=True)

        self.nomVar = EntryWidget(master, key='nom', row=1, column=0, fg=mandatory(patient.nom), value=patient.nom, readonly=self.readonly)
        self.therapeuteVar = OptionWidget(master, key='therapeute', row=1, column=2, fg=mandatory(patient.therapeute), value=patient.therapeute, options=therapeutes, readonly=self.readonly)

        self.prenomVar = EntryWidget(master, key='prenom', row=2, column=0, fg=mandatory(patient.prenom), value=patient.prenom, readonly=self.readonly)

        if patient.date_naiss:
            key = 'naissance'
            fg = 'black'
            date_naiss = patient.date_naiss.strftime(DATE_FMT)
        else:
            key = 'naissance_le'
            fg = 'red'
            date_naiss = "JJ.MM.AAAA"
        self.date_naissVar = EntryWidget(master, key=key, row=3, column=0, fg=fg, value=date_naiss, readonly=self.readonly)
        self.date_ouvVar = EntryWidget(master, key='date_ouverture', row=3, column=2, value=patient.date_ouverture.strftime(DATE_FMT), readonly=self.readonly)

        self.phoneVar = EntryWidget(master, key='tel_fix', row=4, column=0, value=patient.phone, readonly=self.readonly)
        self.importantVar = TextWidget(master, key='important', row=4, column=2, rowspan=2, value=patient.important, readonly=self.readonly, field_fg='red')
        self.portableVar = EntryWidget(master, key='portable', row=5, column=0, value=patient.portable, readonly=self.readonly)

        self.profes_phoneVar = EntryWidget(master, key='tel_prof', row=6, column=0, value=patient.profes_phone, readonly=self.readonly)
        self.medecinVar = TextWidget(master, key='medecin', row=6, column=2, rowspan=2, value=patient.medecin, readonly=self.readonly)
        self.mailVar = EntryWidget(master, key='mail', row=7, column=0, value=patient.mail, readonly=self.readonly)

        self.adresseVar = TextWidget(master, key='adr_priv', row=8, column=0, value=patient.adresse, readonly=self.readonly)
        self.autre_medecinVar = TextWidget(master, key='medecinS', row=8, column=2, rowspan=3, value=patient.autre_medecin, readonly=self.readonly)

        self.ass_complVar = EntryWidget(master, key='ass_comp', row=11, column=0, value=patient.ass_compl, readonly=self.readonly)

        self.profesVar = EntryWidget(master, key='profes', row=12, column=0, value=patient.profes, readonly=self.readonly)
        self.etatVar = EntryWidget(master, key='etat', row=12, column=2, value=patient.etat, readonly=self.readonly)

        self.envoyeVar = EntryWidget(master, key='envoye', row=13, column=0, value=patient.envoye, readonly=self.readonly)

        self.diversVar = TextWidget(master, key='remarques', row=14, column=0, columnspan=3, value=patient.divers, readonly=self.readonly)

        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(3, weight=1)
        master.grid_rowconfigure(4, weight=1)
        master.grid_rowconfigure(5, weight=1)
        master.grid_rowconfigure(6, weight=1)
        master.grid_rowconfigure(7, weight=1)
        master.grid_rowconfigure(8, weight=1)
        master.grid_rowconfigure(14, weight=1)

        return focus_widget


class GererPatients(bp_Dialog.Dialog):
    def __init__(self, parent, action):
        self.action = action
        assert action in ('patient', 'gerer_consultations', 'supprimer', 'nouvelle_consultation')
        if action == 'patient':
            self.action_class = Patient
            self.title_str = windows_title.show_change_patient
        elif action == 'gerer_consultations':
            def act(parent, id_patient, readonly):
                GererConsultations(parent, id_patient, 'afficher')
            self.action_class = act
            self.title_str = windows_title.show_change_consult
        elif action == 'supprimer':
            self.title_str = windows_title.delete_patient
        elif action == 'nouvelle_consultation':
            self.action_class = Consultation
            self.title_str = windows_title.patients_db
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        tk.Button(box, text=buttons_text.search, command=self.recherche).pack(side=tk.LEFT)
        if self.action == 'patient':
            tk.Button(box, text=buttons_text.show_patient, fg='blue', command=self.readonly_action).pack(side=tk.LEFT)
            tk.Button(box, text=buttons_text.change_patient, fg='red', command=self.trigger_action).pack(side=tk.LEFT)
        elif self.action == 'gerer_consultations':
            tk.Button(box, text=buttons_text.show_consults, command=self.trigger_action).pack(side=tk.LEFT)
        elif self.action == 'supprimer':
            tk.Button(box, text=buttons_text.delete_patient, fg='red', command=self.supprime).pack(side=tk.LEFT)
            tk.Button(box, text=buttons_text.show_consults, fg='blue', command=self.supprime_consultation).pack(side=tk.LEFT)
        elif self.action == 'nouvelle_consultation':
            tk.Button(box, text=buttons_text.new_consult, fg='blue', command=self.trigger_action).pack(side=tk.LEFT)
            tk.Button(box, text=buttons_text.show_all_consult, command=self.liste_consultations).pack(side=tk.LEFT)
        tk.Button(box, text=buttons_text.cancel, command=self.cancel).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        self.bind("<Return>", lambda event: self.recherche())
        box.pack()

    def recherche(self):
        try:
            cursor.execute("""SELECT id, sex, nom, prenom, (SELECT count(*) FROM consultations WHERE id = patients.id)
                                 FROM patients
                                WHERE nom LIKE %s AND prenom LIKE %s
                             ORDER BY nom""",
                           [self.nomRec.get().strip(), self.prenomRec.get().strip()])
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_search)
        self.results = []
        self.select.delete(0, tk.END)
        for id, sex, nom, prenom, n_consult in cursor:
            self.select.insert(tk.END, nom+u', '+prenom+u', '+sex)
            self.results.append(id)

    def readonly_action(self):
        self.trigger_action(readonly=True)

    def trigger_action(self, readonly=False):
        selection = self.select.curselection()
        if selection:
            id = self.results[int(selection[0])]
            self.action_class(self, id_patient=id, readonly=readonly)

    def liste_consultations(self):
        selection = self.select.curselection()
        if selection:
            id = self.results[int(selection[0])]
            ListeConsultations(self.parent, id)

    def supprime_consultation(self):
        selection = self.select.curselection()
        if selection:
            id = self.results[int(selection[0])]
            GererConsultations(self.parent, id, 'supprimer')

    def supprime(self):
        selection = self.select.curselection()
        if selection:
            id = self.results[int(selection[0])]
            try:
                cursor.execute("""SELECT sex, nom, prenom, date_naiss
                                    FROM patients
                                    WHERE id = %s""",
                               [id])
                sex, nom, prenom, date_naiss = cursor.fetchone()
            except:
                traceback.print_exc()
                tkMessageBox.showwarning(windows_title.db_error, errors_text.db_search)
                return
            if tkMessageBox.askyesno(windows_title.delete, labels_text.suppr_def_1+u'\n'+str(sex+u" "+prenom+u" "+nom)+labels_text.suppr_def_2+date_naiss.strftime(DATE_FMT)+u'\n'+labels_text.suppr_def_3):
                try:
                    cursor.execute("DELETE FROM rappels WHERE id_consult IN (SELECT id_consult FROM consultations WHERE id=%s", [id])
                    cursor.execute("DELETE FROM consultations WHERE id=%s", [id])
                    cursor.execute("DELETE FROM patients WHERE id=%s", [id])
                    tkMessageBox.showinfo(windows_title.done, labels_text.pat_sup_1+str(prenom+u" "+nom+u" ")+labels_text.pat_sup_2)
                except:
                    traceback.print_exc()
                    tkMessageBox.showwarning(windows_title.db_error, errors_text.db_delete)
        self.recherche()

    def body(self, master):
        self.title(self.title_str)
        self.geometry('+200+5')

        frame = tk.Frame(master)
        self.nomRec = EntryWidget(frame, key='nom', row=0, column=0, value=u'%')
        self.prenomRec = EntryWidget(frame, key='prenom', row=1, column=0, value=u'%')
        frame.grid(row=0, column=0, sticky=tk.NSEW)
        frame.grid_columnconfigure(1, weight=1)

        self.select = ListboxWidget(master, key='rp', row=1, column=0)

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)


class ListeConsultations(bp_Dialog.Dialog):
    def __init__(self, parent, id_patient):
        self.id_patient = id_patient
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        tk.Button(box, text=buttons_text.ok, command=self.cancel).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def auto_affiche(self):
        try:
            patient = PatientModel.load(cursor, self.id_patient)
        except:
            print "id_patient:", self.id_patient
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_show)
            return
        self.toutes.tag_config("date", foreground="red", font=("Helvetica", 15, "bold"))
        self.toutes.tag_config("non_paye", foreground="darkred", font=("Helvetica", 15, "bold"))
        self.toutes.tag_config("titre", foreground="blue", font=("Helvetica", 15))
        self.toutes.tag_config("personne", foreground="black", font=("Helvetica", 15, "bold"))
        self.toutes.tag_config("important", foreground="darkblue", font=("Helvetica", 15, "bold"))
        self.toutes.insert(tk.END, patient.sex+u' '+patient.prenom+u' '+patient.nom+u', '+patient.date_naiss.strftime(DATE_FMT)+u'\n', "personne")
        self.toutes.insert(tk.END, labels_text.atcdp+u'\n', "titre")
        self.toutes.insert(tk.END, patient.ATCD_perso+u'\n')
        self.toutes.insert(tk.END, labels_text.atcdf+u'\n', "titre")
        self.toutes.insert(tk.END, patient.ATCD_fam+u'\n')
        self.toutes.insert(tk.END, labels_text.important+u'\n', "important")
        self.toutes.insert(tk.END, patient.important+u'\n')
        self.toutes.insert(tk.END, labels_text.ass_comp+u'\n', "titre")
        self.toutes.insert(tk.END, patient.ass_compl+u'\n')
        for consult in ConsultationModel.yield_all(cursor, where=dict(id=patient.id), order='-date_consult'):
            self.toutes.insert(tk.END, u'\n********** '+labels_text.date_consult+consult.date_consult.strftime(DATE_FMT)+u' **********'+u'\n', "date")
            if consult.paye_le is None:
                self.toutes.insert(tk.END, u'!!!!! Non-payé !!!!!\n', "non_paye")
            if consult.EG.strip():
                self.toutes.insert(tk.END, labels_text.eg+u'\n', "titre")
                self.toutes.insert(tk.END, consult.EG+u'\n')
            if consult.therapeute:
                self.toutes.insert(tk.END, labels_text.therapeute+u'\n', "titre")
                self.toutes.insert(tk.END, consult.therapeute+u'\n')
            self.toutes.insert(tk.END, labels_text.mc+u'\n', "titre")
            if consult.MC_accident:
                self.toutes.insert(tk.END, labels_text.accident+u'\n')
            else:
                self.toutes.insert(tk.END, labels_text.maladie+u'\n')
            self.toutes.insert(tk.END, consult.MC+u'\n')
            if consult.APT_thorax.strip():
                self.toutes.insert(tk.END, labels_text.thorax+u'\n', "titre")
                self.toutes.insert(tk.END, consult.APT_thorax+u'\n')
            if consult.APT_abdomen.strip():
                self.toutes.insert(tk.END, labels_text.abdomen+u'\n', "titre")
                self.toutes.insert(tk.END, consult.APT_abdomen+u'\n')
            if consult.APT_tete.strip():
                self.toutes.insert(tk.END, labels_text.tete+u'\n', "titre")
                self.toutes.insert(tk.END, consult.APT_tete+u'\n')
            if consult.APT_MS.strip():
                self.toutes.insert(tk.END, labels_text.ms+u'\n', "titre")
                self.toutes.insert(tk.END, consult.APT_MS+u'\n')
            if consult.APT_MI.strip():
                self.toutes.insert(tk.END, labels_text.mi+u'\n', "titre")
                self.toutes.insert(tk.END, consult.APT_MI+u'\n')
            if consult.APT_system.strip():
                self.toutes.insert(tk.END, labels_text.gen+u'\n', "titre")
                self.toutes.insert(tk.END, consult.APT_system+u'\n')
            if consult.A_osteo.strip():
                self.toutes.insert(tk.END, labels_text.a_osteo+u'\n', "titre")
                self.toutes.insert(tk.END, consult.A_osteo+u'\n')
            if consult.exam_phys.strip():
                self.toutes.insert(tk.END, labels_text.exph+u'\n', "titre")
                self.toutes.insert(tk.END, consult.exam_phys+u'\n')
            if consult.traitement.strip():
                self.toutes.insert(tk.END, labels_text.ttt+u'\n', "titre")
                self.toutes.insert(tk.END, consult.traitement+u'\n')
            if consult.exam_pclin.strip():
                self.toutes.insert(tk.END, labels_text.expc+u'\n', "titre")
                self.toutes.insert(tk.END, consult.exam_pclin+u'\n')
            if consult.divers.strip():
                self.toutes.insert(tk.END, labels_text.remarques+u'\n', "titre")
                self.toutes.insert(tk.END, consult.divers+u'\n')
            if consult.paye.strip():
                self.toutes.insert(tk.END, labels_text.paye+u'\n', "titre")
                self.toutes.insert(tk.END, consult.paye+u'\n')

    def body(self, master):
        self.geometry('+200+5')
        # self.geometry("700x710")

        self.toutes = TextWidget(master, key='ttes_cons', row=0, column=0, side_by_side=False, fg='blue')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)

        self.auto_affiche()


def alpha_to_num(char):
    return (ord(char) - ord('A')) % 100


class Consultation(bp_Dialog.Dialog):
    def __init__(self, parent, id_patient, id_consult=None, readonly=False):
        self.patient = PatientModel.load(cursor, id_patient)
        self.consultation = ConsultationModel.load(cursor, id_consult) if id_consult is not None else ConsultationModel(id=id_patient)
        self.consultation.patient = self.patient
        self.readonly = readonly
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        if self.readonly:
            tk.Button(box, text=buttons_text.ok, command=self.cancel).pack(side=tk.LEFT)
        else:
            tk.Button(box, text=buttons_text.save_close, command=self.modif).pack(side=tk.LEFT)  # Was B11
            tk.Button(box, text=buttons_text.cancel, command=self.verify_cancel).pack(side=tk.LEFT)
        if self.consultation:
            tk.Button(box, text=buttons_text.reprint, command=self.generate_pdf).pack(side=tk.LEFT)
        cursor.execute("SELECT count(*) FROM consultations WHERE id = %s", [self.patient.id])
        count, = cursor.fetchone()
        if count > 0:
            tk.Button(box, text=u"Toutes les consultations", command=lambda: ListeConsultations(self.parent, self.patient.id)).pack(side=tk.LEFT)
        self.bind("<Escape>", self.verify_cancel)
        box.pack()

    def verify_cancel(self, *args):
        if self.readonly or tkMessageBox.askyesno(windows_title.really_cancel, labels_text.really_cancel, default=tkMessageBox.NO):
            self.cancel()

    def get_cost(self):
        description_prix, prix = self.prixVar.get().split(u' : ')
        prix_cts = int(float(prix[:-4]) * 100 + 0.5)
        try:
            description_majoration, majoration = self.majorationVar.get().split(u' : ')
            majoration_cts = int(float(majoration[:-4]) * 100 + 0.5)
        except ValueError:
            description_majoration = ""
            majoration_cts = 0
        try:
            description_frais_admin, frais_admin = self.frais_adminVar.get().split(u' : ')
            frais_admin_cts = int(float(frais_admin[:-4]) * 100 + 0.5)
        except ValueError:
            description_frais_admin = ""
            frais_admin_cts = 0
        return description_prix, prix_cts, description_majoration, majoration_cts, description_frais_admin, frais_admin_cts

    def set_consultation_fields(self):
        consult = self.consultation
        consult.date_consult = parse_date(self.date_ouvcVar.get().strip())
        consult.MC = self.MCVar.get(1.0, tk.END).strip()
        consult.MC_accident = self.MC_accidentVar.get()
        consult.EG = self.EGVar.get(1.0, tk.END).strip()
        consult.exam_pclin = self.exam_pclinVar.get(1.0, tk.END).strip()
        consult.exam_phys = self.exam_physVar.get(1.0, tk.END).strip()
        consult.paye = self.payeVar.get(1.0, tk.END).strip()
        consult.divers = self.diversVar.get(1.0, tk.END).strip()
        consult.APT_thorax = self.APT_thoraxVar.get(1.0, tk.END).strip()
        consult.APT_abdomen = self.APT_abdomenVar.get(1.0, tk.END).strip()
        consult.APT_tete = self.APT_teteVar.get(1.0, tk.END).strip()
        consult.APT_MS = self.APT_MSVar.get(1.0, tk.END).strip()
        consult.APT_MI = self.APT_MIVar.get(1.0, tk.END).strip()
        consult.APT_system = self.APT_systemVar.get(1.0, tk.END).strip()
        consult.A_osteo = self.A_osteoVar.get(1.0, tk.END).strip()
        consult.traitement = self.traitementVar.get(1.0, tk.END).strip()
        consult.therapeute = self.therapeuteVar.get().strip()
        consult.prix_txt, consult.prix_cts, consult.majoration_txt, consult.majoration_cts, consult.frais_admin_txt, consult.frais_admin_cts = self.get_cost()
        consult.paye_par = self.paye_parVar.get().strip()
        if consult.paye_le is None and consult.paye_par not in (u'BVR', u'CdM', u'Dû', u'PVPE'):
            consult.paye_le = datetime.date.today()
        try:
            if consult.paye_par in (u'BVR', u'PVPE'):
                cursor.execute("UPDATE bvr_sequence SET counter = @counter := counter + 1")
                cursor.execute("SELECT prenom, nom, @counter FROM patients WHERE id = %s", [consult.id])  # Yes, that's the patient id...
                firstname, lastname, bvr_counter = cursor.fetchone()
                bv_ref = u'%06d%010d%02d%02d%02d%04d' % (bvr.prefix, bvr_counter, alpha_to_num(firstname[0]), alpha_to_num(lastname[0]), consult.date_consult.month, consult.date_consult.year)
                consult.bv_ref = bv_ref + str(bvr_checksum(bv_ref))
            else:
                consult.bv_ref = None
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

    def modif(self):
        if not self.prixVar.get().strip() or not self.paye_parVar.get().strip():
            tkMessageBox.showwarning(windows_title.missing_error, errors_text.missing_payment_info)
            return
        if not self.therapeuteVar.get().strip():
            tkMessageBox.showwarning(windows_title.missing_error, errors_text.missing_therapeute)
            return
        self.set_consultation_fields()
        try:
            if self.consultation:
                cursor.execute("""SELECT paye_par FROM consultations WHERE id_consult=%s""", [self.consultation.id_consult])
                old_paye_par, = cursor.fetchone()
                generate_pdf = self.consultation.paye_par != old_paye_par
                if old_paye_par != self.consultation.paye_par and self.consultation.paye_par in (u'BVR', u'PVPE') and self.consultation.status != STATUS_ABANDONED:
                    self.consultation.status = STATUS_OPENED
                    self.consultation.paye_le = None
            else:
                self.consultation.status = STATUS_OPENED
                if self.consultation.paye_par in (u'Cash', u'Carte'):
                    self.consultation.status = STATUS_PAYED
                generate_pdf = self.consultation.paye_par not in (u'CdM', u'Dû')
            self.consultation.save(cursor)

            self.patient.important = self.importantVar.get(1.0, tk.END).strip()
            self.patient.ATCD_perso = self.ATCD_persoVar.get(1.0, tk.END).strip()
            self.patient.ATCD_fam = self.ATCD_famVar.get(1.0, tk.END).strip()
            self.patient.save(cursor)
            self.cancel()
            if generate_pdf:
                self.generate_pdf()
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)

    def generate_pdf(self):
        ts = datetime.datetime.now().strftime('%H')
        filename = normalize_filename(u'%s_%s_%s_%s_%sh.pdf' % (self.patient.nom, self.patient.prenom, self.patient.sex, self.consultation.date_consult, ts))
        bp_factures.consultations(filename, cursor, [self.consultation])
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
        os.system(cmd)

    def body(self, master):
        self.geometry("+200+5")
        consult = self.consultation
        try:
            if consult.therapeute is not None:
                consult.therapeute = consult.therapeute.strip()  # Sanity guard against old data
            cursor.execute("""SELECT therapeute, login FROM therapeutes ORDER BY therapeute""")
            therapeutes = [u'']
            for t, login in cursor:
                therapeutes.append(t)
                if consult.therapeute is None and login == LOGIN:
                    consult.therapeute = t
            if consult:
                title = windows_title.consultation % (consult.date_consult, self.patient.sex, self.patient.nom)
            else:
                consult.date_consult = datetime.date.today()
                consult.MC_accident = False
                title = windows_title.new_consultation % (self.patient.sex, self.patient.nom)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

        self.title(title)

        # +----------+----------+----------+
        # |    MC    |    EG    |  pclin   |
        # +----------+----------+          |
        # | ATCDperso| ATCD_fam |          |
        # +----------+----------+----------+
        # |  thorax  | abdomen  |  phys    |
        # +----------+----------+          |
        # |   tete   |    MS    |          |
        # +----------+----------+----------+
        # |    MI    |  system  |important |
        # +----------+----------+----------+
        # |  osteo   |traitement|  divers  |
        # +----------+----------+----------+
        # | dateouvc |therapeute|   paye   |
        # +----------+----------+          |
        # |seanceprix| paye par |          |
        # +----------+----------+----------+
        self.MCVar, self.MC_accidentVar = MCWidget(master, key='mc', row=0, column=0, side_by_side=False, fg='blue', field_fg='blue', value=consult.MC, accident=consult.MC_accident, readonly=self.readonly)
        self.EGVar = TextWidget(master, key='eg', row=0, column=1, side_by_side=False, value=consult.EG, readonly=self.readonly)
        self.exam_pclinVar = TextWidget(master, key='expc', row=0, column=2, rowspan=3, side_by_side=False, value=consult.exam_pclin, readonly=self.readonly)

        self.ATCD_persoVar = TextWidget(master, key='atcdp', row=2, column=0, side_by_side=False, value=self.patient.ATCD_perso, readonly=self.readonly)
        self.ATCD_famVar = TextWidget(master, key='atcdf', row=2, column=1, side_by_side=False, value=self.patient.ATCD_fam, readonly=self.readonly)

        self.APT_thoraxVar = TextWidget(master, key='thorax', row=4, column=0, side_by_side=False, value=consult.APT_thorax, readonly=self.readonly)
        self.APT_abdomenVar = TextWidget(master, key='abdomen', row=4, column=1, side_by_side=False, value=consult.APT_abdomen, readonly=self.readonly)
        self.exam_physVar = TextWidget(master, key='exph', row=4, column=2, rowspan=3, side_by_side=False, value=consult.exam_phys, readonly=self.readonly)

        self.APT_teteVar = TextWidget(master, key='tete', row=6, column=0, side_by_side=False, value=consult.APT_tete, readonly=self.readonly)
        self.APT_MSVar = TextWidget(master, key='ms', row=6, column=1, side_by_side=False, value=consult.APT_MS, readonly=self.readonly)

        self.APT_MIVar = TextWidget(master, key='mi', row=8, column=0, side_by_side=False, value=consult.APT_MI, readonly=self.readonly)
        self.APT_systemVar = TextWidget(master, key='gen', row=8, column=1, side_by_side=False, value=consult.APT_system, readonly=self.readonly)
        self.importantVar = TextWidget(master, key='important', row=8, column=2, side_by_side=False, value=self.patient.important, fg='red', field_fg='red', readonly=self.readonly)

        self.A_osteoVar = TextWidget(master, key='a_osteo', row=10, column=0, side_by_side=False, value=consult.A_osteo, readonly=self.readonly)
        self.traitementVar = TextWidget(master, key='ttt', row=10, column=1, side_by_side=False, fg='darkgreen', value=consult.traitement, readonly=self.readonly)
        self.diversVar = TextWidget(master, key='remarques', row=10, column=2, side_by_side=False, value=consult.divers, readonly=self.readonly)

        self.date_ouvcVar = EntryWidget(master, key='date_ouverture', row=12, column=0, side_by_side=False, value=consult.date_consult.strftime(DATE_FMT), readonly=self.readonly)
        self.therapeuteVar = OptionWidget(master, key='therapeute', row=12, column=1, side_by_side=False, value=consult.therapeute, options=therapeutes, readonly=self.readonly)
        self.payeVar = TextWidget(master, key='paye', row=12, column=2, rowspan=3, side_by_side=False, value=consult.paye, field_fg='red', readonly=self.readonly)

        f = tk.Frame(master)
        self.prixVar = TarifWidget(f, table='tarifs', key='seance', row=0, column=0, optional=False, side_by_side=True, value=(consult.prix_cts, consult.prix_txt), readonly=self.readonly)
        self.majorationVar = TarifWidget(f, table='majorations', key='majoration', row=1, column=0, side_by_side=True, value=(consult.majoration_cts, consult.majoration_txt), readonly=self.readonly)
        self.frais_adminVar = TarifWidget(f, table='frais_admins', key='frais_admin', row=2, column=0, side_by_side=True, value=(consult.frais_admin_cts, consult.frais_admin_txt), readonly=self.readonly)
        f.grid(row=14, column=0, rowspan=3, sticky=tk.W+tk.E)
        f.grid_columnconfigure(1, weight=1)

        self.paye_parVar = RadioWidget(master, key='paye_par', row=14, column=1, side_by_side=False, value=consult.paye_par, options=bp_custo.MOYEN_DE_PAYEMENT, readonly=self.readonly)
        if consult and consult.paye_le:
            frame = master.grid_slaves(row=15, column=1)[0]
            tk.Label(frame, text=labels_text.paye_le+u' '+str(consult.paye_le), font=labels_font.paye_le).pack(side=tk.RIGHT)

        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)
        master.grid_rowconfigure(1, weight=1)
        master.grid_rowconfigure(3, weight=1)
        master.grid_rowconfigure(5, weight=1)
        master.grid_rowconfigure(7, weight=1)
        master.grid_rowconfigure(9, weight=1)
        master.grid_rowconfigure(11, weight=1)
        master.grid_rowconfigure(13, weight=1)
        master.grid_rowconfigure(15, weight=1)


class GererConsultations(bp_Dialog.Dialog):
    def __init__(self, parent, id_patient, action):
        self.id_patient = id_patient
        self.action = action
        assert action in ('afficher', 'supprimer')
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        if self.action == 'afficher':
            tk.Button(box, text=buttons_text.show_consult, fg='blue', command=self.affiche).pack(side=tk.LEFT)
            tk.Button(box, text=buttons_text.change_consult, fg='red', command=self.modif).pack(side=tk.LEFT)
            tk.Button(box, text=buttons_text.show_all_consult, fg='blue', command=lambda: ListeConsultations(self.parent, self.id_patient)).pack(side=tk.LEFT)
        if self.action == 'supprimer':
            tk.Button(box, text=buttons_text.delete_consult, fg='red', command=self.supprime_c).pack(side=tk.LEFT)
        tk.Button(box, text=buttons_text.cancel, command=self.cancel).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def affiche_toutes(self):
        try:
            cursor.execute("""SELECT id_consult, date_consult, MC, paye_le
                                 FROM consultations
                                WHERE id=%s
                             ORDER BY date_consult DESC""",
                           [self.id_patient])
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_show)
        self.results = []
        self.select_consult.delete(0, tk.END)
        for id_consult, date_consult, MC, paye_le in cursor:
            self.select_consult.insert(tk.END, date_consult.strftime(DATE_FMT)+u' '+MC)
            if paye_le is None:
                self.select_consult.itemconfig(tk.END, fg="darkred")
            self.results.append(id_consult)

    def affiche(self):
        selection = self.select_consult.curselection()
        if selection:
            id_consult = self.results[int(selection[0])]
            Consultation(self.parent, self.id_patient, id_consult, readonly=True)

    def modif(self):
        selection = self.select_consult.curselection()
        if selection:
            id_consult = self.results[int(selection[0])]
            Consultation(self.parent, self.id_patient, id_consult)

    def supprime_c(self):
        selection = self.select_consult.curselection()
        if selection:
            id_consult = self.results[int(selection[0])]
            if tkMessageBox.askyesno(windows_title.delete, labels_text.sup_def_c):
                try:
                    cursor.execute("DELETE FROM rappels WHERE id_consult=%s", [id_consult])
                    cursor.execute("DELETE FROM consultations WHERE id_consult=%s", [id_consult])
                    tkMessageBox.showinfo(windows_title.done, labels_text.cons_sup)
                except:
                    traceback.print_exc()
                    tkMessageBox.showwarning(windows_title.db_error, errors_text.db_delete)
        self.affiche_toutes()

    def body(self, master):
        self.geometry('+200+5')

        try:
            cursor.execute("""SELECT nom, prenom, sex, therapeute, date_naiss
                                 FROM patients WHERE id = %s""", [self.id_patient])
            nom, prenom, sex, therapeute, date_naiss = cursor.fetchone()
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

        if self.action == 'afficher':
            self.title(windows_title.show_consultation % (sex, nom))
        else:
            self.title(windows_title.delete_consultation % (sex, nom))
        tk.Label(master, text=sex+u' '+prenom+u' '+nom, font=bp_custo.LABEL_BOLD).grid(row=0, column=0, sticky=tk.W)
        tk.Label(master, text=labels_text.naissance+u' '+date_naiss.strftime(DATE_FMT), font=bp_custo.LABEL_NORMAL).grid(row=1, column=0, sticky=tk.W)
        tk.Label(master, text=labels_text.therapeute+u' '+therapeute, font=bp_custo.LABEL_NORMAL).grid(row=2, column=0, sticky=tk.W)

        self.select_consult = ListboxWidget(master, key='rc', row=3, column=0)

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(3, weight=1)

        self.affiche_toutes()


class ManageCosts(bp_Dialog.Dialog):
    def __init__(self, parent, table):
        self.table = table
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Button(self, text=buttons_text.done, command=self.cancel)
        self.bind("<Escape>", self.cancel)
        return box

    def populate(self):
        self.listbox.delete(0, tk.END)
        d_width = 0
        for description, prix_cts in self.costs:
            d_width = max(d_width, len(description))
        for description, prix_cts in self.costs:
            self.listbox.insert(tk.END, u"%*s    %7.2f" % (-d_width, description, prix_cts/100.))
        self.listbox.selection_clear(0, tk.END)

    def select_cost(self, event):
        indexes = self.listbox.curselection()
        self.price.set(u"")
        self.description.set(u"")
        if indexes:
            index = indexes[0]
            if index == self.index:
                self.listbox.selection_clear(0, tk.END)
                self.index = None
                self.update.config(text=buttons_text.add)
                return
            self.index = index
            self.update.config(text=buttons_text.change)
            description, prix_cts = self.costs[index]
            self.description.set(description)
            self.price.set('%0.2f' % (prix_cts/100.))
        else:
            self.index = None
            self.update.config(text=buttons_text.add)

    def update_cost(self):
        indexes = self.listbox.curselection()
        update = bool(indexes)
        description = self.description.get().strip()
        try:
            prix_cts = int(float(self.price.get().strip()) * 100)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.invalid_error, errors_text.invalid_cost)
            return
        try:
            if update:
                key, _ = self.costs[indexes[0]]
                cursor.execute("""UPDATE %s SET description = %%s, prix_cts = %%s WHERE description = %%s""" % self.table,
                               [description, prix_cts, key])
                self.costs[indexes[0]] = (description, prix_cts)
            else:
                cursor.execute("""INSERT INTO %s (description, prix_cts) VALUES (%%s, %%s)""" % self.table,
                               [description, prix_cts])
                self.costs.append((description, prix_cts))
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()
        self.select_cost('ignore')

    def delete_cost(self):
        indexes = self.listbox.curselection()
        if indexes:
            try:
                key, _ = self.costs[indexes[0]]
                cursor.execute("""DELETE FROM %s WHERE description = %%s""" % self.table, [key])
                del self.costs[indexes[0]]
            except:
                traceback.print_exc()
                tkMessageBox.showwarning(windows_title.db_error, errors_text.db_delete)
        self.populate()
        self.select_cost('ignore')

    def body(self, master):
        try:
            cursor.execute("""SELECT description, prix_cts FROM %s""" % self.table)
            self.costs = list(cursor)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

        self.title(getattr(windows_title, 'manage_'+self.table))
        self.listbox = ListboxWidget(master, key=self.table, row=0, column=0, columnspan=3)
        self.listbox.config(selectmode=tk.SINGLE)
        self.listbox.bind('<<ListboxSelect>>', self.select_cost)
        self.index = None
        self.populate()
        self.description = EntryWidget(master, key='description', row=2, column=0, side_by_side=False)
        self.price = EntryWidget(master, key='prix', row=2, column=1, side_by_side=False)
        self.update = tk.Button(master, text=buttons_text.add, command=self.update_cost)
        self.update.grid(row=3, column=2)
        self.delete = tk.Button(master, text=buttons_text.delete, command=self.delete_cost)
        self.delete.grid(row=4, column=2)

        master.grid_rowconfigure(1, weight=2)
        master.grid_rowconfigure(3, weight=1)
        master.grid_rowconfigure(4, weight=1)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)


class GererCollegues(bp_Dialog.Dialog):
    def buttonbox(self):
        box = tk.Button(self, text=buttons_text.done, command=self.cancel)
        self.bind("<Escape>", self.cancel)
        return box

    def populate(self):
        self.listbox.delete(0, tk.END)
        t_width = l_width = 0
        for therapeute, login, entete in self.collegues:
            t_width = max(t_width, len(therapeute))
            l_width = max(l_width, len(login))
        for therapeute, login, entete in self.collegues:
            self.listbox.insert(tk.END, u"%*s    %*s    %s" % (-t_width, therapeute, -l_width, login, entete))
        self.listbox.selection_clear(0, tk.END)

    def select_collegue(self, event):
        indexes = self.listbox.curselection()
        self.entete.delete('1.0', tk.END)
        self.therapeute.set(u"")
        self.login.set(u"")
        if indexes:
            index = indexes[0]
            if index == self.index:
                self.listbox.selection_clear(0, tk.END)
                self.index = None
                self.update.config(text=buttons_text.add)
                return
            self.index = index
            self.update.config(text=buttons_text.change)
            therapeute, login, entete = self.collegues[index]
            self.therapeute.set(therapeute)
            self.login.set(login)
            self.entete.insert(tk.END, entete)
        else:
            self.index = None
            self.update.config(text=buttons_text.add)

    def update_collegue(self):
        therapeute = self.therapeute.get().strip()
        login = self.login.get().strip()
        entete = self.entete.get('1.0', tk.END).strip()
        try:
            if self.index:
                key, _, _ = self.collegues[self.index]
                cursor.execute("""UPDATE therapeutes SET therapeute = %s, login = %s, entete = %s WHERE therapeute = %s""",
                               [therapeute, login, entete, key])
                self.collegues[self.index] = (therapeute, login, entete)
            else:
                cursor.execute("""INSERT INTO therapeutes (therapeute, login, entete) VALUES (%s, %s, %s)""",
                               [therapeute, login, entete])
                self.collegues.append((therapeute, login, entete))
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()
        self.select_collegue('ignore')

    def delete_collegue(self):
        if self.index:
            try:
                key, _, _ = self.collegues[self.index]
                cursor.execute("""DELETE FROM therapeutes WHERE therapeute = %s""", [key])
                del self.collegues[self.index]
            except:
                traceback.print_exc()
                tkMessageBox.showwarning(windows_title.db_error, errors_text.db_delete)
        self.populate()
        self.select_collegue('ignore')

    def body(self, master):
        try:
            cursor.execute("""SELECT therapeute, login, entete FROM therapeutes ORDER BY therapeute""")
            self.collegues = list(cursor)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

        self.title(windows_title.manage_colleagues)
        self.listbox = ListboxWidget(master, key='collabos', row=0, column=0, columnspan=4)
        self.listbox.config(selectmode=tk.SINGLE)
        self.listbox.bind('<<ListboxSelect>>', self.select_collegue)
        self.index = None
        self.populate()
        self.therapeute = EntryWidget(master, key='therapeute', row=2, column=0, side_by_side=False)
        self.login = EntryWidget(master, key='login', row=2, column=1, side_by_side=False)
        self.entete = TextWidget(master, key='entete', row=2, column=2, rowspan=2, side_by_side=False)
        self.update = tk.Button(master, text=buttons_text.add, command=self.update_collegue)
        self.update.grid(row=3, column=3)
        self.delete = tk.Button(master, text=buttons_text.delete, command=self.delete_collegue)
        self.delete.grid(row=4, column=3)

        master.grid_rowconfigure(1, weight=2)
        master.grid_rowconfigure(3, weight=1)
        master.grid_rowconfigure(4, weight=1)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)


class GererAdresses(bp_Dialog.Dialog):
    def buttonbox(self):
        box = tk.Button(self, text=buttons_text.done, command=self.cancel)
        self.bind("<Escape>", self.cancel)
        return box

    def populate(self):
        self.listbox.delete(0, tk.END)
        i_width = a_width = 0
        for identifiant, address in self.addresses:
            i_width = max(i_width, len(identifiant))
            a_width = max(a_width, len(address.replace('\n', ', ')))
        for identifiant, address in self.addresses:
            self.listbox.insert(tk.END, u"%*s   %*s" % (-i_width, identifiant, -a_width, address.replace('\n', ', ')))
        self.listbox.selection_clear(0, tk.END)

    def select_address(self, event):
        indexes = self.listbox.curselection()
        self.identifiant.set(u"")
        self.address.delete('1.0', tk.END)
        if indexes:
            index = indexes[0]
            if index == self.index:
                self.listbox.selection_clear(0, tk.END)
                self.index = None
                self.update.config(text=buttons_text.add)
                return
            self.index = index
            self.update.config(text=buttons_text.change)
            identifiant, address = self.addresses[index]
            self.identifiant.set(identifiant)
            self.address.insert(tk.END, address)
        else:
            self.index = None
            self.update.config(text=buttons_text.add)

    def update_address(self):
        identifiant = self.identifiant.get().strip()
        address = self.address.get('1.0', tk.END).strip()
        try:
            if self.index:
                key, _ = self.addresses[self.index]
                cursor.execute("""UPDATE adresses SET id = %s, adresse = %s WHERE id = %s""",
                               [identifiant, address, key])
                self.addresses[self.index] = (identifiant, address)
            else:
                cursor.execute("""INSERT INTO adresses (id, adresse) VALUES (%s, %s)""",
                               [identifiant, address])
                self.addresses.append((identifiant, address))
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()
        self.select_address('ignore')

    def delete_address(self):
        if self.index:
            try:
                key, _ = self.addresses[self.index]
                cursor.execute("""DELETE FROM adresses WHERE id = %s""", [key])
                del self.addresses[self.index]
            except:
                traceback.print_exc()
                tkMessageBox.showwarning(windows_title.db_error, errors_text.db_delete)
        self.populate()
        self.select_address('ignore')

    def body(self, master):
        try:
            cursor.execute("SELECT id, adresse FROM adresses ORDER BY id")
            self.addresses = list(cursor)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

        self.title(windows_title.manage_addresses)
        self.listbox = ListboxWidget(master, key='addresses', row=0, column=0, columnspan=2)
        self.listbox.config(selectmode=tk.SINGLE)
        self.listbox.bind('<<ListboxSelect>>', self.select_address)
        self.index = None
        self.populate()
        self.identifiant = EntryWidget(master, key='identifiant', row=2, column=0)
        self.address = TextWidget(master, key='address', row=3, column=0)
        button_frame = tk.Frame(master)
        button_frame.grid(row=4, column=0, columnspan=2)
        self.update = tk.Button(button_frame, text=buttons_text.add, command=self.update_address)
        self.update.grid(row=0, column=0)
        self.delete = tk.Button(button_frame, text=buttons_text.delete, command=self.delete_address)
        self.delete.grid(row=0, column=1)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        master.grid_rowconfigure(1, weight=2)
        master.grid_rowconfigure(3, weight=1)
        master.grid_columnconfigure(1, weight=1)


class FactureManuelle(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.option_add('*font', 'Helvetica -15')

        menubar = tk.Menu(self)

        adminmenu = tk.Menu(menubar, tearoff=0)
        adminmenu.add_command(label=menus_text.manage_addresses, command=self.manage_addresses)

        menubar.add_cascade(label=menus_text.admin, menu=adminmenu)
        self.config(menu=menubar)

        default_therapeute = ''
        self.therapeutes = {}
        cursor.execute("SELECT therapeute, login, entete FROM therapeutes")
        for therapeute, login, entete in cursor:
            self.therapeutes[therapeute] = entete + u'\n\n' + labels_text.adresse_pog
            if login == LOGIN:
                default_therapeute = therapeute

        self.therapeute = tk.StringVar()
        self.therapeute.set(default_therapeute)
        self.therapeute.trace('w', self.change_therapeute)
        tk.OptionMenu(self, self.therapeute, *self.therapeutes.keys()).grid(row=0, column=0, sticky=tk.EW)
        self.therapeuteAddress = tk.Label(self, justify=tk.LEFT, state=tk.DISABLED)
        self.therapeuteAddress.grid(row=1, column=0, sticky=tk.NSEW)

        self.prefill = tk.StringVar()
        self.prefill.set(u"Adresse manuelle")
        self.prefill.trace('w', self.change_address)
        self.prefillWidget = tk.OptionMenu(self, self.prefill, u"Adresse manuelle")
        self.prefillWidget.grid(row=0, column=1, sticky=tk.EW)
        self.address = tk.Text(self, relief=tk.SUNKEN, borderwidth=1, width=40, height=6)
        self.address.grid(row=1, column=1, sticky=tk.NSEW)

        tk.Label(self, text=u"Motif").grid(row=2, column=0, sticky=tk.EW)
        tk.Label(self, text=u"Montant").grid(row=2, column=1, sticky=tk.EW)

        self.reason = tk.StringVar()
        tk.Entry(self, textvariable=self.reason).grid(row=3, column=0, sticky=tk.EW)
        self.amount = tk.StringVar()
        tk.Entry(self, textvariable=self.amount).grid(row=3, column=1, sticky=tk.EW)

        tk.Label(self, text=u"Remarques").grid(row=4, column=0, sticky=tk.EW)
        self.remark = tk.Text(self, relief=tk.SUNKEN, borderwidth=1, width=80, height=6)
        self.remark.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW)

        tk.Button(self, text=u"Générer", command=self.generate_pdf).grid(row=6, column=0, columnspan=2, sticky=tk.EW)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.update_prefill()

    def manage_addresses(self):
        GererAdresses(self)
        self.update_prefill()
        self.change_address()

    def change_address(self, *args):
        self.address.delete('1.0', tk.END)
        self.address.insert(tk.END, self.addresses.get(self.prefill.get(), u""))

    def change_therapeute(self, *args):
        self.therapeuteAddress.config(text=self.therapeutes[self.therapeute.get()])

    def update_prefill(self):
        self.addresses = {}
        if len(self.prefillWidget['menu']._tclCommands) > 1:
            self.prefillWidget['menu'].delete(1, tk.END)
        cursor.execute("SELECT id, adresse FROM adresses")
        for id, address in cursor:
            self.addresses[id] = address
            self.prefillWidget['menu'].add_command(label=id, command=tk._setit(self.prefill, id))

    def generate_pdf(self):
        therapeute = self.therapeute.get()
        therapeuteAddress = self.therapeutes[therapeute].strip()
        address = self.address.get('1.0', tk.END).strip()
        identifier = self.prefill.get()
        if identifier == u"Adresse Manuelle":
            identifier = address.splitlines()[0].strip()
        now = datetime.datetime.now()
        ts = now.strftime('%Y-%m-%d_%H')
        filename = normalize_filename(u'%s_%sh.pdf' % (identifier.replace(' ', '_'), ts))
        reason = self.reason.get().strip()
        try:
            amount = float(self.amount.get().strip())
        except ValueError:
            tkMessageBox.showwarning(windows_title.invalid_error, errors_text.invalid_amount)
            return
        remark = self.remark.get('1.0', tk.END).strip()
        try:
            cursor.execute("UPDATE bvr_sequence SET counter = @counter := counter + 1")
            cursor.execute("SELECT @counter")
            bvr_counter, = cursor.fetchone()
            bv_ref = u'%06d%010d%02d%02d%02d%04d' % (bvr.prefix, bvr_counter, alpha_to_num(identifier[0]), alpha_to_num(identifier[1]), now.month, now.year)
            bv_ref = bv_ref + str(bvr_checksum(bv_ref))
            cursor.execute("""INSERT INTO factures_manuelles
                                     (identifiant, therapeute, destinataire, motif, montant_cts, remarque, date, bv_ref)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                           [identifier, therapeute, address, reason, int(amount * 100), remark, now.date(), bv_ref])
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)
            return
        bp_factures.manuals(filename, [(therapeuteAddress, address, reason, amount, remark, bv_ref)])
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
        os.system(cmd)


def save_db():
    myFormats = [('Database', '*.sql'), ]

    fileName = tkFileDialog.asksaveasfilename(filetypes=myFormats, title=u"Sauvegarde de la base de donnée")
    if len(fileName) > 0:
        os.system("mysqldump -u root SuperPatient > %s" % (fileName.encode('UTF-8')))


def restore_db():
    myFormats = [('Database', '*.sql'), ]

    fileName = tkFileDialog.askopenfilename(filetypes=myFormats, title=u'Restauration de la base de donnée')
    if fileName is not None:
        os.system("mysql -u root SuperPatient < %s" % (fileName.encode('UTF-8')))


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
        if (sys.platform != "win32") and hasattr(sys, 'frozen'):
            self.tk.call('console', 'hide')

        self.option_add('*font', 'Helvetica -15')

        menubar = tk.Menu(self)

        adminmenu = tk.Menu(menubar, tearoff=0)
        adminmenu.add_separator()
        adminmenu.add_command(label=menus_text.manage_colleagues, command=lambda: GererCollegues(self))
        adminmenu.add_command(label=menus_text.manage_tarifs, command=lambda: ManageCosts(self, 'tarifs'))
        adminmenu.add_command(label=menus_text.manage_majorations, command=lambda: ManageCosts(self, 'majorations'))
        adminmenu.add_command(label=menus_text.manage_frais_admins, command=lambda: ManageCosts(self, 'frais_admins'))
        adminmenu.add_separator()
        adminmenu.add_command(label=menus_text.manual_bill, command=lambda: FactureManuelle())
        adminmenu.add_separator()
        adminmenu.add_command(label=menus_text.delete_data, command=lambda: GererPatients(self, 'supprimer'), foreground='red')
#        adminmenu.add_command(label=menus_text.save_db, command=save_db)
#        adminmenu.add_command(label=menus_text.restore_db, command=restore_db)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=menus_text.about, command=lambda: apropos(self))
        helpmenu.add_command(label=menus_text.licence, command=lambda: licence(self))

        menubar.add_cascade(label=menus_text.admin, menu=adminmenu)
        menubar.add_cascade(label=menus_text.help, menu=helpmenu)

        tk.Button(self, text=buttons_text.new_patient, command=lambda: Patient(self)).grid(row=0, column=0, sticky=tk.W)

        tk.Button(self, text=buttons_text.show_or_change_patient, command=lambda: GererPatients(self, 'patient')).grid(row=1, column=0, sticky=tk.W)
        self.cntP_label = tk.Label(self)
        self.cntP_label.grid(row=1, column=1)

        tk.Label(self, text=u"").grid(row=2, column=0)
#        tk.Label(self, text=u"Ch").grid(row=2, column=1)
#        self.cntCH_label = tk.Label(self)
#        self.cntCH_label.grid(row=2, column=2)
#        tk.Label(self, text=u"Tib").grid(row=2, column=3)
#        self.cntTib_label = tk.Label(self)
#        self.cntTib_label.grid(row=2, column=4)

        tk.Button(self, text=buttons_text.new_consult_known_patient, command=lambda: GererPatients(self, 'nouvelle_consultation')).grid(row=3, column=0, sticky=tk.W)
#        tk.Label(self, text=u"LI").grid(row=3, column=1)
#        self.cntLIK_label = tk.Label(self)
#        self.cntLIK_label.grid(row=3, column=2)
#        tk.Label(self, text=u"CRT").grid(row=3, column=3)
#        self.cntCRT_label = tk.Label(self)
#        self.cntCRT_label.grid(row=3, column=4)

        tk.Button(self, text=buttons_text.show_or_change_consult, command=lambda: GererPatients(self, 'gerer_consultations')).grid(row=4, column=0, sticky=tk.W)
        self.cntC_label = tk.Label(self)
        self.cntC_label.grid(row=4, column=1)

        self.bind("<FocusIn>", self.update_counters)
        self.config(menu=menubar)

        self.title(windows_title.application)

        self.minsize(400, 180)
        self.geometry('+300+150')

    def update_counters(self, event):
        cursor.execute("SELECT count(*) FROM patients")
        self.cntP_label['text'], = cursor.fetchone()
        cursor.execute("SELECT count(*) FROM consultations")
        self.cntC_label['text'], = cursor.fetchone()
#        cursor.execute("SELECT count(*) FROM patients WHERE therapeute='ch'")
#        self.cntCH_label['text'], = cursor.fetchone()
#        cursor.execute("SELECT count(*) FROM patients WHERE therapeute='tib'")
#        self.cntTib_label['text'], = cursor.fetchone()
#        cursor.execute("SELECT count(*) FROM patients WHERE therapeute='lik'")
#        self.cntLIK_label['text'], = cursor.fetchone()
#        cursor.execute("SELECT count(*) FROM patients WHERE therapeute='CRT'")
#        self.cntCRT_label['text'], = cursor.fetchone()


app = Application()
app.mainloop()
