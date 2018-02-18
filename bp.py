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
from superpatient import bills, normalize_filename, gen_title
from superpatient.bvr import gen_bvr_ref
import superpatient.customization as custo
from superpatient.customization import windows_title, errors_text, labels_text, DATE_FMT
from superpatient.models import (Patient, Consultation, Bill, Position,
                                 STATUS_OPENED, STATUS_PAYED, STATUS_PRINTED,
                                 SEX_ALL, SEX_FEMALE, SEX_MALE,
                                 BILL_TYPE_CONSULTATION, BILL_TYPE_MANUAL,
                                 DEFAULT_CANTON, CANTONS)
from superpatient.ui.common import askyesno, showinfo, showwarning
from superpatient.ui import core, bill


FIX_PATIENT_DELAY = 500  # milliseconds


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
        self.Fit()

    def on_manage_collaborators(self, event):
        ManageCollaboratorsDialog(self).ShowModal()

    def on_manage_tarifs(self, event):
        ManageCostsDialog(self, 'tarifs').ShowModal()

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
            if not entete.strip():
                continue
            if 'RCC' in entete:
                name, rcc = [line for i, line in enumerate(entete.splitlines()) if i == 0 or line.startswith('RCC')]
                rcc = rcc.replace('RCC', '').strip()
            else:
                name = entete
                rcc = ''
            firstname, lastname = name.split(' ', 1)
            self.therapeutes[therapeute] = firstname, lastname, rcc
            if login == LOGIN:
                default_therapeute = therapeute
        self.therapeute.Set(sorted(self.therapeutes.keys()))
        self.therapeute.StringSelection = default_therapeute
        self.on_select_therapeute(None)
        self.addresses = OrderedDict({self.MANUAL_ADDRESS: None})
        self.cursor.execute("SELECT id, title, firstname, lastname, complement, street, zip, city FROM addresses ORDER BY id")
        for row in self.cursor:
            self.addresses[row[0]] = row[1:]
        self.prefilled_address.Set(list(self.addresses.keys()))

        self.Bind(wx.EVT_ACTIVATE, self.on_activate, self)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_tab, self.remark)

    def on_activate(self, event):
        self.Fit()
        self.title.SetFocus()

    def on_select_therapeute(self, event):
        firstname, lastname, rcc = self.therapeutes[self.therapeute.StringSelection]
        if rcc:
            rcc = 'RCC ' + rcc
        self.therapeute_address.Value = '{} {}\n{}\n\n{}'.format(firstname, lastname, rcc, labels_text.adresse_pog)

    def on_select_address(self, event):
        if self.prefilled_address.StringSelection != self.MANUAL_ADDRESS:
            title, firstname, lastname, complement, street, zip, city = self.addresses[self.prefilled_address.StringSelection]
            self.title.Value = title or ''
            self.firstname.Value = firstname
            self.lastname.Value = lastname
            self.complement.Value = complement or ''
            self.street.Value = street
            self.zip.Value = zip
            self.city.Value = city

    def on_generate(self, event):
        therapeute = self.therapeute.StringSelection
        t_firstname, t_lastname, t_rcc = self.therapeutes[therapeute]
        title = self.title.Value.strip()
        firstname = self.firstname.Value.strip()
        lastname = self.lastname.Value.strip()
        complement = self.complement.Value.strip()
        street = self.street.Value.strip()
        zip = self.zip.Value.strip()
        city = self.city.Value.strip()
        identifier = self.prefilled_address.StringSelection
        if identifier == self.MANUAL_ADDRESS:
            name = [firstname]
            if lastname:
                name.append(lastname)
            identifier = '_'.join(name)
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
            bill = Bill(type=BILL_TYPE_MANUAL,
                        bv_ref=bv_ref,
                        payment_method='BVR',
                        status=STATUS_OPENED,
                        timestamp=datetime.datetime.now(),
                        author_id=therapeute,
                        author_lastname=t_lastname,
                        author_firstname=t_firstname,
                        author_rcc=t_rcc,
                        title=title,
                        lastname=lastname,
                        firstname=firstname,
                        complement=complement,
                        street=street,
                        zip=zip,
                        city=city,
                        comment=remark)
            bill.save(self.cursor)
            # and positions
            pos = Position(id_bill=bill.id, position_date=bill.timestamp.date(),
                           tarif_code='999', tarif_description=reason,
                           quantity=1, price_cts=int(amount * 100))
            pos.save(self.cursor)
            bill.positions.append(pos)
            bill.total_cts = pos.price_cts
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
            return
        bills.manuals(filename, [bill])
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
        os.system(cmd)
        if askyesno(windows_title.print_completed, labels_text.ask_confirm_print_bvr):
            bill.status = STATUS_PRINTED
            bill.save(self.cursor)


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
            self.cursor.execute("""SELECT code, description, unit_price_cts FROM %s ORDER BY code, description""" % self.table)
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
        for code, description, unit_price_cts in self.costs:
            self.costs_list.Append((code, description or '', '%7.2f' % (unit_price_cts/100.) if unit_price_cts is not None else ''))
        for c in range(self.costs_list.ColumnCount):
            self.costs_list.SetColumnWidth(c, wx.LIST_AUTOSIZE if c == 1 else wx.LIST_AUTOSIZE_USEHEADER)
        self.on_deselect_cost(None)
        self.Layout()
        self.Fit()

    def on_deselect_cost(self, event):
        self.prev_index = self.index
        self.index = None
        self.code.Value = ''
        self.description.Value = ''
        self.price.Value = ''
        self.add_btn.Show()
        self.change_btn.Hide()
        self.remove_btn.Disable()
        self.Layout()

    def on_select_cost(self, event):
        selected = self.costs_list.GetFirstSelected()
        self.code.Value = ''
        self.description.Value = ''
        self.price.Value = ''
        if selected != self.prev_index:
            self.index = selected
            code, description, unit_price_cts = self.costs[self.index]
            self.code.Value = code
            self.description.Value = description or ''
            self.price.Value = '%0.2f' % (unit_price_cts/100.) if unit_price_cts is not None else ''
            self.add_btn.Hide()
            self.change_btn.Show()
            self.remove_btn.Enable()
            self.Layout()
        else:
            self.costs_list.Select(selected, False)

    def _get_values(self):
        code = self.code.Value.strip()
        description = self.description.Value.strip() or None
        unit_price_cts = self.price.Value.strip() or None
        if unit_price_cts is not None:
            try:
                unit_price_cts = int(float(unit_price_cts) * 100)
            except:
                traceback.print_exc()
                showwarning(windows_title.invalid_error, errors_text.invalid_cost)
                return None
        return [code, description, unit_price_cts]

    def on_add_cost(self, event):
        if self.index is not None:
            return
        values = self._get_values()
        if values is None:
            return
        try:
            self.cursor.execute("""INSERT INTO %s (code, description, unit_price_cts) VALUES (%%s, %%s, %%s)""" % self.table, values)
            self.costs.append(values)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_change_cost(self, event):
        if self.index is None:
            return
        values = self._get_values()
        if values is None:
            return
        try:
            old_value = self.costs[self.index]
            self.cursor.execute("""UPDATE %s SET code = %%s, description = %%s, unit_price_cts = %%s WHERE code = %%s AND description = %%s AND unit_price_cts = %%s""" % self.table,
                                values + list(old_value))
            self.costs[self.index] = values
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_remove_cost(self, event):
        if self.index is None:
            return
        try:
            old_value = self.costs[self.index]
            self.cursor.execute("""DELETE FROM %s WHERE code = %%s AND description = %%s AND unit_price_cts = %%s""" % self.table, list(old_value))
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
            self.cursor.execute("""SELECT id, title, firstname, lastname,
                                          complement, street, zip, city
                                     FROM addresses ORDER BY id""")
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
        for identifier, title, firstname, lastname, complement, street, zip, city in self.addresses:
            self.addresses_list.Append((identifier, title or '', firstname, lastname,
                                        (complement or '').replace('\n', ', '),
                                        (street or '').replace('\n', ', '),
                                        zip, city
                                        ))
        size_key = wx.LIST_AUTOSIZE if self.addresses else wx.LIST_AUTOSIZE_USEHEADER
        for c in range(self.addresses_list.ColumnCount):
            self.addresses_list.SetColumnWidth(c, size_key)
        self.on_deselect_address(None)
        self.Layout()
        self.Fit()

    def on_deselect_address(self, event):
        self.prev_index = self.index
        self.index = None
        self.reset_fields()
        self.add_btn.Show()
        self.change_btn.Hide()
        self.remove_btn.Disable()
        self.Layout()

    def reset_fields(self):
        self.identifier.Value = ''
        self.title.Value = ''
        self.firstname.Value = ''
        self.lastname.Value = ''
        self.complement.Value = ''
        self.street.Value = ''
        self.zip.Value = ''
        self.city.Value = ''

    def parse_fields(self):
        return (self.identifier.Value.strip(),
                self.title.Value.strip() or None,
                self.firstname.Value.strip(),
                self.lastname.Value.strip(),
                self.complement.Value.strip() or None,
                self.street.Value.strip(),
                self.zip.Value.strip(),
                self.city.Value.strip())

    def on_select_address(self, event):
        selected = self.addresses_list.GetFirstSelected()
        self.reset_fields()
        if selected != self.prev_index:
            self.index = selected
            identifier, title, firstname, lastname, complement, street, zip, city = self.addresses[self.index]
            self.identifier.Value = identifier
            self.title.Value = title or ''
            self.firstname.Value = firstname
            self.lastname.Value = lastname
            self.complement.Value = complement or ''
            self.street.Value = street
            self.zip.Value = zip
            self.city.Value = city
            self.add_btn.Hide()
            self.change_btn.Show()
            self.remove_btn.Enable()
            self.Layout()
        else:
            self.addresses_list.Select(selected, False)

    def on_add_address(self, event):
        if self.index is not None:
            return
        fields = self.parse_fields()
        try:
            self.cursor.execute("""INSERT INTO addresses
                                               (id, title, firstname, lastname, complement, street, zip, city)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                                list(fields))
            self.addresses.append(fields)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_change_address(self, event):
        if self.index is None:
            return
        fields = self.parse_fields()
        try:
            key = self.addresses[self.index][0]
            self.cursor.execute("""UPDATE addresses
                                      SET id = %s, title = %s,
                                          firstname = %s, lastname = %s,
                                          complement = %s, street = %s,
                                          zip = %s, city = %s
                                    WHERE id = %s""",
                                list(fields) + [key])
            self.addresses[self.index] = fields
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.populate()

    def on_remove_address(self, event):
        if self.index is None:
            return
        try:
            key = self.addresses[self.index][0]
            self.cursor.execute("""DELETE FROM addresses WHERE id = %s""", [key])
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
                    self.cursor.execute("DELETE FROM bills WHERE id_patient = %s", [id_patient])
                    self.cursor.execute("DELETE FROM consultations WHERE id = %s", [id_patient])
                    self.cursor.execute("DELETE FROM patients WHERE id = %s", [id_patient])
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
        self.delete_consult_btn.Show(self.mode == 'delete')
        self.delete_bill_btn.Show(self.mode == 'delete')
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
            self.cursor.execute("""SELECT consultations.id_consult, date_consult, therapeute, MC, payment_date
                                     FROM consultations
                                     LEFT OUTER JOIN bills ON consultations.id_consult = bills.id_consult
                                    WHERE consultations.id=%s
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
                    self.cursor.execute("DELETE FROM bills WHERE id_consult = %s", [id_consult])
                    self.cursor.execute("DELETE FROM consultations WHERE id_consult=%s", [id_consult])
                    showinfo(windows_title.done, labels_text.cons_sup)
                except:
                    traceback.print_exc()
                    showwarning(windows_title.db_error, errors_text.db_delete)
        self.update_list()

    def on_delete_bill(self, event):
        id_consult = self.get_selected_consult_id()
        if id_consult is not None:
            if askyesno(windows_title.delete, labels_text.sup_def_b):
                try:
                    self.cursor.execute("DELETE FROM bills WHERE id_consult = %s", [id_consult])
                    showinfo(windows_title.done, labels_text.bill_sup)
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
                """<h3 class="unpaid">!!!!! Non-payé !!!!!</h3>""" if consult.bill is not None and consult.bill.payment_date is None else None,
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
            ])
        html.append("</body></html>")
        self.html.SetPage('\n'.join(html), "")


