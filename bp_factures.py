#! /usr/bin/env python2
# coding:UTF-8

import os
import datetime
from math import sqrt
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, Spacer, PageBreak, FrameBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm, inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from bp_custo import bvr, DATE_FMT, labels_text
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

LEFT_TEXT_SHIFT = 8
LEFT_TEXT_SCALE = 0.92
MIDDLE_TEXT_SHIFT = 0
MIDDLE_TEXT_SCALE = 1
RIGHT_TEXT_SHIFT = 0
RIGHT_TEXT_SCALE = 1
REF_NO_SHIFT = -4
REF_NO_SCALE = 1.0


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
    MAJORATION_OU_RAPPEL_TABLE_STYLE = [('FONT', (0, 0), (-1, -1), 'EuclidBPBold', font_size),
                                        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                                        ('ALIGN', (1, 2), (1, 2), 'RIGHT'),
                                        ('LINEABOVE', (2, 2), (2, 2), 2, colors.black),
                                        ]
    MAJORATION_ET_RAPPEL_TABLE_STYLE = [('FONT', (0, 0), (-1, -1), 'EuclidBPBold', font_size),
                                        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                                        ('ALIGN', (1, 3), (1, 3), 'RIGHT'),
                                        ('LINEABOVE', (2, 3), (2, 3), 2, colors.black),
                                        ]
    return DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_OU_RAPPEL_TABLE_STYLE, MAJORATION_ET_RAPPEL_TABLE_STYLE


def draw_head(canvas, font_size):
    canvas.saveState()
    canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.png"), MARGIN, canvas._pagesize[1]-MARGIN-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
    canvas.setFont('EuclidBPBold', font_size)
    canvas.drawRightString(canvas._pagesize[0]-MARGIN, canvas._pagesize[1]-MARGIN-font_size, u"Lausanne, le "+datetime.date.today().strftime(u'%d.%m.%y'))
    canvas.restoreState()


def draw_bvr(canvas, cursor, consultation):
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
    prix = u'01%010d' % (consultation.prix_cts + consultation.majoration_cts + consultation.rappel_cts)
    codage = u'%s%d>%s+ %s' % (prix, bvr_checksum(prix), consultation.bv_ref, codage)
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
    patient = consultation.patient
    if len(u' '.join((patient.prenom, patient.nom))) < 25:
        identite = [u' '.join((patient.prenom, patient.nom))]
    else:
        identite = [patient.prenom, patient.nom]
    address_patient_bv = u'\n'.join(identite + [patient.adresse])
    ref = list(consultation.bv_ref)
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
    text_obj.textLines(address_patient_bv)
    canvas.drawText(text_obj)
    text_obj = canvas.beginText()
    text_obj.setTextTransform(RIGHT_TEXT_SCALE, 0, 0, 1, BV_REF_X + 25*BV_COLUMN + RIGHT_TEXT_SHIFT, BV_REF_Y - 13*BV_LINE)
    text_obj.setLeading(1.5*BV_LINE)
    text_obj.textLines(address_patient_bv)
    canvas.drawText(text_obj)
    # Le montant
    offset = 0.5  # 1.3
    spacing = 1.0
    canvas.setFont('OCRB', 12)
    montant = '%11.2f' % ((consultation.prix_cts + consultation.majoration_cts + consultation.rappel_cts) / 100)
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


