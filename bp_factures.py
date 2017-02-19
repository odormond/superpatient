#! /usr/bin/env python2
# coding:UTF-8

import os
import datetime
from math import sqrt
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Paragraph, Table, Spacer
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
REF_NO_SHIFT = 0
REF_NO_SCALE = 1.0


def ParagraphOrSpacer(text, style):
    if text.strip():
        return Paragraph(text, style)
    return Spacer(0, FONT_SIZE)


def make_styles(font_size):
    DEFAULT_STYLE = ParagraphStyle('default', fontName='EuclidBPBold', fontSize=font_size, leading=font_size*1.2)
    COPIE_STYLE = ParagraphStyle('default', fontName='EuclidBPBold', fontSize=font_size+2)
    FACTURE_STYLE = ParagraphStyle('title', fontName='EuclidBPBold', fontSize=font_size+4)

    NO_TOTAL_TABLE_STYLE = [('FONT', (0, 0), (-1, -1), 'EuclidBPBold', font_size),
                            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                            ]
    TOTAL_TABLE_STYLE = [('FONT', (0, 0), (-1, -1), 'EuclidBPBold', font_size),
                         ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                         ('ALIGN', (1, -2), (1, -2), 'RIGHT'),
                         ('LINEABOVE', (2, -2), (2, -2), 2, colors.black),
                         ]
    return DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, NO_TOTAL_TABLE_STYLE, TOTAL_TABLE_STYLE


def draw_head(canvas, font_size):
    canvas.saveState()
    canvas.drawImage(os.path.join(BASE_DIR, "logo_pog.png"), MARGIN, canvas._pagesize[1]-MARGIN-LOGO_HEIGHT, LOGO_WIDTH, LOGO_HEIGHT)
    canvas.setFont('EuclidBPBold', font_size)
    canvas.drawRightString(canvas._pagesize[0]-MARGIN, canvas._pagesize[1]-MARGIN-font_size, u"Lausanne, le "+datetime.date.today().strftime(u'%d.%m.%y'))
    canvas.restoreState()


def draw_bvr(canvas, prix_cts, address_patient, bv_ref):
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
    montant = '%11.2f' % (prix_cts / 100)
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


def facture_body(consultation, message, style, tstyle):
    prix = u'%0.2f CHF' % (consultation.prix_cts/100.)
    data = [[Paragraph(message, style), None, prix], ]
    if consultation.majoration_cts:
        data += [[consultation.majoration_txt, None, u'%0.2f CHF' % (consultation.majoration_cts/100)]]
    if consultation.frais_admin_cts:
        data += [[consultation.frais_admin_txt, None, u'%0.2f CHF' % (consultation.frais_admin_cts/100)]]
    if consultation.rappel_cts != 0:
        data += [["Frais de rappel", None, u'%0.2f CHF' % (consultation.rappel_cts/100)]]
    if consultation.majoration_cts or consultation.frais_admin_cts or consultation.rappel_cts:
        data += [[None, u'TOTAL', u'%0.2f CHF' % ((consultation.prix_cts + consultation.majoration_cts + consultation.frais_admin_cts + consultation.rappel_cts)/100)]]
    if consultation.MC_accident:
        data += [[u"Raison : accident", None, ]]
    else:
        data += [[u"Raison : maladie", None, ]]
    if not consultation.bv_ref:
        data[-1].append(u"payé par " + consultation.paye_par.lower())
    width = A4[0] - 2*MARGIN
    return [Table(data, colWidths=[width-4.8*cm, 1.5*cm, 3.7*cm], style=tstyle)]


def pvpe_body(consultation, style, tstyle):
    return facture_body(consultation, u"Consultation du %s non annulée 24h à l'avance" % (consultation.date_consult.strftime(DATE_FMT)), style, tstyle)


def consultation_body(consultation, style, tstyle):
    return facture_body(consultation, u"Prise en charge ostéopathique %s datée du %s" % (consultation.prix_txt, consultation.date_consult.strftime(DATE_FMT)), style, tstyle)


