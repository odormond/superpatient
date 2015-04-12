#!/usr/bin/env python2
# -*- coding: latin1 -*-

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
fmt = "%d-%m-%Y"
#strftime(fmt)

try:
    import Tkinter as tk
    import tkMessageBox
    import tkFileDialog

except:
    tkMessageBox.showwarning("Error", "Tkinter is not correctly installed !")
    sys.exit()

try:
    import bp_Dialog
except:
    tkMessageBox.showwarning("Missing file", "bp_Dialog.py is missing")
    sys.exit()

try:
    import bp_variables
except:
    tkMessageBox.showwarning("Missing file", "bp_variables.py is missing")
    sys.exit()

try:
    import bp_texte
except:
    tkMessageBox.showwarning("Missing file", "bp_texte.py is missing")
    sys.exit()

try:
    import bp_custo
except:
    tkMessageBox.showwarning("Missing file", "bp_custo.py is missing")
    sys.exit()

try:
    import bp_connect
except:
    tkMessageBox.showwarning("Missing file", "bp_connect.py is missing")
    sys.exit()

try:
    from bp_facture import facture
except:
    tkMessageBox.showwarning("Missing file", "bp_facture.py is missing")
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

cursorS = db.cursor()
cursorI = db.cursor()
cursorU = db.cursor()
cursorR = db.cursor()


