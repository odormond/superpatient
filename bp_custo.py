# coding:UTF-8

import os
PDF_DIR = os.path.join(os.path.dirname(__file__), 'factures')

DATE_FMT = u"%d.%m.%Y"

DEFAULT_LABEL_SIZE = 9
DEFAULT_ENTRY_SIZE = 10
DEFAULT_FONT_NAME = "Helvetica"
FIXED_FONT_SIZE = 12
FIXED_FONT_NAME = "Bitstream Vera Sans Mono"

LABEL_NORMAL = (DEFAULT_FONT_NAME, DEFAULT_LABEL_SIZE)
LABEL_BOLD = (DEFAULT_FONT_NAME, DEFAULT_LABEL_SIZE, 'bold')
ENTRY_DEFAULT = (DEFAULT_FONT_NAME, DEFAULT_ENTRY_SIZE)
TEXT_DEFAULT = ENTRY_DEFAULT
LISTBOX_DEFAULT = (FIXED_FONT_NAME, FIXED_FONT_SIZE)

ANCIEN_MOYEN_DE_PAYEMENT = [u'CdM']
MOYEN_DE_PAYEMENT = [u'Cash', u'Carte', u'BVR', u'Dû', u'PVPE']
ETAT_PAYEMENT = [u'Tous', u'Comptabilisé', u'Non-comptabilisé']

MONTANT_RAPPEL_CTS = 500


class Config(object):
    def __getitem__(self, key):
        return getattr(self, key)


class BVR(Config):
    CCP = u'12-3456-7'
    prefix = 123456
    versement_pour = u"UBS SA\n1002 Lausanne"
    en_faveur_de = u"Permanance ostéopathique de la Gare\nAv. de la gare 5\n1003 Lausanne"

bvr = BVR()


class WindowsTitle(Config):
    patient = u"Fiche patient"
    new_patient = u"Nouveau patient"
    show_change_patient = u"Voir ou modifier la fiche d'un patient"
    show_change_consult = u"Voir ou modifier les consultations d'un patient"
    delete_patient = u"Base de patients - Suppression de données"
    patients_db = u"Base de patients"
    consultation = u"Consultation du %s - %s %s"
    new_consultation = u"Nouvelle consultation - %s %s"
    show_consultation = u"Afficher une consultation de %s %s"
    delete_consultation = u"Supprimer une consultation de %s %s"
    apropos = u"À propos"
    licence = u"Conditions d'utilisation"
    application = u"BasicPatient"
    db_error = u"Problème avec la base de donnée"
    missing_error = u"Information manquante"
    invalid_error = u"Information invalide"
    delete = u"Suppression"
    done = u"Fait"
    cons_pat = u"Consultation patient"
    manage_colleagues = u"Gérer les collaborateurs"
    manage_majorations = u"Gérer les majorations"
    manage_tarifs = u"Gérer les tarifs"
    manage_addresses = u"Gérer les adresses"
    compta = u"Gestion comptable"
    really_cancel = u"Confirmation d'annulation"
    summaries_import = u"Résumé de l'import"
    compta_statistics = u"Statistiques"
    manage_recalls = u"Gérer les rappels"

windows_title = WindowsTitle()


class ErrorsText(Config):
    db_id = u"Impossible d'attribuer un ID !"
    db_read = u"Impossible de lire les données !"
    db_update = u"Modification impossible !"
    db_insert = u"Insertion impossible !"
    db_delete = u"Suppression impossible !"
    db_search = u"Recherche impossible !"
    db_show = u"Affichage impossible !"
    missing_therapeute = u"Veuillez préciser le thérapeute ayant pris en charge le patient"
    missing_payment_info = u"Veuillez préciser le prix et le moyen de payement"
    missing_data = u"Veuillez compléter les champs en rouge"
    invalid_date = u"Veuillez vérifier le format des champs date"
    invalid_majoration = u"Majoration invalide"
    invalid_tarif = u"Tarif invalide"
    invalid_amount = u"Montant invalide"


errors_text = ErrorsText()


