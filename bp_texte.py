#!/usr/bin/env python2
# -*- coding: latin1 -*-

# File: bp_texte.py

#    Copyright 2006, 2007 Tibor Csernay

#    This file is part of BasicPatient.

#    BasicPatient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    BasicPatient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with BasicPatient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# Generalites
mme = "Madame"
mr = "Monsieur"
mr2 = "Mr"
mme2 = "Mme"
mre = "Mr ou Mme (?)"
m = "M"
f = "F"

T1 = ""
titre = "BasicPatient"
etat_install = "0"

# Boutons
B1 = " Ok, ouvrir une nouvelle consultation "
B2 = " Enregistrer et fermer "
B3 = " Annuler "
B4 = " Ok, passer a l'examen physique "
B5 = " Revenir a l'examen physique "
B6 = " Revenir a l'anamnese "
B7 = " Rechercher "
B8 = " Afficher la fiche patient "
B9 = " Modifier la fiche patient "
B10 = " Ok "
B11 = " Modifier "
B12 = " Nouvelle consultation pour ce patient "
B13 = " Afficher toutes les consultations "
B14 = " Afficher les consultations du patient "
B15 = " Modifier la consultation "
B16 = " Supprimer le patient et toutes ses consultations "
B17 = " Supprimer cette consultation "
B18 = " Afficher la consultation "
B19 = " Pas de mot passe "
B20 = "\nBienvenue !\n\nAvant de pouvoir installer BasicPatient, il est necessaire\nd'avoir un serveur de données MySQL accessible.\nSi vous n'avez pas de serveur MySQL installe,\nveuillez faire le premier choix :\n"
B21 = " Installer et configurer un serveur MySQL 5.0 "
B22 = " Configurer un serveur MySQL 5.0 deja installe "
B23 = " Non merci, je vais configurer mon serveur MySQL moi-meme "
B24 = " Quitter l'installation "
B25 = " Nouveau patient "
B26 = " Voir ou modifier une fiche patient "
B27 = " Nouvelle consultation (patient existant) "
B28 = " Voir ou modifier une consultation "
B29 = "Supprimer des donnees"
B30 = "Sauvegarder la base de donnees"
B31 = "Restaurer la base de donnees"
B32 = "A propos"
B33 = "Conditions d'utilisation"

# Messages
administration = "Administration"
help = "Aide"
apropos = "A propos"
licence = "Conditions d'utilisation"
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

BD = "Base de donnees"
BP = "Base de patients"
id_imp = "Impossible de donner un ID au patient !"
info_manq = "Information manquante"
npdn = "Veuillez entrer le nom, le prenom et la date de naissance"
enr = "Enregistrement"
imp_format_date = "Impossible d'entrer les donnees dans la base !\nVerifiez le format de la date de naissance...\ndans l'ordre : Annee-mois-jour"
mtc = "Veuillez entrer le motif de consultation"
imp_db = "Impossible d'entrer les donnees dans la base !"
error = "Erreur"
imp_lire = "Impossible de lire les donnees !"
excl = "Veuillez entrer l'examen physique"
rech_imp = "Recherche impossible !"
data_p = "Donnees patient"
case_sex = "Appliquer les modifications ?\nAvez-vous coche la case sexe ?"
modif_imp = "Modification impossible !"
affich_imp = "Affichage impossible !"
sup_imp = "Suppression impossible"
idc_imp = "Impossible de donner un id a la consultation !"
atcdp_imp = "Impossible de lire les ATCD personnels !"
atcdf_imp = "Impossible de lire les ATCD familiaux !"
atcdpf_imp = "Impossible de lire les ATCD !"
v_m_cons = "Voir ou modifier les consultations d'un patient"
nouveau_patient = "Nouveau patient"
voir_modif_p = "Voir ou modifier la fiche d'un patient"
nouvel_anamn = "Nouvelle anamnese pour"
nouvel_exph = "Nouvel examen physique pour"
fich_p = "Fiche patient"
exphp = "Examen physique pour"
cons_de = "Consultations de "
ttes_cons = "Toutes les consultations du patient"
cons_pat = "Consultation patient"
appl_modif = "Appliquer les modifications ?"
suppr = "Suppression"
suppr_def_1 = "Supprimer definitivement"
suppr_def_2 = ", ne(e) le "
suppr_def_3 = "ainsi que toutes ses consultations ?"
fait = "Fait"
pat_sup_1 = "Patient(e) "
pat_sup_2 = " supprime(e) de la base"
db_sup_p = "Base de patients - Suppression de donnees"
sup_def_c = "Supprimer definitivement cette consultation ?"
cons_sup = "Consultation supprimee de la base"
sup_cons_de = "Supprimer une consultation de "

