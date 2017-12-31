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

OLD_PAYMENT_METHODS = [u'CdM']
PAYMENT_METHODS = [u'Cash', u'Carte', u'BVR', u'Dû', u'PVPE']
PAYMENT_STATUSES = [u'Tous', u'Comptabilisé', u'Non-comptabilisé']
SEX_MALE = "M"
SEX_FEMALE = "F"
SEX_ALL = [SEX_MALE, SEX_FEMALE]

BILL_STATUSES = [u'Tous', u'Ouverte', u'Imprimée', u'Envoyée', u'Payée', u'Abandonnée']
STATUS_OPENED = u'O'
STATUS_PRINTED = u'I'
STATUS_SENT = u'E'
STATUS_PAYED = u'P'
STATUS_ABANDONED = u'A'

BILL_TYPE_CONSULTATION = "C"
BILL_TYPE_MANUAL = "M"
BILL_TYPES = [BILL_TYPE_CONSULTATION, BILL_TYPE_MANUAL]

CANTONS = ["AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU", "NE", "NW", "OW", "SG", "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH", "N/A"]
DEFAULT_CANTON = "VD"


class Model(object):
    TABLE = None
    FIELDS = []
    AUTO_FIELD = None
    EXTRA_FIELDS = []

    @classmethod
    def load(klass, cursor, key):
        cursor.execute("""SELECT %s FROM %s WHERE %s=%%s"""
                       % (', '.join(klass.FIELDS),
                          klass.TABLE,
                          klass.FIELDS[0]),
                       [key])
        data = cursor.fetchone()
        fields = {}
        for extra in klass.EXTRA_FIELDS:
            fields[extra] = None
        fields.update(dict(zip(klass.FIELDS, data)))
        return klass(**fields)

    @classmethod
    def yield_all(klass, cursor, where=None, order=None):
        where_cond = []
        where_args = []
        if isinstance(where, dict):
            for key, value in where.items():
                if '__' in key:
                    field, test = key.split('__')
                else:
                    field, test = key, 'eq'
                test = {'eq': '=',
                        'gt': '>',
                        'lt': '<',
                        'ge': '>=',
                        'le': '<=',
                        'like': 'LIKE',
                        'ilike': 'ILIKE',
                        }[test]
                where_cond.append('%s %s %%s' % (field, test))
                where_args.append(value)
            where = 'WHERE ' + ' AND '.join(where_cond)
        elif isinstance(where, str):
            where = 'WHERE ' + where
        else:
            where = ''
        if order is not None:
            field, direction = order, 'ASC'
            if order[0] == '-':
                field, direction = order[1:], 'DESC'
            order = 'ORDER BY %s %s' % (field, direction)
        else:
            order = ''
        cursor.execute("SELECT %s FROM %s %s %s"
                       % (', '.join(klass.FIELDS),
                          klass.TABLE,
                          where,
                          order),
                       where_args)
        for data in cursor:
            yield klass(**dict(zip(klass.FIELDS, data)))

    def __init__(self, **kwds):
        for field in self.FIELDS + self.EXTRA_FIELDS:
            setattr(self, field, kwds.pop(field, None))
        if kwds:
            raise TypeError("extraneous parameters %s" % ', '.join("`%s'" % k for k in kwds))

    def __bool__(self):
        # True if this model already has a key
        return getattr(self, self.FIELDS[0]) is not None

    def __setattr__(self, field, value):
        if field not in self.FIELDS + self.EXTRA_FIELDS:
            raise AttributeError("unknown attribute `%s'" % field)
        super(Model, self).__setattr__(field, value)

    def save(self, cursor):
        if not self:
            if not self.AUTO_FIELD:
                cursor.execute("""SELECT max(%s)+1 FROM %s""" % (self.FIELDS[0], self.TABLE))
                key, = cursor.fetchone()
                if key is None:
                    key = 1
                setattr(self, self.FIELDS[0], key)
                fields = self.FIELDS
            else:
                fields = [f for f in self.FIELDS if f != self.AUTO_FIELD]
            cursor.execute("""INSERT INTO %s (%s) VALUES (%s)"""
                           % (self.TABLE,
                              ', '.join(fields),
                              ', '.join(['%s'] * len(fields))),
                           [getattr(self, field) for field in fields])
            if self.AUTO_FIELD:
                setattr(self, self.AUTO_FIELD, cursor.lastrowid)
        else:
            cursor.execute("""UPDATE %s SET %s WHERE %s=%%s"""
                           % (self.TABLE,
                              ', '.join('%s=%%s' % f for f in self.FIELDS[1:]),
                              self.FIELDS[0]),
                           [getattr(self, field) for field in self.FIELDS[1:]] + [getattr(self, self.FIELDS[0])])


