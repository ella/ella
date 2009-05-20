-- MySQL dump 10.13  Distrib 5.1.34, for pc-linux-gnu (i686)
--
-- Host: localhost    Database: ella
-- ------------------------------------------------------
-- Server version	5.1.34

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
-- Current Database: `ella`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `ella` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_czech_ci */;

USE `ella`;

--
-- Table structure for table `adverts_categorysectionmapping`
--

DROP TABLE IF EXISTS `adverts_categorysectionmapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `adverts_categorysectionmapping` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) NOT NULL,
  `section_name` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `category_id` (`category_id`),
  CONSTRAINT `category_id_refs_id_2deea27` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `adverts_categorysectionmapping`
--

LOCK TABLES `adverts_categorysectionmapping` WRITE;
/*!40000 ALTER TABLE `adverts_categorysectionmapping` DISABLE KEYS */;
/*!40000 ALTER TABLE `adverts_categorysectionmapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `adverts_siteservermapping`
--

DROP TABLE IF EXISTS `adverts_siteservermapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `adverts_siteservermapping` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `site_id` int(11) NOT NULL,
  `server_name` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `site_id` (`site_id`),
  CONSTRAINT `site_id_refs_id_69baa80e` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `adverts_siteservermapping`
--

LOCK TABLES `adverts_siteservermapping` WRITE;
/*!40000 ALTER TABLE `adverts_siteservermapping` DISABLE KEYS */;
/*!40000 ALTER TABLE `adverts_siteservermapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `articles_article`
--

DROP TABLE IF EXISTS `articles_article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `articles_article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `upper_title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `perex` longtext COLLATE utf8_czech_ci NOT NULL,
  `created` datetime NOT NULL DEFAULT '2009-05-20 17:58:03',
  `updated` datetime DEFAULT NULL,
  `source_id` int(11) DEFAULT NULL,
  `category_id` int(11) NOT NULL,
  `photo_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `articles_article_slug` (`slug`),
  KEY `articles_article_created` (`created`),
  KEY `articles_article_source_id` (`source_id`),
  KEY `articles_article_category_id` (`category_id`),
  KEY `articles_article_photo_id` (`photo_id`),
  CONSTRAINT `category_id_refs_id_2b88970a` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `photo_id_refs_id_573d4575` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`),
  CONSTRAINT `source_id_refs_id_51b5a8eb` FOREIGN KEY (`source_id`) REFERENCES `core_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `articles_article`
--

