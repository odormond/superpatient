# coding:UTF-8

#    Copyright 2006 Tibor Csernay

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

from pathlib import Path
PDF_DIR = str(Path(__file__).parents[1] / 'factures')

VERSION = '4.24'
SITE = 'Lausanne'
DEFAULT_CANTON = "VD"

BILL_TYPE = '590'
DATE_FMT = "%d.%m.%Y"

MONTANT_RAPPEL_CTS = 500

PAIEMENT_SORTIE = True

SIGNATURE_URL = 'https://api.osteosoft.ch/api/v1/billing/datamatrix'  # Set to None to disable the feature

ROUNDING_MODE = '5cts'  # See models.py for alternatives


class Config(object):
    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __getattribute__(self, key):
        try:
            return super(Config, self).__getattribute__(key)
        except AttributeError:
            if hasattr(self, 'DEFAULT'):
                return self.DEFAULT
            raise


class BVR(Config):
    CCP = u'01-145-6'
    prefix = 272335
    versement_pour = "UBS Switzerland\n8098 Zurich"
    en_faveur_de = "Permanence Ostéopathique\nde la Gare (POG) Sàrl\nPl. de la Gare 10\n1003 Lausanne"


bvr = BVR()


class WindowsTitle(Config):
    patient = "Fiche patient"
    new_patient = "Nouveau patient"
    show_change_patient = "Voir ou modifier la fiche d'un patient"
    show_change_consult = "Voir ou modifier les consultations d'un patient"
    delete_patient = "Base de patients - Suppression de données"
    patients_db = "Base de patients"
    consultation = "Consultation du %s - %s %s"
    new_consultation = "Nouvelle consultation - %s %s"
    show_consultation = "Afficher une consultation de %s %s"
    delete_consultation = "Supprimer une consultation de %s %s"
    db_error = "Problème avec la base de donnée"
    missing_error = "Information manquante"
    invalid_error = "Information invalide"
    delete = "Suppression"
    done = "Fait"
    manage_colleagues = "Gérer les collaborateurs"
    manage_tarifs = "Gérer les tarifs"
    manage_addresses = "Gérer les adresses"
    really_cancel = "Confirmation d'annulation"
    print_completed = "Impression effectuée ?"
    confirm_change = "Confirmer le changement"


windows_title = WindowsTitle()


class ErrorsText(Config):
    db_read = "Impossible de lire les données !"
    db_update = "Modification impossible !"
    db_insert = "Insertion impossible !"
    db_delete = "Suppression impossible !"
    db_search = "Recherche impossible !"
    db_show = "Affichage impossible !"
    missing_therapeute = "Veuillez préciser le thérapeute ayant pris en charge le patient"
    missing_payment_info = "Veuillez préciser le prix et le moyen de payement"
    missing_positions = "Veuillez ajouter au moins une position à la facture"
    missing_data = "Veuillez compléter les champs en rouge"
    invalid_date = "Veuillez vérifier le format des champs date"
    invalid_amount = "Montant invalide"


errors_text = ErrorsText()


class LabelsText(Config):
    therapeute = "Thérapeute"
    remarques = "Remarques"
    eg = "État général"
    expc = "Examens paracliniques"
    thorax = "Thorax"
    abdomen = "Abdomen"
    tete = "Tête et cou"
    ms = "Membres supérieurs"
    mi = "Membres inférieurs"
    gen = "Neuro, vascul, dermato, endocrino, lymph"
    a_osteo = "Anamnèse ostéopathique"
    exph = "Examen physique"
    ttt = "Traitement"
    maladie = "Maladie"
    suppr_def_3 = "ainsi que toutes ses consultations ?"
    pat_sup_2 = " supprimé(e) de la base"
    sup_def_c = "Supprimer définitivement cette consultation ?"
    sup_def_b = "Supprimer définitivement la facture de cette consultation ?"
    cons_sup = "Consultation supprimée de la base"
    bill_sup = "Facture supprimée de la base"
    ask_confirm_print_bvr = "Avez-vous imprimé le BVR ?"
    ask_confirm_payment_method_change_to_BVR = "Voulez-vous vraiment changer la méthode de paiement vers BVR ?"
    apropos_description = """SuperPatient ver. {VERSION} est un gestionnaire de patients,
de consultations, et de facturation.

Il a été créé en 2006 pour satisfaire aux besoins
minimaux d'un cabinet de groupe d'ostéopathes.

Superpatient est sous licence GPL.

Pour tout autre renseignement, veuillez écrire à

Tibor Csernay
csernay@pog.swiss""".format(VERSION=VERSION)
    licence_description = """POG Sàrl - Copyright 2006-2018 - www.pog.swiss

SuperPatient is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

SuperPatient is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with SuperPatient; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA"""
    adresse_pog = """Permanence Ostéopathique de la Gare
Pl. de la Gare 10
1003 Lausanne
www.pog.swiss
021 510 50 50"""
    really_cancel = """Voulez-vous vraiment annuler ?
Les données de cette consultation ne seront pas enregistrées."""
    bill_really_cancel = """Voulez-vous vraiment annuler ?
Aucune facture ne sera émise !"""
    bill_role_locality = "Ostéopathie / {SITE}".format(SITE=SITE)


labels_text = LabelsText()
