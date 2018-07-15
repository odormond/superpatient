#! /usr/bin/env python3
# coding:UTF-8

import datetime
import mailcap
import logging
import os

import wx

from superpatient import BaseApp, DBMixin, HelpMenuMixin
from superpatient import bills, normalize_filename
from superpatient.bvr import gen_bvr_ref
from superpatient.customization import SITE
from superpatient.models import Bill, PAYMENT_METHODS, STATUS_OPENED, STATUS_SENT, STATUS_PAYED
from superpatient.ui.common import askyesno, show_db_warning
from superpatient.ui import cash_register


logger = logging.getLogger(__name__)


class CashRegisterFrame(DBMixin, HelpMenuMixin, cash_register.MainFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payment_method.SetItems(PAYMENT_METHODS[:-1])
        self.selected_idx = None
        self.on_refresh(None)

    def on_deselect_payment(self, event):
        self.firstname.Value = ""
        self.lastname.Value = ""
        self.therapeute.Value = ""
        self.price.Value = ""
        self.payment_method.SetSelection(wx.NOT_FOUND)
        self.payment_method.Disable()
        self.validate_btn.Disable()
        self.change_payment_method_btn.Disable()

    def on_select_payment(self, event):
        self.selected_idx = self.payments.GetFirstSelected()
        bill = self.data[self.selected_idx]
        self.lastname.Value = bill.lastname
        self.firstname.Value = bill.firstname
        self.therapeute.Value = bill.consultation.therapeute
        self.price.Value = '%6.2f CHF' % (bill.total_cts/100)
        self.payment_method.Enable()

    def on_select_payment_method(self, event):
        if self.selected_idx is not None and self.payment_method.StringSelection == self.data[self.selected_idx].payment_method:
            self.validate_btn.Enable()
            self.change_payment_method_btn.Disable()
        else:
            self.validate_btn.Disable()
            self.change_payment_method_btn.Enable()

    def on_validate(self, event):
        if self.payment_method.StringSelection == 'BVR':
            bill = self.data[self.selected_idx]
            if bill.status == STATUS_OPENED:
                filename_consult = normalize_filename(datetime.datetime.now().strftime('consultation_%F_%Hh%Mm%Ss.pdf'))
                bills.consultations(filename_consult, [bill])
                cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_consult)
                os.system(cmd + '&')
        self.real_validate()
        self.on_refresh(None)

    def on_change_payment(self, event):
        bill = self.data[self.selected_idx]
        if self.payment_method.StringSelection == 'BVR':
            if not askyesno("Confirmer le changement", "Voulez-vous vraiment changer la méthode de paiement vers BVR ?"):
                return
            bill.bv_ref = gen_bvr_ref(self.cursor, bill.firstname, bill.lastname, bill.timestamp)
        else:
            bill.bv_ref = None
        bill.payment_method = self.payment_method.StringSelection
        bill.save(self.cursor)
        filename_consult = normalize_filename(datetime.datetime.now().strftime('consultation_%F_%Hh%Mm%Ss.pdf'))
        bills.consultations(filename_consult, [bill])
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_consult)
        os.system(cmd + '&')
        self.real_validate()
        self.on_refresh(None)

    def on_refresh(self, event):
        "Populate liste based on the filter fields"
        self.on_deselect_payment(None)
        self.payments.DeleteAllItems()
        try:
            self.data = list(Bill.yield_all(self.cursor, "type = 'C' AND site = '%s' AND timestamp > CURDATE() AND (status = 'O' OR status = 'I' AND payment_method = 'BVR')" % SITE, "timestamp"))
            for bill in self.data:
                self.payments.Append((bill.sex, bill.lastname, bill.firstname, bill.consultation.therapeute, bill.timestamp.strftime('%H:%M'), '%0.2f' % (bill.total_cts/100), bill.payment_method))
        except:
            show_db_warning(logger, 'read')

    def real_validate(self):
        bill = self.data[self.selected_idx]
        try:
            if self.payment_method.StringSelection == 'BVR':
                bill.status = STATUS_SENT
                bill.save(self.cursor)
            elif self.payment_method.StringSelection not in ('Dû', 'PVPE'):
                bill.status = STATUS_PAYED
                bill.payment_date = datetime.date.today()
                bill.save(self.cursor)
        except:
            show_db_warning(logger, 'update')


class CashRegisterApp(BaseApp):
    MainFrameClass = CashRegisterFrame


if __name__ == '__main__':
    CashRegisterApp() .MainLoop()