class FixPatientAddressDialog(CancelableMixin, wx.Dialog):
    def __init__(self, parent, patient):
        super().__init__(parent)
        self.patient = patient
        self.street = wx.TextCtrl(self, wx.ID_ANY, patient.street or '')
        self.zip = wx.TextCtrl(self, wx.ID_ANY, patient.zip or '')
        self.city = wx.TextCtrl(self, wx.ID_ANY, patient.city or '')
        self.canton = wx.Choice(self, wx.ID_ANY, choices=CANTONS)
        self.canton.StringSelection = patient.canton or DEFAULT_CANTON
        self.ok_btn = wx.Button(self, wx.ID_ANY, "OK")
        self.cancel_btn = wx.Button(self, wx.ID_ANY, "Annuler")

        if self.patient.adresse is None:
            address = '\n'.join((self.patient.street or '',
                                (self.patient.zip or '') + ' ' + (self.patient.city or ''),
                                self.patient.canton or ''))
        else:
            address = self.patient.adresse
        if not address:
            address = "\nAucune adresse\n"
        sizer = wx.GridBagSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Veuillez préciser l'adresse du patient.\n\nInformation existante:\n%s" % address), (0, 0), (1, 3), wx.CENTER | wx.ALL, 5)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Rue"), (1, 0), (1, 1), wx.LEFT, 5)
        sizer.Add(self.street, (1, 1), (1, 2), wx.EXPAND | wx.RIGHT, 5)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "NPA/Localité"), (2, 0), (1, 1), wx.LEFT, 5)
        sizer.Add(self.zip, (2, 1), (1, 1), wx.EXPAND | wx.RIGHT, 5)
        sizer.Add(self.city, (2, 2), (1, 1), wx.EXPAND | wx.RIGHT, 5)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Canton"), (3, 0), (1, 1), wx.LEFT, 5)
        sizer.Add(self.canton, (3, 1), (1, 2), wx.EXPAND | wx.RIGHT, 5)
        sizer.Add(self.ok_btn, (4, 0), (1, 1), wx.CENTER | wx.ALL, 5)
        sizer.Add(self.cancel_btn, (4, 2), (1, 1), wx.ALIGN_RIGHT | wx.CENTER | wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.SetSizeHints(self)
        self.Layout()
        self.Fit()

        self.Bind(wx.EVT_BUTTON, self.on_validate, self.ok_btn)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.cancel_btn)
        self.Bind(wx.EVT_CLOSE, self.on_close, self)

    def on_validate(self, event):
        if (self.street.Value.strip() and self.zip.Value.strip() and self.city.Value.strip() and self.canton.StringSelection):
            self.EndModal(1)

    def on_close(self, event):
        self.EndModal(0)


