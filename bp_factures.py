#! /usr/bin/env python2
# coding:UTF-8

import os
import datetime
from math import sqrt
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, Spacer, PageBreak, FrameBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm, inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from bp_custo import CCP, DATE_FMT
from bp_bvr import bvr_checksum

PRINT_BV_BG = True

SQRT2 = sqrt(2)

BASE_DIR = os.path.join(os.path.dirname(__file__), 'pdfs')
pdfmetrics.registerFont(TTFont('EuclidBPBold', os.path.join(BASE_DIR, 'Euclid_BP_Bold.ttf')))
pdfmetrics.registerFont(TTFont('OCRB', os.path.join(BASE_DIR, 'OCRB10PitchBT-Regular.ttf')))

MARGIN = 1*cm
LOGO_WIDTH = 5.6*cm
LOGO_HEIGHT = LOGO_WIDTH*469./676
BV_WIDTH = 210*mm
BV_HEIGHT = 106*mm
FONT_SIZE = 16
FONT_SIZE_BV = 12
BV_LINE = 1./6*inch
BV_COLUMN = 0.1*inch
BV_REF_X = 61*mm
BV_REF_Y = BV_HEIGHT


def ParagraphOrSpacer(text, style):
    if text.strip():
        return Paragraph(text, style)
    return Spacer(0, FONT_SIZE)


def make_styles(font_size):
    DEFAULT_STYLE = ParagraphStyle('default', fontName='EuclidBPBold', fontSize=font_size, leading=font_size*1.2)
    COPIE_STYLE = ParagraphStyle('default', fontName='EuclidBPBold', fontSize=font_size+2)
    FACTURE_STYLE = ParagraphStyle('title', fontName='EuclidBPBold', fontSize=font_size+4)

    DEFAULT_TABLE_STYLE = [('FONT', (0, 0), (-1, -1), 'EuclidBPBold', font_size),
                           ('ALIGN', (1, 0), (1, -1), 'RIGHT')]
    MAJORATION_TABLE_STYLE = [('FONT', (0, 0), (-1, -1), 'EuclidBPBold', font_size),
                              ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                              ('ALIGN', (1, 2), (1, 2), 'RIGHT'),
                              ('LINEABOVE', (2, 2), (2, 2), 2, colors.black),
                              ]
    return DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_TABLE_STYLE


