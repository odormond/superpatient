#!/usr/bin/env python3

import re

import MySQLdb

from superpatient import db, models
from superpatient.customization import DATE_FMT


ADDRESS_RE = re.compile(r'(.*)\b(\d{4})\s+(.*)', re.MULTILINE | re.DOTALL)


def migrate_patients(connection):
    npas = {}
    with open('npa-canton.csv') as f:
        for line in f:
            npa, canton = line.strip().split(',')
            npas[npa] = canton
    cursor = connection.cursor()
    cursor2 = connection.cursor()
    cursor.execute("UPDATE IGNORE patients SET date_naiss = '1900-01-01' WHERE date_naiss = '0000-00-00'")
    cursor.execute("ALTER TABLE patients ADD COLUMN street text AFTER adresse")
    cursor.execute("ALTER TABLE patients ADD COLUMN zip text AFTER street")
    cursor.execute("ALTER TABLE patients ADD COLUMN city text AFTER zip")
    cursor.execute("ALTER TABLE patients ADD COLUMN canton text AFTER city")
    sex_map = dict(Mr="M", Mme="F")
    ok = ko = zero = 0
    cursor.execute("SELECT id, adresse, sex FROM patients")
    for id, address, sex in cursor:
        if sex in sex_map:
            cursor.execute("UPDATE patients SET sex = %s WHERE id = %s", [sex_map[sex], id])
        if address is None:
            print("0 %4d" % id)
            zero += 1
            continue
        match = ADDRESS_RE.match(address)
        if match:
            street, zip, city = [g.strip() for g in match.groups()]
            if street and street[-1] in ',.:;':
                street = street[:-1]
            canton = npas.get(zip, None)
            cursor2.execute("UPDATE patients SET street = %s, zip = %s, city = %s, canton = %s, adresse = NULL WHere id = %s", [street, zip, city, canton, id])
            print('+ %4d %r -> %r %r %r %r' % (id, address, street, zip, city, canton))
            ok += 1
        else:
            print('- %4d %r' % (id, address))
            ko += 1
    print("OK:", ok)
    print("KO:", ko)
    print("NULL:", zero)


