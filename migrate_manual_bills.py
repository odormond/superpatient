#!/usr/bin/env python3

import re

import MySQLdb

from superpatient import credentials, db, models


ADDRESS_RE = re.compile(r'(?:(Madame|Monsieur)\n)?([^ \n]+)(?: +([^\n]+))?\n(?:([^\n]+)\n)?(.*)\n(\d{4}) +([^\n]*)', re.IGNORECASE | re.DOTALL)


def migrate_manual_bills(connection):
    cursor = connection.cursor()
    cursor2 = connection.cursor()
    cursor.execute("""ALTER TABLE bills ADD COLUMN title text DEFAULT NULL AFTER sex,
                                        ADD COLUMN complement text DEFAULT NULL AFTER firstname,
                                        MODIFY COLUMN sex varchar(1) DEFAULT NULL,
                                        MODIFY COLUMN canton text DEFAULT NULL,
                                        MODIFY COLUMN birthdate date DEFAULT NULL,
                                        MODIFY COLUMN treatment_period text DEFAULT NULL,
                                        MODIFY COLUMN treatment_reason text DEFAULT NULL""")
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
    cursor.execute("""SELECT identifiant, therapeute, destinataire, motif,
                             montant_cts, remarque, date, paye_le, bv_ref, status
                        FROM factures_manuelles""")
    for (identifiant, therapeute, destinataire, motif, montant_cts, remarque,
         date, paye_le, bv_ref, status) in cursor:

        try:
            t_firstname, t_lastname, t_rcc = therapeutes[therapeute]
        except KeyError:
            t_firstname = ''
            t_lastname = therapeute
            t_rcc = ''
        address = ADDRESS_RE.match(destinataire)
        title, firstname, lastname, complement, street, zip, city = address.groups()
        bill = models.Bill(type=models.BILL_TYPE_MANUAL,
                           bv_ref=bv_ref,
                           payment_method='BVR',
                           payment_date=paye_le,
                           status=status,
                           timestamp=date,
                           author_id=therapeute,
                           author_lastname=t_lastname,
                           author_firstname=t_firstname,
                           author_rcc=t_rcc,
                           title=title,
                           lastname=lastname or '',
                           firstname=firstname,
                           complement=complement,
                           street=street,
                           zip=zip,
                           city=city,
                           comment=remarque)
        bill.save(cursor2)
        # and positions
        models.Position(id_bill=bill.id, position_date=bill.timestamp,
                        tarif_code='999', tarif_description=motif,
                        quantity=1, price_cts=montant_cts).save(cursor2)
    cursor.execute("""DROP TABLE factures_manuelles""")
    cursor.execute("""DROP TABLE rappels""")


def migrate_addresses(connection):
    cursor = connection.cursor()
    cursor2 = connection.cursor()
    cursor.execute("""CREATE TABLE addresses (id varchar(50) NOT NULL UNIQUE, PRIMARY KEY (id),
                                              title text DEFAULT NULL,
                                              firstname text NOT NULL,
                                              lastname text NOT NULL,
                                              complement text DEFAULT NULL,
                                              street text NOT NULL,
                                              zip text NOT NULL,
                                              city text NOT NULL)""")
    cursor.execute("""SELECT id, adresse FROM adresses""")
    for id, address in cursor:
        address = ADDRESS_RE.match(address)
        title, firstname, lastname, complement, street, zip, city = address.groups()
        cursor2.execute("""INSERT INTO addresses VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                        [id, title, firstname or '', lastname or '', complement, street or '', zip or '', city or ''])
    cursor.execute("""DROP TABLE adresses""")


connection = MySQLdb.connect(host=db.SERVER, user=credentials.DB_USER, passwd=credentials.DB_PASS, db=db.DATABASE, charset='latin1')
migrate_manual_bills(connection)
migrate_addresses(connection)
