#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

# File: bp.py

#    Copyright 2006 Tibor Csernay

#    This file is part of BasicPatient.

#    BasicPatient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    BasicPatient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with BasicPatient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
import mailcap
import datetime
import traceback

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
    from bp_custo import DATE_FMT
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
    import reportlab
    reportlab
except:
    tkMessageBox.showwarning(u"Missing dependency", u"The reportlab library is missing")
    sys.exit()

try:
    from dateutil.parser import parse as parse_date, parserinfo
except:
    tkMessageBox.showwarning(u"Missing dependency", u"The dateutil module is missing")
    sys.exit()


class FrenchParserInfo(parserinfo):
    MONTHS = [(u'jan', u'janvier'), (u'fév', u'février'), (u'mar', u'mars'), (u'avr', u'avril'), (u'mai', u'mai'), (u'jui', u'juin'), (u'jul', u'juillet'), (u'aoû', u'août'), (u'sep', u'septembre'), (u'oct', u'octobre'), (u'nov', u'novembre'), (u'déc', u'décembre')]
    WEEKDAYS = [(u'Lun', u'Lundi'), (u'Mar', u'Mardi'), (u'Mer', u'Mercredi'), (u'Jeu', u'Jeudi'), (u'Ven', u'Vendredi'), (u'Sam', u'Samedi'), (u'Dim', u'Dimanche')]
    HMS = [(u'h', u'heure', u'heures'), (u'm', u'minute', u'minutes'), (u's', u'seconde', u'secondes')]
    JUMP = [u' ', u'.', u',', u';', u'-', u'/', u"'", u"le", u"er", u"ième"]

datesFR = FrenchParserInfo()


try:
    from bp_factures import facture
except:
    tkMessageBox.showwarning(u"Missing file", u"bp_factures.py is missing")
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

cursorS = db.cursor()
cursorI = db.cursor()
cursorU = db.cursor()
cursorR = db.cursor()


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