def fixed(canvas, doc):
    if not doc.patient_bv:
        canvas.translate(0, doc.pagesize[1])
        canvas.rotate(-90)
        canvas.scale(1/SQRT2, 1/SQRT2)
        font_size = FONT_SIZE
    else:
        font_size = FONT_SIZE_BV

    DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_TABLE_STYLE = make_styles(font_size)

    canvas.saveState()
    canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.png"), doc.leftMargin, doc.pagesize[1]-doc.topMargin-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
    canvas.setFont('EuclidBPBold', font_size)
    canvas.drawRightString(doc.pagesize[0]-doc.rightMargin, doc.pagesize[1]-doc.topMargin-font_size, u"Lausanne, le "+datetime.date.today().strftime(u'%d.%m.%y'))
    if doc.patient_bv and doc.page == 1:
        if PRINT_BV_BG:
            if doc.bv_ref:
                canvas.drawImage(os.path.join(BASE_DIR, "442_05_LAC_609_quer_CMYK.png"), 0, 0, BV_WIDTH, BV_HEIGHT)
            else:
                canvas.drawImage(os.path.join(BASE_DIR, "441_02_ES_LAC_105_quer_CMYK.png"), 0, 0, BV_WIDTH, BV_HEIGHT)
        canvas.saveState()
        # CCP
        canvas.setFont('OCRB', 12)
        canvas.drawString(12*BV_COLUMN, BV_REF_Y - 11*BV_LINE, CCP)
        canvas.drawString(BV_REF_X + 12*BV_COLUMN, BV_REF_Y - 11*BV_LINE, CCP)
        # Lignes de codage
        v, x, c = CCP.split('-')
        codage = u''.join((v, u'0'*(6-len(x)), x, c, u'>'))
        if doc.bv_ref:
            prix = u'01%010d' % (doc.prix * 100)
            codage = u'%s%d>%s+ %s' % (prix, bvr_checksum(prix), doc.bv_ref, codage)
            canvas.drawString(BV_REF_X + 3*BV_COLUMN, BV_REF_Y - 21*BV_LINE, codage)
        else:
            canvas.drawString(BV_REF_X + 46*BV_COLUMN, BV_REF_Y - 21*BV_LINE, codage)
            canvas.drawString(BV_REF_X + 46*BV_COLUMN, BV_REF_Y - 23*BV_LINE, codage)
        canvas.setFont('EuclidBPBold', 10-1)
        # Versé pour
        text_obj = canvas.beginText()
        text_obj.setTextOrigin(BV_COLUMN, BV_REF_Y - 3*BV_LINE)
        text_obj.setLeading(0.9*10)
        text_obj.textLines(doc.therapeute)
        canvas.drawText(text_obj)
        text_obj = canvas.beginText()
        text_obj.setTextOrigin(BV_REF_X+BV_COLUMN, BV_REF_Y - 3*BV_LINE)
        text_obj.setLeading(0.9*10)
        text_obj.textLines(doc.therapeute)
        canvas.drawText(text_obj)
        # Motif
        if not doc.bv_ref:
            canvas.drawString(BV_REF_X + 25*BV_COLUMN, BV_REF_Y - 4*BV_LINE, u"Consultation du "+unicode(doc.date.strftime(DATE_FMT)))
        # Versé par
        if doc.bv_ref:
            ref = list(doc.bv_ref)
            for i in (2, 8, 14, 20, 26):
                ref.insert(i, u' ')
            ref = u''.join(ref)
            canvas.setFont('OCRB', 8)
            text_obj = canvas.beginText()
            text_obj.setTextOrigin(BV_COLUMN, BV_REF_Y - 15*BV_LINE)
            text_obj.textLines(ref)
            canvas.drawText(text_obj)
            canvas.setFont('OCRB', 12)
            text_obj = canvas.beginText()
            text_obj.setTextOrigin(BV_REF_X + 25*BV_COLUMN, BV_REF_Y - 9*BV_LINE)
            text_obj.textLines(ref)
            canvas.drawText(text_obj)
            canvas.setFont('EuclidBPBold', 10-1)
        text_obj = canvas.beginText()
        text_obj.setTextOrigin(BV_COLUMN, BV_REF_Y - 16*BV_LINE)
        text_obj.setLeading(1.5*BV_LINE)
        text_obj.textLines(doc.patient_bv)
        canvas.drawText(text_obj)
        text_obj = canvas.beginText()
        text_obj.setTextOrigin(BV_REF_X + 25*BV_COLUMN, BV_REF_Y - 13*BV_LINE)
        text_obj.setLeading(1.5*BV_LINE)
        text_obj.textLines(doc.patient_bv)
        canvas.drawText(text_obj)
        # Le montant
        offset = 1.3  # 1.4
        spacing = 1.0
        canvas.setFont('OCRB', 12)
        montant = '%11.2f' % doc.prix
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
        canvas.setFont('EuclidBPBold', 10-1)
        canvas.restoreState()
    else:
        canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.png"), doc.pagesize[0]+doc.leftMargin, doc.pagesize[1]-doc.topMargin-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
        canvas.drawRightString(2*doc.pagesize[0]-doc.rightMargin, doc.pagesize[1]-doc.topMargin-font_size, u"Lausanne, le "+datetime.date.today().strftime('%d.%m.%y'))
    canvas.restoreState()

    def make_italic(canvas, event, label):
        canvas.skew(0, 20)
        canvas.setFont('EuclidBPBold', font_size+4)
        canvas.drawString(0, 0, label)

    def make_bold(canvas, event, label):
        canvas.setFont('EuclidBPBold', font_size+2)
        canvas.drawString(-0.1, 0, label)
        canvas.drawString(0.1, 0, label)
        canvas.drawString(0, -0.1, label)
        canvas.drawString(0, 0.1, label)

    canvas.make_italic = make_italic
    canvas.make_bold = make_bold


