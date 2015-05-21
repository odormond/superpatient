#! /usr/bin/env python
# coding:UTF-8

import sys
import datetime
import traceback

try:
    import Tkinter as tk
    import tkMessageBox

except:
    tkMessageBox.showwarning("Error", "Tkinter is not correctly installed !")
    sys.exit()

try:
    import bp_connect
except:
    tkMessageBox.showwarning("Missing file", "bp_connect.py is missing")
    sys.exit()

try:
    import bp_custo
    from bp_custo import windows_title, errors_text
except:
    tkMessageBox.showwarning("Missing file", "bp_custo.py is missing")
    sys.exit()

try:
    from bp_widgets import ListboxWidget, EntryWidget, OptionWidget
except:
    tkMessageBox.showwarning("Missing file", "bp_widgets.py is missing")
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

cursor = db.cursor()


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        if (sys.platform != 'win32') and hasattr(sys, 'frozen'):
            self.tk.call('console', 'hide')

        self.option_add('*font', 'Helvetica -15')

        try:
            cursor.execute("SELECT therapeute FROM therapeutes ORDER BY therapeute")
            therapeutes = ['TOUS'] + [t for t, in cursor]
        except:
            traceback.print_exc()
            tkMessageBox.showwarning(windows_title.db_error, errors_text.db_read)
            sys.exit(1)

        # Top block: select what to display
        self.therapeute = OptionWidget(self, 'therapeute', 0, 0, value=therapeutes)
        self.paye_par = OptionWidget(self, 'paye_par', 1, 0, value=bp_custo.MOYEN_DE_PAYEMENT)
        self.date_du = EntryWidget(self, 'date_du', 0, 2, value=last_month)
        self.date_au = EntryWidget(self, 'date_au', 1, 2)
        self.date_du.bind('<KeyRelease-Return>', self.update_list)
        self.date_au.bind('<KeyRelease-Return>', self.update_list)

        # Middle block: list display
        self.list = ListboxWidget(self, 'consultations', 2, 0, columnspan=4)

        # Bottom block: available action on selected items
