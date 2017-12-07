#! /usr/bin/env python3
# coding:UTF-8

import os
import datetime
import traceback
import mailcap

#sys.path.insert(0, os.path.dirname(__file__))

import wx

from superpatient import BaseApp, DBMixin, HelpMenuMixin
from superpatient import bills, normalize_filename
from superpatient.bvr import gen_bvr_ref
from superpatient.customization import windows_title, errors_text, labels_text
from superpatient.models import Patient, Consultation, PAYMENT_METHODS, STATUS_OPENED
from superpatient.ui.common import askyesno, showwarning
from superpatient.ui import cash_register


class CashRegisterFrame(DBMixin, HelpMenuMixin, cash_register.MainFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payment_method.SetItems(PAYMENT_METHODS[:-1])
        self.selected_idx = None
        self.on_refresh(None)

    def on_deselect_payment(self, event):
        self.firstname.SetValue("")
        self.lastname.SetValue("")
        self.therapeute.SetValue("")
        self.price.SetValue("")
        self.payment_method.SetSelection(wx.NOT_FOUND)
        self.payment_method.Disable()
        self.validate_btn.Disable()
        self.change_payment_method_btn.Disable()

    def on_select_payment(self, event):
        self.selected_idx = self.payments.GetFirstSelected()
        id_consult, sex, lastname, firstname, therapeute, time_consult, total_price_cts, payment_method = self.data[self.selected_idx]
        self.lastname.SetValue(lastname)
        self.firstname.SetValue(firstname)
        self.therapeute.SetValue(therapeute)
        self.price.SetValue('%6.2f CHF' % (total_price_cts/100.))
        self.payment_method.Enable()

    def on_select_payment_method(self, event):
        if self.selected_idx is not None and self.payment_method.GetStringSelection() == self.data[self.selected_idx][-1]:
            self.validate_btn.Enable()
            self.change_payment_method_btn.Disable()
        else:
            self.validate_btn.Disable()
            self.change_payment_method_btn.Enable()

    def on_validate(self, event):
        if self.payment_method.GetStringSelection() == u'BVR':
            id_consult = self.data[self.selected_idx][0]
            consult = Consultation.load(self.cursor, id_consult)
            if consult.status == STATUS_OPENED:
                filename_consult = normalize_filename(datetime.datetime.now().strftime('consultation_%F_%Hh%Mm%Ss.pdf'))
                bills.consultations(filename_consult, self.cursor, [consult])
                cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_consult)
                os.system(cmd + '&')
        self.real_validate()
        self.on_refresh(None)

    def on_change_payment(self, event):
        id_consult = self.data[self.selected_idx][0]
        consult = Consultation.load(self.cursor, id_consult)
        if self.payment_method.GetStringSelection() == u'BVR':
            if not askyesno(windows_title.confirm_change, labels_text.ask_confirm_payment_method_change_to_BVR):
                return
            patient = Patient.load(self.cursor, consult.id)
            consult.bv_ref = gen_bvr_ref(self.cursor, patient.prenom, patient.nom, consult.date_consult)
        else:
            consult.bv_ref = None
        consult.paye_par = self.payment_method.GetStringSelection()
        consult.save(self.cursor)
        filename_consult = normalize_filename(datetime.datetime.now().strftime('consultation_%F_%Hh%Mm%Ss.pdf'))
        bills.consultations(filename_consult, self.cursor, [consult])
        cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename_consult)
        os.system(cmd + '&')
        self.real_validate()
        self.on_refresh(None)

    def on_refresh(self, event):
        "Populate liste based on the filter fields"
        self.on_deselect_payment(None)
        self.payments.DeleteAllItems()
        try:
            self.cursor.execute("""SELECT consultations.id_consult, sex, nom, prenom, COALESCE(consultations.therapeute, patients.therapeute), heure_consult, prix_cts + majoration_cts + frais_admin_cts, paye_par
                                FROM consultations INNER JOIN patients ON consultations.id = patients.id
                               WHERE date_consult = CURDATE() AND (status = 'O' OR status = 'I' AND paye_par = 'BVR')
                               ORDER BY heure_consult""")
            today = datetime.datetime.combine(datetime.date.today(), datetime.time())
            self.data = [(id_consult, sex, nom, prenom, therapeute, (today + (heure_consult or datetime.timedelta(0))).time(), prix_cts, paye_par) for id_consult, sex, nom, prenom, therapeute, heure_consult, prix_cts, paye_par in self.cursor]
            for id_consult, sex, nom, prenom, therapeute, heure_consult, prix_total_cts, paye_par in self.data:
                self.payments.Append((sex, nom, prenom, therapeute, heure_consult.strftime(u'%H:%M'), '%0.2f' % (prix_total_cts/100.), paye_par))
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_read)

    def real_validate(self):
        id_consult = self.data[self.selected_idx][0]
        try:
            if self.payment_method.GetStringSelection() == u'BVR':
                self.cursor.execute("""UPDATE consultations SET status = 'E' WHERE id_consult = %s""", [id_consult])
            elif self.payment_method.GetStringSelection() not in (u'Dû', u'PVPE'):
                self.cursor.execute("""UPDATE consultations SET paye_le = CURDATE(), status = 'P' WHERE id_consult = %s""", [id_consult])
        except:
            traceback.print_exc()
            showwarning(windows_title.db_error, errors_text.db_update)


class CashRegisterApp(BaseApp):
    MainFrameClass = CashRegisterFrame


if __name__ == '__main__':
    CashRegisterApp().MainLoop()
