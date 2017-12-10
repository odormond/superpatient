#! /usr/bin/env python3
# coding:UTF-8

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
import datetime
import traceback
import calendar
import mailcap

#sys.path.insert(0, os.path.dirname(__file__))

import wx

from superpatient import BaseApp, DBMixin, HelpMenuMixin
from superpatient import bills, normalize_filename
import superpatient.customization as custo
from superpatient.customization import windows_title, errors_text, labels_text, menus_text
from superpatient.models import Consultation, PAYMENT_METHODS, OLD_PAYMENT_METHODS, BILL_STATUSES, STATUS_PRINTED, STATUS_SENT, STATUS_PAYED, STATUS_ABANDONED
from superpatient.ui.common import showwarning, showerror, DatePickerDialog
from superpatient.ui import accounting


def sum_found(positions):
    return sum(p[8] for p in positions) / 100.0


def sum_notfound(positions):
    return sum(p[3] for p in positions) / 100.0


class AccountingFrame(DBMixin, HelpMenuMixin, accounting.MainFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.cursor.execute("SELECT therapeute FROM therapeutes ORDER BY therapeute")
            therapeutes = ['Tous'] + [t for t, in self.cursor]
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
            sys.exit(1)
        self.therapeute.SetItems(therapeutes)
        self.payment_method.SetItems([''] + PAYMENT_METHODS + OLD_PAYMENT_METHODS)
        self.bill_status.SetItems(BILL_STATUSES)
        today = datetime.date.today()
        month_end = datetime.date(today.year, today.month, 1) - datetime.timedelta(days=1)
        last_month = datetime.date(month_end.year, month_end.month, 1)
        self.filter_start.Value = str(last_month)
        self.update_list()

    def update_list(self):
        from dateutil import parse_ISO
        therapeute = self.therapeute.StringSelection
        payment_method = self.payment_method.StringSelection
        filter_start = parse_ISO(self.filter_start.Value.strip())
        filter_end = parse_ISO(self.filter_end.Value.strip())
        bill_status = self.bill_status.StringSelection
        filter_firstname = self.filter_firstname.Value.strip()
        filter_lastname = self.filter_lastname.Value.strip()
        conditions = ['TRUE']
        args = []
        manual_bills_conditions = ['TRUE']
        manual_bills_args = []
        if therapeute != 'Tous':
            conditions.append('consultations.therapeute = %s')
            args.append(therapeute)
            manual_bills_conditions.append('therapeute = %s')
            manual_bills_args.append(therapeute)
        if payment_method != '':
            conditions.append('paye_par = %s')
            args.append(payment_method)
        if filter_start:
            conditions.append('date_consult >= %s')
            args.append(filter_start)
            manual_bills_conditions.append('date >= %s')
            manual_bills_args.append(filter_start)
        if filter_end:
            conditions.append('date_consult < %s')
            args.append(filter_end + datetime.timedelta(days=1))
            manual_bills_conditions.append('date < %s')
            manual_bills_args.append(filter_end + datetime.timedelta(days=1))
        if bill_status != 'Tous':
            bill_status = bill_status[0]
            if bill_status == u'O':
                conditions.append("consultations.status in ('O', 'I', 'E')")
                manual_bills_conditions.append("status in ('O', 'I', 'E')")
            else:
                conditions.append('consultations.status = %s')
                args.append(bill_status)
                manual_bills_conditions.append('status = %s')
                manual_bills_args.append(bill_status)
        if filter_firstname:
            conditions.append('prenom LIKE %s')
            args.append(filter_firstname.replace('*', '%'))
        if filter_lastname:
            conditions.append('nom LIKE %s')
            args.append(filter_lastname.replace('*', '%'))
            manual_bills_conditions.append('destinataire LIKE %s')
            manual_bills_args.append(filter_lastname.replace('*', '%'))
        self.payments.DeleteAllItems()
        self.payments_count.Value = ''
        self.total_consultations.Value = ''
        self.total_majorations.Value = ''
        self.total_admin_costs.Value = ''
        self.total_reminder_costs.Value = ''
        self.total.Value = ''
        self.data = []
        count = 0
        total_consultations = 0
        total_majorations = 0
        total_admin_costs = 0
        total_reminder_costs = 0
        try:
            self.cursor.execute("""SELECT consultations.id_consult, date_consult, paye_le, prix_cts, majoration_cts, frais_admin_cts, sex, nom, prenom, COALESCE(CAST(SUM(rappel_cts) AS SIGNED), 0), count(date_rappel), consultations.status
                                    FROM consultations INNER JOIN patients ON consultations.id = patients.id
                                    LEFT OUTER JOIN rappels ON consultations.id_consult = rappels.id_consult
                                   WHERE %s
                                   GROUP BY consultations.id_consult, date_consult, paye_le, prix_cts, majoration_cts, frais_admin_cts, sex, nom, prenom
                                   ORDER BY date_consult""" % ' AND '.join(conditions), args)
            data = list(self.cursor)
            if payment_method in ('', 'BVR'):
                self.cursor.execute("""SELECT -id, date, paye_le, montant_cts, 0, 0, '-', identifiant, '', 0, 0, status
                                         FROM factures_manuelles
                                        WHERE %s
                                        ORDER BY date""" % ' AND '.join(manual_bills_conditions), manual_bills_args)
                data += list(self.cursor)
            aux_cursor = self.connection.cursor()
            for id_consult, date_consult, paye_le, prix_cts, majoration_cts, frais_admin_cts, sex, nom, prenom, rappel_cts, rappel_cnt, status in data:
                if status not in (STATUS_ABANDONED, STATUS_PAYED) and rappel_cnt != 0:
                    aux_cursor.execute("""SELECT status FROM rappels WHERE id_consult = %s ORDER BY date_rappel DESC LIMIT 1""", [id_consult])
                    status, = aux_cursor.fetchone()
                index = self.payments.Append((status, sex, nom, prenom, date_consult, '%6.2f' % ((prix_cts+majoration_cts+frais_admin_cts+rappel_cts)/100.), paye_le or ''))
                if rappel_cnt == 1:
                    self.payments.GetItem(index).SetTextColour(wx.Colour(64, 0, 0))
                elif rappel_cnt > 1:
                    self.payments.GetItem(index).SetTextColour(wx.Colour(128, 0, 0))
                self.data.append(id_consult)
                total_consultations += prix_cts
                total_majorations += majoration_cts
                total_admin_costs += frais_admin_cts
                total_reminder_costs += rappel_cts
                count += 1
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
        for c in range(self.payments.ColumnCount):
            self.payments.SetColumnWidth(c, wx.LIST_AUTOSIZE)
        self.payments_count.Value = str(count)
        self.total_consultations.Value = '%0.2f CHF' % (total_consultations/100.)
        self.total_majorations.Value = '%0.2f CHF' % (total_majorations/100.)
        self.total_admin_costs.Value = '%0.2f CHF' % (total_admin_costs/100.)
        self.total_reminder_costs.Value = '%0.2f CHF' % (total_reminder_costs/100.)
        self.total.Value = '%0.2f CHF' % ((total_consultations + total_majorations + total_admin_costs + total_reminder_costs)/100.)

    def read_payments(self, filename):
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
                        zeros, line = line[:9], line[9:]  # noqa
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
                        reserved, line = line[:13], line[13:].strip()  # noqa
                        assert total_line is None, "Multiple total line found"
                        total_line = (transaction_type, bvr_client_no, ref_no, total_cts, count, date, postal_fees_cts, hw_postal_fees_cts)
                    assert line in ('', '\n'), "Garbage at end of line %d" % line_no
                assert total_line is not None and len(records) == count, "Records count does not match total line indication"
            except Exception as e:
                print(e)
                showerror("Fichier corrompu", "Une erreur s'est produite lors de la lecture du fichier de payement.\n%r" % e.args)
                return None
        return records

    def on_import_payments(self, event):
        with wx.FileDialog(self, menus_text.import_bvr, wildcard="Relevers de payement (*.v11)|*.v11", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            filename = dlg.GetPath()
        records = self.read_payments(filename)
        if records is None:
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
            self.cursor.execute("SELECT id_consult, prix_cts, majoration_cts, frais_admin_cts, paye_le FROM consultations WHERE bv_ref = %s", [ref_no])
            if self.cursor.rowcount != 0:
                id_consult, prix_cts, majoration_cts, frais_admin_cts, paye_le = self.cursor.fetchone()
                self.cursor.execute("SELECT rappel_cts FROM rappels WHERE id_consult = %s ORDER BY date_rappel", [id_consult])
                a_payer_cts = prix_cts + majoration_cts + frais_admin_cts
                for r in [0] + [r for r, in self.cursor]:
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
                self.cursor.execute("SELECT id, montant_cts, paye_le FROM factures_manuelles WHERE bv_ref = %s", [ref_no])
                if self.cursor.rowcount != 0:
                    id, montant_cts, paye_le = self.cursor.fetchone()
                    id_consult = -id
                    prix_cts, majoration_cts, frais_admin_cts = montant_cts, 0, 0
                    if montant_cts != amount_cts:
                        l = ko
                    elif paye_le is None:
                        l = ok
                    else:
                        l = doubled
            if l is not None:
                l.append((id_consult, prix_cts, majoration_cts, frais_admin_cts, rappel_cts, transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts))
            else:
                not_found.append((transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts))

        ImportDialog(self, ok, ko, doubled, not_found, ignored).ShowModal()
        self.update_list()

    def on_manage_reminders(self, event):
        RemindersManagementDialog(self).ShowModal()
        self.update_list()

    def on_show_stats(self, event):
        StatisticsDialog(self).ShowModal()

    def on_popup_start_date(self, event):
        dlg = DatePickerDialog(event.EventObject, date=self.filter_start.Value)
        dlg.CenterOnParent()
        dlg.ShowModal()
        self.filter_start.Value = dlg.Value.strftime('%Y-%m-%d')
        self.filter_end.Value = self.filter_start.Value
        self.update_list()

    def on_popup_end_date(self, event):
        dlg = DatePickerDialog(event.EventObject, date=self.filter_end.Value)
        dlg.CenterOnParent()
        dlg.ShowModal()
        self.filter_end.Value = dlg.Value.strftime('%Y-%m-%d')
        self.update_list()

    def on_search(self, event):
        self.update_list()

    def on_mark_paid(self, event):
        from dateutil import parse_ISO
        payment_date = parse_ISO(self.payment_date.Value.strip())
        consult_ids = [id for i, id in enumerate(self.data) if self.payments.IsSelected(i) and id >= 0]
        manual_bills_ids = [-id for i, id in enumerate(self.data) if self.payments.IsSelected(i) and id < 0]
        try:
            if len(consult_ids) > 1:
                self.cursor.execute("""UPDATE consultations SET paye_le = %s, status = 'P'
                                        WHERE paye_le IS NULL AND id_consult IN %s""",
                                    [payment_date, tuple(consult_ids)])
            elif len(consult_ids) == 1:
                self.cursor.execute("""UPDATE consultations SET paye_le = %s, status = 'P' WHERE id_consult = %s""", [payment_date, consult_ids[0]])
            if len(manual_bills_ids) > 1:
                self.cursor.execute("""UPDATE factures_manuelles SET paye_le = %s, status = 'P'
                                        WHERE paye_le IS NULL AND id IN %s""",
                                    [payment_date, tuple(manual_bills_ids)])
            elif len(manual_bills_ids) == 1:
                self.cursor.execute("""UPDATE factures_manuelles SET paye_le = %s, status = 'P' WHERE id = %s""", [payment_date, manual_bills_ids[0]])
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.update_list()

    def on_print_again(self, event):
        consult_ids = [id for i, id in enumerate(self.data) if self.payments.IsSelected(i) and id >= 0]
        if consult_ids:
            filename_consult = normalize_filename(datetime.datetime.now().strftime('consultations_%F_%Hh%Mm%Ss.pdf'))
            bills.consultations(filename_consult, self.cursor, [Consultation.load(self.cursor, id_consult) for id_consult in consult_ids])
            cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_consult)
            os.system(cmd + '&')
        manual_bills_ids = [-id for i, id in enumerate(self.data) if self.payments.IsSelected(i) and id < 0]
        if manual_bills_ids:
            filename_manual = normalize_filename(datetime.datetime.now().strftime('fact_manuelles_%F_%Hh%Mm%Ss.pdf'))
            self.cursor.execute("""SELECT therapeute, destinataire, motif, montant_cts, remarque, bv_ref
                                     FROM factures_manuelles
                                    WHERE id in %s""",
                                [manual_bills_ids])
            factures = []
            cursor2 = self.connection.cursor()
            for therapeute, destinataire, motif, montant_cts, remarque, bv_ref in self.cursor:
                cursor2.execute("SELECT entete FROM therapeutes WHERE therapeute = %s", [therapeute])
                entete, = cursor2.fetchone()
                therapeuteAddress = entete + u'\n\n' + labels_text.adresse_pog
                factures.append((therapeuteAddress, destinataire, motif, float(montant_cts)/100, remarque, bv_ref))
            bills.manuals(filename_manual, factures)
            cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_manual)
            os.system(cmd + '&')

    def on_mark_printed(self, event):
        self.mark_status(STATUS_PRINTED)

    def on_mark_sent(self, event):
        self.mark_status(STATUS_SENT)

    def on_mark_abandoned(self, event):
        self.mark_status(STATUS_ABANDONED)

    def mark_status(self, status):
        consult_ids = [id for i, id in enumerate(self.data) if self.payments.IsSelected(i) and id >= 0]
        manual_bills_ids = [-id for i, id in enumerate(self.data) if self.payments.IsSelected(i) and id < 0]
        try:
            for consult_id in consult_ids:
                self.cursor.execute("""SELECT date_rappel FROM rappels WHERE id_consult = %s ORDER BY date_rappel DESC LIMIT 1""", [consult_id])
                last_rappel, = self.cursor.fetchone() or (None,)
                self.cursor.execute("""UPDATE consultations SET status = %s WHERE status != 'P' AND id_consult = %s""", [status, consult_id])
                if last_rappel is not None:
                    self.cursor.execute("""UPDATE rappels SET status = %s WHERE status != 'P' AND id_consult = %s AND date_rappel = %s""", [status, consult_id, last_rappel])
            if len(manual_bills_ids) > 1:
                self.cursor.execute("""UPDATE factures_manuelles SET status = %s
                                        WHERE status != 'P' AND id IN %s""",
                                    [status, tuple(manual_bills_ids)])
            elif len(manual_bills_ids) == 1:
                self.cursor.execute("""UPDATE factures_manuelles SET status = %s WHERE status != 'P' AND id = %s""", [status, manual_bills_ids[0]])
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)
        self.update_list()


