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
-- Table structure for table `answers_answer`
--

DROP TABLE IF EXISTS `answers_answer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `answers_answer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text` longtext COLLATE utf8_czech_ci NOT NULL,
  `nick` varchar(150) COLLATE utf8_czech_ci NOT NULL,
  `authorized_user_id` int(11) DEFAULT NULL,
  `created` datetime NOT NULL,
  `question_id` int(11) NOT NULL,
  `is_hidden` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `answers_answer_authorized_user_id` (`authorized_user_id`),
  KEY `answers_answer_question_id` (`question_id`),
  CONSTRAINT `authorized_user_id_refs_id_4903a00c` FOREIGN KEY (`authorized_user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `question_id_refs_id_65280acf` FOREIGN KEY (`question_id`) REFERENCES `answers_question` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `answers_answer`
--

LOCK TABLES `answers_answer` WRITE;
/*!40000 ALTER TABLE `answers_answer` DISABLE KEYS */;
/*!40000 ALTER TABLE `answers_answer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `answers_question`
--

DROP TABLE IF EXISTS `answers_question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `answers_question` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text` varchar(200) COLLATE utf8_czech_ci NOT NULL,
  `specification` longtext COLLATE utf8_czech_ci NOT NULL,
  `nick` varchar(150) COLLATE utf8_czech_ci NOT NULL,
  `created` datetime NOT NULL,
  `slug` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `timelimit` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `answers_question_slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `answers_question`
--

LOCK TABLES `answers_question` WRITE;
/*!40000 ALTER TABLE `answers_question` DISABLE KEYS */;
/*!40000 ALTER TABLE `answers_question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `answers_questiongroup`
--

DROP TABLE IF EXISTS `answers_questiongroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `answers_questiongroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `site_id` int(11) NOT NULL,
  `default_timelimit` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `answers_questiongroup_site_id` (`site_id`),
  CONSTRAINT `site_id_refs_id_7104979b` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `answers_questiongroup`
--

LOCK TABLES `answers_questiongroup` WRITE;
/*!40000 ALTER TABLE `answers_questiongroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `answers_questiongroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `answers_questiongroup_questions`
--

DROP TABLE IF EXISTS `answers_questiongroup_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `answers_questiongroup_questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `questiongroup_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `questiongroup_id` (`questiongroup_id`,`question_id`),
  KEY `question_id_refs_id_4159f261` (`question_id`),
  CONSTRAINT `question_id_refs_id_4159f261` FOREIGN KEY (`question_id`) REFERENCES `answers_question` (`id`),
  CONSTRAINT `questiongroup_id_refs_id_7b20bdf5` FOREIGN KEY (`questiongroup_id`) REFERENCES `answers_questiongroup` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `answers_questiongroup_questions`
--

LOCK TABLES `answers_questiongroup_questions` WRITE;
/*!40000 ALTER TABLE `answers_questiongroup_questions` DISABLE KEYS */;
/*!40000 ALTER TABLE `answers_questiongroup_questions` ENABLE KEYS */;
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
  `created` datetime NOT NULL,
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
  UNIQUE KEY `article_id` (`article_id`,`author_id`),
  KEY `author_id_refs_id_23a52912` (`author_id`),
  CONSTRAINT `author_id_refs_id_23a52912` FOREIGN KEY (`author_id`) REFERENCES `core_author` (`id`),
  CONSTRAINT `article_id_refs_id_1bb2108a` FOREIGN KEY (`article_id`) REFERENCES `articles_article` (`id`)
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
  `created` datetime NOT NULL,
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
  UNIQUE KEY `category_id` (`category_id`,`publish_date`),
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
  `ordering` smallint(5) unsigned NOT NULL,
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
  UNIQUE KEY `sign_id` (`sign_id`,`duration_id`,`type_id`,`start_day`),
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
  `ordering` smallint(5) unsigned NOT NULL,
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
  `ordering` smallint(5) unsigned NOT NULL,
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
  `ordering` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `horoscope_id` (`horoscope_id`,`slug`),
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
  UNIQUE KEY `sign_male_id` (`sign_male_id`,`sign_female_id`),
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
  UNIQUE KEY `sign_id` (`sign_id`,`type_id`),
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
  `ordering` smallint(5) unsigned NOT NULL,
  `visible` tinyint(1) NOT NULL,
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
  `ordering` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sign_id` (`sign_id`,`stone_id`),
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
  `created` datetime NOT NULL,
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
  UNIQUE KEY `name` (`name`,`mimetype`)
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
) ENGINE=InnoDB AUTO_INCREMENT=474 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add message',4,'add_message'),(11,'Can change message',4,'change_message'),(12,'Can delete message',4,'delete_message'),(13,'Can view permission',1,'view_permission'),(14,'Can view group',2,'view_group'),(15,'Can view user',3,'view_user'),(16,'Can view message',4,'view_message'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add site',7,'add_site'),(26,'Can change site',7,'change_site'),(27,'Can delete site',7,'delete_site'),(28,'Can view site',7,'view_site'),(29,'Can add redirect',8,'add_redirect'),(30,'Can change redirect',8,'change_redirect'),(31,'Can delete redirect',8,'delete_redirect'),(32,'Can view redirect',8,'view_redirect'),(33,'Can add Author',9,'add_author'),(34,'Can change Author',9,'change_author'),(35,'Can delete Author',9,'delete_author'),(36,'Can add Source',10,'add_source'),(37,'Can change Source',10,'change_source'),(38,'Can delete Source',10,'delete_source'),(39,'Can add Category',11,'add_category'),(40,'Can change Category',11,'change_category'),(41,'Can delete Category',11,'delete_category'),(42,'Can add Placement',12,'add_placement'),(43,'Can change Placement',12,'change_placement'),(44,'Can delete Placement',12,'delete_placement'),(45,'Can add Listing',13,'add_listing'),(46,'Can change Listing',13,'change_listing'),(47,'Can delete Listing',13,'delete_listing'),(48,'Can add Hit Count',14,'add_hitcount'),(49,'Can change Hit Count',14,'change_hitcount'),(50,'Can delete Hit Count',14,'delete_hitcount'),(51,'Can add Related',15,'add_related'),(52,'Can change Related',15,'change_related'),(53,'Can delete Related',15,'delete_related'),(54,'Can view Author',9,'view_author'),(55,'Can view Source',10,'view_source'),(56,'Can view Category',11,'view_category'),(57,'Can view Placement',12,'view_placement'),(58,'Can view Listing',13,'view_listing'),(59,'Can view Hit Count',14,'view_hitcount'),(60,'Can view Related',15,'view_related'),(61,'Can add Info box',16,'add_infobox'),(62,'Can change Info box',16,'change_infobox'),(63,'Can delete Info box',16,'delete_infobox'),(64,'Can add Article',17,'add_article'),(65,'Can change Article',17,'change_article'),(66,'Can delete Article',17,'delete_article'),(67,'Can add Article content',18,'add_articlecontents'),(68,'Can change Article content',18,'change_articlecontents'),(69,'Can delete Article content',18,'delete_articlecontents'),(70,'Can view Info box',16,'view_infobox'),(71,'Can view Article',17,'view_article'),(72,'Can view Article content',18,'view_articlecontents'),(73,'Can add Comment Options',19,'add_commentoptions'),(74,'Can change Comment Options',19,'change_commentoptions'),(75,'Can delete Comment Options',19,'delete_commentoptions'),(76,'Can add Comment',20,'add_comment'),(77,'Can change Comment',20,'change_comment'),(78,'Can delete Comment',20,'delete_comment'),(79,'Can add Banned User',21,'add_banneduser'),(80,'Can change Banned User',21,'change_banneduser'),(81,'Can delete Banned User',21,'delete_banneduser'),(82,'Can add banned ip',22,'add_bannedip'),(83,'Can change banned ip',22,'change_bannedip'),(84,'Can delete banned ip',22,'delete_bannedip'),(85,'Can view Comment Options',19,'view_commentoptions'),(86,'Can view Comment',20,'view_comment'),(87,'Can view Banned User',21,'view_banneduser'),(88,'Can view banned ip',22,'view_bannedip'),(89,'Can add Photo',23,'add_photo'),(90,'Can change Photo',23,'change_photo'),(91,'Can delete Photo',23,'delete_photo'),(92,'Can add Format',24,'add_format'),(93,'Can change Format',24,'change_format'),(94,'Can delete Format',24,'delete_format'),(95,'Can add Formated photo',25,'add_formatedphoto'),(96,'Can change Formated photo',25,'change_formatedphoto'),(97,'Can delete Formated photo',25,'delete_formatedphoto'),(98,'Can view Photo',23,'view_photo'),(99,'Can view Format',24,'view_format'),(100,'Can view Formated photo',25,'view_formatedphoto'),(101,'Can add Template',26,'add_dbtemplate'),(102,'Can change Template',26,'change_dbtemplate'),(103,'Can delete Template',26,'delete_dbtemplate'),(104,'Can add Template block',27,'add_templateblock'),(105,'Can change Template block',27,'change_templateblock'),(106,'Can delete Template block',27,'delete_templateblock'),(107,'Can view Template',26,'view_dbtemplate'),(108,'Can view Template block',27,'view_templateblock'),(109,'Can add Gallery',28,'add_gallery'),(110,'Can change Gallery',28,'change_gallery'),(111,'Can delete Gallery',28,'delete_gallery'),(112,'Can add Gallery item',29,'add_galleryitem'),(113,'Can change Gallery item',29,'change_galleryitem'),(114,'Can delete Gallery item',29,'delete_galleryitem'),(115,'Can view Gallery',28,'view_gallery'),(116,'Can view Gallery item',29,'view_galleryitem'),(117,'Can add Contest',30,'add_contest'),(118,'Can change Contest',30,'change_contest'),(119,'Can delete Contest',30,'delete_contest'),(120,'Can add Quiz',31,'add_quiz'),(121,'Can change Quiz',31,'change_quiz'),(122,'Can delete Quiz',31,'delete_quiz'),(123,'Can add Question',32,'add_question'),(124,'Can change Question',32,'change_question'),(125,'Can delete Question',32,'delete_question'),(126,'Can add Poll',33,'add_poll'),(127,'Can change Poll',33,'change_poll'),(128,'Can delete Poll',33,'delete_poll'),(129,'Can add Choice',34,'add_choice'),(130,'Can change Choice',34,'change_choice'),(131,'Can delete Choice',34,'delete_choice'),(132,'Can add Vote',35,'add_vote'),(133,'Can change Vote',35,'change_vote'),(134,'Can delete Vote',35,'delete_vote'),(135,'Can add Contestant',36,'add_contestant'),(136,'Can change Contestant',36,'change_contestant'),(137,'Can delete Contestant',36,'delete_contestant'),(138,'Can add Result',37,'add_result'),(139,'Can change Result',37,'change_result'),(140,'Can delete Result',37,'delete_result'),(141,'Can view Contest',30,'view_contest'),(142,'Can view Quiz',31,'view_quiz'),(143,'Can view Question',32,'view_question'),(144,'Can view Poll',33,'view_poll'),(145,'Can view Choice',34,'view_choice'),(146,'Can view Vote',35,'view_vote'),(147,'Can view Contestant',36,'view_contestant'),(148,'Can view Result',37,'view_result'),(149,'Can add tag',38,'add_tag'),(150,'Can change tag',38,'change_tag'),(151,'Can delete tag',38,'delete_tag'),(152,'Can add tagged item',39,'add_taggeditem'),(153,'Can change tagged item',39,'change_taggeditem'),(154,'Can delete tagged item',39,'delete_taggeditem'),(155,'Can view tag',38,'view_tag'),(156,'Can view tagged item',39,'view_taggeditem'),(157,'Can add Model weight',40,'add_modelweight'),(158,'Can change Model weight',40,'change_modelweight'),(159,'Can delete Model weight',40,'delete_modelweight'),(160,'Can add Total rate',41,'add_totalrate'),(161,'Can change Total rate',41,'change_totalrate'),(162,'Can delete Total rate',41,'delete_totalrate'),(163,'Can add Aggregation',42,'add_agg'),(164,'Can change Aggregation',42,'change_agg'),(165,'Can delete Aggregation',42,'delete_agg'),(166,'Can add Rating',43,'add_rating'),(167,'Can change Rating',43,'change_rating'),(168,'Can delete Rating',43,'delete_rating'),(169,'Can view Model weight',40,'view_modelweight'),(170,'Can view Total rate',41,'view_totalrate'),(171,'Can view Aggregation',42,'view_agg'),(172,'Can view Rating',43,'view_rating'),(173,'Can add atlas export',44,'add_atlasexport'),(174,'Can change atlas export',44,'change_atlasexport'),(175,'Can delete atlas export',44,'delete_atlasexport'),(176,'Can view atlas export',44,'view_atlasexport'),(177,'Can add Server',45,'add_server'),(178,'Can change Server',45,'change_server'),(179,'Can delete Server',45,'delete_server'),(180,'Can add Server item',46,'add_serveritem'),(181,'Can change Server item',46,'change_serveritem'),(182,'Can delete Server item',46,'delete_serveritem'),(183,'Can view Server',45,'view_server'),(184,'Can view Server item',46,'view_serveritem'),(185,'Can add Topic',47,'add_topic'),(186,'Can change Topic',47,'change_topic'),(187,'Can delete Topic',47,'delete_topic'),(188,'Can add post viewed',48,'add_postviewed'),(189,'Can change post viewed',48,'change_postviewed'),(190,'Can delete post viewed',48,'delete_postviewed'),(191,'Can add Thread',49,'add_topicthread'),(192,'Can change Thread',49,'change_topicthread'),(193,'Can delete Thread',49,'delete_topicthread'),(194,'Can add banned string',50,'add_bannedstring'),(195,'Can change banned string',50,'change_bannedstring'),(196,'Can delete banned string',50,'delete_bannedstring'),(197,'Can add banned user',51,'add_banneduser'),(198,'Can change banned user',51,'change_banneduser'),(199,'Can delete banned user',51,'delete_banneduser'),(200,'Can view Topic',47,'view_topic'),(201,'Can view post viewed',48,'view_postviewed'),(202,'Can view Thread',49,'view_topicthread'),(203,'Can view banned string',50,'view_bannedstring'),(204,'Can view banned user',51,'view_banneduser'),(205,'Can add Interviewee',52,'add_interviewee'),(206,'Can change Interviewee',52,'change_interviewee'),(207,'Can delete Interviewee',52,'delete_interviewee'),(208,'Can add Interview',53,'add_interview'),(209,'Can change Interview',53,'change_interview'),(210,'Can delete Interview',53,'delete_interview'),(211,'Can add Question',54,'add_question'),(212,'Can change Question',54,'change_question'),(213,'Can delete Question',54,'delete_question'),(214,'Can add Answer',55,'add_answer'),(215,'Can change Answer',55,'change_answer'),(216,'Can delete Answer',55,'delete_answer'),(217,'Can view Interviewee',52,'view_interviewee'),(218,'Can view Interview',53,'view_interview'),(219,'Can view Question',54,'view_question'),(220,'Can view Answer',55,'view_answer'),(221,'Can add position',56,'add_position'),(222,'Can change position',56,'change_position'),(223,'Can delete position',56,'delete_position'),(224,'Can view position',56,'view_position'),(225,'Can add Category Lock',57,'add_categorylock'),(226,'Can change Category Lock',57,'change_categorylock'),(227,'Can delete Category Lock',57,'delete_categorylock'),(228,'Can view Category Lock',57,'view_categorylock'),(229,'Can add mail',58,'add_mail'),(230,'Can change mail',58,'change_mail'),(231,'Can delete mail',58,'delete_mail'),(232,'Can view mail',58,'view_mail'),(233,'Can add log entry',59,'add_logentry'),(234,'Can change log entry',59,'change_logentry'),(235,'Can delete log entry',59,'delete_logentry'),(236,'Can view log entry',59,'view_logentry'),(237,'Can add Type',60,'add_type'),(238,'Can change Type',60,'change_type'),(239,'Can delete Type',60,'delete_type'),(240,'Can add Attachment',61,'add_attachment'),(241,'Can change Attachment',61,'change_attachment'),(242,'Can delete Attachment',61,'delete_attachment'),(243,'Can view Type',60,'view_type'),(244,'Can view Attachment',61,'view_attachment'),(245,'Can add question',62,'add_question'),(246,'Can change question',62,'change_question'),(247,'Can delete question',62,'delete_question'),(248,'Can add answer',63,'add_answer'),(249,'Can change answer',63,'change_answer'),(250,'Can delete answer',63,'delete_answer'),(251,'Can answer as an expert',63,'can_answer_as_expert'),(252,'Can add question group',64,'add_questiongroup'),(253,'Can change question group',64,'change_questiongroup'),(254,'Can delete question group',64,'delete_questiongroup'),(255,'Can view question',62,'view_question'),(256,'Can view answer',63,'view_answer'),(257,'Can view question group',64,'view_questiongroup'),(258,'Can add Serie',65,'add_serie'),(259,'Can change Serie',65,'change_serie'),(260,'Can delete Serie',65,'delete_serie'),(261,'Can add Serie part',66,'add_seriepart'),(262,'Can change Serie part',66,'change_seriepart'),(263,'Can delete Serie part',66,'delete_seriepart'),(264,'Can view Serie',65,'view_serie'),(265,'Can view Serie part',66,'view_seriepart'),(266,'Can add Media',67,'add_media'),(267,'Can change Media',67,'change_media'),(268,'Can delete Media',67,'delete_media'),(269,'Can add section',68,'add_section'),(270,'Can change section',68,'change_section'),(271,'Can delete section',68,'delete_section'),(272,'Can add usage',69,'add_usage'),(273,'Can change usage',69,'change_usage'),(274,'Can delete usage',69,'delete_usage'),(275,'Can view Media',67,'view_media'),(276,'Can view section',68,'view_section'),(277,'Can view usage',69,'view_usage'),(278,'Can add Instruction',70,'add_instruction'),(279,'Can change Instruction',70,'change_instruction'),(280,'Can delete Instruction',70,'delete_instruction'),(281,'Can view Instruction',70,'view_instruction'),(282,'Can add Cooking type',71,'add_cookingtype'),(283,'Can change Cooking type',71,'change_cookingtype'),(284,'Can delete Cooking type',71,'delete_cookingtype'),(285,'Can add Cuisine',72,'add_cuisine'),(286,'Can change Cuisine',72,'change_cuisine'),(287,'Can delete Cuisine',72,'delete_cuisine'),(288,'Can add Nutrient group',73,'add_nutrientgroup'),(289,'Can change Nutrient group',73,'change_nutrientgroup'),(290,'Can delete Nutrient group',73,'delete_nutrientgroup'),(291,'Can add Nutrient',74,'add_nutrient'),(292,'Can change Nutrient',74,'change_nutrient'),(293,'Can delete Nutrient',74,'delete_nutrient'),(294,'Can add Unit',75,'add_unit'),(295,'Can change Unit',75,'change_unit'),(296,'Can delete Unit',75,'delete_unit'),(297,'Can add Unit conversion',76,'add_unitconversion'),(298,'Can change Unit conversion',76,'change_unitconversion'),(299,'Can delete Unit conversion',76,'delete_unitconversion'),(300,'Can add Ingredient group',77,'add_ingredientgroup'),(301,'Can change Ingredient group',77,'change_ingredientgroup'),(302,'Can delete Ingredient group',77,'delete_ingredientgroup'),(303,'Can add Ingredient',78,'add_ingredient'),(304,'Can change Ingredient',78,'change_ingredient'),(305,'Can delete Ingredient',78,'delete_ingredient'),(306,'Can add Nutrient in ingredient',79,'add_nutrientiningredient'),(307,'Can change Nutrient in ingredient',79,'change_nutrientiningredient'),(308,'Can delete Nutrient in ingredient',79,'delete_nutrientiningredient'),(309,'Can add Category photo',80,'add_recipecategoryphoto'),(310,'Can change Category photo',80,'change_recipecategoryphoto'),(311,'Can delete Category photo',80,'delete_recipecategoryphoto'),(312,'Can add Side-dish',81,'add_sidedish'),(313,'Can change Side-dish',81,'change_sidedish'),(314,'Can delete Side-dish',81,'delete_sidedish'),(315,'Can add Recipe',82,'add_recipe'),(316,'Can change Recipe',82,'change_recipe'),(317,'Can delete Recipe',82,'delete_recipe'),(318,'Can add Ingredient in recipe',83,'add_ingredientinrecipe'),(319,'Can change Ingredient in recipe',83,'change_ingredientinrecipe'),(320,'Can delete Ingredient in recipe',83,'delete_ingredientinrecipe'),(321,'Can add Recipe of day',84,'add_recipeofday'),(322,'Can change Recipe of day',84,'change_recipeofday'),(323,'Can delete Recipe of day',84,'delete_recipeofday'),(324,'Can add old recipe article redirect',85,'add_oldrecipearticleredirect'),(325,'Can change old recipe article redirect',85,'change_oldrecipearticleredirect'),(326,'Can delete old recipe article redirect',85,'delete_oldrecipearticleredirect'),(327,'Can add old recipe category redirect',86,'add_oldrecipecategoryredirect'),(328,'Can change old recipe category redirect',86,'change_oldrecipecategoryredirect'),(329,'Can delete old recipe category redirect',86,'delete_oldrecipecategoryredirect'),(330,'Can view Cooking type',71,'view_cookingtype'),(331,'Can view Cuisine',72,'view_cuisine'),(332,'Can view Nutrient group',73,'view_nutrientgroup'),(333,'Can view Nutrient',74,'view_nutrient'),(334,'Can view Unit',75,'view_unit'),(335,'Can view Unit conversion',76,'view_unitconversion'),(336,'Can view Ingredient group',77,'view_ingredientgroup'),(337,'Can view Ingredient',78,'view_ingredient'),(338,'Can view Nutrient in ingredient',79,'view_nutrientiningredient'),(339,'Can view Category photo',80,'view_recipecategoryphoto'),(340,'Can view Side-dish',81,'view_sidedish'),(341,'Can view Recipe',82,'view_recipe'),(342,'Can view Ingredient in recipe',83,'view_ingredientinrecipe'),(343,'Can view Recipe of day',84,'view_recipeofday'),(344,'Can view old recipe article redirect',85,'view_oldrecipearticleredirect'),(345,'Can view old recipe category redirect',86,'view_oldrecipecategoryredirect'),(346,'Can add Horoscope',87,'add_horoscope'),(347,'Can change Horoscope',87,'change_horoscope'),(348,'Can delete Horoscope',87,'delete_horoscope'),(349,'Can add Sign',88,'add_sign'),(350,'Can change Sign',88,'change_sign'),(351,'Can delete Sign',88,'delete_sign'),(352,'Can add Sign description type',89,'add_signdescriptiontype'),(353,'Can change Sign description type',89,'change_signdescriptiontype'),(354,'Can delete Sign description type',89,'delete_signdescriptiontype'),(355,'Can add Sign description',90,'add_signdescription'),(356,'Can change Sign description',90,'change_signdescription'),(357,'Can delete Sign description',90,'delete_signdescription'),(358,'Can add Birth period',91,'add_birthperiod'),(359,'Can change Birth period',91,'change_birthperiod'),(360,'Can delete Birth period',91,'delete_birthperiod'),(361,'Can add Sign compatibility',92,'add_signcompatibility'),(362,'Can change Sign compatibility',92,'change_signcompatibility'),(363,'Can delete Sign compatibility',92,'delete_signcompatibility'),(364,'Can add Prognosis duration',93,'add_prognosisduration'),(365,'Can change Prognosis duration',93,'change_prognosisduration'),(366,'Can delete Prognosis duration',93,'delete_prognosisduration'),(367,'Can add Prognosis type',94,'add_prognosistype'),(368,'Can change Prognosis type',94,'change_prognosistype'),(369,'Can delete Prognosis type',94,'delete_prognosistype'),(370,'Can add Prognosis',95,'add_prognosis'),(371,'Can change Prognosis',95,'change_prognosis'),(372,'Can delete Prognosis',95,'delete_prognosis'),(373,'Can add Lunar diary category',96,'add_lunardiarycategory'),(374,'Can change Lunar diary category',96,'change_lunardiarycategory'),(375,'Can delete Lunar diary category',96,'delete_lunardiarycategory'),(376,'Can add Lunar diary',97,'add_lunardiary'),(377,'Can change Lunar diary',97,'change_lunardiary'),(378,'Can delete Lunar diary',97,'delete_lunardiary'),(379,'Can add Lexicon term',98,'add_astrolex'),(380,'Can change Lexicon term',98,'change_astrolex'),(381,'Can delete Lexicon term',98,'delete_astrolex'),(382,'Can add Life number',99,'add_lifenumber'),(383,'Can change Life number',99,'change_lifenumber'),(384,'Can delete Life number',99,'delete_lifenumber'),(385,'Can add Stone',100,'add_stone'),(386,'Can change Stone',100,'change_stone'),(387,'Can delete Stone',100,'delete_stone'),(388,'Can add Stone for Sign',101,'add_stoneforsign'),(389,'Can change Stone for Sign',101,'change_stoneforsign'),(390,'Can delete Stone for Sign',101,'delete_stoneforsign'),(391,'Can add Numerology grid number',102,'add_numerologygrid'),(392,'Can change Numerology grid number',102,'change_numerologygrid'),(393,'Can delete Numerology grid number',102,'delete_numerologygrid'),(394,'Can add Moon in Sign',103,'add_moon'),(395,'Can change Moon in Sign',103,'change_moon'),(396,'Can delete Moon in Sign',103,'delete_moon'),(397,'Can view Horoscope',87,'view_horoscope'),(398,'Can view Sign',88,'view_sign'),(399,'Can view Sign description type',89,'view_signdescriptiontype'),(400,'Can view Sign description',90,'view_signdescription'),(401,'Can view Birth period',91,'view_birthperiod'),(402,'Can view Sign compatibility',92,'view_signcompatibility'),(403,'Can view Prognosis duration',93,'view_prognosisduration'),(404,'Can view Prognosis type',94,'view_prognosistype'),(405,'Can view Prognosis',95,'view_prognosis'),(406,'Can view Lunar diary category',96,'view_lunardiarycategory'),(407,'Can view Lunar diary',97,'view_lunardiary'),(408,'Can view Lexicon term',98,'view_astrolex'),(409,'Can view Life number',99,'view_lifenumber'),(410,'Can view Stone',100,'view_stone'),(411,'Can view Stone for Sign',101,'view_stoneforsign'),(412,'Can view Numerology grid number',102,'view_numerologygrid'),(413,'Can view Moon in Sign',103,'view_moon'),(414,'Can add newsletter',104,'add_newsletter'),(415,'Can change newsletter',104,'change_newsletter'),(416,'Can delete newsletter',104,'delete_newsletter'),(417,'Can add recipient',105,'add_recipient'),(418,'Can change recipient',105,'change_recipient'),(419,'Can delete recipient',105,'delete_recipient'),(420,'Can view newsletter',104,'view_newsletter'),(421,'Can view recipient',105,'view_recipient'),(422,'Can add format',106,'add_format'),(423,'Can change format',106,'change_format'),(424,'Can delete format',106,'delete_format'),(425,'Can add source',107,'add_source'),(426,'Can change source',107,'change_source'),(427,'Can delete source',107,'delete_source'),(428,'Can add target',108,'add_target'),(429,'Can change target',108,'change_target'),(430,'Can delete target',108,'delete_target'),(431,'Can view format',106,'view_format'),(432,'Can view source',107,'view_source'),(433,'Can view target',108,'view_target'),(434,'Can add Contact form recipient',109,'add_recipient'),(435,'Can change Contact form recipient',109,'change_recipient'),(436,'Can delete Contact form recipient',109,'delete_recipient'),(437,'Can add Contact form message',110,'add_message'),(438,'Can change Contact form message',110,'change_message'),(439,'Can delete Contact form message',110,'delete_message'),(440,'Can view Contact form recipient',109,'view_recipient'),(441,'Can view Contact form message',110,'view_message'),(442,'Can add Eshop',111,'add_eshop'),(443,'Can change Eshop',111,'change_eshop'),(444,'Can delete Eshop',111,'delete_eshop'),(445,'Can add Feedset',112,'add_feedset'),(446,'Can change Feedset',112,'change_feedset'),(447,'Can delete Feedset',112,'delete_feedset'),(448,'Can add Category',113,'add_category'),(449,'Can change Category',113,'change_category'),(450,'Can delete Category',113,'delete_category'),(451,'Can add Target group',114,'add_targetgroup'),(452,'Can change Target group',114,'change_targetgroup'),(453,'Can delete Target group',114,'delete_targetgroup'),(454,'Can add Present',115,'add_present'),(455,'Can change Present',115,'change_present'),(456,'Can delete Present',115,'delete_present'),(457,'Can view Eshop',111,'view_eshop'),(458,'Can view Feedset',112,'view_feedset'),(459,'Can view Category',113,'view_category'),(460,'Can view Target group',114,'view_targetgroup'),(461,'Can view Present',115,'view_present'),(462,'Can add Inquiry of Santa',116,'add_inquiryofsanta'),(463,'Can change Inquiry of Santa',116,'change_inquiryofsanta'),(464,'Can delete Inquiry of Santa',116,'delete_inquiryofsanta'),(465,'Can view Inquiry of Santa',116,'view_inquiryofsanta'),(466,'Can add Category - section mapping',117,'add_categorysectionmapping'),(467,'Can change Category - section mapping',117,'change_categorysectionmapping'),(468,'Can delete Category - section mapping',117,'delete_categorysectionmapping'),(469,'Can add Site - server mapping',118,'add_siteservermapping'),(470,'Can change Site - server mapping',118,'change_siteservermapping'),(471,'Can delete Site - server mapping',118,'delete_siteservermapping'),(472,'Can view Category - section mapping',117,'view_categorysectionmapping'),(473,'Can view Site - server mapping',118,'view_siteservermapping');
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
INSERT INTO `auth_user` VALUES (1,'admin','','','a@a.cz','sha1$9bf55$e1577b0bbfc0437c6e1173d5d08f6c5702c21b97',1,1,1,'2009-05-19 15:10:30','2009-05-19 15:10:30');
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
  `submit_date` datetime NOT NULL,
  `is_public` tinyint(1) NOT NULL,
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
  `timestamp` datetime NOT NULL,
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
  `created` datetime NOT NULL,
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
  UNIQUE KEY `recipient_id` (`recipient_id`,`site_id`),
  KEY `site_id_refs_id_5e2dda37` (`site_id`),
  CONSTRAINT `site_id_refs_id_5e2dda37` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`),
  CONSTRAINT `recipient_id_refs_id_65d1f87e` FOREIGN KEY (`recipient_id`) REFERENCES `contact_form_recipient` (`id`)
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
  UNIQUE KEY `site_id` (`site_id`,`tree_path`),
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
  `hits` int(10) unsigned NOT NULL,
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
  `remove` tinyint(1) NOT NULL,
  `commercial` tinyint(1) NOT NULL,
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
  `static` tinyint(1) NOT NULL,
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
  UNIQUE KEY `site_id` (`site_id`,`name`),
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
  UNIQUE KEY `template_id` (`template_id`,`name`,`active_from`,`active_till`),
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
-- Table structure for table `discussions_bannedstring`
--

