#!/usr/bin/local/python
# -*- coding: UTF-8 -*-

# File: bp_Dialog.py

#    Copyright 2006, 2007 Tibor Csernay

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

from Tkinter import Toplevel, Frame, BOTH


class Dialog(Toplevel):

    def __init__(self, parent):
        Toplevel.__init__(self, parent)

        self.transient(parent)

        self.parent = parent
        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5, fill=BOTH, expand=1)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self):
        pass

    def buttonbox(self):
        pass

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()