class RemindersManagementDialog(DBMixin, accounting.RemindersManagementDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.upto.Value = str(datetime.date.today() - datetime.timedelta(days=40))
        self.on_update_list()

    def on_update_list(self, *args):
        print("update_list")
        from dateutil import parse_ISO
        upto = parse_ISO(self.upto.Value.strip())
        self.reminders.DeleteAllItems()
        self.total.Value = ''
        self.data = []
        self.is_updating_list = True
        try:
            self.cursor.execute("""SELECT consultations.id_consult, date_consult, prix_cts, majoration_cts, frais_admin_cts, sex, nom, prenom, COALESCE(CAST(SUM(rappel_cts) AS SIGNED), 0), count(date_rappel), max(date_rappel)
                                     FROM consultations INNER JOIN patients ON consultations.id = patients.id
                                     LEFT OUTER JOIN rappels ON consultations.id_consult = rappels.id_consult
                                    WHERE paye_le IS NULL AND bv_ref IS NOT NULL AND bv_ref != '' AND date_consult <= %s AND consultations.status NOT IN ('P', 'A')
                                    GROUP BY consultations.id_consult, date_consult, prix_cts, majoration_cts, sex, nom, prenom
                                    ORDER BY date_consult""", [upto])
            for id_consult, date_consult, prix_cts, majoration_cts, frais_admin_cts, sex, nom, prenom, rappel_cts, rappel_cnt, rappel_last in self.cursor:
                if rappel_last is None:
                    rappel_last = ''
                elif rappel_last > upto:
                    continue
                index = self.reminders.Append((sex, nom, prenom, date_consult, '%0.2f' % ((prix_cts+majoration_cts+frais_admin_cts+rappel_cts)/100.), rappel_last, rappel_cnt))
                self.reminders.Select(index)
                if rappel_cnt == 1:
                    self.reminders.SetItemTextColour(index, wx.Colour(64, 0, 0))
                    self.reminders.SetItemFont(index, self.GetFont().Italic())
                elif rappel_cnt > 1:
                    self.reminders.SetItemTextColour(index, wx.Colour(128, 0, 0))
                    self.reminders.SetItemFont(index, self.GetFont().Bold())
                self.data.append((id_consult, (prix_cts+majoration_cts+frais_admin_cts+rappel_cts), sex, nom, prenom, date_consult, rappel_cnt, prix_cts, majoration_cts, frais_admin_cts, rappel_cts))
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)
        self.is_updating_list = False
        for c in range(self.reminders.ColumnCount):
            self.reminders.SetColumnWidth(c, wx.LIST_AUTOSIZE)
            self.reminders.SetColumnWidth(c, self.reminders.GetColumnWidth(c) + 5)  # Workaround for font style not being taken into account
        self.on_update_selection()

    def on_update_selection(self, *args):
        if self.is_updating_list:
            return  # Skip stupidly generated events while populating the data
        total = 0
        item = -1
        while True:
            item = self.reminders.GetNextSelected(item)
            if item == -1:
                break
            total += self.data[item][1]
        self.total.Value = '%0.2f CHF' % (total/100.)

    def on_popup_date(self, event):
        dlg = DatePickerDialog(event.EventObject, date=self.upto.Value)
        dlg.CenterOnParent()
        dlg.ShowModal()
        self.upto.Value = dlg.Value.strftime('%Y-%m-%d')
        self.on_update_list()

    def on_generate(self, event):
        filename = normalize_filename(datetime.datetime.now().strftime('rappels_%F_%Hh%Mm%Ss.pdf'))
        today = datetime.date.today()
        consultations = []
        item = -1
        while True:
            item = self.reminders.GetNextSelected(item)
            if item == -1:
                break
            id_consult = self.data[item][0]
            self.cursor.execute("""INSERT INTO rappels (id_consult, rappel_cts, date_rappel) VALUES (%s, %s, %s)""",
                                [id_consult, custo.MONTANT_RAPPEL_CTS, today])

            consultations.append(Consultation.load(self.cursor, id_consult))
        if consultations:
            bills.consultations(filename, self.cursor, consultations)
            cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
            os.system(cmd)
        self.Close()

    def on_cancel(self, event):
        self.Close()