class FixPatientSexDialog(CancelableMixin, wx.Dialog):
    def __init__(self, parent, patient):
        super().__init__(parent)
        self.patient = patient
        self.male = wx.RadioButton(self, wx.ID_ANY, SEX_MALE, style=wx.RB_GROUP)
        self.female = wx.RadioButton(self, wx.ID_ANY, SEX_FEMALE)
        self.ok_btn = wx.Button(self, wx.ID_ANY, "OK")
        self.cancel_btn = wx.Button(self, wx.ID_ANY, "Annuler")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, "Veuillez préciser le sexe du patient"), 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        sizer.Add(self.male, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        sizer.Add(self.female, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.ok_btn, 0, 0, 0)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(self.cancel_btn, 0, 0, 0)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.SetSizeHints(self)
        self.Layout()
        self.Fit()

        self.Bind(wx.EVT_BUTTON, self.on_validate, self.ok_btn)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.cancel_btn)
        self.Bind(wx.EVT_CLOSE, self.on_close, self)

    def on_validate(self, event):
        if self.male.Value:
            self.EndModal(1)
        elif self.female.Value:
            self.EndModal(2)

    def on_close(self, event):
        self.EndModal(0)


class FixPatientMixin:
    def fix_patient(self, update_ui=False):
        changed = False
        if self.patient.adresse is not None or not self.patient.canton:
            with FixPatientAddressDialog(self, self.patient) as dlg:
                if dlg.ShowModal():
                    self.patient.street = dlg.street.Value.strip()
                    self.patient.zip = dlg.zip.Value.strip()
                    self.patient.city = dlg.city.Value.strip()
                    self.patient.canton = dlg.canton.StringSelection
                    if update_ui:
                        self.street.Value = self.patient.street
                        self.zip.Value = self.patient.zip
                        self.city.Value = self.patient.city
                        self.canton.StringSelection = self.patient.canton
                    self.patient.adresse = None
                    changed = True
        if self.patient.sex not in SEX_ALL:
            with FixPatientSexDialog(self, self.patient) as dlg:
                result_code = dlg.ShowModal()
                if result_code == 1:
                    self.patient.sex = SEX_MALE
                    if update_ui:
                        self.male.SetValue(True)
                elif result_code == 2:
                    self.patient.sex = SEX_FEMALE
                    if update_ui:
                        self.female.SetValue(True)
                changed = changed or (result_code != 0)
        if changed:
            self.patient.save(self.cursor)


