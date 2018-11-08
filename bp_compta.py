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

import calendar
import datetime
import mailcap
import logging
from operator import attrgetter
import os
import sys

import wx

from superpatient import BaseApp, DBMixin, CancelableMixin, HelpMenuMixin
from superpatient import bills as pdf_bills, normalize_filename
import superpatient.customization as custo
from superpatient.models import Bill, PAYMENT_METHODS, OLD_PAYMENT_METHODS, BILL_STATUSES, STATUS_PRINTED, STATUS_SENT, STATUS_PAYED, STATUS_ABANDONED, BILL_TYPE_CONSULTATION, BILL_TYPE_MANUAL
from superpatient.ui.common import show_db_warning, show_error, DatePickerDialog
from superpatient.ui import accounting

logger = logging.getLogger(__name__)


def sum_found(positions):
    return sum(p[6] for p in positions) / 100.0


def sum_notfound(positions):
    return sum(p[3] for p in positions) / 100.0


class AccountingFrame(DBMixin, HelpMenuMixin, accounting.MainFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.cursor.execute("SELECT therapeute FROM therapeutes ORDER BY therapeute")
            therapeutes = ['Tous'] + [t for t, in self.cursor]
        except:
            show_db_warning(logger, 'read')
            sys.exit(1)
        try:
            self.cursor.execute("SELECT DISTINCT site FROM bills ORDER BY site")
            sites = ['Tous'] + [s for s, in self.cursor]
        except:
            show_db_warning(logger, 'read')
            sys.exit(1)
        self.therapeute.SetItems(therapeutes)
        self.therapeute.StringSelection = therapeutes[0]
        self.payment_method.SetItems([''] + PAYMENT_METHODS + OLD_PAYMENT_METHODS)
        self.payment_method.StringSelection = ''
        self.bill_status.SetItems(BILL_STATUSES)
        self.bill_status.StringSelection = BILL_STATUSES[0]
        self.site.SetItems(sites)
        self.site.StringSelection = sites[0]
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
        site = self.site.StringSelection
        filter_firstname = self.filter_firstname.Value.strip()
        filter_lastname = self.filter_lastname.Value.strip()
        where = {}
        if therapeute != 'Tous':
            where['author_id'] = therapeute
        if payment_method != '':
            where['payment_method'] = payment_method
        if filter_start:
            where['timestamp__ge'] = filter_start
        if filter_end:
            where['timestamp__lt'] = filter_end + datetime.timedelta(days=1)
        if bill_status != 'Tous':
            bill_status = bill_status[0]
            if bill_status == 'O':
                where['status__in'] = ('O', 'I', 'E')
            else:
                where['status'] = bill_status
        if site != 'Tous':
            where['site'] = site
        if filter_firstname:
            where['firstname__like'] = filter_firstname.replace('*', '%')
        if filter_lastname:
            where['lastname__like'] = filter_lastname.replace('*', '%')
        self.payments.DeleteAllItems()
        self.payments_count.Value = ''
        self.total_bills.Value = ''
        self.total_reminder_costs.Value = ''
        self.total.Value = ''
        self.data = []
        count = 0
        total_bills = 0
        total_reminder_costs = 0
        try:
            for bill in Bill.yield_all(self.cursor, where=where, order='timestamp'):
                if bill.status not in (STATUS_ABANDONED, STATUS_PAYED) and bill.reminders:
                    status = sorted(bill.reminders, key=attrgetter('reminder_date'))[-1].status
                else:
                    status = bill.status
                index = self.payments.Append((status, bill.sex, bill.lastname, bill.firstname, bill.site, bill.timestamp.date(), '%6.2f' % (bill.total_cts/100), bill.payment_date or ''))
                if len(bill.reminders) == 1:
                    self.payments.GetItem(index).SetTextColour(wx.Colour(64, 0, 0))
                elif len(bill.reminders) > 1:
                    self.payments.GetItem(index).SetTextColour(wx.Colour(128, 0, 0))
                self.data.append(bill.id)
                total_bills += sum(p.total_cts for p in bill.positions)
                total_reminder_costs += sum(r.amount_cts for r in bill.reminders)
                count += 1
        except:
            show_db_warning(logger, 'read')
        for c in range(self.payments.ColumnCount):
            self.payments.SetColumnWidth(c, wx.LIST_AUTOSIZE_USEHEADER if c == 1 else wx.LIST_AUTOSIZE)
        self.payments_count.Value = str(count)
        self.total_bills.Value = '%0.2f CHF' % (total_bills/100.)
        self.total_reminder_costs.Value = '%0.2f CHF' % (total_reminder_costs/100.)
        self.total.Value = '%0.2f CHF' % ((total_bills + total_reminder_costs)/100.)

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
                show_error(logger, "Une erreur s'est produite lors de la lecture du fichier de paiement.\n%r" % e.args)
                return None
        return records

    def on_import_payments(self, event):
        with wx.FileDialog(self, "Importer les paiements", wildcard="Relevers de paiement (*.v11)|*.v11", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
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
            reminder_cts = 0
            bills = list(Bill.yield_all(self.cursor, where=dict(bv_ref=ref_no)))
            if bills:
                bill = bills[0]
                bill_cts = sum(p.total_cts for p in bill.positions)
                for reminder in [0] + [r.amount_cts for r in sorted(bill.reminders, key=attrgetter('reminder_date'))]:
                    reminder_cts += reminder
                    if bill_cts + reminder_cts == amount_cts:
                        if bill.payment_date is None:
                            l = ok
                        else:
                            l = doubled
                        break
                else:
                    l = ko
            if l is not None:
                l.append((bill.id, bill_cts, reminder_cts, transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts))
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
        bill_ids = [id for i, id in enumerate(self.data) if self.payments.IsSelected(i)]
        try:
            if len(bill_ids) > 1:
                self.cursor.execute("""UPDATE bills SET payment_date = %s, status = 'P'
                                        WHERE payment_date IS NULL AND id IN %s""",
                                    [payment_date, tuple(bill_ids)])
            elif len(bill_ids) == 1:
                self.cursor.execute("""UPDATE bills SET payment_date = %s, status = 'P' WHERE id = %s""", [payment_date, bill_ids[0]])
        except:
            show_db_warning(logger, 'update')
        self.update_list()

    def on_print_again(self, event):
        bill_ids = [id for i, id in enumerate(self.data) if self.payments.IsSelected(i)]
        if bill_ids:
            bills = [Bill.load(self.cursor, id_bill) for id_bill in bill_ids]
            consults = [b for b in bills if b.type == BILL_TYPE_CONSULTATION]
            if consults:
                filename_consult = normalize_filename(datetime.datetime.now().strftime('consultations_%F_%Hh%Mm%Ss.pdf'))
                pdf_bills.consultations(filename_consult, consults)
                cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_consult)
                os.system(cmd + '&')
            manuals = [b for b in bills if b.type == BILL_TYPE_MANUAL]
            if manuals:
                filename_manual = normalize_filename(datetime.datetime.now().strftime('fact_manuelles_%F_%Hh%Mm%Ss.pdf'))
                pdf_bills.manuals(filename_manual, manuals)
                cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_manual)
                os.system(cmd + '&')

    def on_mark_printed(self, event):
        self.mark_status(STATUS_PRINTED)

    def on_mark_sent(self, event):
        self.mark_status(STATUS_SENT)

    def on_mark_abandoned(self, event):
        self.mark_status(STATUS_ABANDONED)

    def mark_status(self, status):
        bill_ids = [id for i, id in enumerate(self.data) if self.payments.IsSelected(i)]
        try:
            for id_bill in bill_ids:
                self.cursor.execute("""SELECT id FROM reminders WHERE id_bill = %s ORDER BY reminder_date DESC LIMIT 1""", [id_bill])
                last_reminder_id, = self.cursor.fetchone() or (None,)
                self.cursor.execute("""UPDATE bills SET status = %s WHERE status != 'P' AND id = %s""", [status, id_bill])
                if last_reminder_id is not None:
                    self.cursor.execute("""UPDATE reminders SET status = %s WHERE status != 'P' AND id = %s""", [status, last_reminder_id])
        except:
            show_db_warning(logger, 'update')
        self.update_list()