class StatisticsDialog(DBMixin, accounting.StatisticsDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.cursor.execute("SELECT DISTINCT COALESCE(consultations.therapeute, patients.therapeute) AS therapeute FROM consultations RIGHT OUTER JOIN patients ON consultations.id = patients.id ORDER BY therapeute")
        self.therapeutes = [t for t, in self.cursor]
        self.stats.AppendRows(len(self.therapeutes) + 1)
        for r, therapeute in enumerate(self.therapeutes + ['Total']):
            self.stats.SetRowLabelValue(r, therapeute)
        self.cursor.execute("SELECT DISTINCT YEAR(date_consult) AS year FROM consultations ORDER BY year")
        self.years = [y for y, in self.cursor]
        self.months = [u'tout', u'janvier', u'février', u'mars', u'avril', u'mai', u'juin', u'juillet', u'août', u'septembre', u'octobre', u'novembre', u'décembre']
        self.year.SetItems(['tout'] + [str(y) for y in self.years])
        self.month.SetItems(self.months)

        self.update_display()

    def update_display(self, event=None):
        year = self.year.StringSelection
        month = self.month.StringSelection
        if year != 'tout':
            year = int(year)
        self.month.Enable(year != 'tout')
        self.cleanup()
        if year != 'tout' and month != 'tout':
            month = self.months.index(month)
            self.setup_month_view(year, month)
        elif year != 'tout':
            self.setup_year_view(year)
        else:
            self.setup_full_view()

    def cleanup(self):
        if self.stats.NumberCols:
            self.stats.DeleteCols(numCols=self.stats.NumberCols)

    def setup_full_view(self):
        sequence = [[year] for year in self.years]
        sql = """SELECT COALESCE(consultations.therapeute, patients.therapeute) AS therapeute, count(*), CAST(SUM(prix_cts) AS SIGNED), CAST(SUM(majoration_cts) AS SIGNED), CAST(SUM(frais_admin_cts) AS SIGNED)
                   FROM consultations INNER JOIN patients ON consultations.id = patients.id
                  WHERE YEAR(date_consult) = %s
                  GROUP BY therapeute
                  ORDER BY therapeute"""

        def label_fn(args):
            return str(args[0])
        self.setup_view(sequence, sql, label_fn)

    def setup_year_view(self, year):
        sequence = [[year, month] for month in range(1, 13)]
        sql = """SELECT COALESCE(consultations.therapeute, patients.therapeute) AS therapeute, count(*), CAST(SUM(prix_cts) AS SIGNED), CAST(SUM(majoration_cts) AS SIGNED), CAST(SUM(frais_admin_cts) AS SIGNED)
                   FROM consultations INNER JOIN patients ON consultations.id = patients.id
                  WHERE YEAR(date_consult) = %s AND MONTH(date_consult) = %s
                  GROUP BY therapeute
                  ORDER BY therapeute"""

        def label_fn(args):
            return self.months[args[1]]
        self.setup_view(sequence, sql, label_fn)

    def setup_month_view(self, year, month):
        sequence = [[year, month, day] for day in range(1, calendar.mdays[month]+1)]
        sql = """SELECT COALESCE(consultations.therapeute, patients.therapeute) AS therapeute,
                        count(*),
                        CAST(SUM(prix_cts) AS SIGNED),
                        CAST(SUM(majoration_cts) AS SIGNED),
                        CAST(SUM(frais_admin_cts) AS SIGNED)
                   FROM consultations INNER JOIN patients ON consultations.id = patients.id
                  WHERE YEAR(date_consult) = %s AND MONTH(date_consult) = %s AND DAY(date_consult) = %s
                  GROUP BY therapeute
                  ORDER BY therapeute"""

        def label_fn(args):
            return str(args[2])
        self.setup_view(sequence, sql, label_fn)

    def setup_view(self, sequence, sql, label_fn):
        totals = {}
        grand_total = 0
        mode = self.stats_type.StringSelection
        format = '%d' if mode == '# Consultations' else '%0.2f'
        self.stats.BeginBatch()
        self.stats.AppendCols(len(sequence) + 1)
        self.stats.SetColLabelValue(len(sequence), 'Total')
        self.stats.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        for c, args in enumerate(sequence):
            self.stats.SetColLabelValue(c, label_fn(args))
            self.cursor.execute(sql, args)
            col_total = 0
            for therapeute, count, prix_cts, majoration_cts, frais_admin_cts in self.cursor:
                if mode == '# Consultations':
                    value = count
                elif mode == 'CHF Consultations':
                    value = prix_cts/100.
                elif mode == 'CHF Majorations':
                    value = majoration_cts/100.
                elif mode == 'CHF Frais Admin':
                    value = frais_admin_cts/100.
                else:
                    value = (prix_cts + majoration_cts + frais_admin_cts)/100.
                line = self.therapeutes.index(therapeute)
                #bg = 'white' if line % 2 == 0 else '#eee'
                self.stats.SetCellValue(line, c, format % value)
                totals[therapeute] = totals.get(therapeute, 0) + value
                col_total += value
                grand_total += value
            self.stats.SetCellValue(len(self.therapeutes), c, format % col_total)
        for therapeute, total in totals.items():
            line = self.therapeutes.index(therapeute)
            self.stats.SetCellValue(line, len(sequence), format % total)
        self.stats.SetCellValue(len(self.therapeutes), len(sequence), format % grand_total)
        self.stats.EndBatch()
        self.stats.AutoSize()
        self.Layout()
        self.Fit()
        self.CenterOnScreen()

    def on_done(self, event):
        self.Close()


class ImportDialog(DBMixin, accounting.ImportDialog):
    def __init__(self, parent, ok, ko, doubled, not_found, ignored):
        super().__init__(parent)
        self.ok = ok
        self.ko = ko
        self.doubled = doubled
        self.not_found = not_found
        self.ignored = ignored

        self.volume_in_order.LabelText = str(len(self.ok))
        self.revenue_in_order.LabelText = '%0.2f CHF' % sum_found(self.ok)
        self.details_in_order.Show(bool(self.ok))

        self.volume_wrong_amount.LabelText = str(len(self.ko))
        self.revenue_wrong_amount.Labeltext = '%0.2f CHF' % sum_found(self.ko)
        self.details_wrong_amount.Show(bool(self.ko))

        self.volume_already_paid.LabelText = str(len(self.doubled))
        self.revenue_already_paid.Labeltext = '%0.2f CHF' % sum_found(self.doubled)
        self.details_already_paid.Show(bool(self.doubled))

        self.volume_not_found.LabelText = str(len(self.not_found))
        self.revenue_not_found.Labeltext = '%0.2f CHF' % sum_notfound(self.not_found)
        self.details_not_found.Show(bool(self.not_found))

        self.volume_ignored.LabelText = str(len(self.ignored))
        self.details_ignored.Show(bool(self.ignored))

    def on_details_in_order(self, event):
        DetailsDialog(self, self.ok).ShowModal()

    def on_details_wrong_amount(self, event):
        DetailsDialog(self, self.ko).ShowModal()

    def on_details_already_paid(self, event):
        DetailsDialog(self, self.doubled).ShowModal()

    def on_details_not_found(self, event):
        DetailsDialog(self, self.not_found).ShowModal()

    def on_details_ignored(self, event):
        DetailsDialog(self, self.ignored).ShowModal()

    def on_validate_import(self, event):
        try:
            for payment in self.ok:
                id_consult = payment[0]
                rappel_cts = payment[4]
                credit_date = payment[11]
                if id_consult >= 0:
                    self.cursor.execute("UPDATE consultations SET paye_le = %s WHERE id_consult = %s", [credit_date, id_consult])
                    if rappel_cts > 0:
                        self.cursor.execute("SELECT rappel_cts, date_rappel FROM rappels WHERE id_consult = %s ORDER BY date_rappel", [id_consult])
                        for fact_rappel_cts, date_rappel in list(self.cursor):
                            if rappel_cts >= fact_rappel_cts:
                                self.cursor.execute("UPDATE rappels SET status = 'P' WHERE id_consult = %s AND date_rappel = %s", [id_consult, date_rappel])
                            else:
                                break
                            rappel_cts -= fact_rappel_cts
                else:
                    self.cursor.execute("UPDATE factures_manuelles SET paye_le = %s WHERE id = %s", [credit_date, -id_consult])
            self.Close()
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)

    def on_cancel_import(self, event):
        self.Close()