def PriceWidget(parent, key, row, column, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black', want_widget=False):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=labels_text[key], font=labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    try:
        cursorS.execute("""SELECT description, prix_cts FROM tarifs ORDER BY prix_cts""")
        tarifs = []
        for description, prix_cts in cursorS:
            label = u'%s : %0.2f CHF' % (description, prix_cts/100.)
            tarifs.append((prix_cts, description, label))
    except:
        traceback.print_exc()
        tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
        tarifs = [u"-- ERREUR --"]
    var = tk.StringVar()
    try:
        idx = [p for p, d, l in tarifs].index(value)
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
        self.id_patient = id_patient
        self.readonly = readonly and id_patient is not None
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        if self.id_patient is None:
            tk.Button(box, text=buttons_text.ok_new_consult, command=self.add_1ere_Consult).pack(side=tk.LEFT)
            tk.Button(box, text=buttons_text.save_close, command=self.addEntry).pack(side=tk.LEFT)
        elif not self.readonly:
            tk.Button(box, text=buttons_text.change, command=self.updateEntry).pack(side=tk.LEFT)
        tk.Button(box, text=buttons_text.cancel, command=self.cancel).pack(side=tk.LEFT)

        self.bind("<Escape>", self.cancel)

        box.pack()

    def addEntry(self, avec_anamnese=False):
        try:
            date_naiss = parse_date(self.date_naissVar.get().strip(), parserinfo=datesFR)
            date_ouv = parse_date(self.date_ouvVar.get().strip(), parserinfo=datesFR)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.invalid_error, errors_text.invalid_date)
            return
        if not self.sexVar.get() or not self.therapeuteVar.get() or not self.nomVar.get().strip() or not self.prenomVar.get().strip():
            tkMessageBox.showwarning(windows_title.invalid_error, errors_text.missing_data)
            return
        try:
            cursorS.execute("SELECT max(id)+1 FROM patients")
            id_patient, = cursorS.fetchone()
            if id_patient is None:
                id_patient = 1
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_id)
            return
        try:
            cursorI.execute("""INSERT INTO patients
                                        (id, date_ouverture, therapeute, sex, nom, prenom, date_naiss, ATCD_perso,
                                        ATCD_fam, medecin, autre_medecin, phone, portable, profes_phone, mail,
                                        adresse, ass_compl, profes, etat, envoye, divers, important)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            [id_patient, date_ouv, self.therapeuteVar.get(), self.sexVar.get(),
                                self.nomVar.get().strip(), self.prenomVar.get().strip(),
                                date_naiss, u"", u"", self.medecinVar.get(1.0, tk.END).strip(),
                                self.autre_medecinVar.get(1.0, tk.END).strip(), self.phoneVar.get().strip(),
                                self.portableVar.get().strip(), self.profes_phoneVar.get().strip(),
                                self.mailVar.get().strip(), self.adresseVar.get(1.0, tk.END).strip(),
                                self.ass_complVar.get().strip(), self.profesVar.get().strip(),
                                self.etatVar.get().strip(), self.envoyeVar.get().strip(),
                                self.diversVar.get(1.0, tk.END).strip(), self.importantVar.get(1.0, tk.END).strip()])
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_insert)
            return
        self.cancel()
        if avec_anamnese:
            Consultation(self.parent, id_patient)

    def updateEntry(self):
        try:
            cursorU.execute("""UPDATE patients
                                    SET sex=%s,
                                        nom=%s,
                                        prenom=%s,
                                        therapeute=%s,
                                        date_naiss=%s,
                                        date_ouverture=%s,
                                        adresse=%s,
                                        important=%s,
                                        medecin=%s,
                                        autre_medecin=%s,
                                        phone=%s,
                                        portable=%s,
                                        profes_phone=%s,
                                        mail=%s,
                                        ass_compl=%s,
                                        profes=%s,
                                        etat=%s,
                                        envoye=%s,
                                        divers=%s
                                WHERE id=%s""",
                            [self.sexVar.get(), self.nomVar.get().strip(), self.prenomVar.get().strip(),
                                self.therapeuteVar.get(), parse_date(self.date_naissVar.get().strip(), parserinfo=datesFR),
                                parse_date(self.date_ouvVar.get().strip(), parserinfo=datesFR), self.adresseVar.get(1.0, tk.END).strip(),
                                self.importantVar.get(1.0, tk.END).strip(), self.medecinVar.get(1.0, tk.END).strip(),
                                self.autre_medecinVar.get(1.0, tk.END).strip(), self.phoneVar.get().strip(),
                                self.portableVar.get().strip(), self.profes_phoneVar.get().strip(),
                                self.mailVar.get().strip(), self.ass_complVar.get().strip(),
                                self.profesVar.get().strip(), self.etatVar.get().strip(),
                                self.envoyeVar.get().strip(), self.diversVar.get(1.0, tk.END).strip(),
                                self.id_patient])
            self.cancel()
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)

    def add_1ere_Consult(self):
        self.addEntry(avec_anamnese=True)

    def body(self, master):
        if self.id_patient:
            title = windows_title.patient
        else:
            title = windows_title.new_patient
        self.title(title)
        self.geometry('+200+5')
        # self.geometry("1024x710")

        sexe = therapeute = nom = prenom = date_naiss = phone = medecin = portable = profes_phone = mail = adresse = autre_medecin = ass_compl = profes = etat = envoye = divers = important = None
        date_ouv = datetime.date.today()

        try:
            cursorS.execute("""SELECT therapeute FROM therapeutes""")
            therapeutes = [t for t, in cursorS]
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

        def mandatory(value):
            if value:
                return 'black'
            return 'red'

        if self.id_patient:
            cursorS.execute("""SELECT sex, therapeute, nom, prenom, date_naiss, phone, medecin, portable, profes_phone,
                                      mail, adresse, autre_medecin, ass_compl, profes, etat, envoye, divers, important,
                                      date_ouverture
                                 FROM patients
                                WHERE id = %s""",
                            [self.id_patient])
            (sexe, therapeute, nom, prenom, date_naiss, phone, medecin, portable, profes_phone, mail, adresse,
             autre_medecin, ass_compl, profes, etat, envoye, divers, important, date_ouv) = cursorS.fetchone()

            EntryWidget(master, key='id', row=0, column=2, value=self.id_patient, readonly=True)
        self.sexVar, focus_widget = RadioWidget(master, key='sexe', row=0, column=0, fg=mandatory(sexe), options=[(u'Mme', u'F'), (u'Mr', u'M')], value=sexe, readonly=self.readonly, want_widget=True)

        self.nomVar = EntryWidget(master, key='nom', row=1, column=0, fg=mandatory(nom), value=nom, readonly=self.readonly)
        self.therapeuteVar = OptionWidget(master, key='therapeute', row=1, column=2, fg=mandatory(therapeute), value=therapeute, options=therapeutes, readonly=self.readonly)

        self.prenomVar = EntryWidget(master, key='prenom', row=2, column=0, fg=mandatory(prenom), value=prenom, readonly=self.readonly)

        if date_naiss:
            key = 'naissance'
            fg = 'black'
            date_naiss = date_naiss.strftime(DATE_FMT)
        else:
            key = 'naissance_le'
            fg = 'red'
            date_naiss = labels_text.date_format
        self.date_naissVar = EntryWidget(master, key=key, row=3, column=0, fg=fg, value=date_naiss, readonly=self.readonly)
        self.date_ouvVar = EntryWidget(master, key='date_ouverture', row=3, column=2, value=date_ouv.strftime(DATE_FMT), readonly=self.readonly)

        self.phoneVar = EntryWidget(master, key='tel_fix', row=4, column=0, value=phone, readonly=self.readonly)
        self.importantVar = TextWidget(master, key='important', row=4, column=2, rowspan=2, value=important, readonly=self.readonly, field_fg='red')
        self.portableVar = EntryWidget(master, key='portable', row=5, column=0, value=portable, readonly=self.readonly)

        self.profes_phoneVar = EntryWidget(master, key='tel_prof', row=6, column=0, value=profes_phone, readonly=self.readonly)
        self.medecinVar = TextWidget(master, key='medecin', row=6, column=2, rowspan=2, value=medecin, readonly=self.readonly)
        self.mailVar = EntryWidget(master, key='mail', row=7, column=0, value=mail, readonly=self.readonly)

        self.adresseVar = TextWidget(master, key='adr_priv', row=8, column=0, value=adresse, readonly=self.readonly)
        self.autre_medecinVar = TextWidget(master, key='medecinS', row=8, column=2, rowspan=3, value=autre_medecin, readonly=self.readonly)

        self.ass_complVar = EntryWidget(master, key='ass_comp', row=11, column=0, value=ass_compl, readonly=self.readonly)

        self.profesVar = EntryWidget(master, key='profes', row=12, column=0, value=profes, readonly=self.readonly)
        self.etatVar = EntryWidget(master, key='etat', row=12, column=2, value=etat, readonly=self.readonly)

        self.envoyeVar = EntryWidget(master, key='envoye', row=13, column=0, value=envoye, readonly=self.readonly)

        self.diversVar = TextWidget(master, key='remarques', row=14, column=0, columnspan=3, value=divers, readonly=self.readonly)

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
        box.pack()

    def recherche(self):
        try:
            cursorS.execute("""SELECT id, sex, nom, prenom, (SELECT count(*) FROM consultations WHERE id = patients.id)
                                 FROM patients
                                WHERE nom LIKE %s AND prenom LIKE %s
                             ORDER BY nom""",
                            [self.nomRec.get().strip(), self.prenomRec.get().strip()])
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_search)
        self.results = []
        self.select.delete(0, tk.END)
        for id, sex, nom, prenom, n_consult in cursorS:
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
                cursorS.execute("""SELECT sex, nom, prenom, date_naiss
                                    FROM patients
                                    WHERE id = %s""",
                                [id])
                sex, nom, prenom, date_naiss = cursorS.fetchone()
            except:
                traceback.print_exc()
                tkMessageBox.showwarning(windows_title.db_error, errors_text.db_search)
                return
            if tkMessageBox.askyesno(windows_title.delete, labels_text.suppr_def_1+u'\n'+str(sex+u" "+prenom+u" "+nom)+labels_text.suppr_def_2+date_naiss.strftime(DATE_FMT)+u'\n'+labels_text.suppr_def_3):
                try:
                    cursorR.execute("DELETE FROM consultations WHERE id=%s", [id])
                    cursorR.execute("DELETE FROM patients WHERE id=%s", [id])
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
            cursorS.execute("""SELECT sex, nom, prenom, date_naiss, ATCD_perso, ATCD_fam, important FROM patients WHERE id = %s""", [self.id_patient])
            sex, nom, prenom, date_naiss, ATCD_perso, ATCD_fam, Important = cursorS.fetchone()
            cursorS.execute("""SELECT id_consult, date_consult, MC, MC_accident, EG, APT_thorax, APT_abdomen, APT_tete, APT_MS,
                                      APT_MI, APT_system, A_osteo, exam_phys, traitement, divers, exam_pclin, paye
                                 FROM consultations
                                WHERE id=%s
                             ORDER BY date_consult DESC""",
                            [self.id_patient])
        except:
            print "id_patient:", self.id_patient
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_show)
            return
        self.toutes.tag_config("date", foreground="red", font=("Helvetica", 15, "bold"))
        self.toutes.tag_config("titre", foreground="blue", font=("Helvetica", 15))
        self.toutes.tag_config("personne", foreground="black", font=("Helvetica", 15, "bold"))
        self.toutes.tag_config("important", foreground="darkblue", font=("Helvetica", 15, "bold"))
        self.toutes.insert(tk.END, sex+u' '+prenom+u' '+nom+u', '+date_naiss.strftime(DATE_FMT)+u'\n', "personne")
        self.toutes.insert(tk.END, labels_text.atcdp+u'\n', "titre")
        self.toutes.insert(tk.END, ATCD_perso+u'\n')
        self.toutes.insert(tk.END, labels_text.atcdf+u'\n', "titre")
        self.toutes.insert(tk.END, ATCD_fam+u'\n')
        self.toutes.insert(tk.END, labels_text.important+u'\n', "important")
        self.toutes.insert(tk.END, Important+u'\n')
        for id_consult, date_consult, MC, MC_accident, EG, APT_thorax, APT_abdomen, APT_tete, APT_MS, APT_MI, APT_system, A_osteo, exam_phys, traitement, divers, exam_pclin, paye in cursorS:
            self.toutes.insert(tk.END, u'\n********** '+labels_text.date_consult+date_consult.strftime(DATE_FMT)+u' **********'+u'\n', "date")
            if EG.strip():
                self.toutes.insert(tk.END, labels_text.eg+u'\n', "titre")
                self.toutes.insert(tk.END, EG+u'\n')
            self.toutes.insert(tk.END, labels_text.mc+u'\n', "titre")
            if MC_accident:
                self.toutes.insert(tk.END, labels_text.accident+u'\n')
            else:
                self.toutes.insert(tk.END, labels_text.maladie+u'\n')
            self.toutes.insert(tk.END, MC+u'\n')
            if APT_thorax.strip():
                self.toutes.insert(tk.END, labels_text.thorax+u'\n', "titre")
                self.toutes.insert(tk.END, APT_thorax+u'\n')
            if APT_abdomen.strip():
                self.toutes.insert(tk.END, labels_text.abdomen+u'\n', "titre")
                self.toutes.insert(tk.END, APT_abdomen+u'\n')
            if APT_tete.strip():
                self.toutes.insert(tk.END, labels_text.tete+u'\n', "titre")
                self.toutes.insert(tk.END, APT_tete+u'\n')
            if APT_MS.strip():
                self.toutes.insert(tk.END, labels_text.ms+u'\n', "titre")
                self.toutes.insert(tk.END, APT_MS+u'\n')
            if APT_MI.strip():
                self.toutes.insert(tk.END, labels_text.mi+u'\n', "titre")
                self.toutes.insert(tk.END, APT_MI+u'\n')
            if APT_system.strip():
                self.toutes.insert(tk.END, labels_text.gen+u'\n', "titre")
                self.toutes.insert(tk.END, APT_system+u'\n')
            if A_osteo.strip():
                self.toutes.insert(tk.END, labels_text.a_osteo+u'\n', "titre")
                self.toutes.insert(tk.END, A_osteo+u'\n')
            if exam_phys.strip():
                self.toutes.insert(tk.END, labels_text.exph+u'\n', "titre")
                self.toutes.insert(tk.END, exam_phys+u'\n')
            if traitement.strip():
                self.toutes.insert(tk.END, labels_text.ttt+u'\n', "titre")
                self.toutes.insert(tk.END, traitement+u'\n')
            if exam_pclin.strip():
                self.toutes.insert(tk.END, labels_text.expc+u'\n', "titre")
                self.toutes.insert(tk.END, exam_pclin+u'\n')
            if divers.strip():
                self.toutes.insert(tk.END, labels_text.remarques+u'\n', "titre")
                self.toutes.insert(tk.END, divers+u'\n')
            if paye.strip():
                self.toutes.insert(tk.END, labels_text.paye+u'\n', "titre")
                self.toutes.insert(tk.END, paye+u'\n')

    def body(self, master):
        self.geometry('+200+5')
        # self.geometry("700x710")

        self.toutes = TextWidget(master, key='ttes_cons', row=0, column=0, side_by_side=False, fg='blue')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)

        self.auto_affiche()


class Consultation(bp_Dialog.Dialog):
    def __init__(self, parent, id_patient, id_consult=None, readonly=False):
        self.id_patient = id_patient
        self.id_consult = id_consult
        self.readonly = readonly
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        if self.readonly:
            tk.Button(box, text=buttons_text.ok, command=self.cancel).pack(side=tk.LEFT)
        else:
            tk.Button(box, text=buttons_text.save_close, command=self.modif).pack(side=tk.LEFT)  # Was B11
            tk.Button(box, text=buttons_text.cancel, command=self.cancel).pack(side=tk.LEFT)
        if self.id_consult is not None:
            tk.Button(box, text=buttons_text.reprint, command=self.generate_pdf).pack(side=tk.LEFT)
        cursorS.execute("SELECT count(*) FROM consultations WHERE id = %s", [self.id_patient])
        count, = cursorS.fetchone()
        if count > 0:
            tk.Button(box, text=u"Toutes les consultations", command=lambda: ListeConsultations(self.parent, self.id_patient)).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def get_cost(self):
        description, prix = self.prixVar.get().split(u' : ')
        prix_cts = int(float(prix[:-4]) * 100 + 0.5)
        if self.majorationVar.get():
            majoration_cts = bp_custo.MAJORATION_CTS
        else:
            majoration_cts = 0
        return description, prix_cts, majoration_cts

    def modif(self):
        paye_par = self.paye_parVar.get().strip()
        if not self.prixVar.get().strip() or not paye_par:
            tkMessageBox.showwarning(windows_title.missing_error, errors_text.missing_payment_info)
            return
        if not self.therapeuteVar.get().strip():
            tkMessageBox.showwarning(windows_title.missing_error, errors_text.missing_therapeute)
            return
        try:
            description, prix_cts, majoration_cts = self.get_cost()
            if paye_par in (u'BVR', u'CdM'):
                paye_le = None
            else:
                paye_le = datetime.date.today()
            date_ouvc = parse_date(self.date_ouvcVar.get().strip(), parserinfo=datesFR)
            new_consult = self.id_consult is None
            if new_consult:
                try:
                    cursorS.execute("SELECT max(id_consult)+1 FROM consultations")
                    self.id_consult, = cursorS.fetchone()
                    if self.id_consult is None:
                        self.id_consult = 1
                except:
                    traceback.print_exc()
                    tkMessageBox.showwarning(windows_title.db_error, errors_text.db_id)
                    return
                cursorI.execute("""INSERT INTO consultations
                                        (id_consult, id, date_consult,
                                            MC, MC_accident, EG, exam_pclin, exam_phys, paye, divers, APT_thorax, APT_abdomen,
                                            APT_tete, APT_MS, APT_MI, APT_system, A_osteo, traitement, therapeute,
                                            prix_cts, majoration_cts, paye_par, paye_le)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                [self.id_consult, self.id_patient, date_ouvc,
                                    self.MCVar.get(1.0, tk.END).strip(), self.MC_accidentVar.get(),
                                    self.EGVar.get(1.0, tk.END).strip(), self.exam_pclinVar.get(1.0, tk.END).strip(),
                                    self.exam_physVar.get(1.0, tk.END).strip(), self.payeVar.get(1.0, tk.END).strip(),
                                    self.diversVar.get(1.0, tk.END).strip(), self.APT_thoraxVar.get(1.0, tk.END).strip(),
                                    self.APT_abdomenVar.get(1.0, tk.END).strip(), self.APT_teteVar.get(1.0, tk.END).strip(),
                                    self.APT_MSVar.get(1.0, tk.END).strip(), self.APT_MIVar.get(1.0, tk.END).strip(),
                                    self.APT_systemVar.get(1.0, tk.END).strip(), self.A_osteoVar.get(1.0, tk.END).strip(),
                                    self.traitementVar.get(1.0, tk.END).strip(), self.therapeuteVar.get(),
                                    prix_cts, majoration_cts, paye_par, paye_le])
                generate_pdf = paye_par != u'CdM'
            else:
                cursorS.execute("""SELECT paye_par FROM consultations WHERE id_consult=%s""", [self.id_consult])
                old_paye_par, = cursorS.fetchone()
                generate_pdf = paye_par != old_paye_par
                cursorU.execute("""UPDATE consultations
                                    SET MC=%s,
                                        MC_accident=%s,
                                        EG=%s,
                                        exam_pclin=%s,
                                        exam_phys=%s,
                                        paye=%s,
                                        divers=%s,
                                        APT_thorax=%s,
                                        APT_abdomen=%s,
                                        APT_tete=%s,
                                        APT_MS=%s,
                                        APT_MI=%s,
                                        APT_system=%s,
                                        A_osteo=%s,
                                        traitement=%s,
                                        date_consult=%s,
                                        therapeute=%s,
                                        prix_cts=%s,
                                        majoration_cts=%s,
                                        paye_par=%s,
                                        paye_le=%s
                                    WHERE id_consult=%s""",
                                [self.MCVar.get(1.0, tk.END).strip(), self.MC_accidentVar.get(), self.EGVar.get(1.0, tk.END).strip(),
                                    self.exam_pclinVar.get(1.0, tk.END).strip(), self.exam_physVar.get(1.0, tk.END).strip(),
                                    self.payeVar.get(1.0, tk.END).strip(), self.diversVar.get(1.0, tk.END).strip(),
                                    self.APT_thoraxVar.get(1.0, tk.END).strip(), self.APT_abdomenVar.get(1.0, tk.END).strip(),
                                    self.APT_teteVar.get(1.0, tk.END).strip(), self.APT_MSVar.get(1.0, tk.END).strip(),
                                    self.APT_MIVar.get(1.0, tk.END).strip(), self.APT_systemVar.get(1.0, tk.END).strip(),
                                    self.A_osteoVar.get(1.0, tk.END).strip(), self.traitementVar.get(1.0, tk.END).strip(),
                                    date_ouvc, self.therapeuteVar.get(), prix_cts, majoration_cts, paye_par, paye_le, self.id_consult])
            cursorU.execute("UPDATE patients SET important=%s, ATCD_perso=%s, ATCD_fam=%s WHERE id=%s",
                            [self.importantVar.get(1.0, tk.END).strip(), self.ATCD_persoVar.get(1.0, tk.END).strip(),
                                self.ATCD_famVar.get(1.0, tk.END).strip(), self.id_patient])
            self.cancel()
            if generate_pdf:
                self.generate_pdf()
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)

    def generate_pdf(self):
        paye_par = self.paye_parVar.get().strip()
        if not self.prixVar.get().strip() or not paye_par:
            tkMessageBox.showwarning(windows_title.missing_error, errors_text.missing_payment_info)
            return
        if not self.therapeuteVar.get().strip():
            tkMessageBox.showwarning(windows_title.missing_error, errors_text.missing_therapeute)
            return
        description, prix_cts, majoration_cts = self.get_cost()
        date_ouvc = parse_date(self.date_ouvcVar.get().strip(), parserinfo=datesFR)
        cursorS.execute("""SELECT entete FROM therapeutes WHERE therapeute = %s""", [self.therapeuteVar.get()])
        entete_therapeute, = cursorS.fetchone()
        adresse_therapeute = entete_therapeute + u'\n\n' + labels_text.adresse_pog
        cursorS.execute("""SELECT sex, nom, prenom FROM patients WHERE id=%s""", [self.id_patient])
        sex, nom, prenom = cursorS.fetchone()
        cursorS.execute("""SELECT adresse FROM patients WHERE id = %s""", [self.id_patient])
        adresse_patient, = cursorS.fetchone()
        if len(u' '.join((sex, prenom, nom))) < 25:
            identite = [u' '.join((sex, prenom, nom))]
        elif len(u' '.join((prenom, nom))) < 25:
            identite = [sex, u' '.join((prenom, nom))]
        else:
            identite = [sex, prenom, nom]
        adresse_patient = u'\n'.join(identite + [adresse_patient])
        ts = datetime.datetime.now().strftime('%H')
        filename = os.path.join(bp_custo.PDF_DIR, (u'%s_%s_%s_%s_%sh.pdf' % (nom, prenom, sex, date_ouvc, ts)).encode('UTF-8'))
        facture(filename, adresse_therapeute, adresse_patient, description, self.MC_accidentVar.get(), prix_cts, majoration_cts, date_ouvc, with_bv=(paye_par == u'BVR'))
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
        os.system(cmd)

    def body(self, master):
        self.geometry("+200+5")
        # self.geometry("1024x900")

        try:
            cursorS.execute("""SELECT therapeute FROM therapeutes ORDER BY therapeute""")
            therapeutes = [u''] + [t for t, in cursorS]
            cursorS.execute("""SELECT sex, nom, prenom, date_naiss, important, ATCD_perso, ATCD_fam, therapeute
                                 FROM patients
                                WHERE id=%s""",
                            [self.id_patient])
            sex, nom, prenom, date_naiss, important, ATCD_perso, ATCD_fam, therapeute = cursorS.fetchone()
            if self.id_consult:
                cursorS.execute("""SELECT date_consult, MC, MC_accident, EG, exam_pclin, exam_phys, traitement, APT_thorax, APT_abdomen,
                                        APT_tete, APT_MS, APT_MI, APT_system, A_osteo, divers, paye, therapeute, prix_cts, majoration_cts, paye_par, paye_le
                                    FROM consultations
                                    WHERE id_consult=%s""",
                                [self.id_consult])
                (date_consult, MC, MC_accident, EG, exam_pclin, exam_phys, traitement, APT_thorax, APT_abdomen,
                 APT_tete, APT_MS, APT_MI, APT_system, A_osteo, divers, paye, therapeute, prix_cts, majoration_cts,
                 paye_par, paye_le) = cursorS.fetchone()
                title = windows_title.consultation % (date_consult, sex, nom)
            else:
                date_consult = MC = EG = exam_pclin = exam_phys = traitement = APT_thorax = APT_abdomen = APT_tete = APT_MS = APT_MI = APT_system = A_osteo = divers = paye = prix_cts = majoration_cts = paye_par = paye_le = None
                MC_accident = False
                title = windows_title.new_consultation % (sex, nom)
            if therapeute is not None:
                therapeute = therapeute.strip()  # Sanity guard against old data
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
        self.MCVar, self.MC_accidentVar = MCWidget(master, key='mc', row=0, column=0, side_by_side=False, fg='blue', field_fg='blue', value=MC, accident=MC_accident, readonly=self.readonly)
        self.EGVar = TextWidget(master, key='eg', row=0, column=1, side_by_side=False, value=EG, readonly=self.readonly)
        self.exam_pclinVar = TextWidget(master, key='expc', row=0, column=2, rowspan=3, side_by_side=False, value=exam_pclin, readonly=self.readonly)

        self.ATCD_persoVar = TextWidget(master, key='atcdp', row=2, column=0, side_by_side=False, value=ATCD_perso, readonly=self.readonly)
        self.ATCD_famVar = TextWidget(master, key='atcdf', row=2, column=1, side_by_side=False, value=ATCD_fam, readonly=self.readonly)

        self.APT_thoraxVar = TextWidget(master, key='thorax', row=4, column=0, side_by_side=False, value=APT_thorax, readonly=self.readonly)
        self.APT_abdomenVar = TextWidget(master, key='abdomen', row=4, column=1, side_by_side=False, value=APT_abdomen, readonly=self.readonly)
        self.exam_physVar = TextWidget(master, key='exph', row=4, column=2, rowspan=3, side_by_side=False, value=exam_phys, readonly=self.readonly)

        self.APT_teteVar = TextWidget(master, key='tete', row=6, column=0, side_by_side=False, value=APT_tete, readonly=self.readonly)
        self.APT_MSVar = TextWidget(master, key='ms', row=6, column=1, side_by_side=False, value=APT_MS, readonly=self.readonly)

        self.APT_MIVar = TextWidget(master, key='mi', row=8, column=0, side_by_side=False, value=APT_MI, readonly=self.readonly)
        self.APT_systemVar = TextWidget(master, key='gen', row=8, column=1, side_by_side=False, value=APT_system, readonly=self.readonly)
        self.importantVar = TextWidget(master, key='important', row=8, column=2, side_by_side=False, value=important, fg='red', field_fg='red', readonly=self.readonly)

        self.A_osteoVar = TextWidget(master, key='a_osteo', row=10, column=0, side_by_side=False, value=A_osteo, readonly=self.readonly)
        self.traitementVar = TextWidget(master, key='ttt', row=10, column=1, side_by_side=False, fg='darkgreen', value=traitement, readonly=self.readonly)
        self.diversVar = TextWidget(master, key='remarques', row=10, column=2, side_by_side=False, value=divers, readonly=self.readonly)

        self.date_ouvcVar = EntryWidget(master, key='date_ouverture', row=12, column=0, side_by_side=False, value=date_consult.strftime(DATE_FMT), readonly=self.readonly)
        self.therapeuteVar = OptionWidget(master, key='therapeute', row=12, column=1, side_by_side=False, value=therapeute, options=therapeutes, readonly=self.readonly)
        self.payeVar = TextWidget(master, key='paye', row=12, column=2, rowspan=3, side_by_side=False, value=paye, field_fg='red', readonly=self.readonly)

        self.majorationVar = tk.IntVar()
        if majoration_cts:
            self.majorationVar.set(1)
        else:
            self.majorationVar.set(0)
        f = tk.Frame(master)
        check_btn = tk.Checkbutton(f, text=labels_text['majoration'], font=labels_font['majoration'], variable=self.majorationVar)
        check_btn.grid(row=1, column=0)
        if self.readonly:
            check_btn.config(state=tk.DISABLED)
        self.prixVar = PriceWidget(f, key='seance', row=0, column=1, side_by_side=False, value=prix_cts, readonly=self.readonly)
        f.grid(row=14, column=0, rowspan=2, sticky=tk.W+tk.E)
        f.grid_columnconfigure(1, weight=1)

        self.paye_parVar = RadioWidget(master, key='paye_par', row=14, column=1, side_by_side=False, value=paye_par, options=bp_custo.MOYEN_DE_PAYEMENT, readonly=self.readonly)
        if self.id_consult and paye_le:
            frame = master.grid_slaves(row=15, column=1)[0]
            tk.Label(frame, text=labels_text.paye_le+u' '+str(paye_le), font=labels_font.paye_le).pack(side=tk.RIGHT)

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
            cursorS.execute("""SELECT id_consult, date_consult, MC
                                 FROM consultations
                                WHERE id=%s
                             ORDER BY date_consult DESC""",
                            [self.id_patient])
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_show)
        self.results = []
        self.select_consult.delete(0, tk.END)
        for id_consult, date_consult, MC in cursorS:
            self.select_consult.insert(tk.END, date_consult.strftime(DATE_FMT)+u' '+MC)
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
                    cursorR.execute("DELETE FROM consultations WHERE id_consult=%s", [id_consult])
                    tkMessageBox.showinfo(windows_title.done, labels_text.cons_sup)
                except:
                    traceback.print_exc()
                    tkMessageBox.showwarning(windows_title.db_error, errors_text.db_delete)
        self.affiche_toutes()

    def body(self, master):
        self.geometry('+200+5')

        try:
            cursorS.execute("""SELECT nom, prenom, sex, therapeute, date_naiss
                                 FROM patients WHERE id = %s""", [self.id_patient])
            nom, prenom, sex, therapeute, date_naiss = cursorS.fetchone()
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