def RadioWidget(parent, key, row, column, options, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black', want_widget=False):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=bp_custo.labels_text[key], font=bp_custo.labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    radioVar = tk.StringVar()
    if value:
        radioVar.set(value)
    frame = tk.Frame(parent)
    r1 = None
    for option in options:
        if isinstance(option, tuple):
            value, label = option
        else:
            value = label = option
        r = tk.Radiobutton(frame, text=label, variable=radioVar, value=value, font=bp_custo.fields_font[key], disabledforeground='black')
        if readonly:
            r.config(state=tk.DISABLED)
        r.pack(side=tk.LEFT)
        if r1 is None:
            r1 = r
    frame.grid(row=row+rowshift, column=column+colshift, sticky=tk.W+tk.E)
    if want_widget:
        return radioVar, r1
    return radioVar


def EntryWidget(parent, key, row, column, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black', want_widget=False):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=bp_custo.labels_text[key], font=bp_custo.labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    var = tk.StringVar()
    if value:
        var.set(value)
    entry = tk.Entry(parent, textvariable=var, font=bp_custo.fields_font[key], fg=field_fg, disabledforeground='black')
    if readonly:
        entry.config(state=tk.DISABLED)
    entry.grid(row=row+rowshift, column=column+colshift, sticky=tk.W+tk.E)
    if want_widget:
        return var, entry
    return var


def OptionWidget(parent, key, row, column, options, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black', want_widget=False):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=bp_custo.labels_text[key], font=bp_custo.labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    frame = tk.Frame(parent)
    var = tk.StringVar()
    if value:
        var.set(value)
    entry_var = tk.StringVar()
    entry = tk.Entry(frame, textvariable=entry_var, font=bp_custo.fields_font[key], fg=field_fg, disabledforeground='black')

    def update_var(*event):
        if len(event) == 3:
            val = entry_var.get().strip()
            if val:
                var.set(val)
        elif event == ('Autre...',):
            parent.after_idle(lambda: entry.focus_set())
        else:
            entry_var.set('')

    dropdown = tk.OptionMenu(frame, var, *(options+['Autre...']), command=update_var)
    entry_var.trace('w', update_var)
    if readonly:
        dropdown.config(state=tk.DISABLED)
    dropdown.pack(side=tk.LEFT, fill=tk.X, expand=1)
    entry.pack(side=tk.RIGHT, fill=tk.X, expand=2)
    frame.grid(row=row+rowshift, column=column+colshift, sticky=tk.W+tk.E)
    if want_widget:
        return var, dropdown
    return var


def PriceWidget(parent, key, row, column, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black', want_widget=False):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=bp_custo.labels_text[key], font=bp_custo.labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    try:
        cursorS.execute("""SELECT description, prix_cts from tarifs""")
        tarifs = ['%s : %0.2f CHF' % (d, p/100.) for d, p in cursorS]
    except:
        traceback.print_exc()
        tkMessageBox.showwarning(bp_texte.error, bp_texte.imp_lire)
        tarifs = ["-- ERREUR --"]
    var = tk.StringVar()
    if value:
        var.set('%0.2f CHF' % (value/100.))
        widget = tk.Entry(parent, textvariable=var, font=bp_custo.fields_font[key], fg=field_fg, disabledforeground='black')
    else:
        dropvar = tk.StringVar()

        def set_price(value):
            var.set(value.split(' : ')[1])

        widget = tk.OptionMenu(parent, dropvar, *tarifs, command=set_price)
    if readonly:
        widget.config(state=tk.DISABLED)
    widget.grid(row=row+rowshift, column=column+colshift, sticky=tk.W+tk.E)
    if want_widget:
        return var, widget
    return var


def TextWidget(parent, key, row, column, rowspan=1, columnspan=1, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black'):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=bp_custo.labels_text[key], font=bp_custo.labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    frame = tk.Frame(parent)
    scroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
    var = tk.Text(frame, yscrollcommand=scroll.set, relief=tk.SUNKEN, borderwidth=1, height=bp_custo.fields_height[key], font=bp_custo.fields_font[key], wrap=tk.WORD, fg=field_fg)
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
    return var


def ListboxWidget(parent, key, row, column, rowspan=1, columnspan=2):
    frame = tk.Frame(parent)
    scroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
    select = tk.Listbox(frame, yscrollcommand=scroll.set, height=bp_custo.fields_height[key], width=bp_custo.fields_width[key])
    scroll.config(command=select.yview)
    select.grid(row=0, column=0, sticky=tk.NSEW)
    scroll.grid(row=0, column=1, pady=3, sticky=tk.N+tk.S)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=tk.NSEW)
    return select


class Patient(bp_Dialog.Dialog):
    def __init__(self, parent, id_patient=None, readonly=False):
        self.id_patient = id_patient
        self.readonly = readonly and id_patient is not None
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        if self.id_patient is None:
            tk.Button(box, text=bp_texte.B1, command=self.add_1ere_Consult).pack(side=tk.LEFT)
            tk.Button(box, text=bp_texte.B2, command=self.addEntry).pack(side=tk.LEFT)
        elif not self.readonly:
            tk.Button(box, text=bp_texte.B11, command=self.updateEntry).pack(side=tk.LEFT)
        tk.Button(box, text=bp_texte.B3, command=self.cancel).pack(side=tk.LEFT)

        self.bind("<Escape>", self.cancel)

        box.pack()

    def addEntry(self, avec_anamnese=False):
        try:
            cursorS.execute("SELECT max(id)+1 FROM patients")
            id_patient, = cursorS.fetchone()
            if id_patient is None:
                id_patient = 1
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(bp_texte.BD, bp_texte.id_imp)
            return
        try:
            if (self.nomVar.get() != '' and self.prenomVar.get() != '' and self.date_naissVar.get() != ''):
                cursorI.execute("""INSERT INTO patients
                                          (id, date_ouverture, therapeute, sex, nom, prenom, date_naiss, ATCD_perso,
                                           ATCD_fam, medecin, autre_medecin, phone, portable, profes_phone, mail,
                                           adresse, ass_compl, profes, etat, envoye, divers, important)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                [id_patient, self.date_ouvVar.get(), self.therapeuteVar.get(), self.sexVar.get(),
                                    self.nomVar.get(), self.prenomVar.get(), self.date_naissVar.get(), "", "",
                                    self.medecinVar.get(1.0, tk.END), self.autre_medecinVar.get(1.0, tk.END),
                                    self.phoneVar.get(), self.portableVar.get(), self.profes_phoneVar.get(),
                                    self.mailVar.get(), self.adresseVar.get(1.0, tk.END), self.ass_complVar.get(),
                                    self.profesVar.get(), self.etatVar.get(), self.envoyeVar.get(),
                                    self.diversVar.get(1.0, tk.END), self.importantVar.get(1.0, tk.END)])
                self.cancel()
                if avec_anamnese:
                    Consultation(self.parent, id_patient)
            else:
                tkMessageBox.showwarning(bp_texte.info_manq, bp_texte.npdn)
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(bp_texte.enr, bp_texte.imp_format_date)

    def updateEntry(self):
        if not tkMessageBox.askyesno(bp_texte.data_p, bp_texte.case_sex):
            return  # Abort
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
                            [self.sexVar.get(), self.nomVar.get(), self.prenomVar.get(), self.therapeuteVar.get(), self.date_naissVar.get(), self.date_ouvVar.get(),
                                self.adresseVar.get(1.0, tk.END), self.importantVar.get(1.0, tk.END), self.medecinVar.get(1.0, tk.END), self.autre_medecinVar.get(1.0, tk.END), self.phoneVar.get(), self.portableVar.get(),
                                self.profes_phoneVar.get(), self.mailVar.get(), self.ass_complVar.get(), self.profesVar.get(), self.etatVar.get(), self.envoyeVar.get(), self.diversVar.get(1.0, tk.END),
                                self.id_patient])
            self.cancel()
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(bp_texte.error, bp_texte.modif_imp)

    def add_1ere_Consult(self):
        self.addEntry(avec_anamnese=True)

    def body(self, master):
        if self.id_patient:
            if self.readonly:
                title = bp_texte.fich_p
            else:
                title = bp_texte.B11
        else:
            title = bp_texte.nouveau_patient
        self.title(title)
        self.geometry('+200+5')
        self.geometry("1024x710")

        sexe = therapeute = nom = prenom = date_naiss = phone = medecin = portable = profes_phone = mail = adresse = autre_medecin = ass_compl = profes = etat = envoye = divers = important = None
        date_ouv = datetime.date.today()

        try:
            cursorS.execute("""SELECT therapeute FROM therapeutes""")
            therapeutes = [t for t, in cursorS]
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(bp_texte.error, bp_texte.imp_lire)
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
        self.sexVar, focus_widget = RadioWidget(master, key='sexe', row=0, column=0, options=[('Mme', 'F'), ('Mr', 'M')], value=sexe, readonly=self.readonly, want_widget=True)

        self.nomVar = EntryWidget(master, key='nom', row=1, column=0, fg=mandatory(nom), value=nom, readonly=self.readonly)
        self.therapeuteVar = OptionWidget(master, key='therapeute', row=1, column=2, value=therapeute, options=therapeutes, readonly=self.readonly)

        self.prenomVar = EntryWidget(master, key='prenom', row=2, column=0, fg=mandatory(prenom), value=prenom, readonly=self.readonly)

        if date_naiss:
            key = 'naissance'
            fg = 'black'
        else:
            key = 'naissance_le'
            fg = 'red'
            date_naiss = bp_texte.veuillez
        self.date_naissVar = EntryWidget(master, key=key, row=3, column=0, fg=fg, value=date_naiss, readonly=self.readonly)
        self.date_ouvVar = EntryWidget(master, key='date_ouverture', row=3, column=2, value=date_ouv, readonly=self.readonly)

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
            self.title_str = bp_texte.voir_modif_p
        elif action == 'gerer_consultations':
            def act(parent, id_patient, readonly):
                GererConsultations(parent, id_patient, 'afficher')
            self.action_class = act
            self.title_str = bp_texte.v_m_cons
        elif action == 'supprimer':
            self.title_str = bp_texte.db_sup_p
        elif action == 'nouvelle_consultation':
            self.action_class = Consultation
            self.title_str = bp_texte.BP
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        tk.Button(box, text=bp_texte.B7, command=self.recherche).pack(side=tk.LEFT)
        if self.action == 'patient':
            tk.Button(box, text=bp_texte.B8, fg='blue', command=self.readonly_action).pack(side=tk.LEFT)
            tk.Button(box, text=bp_texte.B9, fg='red', command=self.trigger_action).pack(side=tk.LEFT)
        elif self.action == 'gerer_consultations':
            tk.Button(box, text=bp_texte.B14, command=self.trigger_action).pack(side=tk.LEFT)
        elif self.action == 'supprimer':
            tk.Button(box, text=bp_texte.B16, fg='red', command=self.supprime).pack(side=tk.LEFT)
            tk.Button(box, text=bp_texte.B14, fg='blue', command=self.supprime_consultation).pack(side=tk.LEFT)
        elif self.action == 'nouvelle_consultation':
            tk.Button(box, text=bp_texte.B12, fg='blue', command=self.trigger_action).pack(side=tk.LEFT)
            tk.Button(box, text=bp_texte.B13, command=self.liste_consultations).pack(side=tk.LEFT)
        tk.Button(box, text=bp_texte.B3, command=self.cancel).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def recherche(self):
        try:
            cursorS.execute("""SELECT id, sex, nom, prenom, (SELECT count(*) FROM consultations WHERE id = patients.id)
                                 FROM patients
                                WHERE nom LIKE %s AND prenom LIKE %s
                             ORDER BY nom""",
                            [self.nomRec.get(), self.prenomRec.get()])
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(bp_texte.error, bp_texte.rech_imp)
        self.results = []
        self.select.delete(0, tk.END)
        for id, sex, nom, prenom, n_consult in cursorS:
            self.select.insert(tk.END, nom+', '+prenom+', '+sex+', %d consultations' % n_consult)
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
                tkMessageBox.showwarning(bp_texte.error, bp_texte.rech_imp)
                return
            if tkMessageBox.askyesno(bp_texte.suppr, bp_texte.suppr_def_1+'\n'+str(sex+" "+prenom+" "+nom)+bp_texte.suppr_def_2+str(date_naiss)+'\n'+bp_texte.suppr_def_3):
                try:
                    cursorR.execute("DELETE FROM consultations WHERE id=%s", [id])
                    cursorR.execute("DELETE FROM patients WHERE id=%s", [id])
                    tkMessageBox.showinfo(bp_texte.fait, bp_texte.pat_sup_1+str(prenom+" "+nom+" ")+bp_texte.pat_sup_2)
                except:
                    traceback.print_exc()
                    tkMessageBox.showwarning(bp_texte.error, bp_texte.sup_imp)
        self.recherche()

    def body(self, master):
        self.title(self.title_str)
        self.geometry('+200+5')

        frame = tk.Frame(master)
        self.nomRec = EntryWidget(frame, key='nom', row=0, column=0, value='%')
        self.prenomRec = EntryWidget(frame, key='prenom', row=1, column=0, value='%')
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

        tk.Button(box, text=bp_texte.B10, command=self.cancel).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def auto_affiche(self):
        try:
            cursorS.execute("""SELECT sex, nom, prenom, date_naiss, ATCD_perso, ATCD_fam, important FROM patients WHERE id = %s""", [self.id_patient])
            sex, nom, prenom, date_naiss, ATCD_perso, ATCD_fam, Important = cursorS.fetchone()
            cursorS.execute("""SELECT id_consult, date_consult, MC, EG, APT_thorax, APT_abdomen, APT_tete, APT_MS,
                                      APT_MI, APT_system, A_osteo, exam_phys, traitement, divers, exam_pclin, paye
                                 FROM consultations
                                WHERE id=%s
                             ORDER BY date_consult DESC""",
                            [self.id_patient])
        except:
            print "id_patient:", self.id_patient
            traceback.print_exc()
            tkMessageBox.showwarning(bp_texte.error, bp_texte.affich_imp)
            return
        self.toutes.tag_config("date", foreground="red", font=("Helvetica", 15, "bold"))
        self.toutes.tag_config("titre", foreground="blue", font=("Helvetica", 15))
        self.toutes.tag_config("personne", foreground="black", font=("Helvetica", 15, "bold"))
        self.toutes.tag_config("important", foreground="darkblue", font=("Helvetica", 15, "bold"))
        self.toutes.insert(tk.END, sex+' '+prenom+' '+nom+', '+str(date_naiss)+'\n', "personne")
        self.toutes.insert(tk.END, bp_texte.atcdp+'\n', "titre")
        self.toutes.insert(tk.END, ATCD_perso)
        self.toutes.insert(tk.END, bp_texte.atcdf+'\n', "titre")
        self.toutes.insert(tk.END, ATCD_fam)
        self.toutes.insert(tk.END, bp_texte.important+'\n', "important")
        self.toutes.insert(tk.END, Important)
        for id_consult, date_consult, MC, EG, APT_thorax, APT_abdomen, APT_tete, APT_MS, APT_MI, APT_system, A_osteo, exam_phys, traitement, divers, exam_pclin, paye in cursorS:
            self.toutes.insert(tk.END, '********** '+bp_texte.cons_du_1er+str(date_consult)+' **********'+'\n', "date")
            if EG.strip():
                self.toutes.insert(tk.END, bp_texte.eg+'\n', "titre")
                self.toutes.insert(tk.END, EG)
            self.toutes.insert(tk.END, bp_texte.mc+'\n', "titre")
            self.toutes.insert(tk.END, MC)
            if APT_thorax.strip():
                self.toutes.insert(tk.END, bp_texte.thorax+'\n', "titre")
                self.toutes.insert(tk.END, APT_thorax)
            if APT_abdomen.strip():
                self.toutes.insert(tk.END, bp_texte.abdomen+'\n', "titre")
                self.toutes.insert(tk.END, APT_abdomen)
            if APT_tete.strip():
                self.toutes.insert(tk.END, bp_texte.tete+'\n', "titre")
                self.toutes.insert(tk.END, APT_tete)
            if APT_MS.strip():
                self.toutes.insert(tk.END, bp_texte.ms+'\n', "titre")
                self.toutes.insert(tk.END, APT_MS)
            if APT_MI.strip():
                self.toutes.insert(tk.END, bp_texte.mi+'\n', "titre")
                self.toutes.insert(tk.END, APT_MI)
            if APT_system.strip():
                self.toutes.insert(tk.END, bp_texte.gen+'\n', "titre")
                self.toutes.insert(tk.END, APT_system)
            if A_osteo.strip():
                self.toutes.insert(tk.END, bp_texte.a_osteo+'\n', "titre")
                self.toutes.insert(tk.END, A_osteo)
            if exam_phys.strip():
                self.toutes.insert(tk.END, bp_texte.exph+'\n', "titre")
                self.toutes.insert(tk.END, exam_phys)
            if traitement.strip():
                self.toutes.insert(tk.END, bp_texte.ttt+'\n', "titre")
                self.toutes.insert(tk.END, traitement)
            if exam_pclin.strip():
                self.toutes.insert(tk.END, bp_texte.expc+'\n', "titre")
                self.toutes.insert(tk.END, exam_pclin)
            if divers.strip():
                self.toutes.insert(tk.END, bp_texte.rem+'\n', "titre")
                self.toutes.insert(tk.END, divers)
            if paye.strip():
                self.toutes.insert(tk.END, bp_texte.paye+'\n', "titre")
                self.toutes.insert(tk.END, paye)

    def body(self, master):
        self.geometry('+200+5')
        self.geometry("700x710")

        self.toutes = TextWidget(master, key='ttes_cons', row=0, column=0, side_by_side=False, fg='blue')
        scroll = tk.Scrollbar(master, orient=tk.VERTICAL)
        tk.Label(master, text=bp_texte.ttes_cons, font=("Helvetica", bp_variables.entete_taille_vcs, 'bold'), fg='blue').grid(row=0, column=0, sticky=tk.W)
        self.toutes = tk.Text(master, relief=tk.SUNKEN, height=bp_variables.liste_hauteur_vcs, yscrollcommand=scroll.set, font=("Helvetica", bp_variables.texte_bulle_taille_vcs), fg='black', wrap=tk.WORD)
        scroll.config(command=self.toutes.yview)
        scroll.grid(row=1, column=1, sticky=tk.W+tk.N+tk.S)
        self.toutes.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

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
            tk.Button(box, text=bp_texte.B10, command=self.cancel).pack(side=tk.LEFT)
        else:
            tk.Button(box, text=bp_texte.B2, command=self.modif).pack(side=tk.LEFT)  # Was B11
            tk.Button(box, text=bp_texte.B3, command=self.cancel).pack(side=tk.LEFT)
        cursorS.execute("SELECT count(*) FROM consultations WHERE id = %s", [self.id_patient])
        count, = cursorS.fetchone()
        if count > 0:
            tk.Button(box, text="Toutes les consultations", command=lambda: ListeConsultations(self.parent, self.id_patient)).pack(side=tk.LEFT)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def modif(self):
        if tkMessageBox.askyesno(bp_texte.cons_pat, bp_texte.appl_modif):
            try:
                description, prix = self.prixVar.get().split(' : ')
                prix_cts = int(float(prix[:-4]) * 100 + 0.5)
                paye_le = self.paye_leVar.get()
                if not paye_le.strip():
                    paye_le = None
                if self.id_consult is None:
                    try:
                        cursorS.execute("SELECT max(id_consult)+1 FROM consultations")
                        self.id_consult, = cursorS.fetchone()
                        if self.id_consult is None:
                            self.id_consult = 1
                    except:
                        traceback.print_exc()
                        tkMessageBox.showwarning(bp_texte.BD, bp_texte.id_imp)
                        return
                    cursorI.execute("""INSERT INTO consultations
                                            (id_consult, id, date_consult,
                                             MC, EG, exam_pclin, exam_phys, paye, divers, APT_thorax, APT_abdomen,
                                             APT_tete, APT_MS, APT_MI, APT_system, A_osteo, traitement, therapeute,
                                             prix_cts, paye_par, paye_le)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                    [self.id_consult, self.id_patient, self.date_ouvcVar.get(),
                                        self.MCVar.get(1.0, tk.END), self.EGVar.get(1.0, tk.END), self.exam_pclinVar.get(1.0, tk.END),
                                        self.exam_physVar.get(1.0, tk.END), self.payeVar.get(1.0, tk.END),
                                        self.diversVar.get(1.0, tk.END), self.APT_thoraxVar.get(1.0, tk.END),
                                        self.APT_abdomenVar.get(1.0, tk.END), self.APT_teteVar.get(1.0, tk.END),
                                        self.APT_MSVar.get(1.0, tk.END), self.APT_MIVar.get(1.0, tk.END),
                                        self.APT_systemVar.get(1.0, tk.END), self.A_osteoVar.get(1.0, tk.END),
                                        self.traitementVar.get(1.0, tk.END), self.therapeuteVar.get(),
                                        prix_cts, self.paye_parVar.get(), paye_le])
                else:
                    cursorU.execute("""UPDATE consultations
                                        SET MC=%s,
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
                                            paye_par=%s,
                                            paye_le=%s
                                        WHERE id_consult=%s""",
                                    [self.MCVar.get(1.0, tk.END), self.EGVar.get(1.0, tk.END), self.exam_pclinVar.get(1.0, tk.END),
                                        self.exam_physVar.get(1.0, tk.END), self.payeVar.get(1.0, tk.END),
                                        self.diversVar.get(1.0, tk.END), self.APT_thoraxVar.get(1.0, tk.END),
                                        self.APT_abdomenVar.get(1.0, tk.END), self.APT_teteVar.get(1.0, tk.END),
                                        self.APT_MSVar.get(1.0, tk.END), self.APT_MIVar.get(1.0, tk.END),
                                        self.APT_systemVar.get(1.0, tk.END), self.A_osteoVar.get(1.0, tk.END),
                                        self.traitementVar.get(1.0, tk.END), self.date_ouvcVar.get(),
                                        self.therapeuteVar.get(), prix_cts, self.paye_parVar.get(), paye_le,
                                        self.id_consult])
                cursorU.execute("UPDATE patients SET important=%s, ATCD_perso=%s, ATCD_fam=%s WHERE id=%s",
                                [self.importantVar.get(1.0, tk.END), self.ATCD_persoVar.get(1.0, tk.END), self.ATCD_famVar.get(1.0, tk.END), self.id_patient])
                self.cancel()
                filename = os.tempnam()+'.pdf'
                cursorS.execute("""SELECT adresse FROM therapeutes WHERE therapeute = %s""", [self.therapeuteVar.get()])
                adresse_therapeute, = cursorS.fetchone()
                cursorS.execute("""SELECT adresse FROM patients WHERE id = %s""", [self.id_patient])
                adresse_patient, = cursorS.fetchone()
                facture(filename, adresse_therapeute, adresse_patient, description, prix, self.date_ouvcVar.get(), with_bv=True)
                cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
                os.system(cmd)
            except:
                traceback.print_exc()
                tkMessageBox.showwarning(bp_texte.error, bp_texte.modif_imp)

    def body(self, master):
        self.geometry('+200+5')
        self.geometry("1024x800")

        try:
            cursorS.execute("""SELECT therapeute FROM therapeutes""")
            therapeutes = [t for t, in cursorS]
            cursorS.execute("""SELECT sex, nom, prenom, date_naiss, important, ATCD_perso, ATCD_fam, therapeute
                                 FROM patients
                                WHERE id=%s""",
                            [self.id_patient])
            sex, nom, prenom, date_naiss, important, ATCD_perso, ATCD_fam, therapeute = cursorS.fetchone()
            if self.id_consult:
                cursorS.execute("""SELECT date_consult, MC, EG, exam_pclin, exam_phys, traitement, APT_thorax, APT_abdomen,
                                        APT_tete, APT_MS, APT_MI, APT_system, A_osteo, divers, paye, therapeute, prix_cts, paye_par, paye_le
                                    FROM consultations
                                    WHERE id_consult=%s""",
                                [self.id_consult])
                (date_consult, MC, EG, exam_pclin, exam_phys, traitement, APT_thorax, APT_abdomen,
                 APT_tete, APT_MS, APT_MI, APT_system, A_osteo, divers, paye, therapeute, prix_cts,
                 paye_par, paye_le) = cursorS.fetchone()
            else:
                date_consult = MC = EG = exam_pclin = exam_phys = traitement = APT_thorax = APT_abdomen = APT_tete = APT_MS = APT_MI = APT_system = A_osteo = divers = paye = therapeute = prix_cts = paye_par = paye_le = None
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(bp_texte.error, bp_texte.imp_lire)
            return

        self.title("%s %s - %s %s" % (bp_texte.cons_du_1er, date_consult, sex, nom))
        #self.minsize(800, 650)

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
        # +----------+----------+----------+
        # |seanceprix| paye par | paye le  |
        # +----------+----------+----------+
        self.MCVar = TextWidget(master, key='mc', row=0, column=0, side_by_side=False, fg='blue', field_fg='blue', value=MC, readonly=self.readonly)
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

        self.date_ouvcVar = EntryWidget(master, key='date_ouverture', row=12, column=0, side_by_side=False, value=datetime.date.today(), readonly=self.readonly)
        self.therapeuteVar = OptionWidget(master, key='therapeute', row=12, column=1, side_by_side=False, value=therapeute, options=therapeutes, readonly=self.readonly)
        self.payeVar = TextWidget(master, key='paye', row=12, column=2, side_by_side=False, value=paye, field_fg='red', readonly=self.readonly)

        self.prixVar = PriceWidget(master, key='seance', row=14, column=0, side_by_side=False, value=prix_cts, readonly=self.readonly)
        self.paye_parVar = RadioWidget(master, key='paye_par', row=14, column=1, side_by_side=False, value=paye_par, options=bp_custo.MOYEN_DE_PAYEMENT, readonly=self.readonly)
        self.paye_leVar = EntryWidget(master, key='paye_le', row=14, column=2, side_by_side=False, value=paye_le, readonly=self.readonly)

        self.paye_parVar.trace('w', self.update_paye_le)

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

    def update_paye_le(self, *args):
        if self.paye_parVar.get() == 'BVR':
            self.paye_leVar.set('')
        else:
            self.paye_leVar.set(datetime.date.today())


class GererConsultations(bp_Dialog.Dialog):
    def __init__(self, parent, id_patient, action):
        self.id_patient = id_patient
        self.action = action
        assert action in ('afficher', 'supprimer')
        bp_Dialog.Dialog.__init__(self, parent)

    def buttonbox(self):
        box = tk.Frame(self)

        if self.action == 'afficher':
            tk.Button(box, text=bp_texte.B18, fg='blue', command=self.affiche).pack(side=tk.LEFT)
            tk.Button(box, text=bp_texte.B15, fg='red', command=self.modif).pack(side=tk.LEFT)
            tk.Button(box, text=bp_texte.B13, fg='blue', command=lambda: ListeConsultations(self.parent, self.id_patient)).pack(side=tk.LEFT)
        if self.action == 'supprimer':
            tk.Button(box, text=bp_texte.B17, fg='red', command=self.supprime_c).pack(side=tk.LEFT)
        tk.Button(box, text=bp_texte.B3, command=self.cancel).pack(side=tk.LEFT)
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
            tkMessageBox.showwarning(bp_texte.error, bp_texte.affich_imp)
        self.results = []
        self.select_consult.delete(0, tk.END)
        for id_consult, date_consult, MC in cursorS:
            self.select_consult.insert(tk.END, str(date_consult)+' '+MC)
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
            if tkMessageBox.askyesno(bp_texte.suppr, bp_texte.sup_def_c):
                try:
                    cursorR.execute("DELETE FROM consultations WHERE id_consult=%s", [id_consult])
                    tkMessageBox.showinfo(bp_texte.fait, bp_texte.cons_sup)
                except:
                    traceback.print_exc()
                    tkMessageBox.showwarning(bp_texte.error, bp_texte.sup_imp)
        self.affiche_toutes()

    def body(self, master):
        self.title(bp_texte.sup_cons_de)
        self.geometry('+200+5')

        try:
            cursorS.execute("""SELECT nom, prenom, sex, therapeute, date_naiss
                                 FROM patients WHERE id = %s""", [self.id_patient])
            nom, prenom, sex, therapeute, date_naiss = cursorS.fetchone()
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(bp_texte.error, bp_texte.imp_lire)
            return

        tk.Label(master, text=sex+' '+prenom+' '+nom, font=("Helvetica", bp_variables.texte_bulle_taille_rc, 'bold')).grid(row=0, column=0, sticky=tk.W)
        tk.Label(master, text=bp_texte.naissance+str(date_naiss), font=("Helvetica", bp_variables.entete_taille_rc)).grid(row=1, column=0, sticky=tk.W)
        tk.Label(master, text=bp_texte.therapeute+therapeute, font=("Helvetica", bp_variables.entete_taille_rc)).grid(row=2, column=0, sticky=tk.W)

        self.select_consult = ListboxWidget(master, key='rc', row=3, column=0)

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(3, weight=1)

        self.affiche_toutes()


class save_db(bp_Dialog.Dialog):
    def body(self, master):
        myFormats = [('Database', '*.sql'), ]

        fileName = tkFileDialog.asksaveasfilename(filetypes=myFormats, title="Sauvegarde de la Database")
        if len(fileName) > 0:
            os.system("mysqldump -u root basicpatient > %s" % (fileName))
            self.cancel()


class restore_db(bp_Dialog.Dialog):
    def body(self, master):
        myFormats = [('Database', '*.sql'), ]

        fileName = tkFileDialog.askopenfilename(filetypes=myFormats, title='Restauration de la Database')
        if fileName is not None:
            os.system("mysql -u root basicpatient < %s" % (fileName))
            self.cancel()


class apropos(bp_Dialog.Dialog):
    def body(self, master):
        self.title(bp_texte.apropos)
        self.geometry('+350+250')
        tk.Label(master, text=bp_texte.apropos_description, font=("Helvetica", 13, 'bold')).grid(row=0, column=0, sticky=tk.W)


class licence(bp_Dialog.Dialog):
    def body(self, master):
        self.title(bp_texte.licence)
        self.geometry('+350+250')
        tk.Label(master, text=bp_texte.licence_description, font=("Helvetica", 13, 'bold')).grid(row=0, column=0, sticky=tk.W)


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        if (sys.platform != "win32") and hasattr(sys, 'frozen'):
            self.tk.call('console', 'hide')

        self.option_add('*font', 'Helvetica -15')

        menubar = tk.Menu(self)

        adminmenu = tk.Menu(menubar, tearoff=0)
        adminmenu.add_separator()
        adminmenu.add_command(label=bp_texte.B29, command=lambda: GererPatients(self, 'supprimer'), foreground='red')
        adminmenu.add_command(label=bp_texte.B30, command=lambda: save_db(self))
        adminmenu.add_command(label=bp_texte.B31, command=lambda: restore_db(self))

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=bp_texte.B32, command=lambda: apropos(self))
        helpmenu.add_command(label=bp_texte.B33, command=lambda: licence(self))

        menubar.add_cascade(label=bp_texte.administration, menu=adminmenu)
        menubar.add_cascade(label=bp_texte.help, menu=helpmenu)

        tk.Button(self, text=bp_texte.B25, command=lambda: Patient(self)).grid(row=0, column=0, sticky=tk.W)

        tk.Button(self, text=bp_texte.B26, command=lambda: GererPatients(self, 'patient')).grid(row=1, column=0, sticky=tk.W)
        self.cntP_label = tk.Label(self)
        self.cntP_label.grid(row=1, column=1)

        tk.Label(self, text="").grid(row=2, column=0)
        tk.Label(self, text="Ch").grid(row=2, column=1)
        self.cntCH_label = tk.Label(self)
        self.cntCH_label.grid(row=2, column=2)
        tk.Label(self, text="Tib").grid(row=2, column=3)
        self.cntTib_label = tk.Label(self)
        self.cntTib_label.grid(row=2, column=4)

        tk.Button(self, text=bp_texte.B27, command=lambda: GererPatients(self, 'nouvelle_consultation')).grid(row=3, column=0, sticky=tk.W)
        tk.Label(self, text="LI").grid(row=3, column=1)
        self.cntLIK_label = tk.Label(self)
        self.cntLIK_label.grid(row=3, column=2)
        tk.Label(self, text="CRT").grid(row=3, column=3)
        self.cntCRT_label = tk.Label(self)
        self.cntCRT_label.grid(row=3, column=4)

        tk.Button(self, text=bp_texte.B28, command=lambda: GererPatients(self, 'gerer_consultations')).grid(row=4, column=0, sticky=tk.W)
        self.cntC_label = tk.Label(self)
        self.cntC_label.grid(row=4, column=1)

        #self.update_counters()

        self.bind("<FocusIn>", self.update_counters)
        self.config(menu=menubar)

        # 1er argument de basicpatients.py
        self.title(bp_texte.titre)

        self.minsize(400, 180)
        self.geometry('+300+150')
        #self.geometry("320x200")

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
