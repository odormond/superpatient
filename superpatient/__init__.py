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

import datetime
import logging
import logging.config
from pathlib import Path
import re
import sys
import time
import threading

import wx

from . import credentials, db
from .customization import PDF_DIR
from .models import SEX_MALE, SEX_FEMALE
from .ui.common import show_error, AboutDialog, LicenseDialog


logger = logging.getLogger(__name__)

WIN_CORNER_SHIFT = 32


class BaseApp(wx.App):
    def OnInit(self):
        self.app_name = Path(sys.argv[0]).stem
        self.init_logging()
        self.init_db()
        self.init_reportlab()
        self.init_dateutil()

        super().OnInit()
        wx.Dialog.EnableLayoutAdaptation(True)
        self.main_frame = self.MainFrameClass(None)
        self.SetTopWindow(self.main_frame)
        self.main_frame.Show()
        self.main_frame.Position = (0, WIN_CORNER_SHIFT) if sys.platform == 'darwin' else (0, 0)
        return True

    def init_logging(self):
        logfile = (Path(__file__).parents[1] / 'logs' / self.app_name).with_suffix('.log')
        logfile.parent.mkdir(exist_ok=True)
        logging.config.dictConfig(
            {'version': 1,
             'disable_existing_loggers': False,
             'formatters': {'default': {'format': '%(asctime)-15s %(levelname)8s %(name)s:%(lineno)s: %(message)s'},
                            'brief': {'format': '%(levelname)s: %(message)s'},
                            },
             'handlers': {'file': {'class': 'logging.handlers.RotatingFileHandler',
                                   'formatter': 'default',
                                   'level': 'DEBUG',
                                   'filename': str(logfile),
                                   'maxBytes': 10*1024*1024,
                                   'backupCount': 5,
                                   },
                          'console': {'class': 'logging.StreamHandler',
                                      'formatter': 'brief',
                                      'level': 'INFO',
                                      'stream': 'ext://sys.stdout',
                                      },
                          },
             'root': {'level': 'DEBUG',
                      'handlers': ['file', 'console']},
             })
        logger.info("Detailed logs can be found in %s", logfile)

    def init_reportlab(self):
        from . import bills
        if bills.REPORTLAB_IS_MISSING:
            show_error(logger, "The reportlab module is not correctly installed!")
            sys.exit(1)

    def init_db(self):
        try:
            import MySQLdb
            import MySQLdb.cursors
        except:
            show_error(logger, "The MySQLdb module is not correctly installed!")
            sys.exit(1)

        class ResilientCursor(MySQLdb.cursors.Cursor):
            def execute(self, query, args=None):
                t0 = time.time()
                try:
                    return super(ResilientCursor, self).execute(query, args)
                except MySQLdb.OperationalError as e:
                    if e.args[0] in (2006, 2013):  # Connection was lost. Retry once
                        return super(ResilientCursor, self).execute(query, args)
                    else:
                        logger.error("Failed to execute SQL query %r with args %r", query, args)
                        raise
                finally:
                    t1 = time.time()
                    logger.debug("SQL Timing: %.3fms for %r", (t1-t0) * 1000, re.sub(rb'\s+', b' ', self._executed))

        try:
            self.connection = MySQLdb.connect(host=db.SERVER, user=credentials.DB_USER, passwd=credentials.DB_PASS, db=db.DATABASE, charset='utf8', cursorclass=ResilientCursor)
        except:
            show_error(logger, "Cannot connect to database")
            sys.exit(1)

        self.connection.ping(True)
        self.connection.autocommit(True)

        threading.Thread(target=self._keepalive, daemon=True).start()

    def _keepalive(self):
        while True:
            t0 = time.time()
            self.connection.ping(True)
            logger.debug("Pinged DB in %0.3fms", (time.time()-t0)*1000)
            time.sleep(30)

    def init_dateutil(self):
        try:
            import dateutil
            from dateutil.parser import parse, parserinfo
        except:
            show_error(logger, "The dateutil module is not correctly installed!")
            sys.exit(1)

        class FrenchParserInfo(parserinfo):
            MONTHS = [('jan', 'janvier'), ('fév', 'février'), ('mar', 'mars'), ('avr', 'avril'), ('mai', 'mai'), ('jui', 'juin'), ('jul', 'juillet'), ('aoû', 'août'), ('sep', 'septembre'), ('oct', 'octobre'), ('nov', 'novembre'), ('déc', 'décembre')]
            WEEKDAYS = [('Lun', 'Lundi'), ('Mar', 'Mardi'), ('Mer', 'Mercredi'), ('Jeu', 'Jeudi'), ('Ven', 'Vendredi'), ('Sam', 'Samedi'), ('Dim', 'Dimanche')]
            HMS = [('h', 'heure', 'heures'), ('m', 'minute', 'minutes'), ('s', 'seconde', 'secondes')]
            JUMP = [' ', '.', ',', ';', '-', '/', "'", "le", "er", "ième"]

        datesFR = FrenchParserInfo(dayfirst=True)
        MIN_DATE = datetime.date(1900, 1, 1)  # Cannot strftime before that date

        def parse_date(s):
            try:
                d = parse(s, parserinfo=datesFR).date()
            except ValueError:
                return None
            if d < MIN_DATE:
                raise ValueError("Date too old")
            return d
        dateutil.parse_date = parse_date

        def parse_ISO(s):
            if s.find('-') != 4:
                return parse_date(s)
            try:
                d = parse(s).date()
            except ValueError:
                return None
            if d < MIN_DATE:
                raise ValueError("Date too old")
            return d
        dateutil.parse_ISO = parse_ISO


class DBMixin:
    def __init__(self, *args, **kwargs):
        self.connection = wx.App.Get().connection
        self.cursor = self.connection.cursor()
        super().__init__(*args, **kwargs)


class HelpMenuMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert hasattr(self, 'menubar'), "A `menubar` must be present to use the HelpMenuMixin"
        help_menu = wx.Menu()
        item = help_menu.Append(wx.ID_ANY, "À propos", "")
        self.Bind(wx.EVT_MENU, self.on_about, id=item.GetId())
        item = help_menu.Append(wx.ID_ANY, "Conditions d'utilisations", "")
        self.Bind(wx.EVT_MENU, self.on_license, id=item.GetId())
        self.menubar.Append(help_menu, "Aide")

    def on_about(self, event):
        AboutDialog(self).ShowModal()

    def on_license(self, event):
        LicenseDialog(self).ShowModal()


class CancelableMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_cancel)
        x, y = self.Parent.Position
        self.Position = x + WIN_CORNER_SHIFT, y

    def on_cancel(self, event=None):
        if not isinstance(event, wx.KeyEvent) or event.KeyCode == wx.WXK_ESCAPE:
            self.Close()
        else:
            event.Skip()


# Utility functions used by more than one module

def normalize_filename(filename):
    for char in '\'"/`!$[]{}':
        filename = filename.replace(char, '-')
    filename = filename.replace(' ', '_').replace('\t', '_')
    return str(Path(PDF_DIR, filename))


def gen_title(sex, birthdate):
    today = datetime.date.today()
    adult = today.replace(year=today.year - 18)
    if birthdate > adult:
        return "Aux parents de"
    elif sex == SEX_MALE:
        return "Monsieur"
    elif sex == SEX_FEMALE:
        return "Madame"
    else:
        return ""
