-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: database
-- Generation Time: Mar 28, 2019 at 02:01 PM
-- Server version: 5.7.25
-- PHP Version: 7.2.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `icu_database`
--

-- --------------------------------------------------------

--
-- Table structure for table `patients`
--

CREATE TABLE `patients` (
  `id` int(11) NOT NULL,
  `first_name` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_of_birth` date NOT NULL,
  `age` tinyint(6) NOT NULL,
  `datetime_of_admission` datetime NOT NULL,
  `datetime_of_discharge` datetime DEFAULT NULL,
  `bed` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `patient_signal_values`
--

CREATE TABLE `patient_signal_values` (
  `id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `signal_id` int(11) NOT NULL,
  `time` datetime NOT NULL,
  `value` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT;

-- --------------------------------------------------------

--
-- Table structure for table `signals`
--

CREATE TABLE `signals` (
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `population_mean` float NOT NULL,
  `population_std` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `signals`
--

INSERT INTO `signals` (`id`, `name`, `population_mean`, `population_std`) VALUES
(1, 'blood_pressure', 64.59, 7.91),
(2, 'respiration_rate', 21.38, 4.54),
(3, 'temperature', 37.11, 0.32);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `patients`
--
ALTER TABLE `patients`
  ADD PRIMARY KEY (`id`),
  ADD KEY `datetime_of_admission` (`datetime_of_admission`),
  ADD KEY `datetime_of_discharge` (`datetime_of_discharge`);

--
-- Indexes for table `patient_signal_values`
--
ALTER TABLE `patient_signal_values`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `patient_id_2` (`patient_id`,`signal_id`,`time`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `signal_id` (`signal_id`),
  ADD KEY `time` (`time`);

--
-- Indexes for table `signals`
--
ALTER TABLE `signals`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `patients`
--
ALTER TABLE `patients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `signals`
--
ALTER TABLE `signals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