DROP TABLE IF EXISTS `discussions_bannedstring`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `discussions_bannedstring` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `expression` varchar(20) COLLATE utf8_czech_ci NOT NULL,
  `isregexp` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `discussions_bannedstring_expression` (`expression`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discussions_bannedstring`
--

LOCK TABLES `discussions_bannedstring` WRITE;
/*!40000 ALTER TABLE `discussions_bannedstring` DISABLE KEYS */;
/*!40000 ALTER TABLE `discussions_bannedstring` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discussions_banneduser`
--

DROP TABLE IF EXISTS `discussions_banneduser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `discussions_banneduser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `discussions_banneduser_user_id` (`user_id`),
  CONSTRAINT `user_id_refs_id_61ee9023` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discussions_banneduser`
--

LOCK TABLES `discussions_banneduser` WRITE;
/*!40000 ALTER TABLE `discussions_banneduser` DISABLE KEYS */;
/*!40000 ALTER TABLE `discussions_banneduser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discussions_postviewed`
--

DROP TABLE IF EXISTS `discussions_postviewed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `discussions_postviewed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_ct_id` int(11) NOT NULL,
  `target_id` int(10) unsigned NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `discussions_postviewed_target_ct_id` (`target_ct_id`),
  KEY `discussions_postviewed_user_id` (`user_id`),
  CONSTRAINT `target_ct_id_refs_id_2086756e` FOREIGN KEY (`target_ct_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_7ccf9622` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discussions_postviewed`
--

LOCK TABLES `discussions_postviewed` WRITE;
/*!40000 ALTER TABLE `discussions_postviewed` DISABLE KEYS */;
/*!40000 ALTER TABLE `discussions_postviewed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discussions_topic`
--

DROP TABLE IF EXISTS `discussions_topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `discussions_topic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `description` longtext COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `category_id` int(11) NOT NULL,
  `photo_id` int(11) DEFAULT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `discussions_topic_slug` (`slug`),
  KEY `discussions_topic_category_id` (`category_id`),
  KEY `discussions_topic_photo_id` (`photo_id`),
  CONSTRAINT `category_id_refs_id_614de80e` FOREIGN KEY (`category_id`) REFERENCES `core_category` (`id`),
  CONSTRAINT `photo_id_refs_id_75a1250f` FOREIGN KEY (`photo_id`) REFERENCES `photos_photo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discussions_topic`
--

LOCK TABLES `discussions_topic` WRITE;
/*!40000 ALTER TABLE `discussions_topic` DISABLE KEYS */;
/*!40000 ALTER TABLE `discussions_topic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discussions_topicthread`
--

DROP TABLE IF EXISTS `discussions_topicthread`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `discussions_topicthread` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `created` datetime NOT NULL,
  `author_id` int(11) DEFAULT NULL,
  `nickname` varchar(50) COLLATE utf8_czech_ci NOT NULL,
  `email` varchar(75) COLLATE utf8_czech_ci NOT NULL,
  `topic_id` int(11) NOT NULL,
  `hit_counts` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `discussions_topicthread_slug` (`slug`),
  KEY `discussions_topicthread_author_id` (`author_id`),
  KEY `discussions_topicthread_topic_id` (`topic_id`),
  CONSTRAINT `author_id_refs_id_64cb7dc` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `topic_id_refs_id_3865f783` FOREIGN KEY (`topic_id`) REFERENCES `discussions_topic` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discussions_topicthread`
--

LOCK TABLES `discussions_topicthread` WRITE;
/*!40000 ALTER TABLE `discussions_topicthread` DISABLE KEYS */;
/*!40000 ALTER TABLE `discussions_topicthread` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8 COLLATE=utf8_czech_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'message','auth','message'),(5,'content type','contenttypes','contenttype'),(6,'session','sessions','session'),(7,'site','sites','site'),(8,'redirect','redirects','redirect'),(9,'Author','core','author'),(10,'Source','core','source'),(11,'Category','core','category'),(12,'Placement','core','placement'),(13,'Listing','core','listing'),(14,'Hit Count','core','hitcount'),(15,'Related','core','related'),(16,'Info box','articles','infobox'),(17,'Article','articles','article'),(18,'Article content','articles','articlecontents'),(19,'Comment Options','comments','commentoptions'),(20,'Comment','comments','comment'),(21,'Banned User','comments','banneduser'),(22,'banned ip','comments','bannedip'),(23,'Photo','photos','photo'),(24,'Format','photos','format'),(25,'Formated photo','photos','formatedphoto'),(26,'Template','db_templates','dbtemplate'),(27,'Template block','db_templates','templateblock'),(28,'Gallery','galleries','gallery'),(29,'Gallery item','galleries','galleryitem'),(30,'Contest','polls','contest'),(31,'Quiz','polls','quiz'),(32,'Question','polls','question'),(33,'Poll','polls','poll'),(34,'Choice','polls','choice'),(35,'Vote','polls','vote'),(36,'Contestant','polls','contestant'),(37,'Result','polls','result'),(38,'tag','tagging','tag'),(39,'tagged item','tagging','taggeditem'),(40,'Model weight','ratings','modelweight'),(41,'Total rate','ratings','totalrate'),(42,'Aggregation','ratings','agg'),(43,'Rating','ratings','rating'),(44,'atlas export','exports','atlasexport'),(45,'Server','imports','server'),(46,'Server item','imports','serveritem'),(47,'Topic','discussions','topic'),(48,'post viewed','discussions','postviewed'),(49,'Thread','discussions','topicthread'),(50,'banned string','discussions','bannedstring'),(51,'banned user','discussions','banneduser'),(52,'Interviewee','interviews','interviewee'),(53,'Interview','interviews','interview'),(54,'Question','interviews','question'),(55,'Answer','interviews','answer'),(56,'position','positions','position'),(57,'Category Lock','catlocks','categorylock'),(58,'mail','sendmail','mail'),(59,'log entry','admin','logentry'),(60,'Type','attachments','type'),(61,'Attachment','attachments','attachment'),(62,'question','answers','question'),(63,'answer','answers','answer'),(64,'question group','answers','questiongroup'),(65,'Serie','series','serie'),(66,'Serie part','series','seriepart'),(67,'Media','media','media'),(68,'section','media','section'),(69,'usage','media','usage'),(70,'Instruction','instruction','instruction'),(71,'Cooking type','recipes','cookingtype'),(72,'Cuisine','recipes','cuisine'),(73,'Nutrient group','recipes','nutrientgroup'),(74,'Nutrient','recipes','nutrient'),(75,'Unit','recipes','unit'),(76,'Unit conversion','recipes','unitconversion'),(77,'Ingredient group','recipes','ingredientgroup'),(78,'Ingredient','recipes','ingredient'),(79,'Nutrient in ingredient','recipes','nutrientiningredient'),(80,'Category photo','recipes','recipecategoryphoto'),(81,'Side-dish','recipes','sidedish'),(82,'Recipe','recipes','recipe'),(83,'Ingredient in recipe','recipes','ingredientinrecipe'),(84,'Recipe of day','recipes','recipeofday'),(85,'old recipe article redirect','recipes','oldrecipearticleredirect'),(86,'old recipe category redirect','recipes','oldrecipecategoryredirect'),(87,'Horoscope','astrology','horoscope'),(88,'Sign','astrology','sign'),(89,'Sign description type','astrology','signdescriptiontype'),(90,'Sign description','astrology','signdescription'),(91,'Birth period','astrology','birthperiod'),(92,'Sign compatibility','astrology','signcompatibility'),(93,'Prognosis duration','astrology','prognosisduration'),(94,'Prognosis type','astrology','prognosistype'),(95,'Prognosis','astrology','prognosis'),(96,'Lunar diary category','astrology','lunardiarycategory'),(97,'Lunar diary','astrology','lunardiary'),(98,'Lexicon term','astrology','astrolex'),(99,'Life number','astrology','lifenumber'),(100,'Stone','astrology','stone'),(101,'Stone for Sign','astrology','stoneforsign'),(102,'Numerology grid number','astrology','numerologygrid'),(103,'Moon in Sign','astrology','moon'),(104,'newsletter','newsletters','newsletter'),(105,'recipient','newsletters','recipient'),(106,'format','cdnclient','format'),(107,'source','cdnclient','source'),(108,'target','cdnclient','target'),(109,'Contact form recipient','contact_form','recipient'),(110,'Contact form message','contact_form','message'),(111,'Eshop','xmastips','eshop'),(112,'Feedset','xmastips','feedset'),(113,'Category','xmastips','category'),(114,'Target group','xmastips','targetgroup'),(115,'Present','xmastips','present'),(116,'Inquiry of Santa','writetosanta','inquiryofsanta'),(117,'Category - section mapping','adverts','categorysectionmapping'),(118,'Site - server mapping','adverts','siteservermapping');
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
  `created` datetime NOT NULL,
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
  UNIQUE KEY `gallery_id` (`gallery_id`,`order`),
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
  `priority` int(11) NOT NULL,
  `slug` varchar(255) COLLATE utf8_czech_ci NOT NULL,
  `link` varchar(400) COLLATE utf8_czech_ci NOT NULL,
  `photo_url` varchar(400) COLLATE utf8_czech_ci NOT NULL,
  `photo_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `server_id` (`server_id`,`slug`),
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
  `created` datetime NOT NULL,
  `updated` datetime DEFAULT NULL,
  `embed_invisible` tinyint(1) NOT NULL,
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
  UNIQUE KEY `instruction_id` (`instruction_id`,`author_id`),
  KEY `author_id_refs_id_cc614fa` (`author_id`),
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
  `submit_date` datetime NOT NULL,
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
  UNIQUE KEY `interview_id` (`interview_id`,`author_id`),
  KEY `author_id_refs_id_77adebcc` (`author_id`),
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
  UNIQUE KEY `interview_id` (`interview_id`,`interviewee_id`),
  KEY `interviewee_id_refs_id_7951e1bf` (`interviewee_id`),
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
  `submit_date` datetime NOT NULL,
  `is_public` tinyint(1) NOT NULL,
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
  `created` datetime NOT NULL,
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
  UNIQUE KEY `media_id` (`media_id`,`author_id`),
  KEY `author_id_refs_id_5a42ef96` (`author_id`),
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
  `flexible_height` tinyint(1) NOT NULL,
  `flexible_max_height` int(10) unsigned DEFAULT NULL,
  `stretch` tinyint(1) NOT NULL,
  `nocrop` tinyint(1) NOT NULL,
  `resample_quality` int(11) NOT NULL,
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
  UNIQUE KEY `photo_id` (`photo_id`,`format_id`),
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
  `created` datetime NOT NULL,
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
  UNIQUE KEY `photo_id` (`photo_id`,`author_id`),
  KEY `author_id_refs_id_2e5fa14a` (`author_id`),
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
  `winner` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `contest_id` (`contest_id`,`email`),
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
  `allow_multiple` tinyint(1) NOT NULL,
  `allow_no_choice` tinyint(1) NOT NULL,
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
  `has_correct_answers` tinyint(1) NOT NULL,
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
  UNIQUE KEY `quiz_id` (`quiz_id`,`author_id`),
  KEY `author_id_refs_id_2a34fb20` (`author_id`),
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
  `disabled` tinyint(1) NOT NULL,
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
  `detract` int(11) NOT NULL,
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
  `weight` int(11) NOT NULL,
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
  `time` datetime NOT NULL,
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
  `order` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `recipe_id` (`recipe_id`,`ingredient_id`),
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
  UNIQUE KEY `ingredient_id` (`ingredient_id`,`nutrient_id`),
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
  `price` smallint(6) NOT NULL,
  `difficulty` smallint(5) unsigned NOT NULL,
  `preparation_time` smallint(5) unsigned NOT NULL,
  `caloric_value` int(10) unsigned DEFAULT NULL,
  `headline` longtext COLLATE utf8_czech_ci NOT NULL,
  `preparation` longtext COLLATE utf8_czech_ci NOT NULL,
  `approved` tinyint(1) NOT NULL,
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
  UNIQUE KEY `recipe_id` (`recipe_id`,`author_id`),
  KEY `author_id_refs_id_315969b8` (`author_id`),
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
  UNIQUE KEY `recipe_id` (`recipe_id`,`cuisine_id`),
  KEY `cuisine_id_refs_id_1f3d8bfb` (`cuisine_id`),
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
  UNIQUE KEY `recipe_id` (`recipe_id`,`sidedish_id`),
  KEY `sidedish_id_refs_id_3c9c54e1` (`sidedish_id`),
  CONSTRAINT `sidedish_id_refs_id_3c9c54e1` FOREIGN KEY (`sidedish_id`) REFERENCES `recipes_sidedish` (`id`),
  CONSTRAINT `recipe_id_refs_id_859070e` FOREIGN KEY (`recipe_id`) REFERENCES `recipes_recipe` (`id`)
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
  UNIQUE KEY `from_unit_id` (`from_unit_id`,`to_unit_id`),
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
  `sent` datetime NOT NULL,
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
  `hide_newer_parts` tinyint(1) NOT NULL,
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
  `part_no` smallint(5) unsigned NOT NULL,
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
  UNIQUE KEY `tag_id` (`tag_id`,`content_type_id`,`object_id`,`priority`),
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

-- Dump completed on 2009-05-19 13:11:11