def facture(filename, therapeute, patient, duree, accident, prix_cts, description_majoration, majoration_cts, date, patient_bv=None, bv_ref=None):
    doc = BaseDocTemplate(filename, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    doc.prix = (prix_cts + majoration_cts) / 100.
    doc.therapeute = therapeute
    doc.patient = patient
    doc.patient_bv = patient_bv
    doc.bv_ref = bv_ref
    doc.date = date
    doc.duree = duree
    if patient_bv:
        templates = [PageTemplate(id='bv', frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height)], onPage=fixed),
                     PageTemplate(id='copie', frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height)], onPage=fixed),
                     ]
        DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_TABLE_STYLE = make_styles(FONT_SIZE_BV)
    else:
        templates = [PageTemplate(id='recu',
                                  frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height),
                                          Frame(doc.pagesize[0]+doc.leftMargin, doc.rightMargin, doc.width, doc.height)],
                                  onPage=fixed)]
        DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_TABLE_STYLE = make_styles(FONT_SIZE)

    doc.addPageTemplates(templates)
    prix = u'%0.2f CHF' % (prix_cts/100.)
    tstyle = DEFAULT_TABLE_STYLE
    data = [[Paragraph(u"Prise en charge ostéopathique %s datée du %s" % (duree, date.strftime(DATE_FMT)), DEFAULT_STYLE), None, prix], ]
    if majoration_cts:
        tstyle = MAJORATION_TABLE_STYLE
        majoration = u'%0.2f CHF' % (majoration_cts/100.)
        total = u'%0.2f CHF' % ((prix_cts+majoration_cts)/100.)
        data += [[description_majoration, None, majoration]]
        data += [[None, u'TOTAL', total]]
    if accident:
        data += [[u"Raison : accident", None, ]]
    else:
        data += [[u"Raison : maladie", None, ]]
    if not patient_bv:
        data[-1].append(u"payé")
    therapeute = [ParagraphOrSpacer(line, DEFAULT_STYLE) for line in therapeute.splitlines()]
    patient = [ParagraphOrSpacer(line, DEFAULT_STYLE) for line in patient.splitlines()]
    fact = [Spacer(0, LOGO_HEIGHT),
            Table([[therapeute, patient]],
                  colWidths=[doc.width*2/3, doc.width/3],
                  style=[('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]),
            Spacer(0, MARGIN),
            Paragraph(u'', DEFAULT_STYLE),
            Spacer(0, 1*MARGIN),
            Paragraph(u'<onDraw name=make_italic label="FACTURE"/>', FACTURE_STYLE),
            Spacer(0, 1*MARGIN),
            Table(data, colWidths=[doc.width-5*cm, 1.5*cm, 3.5*cm], style=tstyle),
            Spacer(0, 1.5*MARGIN),
            Paragraph(u"Avec mes remerciements.", DEFAULT_STYLE),
            ]
    recu = fact[:]
    recu[3] = Paragraph(u'<onDraw name=make_bold label="COPIE"/>', COPIE_STYLE)
    if patient_bv:
        story = fact + [PageBreak()] + recu
    else:
        story = fact + [FrameBreak()] + recu
    doc.build(story)


if __name__ == '__main__':
    filename = os.tempnam()+'.pdf'
    therapeute = u'Tibor Csernay\nDipl. CDS-GDK\n\nAv. de la gare 5\n1003 Lausanne\n021 510 50 50\n021 510 50 49 (N° direct)\n\nRCC U905461'
    patient = u'Monsieur\nJean Dupont\nRoute de Quelque Part\n1234 Perdu\n\n12.03.1974'
    bv_ref = u"012345678901234567890123458"
    patient_bv = u'Jean Dupont\nRoute de Quelque Part\n1234 Perdu'
    duree = u'entre 21 et 30 minutes'
    prix_cts = 1234567890
    majoration_cts = 2000
    description_majoration = u"Supplément test"
    accident = True
    date = datetime.date.today()
    facture(filename, therapeute, patient, duree, accident, prix_cts, description_majoration, majoration_cts, date, patient_bv, bv_ref)

    import mailcap
    import time
    cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
    os.system(cmd)
    time.sleep(10)
    os.unlink(filename)
