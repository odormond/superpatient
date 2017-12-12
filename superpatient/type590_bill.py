import re
import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, PageBreak
from reportlab.platypus.flowables import TopPadder, CallerMacro
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

if __name__ == '__main__':
    from customization import DATE_FMT, labels_text
    from custom_bill import draw_bvr
else:
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


def therapeute(consult):
    header = consult.therapeute_header
    name = header.splitlines()[0]
    rcc = ([l.split(' ', 1)[1] for l in header.splitlines() if l.startswith('RCC')] or [''])[0]
    pog, address, zip_city, web, phone = labels_text.adresse_pog.splitlines()
    data = [
        ["Document", "{} {} {}".format(consult.id_consult, consult.date_consult, consult.heure_consult or '')],
        ["Auteur\nfacture", "N° GLN", "", name, web],
        ["", "N° RCC", rcc, address, zip_city, "Tél: " + phone],
        ["Four. de\nprestations", "N° GLN", "", name, web],
        ["", "N° RCC", rcc, address, zip_city, "Tél: " + phone],
    ]
    return Table(data, colWidths=[2*cm, 1.5*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=THERAPEUTE_TSTYLE)


ADDRESS_RE = re.compile(r'(.*)\b(\d{4})\s+(.*)', re.MULTILINE)


def patient(consult):
    patient = consult.patient
    sex = {"Mme": "F", "Mr": "M", "Enfant": ""}[patient.sex]
    titre = {'Mr': 'Monsieur', 'Mme': 'Madame', 'Enfant': 'Aux parents de'}[patient.sex]
    address = patient.adresse.strip()
    m = ADDRESS_RE.match(address)
    if m:
        street = m.group(1)
        ZIP = m.group(2)
        city = m.group(3)
    else:
        words = address.split()
        street = ' '.join(words[:-2])
        if words[-2:]:
            ZIP = words[-2]
            city = words[-1]
        else:
            ZIP = city = ''
    data = [
        ["Patient:", "Nom", patient.nom, "{}\n{} {}\n{}".format(titre, patient.prenom, patient.nom, patient.adresse)],
        ["", "Prénom", patient.prenom],
        ["", "Rue", street],
        ["", "NPA", ZIP],
        ["", "Localité", city],
        ["", "Date de naissance", patient.date_naiss.strftime(DATE_FMT)],
        ["", "Loi", "LCA"],
        ["", "Sexe", sex],
        ["", "Date cas", ""],
        ["", "N° patient", consult.id],
        ["", "N° AVS", ""],
        ["", "N° CADA", ""],
        ["", "N° assuré", ""],
        ["", "Canton", "VD"],
        ["", "Copie", "Non", "Date/N° GaPrCh"],
        ["", "Type de remb.", "TG", "Date/N° de facture"],
        ["", "N° contrat", "", "Date/N° de rappel"],
        ["", "Traitement", consult.date_consult.strftime(DATE_FMT), "Motif traitement", "Accident" if consult.MC_accident else "Maladie"],
        ["", "N°/Nom entreprise", "Permanence ostéopathique de la Gare (POG) Sàrl"],
        ["", "Rôle/Localité", "Ostéopathie / Lausanne"],

    ]
    return Table(data, colWidths=[2*cm, 2.5*cm, 6.5*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=PATIENT_TSTYLE)


def mandant(consult):
    #data = [["Mandataire", "GLN", "", "RCC", "", "Nom", ""]]
    data = [["Mandataire", ""]]
    return Table(data, colWidths=[2*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=BOXED_TSTYLE)


def diagnostic(consult):
    data = [["Diagnostic", consult.A_osteo.replace('\n', ' ')]]
    return Table(data, colWidths=[2*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=BOXED_TSTYLE)


def therapy(consult):
    data = [["Thérapie", "Thérapie individuelle", "Valeur du point (VPt)", "1.0", "TVA", "Oui"]]
    return Table(data, colWidths=[2*cm, '*', '*', 1*cm, 1*cm, 1.5*cm], rowHeights=[13] + [11]*(len(data)-1), style=BOXED_TSTYLE)


def comment(consult):
    data = [["Commentaire", ""]]
    return Table(data, colWidths=[2*cm, '*'], rowHeights=[13] + [11]*(len(data)-1), style=BOXED_TSTYLE)


def positions(consult):
    VAT = "8.0%"
    data = [["Date", "Tarif", "Code tarifaire", "Quan.", "Prix", "VPt", "TVA", "Montant"]]
    positions = []
    if consult.paye_par == "PVPE":
        positions.append((1250, "Consultation manquée", consult.prix_cts, 1))
    else:
        durations = list(map(int, re.findall(r'\d+', consult.prix_txt)))
        duration = max(durations) if durations else 0
        count = duration // 5
        unit_cts = consult.prix_cts / count if count else 0
        positions.append((1203, "Ostéopathie, par période de 5 minutes", unit_cts, count))
    if consult.majoration_cts:
        positions.append((1251, "Supplément pour consultations de nuit et dimanches et jours fériés", consult.majoration_cts, 1))
    if consult.frais_admin_cts:
        positions.append((999, consult.frais_admin_txt, consult.frais_admin_cts, 1))

    for code, title, unit_cts, count in positions:
        data += [[consult.date_consult.strftime(DATE_FMT), 590, code, count, '%0.2f' % (unit_cts / 100), 1.0, VAT, '%0.2f' % (count * unit_cts / 100)],
                 ["", "", title]]
    tstyle = (POSITION_TSTYLE +
              [('FONT', (0, row), (-1, row), TITLE_STYLE.fontName, 6) for row in range(2, len(data), 2)] +
              [('SPAN', (2, row), (-1, row)) for row in range(2, len(data), 2)])
    total = [["", "", "", "", "Montant dû", "", "", '%0.2f' % ((consult.prix_cts + (consult.majoration_cts or 0) + (consult.frais_admin_cts or 0)) / 100)]]
    return [Table(data, colWidths=[2*cm, 1*cm, '*', 1*cm, 1*cm, 1*cm, 1*cm, 1.5*cm], style=tstyle),
            TopPadder(Table(total, colWidths=[2*cm, 1*cm, '*', 1*cm, 1*cm, 1*cm, 1*cm, 1.5*cm], style=TOTAL_TSTYLE)),
            ]


def consultations(filename, cursor, consultations):
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=LEFT_MARGIN, topMargin=TOP_MARGIN, rightMargin=RIGHT_MARGIN, bottomMargin=BOTTOM_MARGIN)
    story = []
    consultations = consultations[:]
    while consultations:
        consult = consultations.pop()
        story += [Paragraph("Facture", TITLE_STYLE),
                  therapeute(consult),
                  patient(consult),
                  mandant(consult),
                  diagnostic(consult),
                  therapy(consult),
                  comment(consult),
                  ]
        story += positions(consult)
        if consult.paye_par in ('BVR', 'PVPE'):
            if len(' '.join((consult.patient.prenom, consult.patient.nom))) < 25:
                identite = [' '.join((consult.patient.prenom, consult.patient.nom))]
            else:
                identite = [consult.patient.prenom, consult.patient.nom]
            address_patient = '\n'.join(identite + [consult.patient.adresse])

            def render_bvr(flowable):
                canvas = flowable.canv
                x = flowable._frame._x + flowable._frame._leftExtraIndent
                y = flowable._frame._y
                canvas.translate(-x, -y)
                draw_bvr(canvas, consult.prix_cts+consult.majoration_cts+consult.frais_admin_cts, address_patient, consult.bv_ref)
            story += [PageBreak(), CallerMacro(render_bvr)]
        if consult:
            story.append(PageBreak())
    doc.build(story)


if __name__ == '__main__':
    import MySQLdb
    import sys
    import db
    from models import Patient, Consultation
    db = MySQLdb.connect(host=db.SERVER, user=db.USERNAME, passwd=db.PASSWORD, db=db.DATABASE, charset='latin1')
    cursor = db.cursor()
    test_patient = Patient.load(cursor, 1000)
    cursor.execute("""SELECT entete FROM therapeutes WHERE therapeute = %s""", [test_patient.therapeute])
    therapeute_header, = cursor.fetchone()
    print(test_patient.__dict__)
    print(therapeute_header)
    c0 = Consultation(id=1000, patient=test_patient, therapeute=test_patient.therapeute, therapeute_header=therapeute_header, date_consult=datetime.date.today(), prix_cts=8000, prix_txt="20 minutes", paye_par='Cash', bv_ref='012345678901234567890123458', frais_admin_cts=500, frais_admin_txt="BV")
    c1 = Consultation(id=1000, patient=test_patient, therapeute=test_patient.therapeute, therapeute_header=therapeute_header, date_consult=datetime.date.today(), prix_cts=10000, prix_txt="30 minutes", paye_par='BVR', bv_ref='012345678901234567890123458', majoration_cts=0, rappel_cts=0)
    c2 = Consultation(id=1000, patient=test_patient, therapeute=test_patient.therapeute, therapeute_header=therapeute_header, date_consult=datetime.date.today(), prix_cts=11000, prix_txt="40 minutes", paye_par='PVPE', bv_ref='012345678901234567890123458', majoration_cts=0, rappel_cts=300)
    c3 = Consultation(id=1000, patient=test_patient, therapeute=test_patient.therapeute, therapeute_header=therapeute_header, date_consult=datetime.date.today(), prix_cts=12000, prix_txt="50 minutes", paye_par='Carte', majoration_cts=300, rappel_cts=0)
    consultations(sys.argv[1], cursor, [c0, c1, c2, c3])