class PatientDialog(FixPatientMixin, DBMixin, CancelableMixin, core.PatientDialog):
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

        if patient.sex in SEX_ALL:
            {SEX_FEMALE: self.female, SEX_MALE: self.male}[patient.sex].SetValue(True)
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
        if patient.adresse is None:
            self.street.Value = patient.street or ''
            self.zip.Value = patient.zip or ''
            self.city.Value = patient.city or ''
            self.canton.StringSelection = patient.canton or DEFAULT_CANTON
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
            for widget in (self.female, self.male, self.firstname, self.lastname, self.therapeute, self.birthdate,
                           self.opening_date, self.fixed_phone, self.mobile_phone, self.professional_phone, self.email,
                           self.street, self.zip, self.city, self.canton, self.important,
                           self.main_doctor, self.other_doctors, self.complementary_insurance,
                           self.profession, self.civil_status, self.sent_by, self.remarks):
                widget.Disable()

        self.Fit()

        if self.patient.id is not None:
            wx.CallLater(FIX_PATIENT_DELAY, lambda: self.fix_patient(True))

    def highlight_missing_fields(self):
        black = wx.Colour(0, 0, 0)
        red = wx.Colour(255, 0, 0)
        patient = self.patient
        if patient.sex is not None:
            self.sex_label.SetForegroundColour(black)
        else:
            self.sex_label.SetForegroundColour(red)
        if patient.nom:
            self.lastname_label.SetForegroundColour(black)
        else:
            self.lastname_label.SetForegroundColour(red)
        if patient.prenom:
            self.firstname_label.SetForegroundColour(black)
        else:
            self.firstname_label.SetForegroundColour(red)
        if patient.therapeute:
            self.therapeute_label.SetForegroundColour(black)
        else:
            self.therapeute_label.SetForegroundColour(red)
        if patient.date_naiss is not None:
            self.birthdate_label.SetForegroundColour(black)
        else:
            self.birthdate_label.SetForegroundColour(red)
        if patient.street:
            self.street_label.SetForegroundColour(black)
        else:
            self.street_label.SetForegroundColour(red)
        if patient.zip and patient.city:
            self.zip_city_label.SetForegroundColour(black)
        else:
            self.zip_city_label.SetForegroundColour(red)
        if patient.canton:
            self.canton_label.SetForegroundColour(black)
        else:
            self.canton_label.SetForegroundColour(red)
        if patient.date_ouverture:
            self.opening_date_label.SetForegroundColour(black)
        else:
            self.opening_date_label.SetForegroundColour(red)

    def is_patient_valid(self):
        self.set_patient_fields()
        patient = self.patient
        if (patient.sex is None
                or patient.date_naiss is None
                or patient.date_ouverture is None
                or not patient.therapeute
                or not patient.nom
                or not patient.prenom
                or not patient.street
                or not patient.zip
                or not patient.city):
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
        patient.sex = SEX_FEMALE if self.female.Value else SEX_MALE if self.male.Value else None
        patient.nom = self.lastname.Value.strip()
        patient.prenom = self.firstname.Value.strip()
        patient.street = self.street.Value.strip()
        patient.zip = self.zip.Value.strip()
        patient.city = self.city.Value.strip()
        patient.canton = self.canton.StringSelection
        patient.ATCD_perso = getattr(patient, 'ATCD_perso', "")
        patient.ATCD_fam = getattr(patient, 'ATCD_fam', "")
        patient.medecin = self.main_doctor.Value.strip()
        patient.autre_medecin = self.other_doctors.Value.strip()
        patient.phone = self.fixed_phone.Value.strip()
        patient.portable = self.mobile_phone.Value.strip()
        patient.profes_phone = self.professional_phone.Value.strip()
        patient.mail = self.email.Value.strip()
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
            self.patient.save(self.cursor)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.on_cancel()