def addresses(cursor, consultation, style):
    cursor.execute("""SELECT entete FROM therapeutes WHERE therapeute = %s""", [consultation.therapeute])
    entete_therapeute, = cursor.fetchone()
    address_therapeute = entete_therapeute + u'\n\n' + labels_text.adresse_pog
    therapeute = [ParagraphOrSpacer(line, style) for line in address_therapeute.splitlines()]

    patient = consultation.patient
    titre = {u'Mr': u'Monsieur', u'Mme': u'Madame', u'Enfant': u'Aux parents de'}[patient.sex]
    if len(u' '.join((patient.prenom, patient.nom))) < 25:
        identite = [u' '.join((patient.prenom, patient.nom))]
    else:
        identite = [patient.prenom, patient.nom]
    address_patient = u'\n'.join([titre] + identite + [patient.adresse, "", patient.date_naiss.strftime(DATE_FMT)])
    patient = [ParagraphOrSpacer(line, style) for line in address_patient.splitlines()]

    width = A4[0] - 2*MARGIN
    return [Table([[therapeute, patient]],
                  colWidths=[width*2/3, width/3],
                  style=[('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]),
            ]


def pvpe_body(cursor, consultation, style, tstyle):
    prix = u'%0.2f CHF' % (consultation.prix_cts/100.)
    # XXX Adapt text
    data = [[Paragraph(u"Consultation non décommandée datée du %s" % (consultation.date_consult.strftime(DATE_FMT)), style), None, prix], ]
    if consultation.majoration_cts:
        cursor.execute("""SELECT description FROM majorations WHERE prix_cts=%s""", [consultation.majoration_cts])
        description_majoration, = cursor.fetchone()
        data += [[description_majoration, None, u'%0.2f CHF' % (consultation.majoration_cts/100)]]
    if consultation.rappel_cts != 0:
        data += [["Frais de rappel", None, u'%0.2f CHF' % (consultation.rappel_cts/100)]]
    if consultation.majoration_cts or consultation.rappel_cts:
        data += [[None, u'TOTAL', u'%0.2f CHF' % ((consultation.prix_cts + consultation.majoration_cts + consultation.rappel_cts)/100)]]
    if consultation.MC_accident:
        data += [[u"Raison : accident", None, ]]
    else:
        data += [[u"Raison : maladie", None, ]]
    if not consultation.bv_ref:
        data[-1].append(u"payé")
    width = A4[0] - 2*MARGIN
    return [Table(data, colWidths=[width-5*cm, 1.5*cm, 3.5*cm], style=tstyle)]


def consultation_body(cursor, consultation, style, tstyle):
    prix = u'%0.2f CHF' % (consultation.prix_cts/100.)
    cursor.execute("""SELECT description FROM tarifs WHERE prix_cts=%s""", [consultation.prix_cts])
    duree, = cursor.fetchone()
    data = [[Paragraph(u"Prise en charge ostéopathique %s datée du %s" % (duree, consultation.date_consult.strftime(DATE_FMT)), style), None, prix], ]
    if consultation.majoration_cts:
        cursor.execute("""SELECT description FROM majorations WHERE prix_cts=%s""", [consultation.majoration_cts])
        description_majoration, = cursor.fetchone()
        data += [[description_majoration, None, u'%0.2f CHF' % (consultation.majoration_cts/100)]]
    if consultation.rappel_cts != 0:
        data += [["Frais de rappel", None, u'%0.2f CHF' % (consultation.rappel_cts/100)]]
    if consultation.majoration_cts or consultation.rappel_cts:
        data += [[None, u'TOTAL', u'%0.2f CHF' % ((consultation.prix_cts + consultation.majoration_cts + consultation.rappel_cts)/100)]]
    if consultation.MC_accident:
        data += [[u"Raison : accident", None, ]]
    else:
        data += [[u"Raison : maladie", None, ]]
    if not consultation.bv_ref:
        data[-1].append(u"payé")
    width = A4[0] - 2*MARGIN
    return [Table(data, colWidths=[width-5*cm, 1.5*cm, 3.5*cm], style=tstyle)]


# Entry point for generating bills or receipt
def consultations(filename, cursor, consultations):
    canvas = Canvas(filename, pagesize=A4)
    width, height = A4
    for consultation in consultations:
        font_size = FONT_SIZE_BV if consultation.bv_ref else FONT_SIZE

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

        DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_OU_RAPPEL_TABLE_STYLE, MAJORATION_ET_RAPPEL_TABLE_STYLE = make_styles(font_size)
        main = addresses(cursor, consultation, DEFAULT_STYLE)
        main.append(Spacer(0, MARGIN))
        main.append(Paragraph(u'', DEFAULT_STYLE))  # Will be replaced by COPIE in the copy
        main.append(Spacer(0, 1*MARGIN))
        if consultation.rappel_cts:
            main.append(Paragraph(u'<onDraw name=make_italic label="RAPPEL"/>', FACTURE_STYLE))
        else:
            main.append(Paragraph(u'<onDraw name=make_italic label="FACTURE"/>', FACTURE_STYLE))
        main.append(Spacer(0, 1*MARGIN))
        if consultation.majoration_cts and consultation.rappel_cts:
            tstyle = MAJORATION_ET_RAPPEL_TABLE_STYLE
        elif consultation.majoration_cts or consultation.rappel_cts:
            tstyle = MAJORATION_OU_RAPPEL_TABLE_STYLE
        else:
            tstyle = DEFAULT_TABLE_STYLE
        if consultation.paye_par == u'PVPE':
            main += pvpe_body(cursor, consultation, DEFAULT_STYLE, tstyle)
        else:
            main += consultation_body(cursor, consultation, DEFAULT_STYLE, tstyle)
        main.append(Spacer(0, 1*MARGIN))
        main.append(Paragraph(u"Avec mes remerciements.", DEFAULT_STYLE))
        copy = main[:]
        copy[2] = Paragraph(u'<onDraw name=make_bold label="COPIE"/>', COPIE_STYLE)

        canvas.saveState()
        if consultation.paye_par not in (u'BVR', u'PVPE'):
            canvas.translate(0, canvas._pagesize[1])
            canvas.rotate(-90)
            canvas.scale(1/SQRT2, 1/SQRT2)
        draw_head(canvas, font_size)
        frame = Frame(MARGIN, MARGIN, width-2*MARGIN, height-2*MARGIN-LOGO_HEIGHT)
        frame.addFromList(main, canvas)
        if consultation.paye_par in (u'BVR', u'PVPE'):
            draw_bvr(canvas, cursor, consultation)
        canvas.restoreState()
        if consultation.paye_par in (u'BVR', u'PVPE'):
            canvas.showPage()
        if consultation.rappel_cts == 0:
            canvas.saveState()
            if consultation.paye_par not in (u'BVR', u'PVPE'):
                canvas.translate(0, canvas._pagesize[1]/2)
                canvas.rotate(-90)
                canvas.scale(1/SQRT2, 1/SQRT2)
            draw_head(canvas, font_size)
            frame = Frame(MARGIN, MARGIN, width-2*MARGIN, height-2*MARGIN-LOGO_HEIGHT)
            frame.addFromList(copy, canvas)
            canvas.restoreState()
        canvas.showPage()
    canvas.save()


def fixed(canvas, doc):
    if not doc.adresse_bv:
        canvas.translate(0, doc.pagesize[1])
        canvas.rotate(-90)
        canvas.scale(1/SQRT2, 1/SQRT2)
        font_size = FONT_SIZE
    else:
        font_size = FONT_SIZE_BV

    DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_OU_RAPPEL_TABLE_STYLE, MAJORATION_ET_RAPPEL_TABLE_STYLE = make_styles(font_size)

    canvas.saveState()
    canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.png"), doc.leftMargin, doc.pagesize[1]-doc.topMargin-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
    canvas.setFont('EuclidBPBold', font_size)
    canvas.drawRightString(doc.pagesize[0]-doc.rightMargin, doc.pagesize[1]-doc.topMargin-font_size, u"Lausanne, le "+datetime.date.today().strftime(u'%d.%m.%y'))
    if doc.adresse_bv and doc.page == 1:
        if PRINT_BV_BG:
            if doc.bv_ref:
                canvas.drawImage(os.path.join(BASE_DIR, "442_05_LAC_609_quer_Bank_CMYK.png"), 0, 0, BV_WIDTH, BV_HEIGHT)
            else:
                canvas.drawImage(os.path.join(BASE_DIR, "441_02_ES_LAC_105_quer_CMYK.png"), 0, 0, BV_WIDTH, BV_HEIGHT)
        canvas.saveState()
        # CCP
        canvas.setFont('OCRB', 12)
        canvas.drawString(12*BV_COLUMN, BV_REF_Y - 11*BV_LINE, bvr.CCP)
        canvas.drawString(BV_REF_X + 12*BV_COLUMN, BV_REF_Y - 11*BV_LINE, bvr.CCP)
        # Lignes de codage
        v, x, c = bvr.CCP.split('-')
        codage = u''.join((v, u'0'*(6-len(x)), x, c, u'>'))
        if doc.bv_ref:
            prix = u'01%010d' % (doc.prix * 100)
            codage = u'%s%d>%s+ %s' % (prix, bvr_checksum(prix), doc.bv_ref, codage)
            text_obj = canvas.beginText()
            text_obj.setTextTransform(REF_NO_SCALE, 0, 0, 1, BV_REF_X + 3*BV_COLUMN + REF_NO_SHIFT, BV_REF_Y - 21*BV_LINE)
            text_obj.textLines(codage)
            canvas.drawText(text_obj)
        else:
            canvas.drawString(BV_REF_X + 46*BV_COLUMN, BV_REF_Y - 21*BV_LINE, codage)
            canvas.drawString(BV_REF_X + 46*BV_COLUMN, BV_REF_Y - 23*BV_LINE, codage)
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
        text_obj.textLines(doc.adresse_bv)
        canvas.drawText(text_obj)
        text_obj = canvas.beginText()
        text_obj.setTextTransform(RIGHT_TEXT_SCALE, 0, 0, 1, BV_REF_X + 25*BV_COLUMN + RIGHT_TEXT_SHIFT, BV_REF_Y - 13*BV_LINE)
        text_obj.setLeading(1.5*BV_LINE)
        text_obj.textLines(doc.adresse_bv)
        canvas.drawText(text_obj)
        # Le montant
        offset = 0.5  # 1.3
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


def facture(filename, therapeute, patient, duree, accident, prix_cts, description_majoration, majoration_cts, date, adresse_bv=None, bv_ref=None, rappel_cts=0):
    doc = BaseDocTemplate(filename, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    doc.prix = (prix_cts + majoration_cts + rappel_cts) / 100.
    doc.therapeute = therapeute
    doc.patient = patient
    doc.adresse_bv = adresse_bv
    doc.bv_ref = bv_ref
    doc.date = date
    doc.duree = duree
    doc.rappel_cts = rappel_cts
    if adresse_bv:
        templates = [PageTemplate(id='bv', frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height)], onPage=fixed)]
        if rappel_cts == 0:
            templates.append(PageTemplate(id='copie', frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height)], onPage=fixed))
        DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_OU_RAPPEL_TABLE_STYLE, MAJORATION_ET_RAPPEL_TABLE_STYLE = make_styles(FONT_SIZE_BV)
    else:
        templates = [PageTemplate(id='recu',
                                  frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height),
                                          Frame(doc.pagesize[0]+doc.leftMargin, doc.rightMargin, doc.width, doc.height)],
                                  onPage=fixed)]
        DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_OU_RAPPEL_TABLE_STYLE, MAJORATION_ET_RAPPEL_TABLE_STYLE = make_styles(FONT_SIZE)

    doc.addPageTemplates(templates)
    prix = u'%0.2f CHF' % (prix_cts/100.)
    tstyle = DEFAULT_TABLE_STYLE
    data = [[Paragraph(u"Prise en charge ostéopathique %s datée du %s" % (duree, date.strftime(DATE_FMT)), DEFAULT_STYLE), None, prix], ]
    if majoration_cts:
        data += [[description_majoration, None, u'%0.2f CHF' % (majoration_cts/100.)]]
    if rappel_cts != 0:
        data += [["Frais de rappel", None, u'%0.2f CHF' % (rappel_cts/100.)]]
    if majoration_cts or rappel_cts:
        tstyle = MAJORATION_OU_RAPPEL_TABLE_STYLE
        if majoration_cts and rappel_cts:
            tstyle = MAJORATION_ET_RAPPEL_TABLE_STYLE
        data += [[None, u'TOTAL', u'%0.2f CHF' % doc.prix]]
    if accident:
        data += [[u"Raison : accident", None, ]]
    else:
        data += [[u"Raison : maladie", None, ]]
    if not adresse_bv:
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
            ]
    if rappel_cts:
        fact.append(Paragraph(u'<onDraw name=make_italic label="RAPPEL"/>', FACTURE_STYLE))
    else:
        fact.append(Paragraph(u'<onDraw name=make_italic label="FACTURE"/>', FACTURE_STYLE))
    fact += [Spacer(0, 1*MARGIN),
             Table(data, colWidths=[doc.width-5*cm, 1.5*cm, 3.5*cm], style=tstyle),
             Spacer(0, 1*MARGIN),
             Paragraph(u"Avec mes remerciements.", DEFAULT_STYLE),
             ]
    recu = fact[:]
    recu[3] = Paragraph(u'<onDraw name=make_bold label="COPIE"/>', COPIE_STYLE)
    if adresse_bv:
        if rappel_cts == 0:
            story = fact + [PageBreak()] + recu
        else:
            story = fact
    else:
        story = fact + [FrameBreak()] + recu
    doc.build(story)


