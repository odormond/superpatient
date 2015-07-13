#! /usr/bin/env python
# coding:UTF-8

import os
import datetime
from math import sqrt
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Preformatted, Table, Spacer, PageBreak, FrameBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm, inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from bp_custo import CCP

SQRT2 = sqrt(2)

BASE_DIR = os.path.join(os.path.dirname(__file__), 'pdfs')
pdfmetrics.registerFont(TTFont('EuclidBPBold', os.path.join(BASE_DIR, 'Euclid_BP_Bold.ttf')))
pdfmetrics.registerFont(TTFont('OCRB', os.path.join(BASE_DIR, 'OCRB10PitchBT-Regular.ttf')))

MARGIN = 1*cm
LOGO_WIDTH = 5.6*cm
LOGO_HEIGHT = LOGO_WIDTH*469./676
BV_WIDTH = 210*mm
BV_HEIGHT = 106*mm
FONT_SIZE = 10
BV_LINE = 1./6*inch
BV_COLUMN = 0.1*inch
BV_REF_X = 61*mm
BV_REF_Y = BV_HEIGHT

DEFAULT_STYLE = ParagraphStyle('default', fontName='EuclidBPBold', fontSize=FONT_SIZE)
COPIE_STYLE = ParagraphStyle('default', fontName='EuclidBPBold', fontSize=FONT_SIZE+2)
FACTURE_STYLE = ParagraphStyle('title', fontName='EuclidBPBold', fontSize=FONT_SIZE+4)

DEFAULT_TABLE_STYLE = [('FONT', (0, 0), (-1, -1), 'EuclidBPBold', FONT_SIZE),
                       ('ALIGN', (1, 0), (1, -1), 'RIGHT')]
MAJORATION_TABLE_STYLE = [('FONT', (0, 0), (-1, -1), 'EuclidBPBold', FONT_SIZE),
                          ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                          ('ALIGN', (0, 2), (0, 2), 'RIGHT'),
                          ('LINEABOVE', (1, 2), (1, 2), 2, colors.black),
                          ]


def fixed(canvas, doc):
    if not doc.with_bv:
        canvas.translate(0, doc.pagesize[1])
        canvas.rotate(-90)
        canvas.scale(1/SQRT2, 1/SQRT2)
    canvas.saveState()
    canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.png"), doc.leftMargin, doc.pagesize[1]-doc.topMargin-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
    canvas.setFont('EuclidBPBold', FONT_SIZE)
    canvas.drawRightString(doc.pagesize[0]-doc.rightMargin, doc.pagesize[1]-doc.topMargin-FONT_SIZE, u"Lausanne, le "+datetime.date.today().strftime(u'%d.%m.%y'))
    if doc.with_bv and doc.page == 1:
        canvas.drawImage(os.path.join(BASE_DIR, "441_02_ES_LAC_105_quer_CMYK.png"), 0, 0, BV_WIDTH, BV_HEIGHT)
        canvas.saveState()
        # CCP
        canvas.setFont('OCRB', FONT_SIZE)
        canvas.drawString(12*BV_COLUMN, BV_REF_Y - 11*BV_LINE, CCP)
        canvas.drawString(BV_REF_X + 12*BV_COLUMN, BV_REF_Y - 11*BV_LINE, CCP)
        # Lignes de codage
        v, x, c = CCP.split('-')
        codage = u''.join((v, u'0'*(6-len(x)), x, c, u'>'))
        canvas.drawString(BV_REF_X + 46*BV_COLUMN, BV_REF_Y - 21*BV_LINE, codage)
        canvas.drawString(BV_REF_X + 46*BV_COLUMN, BV_REF_Y - 23*BV_LINE, codage)
        canvas.setFont('EuclidBPBold', FONT_SIZE-1)
        # Versé pour
        text_obj = canvas.beginText()
        text_obj.setTextOrigin(BV_COLUMN, BV_REF_Y - 3*BV_LINE)
        text_obj.textLines(doc.therapeute)
        canvas.drawText(text_obj)
        text_obj = canvas.beginText()
        text_obj.setTextOrigin(BV_REF_X+BV_COLUMN, BV_REF_Y - 3*BV_LINE)
        text_obj.textLines(doc.therapeute)
        canvas.drawText(text_obj)
        # Motif
        canvas.drawString(BV_REF_X + 25*BV_COLUMN, BV_REF_Y - 4*BV_LINE, u"Consultation du "+unicode(doc.date))
        # Versé par
        text_obj = canvas.beginText()
        text_obj.setTextOrigin(BV_COLUMN, BV_REF_Y - 16*BV_LINE)
        text_obj.setLeading(1.5*BV_LINE)
        text_obj.textLines(doc.patient)
        canvas.drawText(text_obj)
        text_obj = canvas.beginText()
        text_obj.setTextOrigin(BV_REF_X + 25*BV_COLUMN, BV_REF_Y - 13*BV_LINE)
        text_obj.setLeading(1.5*BV_LINE)
        text_obj.textLines(doc.patient)
        canvas.drawText(text_obj)
        # Le montant
        offset = 1.4
        spacing = 1.16
        canvas.setFont('OCRB', FONT_SIZE)
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
        canvas.setFont('EuclidBPBold', FONT_SIZE-1)
        canvas.restoreState()
    else:
        canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.png"), doc.pagesize[0]+doc.leftMargin, doc.pagesize[1]-doc.topMargin-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
        canvas.drawRightString(2*doc.pagesize[0]-doc.rightMargin, doc.pagesize[1]-doc.topMargin-FONT_SIZE, u"Lausanne, le "+datetime.date.today().strftime('%d.%m.%y'))
    canvas.restoreState()

    def make_italic(canvas, event, label):
        canvas.skew(0, 20)
        canvas.setFont('EuclidBPBold', FONT_SIZE+4)
        canvas.drawString(0, 0, label)

    def make_bold(canvas, event, label):
        canvas.setFont('EuclidBPBold', FONT_SIZE+2)
        canvas.drawString(-0.1, 0, label)
        canvas.drawString(0.1, 0, label)
        canvas.drawString(0, -0.1, label)
        canvas.drawString(0, 0.1, label)

    canvas.make_italic = make_italic
    canvas.make_bold = make_bold