## Donnees concernant la fiche du patient
therapeute = "Therapeute "
nom = "Nom"
prenom = "Prenom"
naissance = "Naissance "
naissance_le = "Naissance le (AAAA-MM-JJ)"
date_ouverture = "Date d'ouverture"
tel_fix = "Telephone fixe"
prive = "Prive"
natel = "Telephone portable"
portable = "Portable"
tel_prof = "Telephone professionnel"
t_prof = "Professionnel"
medecin = "Medecin traitant"
medecinS = "Autres medecins"
mail = "Courriel"
adr = "Adresse"
adr_priv = "Adresse privee"
ass_comp = "Assurance complementaire"
prof = "Profession"
etat = "Etat civil"
envoye = "Envoye par"
rem = "Remarques"
id_p = "ID patient"
ouv_fich = "Ouverture de la fiche"
date_manq = " date manquante !!!"
veuillez = "Veuillez remplir,svp"

# Donnees concernant les consultations
mc = "Motif(s) de consultation"
eg = "Etat general"
expc = "Examens paracliniques"
atcdp = "Antecedents personnels"
atcdf = "Antecedents familiaux"
thorax = "Thorax"
abdomen = "Abdomen"
tete = "Tete et cou"
ms = "Membres superieurs"
mi = "Membres inferieurs"
gen = "Neuro, vascul, dermato, endocrino, lymph"
a_osteo = "Anamnese osteopathique"
important = "Important"
anamn = "Anamnese pour"
exph = "Examen physique"
ttt = "Traitement"
rem = "Remarques"
paye = "Paye ?"
cons_du_1er = "Consultation du "

# Save / Restore DB
verif_rest = "Veuillez verifier que le fichier representant votre base\nest bien sur votre bureau,\net qu'il ne contient pas d'espace dans le nom !"
filename = "Veuillez entrer un nom de fichier representant la base actuelle.\nLe nom ne doit pas contenir d'espace.\npar ex.     patients-23janvier2007"
filename_follow = "Le fichier sera sauvegarde sur le bureau."
attention_base = "ATTENTION, LA BASE ACTUELLE SERA DEFINITIVEMENT EFFACEE !!"
filename2 = "Nom du fichier (avec son extension)"
filename3 = "Nom du fichier"

# Installer
inst_choix = "Veuillez choisir votre architecture (Intel, PowerPC) :"
inst_er_1 = "Impossible d'installer MySQL"
inst_er_2 = "Impossible de demarrer le serveur MySQL"
inst_er_3 = "Imposible de se connecter a la base SQL\nMot de passe invalide..."
inst_er_4 = "Impossible de configurer la base BasicPatient"
inst_fin = "Fin de l'installation et de la configuration !\nBasicPatient se trouve dans le repertoire\nApplications de votre mac"
inst_passwd_entry = "Veuillez entrer le mot de passe administrateur (root)\ndu serveur MySQL. Si vous n'en avez pas donne lors\nde l'installation, veuillez cliquer sur le bouton\ncorrespondant.\nMerci !"
inst_m = "Installation de MySQL"
install_B1 = "\nBienvenue !\n\nAvant de pouvoir installer BasicPatient, il est necessaire\nd'avoir un serveur de données MySQL accessible.\nSi vous n'avez pas de serveur MySQL installe,\nveuillez faire le premier choix :\n"
inst_infos = "\nVeuillez configurer MySQL pour que l'utilisateur bpuser\n(mot de pass : bppass) puisse acceder a la base\nbasicpatient avec les droits : SELECT,INSERT,UPDATE,DELETE.\n\nVeuillez egalement inserer la structure de base bp.sql\n\nmysql> CREATE DATABASE basicpatient;\n\nmysql> GRANT SELECT,UPDATE,INSERT,DELETE on basicpatient.*\n-> to 'bpuser'@localhost IDENTIFIED by\n-> 'bppass' WITH GRANT OPTION;\nmysql> FLUSH PRIVILEGES;\n\n $ mysql -u root -p 'password' basicpatient < bp.sql"