# des espaces étaient présent aux deux bouts pour avoir du padding
class ButtonsText(Config):
    ok = u"OK"  # B10
    ok_new_consult = u"OK, ouvrir une nouvelle consultation"  # B1
    save_close = u"Enregistrer et fermer"  # B2
    cancel = u"Annuler"  # B3
    reprint = u"Réimprimmer"
    search = u"Rechercher"  # B7
    add = u"Ajouter"
    change = u"Modifier"  # B11
    delete = u"Supprimer"
    show_patient = u"Afficher la fiche patient"  # B8
    change_patient = u"Modifier la fiche patient"  # B9
    new_consult = u"Nouvelle consultation pour ce patient"  # B12
    show_all_consult = u"Afficher toutes les consultations"  # B13
    show_consults = u"Afficher les consultations du patient"  # B14
    change_consult = u"Modifier la consultation"  # B15
    delete_patient = u"Supprimer le patient et toutes ses consultations"  # B16
    delete_consult = u"Supprimer cette consultation"  # B17
    show_consult = u"Afficher la consultation"  # B18
    new_patient = u"Nouveau patient"  # B25
    show_or_change_patient = u"Voir ou modifier une fiche patient"  # B26
    new_consult_known_patient = u"Nouvelle consultation (patient existant)"  # B27
    show_or_change_consult = u"Voir ou modifier une consultation"  # B28
    done = u"Terminé"
    mark_paye = u"Marquer payé"
    valider_import = u"Valider l'import"
    details = u"Détails"
    output_recalls = u"Générer les rappels"


buttons_text = ButtonsText()


class MenusText(Config):
    manage_colleagues = u"Gestion des collaborateurs"
    manage_majorations = u"Gestion des majorations"
    manage_tarifs = u"Gestion des tarifs"
    manage_addresses = u"Gestion des adresses"
    manual_bill = u"Facture manuelle"
    delete_data = u"Supprimer des données"
    save_db = u"Sauvegarder la base de données"
    restore_db = u"Restaurer la base de données"
    about = u"À propos"
    licence = u"Conditions d'utilisation"
    admin = u"Administration"
    help = u"Aide"
    bvr = u"BVRs"
    payments = u"Paiements"
    import_bvr = u"Importer les paiements"
    manage_recalls = u"Gestion des rappels"
    show_stats = u"Statistiques"


menus_text = MenusText()


class LabelsText(Config):
    # Données concernant la fiche du patient
    id = u"ID patient"
    sexe = u"Sexe"
    therapeute = u"Thérapeute"
    login = u"Login"
    nom = u"Nom"
    prenom = u"Prénom"
    naissance_le = u"Naissance le"
    naissance = u"Naissance"
    date_ouverture = u"Date d'ouverture"
    tel_fix = u"Téléphone fixe"
    medecin = u"Médecin traitant"
    portable = u"Portable"
    tel_prof = u"Téléphone professionnel"
    mail = u"Courriel"
    adr_priv = u"Adresse privée"
    medecinS = u"Autres médecins"
    ass_comp = u"Assurance complémentaire"
    profes = u"Profession"
    etat = u"État civil"
    envoye = u"Envoyé par"
    remarques = u"Remarques"
    # Données concernant les consultations
    mc = u"Motif(s) de consultation"
    eg = u"État général"
    expc = u"Examens paracliniques"
    atcdp = u"Antécédents personnels"
    atcdf = u"Antécédents familiaux"
    thorax = u"Thorax"
    abdomen = u"Abdomen"
    tete = u"Tête et cou"
    ms = u"Membres supérieurs"
    mi = u"Membres inférieurs"
    gen = u"Neuro, vascul, dermato, endocrino, lymph"
    a_osteo = u"Anamnèse ostéopathique"
    exph = u"Examen physique"
    ttt = u"Traitement"
    important = u"Important"
    paye = u"Paye ?"
    ttes_cons = u"Toutes les consultations du patient"
    seance = u"Durée / Prix"
    majoration = u"Majoré"
    paye_par = u"Moyen de payement"
    paye_le = u"Payement reçu le"
    date_consult = u"Consultation du "
    maladie = u"Maladie"
    accident = u"Accident"
    # Divers
    suppr_def_1 = u"Supprimer définitivement"
    suppr_def_2 = u", né(e) le "
    suppr_def_3 = u"ainsi que toutes ses consultations ?"
    pat_sup_1 = u"Patient(e) "
    pat_sup_2 = u" supprimé(e) de la base"
    sup_def_c = u"Supprimer définitivement cette consultation ?"
    cons_sup = u"Consultation supprimée de la base"
    collabos = u"Collaborateurs"
    entete = u"Entête d'adresse"
    majorations = u"Majorations"
    majoration = u"Majoration"
    tarifs = u"Tarifs"
    tarif = u"Tarif"
    description = u"Description"
    date_du = u"Consultations dès le"
    date_au = u"Consultations jusqu'au"
    etat_payement = u"État du payement"
    count = u"# entrées"
    total_consultation = u"Total consultation"
    total_majoration = u"Total majoration"
    total_rappel = u"Total frais de rappel"
    total = u"Total"
    addresses = u"Adresses"
    address = u"Adresse"
    identifiant = u"Identifiant"
    consult_upto = u"Consultations ou rappel jusqu'au"
    # Info sur l'application
    apropos_description = u"""BasicPatient ver. 2.0 est un gestionnaire de patients et de consultations open-source.

Il a été créé en 2006 pour satisfaire aux besoins minimaux d'un cabinet de groupe d'ostéopathes.

BasicPatient est sous licence GPL, ce qui vous donne le droit de le modifier et de l'utiliser
à votre guise.

Le manuel peut être téléchargé depuis le site web

bp.csernay.ch

Pour tout autre renseignement, veuillez écrire à

csernay@permanence-lausanne.ch"""
    licence_description = u"""Copyright 2006-2015 Tibor Csernay

BasicPatient is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

BasicPatient is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with BasicPatient; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA"""
    adresse_pog = u"""Permanence Ostéopathique de la Gare
Av. de la gare 5
1003 Lausanne
www.permanence-lausanne.ch
021 510 50 50"""
    really_cancel = u"""Voulez-vous vraiment annuler ?
Les données de cette consultation ne seront pas enregistrées."""