# Entry point for generating bills or receipt from a list of consultations
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

        DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, NO_TOTAL_TABLE_STYLE, TOTAL_TABLE_STYLE = make_styles(font_size)
        main = addresses(cursor, consultation, DEFAULT_STYLE)
        main.append(Spacer(0, MARGIN))
        main.append(Paragraph(u'', DEFAULT_STYLE))  # Will be replaced by COPIE in the copy
        main.append(Spacer(0, 1*MARGIN))
        if consultation.rappel_cts:
            main.append(Paragraph(u'<onDraw name=make_italic label="RAPPEL"/>', FACTURE_STYLE))
        else:
            main.append(Paragraph(u'<onDraw name=make_italic label="FACTURE"/>', FACTURE_STYLE))
        main.append(Spacer(0, 1*MARGIN))
        if consultation.majoration_cts or consultation.frais_admin_cts or consultation.rappel_cts:
            tstyle = TOTAL_TABLE_STYLE
        else:
            tstyle = NO_TOTAL_TABLE_STYLE
        if consultation.paye_par == u'PVPE':
            main += pvpe_body(consultation, DEFAULT_STYLE, tstyle)
        else:
            main += consultation_body(consultation, DEFAULT_STYLE, tstyle)
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
            patient = consultation.patient
            if len(u' '.join((patient.prenom, patient.nom))) < 25:
                identite = [u' '.join((patient.prenom, patient.nom))]
            else:
                identite = [patient.prenom, patient.nom]
            address_patient = u'\n'.join(identite + [patient.adresse])
            draw_bvr(canvas, consultation.prix_cts+consultation.majoration_cts+consultation.frais_admin_cts+consultation.rappel_cts, address_patient, consultation.bv_ref)
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


# Entry point for generating manual bills
def manuals(filename, data):
    canvas = Canvas(filename, pagesize=A4)
    width, height = A4
    for therapeute, adresse, motif, prix, remarque, bv_ref in data:
        def make_italic(canvas, event, label):
            canvas.skew(0, 20)
            canvas.setFont('EuclidBPBold', FONT_SIZE_BV+4)
            canvas.drawString(0, 0, label)

        def make_bold(canvas, event, label):
            canvas.setFont('EuclidBPBold', FONT_SIZE_BV+2)
            canvas.drawString(-0.1, 0, label)
            canvas.drawString(0.1, 0, label)
            canvas.drawString(0, -0.1, label)
            canvas.drawString(0, 0.1, label)

        canvas.make_italic = make_italic
        canvas.make_bold = make_bold

        DEFAULT_STYLE, COPIE_STYLE, FACTURE_STYLE, NO_TOTAL_TABLE_STYLE, TOTAL_TABLE_STYLE = make_styles(FONT_SIZE_BV)
        tstyle = NO_TOTAL_TABLE_STYLE
        story = [Table([[[ParagraphOrSpacer(line, DEFAULT_STYLE) for line in therapeute.splitlines()],
                         [ParagraphOrSpacer(line, DEFAULT_STYLE) for line in adresse.splitlines()]]],
                       colWidths=[(width-2*MARGIN)*2/3, (width-2*MARGIN)/3],
                       style=[('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]),
                 Spacer(0, MARGIN),
                 Paragraph(u'', DEFAULT_STYLE),
                 Spacer(0, 1*MARGIN),
                 Paragraph(u'<onDraw name=make_italic label="FACTURE"/>', FACTURE_STYLE),
                 Spacer(0, 1*MARGIN),
                 Table([[Paragraph(motif, DEFAULT_STYLE), u'%0.2f CHF' % prix]], colWidths=[width-2*MARGIN-6*cm, 5*cm], style=tstyle),
                 ]
        if remarque:
            story.append(Spacer(0, 1*MARGIN))
            story.append(Table([[Paragraph(u"Remarque:", DEFAULT_STYLE), Paragraph(remarque, DEFAULT_STYLE)]],
                               colWidths=[3*cm, width-2*MARGIN-3*cm],
                               style=[('ALIGN', (0, 0), (1, 0), 'LEFT')]))
        story += [Spacer(0, 1.5*MARGIN),
                  Paragraph(u"Avec mes remerciements.", DEFAULT_STYLE),
                  ]
        canvas.saveState()
        draw_head(canvas, FONT_SIZE_BV)
        draw_bvr(canvas, int(prix*100+0.5), adresse, bv_ref)
        frame = Frame(MARGIN, MARGIN, width-2*MARGIN, height-2*MARGIN-LOGO_HEIGHT)
        frame.addFromList(story, canvas)
        canvas.restoreState()
        canvas.showPage()
        # Add an empty page
        canvas.showPage()
    canvas.save()


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
    c2 = bp_model.Consultation(id=1, patient=patient, therapeute=patient.therapeute, date_consult=datetime.date.today(), prix_cts=10000, paye_par=u'PVPE', bv_ref='012345678901234567890123458', majoration_cts=0, rappel_cts=300)
    c3 = bp_model.Consultation(id=1, patient=patient, therapeute=patient.therapeute, date_consult=datetime.date.today(), prix_cts=10000, paye_par=u'Carte', majoration_cts=300, rappel_cts=0)
    consultations(sys.argv[1], cursor, [c1, c2, c3])
