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

import os
import datetime

from reportlab.lib.units import mm, cm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .customization import bvr
from .bvr import bvr_checksum

BASE_DIR = os.path.join(os.path.dirname(__file__), 'pdfs')
pdfmetrics.registerFont(TTFont('OCRB', os.path.join(BASE_DIR, 'OCRB10PitchBT-Regular.ttf')))

PRINT_BV_BG = False

MARGIN = 1*cm
LOGO_WIDTH = 5.6*cm
#LOGO_HEIGHT = LOGO_WIDTH*469./676 (OLD LOGO)
LOGO_HEIGHT = LOGO_WIDTH*423./1280
BV_WIDTH = 210*mm
BV_HEIGHT = 106*mm
FONT_SIZE = 16
FONT_SIZE_BV = 12
BV_LINE = 1./6*inch
BV_COLUMN = 0.1*inch
BV_REF_X = 61*mm
BV_REF_Y = BV_HEIGHT

LEFT_TEXT_SHIFT = 8
LEFT_TEXT_SCALE = 0.92
MIDDLE_TEXT_SHIFT = 0
MIDDLE_TEXT_SCALE = 1
RIGHT_TEXT_SHIFT = 0
RIGHT_TEXT_SCALE = 1
REF_NO_SHIFT = 0
REF_NO_SCALE = 1.0


def draw_head(canvas, font_size):
    canvas.saveState()
    canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.jpg"), MARGIN, canvas._pagesize[1]-MARGIN-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
    canvas.setFont('EuclidBPBold', font_size)
    canvas.drawRightString(canvas._pagesize[0]-MARGIN, canvas._pagesize[1]-MARGIN-font_size, u"Lausanne, le "+datetime.date.today().strftime(u'%d.%m.%y'))
    canvas.restoreState()


def draw_bvr(canvas, prix_cts, address_patient, bv_ref):
    bv_ref = bv_ref or ''
    canvas.saveState()
    if PRINT_BV_BG:
        canvas.drawImage(os.path.join(BASE_DIR, "442_05_LAC_609_quer_Bank_CMYK.png"), 0, 0, BV_WIDTH, BV_HEIGHT)
    # CCP
    canvas.setFont('OCRB', 12)
    canvas.drawString(12*BV_COLUMN, BV_REF_Y - 11*BV_LINE, bvr.CCP)
    canvas.drawString(BV_REF_X + 12*BV_COLUMN, BV_REF_Y - 11*BV_LINE, bvr.CCP)
    # Lignes de codage
    v, x, c = bvr.CCP.split('-')
    codage = u''.join((v, u'0'*(6-len(x)), x, c, u'>'))
    prix = u'01%010d' % prix_cts
    codage = u'%s%d>%s+ %s' % (prix, bvr_checksum(prix), bv_ref, codage)
    text_obj = canvas.beginText()
    text_obj.setTextTransform(REF_NO_SCALE, 0, 0, 1, BV_REF_X + 3*BV_COLUMN + REF_NO_SHIFT, BV_REF_Y - 21*BV_LINE)
    text_obj.textLines(codage)
    canvas.drawText(text_obj)
    canvas.setFont('EuclidBPBold', 10-1)
    # Versé pour
    text_obj = canvas.beginText()
    text_obj.setTextTransform(LEFT_TEXT_SCALE, 0, 0, 1, BV_COLUMN + LEFT_TEXT_SHIFT, BV_REF_Y - 3*BV_LINE)
    text_obj.setLeading(0.9*10)
    text_obj.textLines(bvr.versement_pour+u'\n\n\n'+bvr.en_faveur_de)
    canvas.drawText(text_obj)
    text_obj = canvas.beginText()
    text_obj.setTextTransform(MIDDLE_TEXT_SCALE, 0, 0, 1, BV_REF_X + BV_COLUMN + MIDDLE_TEXT_SHIFT, BV_REF_Y - 3*BV_LINE)
    text_obj.setLeading(0.9*10)
    text_obj.textLines(bvr.versement_pour+u'\n\n\n'+bvr.en_faveur_de)
    canvas.drawText(text_obj)
    # Versé par
    ref = list(bv_ref)
    for i in (2, 8, 14, 20, 26):
        ref.insert(i, u' ')
    ref = u''.join(ref)
    canvas.setFont('OCRB', 8)
    text_obj = canvas.beginText()
    text_obj.setTextTransform(LEFT_TEXT_SCALE, 0, 0, 1, BV_COLUMN + LEFT_TEXT_SHIFT, BV_REF_Y - 15*BV_LINE)
    text_obj.textLines(ref)
    canvas.drawText(text_obj)
    canvas.setFont('OCRB', 12)
    text_obj = canvas.beginText()
    text_obj.setTextTransform(REF_NO_SCALE, 0, 0, 1, BV_REF_X + 25*BV_COLUMN + REF_NO_SHIFT, BV_REF_Y - 9*BV_LINE)
    text_obj.textLines(ref)
    canvas.drawText(text_obj)
    canvas.setFont('EuclidBPBold', 10-1)
    text_obj = canvas.beginText()
    text_obj.setTextTransform(LEFT_TEXT_SCALE, 0, 0, 1, BV_COLUMN + LEFT_TEXT_SHIFT, BV_REF_Y - 16*BV_LINE)
    text_obj.setLeading(1.5*BV_LINE)
    text_obj.textLines(address_patient)
    canvas.drawText(text_obj)
    text_obj = canvas.beginText()
    text_obj.setTextTransform(RIGHT_TEXT_SCALE, 0, 0, 1, BV_REF_X + 25*BV_COLUMN + RIGHT_TEXT_SHIFT, BV_REF_Y - 13*BV_LINE)
    text_obj.setLeading(1.5*BV_LINE)
    text_obj.textLines(address_patient)
    canvas.drawText(text_obj)
    # Le montant
    offset = 0.9
    spacing = 1.0
    canvas.setFont('OCRB', 12)
    montant = '%11.2f' % (float(prix_cts) / 100)
    text_obj = canvas.beginText()
    text_obj.setTextOrigin(offset*BV_COLUMN, BV_REF_Y - 13*BV_LINE)
    text_obj.setCharSpace(spacing*BV_COLUMN)
    text_obj.textLine(montant)
    canvas.drawText(text_obj)
    text_obj = canvas.beginText()
    text_obj.setTextOrigin(BV_REF_X + offset*BV_COLUMN, BV_REF_Y - 13*BV_LINE)
    text_obj.setCharSpace(spacing*BV_COLUMN)
    text_obj.textLine(montant)
    canvas.drawText(text_obj)
    #canvas.setFont('EuclidBPBold', 10-1)
    canvas.restoreState()