class Patient(Model):
    TABLE = 'patients'
    FIELDS = ['id', 'date_ouverture', 'therapeute', 'sex', 'nom', 'prenom',
              'date_naiss', 'adresse', 'street', 'zip', 'city', 'canton',
              'ATCD_perso', 'ATCD_fam', 'medecin',
              'autre_medecin', 'phone', 'portable', 'profes_phone', 'mail',
              'ass_compl', 'profes', 'etat', 'envoye', 'divers',
              'important']


class Consultation(Model):
    TABLE = 'consultations'
    FIELDS = ['id_consult', 'id', 'date_consult', 'MC', 'MC_accident', 'EG',
              'exam_pclin', 'exam_phys', 'divers', 'APT_thorax',
              'APT_abdomen', 'APT_tete', 'APT_MS', 'APT_MI', 'APT_system',
              'A_osteo', 'traitement', 'therapeute']
    EXTRA_FIELDS = ['patient', 'bill']

    @classmethod
    def load(klass, cursor, key, bill=None):
        instance = super().load(cursor, key)
        instance.patient = Patient.load(cursor, instance.id)
        instance.bill = Bill.load_from_consultation(cursor, instance) if bill is None else bill
        #cursor.execute("""SELECT sum(rappel_cts) FROM rappels WHERE id_consult=%s""", [key])
        #if cursor.rowcount:
        #    instance.rappel_cts, = cursor.fetchone()
        #if instance.rappel_cts is None:
        #    instance.rappel_cts = 0
        if instance.therapeute is None:
            instance.therapeute = instance.patient.therapeute
        return instance

    @classmethod
    def yield_all(klass, cursor, where=None, order=None):
        cursor2 = cursor.connection.cursor()
        for instance in super().yield_all(cursor, where, order):
            instance.patient = Patient.load(cursor2, instance.id)
            instance.bill = Bill.load_from_consultation(cursor, instance)
            yield instance

    def __init__(self, **kwds):
        super().__init__(**kwds)


class Position(Model):
    TABLE = 'positions'
    FIELDS = ['id', 'id_bill', 'position_date', 'tarif_code', 'tarif_description',
              'quantity', 'price_cts']


class Reminder(Model):
    TABLE = 'reminders'
    FIELDS = ['id', 'id_bill', 'reminder_date', 'amount_cts', 'status']


class Bill(Model):
    TABLE = 'bills'
    FIELDS = ['id', 'type', 'payment_method', 'bv_ref', 'payment_date', 'status',
              'id_consult', 'id_patient', 'timestamp',
              'author_id', 'author_lastname', 'author_firstname', 'author_rcc',
              'sex', 'lastname', 'firstname', 'street', 'zip', 'city', 'canton',
              'birthdate', 'treatment_period', 'treatment_reason',
              'mandant', 'diagnostic', 'comment']
    AUTO_FIELD = 'id'
    EXTRA_FIELDS = ['patient', 'consultation', 'positions', 'reminders', 'copy', 'total_cts']

    @classmethod
    def load(klass, cursor, key, consultation=None):
        instance = super().load(cursor, key)
        instance.load_positions(cursor)
        instance.load_reminders(cursor)
        instance.consultation = instance.load_consultation(cursor) if consultation is None else consultation
        return instance

    def load_positions(self, cursor):
        cursor.execute("SELECT id FROM positions WHERE id_bill = %s", [self.id])
        position_ids = [i for i, in cursor]
        self.positions = [Position.load(cursor, id_pos) for id_pos in position_ids]
        self.total_cts = sum(pos.quantity * pos.price_cts for pos in self.positions)

    def load_reminders(self, cursor):
        cursor.execute("SELECT id FROM reminders WHERE id_bill = %s", [self.id])
        reminder_ids = [i for i, in cursor]
        self.reminders = [Reminder.load(cursor, id_reminder) for id_reminder in reminder_ids]
        self.total_cts += sum(r.amount_cts for r in self.reminders)

    def load_consultation(self, cursor):
        if self.type == BILL_TYPE_CONSULTATION:
            self.consultation = Consultation.load(cursor, self.id_consult, bill=self)
            self.patient = self.consultation.patient
        else:
            self.consultation = None
            self.patient = None

    @classmethod
    def load_from_consultation(klass, cursor, consultation):
        cursor.execute("SELECT id FROM bills WHERE id_consult = %s", [consultation.id_consult])
        if cursor.rowcount != 0:
            bill_id, = cursor.fetchone()
            bill = Bill.load(cursor, bill_id, consultation)
        else:
            bill = None
        return bill

    @classmethod
    def yield_all(klass, cursor, where=None, order=None):
        cursor2 = cursor.connection.cursor()
        for instance in super().yield_all(cursor, where, order):
            instance.load_positions(cursor2)
            instance.load_reminders(cursor2)
            instance.load_consultation(cursor2)
            yield instance

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.positions = []
        self.reminders = []