class GererTarifs(bp_Dialog.Dialog):
    def buttonbox(self):
        box = tk.Button(self, text=buttons_text.done, command=self.cancel)
        self.bind("<Escape>", self.cancel)
        return box

    def populate(self):
        self.listbox.delete(0, tk.END)
        d_width = 0
        for description, prix_cts in self.tarifs:
            d_width = max(d_width, len(description))
        for description, prix_cts in self.tarifs:
            self.listbox.insert(tk.END, u"%*s    %7.2f" % (-d_width, description, prix_cts/100.))
        self.listbox.selection_clear(0, tk.END)

    def select_tarif(self, event):
        indexes = self.listbox.curselection()
        self.tarif.set(u"")
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
            description, prix_cts = self.tarifs[index]
            self.description.set(description)
            self.tarif.set('%0.2f' % (prix_cts/100.))
        else:
            self.index = None
            self.update.config(text=buttons_text.add)

    def update_tarif(self):
        indexes = self.listbox.curselection()
        update = bool(indexes)
        description = self.description.get().strip()
        try:
            prix_cts = int(float(self.tarif.get().strip()) * 100)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.invalid_error, errors_text.invalid_tarif)
            return
        try:
            if update:
                key, _ = self.tarifs[indexes[0]]
                cursorU.execute("""UPDATE tarifs SET description = %s, prix_cts = %s WHERE description = %s""",
                                [description, prix_cts, key])
                self.tarifs[indexes[0]] = (description, prix_cts)
            else:
                cursorI.execute("""INSERT INTO tarifs (description, prix_cts) VALUES (%s, %s)""",
                                [description, prix_cts])
                self.tarifs.append((description, prix_cts))
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()
        self.select_tarif('ignore')

    def delete_tarif(self):
        indexes = self.listbox.curselection()
        if indexes:
            try:
                key, _ = self.tarifs[indexes[0]]
                cursorU.execute("""DELETE FROM tarifs WHERE description = %s""", [key])
                del self.tarifs[indexes[0]]
            except:
                traceback.print_exc()
                tkMessageBox.showwarning(windows_title.db_error, errors_text.db_delete)
        self.populate()
        self.select_tarif('ignore')

    def body(self, master):
        try:
            cursorS.execute("""SELECT description, prix_cts FROM tarifs""")
            self.tarifs = list(cursorS)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

        self.title(windows_title.manage_tarifs)
        self.listbox = ListboxWidget(master, key='tarifs', row=0, column=0, columnspan=3)
        self.listbox.config(selectmode=tk.SINGLE)
        self.listbox.bind('<<ListboxSelect>>', self.select_tarif)
        self.index = None
        self.populate()
        self.description = EntryWidget(master, key='description', row=2, column=0, side_by_side=False)
        self.tarif = EntryWidget(master, key='tarif', row=2, column=1, side_by_side=False)
        self.update = tk.Button(master, text=buttons_text.add, command=self.update_tarif)
        self.update.grid(row=3, column=2)
        self.delete = tk.Button(master, text=buttons_text.delete, command=self.delete_tarif)
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
        t_width = 0
        for therapeute, entete in self.collegues:
            t_width = max(t_width, len(therapeute))
        for therapeute, entete in self.collegues:
            self.listbox.insert(tk.END, u"%*s    %s" % (-t_width, therapeute, entete))
        self.listbox.selection_clear(0, tk.END)

    def select_collegue(self, event):
        indexes = self.listbox.curselection()
        self.entete.delete('1.0', tk.END)
        self.therapeute.set(u"")
        if indexes:
            index = indexes[0]
            if index == self.index:
                self.listbox.selection_clear(0, tk.END)
                self.index = None
                self.update.config(text=buttons_text.add)
                return
            self.index = index
            self.update.config(text=buttons_text.change)
            therapeute, entete = self.collegues[index]
            self.therapeute.set(therapeute)
            self.entete.insert(tk.END, entete)
        else:
            self.index = None
            self.update.config(text=buttons_text.add)

    def update_collegue(self):
        indexes = self.listbox.curselection()
        update = bool(indexes)
        therapeute = self.therapeute.get().strip()
        entete = self.entete.get('1.0', tk.END).strip()
        try:
            if update:
                key, _ = self.collegues[indexes[0]]
                cursorU.execute("""UPDATE therapeutes SET therapeute = %s, entete = %s WHERE therapeute = %s""",
                                [therapeute, entete, key])
                self.collegues[indexes[0]] = (therapeute, entete)
            else:
                cursorI.execute("""INSERT INTO therapeutes (therapeute, entete) VALUES (%s, %s)""",
                                [therapeute, entete])
                self.collegues.append((therapeute, entete))
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()
        self.select_collegue('ignore')

    def delete_collegue(self):
        indexes = self.listbox.curselection()
        if indexes:
            try:
                key, _ = self.collegues[indexes[0]]
                cursorU.execute("""DELETE FROM therapeutes WHERE therapeute = %s""", [key])
                del self.collegues[indexes[0]]
            except:
                traceback.print_exc()
                tkMessageBox.showwarning(windows_title.db_error, errors_text.db_delete)
        self.populate()
        self.select_collegue('ignore')

    def body(self, master):
        try:
            cursorS.execute("""SELECT therapeute, entete FROM therapeutes ORDER BY therapeute""")
            self.collegues = list(cursorS)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            return

        self.title(windows_title.manage_colleagues)
        self.listbox = ListboxWidget(master, key='collabos', row=0, column=0, columnspan=3)
        self.listbox.config(selectmode=tk.SINGLE)
        self.listbox.bind('<<ListboxSelect>>', self.select_collegue)
        self.index = None
        self.populate()
        self.therapeute = EntryWidget(master, key='therapeute', row=2, column=0, side_by_side=False)
        self.entete = TextWidget(master, key='entete', row=2, column=1, rowspan=2, side_by_side=False)
        self.update = tk.Button(master, text=buttons_text.add, command=self.update_collegue)
        self.update.grid(row=3, column=2)
        self.delete = tk.Button(master, text=buttons_text.delete, command=self.delete_collegue)
        self.delete.grid(row=4, column=2)

        master.grid_rowconfigure(1, weight=2)
        master.grid_rowconfigure(3, weight=1)
        master.grid_rowconfigure(4, weight=1)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)