class ConsultationDialog(FixPatientMixin, DBMixin, CancelableMixin, core.ConsultationDialog):
    def __init__(self, parent, id_patient, id_consult=None, readonly=False):
        super().__init__(parent)
        self.patient = Patient.load(self.cursor, id_patient)
        self.consultation = Consultation.load(self.cursor, id_consult) if id_consult is not None else Consultation(id=id_patient)
        self.consultation.patient = self.patient
        self.readonly = readonly

        if self.consultation:
            # Existing consultation, editing or viewing it
            self.save_and_bill_btn.Show(False)
            self.save_and_close_btn.Show(not self.readonly)
            if self.readonly:
                self.view_bill_btn.Show(True)
                self.save_and_edit_bill_btn.Show(False)
            else:
                self.view_bill_btn.Show(False)
                self.save_and_edit_bill_btn.Show(True)
        else:
            # New consultation
            self.save_and_bill_btn.Show(True)
            self.save_and_close_btn.Show(False)
            self.view_bill_btn.Show(False)
            self.save_and_edit_bill_btn.Show(False)
        self.cancel_btn.Show(not self.readonly)
        self.ok_btn.Show(self.readonly)
        self.cursor.execute("SELECT count(*) FROM consultations WHERE id = %s", [self.patient.id])
        count, = self.cursor.fetchone()
        self.show_all_consultations_btn.Show(count > 0)

        consult = self.consultation
        try:
            if consult.therapeute is not None:
                consult.therapeute = consult.therapeute.strip()  # Sanity guard against old data
            self.cursor.execute("""SELECT therapeute, login, entete FROM therapeutes ORDER BY therapeute""")
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            return
        therapeutes = ['']
        for t, login, header in self.cursor:
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

        fixed_therapist = self.readonly or (consult.id_consult is not None and 'MANAGE_CONSULTATIONS' not in wx.GetApp().ACCESS_RIGHTS)

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
        self.diagnostic.Value = consult.A_osteo or ''
        self.treatment.Value = consult.traitement or ''
        self.remarks.Value = consult.divers or ''
        self.consultation_date.Value = consult.date_consult.strftime(DATE_FMT)
        if consult.therapeute:
            self.therapeute.StringSelection = consult.therapeute

        if self.readonly:
            for widget in (self.illness, self.accident, self.reason, self.general_state, self.paraclinic_exams,
                           self.medical_background, self.family_history, self.thorax, self.abdomen, self.physical_exam,
                           self.head_neck, self.upper_limbs, self.lower_limbs, self.other, self.important, self.diagnostic,
                           self.treatment, self.remarks, self.consultation_date, self.therapeute):
                widget.Disable()

        if fixed_therapist:
            self.therapeute.Disable()

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Fit()

        if self.patient.id is not None:
            wx.CallLater(FIX_PATIENT_DELAY, self.fix_patient)

    def set_consultation_fields(self):
        from dateutil import parse_date
        consult = self.consultation
        consult.date_consult = parse_date(self.consultation_date.Value.strip())
        consult.MC = self.reason.Value.strip()
        consult.MC_accident = self.accident.Value
        consult.EG = self.general_state.Value.strip()
        consult.exam_pclin = self.paraclinic_exams.Value.strip()
        consult.exam_phys = self.physical_exam.Value.strip()
        consult.divers = self.remarks.Value.strip()
        consult.APT_thorax = self.thorax.Value.strip()
        consult.APT_abdomen = self.abdomen.Value.strip()
        consult.APT_tete = self.head_neck.Value.strip()
        consult.APT_MS = self.upper_limbs.Value.strip()
        consult.APT_MI = self.lower_limbs.Value.strip()
        consult.APT_system = self.other.Value.strip()
        consult.A_osteo = self.diagnostic.Value.strip()
        consult.traitement = self.treatment.Value.strip()
        consult.therapeute = self.therapeute.StringSelection

    def on_close(self, event):
        if self.readonly or event.EventObject == self.ok_btn or askyesno(windows_title.really_cancel, labels_text.really_cancel):
            self.EndModal(0)

    def on_save(self, event):
        if not self.therapeute.StringSelection:
            showwarning(windows_title.missing_error, errors_text.missing_therapeute)
            return
        self.set_consultation_fields()
        # New consultation => create a new bill or user explicitely requested that with the button
        go_to_bill = not self.consultation or event.EventObject == self.save_and_edit_bill_btn
        try:
            self.consultation.save(self.cursor)

            self.patient.important = self.important.Value.strip()
            self.patient.ATCD_perso = self.medical_background.Value.strip()
            self.patient.ATCD_fam = self.family_history.Value.strip()
            self.patient.save(self.cursor)
            if go_to_bill:
                BillDialog(self, self.consultation.id_consult).ShowModal()
            self.EndModal(0)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)

    def on_view_bill(self, *args):
        if self.consultation.bill is None:
            if askyesno("Aucune facture n'existe pour cette consultation", "Voulez-vous la créer maintenant ?"):
                BillDialog(self, self.consultation.id_consult).ShowModal()
        else:
            BillDialog(self, self.consultation.id_consult, readonly=self.readonly).ShowModal()

    def on_show_all_consultations(self, event):
        AllConsultationsDialog(self, self.patient.id).ShowModal()


