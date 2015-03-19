#!/usr/bin/env python2
# -*- coding: latin1 -*-

# File: bp_variables.py

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

## Variables generales
# taille des characteres
entete_taille_np = entete_taille_npa = entete_taille_npp = entete_taille_rp = entete_taille_aps = entete_taille_mps = entete_taille_rpe = entete_taille_nape = entete_taille_nppe = entete_taille_rc = entete_taille_vcs = entete_taille_vmc = alasuite = 9
texte_bulle_taille_np = texte_bulle_taille_npa = texte_bulle_taille_npp = texte_bulle_taille_rp = texte_bulle_taille_aps = texte_bulle_taille_mps = texte_bulle_taille_rpe = texte_bulle_taille_nape = texte_bulle_taille_nppe = texte_bulle_taille_rc = texte_bulle_taille_vcs = texte_bulle_taille_vmc = 9

##### Section 1 Nouveau patient #####
## class nouv_pat ##
#entete_taille_np = 10                      # taille des labels
#texte_bulle_taille_np = 12                 # taille du texte dans les bulles
entry_largeur_np = 30                       # largeur des cases entry (p.ex. nom)
texte_bulle_largeur_np = 30                 # largeur des bulles text (p.ex adresse)
texte_bulle_haut_np1 = 5                    # hauteur des bulles medecins, adresse et remarques
texte_bulle_haut_np2 = 8                    # hauteur de la bulle autres medecins
## class nouv_1ere_anamnese, anamnese ##
#entete_taille_npa = 10                     # taille des labels
#texte_bulle_taille_npa = 12                # taille du texte dans les bulles
texte_bulle_haut_npa = 5                    # hauteur des bulles (p.ex. ATCD)
texte_bulle_largeur_npa = 50                # largeur des bulles (p.ex ATCD)
texte_bulle_haut_npa2 = 12                  # hauteur de la bulle examen paracliniques
texte_bulle_largeur_npa2 = 30               # largeur de la bulle examens paracliniques et etat general
texte_bulle_largeur_npa3 = 102            # largeur de la bulle motif de consultation
texte_bulle_haut_npa4 = 12                  # hauteur de la bulle etat general
## class nouv_exam_phys, exam phys ##
#entete_taille_npp = 10                     # taille des labels
#texte_bulle_taille_npp = 12                # taille du texte dans les bulles
texte_bulle_largeur_npp = 60                # largeur des bulles
texte_bulle_haut_npp1 = 7                   # hauteur des bulles important et paye
texte_bulle_haut_npp2 = 8                   # hauteur des bulles traitement et remarques
texte_bulle_haut_npp3 = 18                  # hauteur des bulles examen physique
##### #####

##### Section 2 Modifier la fiche d'un patient #####
## class recherche_patient ##
#entete_taille_rp = 10                      # taille des labels
#texte_bulle_taille_rp = 12                 # taille du texte dans les bulles
liste_largeur_rp = 75                     # largeur de la liste box
liste_hauteur_rp = 20                     # hauteur de la liste box
## class affiche_patient_selectionne ##
#entete_taille_aps = 10                   # taille des labels
#texte_bulle_taille_aps = 12              # taille du texte dans les bulles
bulle_haut_aps = 5                        # hauteur des bulles de texte
bulle_larg_aps = 30                       # largeur des bulles de texte
## class modif_patient_selectionne ##
#entete_taille_mps = 10                   # taille des labels
#texte_bulle_taille_mps = 12              # taille du texte dans les bulles
bulle_haut_mps = 5                        # hauteur des bulles de texte
bulle_larg_mps = 30                       # largeur des bulles de texte
texte_bulle_larg_mps = 30                         # largeur des bulles
entry_larg_mps = 30                       # largeur des entry textes
texte_bulle_haut_mps = 5                          # hauteur des bulles
##### #####

##### Section 3 Nouvelle consultation (patient existant) #####
## class recherche_pe ##
#entete_taille_rpe = 10
#texte_bulle_taille_rpe = 12
liste_largeur_rpe = 75
liste_hauteur_rpe = 20
## class nouv_1ere_anamnese_pe, anamnese_pe ##
#entete_taille_nape = 10
#texte_bulle_taille_nape = 12
bulle_haut_nape = 5                        # hauteur des bulles (p.ex. ATCD)
bulle_larg_nape = 50                       # largeur des bulles (p.ex ATCD)
bulle_haut_nape2 = 12                      # hauteur de la bulle examen paracliniques
bulle_larg_nape2 = 30                      # largeur de la bulle examens paracliniques et etat general
bulle_larg_nape3 = 102                   # largeur de la bulle motif de consultation
bulle_haut_nape4 = 12                      # hauteur de la bulle etat general
## class nouv_exam_phys_pe, exam_phys_pe ##
#entete_taille_nppe = 10
#texte_bulle_taille_nppe = 12
bulle_haut_nppe = 18                      # bulle examen physique
bulle_larg_nppe = 50
bulle_haut_nppe2 = 8                      # bulle traitement
bulle_larg_nppe2 = 50
bulle_haut_nppe3 = 8                      # bulle remarques
bulle_larg_nppe3 = 50
bulle_haut_nppe4 = 7                      # bulle important
bulle_larg_nppe4 = 50
bulle_haut_nppe5 = 7                      # bulle paye
bulle_larg_nppe5 = 50
##### #####

##### Section 4 Modifier une consultation #####
## class recherche_consult, affiche_consult_selectionne ##
#entete_taille_rc = 10
#texte_bulle_taille_rc = 12
liste_largeur_rc = 75
liste_hauteur_rc = 20
## class voir_consult_suite ##
#entete_taille_vcs = 10
#texte_bulle_taille_vcs = 12
liste_largeur_vcs = 120
liste_hauteur_vcs = 40
## class voir_consult, modif_consult ##
#entete_taille_vmc = 10
#texte_bulle_taille_vmc = 12
bulle_haut_vmc = 4                         # bulle autres
bulle_larg_vmc = 45
bulle_haut_vmc2 = 10                       # bulle examen physique et examens paracliniques
##### #####