labels_text = LabelsText()


class LabelsFont(Config):
    id = sexe = therapeute = login = nom = prenom = naissance_le = naissance = LABEL_BOLD
    date_ouverture = tel_fix = medecin = portable = tel_prof = mail = LABEL_BOLD
    adr_priv = medecinS = ass_comp = profes = etat = envoye = remarques = LABEL_BOLD
    mc = eg = expc = atcdp = atcdf = thorax = abdomen = tete = ms = mi = LABEL_BOLD
    gen = a_osteo = exph = ttt = important = paye = ttes_cons = seance = LABEL_BOLD
    paye_par = paye_le = entete = collabos = date_du = date_au = etat_payement = LABEL_BOLD
    count = total_consultation = total_majoration = total_rappel = total = majorations = LABEL_BOLD
    majoration = tarifs = tarif = description = addresses = address = identifiant = LABEL_BOLD
    consult_upto = LABEL_BOLD


labels_font = LabelsFont()


class FieldsFont(Config):
    id = sexe = therapeute = login = nom = prenom = naissance_le = naissance = ENTRY_DEFAULT
    date_ouverture = tel_fix = portable = tel_prof = mail = ENTRY_DEFAULT
    ass_comp = profes = etat = envoye = seance = count = total_consultation = ENTRY_DEFAULT
    total_majoration = total_rappel = total = consult_upto = ENTRY_DEFAULT
    paye_par = paye_le = date_du = date_au = etat_payement = ENTRY_DEFAULT
    majoration = tarif = description = ENTRY_DEFAULT
    important = medecin = adr_priv = medecinS = remarques = ttes_cons = TEXT_DEFAULT
    mc = eg = expc = atcdp = atcdf = thorax = abdomen = tete = ms = TEXT_DEFAULT
    mi = gen = a_osteo = exph = ttt = paye = entete = TEXT_DEFAULT
    rp = rc = collabos = majorations = tarifs = consultations = LISTBOX_DEFAULT
    addresses = address = identifiant = TEXT_DEFAULT


fields_font = FieldsFont()


class FieldsHeight(Config):
    medecin = 4
    adr_priv = 4
    medecinS = 7
    remarques = 4
    mc = 4
    eg = 6
    expc = 11
    atcdp = 4
    atcdf = 4
    thorax = 4
    abdomen = 4
    tete = 4
    ms = 4
    mi = 4
    gen = 4
    a_osteo = 4
    exph = 17
    ttt = 7
    important = 6
    paye = 6
    rp = 19
    rc = 19
    ttes_cons = 39
    entete = 6
    collabos = 10
    majorations = 10
    majoration = 6
    tarifs = 10
    tarif = 6
    description = 6
    consultations = 40
    addresses = 20
    address = 6


fields_height = FieldsHeight()


class FieldsWidth(Config):
    rp = 75
    rc = 75
    collabos = 75
    majorations = 40
    tarifs = 40
    consultations = 100
    ttes_cons = 100
    important = 60
    medecin = 60
    adr_priv = 60
    medecinS = 60
    remarques = 60
    eg = 60
    expc = 60
    atcdp = 60
    atcdf = 60
    thorax = 60
    abdomen = 60
    exph = 60
    tete = 60
    ms = 60
    mi = 60
    gen = 60
    a_osteo = 60
    ttt = 60
    paye = 60
    entete = 60
    addresses = 100
    address = 60


fields_width = FieldsWidth()
