from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, PageBreak
from reportlab.platypus.flowables import CallerMacro
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

from . import gen_title
from .customization import DATE_FMT, labels_text
from .custom_bill import draw_bvr


LEFT_MARGIN = 1.7*cm
RIGHT_MARGIN = 1.2*cm
TOP_MARGIN = 1*cm
BOTTOM_MARGIN = 2.5*cm
DEFAULT_STYLE = ParagraphStyle('default')
TITLE_STYLE = ParagraphStyle('title', DEFAULT_STYLE, fontSize=18, fontName=DEFAULT_STYLE.fontName+'-Bold', leading=22)
BASE_TSTYLE = [('TOPPADDING', (0, 0), (-1, -1), 0),
               ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
               ('LEFTPADDING', (0, 0), (-1, -1), 2),
               ('RIGHTPADDING', (0, 0), (-1, -1), 0),
               ]
BOXED_TSTYLE = BASE_TSTYLE + [('FONT', (0, 0), (0, -1), TITLE_STYLE.fontName, 8, 12),
                              ('FONT', (1, 0), (-1, -1), DEFAULT_STYLE.fontName, 8, 12),
                              ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
                              ]
THERAPEUTE_TSTYLE = BOXED_TSTYLE + [('SPAN', (0, 1), (0, 2)),
                                    ('SPAN', (0, 3), (0, 4)),
                                    ('SPAN', (1, 0), (-1, 0)),
                                    ('LEADING', (0, 1), (0, -1), 8),
                                    ('VALIGN', (0, 1), (0, -1), 'TOP'),
                                    ]
PATIENT_TSTYLE = BOXED_TSTYLE + [('SPAN', (3, 0), (4, 16)),
                                 ('VALIGN', (3, 0), (3, 0), 'MIDDLE'),
                                 ]
POSITION_TSTYLE = BASE_TSTYLE + [('FONT', (0, 0), (-1, 0), DEFAULT_STYLE.fontName, 7, 12),
                                 ('FONT', (0, 1), (-1, -2), DEFAULT_STYLE.fontName, 8, 12),
                                 ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                                 ]
TOTAL_TSTYLE = POSITION_TSTYLE + [('FONT', (0, -1), (-1, -1), TITLE_STYLE.fontName, 8, 12),
                                  ('SPAN', (4, -1), (6, -1)),
                                  ]


