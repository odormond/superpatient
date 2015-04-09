#! /usr/bin/env python
# coding:UTF-8

import os
import datetime
from math import sqrt
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Preformatted, Table, Spacer, PageBreak, FrameBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

SQRT2 = sqrt(2)

BASE_DIR = os.path.join(os.path.dirname(__file__), 'pdfs')
pdfmetrics.registerFont(TTFont('EuclidBPBold', os.path.join(BASE_DIR, 'Euclid_BP_Bold.ttf')))

MARGIN = 1*cm
LOGO_WIDTH = 5.6*cm
LOGO_HEIGHT = LOGO_WIDTH*469./676
BV_WIDTH = 210*mm
BV_HEIGHT = 106*mm
FONT_SIZE = 10

DEFAULT_STYLE = ParagraphStyle('default', fontName='EuclidBPBold', fontSize=FONT_SIZE)
COPIE_STYLE = ParagraphStyle('default', fontName='EuclidBPBold', fontSize=FONT_SIZE+2)
FACTURE_STYLE = ParagraphStyle('title', fontName='EuclidBPBold', fontSize=FONT_SIZE+4)


def fixed(canvas, doc):
    if not doc.with_bv:
        canvas.translate(0, doc.pagesize[1])
        canvas.rotate(-90)
        canvas.scale(1/SQRT2, 1/SQRT2)
    canvas.saveState()
    canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.png"), doc.leftMargin, doc.pagesize[1]-doc.topMargin-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
    canvas.setFont('EuclidBPBold', FONT_SIZE)
    canvas.drawRightString(doc.pagesize[0]-doc.rightMargin, doc.pagesize[1]-doc.topMargin-FONT_SIZE, "Lausanne, le "+datetime.date.today().strftime('%d.%m.%y'))
    if doc.with_bv and doc.page == 1:
        canvas.drawImage(os.path.join(BASE_DIR, "441_02_ES_LAC_105_quer_CMYK.png"), 0, 0, BV_WIDTH, BV_HEIGHT)
    else:
        canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.png"), doc.pagesize[0]+doc.leftMargin, doc.pagesize[1]-doc.topMargin-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
        canvas.drawRightString(2*doc.pagesize[0]-doc.rightMargin, doc.pagesize[1]-doc.topMargin-FONT_SIZE, "Lausanne, le "+datetime.date.today().strftime('%d.%m.%y'))
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


def facture(filename, therapeute, patient, duree, prix, date, with_bv=False):
    doc = BaseDocTemplate(filename, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    doc.with_bv = with_bv
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
    fact = [Spacer(0, LOGO_HEIGHT),
            Table([[Preformatted(therapeute, DEFAULT_STYLE), Preformatted(patient, DEFAULT_STYLE)]],
                  colWidths=[doc.width*2/3, doc.width/3],
                  style=[('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]),
            Spacer(0, MARGIN),
            Paragraph('', DEFAULT_STYLE),
            Spacer(0, 2*MARGIN),
            Paragraph('<onDraw name=make_italic label="FACTURE"/>', FACTURE_STYLE),
            Spacer(0, 1*MARGIN),
            Table([(Paragraph("Prise en charge ostéopathique %s datée du %s" % (duree, date.strftime('%d.%m.%y')), DEFAULT_STYLE), Paragraph(prix, DEFAULT_STYLE)),
                   (Paragraph("Raison&nbsp;: maladie", DEFAULT_STYLE), Paragraph("payé", DEFAULT_STYLE))],
                  colWidths=[doc.width-3*cm, 3*cm]),
            Spacer(0, 3*MARGIN),
            Paragraph("Avec mes remerciements.", DEFAULT_STYLE),
            ]
    recu = fact[:]
    recu[3] = Paragraph('<onDraw name=make_bold label="COPIE"/>', COPIE_STYLE)
    if with_bv:
        story = fact + [PageBreak()] + recu
    else:
        story = fact + [FrameBreak()] + recu
    doc.build(story)


if __name__ == '__main__':
    filename = os.tempnam()+'.pdf'
    therapeute = 'Tibor Csernay\nDipl. CDS-GDK\n\nAv. de la gare 5\n1003 Lausanne\n021 510 50 50\n021 510 50 49 (N° direct)\n\nRCC U905461'
    patient = 'Jean Dupont\nRoute de Quelque Part\n1234 Perdu'
    duree = 'entre 21 et 30 minutes'
    prix = '100.00 CHF'
    date = datetime.date.today()
    facture(filename, therapeute, patient, duree, prix, date, with_bv=True)
    #facture(filename, therapeute, patient, duree, prix, date, with_bv=False)

    import mailcap
    import time
    cmd, cap = mailcap.findmatch(mailcap.getcaps(), 'application/pdf', 'view', filename)
    os.system(cmd)
    time.sleep(10)
    os.unlink(filename)
