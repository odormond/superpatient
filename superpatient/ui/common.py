import datetime

import wx
import wx.adv


def showinfo(title, message, parent=None):
    print("INFO:", title, ":", message)
    wx.MessageBox(message, title, wx.OK | wx.ICON_INFORMATION, parent)


def showwarning(title, message, parent=None):
    print("WARN:", title, ":", message)
    wx.MessageBox(message, title, wx.OK | wx.ICON_EXCLAMATION, parent)


def showerror(title, message, parent=None):
    print("WARN:", title, ":", message)
    wx.MessageBox(message, title, wx.OK | wx.ICON_ERROR, parent)


def askyesno(title, message, parent=None):
    return wx.MessageBox(message, title, wx.YES_NO | wx.STAY_ON_TOP, parent) == wx.YES


class AboutDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        super().__init__(*args, **kwds)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle(u"À propos")

    def __do_layout(self):
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        label_15 = wx.StaticText(self, wx.ID_ANY, u"SuperPatient ver. 4.0 est un gestionnaire de patients,\nde consultations et de facturations.\n\nIl a été créé en 2006 pour satisfaire aux besoins\nminimaux d'un cabinet de groupe d'ostéopathes.\n\nSuperPatient est sous licence GPL.\n\nPour tout autre renseignement, veuillez écrire à\n\nTibor Csernay\ncsernay@pog.swiss", style=wx.ALIGN_CENTER)
        label_15.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_3.Add(label_15, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer_3)
        sizer_3.Fit(self)
        self.Layout()


class LicenseDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        super().__init__(*args, **kwds)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("License")
        self.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        label_1 = wx.StaticText(self, wx.ID_ANY, u"POG Sàrl - Copyright 2006-2017 - www.pog.swiss\n\nSuperPatient is free software; you can redistribute it and/or modify\nit under the terms of the GNU General Public License as published by\nthe Free Software Foundation; either version 2 of the License, or\n(at you option) any later version.\n\nSuperPatient is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without event the implied warranty of\nMECHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\nSee the GNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public LIcense\nalong with SuperPatient; if not, write to the Free Software\nFoundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA", style=wx.ALIGN_CENTER)
        sizer_1.Add(label_1, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()


class DatePickerDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        date = kwds.pop('date', None)
        kwds['style'] = wx.DEFAULT_DIALOG_STYLE
        super().__init__(*args, **kwds)

        if date is not None:
            wx_date = wx.DateTime()
            if isinstance(date, str):
                wx_date.ParseDate(date)
            elif isinstance(date, datetime.date):
                wx_date = wx.pydate2wxdate(date)
            else:
                wx_date = date
        else:
            wx_date = wx.DefaultDateTime
        self.date = wx.adv.GenericCalendarCtrl(self, wx.ID_ANY, date=wx_date)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.adv.EVT_CALENDAR, self.on_date_picked, self.date)
        self.Bind(wx.EVT_CLOSE, self.on_date_picked, self)

    def on_date_picked(self, event):
        self.Value = wx.wxdate2pydate(self.date.Date)
        self.EndModal(1)

    def __set_properties(self):
        self.SetTitle("Sélectionner une date")
        self.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.date, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
