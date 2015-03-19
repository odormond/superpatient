-- MySQL dump 10.13  Distrib 5.5.40, for debian-linux-gnu (i686)
--
-- Host: localhost    Database: basicpatient
-- ------------------------------------------------------
-- Server version	5.5.40-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `consultations`
--

DROP TABLE IF EXISTS `consultations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `consultations` (
  `id_consult` int(11) NOT NULL DEFAULT '0',
  `id` mediumint(9) DEFAULT NULL,
  `date_consult` date DEFAULT NULL,
  `MC` text,
  `EG` text,
  `APT_thorax` text,
  `APT_abdomen` text,
  `APT_tete` text,
  `APT_MS` text,
  `APT_MI` text,
  `APT_system` text,
  `A_osteo` text,
  `exam_phys` text,
  `traitement` text,
  `divers` text,
  `exam_pclin` text,
  `paye` text,
  PRIMARY KEY (`id_consult`),
  KEY `id_consult_id` (`id`,`id_consult`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consultations`
--

LOCK TABLES `consultations` WRITE;
/*!40000 ALTER TABLE `consultations` DISABLE KEYS */;
/*!40000 ALTER TABLE `consultations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medical`
--

DROP TABLE IF EXISTS `medical`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `medical` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Salutations` varchar(15) NOT NULL DEFAULT '',
  `Titre` varchar(50) DEFAULT NULL,
  `Prénom` varchar(50) NOT NULL DEFAULT '',
  `Nom` varchar(50) NOT NULL DEFAULT '',
  `NomSociété` varchar(50) DEFAULT NULL,
  `Adresse` varchar(200) NOT NULL DEFAULT '',
  `CodePostal` varchar(20) DEFAULT NULL,
  `Ville` varchar(50) NOT NULL DEFAULT '',
  `NuméroTéléphone` varchar(30) DEFAULT NULL,
  `NuméroPortable` varchar(30) DEFAULT NULL,
  `NuméroFax` varchar(30) DEFAULT NULL,
  `AdresseEmail` varchar(50) DEFAULT NULL,
  `Notes` mediumtext,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical`
--

LOCK TABLES `medical` WRITE;
/*!40000 ALTER TABLE `medical` DISABLE KEYS */;
/*!40000 ALTER TABLE `medical` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `patients` (
  `id` mediumint(9) NOT NULL DEFAULT '0',
  `date_ouverture` date DEFAULT NULL,
  `therapeute` varchar(20) DEFAULT NULL,
  `sex` varchar(8) DEFAULT NULL,
  `nom` varchar(30) DEFAULT NULL,
  `prenom` varchar(30) DEFAULT NULL,
  `date_naiss` date DEFAULT NULL,
  `ATCD_perso` text,
  `ATCD_fam` text,
  `medecin` text,
  `autre_medecin` text,
  `phone` varchar(30) DEFAULT NULL,
  `portable` varchar(30) DEFAULT NULL,
  `profes_phone` varchar(30) DEFAULT NULL,
  `mail` varchar(40) DEFAULT NULL,
  `adresse` text,
  `ass_compl` varchar(30) DEFAULT NULL,
  `profes` varchar(30) DEFAULT NULL,
  `etat` varchar(30) DEFAULT NULL,
  `envoye` varchar(30) DEFAULT NULL,
  `divers` text,
  `important` text,
  PRIMARY KEY (`id`),
  KEY `nom_prenom` (`nom`(15),`prenom`(15))
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patients`
--

LOCK TABLES `patients` WRITE;
/*!40000 ALTER TABLE `patients` DISABLE KEYS */;
/*!40000 ALTER TABLE `patients` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-11-24 12:55:05
