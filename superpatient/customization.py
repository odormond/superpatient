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

from pathlib import Path
PDF_DIR = str(Path(__file__).parents[1] / 'factures')


VERSION = '4.27'


SITE = 'Lausanne'
DEFAULT_CANTON = "VD"

BILL_TYPE = '590'
DATE_FMT = "%d.%m.%Y"

MONTANT_RAPPEL_CTS = 500

PAIEMENT_SORTIE = True

# Set to an empty list to disable the feature
SIGNATURE_URLS = [
    'https://api.osteosoft.ch/api/v1/billing/datamatrix',
    'https://api2.osteosoft.ch/api/v1/billing/datamatrix',
]

ROUNDING_MODE = '5cts'  # See models.py for alternatives


COMPANY_NAME = "Permanence Ostéopathique de la Gare (POG) Sàrl"
ADDRESS = "Pl. de la Gare 10\n1003 Lausanne"
WEB_SITE = "www.pog.swiss"
PHONE = "021 510 50 50"
FULL_ADDRESS = "\n".join((COMPANY_NAME, ADDRESS, WEB_SITE, PHONE))

BILL_TYPE_AND_SITE = "Ostéopathie / {SITE}".format(SITE=SITE)


class BVR:
    CCP = '01-145-6'
    prefix = 272335
    versement_pour = "UBS Switzerland\n8098 Zurich"
    en_faveur_de = "Permanence Ostéopathique\nde la Gare (POG) Sàrl\nPl. de la Gare 10\n1003 Lausanne"