class BillDialog(DBMixin, CancelableMixin, bill.BillDialog):
    def __init__(self, parent, id_consult, readonly=False):
        super().__init__(parent)
        self.readonly = readonly
        self.consultation = Consultation.load(self.cursor, id_consult)
        try:
            self.cursor.execute("""SELECT id FROM bills WHERE id_consult = %s""", [id_consult])
            if self.cursor.rowcount != 0:
                bill_id, = self.cursor.fetchone()
                self.bill = Bill.load(self.cursor, bill_id)
            else:
                self.bill = Bill(consultation=self.consultation, patient=self.consultation.patient)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
        try:
            self.cursor.execute("""SELECT code, description, unit_price_cts FROM tarifs ORDER BY code, description""")
            for code, description, unit_price_cts in self.cursor:
                self.tarif_codes[self.tarif_display(code, description)] = (code, description, unit_price_cts)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
        if not self.bill:
            self.initialize_bill()
        else:
            for pos in self.bill.positions:
                # Ensure any code used is available as such but don't overwrite the entries comming from the DB
                tarif_code = (code, description, unit_price_cts) = (pos.tarif_code, pos.tarif_description, pos.price_cts)
                display = self.tarif_display(code, description)
                self.tarif_codes.setdefault(display, tarif_code)
        if not self.readonly:
            self.print_btn.Show(False)
            self.save_and_print_btn.Show(True)
        else:
            self.print_btn.Show(True)
            self.save_and_print_btn.Show(False)

        bill = self.bill
        self.document_id.LabelText = "{} {}".format(bill.id or '', bill.timestamp)
        self.therapeute.LabelText = "{} {} RCC {}".format(bill.author_firstname, bill.author_lastname, bill.author_rcc)
        self.lastname.Value = bill.lastname
        self.firstname.Value = bill.firstname
        self.sex.StringSelection = bill.sex
        self.birthdate.Value = bill.birthdate.strftime(DATE_FMT)
        self.street.Value = bill.street
        self.zip.Value = bill.zip
        self.city.Value = bill.city
        self.canton.StringSelection = bill.canton
        title = gen_title(bill.sex, bill.birthdate)
        self.address.Value = '\n'.join((title, bill.firstname + ' ' + bill.lastname, bill.street, bill.zip + ' ' + bill.city))
        self.patient_id.Value = str(bill.id_patient)
        self.treatment_period.Value = bill.treatment_period
        self.reason.StringSelection = bill.treatment_reason
        self.mandant.Value = bill.mandant
        self.diagnostic.Value = bill.diagnostic
        self.comment.Value = bill.comment
        self.payment_method.StringSelection = bill.payment_method or ''
        for position in bill.positions:
            self.add_position(position, self.readonly)

        if self.readonly:
            for widget in (self.reason, self.treatment_period, self.comment, self.payment_method, self.position_adder_btn):
                widget.Disable()

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.Fit()

    def initialize_bill(self):
        """Initialize a newly created bill object from the consultation"""
        bill = self.bill
        bill.timestamp = datetime.datetime.now()
        therapeute = self.consultation.therapeute or self.patient.therapeute
        try:
            self.cursor.execute("""SELECT entete FROM therapeutes WHERE therapeute = %s""", [therapeute])
            if self.cursor.rowcount != 0:
                entete, = self.cursor.fetchone()
            else:
                entete = ""
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            entete = ""
        bill.author_id = therapeute
        bill.author_firstname = bill.author_lastname = bill.author_rcc = ''
        for i, line in enumerate(entete.splitlines()):
            if i == 0:
                bill.author_firstname, bill.author_lastname = line.strip().split(maxsplit=1)
            elif line.startswith('RCC'):
                bill.author_rcc = line.replace('RCC', '').strip()
        consult = self.consultation
        patient = consult.patient
        bill.type = BILL_TYPE_CONSULTATION
        bill.lastname = patient.nom
        bill.firstname = patient.prenom
        bill.sex = patient.sex if patient.sex in SEX_ALL else ''
        bill.birthdate = patient.date_naiss
        bill.street = patient.street or ''
        bill.zip = patient.zip or ''
        bill.city = patient.city or ''
        bill.canton = patient.canton or ''
        bill.id_patient = patient.id
        bill.id_consult = consult.id_consult
        bill.treatment_period = consult.date_consult.strftime(DATE_FMT)
        bill.treatment_reason = 'Accident' if consult.MC_accident else 'Maladie'
        bill.accident_date = None
        bill.accident_no = None
        bill.mandant = ''
        bill.diagnostic = consult.A_osteo
        bill.comment = ''
        bill.payment_method = ''
        bill.bv_ref = None
        bill.payment_date = None
        bill.status = STATUS_OPENED

    def set_bill_fields(self):
        from dateutil import parse_date
        bill = self.bill
        bill.copy = self.copy.StringSelection == "Oui"
        bill.treatment_reason = self.reason.StringSelection
        bill.treatment_period = self.treatment_period.Value.strip()
        bill.accident_date = parse_date(self.accident_date.Value.strip())
        bill.accident_no = self.accident_no.Value.strip()
        bill.comment = self.comment.Value.strip()
        bill.payment_method = self.payment_method.StringSelection or None
        bill.total_cts = 0
        bill.positions = []
        for position_id, position_date, tarif_code, tarif_description, quantity, price_cts in self.get_positions():
            bill.total_cts += quantity * price_cts
            bill.positions.append(Position(id=position_id,
                                           position_date=position_date,
                                           tarif_code=tarif_code,
                                           tarif_description=tarif_description,
                                           quantity=quantity,
                                           price_cts=price_cts))
        if not custo.PAIEMENT_SORTIE and bill.payment_date is None and bill.payment_method not in ('BVR', 'CdM', 'Dû', 'PVPE'):
            bill.payment_date = datetime.date.today()
            bill.status = STATUS_PAYED
        try:
            if bill.payment_method in ('BVR', 'PVPE'):
                if bill.bv_ref is None:
                    bill.bv_ref = gen_bvr_ref(self.cursor, bill.firstname, bill.lastname, bill.timestamp)
            else:
                bill.bv_ref = None
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)

    def on_print(self, *args):
        self.bill.copy = self.copy.StringSelection == "Oui"
        ts = datetime.datetime.now().strftime('%H')
        filename = normalize_filename(u'%s_%s_%s_%s_%sh.pdf' % (self.bill.lastname,
                                                                self.bill.firstname,
                                                                self.bill.sex,
                                                                self.bill.timestamp.date(),
                                                                ts))
        bills.consultations(filename, [self.bill])
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
        os.system(cmd)
        if self.bill.payment_method == 'BVR' and askyesno(windows_title.print_completed, labels_text.ask_confirm_print_bvr):
            self.bill.status = STATUS_PRINTED
            self.bill.save(self.cursor)

    def on_save_and_print(self, event):
        if (self.payment_method.StringSelection or None) is None:
            showwarning(windows_title.missing_error, errors_text.missing_payment_info)
            return
        if not self.get_positions():
            showwarning(windows_title.missing_error, errors_text.missing_positions)
            return
        if self.bill:
            self.save_edited_bill()
        else:
            self.save_new_bill()

    def save_new_bill(self):
        self.set_bill_fields()
        try:
            self.bill.save(self.cursor)
            for position in self.bill.positions:
                position.id_bill = self.bill.id
                position.save(self.cursor)
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_insert)
        else:
            self.on_print()
            self.EndModal(0)

    def save_edited_bill(self):
        existing = {p.id for p in self.bill.positions}
        edited = {pos[0] for pos in self.get_positions()}
        for removed_id in existing.difference(edited):
            self.cursor.execute("""DELETE FROM positions WHERE id = %s""", [removed_id])
        self.save_new_bill()

    def on_close(self, event):
        if self.readonly or event.EventObject == self.save_and_print_btn or askyesno(windows_title.really_cancel, labels_text.bill_really_cancel):
            self.EndModal(0)


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
