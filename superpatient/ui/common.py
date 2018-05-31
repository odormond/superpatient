import datetime
from textwrap import dedent

import wx
import wx.adv


def show_info(message, parent=None):
    print("INFO:", message)
    wx.MessageBox(message, "Information", wx.OK | wx.ICON_INFORMATION, parent)


def show_warning(message, parent=None):
    print("WARN:", message)
    wx.MessageBox(message, "Attention", wx.OK | wx.ICON_EXCLAMATION, parent)


def show_db_warning(operation):
    message = dict(read="Impossible de lire les données !",
                   update="Modification impossible !",
                   insert="Insertion impossible !",
                   delete="Suppression impossible !",
                   search="Recherche impossible !",
                   show="Affichage impossible !",
                   )[operation]
    print("WARN: database error:", message)
    wx.MessageBox(message, "Problème avec la base de donnée", wx.OK | wx.ICON_EXCLAMATION)


def show_error(message, parent=None):
    print("ERROR:", message)
    wx.MessageBox(message, "Erreur", wx.OK | wx.ICON_ERROR, parent)


def askyesno(title, message, parent=None):
    return wx.MessageBox(message, title, wx.YES_NO | wx.STAY_ON_TOP, parent) == wx.YES


class AboutDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        super().__init__(*args, **kwds)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("À propos")
        self.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

    def __do_layout(self):
        from ..customization import VERSION
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(
            self, wx.ID_ANY,
            dedent("""
            SuperPatient ver. {VERSION} est un gestionnaire de patients, de consultations, et de facturation.

            Il a été créé en 2006 pour satisfaire aux besoins minimaux d'un cabinet de groupe d'ostéopathes.

            Superpatient est sous licence GPL.

            Pour tout autre renseignement, veuillez écrire à

            Tibor Csernay
            csernay@pog.swiss
            """).format(VERSION=VERSION),
            style=wx.ALIGN_CENTER)
        label.Wrap(350)
        sizer.Add(label, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(sizer)
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
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(
            self, wx.ID_ANY,
            dedent("""
            POG Sàrl - Copyright 2006-2018 - www.pog.swiss

            SuperPatient is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

            SuperPatient is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

            You should have received a copy of the GNU General Public License along with SuperPatient; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
            """),
            style=wx.ALIGN_CENTER)
        label.Wrap(400)
        sizer.Add(label, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizerAndFit(sizer)
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