def facture(filename, therapeute, patient, duree, accident, prix_cts, majoration_cts, date, with_bv=False):
    doc = BaseDocTemplate(filename, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    doc.with_bv = with_bv
    doc.prix = (prix_cts + majoration_cts) / 100.
    doc.therapeute = therapeute
    doc.patient = patient
    doc.date = date
    doc.duree = duree
    if with_bv:
        templates = [PageTemplate(id='bv', frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height)], onPage=fixed),
                     PageTemplate(id='copie', frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height)], onPage=fixed),
                     ]
    else:
        templates = [PageTemplate(id='recu',
                                  frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height),
                                          Frame(doc.pagesize[0]+doc.leftMargin, doc.rightMargin, doc.width, doc.height)],
                                  onPage=fixed)]
    doc.addPageTemplates(templates)
    prix = u'%0.2f CHF' % (prix_cts/100.)
    tstyle = DEFAULT_TABLE_STYLE
    data = [[u"Prise en charge ostéopathique %s datée du %s" % (duree, date.strftime(u'%d.%m.%y')), prix], ]
    if majoration_cts:
        tstyle = MAJORATION_TABLE_STYLE
        majoration = u'%0.2f CHF' % (majoration_cts/100.)
        total = u'%0.2f CHF' % ((prix_cts+majoration_cts)/100.)
        data += [[u'Majoration week-end', majoration]]
        data += [[u'TOTAL', total]]
    if accident:
        data += [[u"Raison : accident", ]]
    else:
        data += [[u"Raison : maladie", ]]
    if not with_bv:
        data[-1].append(u"payé")
    fact = [Spacer(0, LOGO_HEIGHT),
            Table([[Preformatted(therapeute, DEFAULT_STYLE), Preformatted(patient, DEFAULT_STYLE)]],
                  colWidths=[doc.width*2/3, doc.width/3],
                  style=[('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]),
            Spacer(0, MARGIN),
            Paragraph(u'', DEFAULT_STYLE),
            Spacer(0, 2*MARGIN),
            Paragraph(u'<onDraw name=make_italic label="FACTURE"/>', FACTURE_STYLE),
            Spacer(0, 1*MARGIN),
            Table(data, colWidths=[doc.width-3*cm, 3*cm], style=tstyle),
            Spacer(0, 2*MARGIN),
            Paragraph(u"Avec mes remerciements.", DEFAULT_STYLE),
            ]
    recu = fact[:]
    recu[3] = Paragraph(u'<onDraw name=make_bold label="COPIE"/>', COPIE_STYLE)
    if with_bv:
        story = fact + [PageBreak()] + recu
    else:
        story = fact + [FrameBreak()] + recu
    doc.build(story)


if __name__ == '__main__':
    filename = os.tempnam()+'.pdf'
    therapeute = u'Tibor Csernay\nDipl. CDS-GDK\n\nAv. de la gare 5\n1003 Lausanne\n021 510 50 50\n021 510 50 49 (N° direct)\n\nRCC U905461'
    patient = u'Jean Dupont\nRoute de Quelque Part\n1234 Perdu'
    duree = u'entre 21 et 30 minutes'
    prix_cts = 10000
    majoration_cts = 2000
    accident = True
    date = datetime.date.today()
    facture(filename, therapeute, patient, duree, accident, prix_cts, majoration_cts, date, with_bv=True)

    import mailcap
    import time
    cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
    os.system(cmd)
    time.sleep(10)
    os.unlink(filename)
