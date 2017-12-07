#!/usr/bin/env python3

# File: bp.py

#    Copyright 2006-2017 Tibor Csernay

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
import mailcap
import datetime
import traceback
from collections import OrderedDict

import wx

from superpatient import BaseApp, DBMixin, HelpMenuMixin, CancelableMixin
from superpatient import bills, normalize_filename
from superpatient.bvr import gen_bvr_ref
import superpatient.customization as custo
from superpatient.customization import windows_title, errors_text, labels_text, DATE_FMT
from superpatient.models import Patient, Consultation, PAYMENT_METHODS, STATUS_OPENED, STATUS_PAYED, STATUS_PRINTED, STATUS_ABANDONED
from superpatient.ui.common import askyesno, showinfo, showwarning
from superpatient.ui import core


class MainFrame(DBMixin, HelpMenuMixin, core.MainFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_activate(self, event):
        if not event.Active:
            return
        self.cursor.execute("SELECT count(*) FROM patients")
        self.patients_count.LabelText = str(self.cursor.fetchone()[0])
        self.cursor.execute("SELECT count(*) FROM consultations")
        self.consultations_count.LabelText = str(self.cursor.fetchone()[0])

    def on_manage_collaborators(self, event):
        ManageCollaboratorsDialog(self).ShowModal()

    def on_manage_tariffs(self, event):
        ManageCostsDialog(self, 'tarifs').ShowModal()

    def on_manage_majorations(self, event):
        ManageCostsDialog(self, 'majorations').ShowModal()

    def on_manage_admin_costs(self, event):
        ManageCostsDialog(self, 'frais_admins').ShowModal()

    def on_manual_bill(self, event):
        ManualBillDialog(self).ShowModal()

    def on_manage_addresses(self, event):
        ManageAddressesDialog(self).ShowModal()

    def on_delete_data(self, event):
        ManagePatientsDialog(self, mode='delete').ShowModal()

    def on_dump_database(self, event):
        filename = wx.FileSelector("Sauvegarde de la base de donnée", default_extension="*.sql", wildcard="Database files (*.sql)|*.sql", flags=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT).strip()
        if filename:
            os.system("mysqldump -u root SuperPatient > %s" % filename)

    def on_restore_database(self, event):
        filename = wx.FileSelector("Restauration de la base de donnée", default_extension="*.sql", wildcard="Database files (*.sql)|*.sql", flags=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST).strip()
        if filename:
            os.system("mysql -u root SuperPatient < %s" % filename)

    def on_new_patient(self, event):
        PatientDialog(self).ShowModal()

    def on_search_patient(self, event):
        ManagePatientsDialog(self, mode='patient').ShowModal()

    def on_new_consultation(self, event):
        ManagePatientsDialog(self, mode='new_consultation').ShowModal()

    def on_search_consultation(self, event):
        ManagePatientsDialog(self, mode='consultation').ShowModal()


class ManualBillDialog(DBMixin, CancelableMixin, core.ManualBillDialog):
    MANUAL_ADDRESS = "Adresse manuelle"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_therapeute = ''
        self.therapeutes = {}
        self.cursor.execute("SELECT therapeute, login, entete FROM therapeutes")
        for therapeute, login, entete in self.cursor:
            self.therapeutes[therapeute] = entete + u'\n\n' + labels_text.adresse_pog
            if login == LOGIN:
                default_therapeute = therapeute
        self.therapeute.Set(sorted(self.therapeutes.keys()))
        self.therapeute.StringSelection = default_therapeute
        self.on_select_therapeute(None)
        self.addresses = OrderedDict({self.MANUAL_ADDRESS: None})
        self.cursor.execute("SELECT id, adresse FROM adresses ORDER BY id")
        for id, address in self.cursor:
            self.addresses[id] = address
        self.prefilled_address.Set(list(self.addresses.keys()))

        self.Bind(wx.EVT_ACTIVATE, self.on_activate, self)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_tab, self.address)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_tab, self.remark)

    def on_activate(self, event):
        self.reason.SetFocus()

    def on_tab(self, event):
        if event.KeyCode == wx.WXK_TAB:
            if event.EventObject == self.address:
                self.reason.SetFocus()
            else:
                self.address.SetFocus()
        else:
            event.Skip()

    def on_select_therapeute(self, event):
        self.therapeute_address.Value = self.therapeutes[self.therapeute.StringSelection]

    def on_select_address(self, event):
        if self.prefilled_address.StringSelection != self.MANUAL_ADDRESS:
            self.address.Value = self.addresses[self.prefilled_address.StringSelection]

    def on_generate(self, event):
        therapeute = self.therapeute.StringSelection
        therapeuteAddress = self.therapeutes[therapeute].strip()
        address = self.address.Value.strip()
        identifier = self.prefilled_address.StringSelection
        if identifier == self.MANUAL_ADDRESS:
            identifier = address.splitlines()[0].strip()
        now = datetime.datetime.now()
        ts = now.strftime('%Y-%m-%d_%H')
        filename = normalize_filename(u'%s_%sh.pdf' % (identifier.replace(' ', '_'), ts))
        reason = self.reason.Value.strip()
        try:
            amount = float(self.amount.Value.strip())
        except ValueError:
            showwarning(windows_title.invalid_error, errors_text.invalid_amount)
            return
        remark = self.remark.Value.strip()
        try:
            bv_ref = gen_bvr_ref(self.cursor, identifier[0], identifier[1], now)
            self.cursor.execute("""INSERT INTO factures_manuelles
                                          (identifiant, therapeute, destinataire, motif, montant_cts, remarque, date, bv_ref)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                                [identifier, therapeute, address, reason, int(amount * 100), remark, now.date(), bv_ref])
            facture_id = self.cursor.lastrowid
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
            return
        bills.manuals(filename, [(therapeuteAddress, address, reason, amount, remark, bv_ref)])
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
        os.system(cmd)
        if askyesno(windows_title.print_completed, labels_text.ask_confirm_print_bvr):
            self.cursor.execute("UPDATE factures_manuelles SET status = 'I' WHERE id = %s", [facture_id])


class ManageCollaboratorsDialog(DBMixin, CancelableMixin, core.ManageCollaboratorsDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SetTitle(windows_title.manage_colleagues)
        try:
            self.cursor.execute("""SELECT therapeute, login, entete FROM therapeutes ORDER BY therapeute""")
            self.collaborators = list(self.cursor)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            return
        self.index = None
        self.prev_index = None
        self.populate()

    def populate(self):
        self.collaborators_list.DeleteAllItems()
        for therapeute, login, entete in self.collaborators:
            self.collaborators_list.Append((therapeute, login, entete))
        for c in range(self.collaborators_list.ColumnCount):
            self.collaborators_list.SetColumnWidth(c, wx.LIST_AUTOSIZE)
        self.on_deselect_collaborator(None)
        self.Layout()
        self.Fit()

    def on_deselect_collaborator(self, event):
        self.prev_index = self.index
        self.index = None
        self.therapeute.Value = ''
        self.login.Value = ''
        self.address_header.Value = ''
        self.add_btn.Show()
        self.change_btn.Hide()
        self.remove_btn.Disable()
        self.Layout()

    def on_select_collaborator(self, event):
        selected = self.collaborators_list.GetFirstSelected()
        self.therapeute.Value = ''
        self.login.Value = ''
        self.address_header.Value = ''
        if selected != self.prev_index:
            self.index = selected
            therapeute, login, address_header = self.collaborators[self.index]
            self.therapeute.Value = therapeute
            self.login.Value = login
            self.address_header.Value = address_header
            self.add_btn.Hide()
            self.change_btn.Show()
            self.remove_btn.Enable()
            self.Layout()
        else:
            self.collaborators_list.Select(selected, False)

    def on_add_collaborator(self, event):
        if self.index is not None:
            return
        therapeute = self.therapeute.Value.strip()
        login = self.login.Value.strip()
        address_header = self.address_header.Value.strip()
        try:
            self.cursor.execute("""INSERT INTO therapeutes (therapeute, login, entete) VALUES (%s, %s, %s)""",
                                [therapeute, login, address_header])
            self.collaborators.append((therapeute, login, address_header))
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_change_collaborator(self, event):
        if self.index is None:
            return
        therapeute = self.therapeute.Value.strip()
        login = self.login.Value.strip()
        address_header = self.address_header.Value.strip()
        try:
            key, _, _ = self.collaborators[self.index]
            self.cursor.execute("""UPDATE therapeutes SET therapeute = %s, login = %s, entete = %s WHERE therapeute = %s""",
                                [therapeute, login, address_header, key])
            self.collaborators[self.index] = (therapeute, login, address_header)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_remove_collaborator(self, event):
        if self.index is None:
            return
        try:
            key, _, _ = self.collaborators[self.index]
            self.cursor.execute("""DELETE FROM therapeutes WHERE therapeute = %s""", [key])
            del self.collaborators[self.index]
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_delete)
        self.populate()


class ManageCostsDialog(DBMixin, CancelableMixin, core.ManageCostsDialog):
    def __init__(self, parent, table, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.table = table
        self.SetTitle(getattr(windows_title, 'manage_'+self.table))
        try:
            self.cursor.execute("""SELECT description, prix_cts FROM %s""" % self.table)
            self.costs = list(self.cursor)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            return
        self.index = None
        self.prev_index = None
        self.populate()

    def populate(self):
        self.costs_list.DeleteAllItems()
        for description, prix_cts in self.costs:
            self.costs_list.Append((description, '%7.2f' % (prix_cts/100.)))
        for c in range(self.costs_list.ColumnCount):
            self.costs_list.SetColumnWidth(c, wx.LIST_AUTOSIZE)
        self.on_deselect_cost(None)
        self.Layout()
        self.Fit()

    def on_deselect_cost(self, event):
        self.prev_index = self.index
        self.index = None
        self.price.Value = ''
        self.description.Value = ''
        self.add_btn.Show()
        self.change_btn.Hide()
        self.remove_btn.Disable()
        self.Layout()

    def on_select_cost(self, event):
        selected = self.costs_list.GetFirstSelected()
        self.price.Value = ''
        self.description.Value = ''
        if selected != self.prev_index:
            self.index = selected
            description, prix_cts = self.costs[self.index]
            self.description.Value = description
            self.price.Value = '%0.2f' % (prix_cts/100.)
            self.add_btn.Hide()
            self.change_btn.Show()
            self.remove_btn.Enable()
            self.Layout()
        else:
            self.costs_list.Select(selected, False)

    def on_add_cost(self, event):
        if self.index is not None:
            return
        description = self.description.Value.strip()
        try:
            prix_cts = int(float(self.price.Value.strip()) * 100)
        except:
            traceback.print_exc()
            showwarning(windows_title.invalid_error, errors_text.invalid_cost)
            return
        try:
            self.cursor.execute("""INSERT INTO %s (description, prix_cts) VALUES (%%s, %%s)""" % self.table, [description, prix_cts])
            self.costs.append((description, prix_cts))
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_change_cost(self, event):
        if self.index is None:
            return
        description = self.description.Value.strip()
        try:
            prix_cts = int(float(self.price.Value.strip()) * 100)
        except:
            traceback.print_exc()
            showwarning(windows_title.invalid_error, errors_text.invalid_cost)
            return
        try:
            key, _ = self.costs[self.index]
            self.cursor.execute("""UPDATE %s SET description = %%s, prix_cts = %%s WHERE description = %%s""" % self.table,
                                [description, prix_cts, key])
            self.costs[self.index] = (description, prix_cts)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_remove_cost(self, event):
        if self.index is None:
            return
        try:
            key, _ = self.costs[self.index]
            self.cursor.execute("""DELETE FROM %s WHERE description = %%s""" % self.table, [key])
            del self.costs[self.index]
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_delete)
        self.populate()


class ManageAddressesDialog(DBMixin, CancelableMixin, core.ManageAddressesDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SetTitle(windows_title.manage_addresses)
        try:
            self.cursor.execute("SELECT id, adresse FROM adresses ORDER BY id")
            self.addresses = list(self.cursor)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            return
        self.index = None
        self.prev_index = None
        self.populate()

    def populate(self):
        self.addresses_list.DeleteAllItems()
        for identifier, address in self.addresses:
            self.addresses_list.Append((identifier, address.replace('\n', ', ')))
        for c in range(self.addresses_list.ColumnCount):
            self.addresses_list.SetColumnWidth(c, wx.LIST_AUTOSIZE)
        self.on_deselect_address(None)
        self.Layout()
        self.Fit()

    def on_deselect_address(self, event):
        self.prev_index = self.index
        self.index = None
        self.identifier.Value = ''
        self.address.Value = ''
        self.add_btn.Show()
        self.change_btn.Hide()
        self.remove_btn.Disable()
        self.Layout()

    def on_select_address(self, event):
        selected = self.addresses_list.GetFirstSelected()
        self.identifier.Value = ''
        self.address.Value = ''
        if selected != self.prev_index:
            self.index = selected
            identifier, address = self.addresses[self.index]
            self.identifier.Value = identifier
            self.address.Value = address
            self.add_btn.Hide()
            self.change_btn.Show()
            self.remove_btn.Enable()
            self.Layout()
        else:
            self.addresses_list.Select(selected, False)

    def on_add_address(self, event):
        if self.index is not None:
            return
        identifier = self.identifier.Value.strip()
        address = self.address.Value.strip()
        try:
            self.cursor.execute("""INSERT INTO adresses (id, adresse) VALUES (%s, %s)""",
                                [identifier, address])
            self.addresses.append((identifier, address))
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_change_address(self, event):
        if self.index is None:
            return
        identifier = self.identifier.Value.strip()
        address = self.address.Value.strip()
        try:
            key, _ = self.addresses[self.index]
            self.cursor.execute("""UPDATE adresses SET id = %s, adresse = %s WHERE id = %s""",
                                [identifier, address, key])
            self.addresses[self.index] = (identifier, address)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_remove_address(self, event):
        if self.index is None:
            return
        try:
            key, _ = self.addresses[self.index]
            self.cursor.execute("""DELETE FROM adresses WHERE id = %s""", [key])
            del self.addresses[self.index]
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_delete)
        self.populate()


class ManagePatientsDialog(DBMixin, CancelableMixin, core.ManagePatientsDialog):
    def __init__(self, parent, mode, *args, **kwargs):
        self.mode = mode
        titles = dict(delete=windows_title.delete_patient,
                      patient=windows_title.show_change_patient,
                      consultation=windows_title.show_change_consult,
                      new_consultation=windows_title.patients_db)
        assert self.mode in titles
        super().__init__(parent, *args, **kwargs)
        self.SetTitle(titles[self.mode])
        self.show_patient_btn.Show(self.mode == 'patient')
        self.modify_patient_btn.Show(self.mode == 'patient')
        self.delete_patient_btn.Show(self.mode == 'delete')
        self.show_consultations_btn.Show(self.mode in ('delete', 'consultation'))
        self.new_consultation_btn.Show(self.mode == 'new_consultation')
        self.display_consultations_btn.Show(self.mode == 'new_consultation')
        self.Fit()

    def get_selected_patient_id(self):
        selected = self.patients.GetFirstSelected()
        return self.results[selected] if selected != -1 else None

    def open_patient(self, readonly):
        id_patient = self.get_selected_patient_id()
        if id_patient is not None:
            PatientDialog(self, id_patient, readonly).ShowModal()
            self.on_search_patient(None)

    def on_search_patient(self, event):
        try:
            self.cursor.execute("""SELECT id, sex, nom, prenom, (SELECT count(*) FROM consultations WHERE id = patients.id)
                                     FROM patients
                                    WHERE nom LIKE %s AND prenom LIKE %s
                                 ORDER BY nom""",
                                [self.lastname.Value.strip(), self.firstname.Value.strip()])
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_search)
        self.results = []
        self.patients.DeleteAllItems()
        for id, sex, nom, prenom, n_consult in self.cursor:
            self.patients.Append((sex, nom, prenom))
            self.results.append(id)
        for c in range(self.patients.ColumnCount):
            self.patients.SetColumnWidth(c, wx.LIST_AUTOSIZE)

    def on_show_patient(self, event):
        self.open_patient(True)

    def on_modify_patient(self, event):
        self.open_patient(False)

    def on_new_consultation(self, event):
        id_patient = self.get_selected_patient_id()
        if id_patient is not None:
            ConsultationDialog(self, id_patient, readonly=False).ShowModal()

    def on_show_consultations(self, event):
        id_patient = self.get_selected_patient_id()
        if id_patient is not None:
            ManageConsultationsDialog(self, id_patient, self.mode).ShowModal()

    def on_delete_patient(self, event):
        id_patient = self.get_selected_patient_id()
        if id_patient is not None:
            try:
                self.cursor.execute("""SELECT sex, nom, prenom, date_naiss
                                         FROM patients
                                         WHERE id = %s""",
                                    [id_patient])
                sex, nom, prenom, date_naiss = self.cursor.fetchone()
            except:
                traceback.print_exc()
                showwarning(windows_title.db_error, errors_text.db_search)
                return
            if askyesno(windows_title.delete, labels_text.suppr_def_1+u'\n'+str(sex+u" "+prenom+u" "+nom)+labels_text.suppr_def_2+date_naiss.strftime(DATE_FMT)+u'\n'+labels_text.suppr_def_3):
                try:
                    self.cursor.execute("DELETE FROM rappels WHERE id_consult IN (SELECT id_consult FROM consultations WHERE id=%s)", [id_patient])
                    self.cursor.execute("DELETE FROM consultations WHERE id=%s", [id_patient])
                    self.cursor.execute("DELETE FROM patients WHERE id=%s", [id_patient])
                    showinfo(windows_title.done, labels_text.pat_sup_1+str(prenom+u" "+nom+u" ")+labels_text.pat_sup_2)
                except:
                    traceback.print_exc()
                    showwarning(windows_title.db_error, errors_text.db_delete)
        self.on_search_patient(None)

    def on_display_consultations(self, event):
        id_patient = self.get_selected_patient_id()
        if id_patient is not None:
            AllConsultationsDialog(self, id_patient).ShowModal()


class ManageConsultationsDialog(DBMixin, CancelableMixin, core.ManageConsultationsDialog):
    def __init__(self, parent, id_patient, mode, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.id_patient = id_patient
        self.mode = mode
        assert self.mode in ('delete', 'consultation')
        self.delete_btn.Show(self.mode == 'delete')
        self.show_btn.Show(self.mode == 'consultation')
        self.modify_btn.Show(self.mode == 'consultation')
        self.show_all_btn.Show(self.mode == 'consultation')
        try:
            self.cursor.execute("""SELECT nom, prenom, sex, therapeute, date_naiss
                                     FROM patients WHERE id = %s""", [self.id_patient])
            nom, prenom, sex, therapeute, date_naiss = self.cursor.fetchone()
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            return

        if self.mode == 'delete':
            self.SetTitle(windows_title.delete_consultation % (sex, nom))
        else:
            self.SetTitle(windows_title.show_consultation % (sex, nom))
        self.patient.LabelText = "{} {} {}\nNaissance: {}\nThérapeute: {}".format(sex, prenom, nom, date_naiss, therapeute)

        self.update_list()
        self.Layout()
        self.Fit()

    def update_list(self):
        try:
            self.cursor.execute("""SELECT id_consult, date_consult, therapeute, MC, paye_le
                                     FROM consultations
                                    WHERE id=%s
                                 ORDER BY date_consult DESC""",
                                [self.id_patient])
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_show)
        self.results = []
        self.consultations.DeleteAllItems()
        for id_consult, date_consult, therapeute, MC, paye_le in self.cursor:
            index = self.consultations.Append((date_consult, therapeute or '', MC))
            if paye_le is None:
                self.consultations.SetItemTextColour(index, wx.Colour(128, 0, 0))
            self.results.append(id_consult)
        self.consultations.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.consultations.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.consultations.SetColumnWidth(2, wx.LIST_AUTOSIZE)

    def get_selected_consult_id(self):
        selected = self.consultations.GetFirstSelected()
        return self.results[selected] if selected != -1 else None

    def open_consultation(self, readonly):
        id_consult = self.get_selected_consult_id()
        if id_consult is not None:
            ConsultationDialog(self, self.id_patient, id_consult, readonly=readonly).ShowModal()

    def on_delete_consultation(self, event):
        id_consult = self.get_selected_consult_id()
        if id_consult is not None:
            if askyesno(windows_title.delete, labels_text.sup_def_c):
                try:
                    self.cursor.execute("DELETE FROM rappels WHERE id_consult=%s", [id_consult])
                    self.cursor.execute("DELETE FROM consultations WHERE id_consult=%s", [id_consult])
                    showinfo(windows_title.done, labels_text.cons_sup)
                except:
                    traceback.print_exc()
                    showwarning(windows_title.db_error, errors_text.db_delete)
        self.update_list()

    def on_show_consultation(self, event):
        self.open_consultation(True)

    def on_modify_consultation(self, event):
        self.open_consultation(False)

    def on_show_all_consultations(self, event):
        AllConsultationsDialog(self, self.id_patient).ShowModal()


class AllConsultationsDialog(DBMixin, CancelableMixin, core.AllConsultationsDialog):
    def __init__(self, parent, id_patient, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.id_patient = id_patient
        try:
            patient = Patient.load(self.cursor, self.id_patient)
        except:
            print("id_patient:", self.id_patient)
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_show)
            return
        html = ["""
        <html>
        <head>
        <style>
        .date {{ color: red; }}
        .unpaid {{ color: darkred; }}
        h3 {{ color: blue; }}
        .important {{ color: darkblue; }}
        body {{ font-family: sans-serif; font-size: small; line-height: 1.0; }}
        h1, h2, h3 {{ margin-top: 1ex; margin-bottom: 1ex; }}
        div {{ white-space: pre-line; }}
        </style>
        </head>
        <body>
        <h1>{sex} {prenom} {nom}, {date_naiss}</h1>
        <h3>Antécédents personnels</h3>
        <div>{ATCD_perso}</div>
        <h3>Antécédents familiaux</h3>
        <div>{ATCD_fam}</div>
        <h2 class="important">Important</h2>
        <div>{important}</div>
        <h3>Assurance complémentaire</h3>
        <div>{ass_compl}</div>
        """.format(**patient.__dict__)]
        for consult in Consultation.yield_all(self.cursor, where=dict(id=patient.id), order='-date_consult'):
            html += filter(None, [
                """<hr/><h2 class="date">********** Consultation du {} **********</h2>""".format(consult.date_consult),
                """<h3 class="unpaid">!!!!! Non-payé !!!!!</h3>""" if consult.paye_le is None else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.eg, consult.EG) if consult.EG.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.therapeute, consult.therapeute) if consult.therapeute else None,
                """<h3>{}&nbsp;: {}</h3><div>{}</div>""".format(labels_text.mc, (labels_text.accident if consult.MC_accident else labels_text.maladie), consult.MC),
                """<h3>{}</h3><div>{}</div>""".format(labels_text.thorax, consult.APT_thorax) if consult.APT_thorax.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.abdomen, consult.APT_abdomen) if consult.APT_abdomen.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.tete, consult.APT_tete) if consult.APT_tete.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.ms, consult.APT_MS) if consult.APT_MS.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.mi, consult.APT_MI) if consult.APT_MI.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.gen, consult.APT_system) if consult.APT_system.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.a_osteo, consult.A_osteo) if consult.A_osteo.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.exph, consult.exam_phys) if consult.exam_phys.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.ttt, consult.traitement) if consult.traitement.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.expc, consult.exam_pclin) if consult.exam_pclin.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.remarques, consult.divers) if consult.divers.strip() else None,
                """<h3>{}</h3><div>{}</div>""".format(labels_text.paye, consult.paye) if consult.paye.strip() else None,
            ])
        html.append("</body></html>")
        self.html.SetPage('\n'.join(html), "")


class PatientDialog(DBMixin, CancelableMixin, core.PatientDialog):
    def __init__(self, parent, id_patient=None, readonly=False):
        super().__init__(parent)
        patient = self.patient = Patient.load(self.cursor, id_patient) if id_patient is not None else Patient()
        self.readonly = readonly and patient
        self.new_consultation_btn.Show(not self.patient)
        self.save_btn.Show(not self.patient)
        self.update_btn.Show(bool(self.patient and not self.readonly))

        if patient:
            title = windows_title.patient
        else:
            title = windows_title.new_patient
        self.SetTitle(title)

        if patient.date_ouverture is None:
            patient.date_ouverture = datetime.date.today()

        # Setup fields value
        self.patient_id.Value = str(patient.id) if patient else ''

        if patient.sex:
            {'Mme': self.female, 'Mr': self.male, 'Enfant': self.child}[patient.sex].SetValue(True)
        self.lastname.Value = patient.nom or ''
        self.firstname.Value = patient.prenom or ''

        try:
            self.cursor.execute("""SELECT therapeute, login FROM therapeutes ORDER BY therapeute""")
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            return
        therapeutes = []
        for t, login in self.cursor:
            therapeutes.append(t)
            if login == LOGIN and patient.therapeute is None:
                patient.therapeute = t
        self.therapeute.Set(therapeutes)
        try:
            self.therapeute.SetSelection(therapeutes.index(patient.therapeute))
        except ValueError:
            self.therapeute.SetSelection(wx.NOT_FOUND)

        if patient.date_naiss:
            self.birthdate.Value = patient.date_naiss.strftime(DATE_FMT)
        else:
            self.birthdate.Value = 'JJ.MM.AAAA'
            self.birthdate.SelectAll()

        self.opening_date.Value = patient.date_ouverture.strftime(DATE_FMT)
        self.fixed_phone.Value = patient.phone or ''
        self.mobile_phone.Value = patient.portable or ''
        self.professional_phone.Value = patient.profes_phone or ''
        self.email.Value = patient.mail or ''
        self.private_address.Value = patient.adresse or ''
        self.important.Value = patient.important or ''
        self.main_doctor.Value = patient.medecin or ''
        self.other_doctors.Value = patient.autre_medecin or ''
        self.complementary_insurance.Value = patient.ass_compl or ''
        self.profession.Value = patient.profes or ''
        self.civil_status.Value = patient.etat or ''
        self.sent_by.Value = patient.envoye or ''
        self.remarks.Value = patient.divers or ''

        self.highlight_missing_fields()

        if self.readonly:
            for widget in (self.female, self.male, self.child, self.firstname, self.lastname, self.therapeute, self.birthdate,
                           self.opening_date, self.fixed_phone, self.mobile_phone, self.professional_phone, self.email,
                           self.private_address, self.important, self.main_doctor, self.other_doctors, self.complementary_insurance,
                           self.profession, self.civil_status, self.sent_by, self.remarks):
                widget.Disable()

    def highlight_missing_fields(self):
        black = wx.Colour(0, 0, 0)
        red = wx.Colour(255, 0, 0)
        if any((self.female.Value, self.male.Value, self.child.Value)):
            self.sex_label.SetForegroundColour(black)
        else:
            self.sex_label.SetForegroundColour(red)
        if self.lastname.Value.strip():
            self.lastname_label.SetForegroundColour(black)
        else:
            self.lastname_label.SetForegroundColour(red)
        if self.firstname.Value.strip():
            self.firstname_label.SetForegroundColour(black)
        else:
            self.firstname_label.SetForegroundColour(red)
        if self.therapeute.StringSelection:
            self.therapeute_label.SetForegroundColour(black)
        else:
            self.therapeute_label.SetForegroundColour(red)
        if self.birthdate.Value.strip():
            self.birthdate_label.SetForegroundColour(black)
        else:
            self.birthdate_label.SetForegroundColour(red)

    def is_patient_valid(self):
        sex = 'Mme' if self.female.Value else 'Mr' if self.male.Value else 'Enfant' if self.child.Value else None
        if not sex or not self.therapeute.StringSelection or not self.lastname.Value.strip() or not self.firstname.Value.strip():
            self.highlight_missing_fields()
            showwarning(windows_title.invalid_error, errors_text.missing_data)
            return False
        return True

    def set_patient_fields(self):
        from dateutil import parse_date
        patient = self.patient
        patient.date_naiss = parse_date(self.birthdate.Value.strip())
        patient.date_ouverture = parse_date(self.opening_date.Value.strip())
        patient.therapeute = self.therapeute.StringSelection
        patient.sex = 'Mme' if self.female.Value else 'Mr' if self.male.Value else 'Enfant' if self.child.Value else None
        patient.nom = self.lastname.Value.strip()
        patient.prenom = self.firstname.Value.strip()
        patient.ATCD_perso = getattr(patient, 'ATCD_perso', "")
        patient.ATCD_fam = getattr(patient, 'ATCD_fam', "")
        patient.medecin = self.main_doctor.Value.strip()
        patient.autre_medecin = self.other_doctors.Value.strip()
        patient.phone = self.fixed_phone.Value.strip()
        patient.portable = self.mobile_phone.Value.strip()
        patient.profes_phone = self.professional_phone.Value.strip()
        patient.mail = self.email.Value.strip()
        patient.adresse = self.private_address.Value.strip()
        patient.ass_compl = self.complementary_insurance.Value.strip()
        patient.profes = self.profession.Value.strip()
        patient.etat = self.civil_status.Value.strip()
        patient.envoye = self.sent_by.Value.strip()
        patient.divers = self.remarks.Value.strip()
        patient.important = self.important.Value.strip()

    def on_new_consultation(self, event):
        self.add_entry(with_consultation=True)

    def on_save(self, event):
        self.add_entry(with_consultation=False)

    def add_entry(self, with_consultation):
        from dateutil import parse_date
        try:
            parse_date(self.birthdate.Value.strip())
            parse_date(self.opening_date.Value.strip())
        except:
            traceback.print_exc()
            showwarning(windows_title.invalid_error, errors_text.invalid_date)
            return
        if not self.is_patient_valid():
            return
        try:
            self.set_patient_fields()
            self.patient.save(self.cursor)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_insert)
            return
        self.on_cancel()
        if with_consultation:
            ConsultationDialog(self.Parent, self.patient.id).ShowModal()

    def on_update(self, event):
        if not self.is_patient_valid():
            return
        try:
            self.set_patient_fields()
            self.patient.save(self.cursor)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.on_cancel()


class ConsultationDialog(DBMixin, CancelableMixin, core.ConsultationDialog):
    def __init__(self, parent, id_patient, id_consult=None, readonly=False):
        super().__init__(parent)
        self.patient = Patient.load(self.cursor, id_patient)
        self.consultation = Consultation.load(self.cursor, id_consult) if id_consult is not None else Consultation(id=id_patient)
        self.consultation.patient = self.patient
        self.readonly = readonly

        self.cancel_btn.Show(not self.readonly)
        self.save_close_btn.Show(not self.readonly)
        self.ok_btn.Show(self.readonly)
        self.print_btn.Show(bool(self.consultation))
        self.cursor.execute("SELECT count(*) FROM consultations WHERE id = %s", [self.patient.id])
        count, = self.cursor.fetchone()
        self.show_all_consultations_btn.Show(count > 0)

        consult = self.consultation
        try:
            if consult.therapeute is not None:
                consult.therapeute = consult.therapeute.strip()  # Sanity guard against old data
            self.cursor.execute("""SELECT therapeute, login FROM therapeutes ORDER BY therapeute""")
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            return
        therapeutes = ['']
        for t, login in self.cursor:
            therapeutes.append(t)
            if consult.therapeute is None and login == LOGIN:
                consult.therapeute = t
        if consult:
            title = windows_title.consultation % (consult.date_consult, self.patient.sex, self.patient.nom)
        else:
            consult.date_consult = datetime.date.today()
            consult.MC_accident = False
            title = windows_title.new_consultation % (self.patient.sex, self.patient.nom)
        self.therapeute.Set(therapeutes)

        self.prices = self.load_costs('tarifs', False)
        self.markups = self.load_costs('majorations')
        self.admin_costs = self.load_costs('frais_admins')
        self.price.Set(list(self.prices.keys()))
        self.markup.Set(list(self.markups.keys()))
        self.admin_cost.Set(list(self.admin_costs.keys()))

        fixed_therapist_and_cost = self.readonly or (consult.id_consult is not None and 'MANAGE_CONSULTATIONS' not in wx.GetApp().ACCESS_RIGHTS)

        self.SetTitle(title)

        self.accident.Value = bool(consult.MC_accident)
        self.illness.Value = not self.accident.Value
        self.reason.Value = consult.MC or ''
        self.general_state.Value = consult.EG or ''
        self.paraclinic_exams.Value = consult.exam_pclin or ''
        self.medical_background.Value = self.patient.ATCD_perso or ''
        self.family_history.Value = self.patient.ATCD_fam or ''
        self.thorax.Value = consult.APT_thorax or ''
        self.abdomen.Value = consult.APT_abdomen or ''
        self.physical_exam.Value = consult.exam_phys or ''
        self.head_neck.Value = consult.APT_tete or ''
        self.upper_limbs.Value = consult.APT_MS or ''
        self.lower_limbs.Value = consult.APT_MI or ''
        self.other.Value = consult.APT_system or ''
        self.important.Value = self.patient.important or ''
        self.anamnesis.Value = consult.A_osteo or ''
        self.treatment.Value = consult.traitement or ''
        self.remarks.Value = consult.divers or ''
        self.consultation_date.Value = consult.date_consult.strftime(DATE_FMT)
        if consult.therapeute:
            self.therapeute.StringSelection = consult.therapeute
        self.payment.Value = consult.paye or ''

        price = [l for l, v in self.prices.items() if v == (consult.prix_cts, consult.prix_txt)]
        if price:
            self.price.StringSelection = price[0]
        else:
            print("WARN: price not found:", (consult.prix_cts, consult.prix_txt))
            print(self.prices)
            self.price.Selection = wx.NOT_FOUND
        markup = [l for l, v in self.markups.items() if v == (consult.majoration_cts, consult.majoration_txt)]
        if markup:
            self.markup.StringSelection = markup[0]
        else:
            print("WARN: majoration not found:", (consult.majoration_cts, consult.majoration_txt))
            self.markup.Selection = wx.NOT_FOUND
        admin_cost = [l for l, v in self.admin_costs.items() if v == (consult.frais_admin_cts, consult.frais_admin_txt)]
        if admin_cost:
            self.admin_cost.StringSelection = admin_cost[0]
        else:
            print("WARN: price not found:", (consult.frais_admin_cts, consult.frais_admin_txt))
            self.admin_cost.Selection = wx.NOT_FOUND

        if consult.paye_par:
            self.payment_method.Selection = PAYMENT_METHODS.index(consult.paye_par)
        if consult and consult.paye_le:
            self.payment_date.LabelText = labels_text.paye_le+' '+str(consult.paye_le)

        if self.readonly:
            for widget in (self.illness, self.accident, self.reason, self.general_state, self.paraclinic_exams,
                           self.medical_background, self.family_history, self.thorax, self.abdomen, self.physical_exam,
                           self.head_neck, self.upper_limbs, self.lower_limbs, self.other, self.important, self.anamnesis,
                           self.treatment, self.remarks, self.consultation_date, self.therapeute, self.payment, self.price,
                           self.markup, self.admin_cost, self.payment_method):
                widget.Disable()

        if fixed_therapist_and_cost:
            self.therapeute.Disable()
            self.price.Disable()
            self.markup.Disable()
            self.admin_cost.Disable()
            self.payment_method.Disable()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def load_costs(self, table, optional=True):
        try:
            self.cursor.execute("""SELECT description, prix_cts FROM %s ORDER BY prix_cts""" % table)
            costs = [('Aucun(e)', (0, ''))] if optional else []
            for description, prix_cts in self.cursor:
                label = u'%s : %0.2f CHF' % (description, prix_cts/100.)
                costs.append((label, (prix_cts, description)))
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            costs = [(u"-- ERREUR --", None)]
        return OrderedDict(costs)

    def set_consultation_fields(self):
        from dateutil import parse_date
        consult = self.consultation
        consult.date_consult = parse_date(self.consultation_date.Value.strip())
        consult.heure_consult = consult.heure_consult or datetime.datetime.now().time()
        consult.MC = self.reason.Value.strip()
        consult.MC_accident = self.accident.Value
        consult.EG = self.general_state.Value.strip()
        consult.exam_pclin = self.paraclinic_exams.Value.strip()
        consult.exam_phys = self.physical_exam.Value.strip()
        consult.paye = self.payment.Value.strip()
        consult.divers = self.remarks.Value.strip()
        consult.APT_thorax = self.thorax.Value.strip()
        consult.APT_abdomen = self.abdomen.Value.strip()
        consult.APT_tete = self.head_neck.Value.strip()
        consult.APT_MS = self.upper_limbs.Value.strip()
        consult.APT_MI = self.lower_limbs.Value.strip()
        consult.APT_system = self.other.Value.strip()
        consult.A_osteo = self.anamnesis.Value.strip()
        consult.traitement = self.treatment.Value.strip()
        consult.therapeute = self.therapeute.StringSelection
        consult.prix_cts, consult.prix_txt = self.prices.get(self.price.StringSelection, ("", 0))
        consult.majoration_cts, consult.majoration_txt = self.markups.get(self.markup.StringSelection, ("", 0))
        consult.frais_admin_cts, consult.frais_admin_txt = self.admin_costs.get(self.admin_cost.StringSelection, ("", 0))
        consult.paye_par = self.payment_method.StringSelection
        if not custo.PAIEMENT_SORTIE and consult.paye_le is None and consult.paye_par not in (u'BVR', u'CdM', u'Dû', u'PVPE'):
            consult.paye_le = datetime.date.today()
        try:
            if consult.paye_par in (u'BVR', u'PVPE'):
                if consult.id_consult:
                    self.cursor.execute("SELECT prix_cts + majoration_cts + frais_admin_cts FROM consultations WHERE id_consult = %s", [consult.id_consult])
                    old_price, = self.cursor.fetchone()
                else:
                    old_price = 0
                if consult.bv_ref is None or consult.prix_cts + consult.majoration_cts + consult.frais_admin_cts != old_price:
                    consult.bv_ref = gen_bvr_ref(self.cursor, self.patient.prenom, self.patient.nom, consult.date_consult)
            else:
                consult.bv_ref = None
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            return

    def on_close(self, event):
        if self.readonly or event.EventObject == self.ok_btn or askyesno(windows_title.really_cancel, labels_text.really_cancel):
            self.EndModal(0)

    def on_save(self, event):
        if not self.price.StringSelection or not self.payment_method.StringSelection:
            showwarning(windows_title.missing_error, errors_text.missing_payment_info)
            return
        if not self.therapeute.StringSelection:
            showwarning(windows_title.missing_error, errors_text.missing_therapeute)
            return
        self.set_consultation_fields()
        try:
            if self.consultation:
                self.cursor.execute("""SELECT paye_par FROM consultations WHERE id_consult=%s""", [self.consultation.id_consult])
                old_paye_par, = self.cursor.fetchone()
                generate_pdf = self.consultation.paye_par != old_paye_par
                if old_paye_par != self.consultation.paye_par and self.consultation.paye_par in (u'BVR', u'PVPE') and self.consultation.status != STATUS_ABANDONED:
                    self.consultation.status = STATUS_OPENED
                    self.consultation.paye_le = None
            else:
                self.consultation.status = STATUS_OPENED
                if not custo.PAIEMENT_SORTIE and self.consultation.paye_par in (u'Cash', u'Carte'):
                    self.consultation.status = STATUS_PAYED
                generate_pdf = self.consultation.paye_par not in (u'CdM', u'Dû')
            self.consultation.save(self.cursor)

            self.patient.important = self.important.Value.strip()
            self.patient.ATCD_perso = self.medical_background.Value.strip()
            self.patient.ATCD_fam = self.family_history.Value.strip()
            self.patient.save(self.cursor)
            if generate_pdf:
                self.on_print()
            self.EndModal(0)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)

    def on_print(self, *args):
        ts = datetime.datetime.now().strftime('%H')
        filename = normalize_filename(u'%s_%s_%s_%s_%sh.pdf' % (self.patient.nom, self.patient.prenom, self.patient.sex, self.consultation.date_consult, ts))
        bills.consultations(filename, self.cursor, [self.consultation])
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
        os.system(cmd)
        if self.consultation.paye_par == u'BVR' and askyesno(windows_title.print_completed, labels_text.ask_confirm_print_bvr):
            self.consultation.status = STATUS_PRINTED
            self.consultation.save(self.cursor)

    def on_show_all_consultations(self, event):
        AllConsultationsDialog(self, self.patient.id).ShowModal()


class MainApp(BaseApp):
    MainFrameClass = MainFrame

    def __init__(self, *args, **kwargs):
        # Define the access rights based on the executable name
        self.ACCESS_RIGHTS = []
        # Available values are:
        #   MANAGE_DB
        #   MANAGE_THERAPISTS
        #   MANAGE_COSTS
        #   MANAGE_PATIENTS
        #   MANAGE_CONSULTATIONS
        #   MANUAL_BILL
        app_name = os.path.basename(sys.argv[0])
        if app_name in ['bp_admin.py', 'bp_fondateur.py']:
            self.ACCESS_RIGHTS += ['MANAGE_PATIENTS', 'MANAGE_CONSULTATIONS', 'MANUAL_BILL']
        if app_name in ['bp_admin.py']:
            self.ACCESS_RIGHTS += ['MANAGE_DB', 'MANAGE_THERAPISTS', 'MANAGE_COSTS']
        super().__init__(*args, **kwargs)


LOGIN = os.getlogin()


if __name__ == '__main__':
    app = MainApp()
    try:
        if not os.path.exists(custo.PDF_DIR):
            os.mkdir(custo.PDF_DIR)
        elif not os.path.isdir(custo.PDF_DIR) or not os.access(custo.PDF_DIR, os.W_OK):
            raise ValueError()
    except:
        showwarning(u"Wrong directory", u"Cannot store PDFs in " + custo.PDF_DIR)
        sys.exit()
    app.MainLoop()