def save_db():
    myFormats = [('Database', '*.sql'), ]

    fileName = tkFileDialog.asksaveasfilename(filetypes=myFormats, title=u"Sauvegarde de la base de donnée")
    if len(fileName) > 0:
        os.system("mysqldump -u root basicpatient > %s" % (fileName.encode('UTF-8')))


def restore_db():
    myFormats = [('Database', '*.sql'), ]

    fileName = tkFileDialog.askopenfilename(filetypes=myFormats, title=u'Restauration de la base de donnée')
    if fileName is not None:
        os.system("mysql -u root basicpatient < %s" % (fileName.encode('UTF-8')))


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
        adminmenu.add_command(label=menus_text.manage_tarifs, command=lambda: GererTarifs(self))
        adminmenu.add_command(label=menus_text.delete_data, command=lambda: GererPatients(self, 'supprimer'), foreground='red')
        adminmenu.add_command(label=menus_text.save_db, command=save_db)
        adminmenu.add_command(label=menus_text.restore_db, command=restore_db)

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
        tk.Label(self, text=u"Ch").grid(row=2, column=1)
        self.cntCH_label = tk.Label(self)
        self.cntCH_label.grid(row=2, column=2)
        tk.Label(self, text=u"Tib").grid(row=2, column=3)
        self.cntTib_label = tk.Label(self)
        self.cntTib_label.grid(row=2, column=4)

        tk.Button(self, text=buttons_text.new_consult_known_patient, command=lambda: GererPatients(self, 'nouvelle_consultation')).grid(row=3, column=0, sticky=tk.W)
        tk.Label(self, text=u"LI").grid(row=3, column=1)
        self.cntLIK_label = tk.Label(self)
        self.cntLIK_label.grid(row=3, column=2)
        tk.Label(self, text=u"CRT").grid(row=3, column=3)
        self.cntCRT_label = tk.Label(self)
        self.cntCRT_label.grid(row=3, column=4)

        tk.Button(self, text=buttons_text.show_or_change_consult, command=lambda: GererPatients(self, 'gerer_consultations')).grid(row=4, column=0, sticky=tk.W)
        self.cntC_label = tk.Label(self)
        self.cntC_label.grid(row=4, column=1)

        self.bind("<FocusIn>", self.update_counters)
        self.config(menu=menubar)

        self.title(windows_title.application)

        self.minsize(400, 180)
        self.geometry('+300+150')

    def update_counters(self, event):
        cursorS.execute("SELECT count(*) FROM patients")
        self.cntP_label['text'], = cursorS.fetchone()
        cursorS.execute("SELECT count(*) FROM consultations")
        self.cntC_label['text'], = cursorS.fetchone()
        cursorS.execute("SELECT count(*) FROM patients WHERE therapeute='ch'")
        self.cntCH_label['text'], = cursorS.fetchone()
        cursorS.execute("SELECT count(*) FROM patients WHERE therapeute='tib'")
        self.cntTib_label['text'], = cursorS.fetchone()
        cursorS.execute("SELECT count(*) FROM patients WHERE therapeute='lik'")
        self.cntLIK_label['text'], = cursorS.fetchone()
        cursorS.execute("SELECT count(*) FROM patients WHERE therapeute='CRT'")
        self.cntCRT_label['text'], = cursorS.fetchone()


app = Application()
app.mainloop()
