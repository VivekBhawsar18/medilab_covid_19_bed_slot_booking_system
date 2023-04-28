-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 18, 2023 at 03:31 PM
-- Server version: 8.0.31
-- PHP Version: 8.0.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `covid`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
CREATE TABLE IF NOT EXISTS `admin` (
  `UID` int NOT NULL AUTO_INCREMENT,
  `EMAIL` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `PASSWORD` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL,
  `IS_ACTIVE` tinyint(1) DEFAULT NULL,
  `CREATED_AT` datetime DEFAULT NULL,
  `ROLE` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`UID`),
  UNIQUE KEY `EMAIL` (`EMAIL`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`UID`, `EMAIL`, `PASSWORD`, `IS_ACTIVE`, `CREATED_AT`, `ROLE`) VALUES
(1, 'testadmin01@gmail.com', 'medilabadmin01', 1, '2023-04-18 21:00:00', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `credentials`
--

DROP TABLE IF EXISTS `credentials`;
CREATE TABLE IF NOT EXISTS `credentials` (
  `CID` int NOT NULL AUTO_INCREMENT,
  `UID` int DEFAULT NULL,
  `PASSWORD` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`CID`),
  KEY `UID` (`UID`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hospital`
--

DROP TABLE IF EXISTS `hospital`;
CREATE TABLE IF NOT EXISTS `hospital` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `HCODE` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `HOSPITAL_NAME` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ICU_BEDS` int NOT NULL,
  `NORMAL_BEDS` int NOT NULL,
  `VENTILATOR_BEDS` int NOT NULL,
  `HIGH_CARE_UNIT_BEDS` int NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `HCODE` (`HCODE`)
) ;

-- --------------------------------------------------------

--
-- Table structure for table `hospital_user`
--

DROP TABLE IF EXISTS `hospital_user`;
CREATE TABLE IF NOT EXISTS `hospital_user` (
  `HCODE` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `EMAIL` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `PASSWORD_HASH` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL,
  `IS_ACTIVE` tinyint(1) DEFAULT NULL,
  `CREATED_AT` datetime DEFAULT NULL,
  `ROLE` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`HCODE`),
  UNIQUE KEY `EMAIL` (`EMAIL`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `test`
--

DROP TABLE IF EXISTS `test`;
CREATE TABLE IF NOT EXISTS `test` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fname` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `lname` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `UID` int NOT NULL AUTO_INCREMENT,
  `EMAIL` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `IS_ACTIVE` tinyint(1) DEFAULT NULL,
  `CREATED_AT` datetime DEFAULT NULL,
  `LOGIN_METHOD` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `ROLE` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`UID`),
  UNIQUE KEY `EMAIL` (`EMAIL`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `userbookings`
--

DROP TABLE IF EXISTS `userbookings`;
CREATE TABLE IF NOT EXISTS `userbookings` (
  `BID` int NOT NULL AUTO_INCREMENT,
  `UID` int DEFAULT NULL,
  `HCODE` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `HOSPITAL_NAME` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `BED_TYPE` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `OXYGEN_LEVEL` int DEFAULT NULL,
  `PATIENT_NAME` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `PATIENT_CONTACT` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`BID`),
  UNIQUE KEY `PATIENT_CONTACT` (`PATIENT_CONTACT`),
  KEY `UID` (`UID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `userdata`
--

DROP TABLE IF EXISTS `userdata`;
CREATE TABLE IF NOT EXISTS `userdata` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `UID` int DEFAULT NULL,
  `USER_NAME` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `CONTACT` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `GENDER` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ADDRESS` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `CONTACT` (`CONTACT`),
  KEY `UID` (`UID`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