class DetailsDialog(accounting.DetailsDialog):
    transaction_types = {
        '002': 'Crédit B préimp',
        '005': 'Extourne B préimp',
        '008': 'Correction B préimp',
        '012': 'Crédit P préimp',
        '015': 'Extourne P préimp',
        '018': 'Correction P préimp',
        '102': 'Crédit B',
        '105': 'Extourne B',
        '108': 'Correction B',
        '112': 'Crédit P',
        '115': 'Extourne P',
        '118': 'Correction P',
    }

    def __init__(self, parent, positions):
        super().__init__(parent)
        self.positions = positions

        if len(self.positions[0]) == 16:
            self.populate_found()
        else:
            self.populate_notfound()
        for c in range(self.details.ColumnCount):
            self.details.SetColumnWidth(c, wx.LIST_AUTOSIZE)
        self.details.SetInitialSize(self.details.GetViewRect()[2:])
        self.Layout()
        self.Fit()

    def format_date(self, date):
        if date is None:
            return ''
        elif isinstance(date, str):
            return '20' + date[:2] + '-' + date[2:4] + '-' + date[4:]
        return str(date)

    def format_ref(self, ref):
        ref = list(ref)
        for pos in (2, 8, 14, 20, 26):
            ref.insert(pos, ' ')
        return ''.join(ref)

    def populate_found(self):
        self.details.DeleteAllItems()
        self.details.DeleteAllColumns()
        columns = ["Sex", "Nom", "Prénom", "Naissance", "Consultation du", "Facturé CHF", "Payé CHF", "Rappel", "Crédité le", "Comtabilisé le", "Numéro de référence"]
        for column in columns:
            self.details.AppendColumn(column, format=wx.LIST_FORMAT_LEFT, width=-1)
        data = []
        for id_consult, prix_cts, majoration_cts, frais_admin_cts, rappel_cts, transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts in self.positions:
            if id_consult >= 0:
                self.cursor.execute("""SELECT sex, nom, prenom, date_naiss, date_consult, paye_le, COALESCE(CAST(SUM(rappel_cts) AS SIGNED), 0)
                                         FROM consultations INNER JOIN patients ON patients.id = consultations.id
                                                            LEFT OUTER JOIN rappels ON consultations.id_consult = rappels.id_consult
                                        WHERE consultations.id_consult = %s
                                        GROUP BY sex, nom, prenom, date_naiss, date_consult, paye_le""",
                                    [id_consult])
            else:
                self.cursor.execute("SELECT '-', identifiant, '', '', date, paye_le, 0 FROM factures_manuelles WHERE id = %s", [-id_consult])
            sex, nom, prenom, date_naiss, date_consult, paye_le, fact_rappel_cts = self.cursor.fetchone()
            fact_rappel_cts = int(fact_rappel_cts)
            if fact_rappel_cts == 0:
                rappel = ''
            else:
                rappel = '%3.0f%%' % (rappel_cts * 100 / fact_rappel_cts)
            data.append((sex, nom, prenom, date_naiss, date_consult, '%0.2f' % ((prix_cts+majoration_cts+frais_admin_cts+fact_rappel_cts)/100.), '%0.2f' % (amount_cts/100.), rappel, self.format_date(credit_date), self.format_date(paye_le), self.format_ref(ref_no)))

        for values in data:
            self.details.Append(values)

    def populate_notfound(self):
        self.details.DeleteAllItems()
        self.details.DeleteAllColumns()
        columns = ["Type de transaction", "Payé CHF", "Crédité le", "Numéro de référence"]
        for column in columns:
            self.details.AppendColumn(column, format=wx.LIST_FORMAT_LEFT, width=-1)
        data = []
        for transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts in self.positions:
            data.append((self.transaction_types.get(transaction_type, transaction_type), '%0.2f' % (amount_cts/100.), self.format_date(credit_date), self.format_ref(ref_no)))

        for values in data:
            self.details.Append(values)


class AccountingApp(BaseApp):
    MainFrameClass = AccountingFrame


if __name__ == '__main__':
    AccountingApp().MainLoop()
