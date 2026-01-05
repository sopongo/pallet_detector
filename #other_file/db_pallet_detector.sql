-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Dec 30, 2025 at 10:11 AM
-- Server version: 8.0.30
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_pallet_detector`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_image`
--

CREATE TABLE `tb_image` (
  `id_img` int NOT NULL COMMENT 'เก็บไอดีรูป',
  `image_date` datetime NOT NULL COMMENT 'เก็บวันเวลาที่ถ่ายรูป',
  `image_name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'ชื่อไฟล์ภาพ (เช่น IMG_20251231_1223.jpg)',
  `pallet_detected` int DEFAULT '0' COMMENT 'จำนวนพาเลทที่พบในรูป',
  `site` int DEFAULT NULL COMMENT 'ไซด์/สาขา',
  `location` int DEFAULT NULL COMMENT 'อาคาร/โซน'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ตารางเก็บประวัติการถ่ายภาพประจำรอบ';

-- --------------------------------------------------------

--
-- Table structure for table `tb_pallet`
--

CREATE TABLE `tb_pallet` (
  `id_pallet` int NOT NULL COMMENT 'เก็บไอดีพาเลท',
  `pallet_no` int DEFAULT NULL COMMENT 'เก็บลำดับพาเลทในรูปนั้นของวันนั้นๆ',
  `pallet_name` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'เก็บชื่อพาเลทในรูปนั้น (อาจจะไม่ต้องใช้)',
  `ref_id_img` int NOT NULL COMMENT 'เชื่อมโยงไอดีรูปจาก tb_image',
  `pos_x` decimal(10,4) NOT NULL COMMENT 'เลขตำแหน่งอิงจาก X ของรูป',
  `post_y` decimal(10,4) NOT NULL COMMENT 'เลขตำแหน่งอิงจาก Y ของรูป',
  `in_over` int DEFAULT '0' COMMENT 'เก็บสถานะระยะเวลางวาง 0-ไม่เกิน, 1-เกินเวลา',
  `accuracy` double DEFAULT '0' COMMENT 'ค่า % ความแม่นยำจาก AI',
  `first_detected_at` datetime DEFAULT NULL COMMENT 'เวลาที่พบครั้งแรก (เช่น 10:10:00)',
  `last_detected_at` datetime DEFAULT NULL COMMENT 'เวลาล่าสุดที่เจอ (อัปเดตทุกครั้งที่เจอในตำแหน่งเดิม)',
  `over_time` datetime DEFAULT NULL COMMENT 'เวลาที่เกินกำหนด (ที่พบว่าเริ่มเกิน)',
  `notify_count` int DEFAULT '0' COMMENT 'จำนวนครั้งที่แจ้งเตือน',
  `detector_count` int DEFAULT '1' COMMENT 'จำนวนครั้งที่ตรวจพบซ้ำที่เดิม',
  `is_active` int DEFAULT '1' COMMENT 'สถานะปัจจุบัน: 1-ยังวางอยู่, 0-ไม่เจอที่เดิมแล้ว',
  `status` int DEFAULT '0' COMMENT '0-Normal / 1-Overtime / 2-Moved (ยกออกแล้ว)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ตารางเก็บสถานะและการติดตามพาเลทรายชิ้น';

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_image`
--
ALTER TABLE `tb_image`
  ADD PRIMARY KEY (`id_img`);

--
-- Indexes for table `tb_pallet`
--
ALTER TABLE `tb_pallet`
  ADD PRIMARY KEY (`id_pallet`),
  ADD KEY `fk_ref_id_img` (`ref_id_img`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_image`
--
ALTER TABLE `tb_image`
  MODIFY `id_img` int NOT NULL AUTO_INCREMENT COMMENT 'เก็บไอดีรูป';

--
-- AUTO_INCREMENT for table `tb_pallet`
--
ALTER TABLE `tb_pallet`
  MODIFY `id_pallet` int NOT NULL AUTO_INCREMENT COMMENT 'เก็บไอดีพาเลท';

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tb_pallet`
--
ALTER TABLE `tb_pallet`
  ADD CONSTRAINT `fk_pallet_image` FOREIGN KEY (`ref_id_img`) REFERENCES `tb_image` (`id_img`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