def migrate_consultations_to_bills(connection):
    cursor = connection.cursor()
    cursor2 = connection.cursor()
    cursor3 = connection.cursor()
    cursor.execute("""CREATE TABLE bills (id integer NOT NULL AUTO_INCREMENT UNIQUE, PRIMARY KEY (id),
                                          type varchar(2) NOT NULL,
                                          payment_method varchar(10),
                                          bv_ref text DEFAULT NULL,
                                          payment_date date DEFAULT NULL,
                                          status varchar(2) NOT NULL,
                                          id_consult integer DEFAULT NULL UNIQUE,
                                          id_patient integer DEFAULT NULL,
                                          timestamp datetime DEFAULT CURRENT_TIMESTAMP,
                                          author_lastname text NOT NULL,
                                          author_firstname text NOT NULL,
                                          author_rcc text NOT NULL,
                                          sex varchar(1) NOT NULL,
                                          lastname text NOT NULL,
                                          firstname text NOT NULL,
                                          street text NOT NULL,
                                          zip text NOT NULL,
                                          city text NOT NULL,
                                          canton text NOT NULL,
                                          birthdate date NOT NULL,
                                          treatment_period text NOT NULL,
                                          treatment_reason text NOT NULL,
                                          mandant text DEFAULT NULL,
                                          diagnostic text DEfAULT NULL,
                                          comment text DEFAULT NULL
                                          )""")
    cursor.execute("""CREATE TABLE positions (id integer NOT NULL AUTO_INCREMENT UNIQUE, PRIMARY KEY (id),
                                              id_bill integer NOT NULL, FOREIGN KEY (id_bill) REFERENCES bills(id),
                                              position_date date NOT NULL,
                                              tarif_code text NOT NULL,
                                              tarif_description text NOT NULL,
                                              quantity float NOT NULL,
                                              price_cts integer NOT NULL
                                              )""")
    cursor.execute("""CREATE TABLE reminders (id integer NOT NULL AUTO_INCREMENT UNIQUE, PRIMARY KEY (id),
                                              id_bill integer NOT NULL, FOREIGN KEY (id_bill) REFERENCES bills(id),
                                              reminder_date date NOT NULL,
                                              amount_cts integer NOT NULL,
                                              status varchar(2) NOT NULL
                                              )""")
    therapeutes = {}
    cursor.execute("""SELECT therapeute, entete FROM therapeutes""")
    for therapeute, entete in cursor:
        firstname = lastname = rcc = ''
        for i, line in enumerate(entete.splitlines()):
            if i == 0:
                firstname, lastname = line.split(maxsplit=1)
            elif line.startswith('RCC'):
                rcc = line.replace('RCC', '').strip()
        therapeutes[therapeute] = firstname, lastname, rcc
    cursor.execute("""SELECT id_consult, id, date_consult, heure_consult, MC, MC_accident, EG,
                             exam_pclin, exam_phys, paye, divers, APT_thorax,
                             APT_abdomen, APT_tete, APT_MS, APT_MI, APT_system,
                             A_osteo, traitement, therapeute, prix_cts, prix_txt,
                             majoration_cts, majoration_txt, frais_admin_cts, frais_admin_txt,
                             paye_par, paye_le, bv_ref, status
                        FROM consultations""")
    for (id_consult, id_patient, date_consult, heure_consult, MC, MC_accident, EG, exam_pclin, exam_phys, paye, divers, APT_thorax,
         APT_abdomen, APT_tete, APT_MS, APT_MI, APT_system, A_osteo, traitement, therapeute, prix_cts, prix_txt,
         majoration_cts, majoration_txt, frais_admin_cts, frais_admin_txt, paye_par, paye_le, bv_ref, status) in cursor:

        patient = models.Patient.load(cursor2, id_patient)
        # Create bill
        try:
            t_firstname, t_lastname, t_rcc = therapeutes[therapeute or patient.therapeute]
        except KeyError:
            t_firstname = ''
            t_lastname = therapeute or patient.therapeute
            t_rcc = ''
        bill = models.Bill(type=models.BILL_TYPE_CONSULTATION,
                           bv_ref=bv_ref,
                           payment_method=paye_par,
                           payment_date=paye_le,
                           status=status,
                           id_consult=id_consult,
                           id_patient=id_patient,
                           timestamp=(date_consult + heure_consult) if heure_consult is not None else date_consult,
                           author_lastname=t_lastname,
                           author_firstname=t_firstname,
                           author_rcc=t_rcc,
                           sex=patient.sex if patient.sex != 'Enfant' else '',
                           lastname=patient.nom,
                           firstname=patient.prenom,
                           street=patient.street or '',
                           zip=patient.zip or '',
                           city=patient.city or '',
                           canton=patient.canton or '',
                           birthdate=patient.date_naiss,
                           treatment_period=date_consult.strftime(DATE_FMT),
                           treatment_reason='Accident' if MC_accident else 'Maladie',
                           mandant='',
                           diagnostic=A_osteo,
                           comment='')
        bill.save(cursor2)
        # and positions
        models.Position(id_bill=bill.id, position_date=bill.timestamp,
                        tarif_code='999', tarif_description=prix_txt or '',
                        quantity=1, price_cts=prix_cts).save(cursor2)
        if majoration_cts:
            models.Position(id_bill=bill.id, position_date=bill.timestamp,
                            tarif_code='999', tarif_description=majoration_txt or '',
                            quantity=1, price_cts=majoration_cts).save(cursor2)
        if frais_admin_cts:
            models.Position(id_bill=bill.id, position_date=bill.timestamp,
                            tarif_code='999', tarif_description=frais_admin_txt or '',
                            quantity=1, price_cts=frais_admin_cts).save(cursor2)

        cursor2.execute("""SELECT date_rappel, rappel_cts, status FROM rappels WHERE id_consult = %s""", [id_consult])
        for reminder_date, reminder_cost_cts, reminder_status in cursor2:
            # Create reminders
            models.Reminder(id_bill=bill.id, reminder_date=reminder_date, amount_cts=reminder_cost_cts,
                            status=reminder_status).save(cursor3)
    cursor.execute("""ALTER TABLE consultations DROP COLUMN heure_consult,
                                                DROP COLUMN prix_cts,
                                                DROP COLUMN prix_txt,
                                                DROP COLUMN majoration_cts,
                                                DROP COLUMN majoration_txt,
                                                DROP COLUMN frais_admin_cts,
                                                DROP COLUMN frais_admin_txt,
                                                DROP COLUMN paye_par,
                                                DROP COLUMN paye_le,
                                                DROP COLUMN bv_ref,
                                                DROP COLUMN status""")


def replace_tarifs_and_co(connection):
    cursor = connection.cursor()
    cursor.execute("""DROP TABLE tarifs""")
    cursor.execute("""DROP TABLE frais_admins""")
    cursor.execute("""DROP TABLE majorations""")
    cursor.execute("""CREATE TABLE tarifs (code varchar(10) NOT NULL, description text, unit_price_cts integer)""")
    cursor.execute("""INSERT INTO tarifs VALUES ('1200', 'Anamnèse / bilan / diagnostic / constatations médicales, par période de 5 mins', 1000),
                                                ('1203', 'Ostéopathie, par période de 5 mins', 1500),
                                                ('1250', 'Consultation manquée', 5000),
                                                ('1251', 'Supplément pour consultations de nuit / dimanche / jours fériés', 2000),
                                                ('1252', 'Supplément pour consultation extraordinaire dans des situations aiguës', 2000),
                                                ('1253', 'Rapport officiel', 2000),
                                                ('999', 'Bulletin de versement', 500),
                                                ('999', NULL, NULL)""")
    connection.commit()


connection = MySQLdb.connect(host=db.SERVER, user=db.USERNAME, passwd=db.PASSWORD, db=db.DATABASE, charset='latin1')
migrate_patients(connection)
migrate_consultations_to_bills(connection)
replace_tarifs_and_co(connection)