class RemindersManagementDialog(DBMixin, accounting.RemindersManagementDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.upto.Value = str(datetime.date.today() - datetime.timedelta(days=40))
        self.on_update_list()

    def on_update_list(self, *args):
        from dateutil import parse_ISO
        upto = parse_ISO(self.upto.Value.strip())
        self.reminders.DeleteAllItems()
        self.total.Value = ''
        self.data = []
        self.is_updating_list = True
        try:
            where = dict(payment_date__isnull=True, bv_ref__isnull=False, bv_ref__ne='', timestamp__le=upto, status__notin=('P', 'A'))
            for bill in Bill.yield_all(self.cursor, where=where, order='timestamp'):
                if bill.total_cts == 0:
                    continue
                if bill.reminders:
                    reminders_last = sorted(bill.reminders, key=attrgetter('reminder_date'))[-1].reminder_date
                    if reminders_last > upto:
                        continue
                else:
                    reminders_last = ''
                index = self.reminders.Append((bill.sex, bill.lastname, bill.firstname, bill.site, bill.timestamp.date(), '%0.2f' % ((bill.total_cts)/100.), reminders_last, len(bill.reminders)))
                self.reminders.Select(index)
                if len(bill.reminders) == 1:
                    self.reminders.SetItemTextColour(index, wx.Colour(64, 0, 0))
                    self.reminders.SetItemFont(index, self.GetFont().Italic())
                elif len(bill.reminders) > 1:
                    self.reminders.SetItemTextColour(index, wx.Colour(128, 0, 0))
                    self.reminders.SetItemFont(index, self.GetFont().Bold())
                self.data.append((bill.id, bill.total_cts, bill.sex, bill.lastname, bill.firstname, bill.timestamp, len(bill.reminders), sum(p.total_cts for p in bill.positions), sum(r.amount_cts for r in bill.reminders)))
        except:
            show_db_warning(logger, 'read')
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
        today = datetime.date.today()
        bills = []
        item = -1
        while True:
            item = self.reminders.GetNextSelected(item)
            if item == -1:
                break
            id_bill = self.data[item][0]
            self.cursor.execute("""INSERT INTO reminders (id_bill, amount_cts, reminder_date) VALUES (%s, %s, %s)""",
                                [id_bill, custo.MONTANT_RAPPEL_CTS, today])

            bills.append(Bill.load(self.cursor, id_bill))
        consults = [b for b in bills if b.type == BILL_TYPE_CONSULTATION]
        if consults:
            filename = normalize_filename(datetime.datetime.now().strftime('rappels_consultations_%F_%Hh%Mm%Ss.pdf'))
            pdf_bills.consultations(filename, consults)
            cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
            os.system(cmd)
        manuals = [b for b in bills if b.type == BILL_TYPE_MANUAL]
        if manuals:
            filename = normalize_filename(datetime.datetime.now().strftime('rappels_factures_manuelles_%F_%Hh%Mm%Ss.pdf'))
            pdf_bills.manuals(filename, manuals)
            cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
            os.system(cmd)
        self.Close()

    def on_cancel(self, event):
        self.Close()


class StatisticsDialog(DBMixin, accounting.StatisticsDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.cursor.execute("SELECT DISTINCT author_id AS therapeute FROM bills WHERE type = 'C' ORDER BY author_id")
        self.therapeutes = [t for t, in self.cursor]
        self.stats.AppendRows(len(self.therapeutes) + 1)
        for r, therapeute in enumerate(self.therapeutes + ['Total']):
            self.stats.SetRowLabelValue(r, therapeute)
        self.cursor.execute("SELECT DISTINCT YEAR(timestamp) AS year FROM bills WHERE type = 'C' ORDER BY year")
        self.years = [y for y, in self.cursor]
        self.months = ['tout', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        self.year.SetItems(['tout'] + [str(y) for y in self.years])
        self.month.SetItems(self.months)
        self.cursor.execute("SELECT DISTINCT tarif_code FROM positions ORDER BY tarif_code")
        self.stats_type.SetItems(["# Factures", "CHF Factures"] + ["CHF Code %s" % code for code, in self.cursor])
        self.cursor.execute("SELECT DISTINCT site FROM bills ORDER BY site")
        self.site.SetItems(['Tous'] + [s for s, in self.cursor])

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
        sql_filter = "YEAR(timestamp) = %s"

        def label_fn(args):
            return str(args[0])
        self.setup_view(sequence, sql_filter, label_fn)

    def setup_year_view(self, year):
        sequence = [[year, month] for month in range(1, 13)]
        sql_filter = "YEAR(timestamp) = %s AND MONTH(timestamp) = %s"

        def label_fn(args):
            return self.months[args[1]]
        self.setup_view(sequence, sql_filter, label_fn)

    def setup_month_view(self, year, month):
        sequence = [[year, month, day] for day in range(1, calendar.mdays[month]+1)]
        sql_filter = "YEAR(timestamp) = %s AND MONTH(timestamp) = %s AND DAY(timestamp) = %s"

        def label_fn(args):
            return str(args[2])
        self.setup_view(sequence, sql_filter, label_fn)

    def setup_view(self, sequence, sql_filter, label_fn):
        totals = {}
        grand_total = 0
        mode = self.stats_type.StringSelection
        if self.site.StringSelection != 'Tous':
            sql_filter += ' AND site = %s'
            site = [self.site.StringSelection]
        else:
            site = []

        def format(value):
            return ('{:,d}' if mode == '# Factures' else '{:0,.2f}').format(value).replace(',', "'")
        self.stats.BeginBatch()
        self.stats.AppendCols(len(sequence) + 1)
        self.stats.SetColLabelValue(len(sequence), 'Total')
        self.stats.SetDefaultCellAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        for c, args in enumerate(sequence):
            self.stats.SetColLabelValue(c, label_fn(args))
            if mode == '# Factures':
                self.cursor.execute("""SELECT author_id, count(*)
                                         FROM bills
                                        WHERE type = 'C' AND %s
                                        GROUP BY author_id
                                        ORDER BY author_id""" % sql_filter, args + site)
            elif mode == 'CHF Factures':
                self.cursor.execute("""SELECT author_id,
                                              sum((SELECT sum(total_cts)
                                                 FROM positions
                                                WHERE id_bill = bills.id)) / 100
                                         FROM bills
                                        WHERE type = 'C' AND %s
                                        GROUP BY author_id
                                        ORDER BY author_id""" % sql_filter, args + site)
            else:
                tarif_code = mode.replace('CHF Code ', '')
                self.cursor.execute("""SELECT author_id,
                                              sum((SELECT sum(total_cts)
                                                 FROM positions
                                                WHERE id_bill = bills.id AND tarif_code = %%s)) / 100
                                         FROM bills
                                        WHERE type = 'C' AND %s
                                        GROUP BY author_id
                                        ORDER BY author_id""" % sql_filter, [tarif_code] + args + site)
            col_total = 0
            for therapeute, value in self.cursor:
                if value is None:
                    continue
                line = self.therapeutes.index(therapeute)
                self.stats.SetCellValue(line, c, format(value))
                totals[therapeute] = totals.get(therapeute, 0) + value
                col_total += value
                grand_total += value
            self.stats.SetCellValue(len(self.therapeutes), c, format(col_total))
        for therapeute, total in totals.items():
            line = self.therapeutes.index(therapeute)
            self.stats.SetCellValue(line, len(sequence), format(total))
        self.stats.SetCellValue(len(self.therapeutes), len(sequence), format(grand_total))
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
        self.Fit()

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
                id_bill = payment[0]
                reminder_cts = payment[2]
                credit_date = payment[10]
                self.cursor.execute("UPDATE bills SET payment_date = %s WHERE id = %s", [credit_date, id_bill])
                if reminder_cts > 0:
                    self.cursor.execute("SELECT id, amount_cts FROM reminders WHERE id_bill = %s ORDER BY reminder_date", [id_bill])
                    for reminder_id, billed_reminder_cts in list(self.cursor):
                        if reminder_cts >= billed_reminder_cts:
                            self.cursor.execute("UPDATE reminders SET status = 'P' WHERE id = %s", [reminder_id])
                        else:
                            break
                        reminder_cts -= billed_reminder_cts
            self.Close()
        except:
            show_db_warning(logger, 'update')

    def on_cancel_import(self, event):
        self.Close()


class DetailsDialog(DBMixin, CancelableMixin, accounting.DetailsDialog):
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

        if len(self.positions[0]) == 14:
            self.populate_found()
        else:
            self.populate_notfound()
        for c in range(self.details.ColumnCount):
            self.details.SetColumnWidth(c, wx.LIST_AUTOSIZE)
        self.details.SetInitialSize(self.details.GetViewRect()[2:])
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
            self.details.AppendColumn(column, format=wx.LIST_FORMAT_RIGHT if 'CHF' in column else wx.LIST_FORMAT_LEFT, width=-1)
        data = []
        for id_bill, bill_cts, reminder_cts, transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts in self.positions:
            self.cursor.execute("""SELECT bills.timestamp,
                                          bills.payment_date,
                                          bills.sex,
                                          bills.lastname,
                                          bills.firstname,
                                          bills.birthdate,
                                          CAST(COALESCE((SELECT SUM(amount_cts) FROM reminders WHERE id_bill = bills.id), 0) AS SIGNED)
                                    FROM bills
                                   WHERE id = %s""",
                                [id_bill])
            timestamp, payment_date, sex, lastname, firstname, birthdate, billed_reminders_cts = self.cursor.fetchone()
            billed_reminders_cts = int(billed_reminders_cts)
            if billed_reminders_cts == 0:
                rappel = ''
            else:
                rappel = '%3.0f%%' % (reminder_cts * 100 / billed_reminders_cts)
            data.append((sex, lastname, firstname, birthdate, timestamp, '%0.2f' % ((bill_cts+billed_reminders_cts)/100.), '%0.2f' % (amount_cts/100.), rappel, self.format_date(credit_date), self.format_date(payment_date), self.format_ref(ref_no)))

        for values in data:
            self.details.Append(values)

    def populate_notfound(self):
        self.details.DeleteAllItems()
        self.details.DeleteAllColumns()
        columns = ["Type de transaction", "Payé CHF", "Crédité le", "Numéro de référence"]
        for column in columns:
            self.details.AppendColumn(column, format=wx.LIST_FORMAT_RIGHT if 'CHF' in column else wx.LIST_FORMAT_LEFT, width=-1)
        data = []
        for transaction_type, bvr_client_no, ref_no, amount_cts, depot_ref, depot_date, processing_date, credit_date, microfilm_no, reject_code, postal_fee_cts in self.positions:
            data.append((self.transaction_types.get(transaction_type, transaction_type), '%0.2f' % (amount_cts/100.), self.format_date(credit_date), self.format_ref(ref_no)))

        for values in data:
            self.details.Append(values)


class AccountingApp(BaseApp):
    MainFrameClass = AccountingFrame


if __name__ == '__main__':
    AccountingApp().MainLoop()
