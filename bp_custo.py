# coding:UTF-8

DEFAULT_LABEL_SIZE = 9
DEFAULT_ENTRY_SIZE = DEFAULT_LABEL_SIZE
DEFAULT_FONT_NAME = "Helvetica"

LABEL_BOLD = (DEFAULT_FONT_NAME, DEFAULT_LABEL_SIZE, 'bold')
ENTRY_DEFAULT = (DEFAULT_FONT_NAME, DEFAULT_ENTRY_SIZE)

MOYEN_DE_PAYEMENT = ['Cash', 'Carte', 'BVR']


class Config(object):
    def __getitem__(self, key):
        return getattr(self, key)


class windows_title(Config):
    patient = "Fiche patient"
    new_patient = "Nouveau patient"
    show_change_patient = "Voir ou modifier la fiche d'un patient"
    show_change_consult = "Voir ou modifier les consultations d'un patient"
    delete_patient = "Base de patients - Suppression de donnees"
    patients_db = "Base de patients"
    consultation = "Consultation du %s - %s %s"
    new_consultation = "Nouvelle consultation - %s %s"
    delete_consultation = "Supprimer une consultation de %s %s"
    apropos = "À propos"
    licence = "Conditions d'utilisation"
    application = "BasicPatient"
    db_error = "Problème avec la base de donnée"
    missing_error = "Information manquante"
    invalid_error = "Information invalide"
    delete = "Suppression"
    done = "Fait"
    cons_pat = "Consultation patient"


class errors_text(Config):
    db_id = "Impossible d'attribuer un ID !"
    db_read = "Impossible de lire les données !"
    db_update = "Modification impossible !"
    db_delete = "Suppression impossible !"
    db_search = "Recherche impossible !"
    db_show = "Affichage impossible !"
    missing_paye_par = "Veuillez préciser le moyen de payement"
    missing_names_birthday = "Veuillez entrer le nom, le prenom et la date de naissance"
    invalid_date = "Veuillez saisir la date de naissance sous la forme : AAAA-MM-JJ"


# des espaces étaient présent aux deux bouts pour avoir du padding
class buttons_text(Config):
    ok = "OK"  # B10
    ok_new_consult = "OK, ouvrir une nouvelle consultation"  # B1
    save_close = "Enregistrer et fermer"  # B2
    cancel = "Annuler"  # B3
    search = "Rechercher"  # B7
    change = "Modifier"  # B11
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


class menus_text(Config):
    delete_data = "Supprimer des données"
    save_db = "Sauvegarder la base de données"
    restore_db = "Restaurer la base de données"
    about = "À propos"
    licence = "Conditions d'utilisation"
    admin = "Administration"
    help = "Aide"


class labels_text(Config):
    # Données concernant la fiche du patient
    id = "ID patient"
    sexe = "Sexe"
    therapeute = "Therapeute"
    nom = "Nom"
    prenom = "Prénom"
    naissance_le = "Naissance le (AAAA-MM-JJ)"
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
    etat = "Etat civil"
    envoye = "Envoyé par"
    remarques = "Remarques"
    # Données concernant les consultations
    mc = "Motif(s) de consultation"
    eg = "Etat général"
    expc = "Examens paracliniques"
    atcdp = "Antécedents personnels"
    atcdf = "Antécedents familiaux"
    thorax = "Thorax"
    abdomen = "Abdomen"
    tete = "Tete et cou"
    ms = "Membres superieurs"
    mi = "Membres inferieurs"
    gen = "Neuro, vascul, dermato, endocrino, lymph"
    a_osteo = "Anamnese ostéopathique"
    exph = "Examen physique"
    ttt = "Traitement"
    important = "Important"
    paye = "Paye ?"
    ttes_cons = "Toutes les consultations du patient"
    seance = "Durée / Prix"
    paye_par = "Moyen de payement"
    paye_le = "Payement reçu le"
    date_consult = "Consultation du "
    # Divers
    ttes_cons = "Toutes les consultations du patient"
    date_format = "AAAA-MM-JJ"
    suppr_def_1 = "Supprimer definitivement"
    suppr_def_2 = ", né(e) le "
    suppr_def_3 = "ainsi que toutes ses consultations ?"
    pat_sup_1 = "Patient(e) "
    pat_sup_2 = " supprimé(e) de la base"
    appl_modif = "Appliquer les modifications ?"
    sup_def_c = "Supprimer definitivement cette consultation ?"
    cons_sup = "Consultation supprimée de la base"
    # Info sur l'application
    apropos_description = """BasicPatient ver. 1.0 est un gestionnaire de patients et de consultations open-source.

Il a été créé en 2006 pour satisfaire aux besoins minimaux d'un cabinet de groupe d'ostéopathes.

BasicPatient est sous licence GPL, ce qui vous donne le droit de le modifier et de l'utiliser
à votre guise.

Le manuel peut être téléchargé depuis le site web

bp.csernay.ch

Pour tout autre renseignement, veuillez écrire à

csernay@permanence-lausanne.ch"""
    licence_description = """Copyright 2006, 2007 Tibor Csernay

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
    adresse_pog = """Permanance Ostéopathique de la Gare
Av. de la gare 5
1003 Lausanne
www.permanance-lausanne.ch
021 510 50 50"""


class labels_font(Config):
    id = sexe = therapeute = nom = prenom = naissance_le = naissance = LABEL_BOLD
    date_ouverture = tel_fix = medecin = portable = tel_prof = mail = LABEL_BOLD
    adr_priv = medecinS = ass_comp = profes = etat = envoye = remarques = LABEL_BOLD
    mc = eg = expc = atcdp = atcdf = thorax = abdomen = tete = ms = mi = LABEL_BOLD
    gen = a_osteo = exph = ttt = important = paye = ttes_cons = seance = LABEL_BOLD
    paye_par = paye_le = LABEL_BOLD


class fields_font(Config):
    id = sexe = therapeute = nom = prenom = naissance_le = naissance = ENTRY_DEFAULT
    date_ouverture = tel_fix = medecin = portable = tel_prof = mail = ENTRY_DEFAULT
    adr_priv = medecinS = ass_comp = profes = etat = envoye = remarques = ENTRY_DEFAULT
    mc = eg = expc = atcdp = atcdf = thorax = abdomen = tete = ms = ENTRY_DEFAULT
    mi = gen = a_osteo = exph = ttt = important = paye = ttes_cons = ENTRY_DEFAULT
    seance = paye_par = paye_le = ENTRY_DEFAULT


class fields_height(Config):
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


class fields_width(Config):
    rp = 75
    rc = 75