def facture_manuelle(filename, therapeute, adresse, motif, prix, remarque, bv_ref):
    doc = BaseDocTemplate(filename, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    doc.prix = prix
    doc.therapeute = therapeute
    doc.adresse_bv = adresse
    doc.bv_ref = bv_ref
    templates = [PageTemplate(id='bv', frames=[Frame(doc.leftMargin, doc.rightMargin, doc.width, doc.height)], onPage=fixed)]
    DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, DEFAULT_TABLE_STYLE, MAJORATION_OU_RAPPEL_TABLE_STYLE, MAJORATION_ET_RAPPEL_TABLE_STYLE = make_styles(FONT_SIZE_BV)

    doc.addPageTemplates(templates)
    prix = u'%0.2f CHF' % doc.prix
    tstyle = DEFAULT_TABLE_STYLE
    therapeute = [ParagraphOrSpacer(line, DEFAULT_STYLE) for line in therapeute.splitlines()]
    adresse = [ParagraphOrSpacer(line, DEFAULT_STYLE) for line in adresse.splitlines()]
    story = [Spacer(0, LOGO_HEIGHT),
             Table([[therapeute, adresse]],
                   colWidths=[doc.width*2/3, doc.width/3],
                   style=[('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]),
             Spacer(0, MARGIN),
             Paragraph(u'', DEFAULT_STYLE),
             Spacer(0, 1*MARGIN),
             Paragraph(u'<onDraw name=make_italic label="FACTURE"/>', FACTURE_STYLE),
             Spacer(0, 1*MARGIN),
             Table([[Paragraph(motif, DEFAULT_STYLE), prix]], colWidths=[doc.width-6*cm, 5*cm], style=tstyle),
             ]
    if remarque:
        story.append(Spacer(0, 1*MARGIN))
        story.append(Table([[Paragraph(u"Remarque:", DEFAULT_STYLE), Paragraph(remarque, DEFAULT_STYLE)]],
                           colWidths=[3*cm, doc.width - 3*cm],
                           style=[('ALIGN', (0, 0), (1, 0), 'LEFT')]))
    story += [Spacer(0, 1.5*MARGIN),
              Paragraph(u"Avec mes remerciements.", DEFAULT_STYLE),
              ]
    doc.build(story)


if __name__ == '__main__':
    import MySQLdb
    import bp_connect
    import bp_model
    import sys
    db = MySQLdb.connect(host=bp_connect.serveur, user=bp_connect.identifiant, passwd=bp_connect.secret, db=bp_connect.base, charset='latin1')
    cursor = db.cursor()
    patient = bp_model.Patient.load(cursor, 1)
    print patient.__dict__
    c1 = bp_model.Consultation(id=1, patient=patient, therapeute=patient.therapeute, date_consult=datetime.date.today(), prix_cts=10000, paye_par=u'BVR', bv_ref='012345678901234567890123458', majoration_cts=0, rappel_cts=0)
    c2 = bp_model.Consultation(id=1, patient=patient,  therapeute=patient.therapeute, date_consult=datetime.date.today(), prix_cts=10000, paye_par=u'PVPE', bv_ref='012345678901234567890123458', majoration_cts=0, rappel_cts=300)
    c3 = bp_model.Consultation(id=1, patient=patient,  therapeute=patient.therapeute, date_consult=datetime.date.today(), prix_cts=10000, paye_par=u'Carte', majoration_cts=300, rappel_cts=0)
    consultations(sys.argv[1], cursor, [c1, c2, c3])