def therapeute(bill):
    name = bill.author_firstname + ' ' + bill.author_lastname
    pog, address, zip_city, web, phone = labels_text.adresse_pog.splitlines()
    data = [
        ["Document", "{} {}".format(bill.id, bill.timestamp)],
        ["Auteur\nfacture", "N° GLN", "", name, web],
        ["", "N° RCC", bill.author_rcc, address, zip_city, "Tél: " + phone],
        ["Four. de\nprestations", "N° GLN", "", name, web],
        ["", "N° RCC", bill.author_rcc, address, zip_city, "Tél: " + phone],
    ]
    return Table(data, colWidths=[2*cm, 1.5*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=THERAPEUTE_TSTYLE)


def patient(bill):
    titre = gen_title(bill.sex, bill.birthdate)
    data = [
        ["Patient:", "Nom", bill.lastname, "{}\n{} {}\n{}\n{} {}".format(titre, bill.firstname, bill.lastname, bill.street, bill.zip, bill.city)],
        ["", "Prénom", bill.firstname],
        ["", "Rue", bill.street],
        ["", "NPA", bill.zip],
        ["", "Localité", bill.city],
        ["", "Date de naissance", bill.birthdate.strftime(DATE_FMT)],
        ["", "Loi", "LCA"],
        ["", "Sexe", bill.sex],
        ["", "Date cas", ""],
        ["", "N° patient", bill.id_patient],
        ["", "N° AVS", ""],
        ["", "N° CADA", ""],
        ["", "N° assuré", ""],
        ["", "Canton", bill.canton],
        ["", "Copie", "Oui" if bill.copy else "Non", "Date/N° GaPrCh"],
        ["", "Type de remb.", "TG", "Date/N° de facture"],
        ["", "N° contrat", "", "Date/N° de rappel"],
        ["", "Traitement", bill.treatment_period, "Motif traitement", bill.treatment_reason],
        ["", "N°/Nom entreprise", "Permanence ostéopathique de la Gare (POG) Sàrl"],
        ["", "Rôle/Localité", labels_text.bill_role_locality],
    ]
    return Table(data, colWidths=[2*cm, 2.5*cm, 6.5*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=PATIENT_TSTYLE)


def mandant(bill):
    #data = [["Mandataire", "GLN", "", "RCC", "", "Nom", ""]]
    data = [["Mandataire", bill.mandant]]
    return Table(data, colWidths=[2*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=BOXED_TSTYLE)


def diagnostic(bill):
    data = [["Diagnostic", bill.diagnostic.replace('\n', ' ')]]
    return Table(data, colWidths=[2*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=BOXED_TSTYLE)


def therapy(bill):
    data = [["Thérapie", "Thérapie individuelle", "Valeur du point (VPt)", "1.0", "TVA", "Non"]]
    return Table(data, colWidths=[2*cm, '*', '*', 1*cm, 1*cm, 1.5*cm], rowHeights=[13] + [11]*(len(data)-1), style=BOXED_TSTYLE)


def comment(bill):
    data = [["Commentaire", bill.comment]]
    return Table(data, colWidths=[2*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=BOXED_TSTYLE)


def positions(bill):
    VAT = "0.0%"
    data = [["Date", "Tarif", "Code tarifaire", "Quan.", "Prix", "VPt", "TVA", "Montant"]]
    for position in bill.positions:
        data += [[position.position_date.strftime(DATE_FMT), 590, position.tarif_code, position.quantity, '%0.2f' % (position.price_cts / 100), 1.0, VAT, '%0.2f' % (position.quantity * position.price_cts / 100)],
                 ["", "", position.tarif_description]]
    for reminder in bill.reminders:
        data += [[reminder.reminder_date.strftime(DATE_FMT), 590, 999, 1, '%0.2f' % (reminder.amount_cts / 100), 1.0, VAT, '%0.2f' % (reminder.amount_cts / 100)],
                 ["", "", "Frais de rappels"]]
    tstyle = (POSITION_TSTYLE +
              [('FONT', (0, row), (-1, row), TITLE_STYLE.fontName, 6) for row in range(2, len(data), 2)] +
              [('SPAN', (2, row), (-1, row)) for row in range(2, len(data), 2)])
    total = [["", "", "", "", "Montant dû", "", "", '%0.2f' % (bill.total_cts / 100)]]
    return [Table(data, colWidths=[2*cm, 1*cm, '*', 1*cm, 1*cm, 1*cm, 1*cm, 1.5*cm], style=tstyle),
            Spacer(0, 1*cm),
            Table(total, colWidths=[2*cm, 1*cm, '*', 1*cm, 1*cm, 1*cm, 1*cm, 1.5*cm], style=TOTAL_TSTYLE),
            ]


def consultations(filename, bills):
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=LEFT_MARGIN, topMargin=TOP_MARGIN, rightMargin=RIGHT_MARGIN, bottomMargin=BOTTOM_MARGIN)
    story = []
    bills = bills[:]
    while bills:
        bill = bills.pop()
        page = [Paragraph("Facture", TITLE_STYLE),
                therapeute(bill),
                patient(bill),
                mandant(bill),
                diagnostic(bill),
                therapy(bill),
                comment(bill),
                ]
        page += positions(bill)
        if bill.payment_method in ('BVR', 'PVPE'):
            if len(' '.join((bill.firstname, bill.lastname))) < 25:
                identite = [' '.join((bill.firstname, bill.lastname))]
            else:
                identite = [bill.firstname, bill.lastname]
            address_patient = '\n'.join(identite + [bill.street, bill.zip + ' ' + bill.city])

            def render_bvr(flowable):
                canvas = flowable.canv
                x = flowable._frame._x + flowable._frame._leftExtraIndent
                y = flowable._frame._y
                canvas.translate(-x, -y)
                draw_bvr(canvas, bill.total_cts, address_patient, bill.bv_ref)
            page += [CallerMacro(render_bvr)]
        story += page
        if bill.copy:
            story.append(PageBreak())
            story.append(Paragraph("Facture (copie)", TITLE_STYLE))
            story += page[1:]
        if bills:
            story.append(PageBreak())
    doc.build(story)
