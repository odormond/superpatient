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

BILL_TYPE = '590'
DATE_FMT = "%d.%m.%Y"

MONTANT_RAPPEL_CTS = 500

PAIEMENT_SORTIE = True

SIGNATURE_URL = 'https://api.osteosoft.ch/api/v1/billing/datamatrix'  # Set to None to disable the feature


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
    apropos = "À propos"
    licence = "Conditions d'utilisation"
    application = "SuperPatient"
    db_error = "Problème avec la base de donnée"
    missing_error = "Information manquante"
    invalid_error = "Information invalide"
    delete = "Suppression"
    done = "Fait"
    cons_pat = "Consultation patient"
    manage_colleagues = "Gérer les collaborateurs"
    manage_tarifs = "Gérer les tarifs"
    manage_majorations = "Gérer les majorations"
    manage_frais_admins = "Gérer les frais administratifs"
    manage_addresses = "Gérer les adresses"
    compta = "Gestion comptable"
    encaissement = "Vérification/Confirmation finale de paiement"
    really_cancel = "Confirmation d'annulation"
    summaries_import = "Résumé de l'import"
    compta_statistics = "Statistiques"
    manage_reminders = "Gérer les rappels"
    print_completed = "Impression effectuée ?"
    confirm_change = "Confirmer le changement"


windows_title = WindowsTitle()


class ErrorsText(Config):
    db_id = "Impossible d'attribuer un ID !"
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
    invalid_tarif = "Tarif invalide"
    invalid_majoration = "Majoration invalide"
    invalid_frais_admin = "Frais administratif invalide"
    invalid_amount = "Montant invalide"


errors_text = ErrorsText()


# des espaces étaient présent aux deux bouts pour avoir du padding
class ButtonsText(Config):
    ok = "OK"  # B10
    ok_new_consult = "OK, ouvrir une nouvelle consultation"  # B1
    save_close = "Enregistrer et fermer"  # B2
    cancel = "Annuler"  # B3
    reprint = "Réimprimmer"
    search = "Rechercher"  # B7
    add = "Ajouter"
    change = "Modifier"  # B11
    delete = "Supprimer"
    show_patient = "Afficher la fiche patient"  # B8
    change_patient = "Modifier la fiche patient"  # B9
    new_consult = "Nouvelle consultation pour ce patient"  # B12
    show_all_consult = "Afficher toutes les consultations"  # B13
    show_consults = "Afficher les consultations du patient"  # B14
    change_consult = "Modifier la consultation"  # B15
    delete_patient = "Supprimer le patient et toutes ses consultations"  # B16
    delete_consult = "Supprimer cette consultation"  # B17
    show_consult = "Afficher la consultation"  # B18
    new_patient = "Nouveau patient"  # B25
    show_or_change_patient = "Voir ou modifier une fiche patient"  # B26
    new_consult_known_patient = "Nouvelle consultation (patient existant)"  # B27
    show_or_change_consult = "Voir ou modifier une consultation"  # B28
    done = "Terminé"
    mark_paye = "Marquer payé"
    mark_printed = "Marquer imprimé"
    mark_mailed = "Marquer envoyé"
    mark_abandoned = "Marquer Abandonné"
    change_pay_method_and_print = "Changer moyen de paiement et imprimer"
    valider_import = "Valider l'import"
    details = "Détails"
    output_reminders = "Générer les rappels"
    refresh = "Rafraichir"
    validate = "Valider"


buttons_text = ButtonsText()


class MenusText(Config):
    manage_colleagues = "Gestion des collaborateurs"
    manage_tarifs = "Gestion des tarifs"
    manage_majorations = "Gestion des majorations"
    manage_frais_admins = "Gestion des frais administratifs"
    manage_addresses = "Gestion des adresses"
    manual_bill = "Facture manuelle"
    delete_data = "Supprimer des données"
    save_db = "Sauvegarder la base de données"
    restore_db = "Restaurer la base de données"
    about = "À propos"
    licence = "Conditions d'utilisation"
    admin = "Administration"
    help = "Aide"
    bvr = "BVRs"
    payments = "Paiements"
    import_bvr = "Importer les paiements"
    manage_reminders = "Gestion des rappels"
    show_stats = "Statistiques"


menus_text = MenusText()


class LabelsText(Config):
    # Données concernant la fiche du patient
    id = "ID patient"
    sexe = "Sexe"
    therapeute = "Thérapeute"
    login = "Login"
    nom = "Nom"
    prenom = "Prénom"
    naissance_le = "Naissance le"
    naissance = "Naissance"
    date_ouverture = "Date d'ouverture"
    tel_fix = "Téléphone fixe"
    medecin = "Médecin traitant"
    portable = "Portable"
    tel_prof = "Téléphone professionnel"
    mail = "Courriel"
    adr_priv = "Adresse privée"
    medecinS = "Autres médecins"
    ass_comp = "Assurance complémentaire"
    profes = "Profession"
    etat = "État civil"
    envoye = "Envoyé par"
    remarques = "Remarques"
    # Données concernant les consultations
    mc = "Motif(s) de consultation"
    eg = "État général"
    expc = "Examens paracliniques"
    atcdp = "Antécédents personnels"
    atcdf = "Antécédents familiaux"
    thorax = "Thorax"
    abdomen = "Abdomen"
    tete = "Tête et cou"
    ms = "Membres supérieurs"
    mi = "Membres inférieurs"
    gen = "Neuro, vascul, dermato, endocrino, lymph"
    a_osteo = "Anamnèse ostéopathique"
    exph = "Examen physique"
    ttt = "Traitement"
    important = "Important"
    paye = "Paye ?"
    ttes_cons = "Toutes les consultations du patient"
    seance = "Durée / Prix"
    majoration = "Majoré"
    paye_par = "Moyen de payement"
    paye_le = "Payement reçu le"
    date_consult = "Consultation du "
    maladie = "Maladie"
    accident = "Accident"
    # Divers
    suppr_def_1 = "Supprimer définitivement"
    suppr_def_2 = ", né(e) le "
    suppr_def_3 = "ainsi que toutes ses consultations ?"
    pat_sup_1 = "Patient(e) "
    pat_sup_2 = " supprimé(e) de la base"
    sup_def_c = "Supprimer définitivement cette consultation ?"
    sup_def_b = "Supprimer définitivement la facture de cette consultation ?"
    cons_sup = "Consultation supprimée de la base"
    bill_sup = "Facture supprimée de la base"
    collabos = "Collaborateurs"
    entete = "Entête d'adresse"
    tarifs = "Tarifs"
    tarif = "Tarif"
    majorations = "Majorations"
    majoration = "Majoration"
    frais_admins = "Frais administratifs"
    frais_admin = "Frais administratif"
    prix = "Prix"
    description = "Description"
    date_du = "Consultations dès le"
    date_au = "Consultations jusqu'au"
    etat_payement = "État du payement"
    status_facture = "Status de la facture"
    count = "# entrées"
    total_consultation = "Total consultation"
    total_majoration = "Total majoration"
    total_frais_admin = "Total frais administratif"
    total_rappel = "Total frais de rappel"
    total = "Total"
    addresses = "Adresses"
    address = "Adresse"
    identifiant = "Identifiant"
    consult_upto = "Consultations ou rappel jusqu'au"
    ask_confirm_print_bvr = "Avez-vous imprimé le BVR ?"
    ask_confirm_payment_method_change_to_BVR = "Voulez-vous vraiment changer la méthode de paiement vers BVR ?"
    # Info sur l'application
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