LOCK TABLES `articles_article` WRITE;
/*!40000 ALTER TABLE `articles_article` DISABLE KEYS */;
/*!40000 ALTER TABLE `articles_article` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `articles_article_authors`
--

DROP TABLE IF EXISTS `articles_article_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `articles_article_authors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `articles_article_authors_article_id` (`article_id`),
  KEY `articles_article_authors_author_id` (`author_id`),
  CONSTRAINT `article_id_refs_id_1bb2108a` FOREIGN KEY (`article_id`) REFERENCES `articles_article` (`id`),
  CONSTRAINT `author_id_refs_id_23a52912` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `articles_article_authors`
--

LOCK TABLES `articles_article_authors` WRITE;
/*!40000 ALTER TABLE `articles_article_authors` DISABLE KEYS */;
/*!40000 ALTER TABLE `articles_article_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `articles_articlecontents`
--

DROP TABLE IF EXISTS `articles_articlecontents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `articles_articlecontents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_id` int(11) NOT NULL,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `articles_articlecontents_article_id` (`article_id`),
  CONSTRAINT `article_id_refs_id_1f8b5b91` FOREIGN KEY (`article_id`) REFERENCES `articles_article` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `articles_articlecontents`
--

LOCK TABLES `articles_articlecontents` WRITE;
/*!40000 ALTER TABLE `articles_articlecontents` DISABLE KEYS */;
/*!40000 ALTER TABLE `articles_articlecontents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `articles_infobox`
--

DROP TABLE IF EXISTS `articles_infobox`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `articles_infobox` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `created` datetime NOT NULL DEFAULT '2009-05-20 17:58:03',
  `updated` datetime DEFAULT NULL,
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `articles_infobox`
--

LOCK TABLES `articles_infobox` WRITE;
/*!40000 ALTER TABLE `articles_infobox` DISABLE KEYS */;
/*!40000 ALTER TABLE `articles_infobox` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_astrolex`
--

DROP TABLE IF EXISTS `astrology_astrolex`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_astrolex` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `term` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_astrolex`
--

LOCK TABLES `astrology_astrolex` WRITE;
/*!40000 ALTER TABLE `astrology_astrolex` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_astrolex` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_birthperiod`
--

DROP TABLE IF EXISTS `astrology_birthperiod`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_birthperiod` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_id` int(11) NOT NULL,
  `start_day` date NOT NULL,
  `end_day` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `astrology_birthperiod_sign_id` (`sign_id`),
  CONSTRAINT `sign_id_refs_id_79c9a2c7` FOREIGN KEY (`sign_id`) REFERENCES `astrology_sign` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_birthperiod`
--

LOCK TABLES `astrology_birthperiod` WRITE;
/*!40000 ALTER TABLE `astrology_birthperiod` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_birthperiod` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_horoscope`
--

DROP TABLE IF EXISTS `astrology_horoscope`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_horoscope` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `logo_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `astrology_horoscope_logo_id` (`logo_id`),
  CONSTRAINT `logo_id_refs_id_1e18a2a7` FOREIGN KEY (`logo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_horoscope`
--

LOCK TABLES `astrology_horoscope` WRITE;
/*!40000 ALTER TABLE `astrology_horoscope` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_horoscope` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_lifenumber`
--

DROP TABLE IF EXISTS `astrology_lifenumber`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_lifenumber` (
  `life_no` smallint(5) unsigned NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`life_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_lifenumber`
--

LOCK TABLES `astrology_lifenumber` WRITE;
/*!40000 ALTER TABLE `astrology_lifenumber` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_lifenumber` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_lunardiary`
--

DROP TABLE IF EXISTS `astrology_lunardiary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_lunardiary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) NOT NULL,
  `perex` longtext COLLATE utf8_czech_ci NOT NULL,
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  `publish_date` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `astrology_lunardiary_category_id_76a0eb81` (`category_id`,`publish_date`),
  KEY `astrology_lunardiary_category_id` (`category_id`),
  CONSTRAINT `category_id_refs_id_7b73e5c3` FOREIGN KEY (`category_id`) REFERENCES `astrology_lunardiarycategory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_lunardiary`
--

LOCK TABLES `astrology_lunardiary` WRITE;
/*!40000 ALTER TABLE `astrology_lunardiary` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_lunardiary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_lunardiarycategory`
--

DROP TABLE IF EXISTS `astrology_lunardiarycategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_lunardiarycategory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `ordering` smallint(5) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_lunardiarycategory`
--

LOCK TABLES `astrology_lunardiarycategory` WRITE;
/*!40000 ALTER TABLE `astrology_lunardiarycategory` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_lunardiarycategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_moon`
--

DROP TABLE IF EXISTS `astrology_moon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_moon` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_id` int(11) NOT NULL,
  `title` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sign_id` (`sign_id`),
  CONSTRAINT `sign_id_refs_id_156a7d57` FOREIGN KEY (`sign_id`) REFERENCES `astrology_sign` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_moon`
--

LOCK TABLES `astrology_moon` WRITE;
/*!40000 ALTER TABLE `astrology_moon` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_moon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_numerologygrid`
--

DROP TABLE IF EXISTS `astrology_numerologygrid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_numerologygrid` (
  `base_no` smallint(5) unsigned NOT NULL,
  `title` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `perex` longtext COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`base_no`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_numerologygrid`
--

LOCK TABLES `astrology_numerologygrid` WRITE;
/*!40000 ALTER TABLE `astrology_numerologygrid` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_numerologygrid` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_prognosis`
--

DROP TABLE IF EXISTS `astrology_prognosis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_prognosis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_id` int(11) NOT NULL,
  `duration_id` int(11) NOT NULL,
  `type_id` int(11) NOT NULL,
  `start_day` date NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `astrology_prognosis_sign_id_423a042` (`sign_id`,`duration_id`,`type_id`,`start_day`),
  KEY `astrology_prognosis_sign_id` (`sign_id`),
  KEY `astrology_prognosis_duration_id` (`duration_id`),
  KEY `astrology_prognosis_type_id` (`type_id`),
  CONSTRAINT `duration_id_refs_id_523fe7b5` FOREIGN KEY (`duration_id`) REFERENCES `astrology_prognosisduration` (`id`),
  CONSTRAINT `sign_id_refs_id_63b4f2f5` FOREIGN KEY (`sign_id`) REFERENCES `astrology_sign` (`id`),
  CONSTRAINT `type_id_refs_id_11e5d871` FOREIGN KEY (`type_id`) REFERENCES `astrology_prognosistype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_prognosis`
--

LOCK TABLES `astrology_prognosis` WRITE;
/*!40000 ALTER TABLE `astrology_prognosis` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_prognosis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_prognosisduration`
--

DROP TABLE IF EXISTS `astrology_prognosisduration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_prognosisduration` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `duration` smallint(5) unsigned NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `ordering` smallint(5) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_prognosisduration`
--

LOCK TABLES `astrology_prognosisduration` WRITE;
/*!40000 ALTER TABLE `astrology_prognosisduration` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_prognosisduration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_prognosistype`
--

DROP TABLE IF EXISTS `astrology_prognosistype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_prognosistype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `ordering` smallint(5) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_prognosistype`
--

LOCK TABLES `astrology_prognosistype` WRITE;
/*!40000 ALTER TABLE `astrology_prognosistype` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_prognosistype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_sign`
--

DROP TABLE IF EXISTS `astrology_sign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_sign` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `horoscope_id` int(11) NOT NULL,
  `title` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `perex` longtext COLLATE utf8_czech_ci NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  `logo_id` int(11) DEFAULT NULL,
  `ordering` smallint(5) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `astrology_sign_horoscope_id_40f341c9` (`horoscope_id`,`slug`),
  KEY `astrology_sign_horoscope_id` (`horoscope_id`),
  KEY `astrology_sign_slug` (`slug`),
  KEY `astrology_sign_logo_id` (`logo_id`),
  CONSTRAINT `horoscope_id_refs_id_285d9411` FOREIGN KEY (`horoscope_id`) REFERENCES `astrology_horoscope` (`id`),
  CONSTRAINT `logo_id_refs_id_1e311c81` FOREIGN KEY (`logo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_sign`
--

LOCK TABLES `astrology_sign` WRITE;
/*!40000 ALTER TABLE `astrology_sign` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_sign` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_signcompatibility`
--

DROP TABLE IF EXISTS `astrology_signcompatibility`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_signcompatibility` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_male_id` int(11) NOT NULL,
  `sign_female_id` int(11) NOT NULL,
  `compat_percent` smallint(5) unsigned NOT NULL,
  `compat_text` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `astrology_signcompatibility_sign_male_id_490fe2` (`sign_male_id`,`sign_female_id`),
  KEY `astrology_signcompatibility_sign_male_id` (`sign_male_id`),
  KEY `astrology_signcompatibility_sign_female_id` (`sign_female_id`),
  CONSTRAINT `sign_female_id_refs_id_16240c56` FOREIGN KEY (`sign_female_id`) REFERENCES `astrology_sign` (`id`),
  CONSTRAINT `sign_male_id_refs_id_16240c56` FOREIGN KEY (`sign_male_id`) REFERENCES `astrology_sign` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_signcompatibility`
--

LOCK TABLES `astrology_signcompatibility` WRITE;
/*!40000 ALTER TABLE `astrology_signcompatibility` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_signcompatibility` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_signdescription`
--

DROP TABLE IF EXISTS `astrology_signdescription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_signdescription` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_id` int(11) NOT NULL,
  `type_id` int(11) NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `astrology_signdescription_sign_id_6185feec` (`sign_id`,`type_id`),
  KEY `astrology_signdescription_sign_id` (`sign_id`),
  KEY `astrology_signdescription_type_id` (`type_id`),
  CONSTRAINT `sign_id_refs_id_5141f712` FOREIGN KEY (`sign_id`) REFERENCES `astrology_sign` (`id`),
  CONSTRAINT `type_id_refs_id_2333e57f` FOREIGN KEY (`type_id`) REFERENCES `astrology_signdescriptiontype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_signdescription`
--

LOCK TABLES `astrology_signdescription` WRITE;
/*!40000 ALTER TABLE `astrology_signdescription` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_signdescription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_signdescriptiontype`
--

DROP TABLE IF EXISTS `astrology_signdescriptiontype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_signdescriptiontype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `logo_id` int(11) DEFAULT NULL,
  `ordering` smallint(5) unsigned NOT NULL DEFAULT '0',
  `visible` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `astrology_signdescriptiontype_logo_id` (`logo_id`),
  CONSTRAINT `logo_id_refs_id_326537ac` FOREIGN KEY (`logo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_signdescriptiontype`
--

LOCK TABLES `astrology_signdescriptiontype` WRITE;
/*!40000 ALTER TABLE `astrology_signdescriptiontype` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_signdescriptiontype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_stone`
--

DROP TABLE IF EXISTS `astrology_stone`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_stone` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(96) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_stone`
--

LOCK TABLES `astrology_stone` WRITE;
/*!40000 ALTER TABLE `astrology_stone` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_stone` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `astrology_stoneforsign`
--

DROP TABLE IF EXISTS `astrology_stoneforsign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `astrology_stoneforsign` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sign_id` int(11) NOT NULL,
  `stone_id` int(11) NOT NULL,
  `ordering` smallint(5) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `astrology_stoneforsign_sign_id_d707219` (`sign_id`,`stone_id`),
  KEY `astrology_stoneforsign_sign_id` (`sign_id`),
  KEY `astrology_stoneforsign_stone_id` (`stone_id`),
  CONSTRAINT `sign_id_refs_id_d24d491` FOREIGN KEY (`sign_id`) REFERENCES `astrology_sign` (`id`),
  CONSTRAINT `stone_id_refs_id_6d5c1d66` FOREIGN KEY (`stone_id`) REFERENCES `astrology_stone` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `astrology_stoneforsign`
--

LOCK TABLES `astrology_stoneforsign` WRITE;
/*!40000 ALTER TABLE `astrology_stoneforsign` DISABLE KEYS */;
/*!40000 ALTER TABLE `astrology_stoneforsign` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attachments_attachment`
--

DROP TABLE IF EXISTS `attachments_attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attachments_attachment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `photo_id` int(11) DEFAULT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `created` datetime NOT NULL DEFAULT '2009-05-20 17:58:41',
  `attachment` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `type_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `attachments_attachment_slug` (`slug`),
  KEY `attachments_attachment_photo_id` (`photo_id`),
  KEY `attachments_attachment_type_id` (`type_id`),
  CONSTRAINT `photo_id_refs_id_6a49a731` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`),
  CONSTRAINT `type_id_refs_id_58c996cc` FOREIGN KEY (`type_id`) REFERENCES `attachments_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attachments_attachment`
--

LOCK TABLES `attachments_attachment` WRITE;
/*!40000 ALTER TABLE `attachments_attachment` DISABLE KEYS */;
/*!40000 ALTER TABLE `attachments_attachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attachments_type`
--

DROP TABLE IF EXISTS `attachments_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attachments_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `mimetype` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `attachments_type_name_aed6fdc` (`name`,`mimetype`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attachments_type`
--

LOCK TABLES `attachments_type` WRITE;
/*!40000 ALTER TABLE `attachments_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `attachments_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `permission_id_refs_id_5886d21f` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_5886d21f` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `group_id_refs_id_3cea63fe` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_message`
--

DROP TABLE IF EXISTS `auth_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `message` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_message_user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_650f49a6` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_message`
--

LOCK TABLES `auth_message` WRITE;
/*!40000 ALTER TABLE `auth_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_content_type_id` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_728de91f` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=424 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add message',4,'add_message'),(11,'Can change message',4,'change_message'),(12,'Can delete message',4,'delete_message'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add site',7,'add_site'),(20,'Can change site',7,'change_site'),(21,'Can delete site',7,'delete_site'),(22,'Can add redirect',8,'add_redirect'),(23,'Can change redirect',8,'change_redirect'),(24,'Can delete redirect',8,'delete_redirect'),(25,'Can add log entry',9,'add_logentry'),(26,'Can change log entry',9,'change_logentry'),(27,'Can delete log entry',9,'delete_logentry'),(28,'Can add newsletter',10,'add_newsletter'),(29,'Can change newsletter',10,'change_newsletter'),(30,'Can delete newsletter',10,'delete_newsletter'),(31,'Can add recipient',11,'add_recipient'),(32,'Can change recipient',11,'change_recipient'),(33,'Can delete recipient',11,'delete_recipient'),(34,'Can add format',12,'add_format'),(35,'Can change format',12,'change_format'),(36,'Can delete format',12,'delete_format'),(37,'Can add source',13,'add_source'),(38,'Can change source',13,'change_source'),(39,'Can delete source',13,'delete_source'),(40,'Can add target',14,'add_target'),(41,'Can change target',14,'change_target'),(42,'Can delete target',14,'delete_target'),(43,'Can add migration history',15,'add_migrationhistory'),(44,'Can change migration history',15,'change_migrationhistory'),(45,'Can delete migration history',15,'delete_migrationhistory'),(46,'Can add Eshop',16,'add_eshop'),(47,'Can change Eshop',16,'change_eshop'),(48,'Can delete Eshop',16,'delete_eshop'),(49,'Can add Feedset',17,'add_feedset'),(50,'Can change Feedset',17,'change_feedset'),(51,'Can delete Feedset',17,'delete_feedset'),(52,'Can add Category',18,'add_category'),(53,'Can change Category',18,'change_category'),(54,'Can delete Category',18,'delete_category'),(55,'Can add Target group',19,'add_targetgroup'),(56,'Can change Target group',19,'change_targetgroup'),(57,'Can delete Target group',19,'delete_targetgroup'),(58,'Can add Present',20,'add_present'),(59,'Can change Present',20,'change_present'),(60,'Can delete Present',20,'delete_present'),(61,'Can add Inquiry of Santa',21,'add_inquiryofsanta'),(62,'Can change Inquiry of Santa',21,'change_inquiryofsanta'),(63,'Can delete Inquiry of Santa',21,'delete_inquiryofsanta'),(64,'Can add Author',22,'add_author'),(65,'Can change Author',22,'change_author'),(66,'Can delete Author',22,'delete_author'),(67,'Can add Source',23,'add_source'),(68,'Can change Source',23,'change_source'),(69,'Can delete Source',23,'delete_source'),(70,'Can add Category',24,'add_category'),(71,'Can change Category',24,'change_category'),(72,'Can delete Category',24,'delete_category'),(73,'Can add Placement',25,'add_placement'),(74,'Can change Placement',25,'change_placement'),(75,'Can delete Placement',25,'delete_placement'),(76,'Can add Listing',26,'add_listing'),(77,'Can change Listing',26,'change_listing'),(78,'Can delete Listing',26,'delete_listing'),(79,'Can add Hit Count',27,'add_hitcount'),(80,'Can change Hit Count',27,'change_hitcount'),(81,'Can delete Hit Count',27,'delete_hitcount'),(82,'Can add Related',28,'add_related'),(83,'Can change Related',28,'change_related'),(84,'Can delete Related',28,'delete_related'),(85,'Can view Author',22,'view_author'),(86,'Can view Source',23,'view_source'),(87,'Can view Category',24,'view_category'),(88,'Can view Placement',25,'view_placement'),(89,'Can view Listing',26,'view_listing'),(90,'Can view Hit Count',27,'view_hitcount'),(91,'Can view Related',28,'view_related'),(92,'Can add Photo',29,'add_photo'),(93,'Can change Photo',29,'change_photo'),(94,'Can delete Photo',29,'delete_photo'),(95,'Can add Format',30,'add_format'),(96,'Can change Format',30,'change_format'),(97,'Can delete Format',30,'delete_format'),(98,'Can add Formated photo',31,'add_formatedphoto'),(99,'Can change Formated photo',31,'change_formatedphoto'),(100,'Can delete Formated photo',31,'delete_formatedphoto'),(101,'Can view Photo',29,'view_photo'),(102,'Can view Format',30,'view_format'),(103,'Can view Formated photo',31,'view_formatedphoto'),(104,'Can add Info box',32,'add_infobox'),(105,'Can change Info box',32,'change_infobox'),(106,'Can delete Info box',32,'delete_infobox'),(107,'Can add Article',33,'add_article'),(108,'Can change Article',33,'change_article'),(109,'Can delete Article',33,'delete_article'),(110,'Can add Article content',34,'add_articlecontents'),(111,'Can change Article content',34,'change_articlecontents'),(112,'Can delete Article content',34,'delete_articlecontents'),(113,'Can view Info box',32,'view_infobox'),(114,'Can view Article',33,'view_article'),(115,'Can view Article content',34,'view_articlecontents'),(116,'Can add Comment Options',35,'add_commentoptions'),(117,'Can change Comment Options',35,'change_commentoptions'),(118,'Can delete Comment Options',35,'delete_commentoptions'),(119,'Can add Comment',36,'add_comment'),(120,'Can change Comment',36,'change_comment'),(121,'Can delete Comment',36,'delete_comment'),(122,'Can add Banned User',37,'add_banneduser'),(123,'Can change Banned User',37,'change_banneduser'),(124,'Can delete Banned User',37,'delete_banneduser'),(125,'Can add banned ip',38,'add_bannedip'),(126,'Can change banned ip',38,'change_bannedip'),(127,'Can delete banned ip',38,'delete_bannedip'),(128,'Can view Comment Options',35,'view_commentoptions'),(129,'Can view Comment',36,'view_comment'),(130,'Can view Banned User',37,'view_banneduser'),(131,'Can view banned ip',38,'view_bannedip'),(132,'Can add Template',39,'add_dbtemplate'),(133,'Can change Template',39,'change_dbtemplate'),(134,'Can delete Template',39,'delete_dbtemplate'),(135,'Can add Template block',40,'add_templateblock'),(136,'Can change Template block',40,'change_templateblock'),(137,'Can delete Template block',40,'delete_templateblock'),(138,'Can view Template',39,'view_dbtemplate'),(139,'Can view Template block',40,'view_templateblock'),(140,'Can add Gallery',41,'add_gallery'),(141,'Can change Gallery',41,'change_gallery'),(142,'Can delete Gallery',41,'delete_gallery'),(143,'Can add Gallery item',42,'add_galleryitem'),(144,'Can change Gallery item',42,'change_galleryitem'),(145,'Can delete Gallery item',42,'delete_galleryitem'),(146,'Can view Gallery',41,'view_gallery'),(147,'Can view Gallery item',42,'view_galleryitem'),(148,'Can add Contest',43,'add_contest'),(149,'Can change Contest',43,'change_contest'),(150,'Can delete Contest',43,'delete_contest'),(151,'Can add Quiz',44,'add_quiz'),(152,'Can change Quiz',44,'change_quiz'),(153,'Can delete Quiz',44,'delete_quiz'),(154,'Can add Question',45,'add_question'),(155,'Can change Question',45,'change_question'),(156,'Can delete Question',45,'delete_question'),(157,'Can add Poll',46,'add_poll'),(158,'Can change Poll',46,'change_poll'),(159,'Can delete Poll',46,'delete_poll'),(160,'Can add Choice',47,'add_choice'),(161,'Can change Choice',47,'change_choice'),(162,'Can delete Choice',47,'delete_choice'),(163,'Can add Vote',48,'add_vote'),(164,'Can change Vote',48,'change_vote'),(165,'Can delete Vote',48,'delete_vote'),(166,'Can add Contestant',49,'add_contestant'),(167,'Can change Contestant',49,'change_contestant'),(168,'Can delete Contestant',49,'delete_contestant'),(169,'Can add Result',50,'add_result'),(170,'Can change Result',50,'change_result'),(171,'Can delete Result',50,'delete_result'),(172,'Can view Contest',43,'view_contest'),(173,'Can view Quiz',44,'view_quiz'),(174,'Can view Question',45,'view_question'),(175,'Can view Poll',46,'view_poll'),(176,'Can view Choice',47,'view_choice'),(177,'Can view Vote',48,'view_vote'),(178,'Can view Contestant',49,'view_contestant'),(179,'Can view Result',50,'view_result'),(180,'Can add tag',51,'add_tag'),(181,'Can change tag',51,'change_tag'),(182,'Can delete tag',51,'delete_tag'),(183,'Can add tagged item',52,'add_taggeditem'),(184,'Can change tagged item',52,'change_taggeditem'),(185,'Can delete tagged item',52,'delete_taggeditem'),(186,'Can view tag',51,'view_tag'),(187,'Can view tagged item',52,'view_taggeditem'),(188,'Can add Model weight',53,'add_modelweight'),(189,'Can change Model weight',53,'change_modelweight'),(190,'Can delete Model weight',53,'delete_modelweight'),(191,'Can add Total rate',54,'add_totalrate'),(192,'Can change Total rate',54,'change_totalrate'),(193,'Can delete Total rate',54,'delete_totalrate'),(194,'Can add Aggregation',55,'add_agg'),(195,'Can change Aggregation',55,'change_agg'),(196,'Can delete Aggregation',55,'delete_agg'),(197,'Can add Rating',56,'add_rating'),(198,'Can change Rating',56,'change_rating'),(199,'Can delete Rating',56,'delete_rating'),(200,'Can view Model weight',53,'view_modelweight'),(201,'Can view Total rate',54,'view_totalrate'),(202,'Can view Aggregation',55,'view_agg'),(203,'Can view Rating',56,'view_rating'),(204,'Can add atlas export',57,'add_atlasexport'),(205,'Can change atlas export',57,'change_atlasexport'),(206,'Can delete atlas export',57,'delete_atlasexport'),(207,'Can view atlas export',57,'view_atlasexport'),(208,'Can add Server',58,'add_server'),(209,'Can change Server',58,'change_server'),(210,'Can delete Server',58,'delete_server'),(211,'Can add Server item',59,'add_serveritem'),(212,'Can change Server item',59,'change_serveritem'),(213,'Can delete Server item',59,'delete_serveritem'),(214,'Can view Server',58,'view_server'),(215,'Can view Server item',59,'view_serveritem'),(216,'Can add Interviewee',60,'add_interviewee'),(217,'Can change Interviewee',60,'change_interviewee'),(218,'Can delete Interviewee',60,'delete_interviewee'),(219,'Can add Interview',61,'add_interview'),(220,'Can change Interview',61,'change_interview'),(221,'Can delete Interview',61,'delete_interview'),(222,'Can add Question',62,'add_question'),(223,'Can change Question',62,'change_question'),(224,'Can delete Question',62,'delete_question'),(225,'Can add Answer',63,'add_answer'),(226,'Can change Answer',63,'change_answer'),(227,'Can delete Answer',63,'delete_answer'),(228,'Can view Interviewee',60,'view_interviewee'),(229,'Can view Interview',61,'view_interview'),(230,'Can view Question',62,'view_question'),(231,'Can view Answer',63,'view_answer'),(232,'Can add position',64,'add_position'),(233,'Can change position',64,'change_position'),(234,'Can delete position',64,'delete_position'),(235,'Can view position',64,'view_position'),(236,'Can add Category Lock',65,'add_categorylock'),(237,'Can change Category Lock',65,'change_categorylock'),(238,'Can delete Category Lock',65,'delete_categorylock'),(239,'Can view Category Lock',65,'view_categorylock'),(240,'Can add mail',66,'add_mail'),(241,'Can change mail',66,'change_mail'),(242,'Can delete mail',66,'delete_mail'),(243,'Can view mail',66,'view_mail'),(244,'Can add Type',67,'add_type'),(245,'Can change Type',67,'change_type'),(246,'Can delete Type',67,'delete_type'),(247,'Can add Attachment',68,'add_attachment'),(248,'Can change Attachment',68,'change_attachment'),(249,'Can delete Attachment',68,'delete_attachment'),(250,'Can view Type',67,'view_type'),(251,'Can view Attachment',68,'view_attachment'),(252,'Can add Serie',69,'add_serie'),(253,'Can change Serie',69,'change_serie'),(254,'Can delete Serie',69,'delete_serie'),(255,'Can add Serie part',70,'add_seriepart'),(256,'Can change Serie part',70,'change_seriepart'),(257,'Can delete Serie part',70,'delete_seriepart'),(258,'Can view Serie',69,'view_serie'),(259,'Can view Serie part',70,'view_seriepart'),(260,'Can add Media',71,'add_media'),(261,'Can change Media',71,'change_media'),(262,'Can delete Media',71,'delete_media'),(263,'Can add section',72,'add_section'),(264,'Can change section',72,'change_section'),(265,'Can delete section',72,'delete_section'),(266,'Can add usage',73,'add_usage'),(267,'Can change usage',73,'change_usage'),(268,'Can delete usage',73,'delete_usage'),(269,'Can view Media',71,'view_media'),(270,'Can view section',72,'view_section'),(271,'Can view usage',73,'view_usage'),(272,'Can add Instruction',74,'add_instruction'),(273,'Can change Instruction',74,'change_instruction'),(274,'Can delete Instruction',74,'delete_instruction'),(275,'Can view Instruction',74,'view_instruction'),(276,'Can add Cooking type',75,'add_cookingtype'),(277,'Can change Cooking type',75,'change_cookingtype'),(278,'Can delete Cooking type',75,'delete_cookingtype'),(279,'Can add Cuisine',76,'add_cuisine'),(280,'Can change Cuisine',76,'change_cuisine'),(281,'Can delete Cuisine',76,'delete_cuisine'),(282,'Can add Nutrient group',77,'add_nutrientgroup'),(283,'Can change Nutrient group',77,'change_nutrientgroup'),(284,'Can delete Nutrient group',77,'delete_nutrientgroup'),(285,'Can add Nutrient',78,'add_nutrient'),(286,'Can change Nutrient',78,'change_nutrient'),(287,'Can delete Nutrient',78,'delete_nutrient'),(288,'Can add Unit',79,'add_unit'),(289,'Can change Unit',79,'change_unit'),(290,'Can delete Unit',79,'delete_unit'),(291,'Can add Unit conversion',80,'add_unitconversion'),(292,'Can change Unit conversion',80,'change_unitconversion'),(293,'Can delete Unit conversion',80,'delete_unitconversion'),(294,'Can add Ingredient group',81,'add_ingredientgroup'),(295,'Can change Ingredient group',81,'change_ingredientgroup'),(296,'Can delete Ingredient group',81,'delete_ingredientgroup'),(297,'Can add Ingredient',82,'add_ingredient'),(298,'Can change Ingredient',82,'change_ingredient'),(299,'Can delete Ingredient',82,'delete_ingredient'),(300,'Can add Nutrient in ingredient',83,'add_nutrientiningredient'),(301,'Can change Nutrient in ingredient',83,'change_nutrientiningredient'),(302,'Can delete Nutrient in ingredient',83,'delete_nutrientiningredient'),(303,'Can add Category photo',84,'add_recipecategoryphoto'),(304,'Can change Category photo',84,'change_recipecategoryphoto'),(305,'Can delete Category photo',84,'delete_recipecategoryphoto'),(306,'Can add Side-dish',85,'add_sidedish'),(307,'Can change Side-dish',85,'change_sidedish'),(308,'Can delete Side-dish',85,'delete_sidedish'),(309,'Can add Recipe',86,'add_recipe'),(310,'Can change Recipe',86,'change_recipe'),(311,'Can delete Recipe',86,'delete_recipe'),(312,'Can add Ingredient in recipe',87,'add_ingredientinrecipe'),(313,'Can change Ingredient in recipe',87,'change_ingredientinrecipe'),(314,'Can delete Ingredient in recipe',87,'delete_ingredientinrecipe'),(315,'Can add Recipe of day',88,'add_recipeofday'),(316,'Can change Recipe of day',88,'change_recipeofday'),(317,'Can delete Recipe of day',88,'delete_recipeofday'),(318,'Can add old recipe article redirect',89,'add_oldrecipearticleredirect'),(319,'Can change old recipe article redirect',89,'change_oldrecipearticleredirect'),(320,'Can delete old recipe article redirect',89,'delete_oldrecipearticleredirect'),(321,'Can add old recipe category redirect',90,'add_oldrecipecategoryredirect'),(322,'Can change old recipe category redirect',90,'change_oldrecipecategoryredirect'),(323,'Can delete old recipe category redirect',90,'delete_oldrecipecategoryredirect'),(324,'Can view Cooking type',75,'view_cookingtype'),(325,'Can view Cuisine',76,'view_cuisine'),(326,'Can view Nutrient group',77,'view_nutrientgroup'),(327,'Can view Nutrient',78,'view_nutrient'),(328,'Can view Unit',79,'view_unit'),(329,'Can view Unit conversion',80,'view_unitconversion'),(330,'Can view Ingredient group',81,'view_ingredientgroup'),(331,'Can view Ingredient',82,'view_ingredient'),(332,'Can view Nutrient in ingredient',83,'view_nutrientiningredient'),(333,'Can view Category photo',84,'view_recipecategoryphoto'),(334,'Can view Side-dish',85,'view_sidedish'),(335,'Can view Recipe',86,'view_recipe'),(336,'Can view Ingredient in recipe',87,'view_ingredientinrecipe'),(337,'Can view Recipe of day',88,'view_recipeofday'),(338,'Can view old recipe article redirect',89,'view_oldrecipearticleredirect'),(339,'Can view old recipe category redirect',90,'view_oldrecipecategoryredirect'),(340,'Can add Horoscope',91,'add_horoscope'),(341,'Can change Horoscope',91,'change_horoscope'),(342,'Can delete Horoscope',91,'delete_horoscope'),(343,'Can add Sign',92,'add_sign'),(344,'Can change Sign',92,'change_sign'),(345,'Can delete Sign',92,'delete_sign'),(346,'Can add Sign description type',93,'add_signdescriptiontype'),(347,'Can change Sign description type',93,'change_signdescriptiontype'),(348,'Can delete Sign description type',93,'delete_signdescriptiontype'),(349,'Can add Sign description',94,'add_signdescription'),(350,'Can change Sign description',94,'change_signdescription'),(351,'Can delete Sign description',94,'delete_signdescription'),(352,'Can add Birth period',95,'add_birthperiod'),(353,'Can change Birth period',95,'change_birthperiod'),(354,'Can delete Birth period',95,'delete_birthperiod'),(355,'Can add Sign compatibility',96,'add_signcompatibility'),(356,'Can change Sign compatibility',96,'change_signcompatibility'),(357,'Can delete Sign compatibility',96,'delete_signcompatibility'),(358,'Can add Prognosis duration',97,'add_prognosisduration'),(359,'Can change Prognosis duration',97,'change_prognosisduration'),(360,'Can delete Prognosis duration',97,'delete_prognosisduration'),(361,'Can add Prognosis type',98,'add_prognosistype'),(362,'Can change Prognosis type',98,'change_prognosistype'),(363,'Can delete Prognosis type',98,'delete_prognosistype'),(364,'Can add Prognosis',99,'add_prognosis'),(365,'Can change Prognosis',99,'change_prognosis'),(366,'Can delete Prognosis',99,'delete_prognosis'),(367,'Can add Lunar diary category',100,'add_lunardiarycategory'),(368,'Can change Lunar diary category',100,'change_lunardiarycategory'),(369,'Can delete Lunar diary category',100,'delete_lunardiarycategory'),(370,'Can add Lunar diary',101,'add_lunardiary'),(371,'Can change Lunar diary',101,'change_lunardiary'),(372,'Can delete Lunar diary',101,'delete_lunardiary'),(373,'Can add Lexicon term',102,'add_astrolex'),(374,'Can change Lexicon term',102,'change_astrolex'),(375,'Can delete Lexicon term',102,'delete_astrolex'),(376,'Can add Life number',103,'add_lifenumber'),(377,'Can change Life number',103,'change_lifenumber'),(378,'Can delete Life number',103,'delete_lifenumber'),(379,'Can add Stone',104,'add_stone'),(380,'Can change Stone',104,'change_stone'),(381,'Can delete Stone',104,'delete_stone'),(382,'Can add Stone for Sign',105,'add_stoneforsign'),(383,'Can change Stone for Sign',105,'change_stoneforsign'),(384,'Can delete Stone for Sign',105,'delete_stoneforsign'),(385,'Can add Numerology grid number',106,'add_numerologygrid'),(386,'Can change Numerology grid number',106,'change_numerologygrid'),(387,'Can delete Numerology grid number',106,'delete_numerologygrid'),(388,'Can add Moon in Sign',107,'add_moon'),(389,'Can change Moon in Sign',107,'change_moon'),(390,'Can delete Moon in Sign',107,'delete_moon'),(391,'Can view Horoscope',91,'view_horoscope'),(392,'Can view Sign',92,'view_sign'),(393,'Can view Sign description type',93,'view_signdescriptiontype'),(394,'Can view Sign description',94,'view_signdescription'),(395,'Can view Birth period',95,'view_birthperiod'),(396,'Can view Sign compatibility',96,'view_signcompatibility'),(397,'Can view Prognosis duration',97,'view_prognosisduration'),(398,'Can view Prognosis type',98,'view_prognosistype'),(399,'Can view Prognosis',99,'view_prognosis'),(400,'Can view Lunar diary category',100,'view_lunardiarycategory'),(401,'Can view Lunar diary',101,'view_lunardiary'),(402,'Can view Lexicon term',102,'view_astrolex'),(403,'Can view Life number',103,'view_lifenumber'),(404,'Can view Stone',104,'view_stone'),(405,'Can view Stone for Sign',105,'view_stoneforsign'),(406,'Can view Numerology grid number',106,'view_numerologygrid'),(407,'Can view Moon in Sign',107,'view_moon'),(408,'Can add Contact form recipient',108,'add_recipient'),(409,'Can change Contact form recipient',108,'change_recipient'),(410,'Can delete Contact form recipient',108,'delete_recipient'),(411,'Can add Contact form message',109,'add_message'),(412,'Can change Contact form message',109,'change_message'),(413,'Can delete Contact form message',109,'delete_message'),(414,'Can view Contact form recipient',108,'view_recipient'),(415,'Can view Contact form message',109,'view_message'),(416,'Can add Category - section mapping',110,'add_categorysectionmapping'),(417,'Can change Category - section mapping',110,'change_categorysectionmapping'),(418,'Can delete Category - section mapping',110,'delete_categorysectionmapping'),(419,'Can add Site - server mapping',111,'add_siteservermapping'),(420,'Can change Site - server mapping',111,'change_siteservermapping'),(421,'Can delete Site - server mapping',111,'delete_siteservermapping'),(422,'Can view Category - section mapping',110,'view_categorysectionmapping'),(423,'Can view Site - server mapping',111,'view_siteservermapping');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) COLLATE utf8_czech_ci NOT NULL,
  `first_name` varchar(30) COLLATE utf8_czech_ci NOT NULL,
  `last_name` varchar(30) COLLATE utf8_czech_ci NOT NULL,
  `email` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `password` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'admin','','','a@a.cz','sha1$4d8ee$79e1c8eae8232b705a10d4b00fb0a37b146d3857',1,1,1,'2009-05-20 17:57:32','2009-05-20 17:57:32');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `group_id_refs_id_f116770` (`group_id`),
  CONSTRAINT `group_id_refs_id_f116770` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `user_id_refs_id_7ceef80f` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `permission_id_refs_id_67e79cb` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_67e79cb` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_dfbab7d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catlocks_categorylock`
--

DROP TABLE IF EXISTS `catlocks_categorylock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catlocks_categorylock` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) NOT NULL,
  `password` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `category_id` (`category_id`),
  CONSTRAINT `category_id_refs_id_3d669645` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catlocks_categorylock`
--

LOCK TABLES `catlocks_categorylock` WRITE;
/*!40000 ALTER TABLE `catlocks_categorylock` DISABLE KEYS */;
/*!40000 ALTER TABLE `catlocks_categorylock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cdnclient_format`
--

DROP TABLE IF EXISTS `cdnclient_format`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cdnclient_format` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(20) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cdnclient_format`
--

LOCK TABLES `cdnclient_format` WRITE;
/*!40000 ALTER TABLE `cdnclient_format` DISABLE KEYS */;
INSERT INTO `cdnclient_format` VALUES (1,'flash-video'),(2,'mobile-video');
/*!40000 ALTER TABLE `cdnclient_format` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cdnclient_source`
--

DROP TABLE IF EXISTS `cdnclient_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cdnclient_source` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `token` varchar(20) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cdnclient_source`
--

LOCK TABLES `cdnclient_source` WRITE;
/*!40000 ALTER TABLE `cdnclient_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `cdnclient_source` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cdnclient_target`
--

DROP TABLE IF EXISTS `cdnclient_target`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cdnclient_target` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` int(11) NOT NULL,
  `format_id` int(11) NOT NULL,
  `metadata` text COLLATE utf8_czech_ci NOT NULL,
  `url` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `source_id` (`source_id`,`format_id`),
  KEY `cdnclient_target_source_id` (`source_id`),
  KEY `cdnclient_target_format_id` (`format_id`),
  CONSTRAINT `format_id_refs_id_3852e1c9` FOREIGN KEY (`format_id`) REFERENCES `cdnclient_format` (`id`),
  CONSTRAINT `source_id_refs_id_5ec2976d` FOREIGN KEY (`source_id`) REFERENCES `cdnclient_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cdnclient_target`
--

LOCK TABLES `cdnclient_target` WRITE;
/*!40000 ALTER TABLE `cdnclient_target` DISABLE KEYS */;
/*!40000 ALTER TABLE `cdnclient_target` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments_bannedip`
--

DROP TABLE IF EXISTS `comments_bannedip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments_bannedip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments_bannedip`
--

LOCK TABLES `comments_bannedip` WRITE;
/*!40000 ALTER TABLE `comments_bannedip` DISABLE KEYS */;
/*!40000 ALTER TABLE `comments_bannedip` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments_banneduser`
--

DROP TABLE IF EXISTS `comments_banneduser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments_banneduser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(10) unsigned NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `comments_banneduser_target_ct_id` (`target_ct_id`),
  KEY `comments_banneduser_user_id` (`user_id`),
  CONSTRAINT `target_ct_id_refs_id_1b9c9cf5` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_717f01b7` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments_banneduser`
--

LOCK TABLES `comments_banneduser` WRITE;
/*!40000 ALTER TABLE `comments_banneduser` DISABLE KEYS */;
/*!40000 ALTER TABLE `comments_banneduser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments_comment`
--

DROP TABLE IF EXISTS `comments_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(10) unsigned NOT NULL,
  `subject` longtext COLLATE utf8_czech_ci NOT NULL,
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `path` varchar(500) COLLATE utf8_czech_ci NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `nickname` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `email` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `ip_address` char(15) COLLATE utf8_czech_ci DEFAULT NULL,
  `submit_date` datetime NOT NULL DEFAULT '2009-05-20 17:58:08',
  `is_public` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `comments_comment_target_ct_id` (`target_ct_id`),
  KEY `comments_comment_parent_id` (`parent_id`),
  KEY `comments_comment_user_id` (`user_id`),
  CONSTRAINT `parent_id_refs_id_3b4faabd` FOREIGN KEY (`parent_id`) REFERENCES `comments_comment` (`id`),
  CONSTRAINT `target_ct_id_refs_id_4c03983c` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_508b97b8` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments_comment`
--

LOCK TABLES `comments_comment` WRITE;
/*!40000 ALTER TABLE `comments_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `comments_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments_commentoptions`
--

DROP TABLE IF EXISTS `comments_commentoptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments_commentoptions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(10) unsigned NOT NULL,
  `options` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT '2009-05-20 17:58:08',
  PRIMARY KEY (`id`),
  KEY `comments_commentoptions_target_ct_id` (`target_ct_id`),
  CONSTRAINT `target_ct_id_refs_id_1fd36d3` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments_commentoptions`
--

LOCK TABLES `comments_commentoptions` WRITE;
/*!40000 ALTER TABLE `comments_commentoptions` DISABLE KEYS */;
/*!40000 ALTER TABLE `comments_commentoptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contact_form_message`
--

DROP TABLE IF EXISTS `contact_form_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contact_form_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sender` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `subject` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  `created` datetime NOT NULL DEFAULT '2009-05-20 17:59:26',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contact_form_message`
--

LOCK TABLES `contact_form_message` WRITE;
/*!40000 ALTER TABLE `contact_form_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `contact_form_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contact_form_recipient`
--

DROP TABLE IF EXISTS `contact_form_recipient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contact_form_recipient` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contact_form_recipient`
--

LOCK TABLES `contact_form_recipient` WRITE;
/*!40000 ALTER TABLE `contact_form_recipient` DISABLE KEYS */;
/*!40000 ALTER TABLE `contact_form_recipient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contact_form_recipient_sites`
--

DROP TABLE IF EXISTS `contact_form_recipient_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `contact_form_recipient_sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipient_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `contact_form_recipient_sites_recipient_id` (`recipient_id`),
  KEY `contact_form_recipient_sites_site_id` (`site_id`),
  CONSTRAINT `recipient_id_refs_id_65d1f87e` FOREIGN KEY (`recipient_id`) REFERENCES `contact_form_recipient` (`id`),
  CONSTRAINT `site_id_refs_id_5e2dda37` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contact_form_recipient_sites`
--

LOCK TABLES `contact_form_recipient_sites` WRITE;
/*!40000 ALTER TABLE `contact_form_recipient_sites` DISABLE KEYS */;
/*!40000 ALTER TABLE `contact_form_recipient_sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_author`
--

DROP TABLE IF EXISTS `core_author`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_author` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `name` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `core_author_user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_68f3d442` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_author`
--

LOCK TABLES `core_author` WRITE;
/*!40000 ALTER TABLE `core_author` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_author` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_category`
--

DROP TABLE IF EXISTS `core_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `tree_parent_id` int(11) DEFAULT NULL,
  `tree_path` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_category_site_id_5839c0a2` (`site_id`,`tree_path`),
  KEY `core_category_slug` (`slug`),
  KEY `core_category_tree_parent_id` (`tree_parent_id`),
  KEY `core_category_site_id` (`site_id`),
  CONSTRAINT `site_id_refs_id_48bbfd18` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`),
  CONSTRAINT `tree_parent_id_refs_id_256e3a85` FOREIGN KEY (`tree_parent_id`) REFERENCES `core_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_category`
--

LOCK TABLES `core_category` WRITE;
/*!40000 ALTER TABLE `core_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_hitcount`
--

DROP TABLE IF EXISTS `core_hitcount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_hitcount` (
  `placement_id` int(11) NOT NULL,
  `last_seen` datetime NOT NULL,
  `hits` int(10) unsigned NOT NULL DEFAULT '1',
  PRIMARY KEY (`placement_id`),
  CONSTRAINT `placement_id_refs_id_7d42d973` FOREIGN KEY (`placement_id`) REFERENCES `core_placement` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_hitcount`
--

LOCK TABLES `core_hitcount` WRITE;
/*!40000 ALTER TABLE `core_hitcount` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_hitcount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_listing`
--

DROP TABLE IF EXISTS `core_listing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_listing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `placement_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `publish_from` datetime NOT NULL,
  `priority_from` datetime DEFAULT NULL,
  `priority_to` datetime DEFAULT NULL,
  `priority_value` int(11) DEFAULT NULL,
  `remove` tinyint(1) NOT NULL DEFAULT '0',
  `commercial` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `core_listing_placement_id` (`placement_id`),
  KEY `core_listing_category_id` (`category_id`),
  CONSTRAINT `category_id_refs_id_69946ba0` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `placement_id_refs_id_7c52840e` FOREIGN KEY (`placement_id`) REFERENCES `core_placement` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_listing`
--

LOCK TABLES `core_listing` WRITE;
/*!40000 ALTER TABLE `core_listing` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_listing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_placement`
--

DROP TABLE IF EXISTS `core_placement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_placement` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `publish_from` datetime NOT NULL,
  `publish_to` datetime DEFAULT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `static` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `core_placement_target_ct_id` (`target_ct_id`),
  KEY `core_placement_category_id` (`category_id`),
  KEY `core_placement_slug` (`slug`),
  CONSTRAINT `category_id_refs_id_5bc7e23f` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `target_ct_id_refs_id_15cde42f` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_placement`
--

LOCK TABLES `core_placement` WRITE;
/*!40000 ALTER TABLE `core_placement` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_placement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_related`
--

DROP TABLE IF EXISTS `core_related`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_related` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(11) NOT NULL,
  `source_ct_id` int(11) NOT NULL,
  `source_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_related_target_ct_id` (`target_ct_id`),
  KEY `core_related_source_ct_id` (`source_ct_id`),
  CONSTRAINT `source_ct_id_refs_id_3afe9955` FOREIGN KEY (`source_ct_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `target_ct_id_refs_id_3afe9955` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_related`
--

LOCK TABLES `core_related` WRITE;
/*!40000 ALTER TABLE `core_related` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_related` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_source`
--

DROP TABLE IF EXISTS `core_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `core_source` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `url` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_source`
--

LOCK TABLES `core_source` WRITE;
/*!40000 ALTER TABLE `core_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_source` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `db_templates_dbtemplate`
--

DROP TABLE IF EXISTS `db_templates_dbtemplate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `db_templates_dbtemplate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `site_id` int(11) NOT NULL,
  `description` varchar(500) COLLATE utf8_czech_ci NOT NULL,
  `extends` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `db_templates_dbtemplate_site_id_6b859b8f` (`site_id`,`name`),
  KEY `db_templates_dbtemplate_name` (`name`),
  KEY `db_templates_dbtemplate_site_id` (`site_id`),
  CONSTRAINT `site_id_refs_id_bddf273` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `db_templates_dbtemplate`
--

LOCK TABLES `db_templates_dbtemplate` WRITE;
/*!40000 ALTER TABLE `db_templates_dbtemplate` DISABLE KEYS */;
/*!40000 ALTER TABLE `db_templates_dbtemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `db_templates_templateblock`
--

DROP TABLE IF EXISTS `db_templates_templateblock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `db_templates_templateblock` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `template_id` int(11) NOT NULL,
  `name` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `box_type` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `target_ct_id` int(11) DEFAULT NULL,
  `target_id` int(11) DEFAULT NULL,
  `active_from` datetime DEFAULT NULL,
  `active_till` datetime DEFAULT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `db_templates_templateblock_template_id_5f0bd1c9` (`template_id`,`name`,`active_from`,`active_till`),
  KEY `db_templates_templateblock_template_id` (`template_id`),
  KEY `db_templates_templateblock_target_ct_id` (`target_ct_id`),
  CONSTRAINT `target_ct_id_refs_id_704a1c8` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `template_id_refs_id_61a67229` FOREIGN KEY (`template_id`) REFERENCES `db_templates_dbtemplate` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `db_templates_templateblock`
--

LOCK TABLES `db_templates_templateblock` WRITE;
/*!40000 ALTER TABLE `db_templates_templateblock` DISABLE KEYS */;
/*!40000 ALTER TABLE `db_templates_templateblock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext COLLATE utf8_czech_ci,
  `object_repr` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_user_id` (`user_id`),
  KEY `django_admin_log_content_type_id` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_288599e6` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_c8665aa` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `app_label` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `model` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'message','auth','message'),(5,'content type','contenttypes','contenttype'),(6,'session','sessions','session'),(7,'site','sites','site'),(8,'redirect','redirects','redirect'),(9,'log entry','admin','logentry'),(10,'newsletter','newsletters','newsletter'),(11,'recipient','newsletters','recipient'),(12,'format','cdnclient','format'),(13,'source','cdnclient','source'),(14,'target','cdnclient','target'),(15,'migration history','south','migrationhistory'),(16,'Eshop','xmastips','eshop'),(17,'Feedset','xmastips','feedset'),(18,'Category','xmastips','category'),(19,'Target group','xmastips','targetgroup'),(20,'Present','xmastips','present'),(21,'Inquiry of Santa','writetosanta','inquiryofsanta'),(22,'Author','core','author'),(23,'Source','core','source'),(24,'Category','core','category'),(25,'Placement','core','placement'),(26,'Listing','core','listing'),(27,'Hit Count','core','hitcount'),(28,'Related','core','related'),(29,'Photo','photos','photo'),(30,'Format','photos','format'),(31,'Formated photo','photos','formatedphoto'),(32,'Info box','articles','infobox'),(33,'Article','articles','article'),(34,'Article content','articles','articlecontents'),(35,'Comment Options','comments','commentoptions'),(36,'Comment','comments','comment'),(37,'Banned User','comments','banneduser'),(38,'banned ip','comments','bannedip'),(39,'Template','db_templates','dbtemplate'),(40,'Template block','db_templates','templateblock'),(41,'Gallery','galleries','gallery'),(42,'Gallery item','galleries','galleryitem'),(43,'Contest','polls','contest'),(44,'Quiz','polls','quiz'),(45,'Question','polls','question'),(46,'Poll','polls','poll'),(47,'Choice','polls','choice'),(48,'Vote','polls','vote'),(49,'Contestant','polls','contestant'),(50,'Result','polls','result'),(51,'tag','tagging','tag'),(52,'tagged item','tagging','taggeditem'),(53,'Model weight','ratings','modelweight'),(54,'Total rate','ratings','totalrate'),(55,'Aggregation','ratings','agg'),(56,'Rating','ratings','rating'),(57,'atlas export','exports','atlasexport'),(58,'Server','imports','server'),(59,'Server item','imports','serveritem'),(60,'Interviewee','interviews','interviewee'),(61,'Interview','interviews','interview'),(62,'Question','interviews','question'),(63,'Answer','interviews','answer'),(64,'position','positions','position'),(65,'Category Lock','catlocks','categorylock'),(66,'mail','sendmail','mail'),(67,'Type','attachments','type'),(68,'Attachment','attachments','attachment'),(69,'Serie','series','serie'),(70,'Serie part','series','seriepart'),(71,'Media','media','media'),(72,'section','media','section'),(73,'usage','media','usage'),(74,'Instruction','instruction','instruction'),(75,'Cooking type','recipes','cookingtype'),(76,'Cuisine','recipes','cuisine'),(77,'Nutrient group','recipes','nutrientgroup'),(78,'Nutrient','recipes','nutrient'),(79,'Unit','recipes','unit'),(80,'Unit conversion','recipes','unitconversion'),(81,'Ingredient group','recipes','ingredientgroup'),(82,'Ingredient','recipes','ingredient'),(83,'Nutrient in ingredient','recipes','nutrientiningredient'),(84,'Category photo','recipes','recipecategoryphoto'),(85,'Side-dish','recipes','sidedish'),(86,'Recipe','recipes','recipe'),(87,'Ingredient in recipe','recipes','ingredientinrecipe'),(88,'Recipe of day','recipes','recipeofday'),(89,'old recipe article redirect','recipes','oldrecipearticleredirect'),(90,'old recipe category redirect','recipes','oldrecipecategoryredirect'),(91,'Horoscope','astrology','horoscope'),(92,'Sign','astrology','sign'),(93,'Sign description type','astrology','signdescriptiontype'),(94,'Sign description','astrology','signdescription'),(95,'Birth period','astrology','birthperiod'),(96,'Sign compatibility','astrology','signcompatibility'),(97,'Prognosis duration','astrology','prognosisduration'),(98,'Prognosis type','astrology','prognosistype'),(99,'Prognosis','astrology','prognosis'),(100,'Lunar diary category','astrology','lunardiarycategory'),(101,'Lunar diary','astrology','lunardiary'),(102,'Lexicon term','astrology','astrolex'),(103,'Life number','astrology','lifenumber'),(104,'Stone','astrology','stone'),(105,'Stone for Sign','astrology','stoneforsign'),(106,'Numerology grid number','astrology','numerologygrid'),(107,'Moon in Sign','astrology','moon'),(108,'Contact form recipient','contact_form','recipient'),(109,'Contact form message','contact_form','message'),(110,'Category - section mapping','adverts','categorysectionmapping'),(111,'Site - server mapping','adverts','siteservermapping');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_redirect`
--

DROP TABLE IF EXISTS `django_redirect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_redirect` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `site_id` int(11) NOT NULL,
  `old_path` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `new_path` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `site_id` (`site_id`,`old_path`),
  KEY `django_redirect_site_id` (`site_id`),
  KEY `django_redirect_old_path` (`old_path`),
  CONSTRAINT `site_id_refs_id_4aa27aa6` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_redirect`
--

LOCK TABLES `django_redirect` WRITE;
/*!40000 ALTER TABLE `django_redirect` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_redirect` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8_czech_ci NOT NULL,
  `session_data` longtext COLLATE utf8_czech_ci NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `name` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exports_atlasexport`
--

DROP TABLE IF EXISTS `exports_atlasexport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exports_atlasexport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(11) NOT NULL,
  `title` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `photo_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exports_atlasexport_target_ct_id` (`target_ct_id`),
  KEY `exports_atlasexport_photo_id` (`photo_id`),
  CONSTRAINT `photo_id_refs_id_4e18f09d` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`),
  CONSTRAINT `target_ct_id_refs_id_6700fc98` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exports_atlasexport`
--

LOCK TABLES `exports_atlasexport` WRITE;
/*!40000 ALTER TABLE `exports_atlasexport` DISABLE KEYS */;
/*!40000 ALTER TABLE `exports_atlasexport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `galleries_gallery`
--

DROP TABLE IF EXISTS `galleries_gallery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `galleries_gallery` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `description` varchar(3000) COLLATE utf8_czech_ci NOT NULL,
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT '2009-05-20 17:58:13',
  PRIMARY KEY (`id`),
  KEY `galleries_gallery_slug` (`slug`),
  KEY `galleries_gallery_owner_id` (`owner_id`),
  KEY `galleries_gallery_category_id` (`category_id`),
  CONSTRAINT `category_id_refs_id_2f308ea0` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `owner_id_refs_id_6f96fcc9` FOREIGN KEY (`owner_id`) REFERENCES `core_author` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `galleries_gallery`
--

LOCK TABLES `galleries_gallery` WRITE;
/*!40000 ALTER TABLE `galleries_gallery` DISABLE KEYS */;
/*!40000 ALTER TABLE `galleries_gallery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `galleries_galleryitem`
--

DROP TABLE IF EXISTS `galleries_galleryitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `galleries_galleryitem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gallery_id` int(11) NOT NULL,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(11) NOT NULL,
  `order` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `galleries_galleryitem_gallery_id_4afb2efc` (`gallery_id`,`order`),
  KEY `galleries_galleryitem_gallery_id` (`gallery_id`),
  KEY `galleries_galleryitem_target_ct_id` (`target_ct_id`),
  KEY `galleries_galleryitem_target_id` (`target_id`),
  CONSTRAINT `gallery_id_refs_id_117ccb7a` FOREIGN KEY (`gallery_id`) REFERENCES `galleries_gallery` (`id`),
  CONSTRAINT `target_ct_id_refs_id_4261876b` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `galleries_galleryitem`
--

LOCK TABLES `galleries_galleryitem` WRITE;
/*!40000 ALTER TABLE `galleries_galleryitem` DISABLE KEYS */;
/*!40000 ALTER TABLE `galleries_galleryitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `imports_server`
--

DROP TABLE IF EXISTS `imports_server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `imports_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `domain` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `url` varchar(300) COLLATE utf8_czech_ci NOT NULL,
  `category_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `imports_server_slug` (`slug`),
  KEY `imports_server_category_id` (`category_id`),
  CONSTRAINT `category_id_refs_id_1b3168d6` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `imports_server`
--

LOCK TABLES `imports_server` WRITE;
/*!40000 ALTER TABLE `imports_server` DISABLE KEYS */;
/*!40000 ALTER TABLE `imports_server` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `imports_serveritem`
--

DROP TABLE IF EXISTS `imports_serveritem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `imports_serveritem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` int(11) NOT NULL,
  `title` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `summary` longtext COLLATE utf8_czech_ci NOT NULL,
  `updated` datetime NOT NULL,
  `priority` int(11) NOT NULL DEFAULT '0',
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `link` varchar(400) COLLATE utf8_czech_ci NOT NULL,
  `photo_url` varchar(400) COLLATE utf8_czech_ci NOT NULL,
  `photo_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `imports_serveritem_server_id_7d508d62` (`server_id`,`slug`),
  KEY `imports_serveritem_server_id` (`server_id`),
  KEY `imports_serveritem_slug` (`slug`),
  KEY `imports_serveritem_photo_id` (`photo_id`),
  CONSTRAINT `photo_id_refs_id_144430a6` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`),
  CONSTRAINT `server_id_refs_id_603f63ea` FOREIGN KEY (`server_id`) REFERENCES `imports_server` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `imports_serveritem`
--

LOCK TABLES `imports_serveritem` WRITE;
/*!40000 ALTER TABLE `imports_serveritem` DISABLE KEYS */;
/*!40000 ALTER TABLE `imports_serveritem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `instruction_instruction`
--

DROP TABLE IF EXISTS `instruction_instruction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `instruction_instruction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `media_id` int(11) NOT NULL,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `photo_id` int(11) DEFAULT NULL,
  `source_id` int(11) DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  `created` datetime NOT NULL DEFAULT '2009-05-20 17:58:48',
  `updated` datetime DEFAULT NULL,
  `embed_invisible` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `instruction_instruction_media_id` (`media_id`),
  KEY `instruction_instruction_slug` (`slug`),
  KEY `instruction_instruction_photo_id` (`photo_id`),
  KEY `instruction_instruction_source_id` (`source_id`),
  KEY `instruction_instruction_category_id` (`category_id`),
  CONSTRAINT `category_id_refs_id_2bac5ce2` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `media_id_refs_id_3bcec203` FOREIGN KEY (`media_id`) REFERENCES `media_media` (`id`),
  CONSTRAINT `photo_id_refs_id_1907e3b3` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`),
  CONSTRAINT `source_id_refs_id_3935b2c3` FOREIGN KEY (`source_id`) REFERENCES `core_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `instruction_instruction`
--

LOCK TABLES `instruction_instruction` WRITE;
/*!40000 ALTER TABLE `instruction_instruction` DISABLE KEYS */;
/*!40000 ALTER TABLE `instruction_instruction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `instruction_instruction_authors`
--

DROP TABLE IF EXISTS `instruction_instruction_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `instruction_instruction_authors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `instruction_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `instruction_instruction_authors_instruction_id` (`instruction_id`),
  KEY `instruction_instruction_authors_author_id` (`author_id`),
  CONSTRAINT `author_id_refs_id_cc614fa` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`),
  CONSTRAINT `instruction_id_refs_id_34288ba6` FOREIGN KEY (`instruction_id`) REFERENCES `instruction_instruction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `instruction_instruction_authors`
--

LOCK TABLES `instruction_instruction_authors` WRITE;
/*!40000 ALTER TABLE `instruction_instruction_authors` DISABLE KEYS */;
/*!40000 ALTER TABLE `instruction_instruction_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interviews_answer`
--

DROP TABLE IF EXISTS `interviews_answer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interviews_answer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_id` int(11) NOT NULL,
  `interviewee_id` int(11) NOT NULL,
  `submit_date` datetime NOT NULL DEFAULT '2009-05-20 17:58:31',
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `interviews_answer_question_id` (`question_id`),
  KEY `interviews_answer_interviewee_id` (`interviewee_id`),
  CONSTRAINT `interviewee_id_refs_id_ec2d5ff` FOREIGN KEY (`interviewee_id`) REFERENCES `interviews_interviewee` (`id`),
  CONSTRAINT `question_id_refs_id_668be6ab` FOREIGN KEY (`question_id`) REFERENCES `interviews_question` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interviews_answer`
--

LOCK TABLES `interviews_answer` WRITE;
/*!40000 ALTER TABLE `interviews_answer` DISABLE KEYS */;
/*!40000 ALTER TABLE `interviews_answer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interviews_interview`
--

DROP TABLE IF EXISTS `interviews_interview`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interviews_interview` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `upper_title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `perex` longtext COLLATE utf8_czech_ci NOT NULL,
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  `reply_from` datetime NOT NULL,
  `reply_to` datetime NOT NULL,
  `ask_from` datetime NOT NULL,
  `ask_to` datetime NOT NULL,
  `source_id` int(11) DEFAULT NULL,
  `category_id` int(11) NOT NULL,
  `photo_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `interviews_interview_slug` (`slug`),
  KEY `interviews_interview_source_id` (`source_id`),
  KEY `interviews_interview_category_id` (`category_id`),
  KEY `interviews_interview_photo_id` (`photo_id`),
  CONSTRAINT `category_id_refs_id_908f3cc` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `photo_id_refs_id_13123a57` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`),
  CONSTRAINT `source_id_refs_id_4a4e7fa1` FOREIGN KEY (`source_id`) REFERENCES `core_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interviews_interview`
--

LOCK TABLES `interviews_interview` WRITE;
/*!40000 ALTER TABLE `interviews_interview` DISABLE KEYS */;
/*!40000 ALTER TABLE `interviews_interview` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interviews_interview_authors`
--

DROP TABLE IF EXISTS `interviews_interview_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interviews_interview_authors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `interview_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `interviews_interview_authors_interview_id` (`interview_id`),
  KEY `interviews_interview_authors_author_id` (`author_id`),
  CONSTRAINT `author_id_refs_id_77adebcc` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`),
  CONSTRAINT `interview_id_refs_id_4bdd36f2` FOREIGN KEY (`interview_id`) REFERENCES `interviews_interview` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interviews_interview_authors`
--

LOCK TABLES `interviews_interview_authors` WRITE;
/*!40000 ALTER TABLE `interviews_interview_authors` DISABLE KEYS */;
/*!40000 ALTER TABLE `interviews_interview_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interviews_interview_interviewees`
--

DROP TABLE IF EXISTS `interviews_interview_interviewees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interviews_interview_interviewees` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `interview_id` int(11) NOT NULL,
  `interviewee_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `interviews_interview_interviewees_interview_id` (`interview_id`),
  KEY `interviews_interview_interviewees_interviewee_id` (`interviewee_id`),
  CONSTRAINT `interviewee_id_refs_id_7951e1bf` FOREIGN KEY (`interviewee_id`) REFERENCES `interviews_interviewee` (`id`),
  CONSTRAINT `interview_id_refs_id_335c69d7` FOREIGN KEY (`interview_id`) REFERENCES `interviews_interview` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interviews_interview_interviewees`
--

LOCK TABLES `interviews_interview_interviewees` WRITE;
/*!40000 ALTER TABLE `interviews_interview_interviewees` DISABLE KEYS */;
/*!40000 ALTER TABLE `interviews_interview_interviewees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interviews_interviewee`
--

DROP TABLE IF EXISTS `interviews_interviewee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interviews_interviewee` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `name` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `interviews_interviewee_user_id` (`user_id`),
  KEY `interviews_interviewee_author_id` (`author_id`),
  KEY `interviews_interviewee_slug` (`slug`),
  CONSTRAINT `author_id_refs_id_d4b6afd` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`),
  CONSTRAINT `user_id_refs_id_14ceab80` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interviews_interviewee`
--

LOCK TABLES `interviews_interviewee` WRITE;
/*!40000 ALTER TABLE `interviews_interviewee` DISABLE KEYS */;
/*!40000 ALTER TABLE `interviews_interviewee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interviews_question`
--

DROP TABLE IF EXISTS `interviews_question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interviews_question` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `interview_id` int(11) NOT NULL,
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `nickname` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `email` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `ip_address` char(15) COLLATE utf8_czech_ci DEFAULT NULL,
  `submit_date` datetime NOT NULL DEFAULT '2009-05-20 17:58:31',
  `is_public` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `interviews_question_interview_id` (`interview_id`),
  KEY `interviews_question_user_id` (`user_id`),
  CONSTRAINT `interview_id_refs_id_5f8b8049` FOREIGN KEY (`interview_id`) REFERENCES `interviews_interview` (`id`),
  CONSTRAINT `user_id_refs_id_6fb28eac` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interviews_question`
--

LOCK TABLES `interviews_question` WRITE;
/*!40000 ALTER TABLE `interviews_question` DISABLE KEYS */;
/*!40000 ALTER TABLE `interviews_question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_media`
--

DROP TABLE IF EXISTS `media_media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `media_media` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `photo_id` int(11) DEFAULT NULL,
  `file_id` int(11) NOT NULL,
  `source_id` int(11) DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  `created` datetime NOT NULL DEFAULT '2009-05-20 17:58:45',
  `updated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `media_media_slug` (`slug`),
  KEY `media_media_photo_id` (`photo_id`),
  KEY `media_media_file_id` (`file_id`),
  KEY `media_media_source_id` (`source_id`),
  KEY `media_media_category_id` (`category_id`),
  CONSTRAINT `category_id_refs_id_739dd1aa` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `file_id_refs_id_aeabf3f` FOREIGN KEY (`file_id`) REFERENCES `cdnclient_source` (`id`),
  CONSTRAINT `photo_id_refs_id_1069d727` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`),
  CONSTRAINT `source_id_refs_id_26ee1f4f` FOREIGN KEY (`source_id`) REFERENCES `core_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_media`
--

LOCK TABLES `media_media` WRITE;
/*!40000 ALTER TABLE `media_media` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_media` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_media_authors`
--

DROP TABLE IF EXISTS `media_media_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `media_media_authors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `media_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `media_media_authors_media_id` (`media_id`),
  KEY `media_media_authors_author_id` (`author_id`),
  CONSTRAINT `author_id_refs_id_5a42ef96` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`),
  CONSTRAINT `media_id_refs_id_7a311fae` FOREIGN KEY (`media_id`) REFERENCES `media_media` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_media_authors`
--

LOCK TABLES `media_media_authors` WRITE;
/*!40000 ALTER TABLE `media_media_authors` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_media_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_section`
--

DROP TABLE IF EXISTS `media_section`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `media_section` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `media_id` int(11) NOT NULL,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `time` int(10) unsigned NOT NULL,
  `duration` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `media_section_media_id` (`media_id`),
  CONSTRAINT `media_id_refs_id_1cd98f8` FOREIGN KEY (`media_id`) REFERENCES `media_media` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_section`
--

LOCK TABLES `media_section` WRITE;
/*!40000 ALTER TABLE `media_section` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_section` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_usage`
--

DROP TABLE IF EXISTS `media_usage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `media_usage` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `media_id` int(11) NOT NULL,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `url` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `priority` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `media_usage_media_id` (`media_id`),
  CONSTRAINT `media_id_refs_id_5afe6db2` FOREIGN KEY (`media_id`) REFERENCES `media_media` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_usage`
--

LOCK TABLES `media_usage` WRITE;
/*!40000 ALTER TABLE `media_usage` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_usage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `newsletters_newsletter`
--

DROP TABLE IF EXISTS `newsletters_newsletter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `newsletters_newsletter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `content` longtext COLLATE utf8_czech_ci NOT NULL,
  `date` datetime NOT NULL,
  `sent` tinyint(1) NOT NULL,
  `approved` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `newsletters_newsletter`
--

LOCK TABLES `newsletters_newsletter` WRITE;
/*!40000 ALTER TABLE `newsletters_newsletter` DISABLE KEYS */;
/*!40000 ALTER TABLE `newsletters_newsletter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `newsletters_recipient`
--

DROP TABLE IF EXISTS `newsletters_recipient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `newsletters_recipient` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `date` datetime NOT NULL,
  `sent` tinyint(1) NOT NULL,
  `deleted` tinyint(1) NOT NULL,
  `md5` varchar(32) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `newsletters_recipient`
--

LOCK TABLES `newsletters_recipient` WRITE;
/*!40000 ALTER TABLE `newsletters_recipient` DISABLE KEYS */;
/*!40000 ALTER TABLE `newsletters_recipient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photos_format`
--

DROP TABLE IF EXISTS `photos_format`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `photos_format` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8_czech_ci NOT NULL,
  `max_width` int(10) unsigned NOT NULL,
  `max_height` int(10) unsigned NOT NULL,
  `flexible_height` tinyint(1) NOT NULL DEFAULT '0',
  `flexible_max_height` int(10) unsigned DEFAULT NULL,
  `stretch` tinyint(1) NOT NULL DEFAULT '0',
  `nocrop` tinyint(1) NOT NULL DEFAULT '0',
  `resample_quality` int(11) NOT NULL DEFAULT '85',
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `photos_format_site_id` (`site_id`),
  CONSTRAINT `site_id_refs_id_17e91683` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photos_format`
--

LOCK TABLES `photos_format` WRITE;
/*!40000 ALTER TABLE `photos_format` DISABLE KEYS */;
/*!40000 ALTER TABLE `photos_format` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photos_formatedphoto`
--

DROP TABLE IF EXISTS `photos_formatedphoto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `photos_formatedphoto` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `photo_id` int(11) NOT NULL,
  `format_id` int(11) NOT NULL,
  `filename` varchar(300) COLLATE utf8_czech_ci NOT NULL,
  `crop_left` int(10) unsigned NOT NULL,
  `crop_top` int(10) unsigned NOT NULL,
  `crop_width` int(10) unsigned NOT NULL,
  `crop_height` int(10) unsigned NOT NULL,
  `width` int(10) unsigned NOT NULL,
  `height` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `photos_formatedphoto_photo_id_27c93d24` (`photo_id`,`format_id`),
  KEY `photos_formatedphoto_photo_id` (`photo_id`),
  KEY `photos_formatedphoto_format_id` (`format_id`),
  CONSTRAINT `format_id_refs_id_603486bf` FOREIGN KEY (`format_id`) REFERENCES `photos_format` (`id`),
  CONSTRAINT `photo_id_refs_id_9a536db` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photos_formatedphoto`
--

LOCK TABLES `photos_formatedphoto` WRITE;
/*!40000 ALTER TABLE `photos_formatedphoto` DISABLE KEYS */;
/*!40000 ALTER TABLE `photos_formatedphoto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photos_photo`
--

DROP TABLE IF EXISTS `photos_photo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `photos_photo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `image` varchar(100) COLLATE utf8_czech_ci NOT NULL,
  `width` int(10) unsigned NOT NULL,
  `height` int(10) unsigned NOT NULL,
  `source_id` int(11) DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT '2009-05-20 17:58:02',
  PRIMARY KEY (`id`),
  KEY `photos_photo_slug` (`slug`),
  KEY `photos_photo_source_id` (`source_id`),
  CONSTRAINT `source_id_refs_id_c929c61` FOREIGN KEY (`source_id`) REFERENCES `core_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photos_photo`
--

LOCK TABLES `photos_photo` WRITE;
/*!40000 ALTER TABLE `photos_photo` DISABLE KEYS */;
/*!40000 ALTER TABLE `photos_photo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photos_photo_authors`
--

DROP TABLE IF EXISTS `photos_photo_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `photos_photo_authors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `photo_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `photos_photo_authors_photo_id` (`photo_id`),
  KEY `photos_photo_authors_author_id` (`author_id`),
  CONSTRAINT `author_id_refs_id_2e5fa14a` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`),
  CONSTRAINT `photo_id_refs_id_57798e82` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photos_photo_authors`
--

LOCK TABLES `photos_photo_authors` WRITE;
/*!40000 ALTER TABLE `photos_photo_authors` DISABLE KEYS */;
/*!40000 ALTER TABLE `photos_photo_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `polls_choice`
--

DROP TABLE IF EXISTS `polls_choice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polls_choice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_id` int(11) NOT NULL,
  `choice` longtext COLLATE utf8_czech_ci NOT NULL,
  `points` int(11) DEFAULT NULL,
  `votes` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `polls_choice_question_id` (`question_id`),
  CONSTRAINT `question_id_refs_id_7115173a` FOREIGN KEY (`question_id`) REFERENCES `polls_question` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polls_choice`
--

LOCK TABLES `polls_choice` WRITE;
/*!40000 ALTER TABLE `polls_choice` DISABLE KEYS */;
/*!40000 ALTER TABLE `polls_choice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `polls_contest`
--

DROP TABLE IF EXISTS `polls_contest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polls_contest` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `category_id` int(11) NOT NULL,
  `text_announcement` longtext COLLATE utf8_czech_ci NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  `text_results` longtext COLLATE utf8_czech_ci NOT NULL,
  `active_from` datetime NOT NULL,
  `active_till` datetime NOT NULL,
  `photo_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `polls_contest_slug` (`slug`),
  KEY `polls_contest_category_id` (`category_id`),
  KEY `polls_contest_photo_id` (`photo_id`),
  CONSTRAINT `category_id_refs_id_6b11232a` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `photo_id_refs_id_565fe755` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polls_contest`
--

LOCK TABLES `polls_contest` WRITE;
/*!40000 ALTER TABLE `polls_contest` DISABLE KEYS */;
/*!40000 ALTER TABLE `polls_contest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `polls_contestant`
--

DROP TABLE IF EXISTS `polls_contestant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polls_contestant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contest_id` int(11) NOT NULL,
  `datetime` datetime NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `name` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `surname` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `email` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `phonenumber` varchar(20) COLLATE utf8_czech_ci NOT NULL,
  `address` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `choices` longtext COLLATE utf8_czech_ci NOT NULL,
  `count_guess` int(11) NOT NULL,
  `winner` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `polls_contestant_contest_id_4b119dad` (`contest_id`,`email`),
  KEY `polls_contestant_contest_id` (`contest_id`),
  KEY `polls_contestant_user_id` (`user_id`),
  CONSTRAINT `contest_id_refs_id_1bc9f9af` FOREIGN KEY (`contest_id`) REFERENCES `polls_contest` (`id`),
  CONSTRAINT `user_id_refs_id_52cb5f22` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polls_contestant`
--

LOCK TABLES `polls_contestant` WRITE;
/*!40000 ALTER TABLE `polls_contestant` DISABLE KEYS */;
/*!40000 ALTER TABLE `polls_contestant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `polls_poll`
--

DROP TABLE IF EXISTS `polls_poll`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polls_poll` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `text_announcement` longtext COLLATE utf8_czech_ci,
  `text` longtext COLLATE utf8_czech_ci,
  `text_results` longtext COLLATE utf8_czech_ci,
  `active_from` datetime DEFAULT NULL,
  `active_till` datetime DEFAULT NULL,
  `question_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `question_id` (`question_id`),
  CONSTRAINT `question_id_refs_id_6a846a76` FOREIGN KEY (`question_id`) REFERENCES `polls_question` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polls_poll`
--

LOCK TABLES `polls_poll` WRITE;
/*!40000 ALTER TABLE `polls_poll` DISABLE KEYS */;
/*!40000 ALTER TABLE `polls_poll` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `polls_question`
--

DROP TABLE IF EXISTS `polls_question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polls_question` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question` longtext COLLATE utf8_czech_ci NOT NULL,
  `allow_multiple` tinyint(1) NOT NULL DEFAULT '0',
  `allow_no_choice` tinyint(1) NOT NULL DEFAULT '0',
  `quiz_id` int(11) DEFAULT NULL,
  `contest_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `polls_question_quiz_id` (`quiz_id`),
  KEY `polls_question_contest_id` (`contest_id`),
  CONSTRAINT `contest_id_refs_id_77f1316e` FOREIGN KEY (`contest_id`) REFERENCES `polls_contest` (`id`),
  CONSTRAINT `quiz_id_refs_id_5c3edd08` FOREIGN KEY (`quiz_id`) REFERENCES `polls_quiz` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polls_question`
--

LOCK TABLES `polls_question` WRITE;
/*!40000 ALTER TABLE `polls_question` DISABLE KEYS */;
/*!40000 ALTER TABLE `polls_question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `polls_quiz`
--

DROP TABLE IF EXISTS `polls_quiz`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polls_quiz` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `category_id` int(11) NOT NULL,
  `text_announcement` longtext COLLATE utf8_czech_ci NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  `text_results` longtext COLLATE utf8_czech_ci NOT NULL,
  `active_from` datetime NOT NULL,
  `active_till` datetime NOT NULL,
  `photo_id` int(11) NOT NULL,
  `has_correct_answers` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `polls_quiz_slug` (`slug`),
  KEY `polls_quiz_category_id` (`category_id`),
  KEY `polls_quiz_photo_id` (`photo_id`),
  CONSTRAINT `category_id_refs_id_6ca0d9a0` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `photo_id_refs_id_3811f795` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polls_quiz`
--

LOCK TABLES `polls_quiz` WRITE;
/*!40000 ALTER TABLE `polls_quiz` DISABLE KEYS */;
/*!40000 ALTER TABLE `polls_quiz` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `polls_quiz_authors`
--

DROP TABLE IF EXISTS `polls_quiz_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polls_quiz_authors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `quiz_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `polls_quiz_authors_quiz_id` (`quiz_id`),
  KEY `polls_quiz_authors_author_id` (`author_id`),
  CONSTRAINT `author_id_refs_id_2a34fb20` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`),
  CONSTRAINT `quiz_id_refs_id_64e88502` FOREIGN KEY (`quiz_id`) REFERENCES `polls_quiz` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polls_quiz_authors`
--

LOCK TABLES `polls_quiz_authors` WRITE;
/*!40000 ALTER TABLE `polls_quiz_authors` DISABLE KEYS */;
/*!40000 ALTER TABLE `polls_quiz_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `polls_result`
--

DROP TABLE IF EXISTS `polls_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polls_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `quiz_id` int(11) NOT NULL,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  `points_from` int(11) DEFAULT NULL,
  `points_to` int(11) DEFAULT NULL,
  `count` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `polls_result_quiz_id` (`quiz_id`),
  CONSTRAINT `quiz_id_refs_id_5d48b3ef` FOREIGN KEY (`quiz_id`) REFERENCES `polls_quiz` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polls_result`
--

LOCK TABLES `polls_result` WRITE;
/*!40000 ALTER TABLE `polls_result` DISABLE KEYS */;
/*!40000 ALTER TABLE `polls_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `polls_vote`
--

DROP TABLE IF EXISTS `polls_vote`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polls_vote` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `poll_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `time` datetime NOT NULL,
  `ip_address` char(15) COLLATE utf8_czech_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `polls_vote_poll_id` (`poll_id`),
  KEY `polls_vote_user_id` (`user_id`),
  CONSTRAINT `poll_id_refs_id_58436f24` FOREIGN KEY (`poll_id`) REFERENCES `polls_poll` (`id`),
  CONSTRAINT `user_id_refs_id_355ea0a1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polls_vote`
--

LOCK TABLES `polls_vote` WRITE;
/*!40000 ALTER TABLE `polls_vote` DISABLE KEYS */;
/*!40000 ALTER TABLE `polls_vote` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `positions_position`
--

DROP TABLE IF EXISTS `positions_position`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `positions_position` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) NOT NULL,
  `name` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `target_ct_id` int(11) DEFAULT NULL,
  `target_id` int(10) unsigned DEFAULT NULL,
  `active_from` datetime DEFAULT NULL,
  `active_till` datetime DEFAULT NULL,
  `box_type` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  `disabled` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `positions_position_category_id` (`category_id`),
  KEY `positions_position_target_ct_id` (`target_ct_id`),
  CONSTRAINT `category_id_refs_id_71cdff18` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `target_ct_id_refs_id_a7caba8` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `positions_position`
--

LOCK TABLES `positions_position` WRITE;
/*!40000 ALTER TABLE `positions_position` DISABLE KEYS */;
/*!40000 ALTER TABLE `positions_position` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratings_agg`
--

DROP TABLE IF EXISTS `ratings_agg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratings_agg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(10) unsigned NOT NULL,
  `time` date NOT NULL,
  `people` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `period` varchar(1) COLLATE utf8_czech_ci NOT NULL,
  `detract` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `ratings_agg_target_ct_id` (`target_ct_id`),
  KEY `ratings_agg_target_id` (`target_id`),
  CONSTRAINT `target_ct_id_refs_id_665a7b51` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratings_agg`
--

LOCK TABLES `ratings_agg` WRITE;
/*!40000 ALTER TABLE `ratings_agg` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratings_agg` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratings_modelweight`
--

DROP TABLE IF EXISTS `ratings_modelweight`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratings_modelweight` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content_type_id` int(11) NOT NULL,
  `weight` int(11) NOT NULL DEFAULT '1',
  `owner_field` varchar(30) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_6435f545` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratings_modelweight`
--

LOCK TABLES `ratings_modelweight` WRITE;
/*!40000 ALTER TABLE `ratings_modelweight` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratings_modelweight` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratings_rating`
--

DROP TABLE IF EXISTS `ratings_rating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratings_rating` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(10) unsigned NOT NULL,
  `time` datetime NOT NULL DEFAULT '2009-05-20 17:58:24',
  `user_id` int(11) DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `ip_address` varchar(15) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratings_rating_target_ct_id` (`target_ct_id`),
  KEY `ratings_rating_target_id` (`target_id`),
  KEY `ratings_rating_user_id` (`user_id`),
  CONSTRAINT `target_ct_id_refs_id_73004ca0` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_5240d2dc` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratings_rating`
--

LOCK TABLES `ratings_rating` WRITE;
/*!40000 ALTER TABLE `ratings_rating` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratings_rating` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratings_totalrate`
--

DROP TABLE IF EXISTS `ratings_totalrate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratings_totalrate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(10) unsigned NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratings_totalrate_target_ct_id` (`target_ct_id`),
  KEY `ratings_totalrate_target_id` (`target_id`),
  CONSTRAINT `target_ct_id_refs_id_158d5dee` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratings_totalrate`
--

LOCK TABLES `ratings_totalrate` WRITE;
/*!40000 ALTER TABLE `ratings_totalrate` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratings_totalrate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_cookingtype`
--

DROP TABLE IF EXISTS `recipes_cookingtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_cookingtype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_cookingtype`
--

LOCK TABLES `recipes_cookingtype` WRITE;
/*!40000 ALTER TABLE `recipes_cookingtype` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_cookingtype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_cuisine`
--

DROP TABLE IF EXISTS `recipes_cuisine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_cuisine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) DEFAULT NULL,
  `name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  `path` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `recipes_cuisine_parent_id` (`parent_id`),
  CONSTRAINT `parent_id_refs_id_365f53fd` FOREIGN KEY (`parent_id`) REFERENCES `recipes_cuisine` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_cuisine`
--

LOCK TABLES `recipes_cuisine` WRITE;
/*!40000 ALTER TABLE `recipes_cuisine` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_cuisine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_ingredient`
--

DROP TABLE IF EXISTS `recipes_ingredient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_ingredient` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) DEFAULT NULL,
  `name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `genitive` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  `default_unit_id` int(11) NOT NULL,
  `ndb_no` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `recipes_ingredient_group_id` (`group_id`),
  KEY `recipes_ingredient_default_unit_id` (`default_unit_id`),
  CONSTRAINT `default_unit_id_refs_id_60ebe51a` FOREIGN KEY (`default_unit_id`) REFERENCES `recipes_unit` (`id`),
  CONSTRAINT `group_id_refs_id_2c201c23` FOREIGN KEY (`group_id`) REFERENCES `recipes_ingredientgroup` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_ingredient`
--

LOCK TABLES `recipes_ingredient` WRITE;
/*!40000 ALTER TABLE `recipes_ingredient` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_ingredient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_ingredientgroup`
--

DROP TABLE IF EXISTS `recipes_ingredientgroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_ingredientgroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_ingredientgroup`
--

LOCK TABLES `recipes_ingredientgroup` WRITE;
/*!40000 ALTER TABLE `recipes_ingredientgroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_ingredientgroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_ingredientinrecipe`
--

DROP TABLE IF EXISTS `recipes_ingredientinrecipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_ingredientinrecipe` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipe_id` int(11) NOT NULL,
  `ingredient_id` int(11) NOT NULL,
  `amount` decimal(5,2) DEFAULT NULL,
  `unit_id` int(11) DEFAULT NULL,
  `order` smallint(5) unsigned NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `recipes_ingredientinrecipe_recipe_id_3c0425fb` (`recipe_id`,`ingredient_id`),
  KEY `recipes_ingredientinrecipe_recipe_id` (`recipe_id`),
  KEY `recipes_ingredientinrecipe_ingredient_id` (`ingredient_id`),
  KEY `recipes_ingredientinrecipe_unit_id` (`unit_id`),
  CONSTRAINT `ingredient_id_refs_id_5c444206` FOREIGN KEY (`ingredient_id`) REFERENCES `recipes_ingredient` (`id`),
  CONSTRAINT `recipe_id_refs_id_44525c1d` FOREIGN KEY (`recipe_id`) REFERENCES `recipes_recipe` (`id`),
  CONSTRAINT `unit_id_refs_id_3744695d` FOREIGN KEY (`unit_id`) REFERENCES `recipes_unit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_ingredientinrecipe`
--

LOCK TABLES `recipes_ingredientinrecipe` WRITE;
/*!40000 ALTER TABLE `recipes_ingredientinrecipe` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_ingredientinrecipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_nutrient`
--

DROP TABLE IF EXISTS `recipes_nutrient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_nutrient` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `ndb_no` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `recipes_nutrient_group_id` (`group_id`),
  CONSTRAINT `group_id_refs_id_1146b305` FOREIGN KEY (`group_id`) REFERENCES `recipes_nutrientgroup` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_nutrient`
--

LOCK TABLES `recipes_nutrient` WRITE;
/*!40000 ALTER TABLE `recipes_nutrient` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_nutrient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_nutrientgroup`
--

DROP TABLE IF EXISTS `recipes_nutrientgroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_nutrientgroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_nutrientgroup`
--

LOCK TABLES `recipes_nutrientgroup` WRITE;
/*!40000 ALTER TABLE `recipes_nutrientgroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_nutrientgroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_nutrientiningredient`
--

DROP TABLE IF EXISTS `recipes_nutrientiningredient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_nutrientiningredient` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ingredient_id` int(11) NOT NULL,
  `nutrient_id` int(11) NOT NULL,
  `unit_id` int(11) NOT NULL,
  `amount` decimal(8,3) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `recipes_nutrientiningredient_ingredient_id_42f9cbc9` (`ingredient_id`,`nutrient_id`),
  KEY `recipes_nutrientiningredient_ingredient_id` (`ingredient_id`),
  KEY `recipes_nutrientiningredient_nutrient_id` (`nutrient_id`),
  KEY `recipes_nutrientiningredient_unit_id` (`unit_id`),
  CONSTRAINT `ingredient_id_refs_id_3a5aed61` FOREIGN KEY (`ingredient_id`) REFERENCES `recipes_ingredient` (`id`),
  CONSTRAINT `nutrient_id_refs_id_5c5afc8b` FOREIGN KEY (`nutrient_id`) REFERENCES `recipes_nutrient` (`id`),
  CONSTRAINT `unit_id_refs_id_7ab138c4` FOREIGN KEY (`unit_id`) REFERENCES `recipes_unit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_nutrientiningredient`
--

LOCK TABLES `recipes_nutrientiningredient` WRITE;
/*!40000 ALTER TABLE `recipes_nutrientiningredient` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_nutrientiningredient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_oldrecipearticleredirect`
--

DROP TABLE IF EXISTS `recipes_oldrecipearticleredirect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_oldrecipearticleredirect` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `new_id_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recipes_oldrecipearticleredirect_new_id_id` (`new_id_id`),
  CONSTRAINT `new_id_id_refs_id_698c78bc` FOREIGN KEY (`new_id_id`) REFERENCES `articles_article` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_oldrecipearticleredirect`
--

LOCK TABLES `recipes_oldrecipearticleredirect` WRITE;
/*!40000 ALTER TABLE `recipes_oldrecipearticleredirect` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_oldrecipearticleredirect` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_oldrecipecategoryredirect`
--

DROP TABLE IF EXISTS `recipes_oldrecipecategoryredirect`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_oldrecipecategoryredirect` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `new_id_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recipes_oldrecipecategoryredirect_new_id_id` (`new_id_id`),
  CONSTRAINT `new_id_id_refs_id_23a1754` FOREIGN KEY (`new_id_id`) REFERENCES `core_category` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_oldrecipecategoryredirect`
--

LOCK TABLES `recipes_oldrecipecategoryredirect` WRITE;
/*!40000 ALTER TABLE `recipes_oldrecipecategoryredirect` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_oldrecipecategoryredirect` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_recipe`
--

DROP TABLE IF EXISTS `recipes_recipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_recipe` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  `category_id` int(11) NOT NULL,
  `cooking_type_id` int(11) DEFAULT NULL,
  `photo_id` int(11) DEFAULT NULL,
  `servings` smallint(5) unsigned DEFAULT NULL,
  `price` smallint(6) NOT NULL DEFAULT '3',
  `difficulty` smallint(5) unsigned NOT NULL DEFAULT '3',
  `preparation_time` smallint(5) unsigned NOT NULL,
  `caloric_value` int(10) unsigned DEFAULT NULL,
  `headline` longtext COLLATE utf8_czech_ci NOT NULL,
  `preparation` longtext COLLATE utf8_czech_ci NOT NULL,
  `approved` tinyint(1) NOT NULL DEFAULT '0',
  `inserted` datetime NOT NULL,
  `modified` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `recipes_recipe_category_id` (`category_id`),
  KEY `recipes_recipe_cooking_type_id` (`cooking_type_id`),
  KEY `recipes_recipe_photo_id` (`photo_id`),
  CONSTRAINT `category_id_refs_id_1f280250` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `cooking_type_id_refs_id_654c8282` FOREIGN KEY (`cooking_type_id`) REFERENCES `recipes_cookingtype` (`id`),
  CONSTRAINT `photo_id_refs_id_2be20725` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_recipe`
--

LOCK TABLES `recipes_recipe` WRITE;
/*!40000 ALTER TABLE `recipes_recipe` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_recipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_recipe_authors`
--

DROP TABLE IF EXISTS `recipes_recipe_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_recipe_authors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipe_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recipes_recipe_authors_recipe_id` (`recipe_id`),
  KEY `recipes_recipe_authors_author_id` (`author_id`),
  CONSTRAINT `author_id_refs_id_315969b8` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`),
  CONSTRAINT `recipe_id_refs_id_64395126` FOREIGN KEY (`recipe_id`) REFERENCES `recipes_recipe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_recipe_authors`
--

LOCK TABLES `recipes_recipe_authors` WRITE;
/*!40000 ALTER TABLE `recipes_recipe_authors` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_recipe_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_recipe_cuisines`
--

DROP TABLE IF EXISTS `recipes_recipe_cuisines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_recipe_cuisines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipe_id` int(11) NOT NULL,
  `cuisine_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recipes_recipe_cuisines_recipe_id` (`recipe_id`),
  KEY `recipes_recipe_cuisines_cuisine_id` (`cuisine_id`),
  CONSTRAINT `cuisine_id_refs_id_1f3d8bfb` FOREIGN KEY (`cuisine_id`) REFERENCES `recipes_cuisine` (`id`),
  CONSTRAINT `recipe_id_refs_id_1b9a854c` FOREIGN KEY (`recipe_id`) REFERENCES `recipes_recipe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_recipe_cuisines`
--

LOCK TABLES `recipes_recipe_cuisines` WRITE;
/*!40000 ALTER TABLE `recipes_recipe_cuisines` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_recipe_cuisines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_recipe_side_dishes`
--

DROP TABLE IF EXISTS `recipes_recipe_side_dishes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_recipe_side_dishes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recipe_id` int(11) NOT NULL,
  `sidedish_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `recipes_recipe_side_dishes_recipe_id` (`recipe_id`),
  KEY `recipes_recipe_side_dishes_sidedish_id` (`sidedish_id`),
  CONSTRAINT `recipe_id_refs_id_859070e` FOREIGN KEY (`recipe_id`) REFERENCES `recipes_recipe` (`id`),
  CONSTRAINT `sidedish_id_refs_id_3c9c54e1` FOREIGN KEY (`sidedish_id`) REFERENCES `recipes_sidedish` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_recipe_side_dishes`
--

LOCK TABLES `recipes_recipe_side_dishes` WRITE;
/*!40000 ALTER TABLE `recipes_recipe_side_dishes` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_recipe_side_dishes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_recipecategoryphoto`
--

DROP TABLE IF EXISTS `recipes_recipecategoryphoto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_recipecategoryphoto` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) NOT NULL,
  `photo_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `category_id` (`category_id`),
  KEY `recipes_recipecategoryphoto_photo_id` (`photo_id`),
  CONSTRAINT `category_id_refs_id_3435f637` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `photo_id_refs_id_4fc9ffac` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_recipecategoryphoto`
--

LOCK TABLES `recipes_recipecategoryphoto` WRITE;
/*!40000 ALTER TABLE `recipes_recipecategoryphoto` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_recipecategoryphoto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_recipeofday`
--

DROP TABLE IF EXISTS `recipes_recipeofday`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_recipeofday` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `recipe_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`),
  KEY `recipes_recipeofday_recipe_id` (`recipe_id`),
  CONSTRAINT `recipe_id_refs_id_305d818b` FOREIGN KEY (`recipe_id`) REFERENCES `recipes_recipe` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_recipeofday`
--

LOCK TABLES `recipes_recipeofday` WRITE;
/*!40000 ALTER TABLE `recipes_recipeofday` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_recipeofday` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_sidedish`
--

DROP TABLE IF EXISTS `recipes_sidedish`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_sidedish` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(64) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_sidedish`
--

LOCK TABLES `recipes_sidedish` WRITE;
/*!40000 ALTER TABLE `recipes_sidedish` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_sidedish` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_unit`
--

DROP TABLE IF EXISTS `recipes_unit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_unit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `plurals` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `note` varchar(128) COLLATE utf8_czech_ci NOT NULL,
  `g` decimal(8,3) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_unit`
--

LOCK TABLES `recipes_unit` WRITE;
/*!40000 ALTER TABLE `recipes_unit` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_unit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes_unitconversion`
--

DROP TABLE IF EXISTS `recipes_unitconversion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `recipes_unitconversion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_unit_id` int(11) NOT NULL,
  `to_unit_id` int(11) NOT NULL,
  `ratio` decimal(10,5) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `recipes_unitconversion_from_unit_id_6a402957` (`from_unit_id`,`to_unit_id`),
  KEY `recipes_unitconversion_from_unit_id` (`from_unit_id`),
  KEY `recipes_unitconversion_to_unit_id` (`to_unit_id`),
  CONSTRAINT `from_unit_id_refs_id_31fa2bc3` FOREIGN KEY (`from_unit_id`) REFERENCES `recipes_unit` (`id`),
  CONSTRAINT `to_unit_id_refs_id_31fa2bc3` FOREIGN KEY (`to_unit_id`) REFERENCES `recipes_unit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes_unitconversion`
--

LOCK TABLES `recipes_unitconversion` WRITE;
/*!40000 ALTER TABLE `recipes_unitconversion` DISABLE KEYS */;
/*!40000 ALTER TABLE `recipes_unitconversion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sendmail_mail`
--

DROP TABLE IF EXISTS `sendmail_mail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sendmail_mail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sender` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `recipient` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `sent` datetime NOT NULL DEFAULT '2009-05-20 17:58:39',
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(10) unsigned NOT NULL,
  `content` longtext COLLATE utf8_czech_ci,
  PRIMARY KEY (`id`),
  KEY `sendmail_mail_target_ct_id` (`target_ct_id`),
  KEY `sendmail_mail_target_id` (`target_id`),
  CONSTRAINT `target_ct_id_refs_id_75539bc2` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sendmail_mail`
--

LOCK TABLES `sendmail_mail` WRITE;
/*!40000 ALTER TABLE `sendmail_mail` DISABLE KEYS */;
/*!40000 ALTER TABLE `sendmail_mail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `series_serie`
--

DROP TABLE IF EXISTS `series_serie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `series_serie` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(96) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `perex` longtext COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `category_id` int(11) NOT NULL,
  `hide_newer_parts` tinyint(1) NOT NULL DEFAULT '0',
  `started` date NOT NULL,
  `finished` date DEFAULT NULL,
  `photo_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `series_serie_category_id` (`category_id`),
  KEY `series_serie_photo_id` (`photo_id`),
  CONSTRAINT `category_id_refs_id_269265ea` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `photo_id_refs_id_13a99f67` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `series_serie`
--

LOCK TABLES `series_serie` WRITE;
/*!40000 ALTER TABLE `series_serie` DISABLE KEYS */;
/*!40000 ALTER TABLE `series_serie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `series_seriepart`
--

DROP TABLE IF EXISTS `series_seriepart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `series_seriepart` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `serie_id` int(11) NOT NULL,
  `placement_id` int(11) NOT NULL,
  `part_no` smallint(5) unsigned NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `placement_id` (`placement_id`),
  KEY `series_seriepart_serie_id` (`serie_id`),
  CONSTRAINT `placement_id_refs_id_579f1421` FOREIGN KEY (`placement_id`) REFERENCES `core_placement` (`id`),
  CONSTRAINT `serie_id_refs_id_40fb1700` FOREIGN KEY (`serie_id`) REFERENCES `series_serie` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `series_seriepart`
--

LOCK TABLES `series_seriepart` WRITE;
/*!40000 ALTER TABLE `series_seriepart` DISABLE KEYS */;
/*!40000 ALTER TABLE `series_seriepart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `south_migrationhistory`
--

DROP TABLE IF EXISTS `south_migrationhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `south_migrationhistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_name` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `migration` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `applied` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `south_migrationhistory`
--

LOCK TABLES `south_migrationhistory` WRITE;
/*!40000 ALTER TABLE `south_migrationhistory` DISABLE KEYS */;
INSERT INTO `south_migrationhistory` VALUES (1,'core','0001_initial','2009-05-20 15:57:59'),(2,'photos','0001_initial','2009-05-20 15:58:03'),(3,'articles','0001_initial','2009-05-20 15:58:05'),(4,'comments','0001_initial','2009-05-20 15:58:08'),(5,'db_templates','0001_initial','2009-05-20 15:58:12'),(6,'galleries','0001_initial','2009-05-20 15:58:14'),(7,'polls','0001_initial','2009-05-20 15:58:18'),(8,'tagging','0001_initial','2009-05-20 15:58:23'),(9,'ratings','0001_initial','2009-05-20 15:58:25'),(10,'exports','0001_initial','2009-05-20 15:58:27'),(11,'imports','0001_initial','2009-05-20 15:58:29'),(12,'ellaadmin','0001_initial','2009-05-20 15:58:30'),(13,'interviews','0001_initial','2009-05-20 15:58:34'),(14,'positions','0001_initial','2009-05-20 15:58:37'),(15,'catlocks','0001_initial','2009-05-20 15:58:38'),(16,'sendmail','0001_initial','2009-05-20 15:58:39'),(17,'attachments','0001_initial','2009-05-20 15:58:42'),(18,'series','0001_initial','2009-05-20 15:58:44'),(19,'media','0001_initial','2009-05-20 15:58:47'),(20,'instruction','0001_initial','2009-05-20 15:58:50'),(21,'recipes','0001_initial','2009-05-20 15:58:57'),(22,'astrology','0001_initial','2009-05-20 15:59:13'),(23,'contact_form','0001_initial','2009-05-20 15:59:26'),(24,'adverts','0001_initial','2009-05-20 15:59:29');
/*!40000 ALTER TABLE `south_migrationhistory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tagging_tag`
--

DROP TABLE IF EXISTS `tagging_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tagging_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tagging_tag`
--

LOCK TABLES `tagging_tag` WRITE;
/*!40000 ALTER TABLE `tagging_tag` DISABLE KEYS */;
/*!40000 ALTER TABLE `tagging_tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tagging_taggeditem`
--

DROP TABLE IF EXISTS `tagging_taggeditem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tagging_taggeditem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag_id` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `object_id` int(10) unsigned NOT NULL,
  `category_id` int(11) DEFAULT NULL,
  `priority` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tagging_taggeditem_tag_id_2cd7eb0a` (`tag_id`,`content_type_id`,`object_id`,`priority`),
  KEY `tagging_taggeditem_tag_id` (`tag_id`),
  KEY `tagging_taggeditem_content_type_id` (`content_type_id`),
  KEY `tagging_taggeditem_object_id` (`object_id`),
  KEY `tagging_taggeditem_category_id` (`category_id`),
  KEY `tagging_taggeditem_priority` (`priority`),
  CONSTRAINT `category_id_refs_id_7d162783` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `content_type_id_refs_id_e07b113` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `tag_id_refs_id_60aefff3` FOREIGN KEY (`tag_id`) REFERENCES `tagging_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tagging_taggeditem`
--

LOCK TABLES `tagging_taggeditem` WRITE;
/*!40000 ALTER TABLE `tagging_taggeditem` DISABLE KEYS */;
/*!40000 ALTER TABLE `tagging_taggeditem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `writetosanta_inquiryofsanta`
--

DROP TABLE IF EXISTS `writetosanta_inquiryofsanta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `writetosanta_inquiryofsanta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `salutation` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `email_of_interviewed` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `email_of_inquirer` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `answer` varchar(3000) COLLATE utf8_czech_ci NOT NULL,
  `private_slug` varchar(40) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `writetosanta_inquiryofsanta_private_slug` (`private_slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `writetosanta_inquiryofsanta`
--

LOCK TABLES `writetosanta_inquiryofsanta` WRITE;
/*!40000 ALTER TABLE `writetosanta_inquiryofsanta` DISABLE KEYS */;
/*!40000 ALTER TABLE `writetosanta_inquiryofsanta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `xmastips_category`
--

DROP TABLE IF EXISTS `xmastips_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xmastips_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `xmastips_category`
--

LOCK TABLES `xmastips_category` WRITE;
/*!40000 ALTER TABLE `xmastips_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `xmastips_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `xmastips_eshop`
--

DROP TABLE IF EXISTS `xmastips_eshop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xmastips_eshop` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `service_email` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `xml_url` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `feedset_count` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `xmastips_eshop`
--

LOCK TABLES `xmastips_eshop` WRITE;
/*!40000 ALTER TABLE `xmastips_eshop` DISABLE KEYS */;
/*!40000 ALTER TABLE `xmastips_eshop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `xmastips_feedset`
--

DROP TABLE IF EXISTS `xmastips_feedset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xmastips_feedset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `eshop_id` int(11) NOT NULL,
  `serial_number` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `xmastips_feedset_eshop_id` (`eshop_id`),
  CONSTRAINT `eshop_id_refs_id_5eb11346` FOREIGN KEY (`eshop_id`) REFERENCES `xmastips_eshop` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `xmastips_feedset`
--

LOCK TABLES `xmastips_feedset` WRITE;
/*!40000 ALTER TABLE `xmastips_feedset` DISABLE KEYS */;
/*!40000 ALTER TABLE `xmastips_feedset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `xmastips_present`
--

DROP TABLE IF EXISTS `xmastips_present`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xmastips_present` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) NOT NULL,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `price` int(11) NOT NULL,
  `price_tax` int(11) NOT NULL,
  `product_url` varchar(400) COLLATE utf8_czech_ci NOT NULL,
  `image_url` varchar(400) COLLATE utf8_czech_ci NOT NULL,
  `age` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `feedset_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `xmastips_present_category_id` (`category_id`),
  KEY `xmastips_present_feedset_id` (`feedset_id`),
  CONSTRAINT `category_id_refs_id_33f06f6d` FOREIGN KEY (`category_id`) REFERENCES `xmastips_category` (`id`),
  CONSTRAINT `feedset_id_refs_id_46bbd222` FOREIGN KEY (`feedset_id`) REFERENCES `xmastips_feedset` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `xmastips_present`
--

LOCK TABLES `xmastips_present` WRITE;
/*!40000 ALTER TABLE `xmastips_present` DISABLE KEYS */;
/*!40000 ALTER TABLE `xmastips_present` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `xmastips_present_target_group`
--

DROP TABLE IF EXISTS `xmastips_present_target_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xmastips_present_target_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `present_id` int(11) NOT NULL,
  `targetgroup_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `present_id` (`present_id`,`targetgroup_id`),
  KEY `targetgroup_id_refs_id_1b185599` (`targetgroup_id`),
  CONSTRAINT `targetgroup_id_refs_id_1b185599` FOREIGN KEY (`targetgroup_id`) REFERENCES `xmastips_targetgroup` (`id`),
  CONSTRAINT `present_id_refs_id_5dfc311a` FOREIGN KEY (`present_id`) REFERENCES `xmastips_present` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `xmastips_present_target_group`
--

LOCK TABLES `xmastips_present_target_group` WRITE;
/*!40000 ALTER TABLE `xmastips_present_target_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `xmastips_present_target_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `xmastips_targetgroup`
--

DROP TABLE IF EXISTS `xmastips_targetgroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xmastips_targetgroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `xmastips_targetgroup`
--

LOCK TABLES `xmastips_targetgroup` WRITE;
/*!40000 ALTER TABLE `xmastips_targetgroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `xmastips_targetgroup` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-05-20 16:01:40
