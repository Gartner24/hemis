-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema hemis_db
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema hemis_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `hemis_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `hemis_db` ;

-- -----------------------------------------------------
-- Table `hemis_db`.`identification_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`identification_type` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(10) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `code_UNIQUE` ON `hemis_db`.`identification_type` (`code` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`insurer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`insurer` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(120) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `name_UNIQUE` ON `hemis_db`.`insurer` (`name` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`patient`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`patient` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `identification_type_id` INT UNSIGNED NOT NULL,
  `ident_number` VARCHAR(30) NOT NULL,
  `full_name` VARCHAR(150) NOT NULL,
  `birth_date` DATE NOT NULL,
  `sex` ENUM('M', 'F', 'X') NOT NULL,
  `phone` VARCHAR(30) NULL,
  `email` VARCHAR(120) NULL,
  `allergies` TEXT NULL,
  `emergency_contact` VARCHAR(150) NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_patient_identification_type`
    FOREIGN KEY (`identification_type_id`)
    REFERENCES `hemis_db`.`identification_type` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_patient_identification_type_idx` ON `hemis_db`.`patient` (`identification_type_id` ASC) VISIBLE;

CREATE UNIQUE INDEX `uq_patient_identification_type_ident_number` ON `hemis_db`.`patient` (`identification_type_id` ASC, `ident_number` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`patient_insurer`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`patient_insurer` (
  `patient_id` INT UNSIGNED NOT NULL,
  `insurer_id` INT UNSIGNED NOT NULL,
  `policy_number` VARCHAR(40) NOT NULL,
  `valid_from` DATE NOT NULL,
  `valid_to` DATE NOT NULL,
  PRIMARY KEY (`patient_id`, `insurer_id`),
  CONSTRAINT `fk_patient_insurer_patient`
    FOREIGN KEY (`patient_id`)
    REFERENCES `hemis_db`.`patient` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_patient_insurer_insurer`
    FOREIGN KEY (`insurer_id`)
    REFERENCES `hemis_db`.`insurer` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_patient_insurer_patient_idx` ON `hemis_db`.`patient_insurer` (`patient_id` ASC) VISIBLE;

CREATE INDEX `idx_patient_insurer_insurer` ON `hemis_db`.`patient_insurer` (`insurer_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`role`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`role` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `name_UNIQUE` ON `hemis_db`.`role` (`name` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`user` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(150) NOT NULL,
  `full_name` VARCHAR(150) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `email_UNIQUE` ON `hemis_db`.`user` (`email` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`user_role`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`user_role` (
  `user_id` INT UNSIGNED NOT NULL,
  `role_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`user_id`, `role_id`),
  CONSTRAINT `fk_user_role_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `hemis_db`.`user` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_role_role`
    FOREIGN KEY (`role_id`)
    REFERENCES `hemis_db`.`role` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_user_role_role_idx` ON `hemis_db`.`user_role` (`role_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`specialty`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`specialty` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `uq_specialty_name` ON `hemis_db`.`specialty` (`name` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`doctor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`doctor` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `license_number` VARCHAR(40) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_doctor_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `hemis_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `user_id_UNIQUE` ON `hemis_db`.`doctor` (`user_id` ASC) VISIBLE;

CREATE UNIQUE INDEX `license_number_UNIQUE` ON `hemis_db`.`doctor` (`license_number` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`doctor_specialty`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`doctor_specialty` (
  `doctor_id` INT UNSIGNED NOT NULL,
  `specialty_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`doctor_id`, `specialty_id`),
  CONSTRAINT `fk_doctor_specialty_doctor`
    FOREIGN KEY (`doctor_id`)
    REFERENCES `hemis_db`.`doctor` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_doctor_specialty_specialty`
    FOREIGN KEY (`specialty_id`)
    REFERENCES `hemis_db`.`specialty` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_doctor_specialty_specialty_idx` ON `hemis_db`.`doctor_specialty` (`specialty_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`doctor_schedule`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`doctor_schedule` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `doctor_id` INT UNSIGNED NOT NULL,
  `weekday` TINYINT UNSIGNED NOT NULL,
  `start_time` TIME NOT NULL,
  `end_time` TIME NOT NULL,
  `slot_minutes` SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_doctor_schedule_doctor`
    FOREIGN KEY (`doctor_id`)
    REFERENCES `hemis_db`.`doctor` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_doctor_schedule_doctor_idx` ON `hemis_db`.`doctor_schedule` (`doctor_id` ASC) VISIBLE;

CREATE INDEX `idx_doctor_schedule_doctor_wd_start` ON `hemis_db`.`doctor_schedule` (`doctor_id` ASC, `weekday` ASC, `start_time` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`doctor_absence`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`doctor_absence` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `doctor_id` INT UNSIGNED NOT NULL,
  `start_at` DATETIME NOT NULL,
  `end_at` DATETIME NOT NULL,
  `reason` VARCHAR(200) NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_doctor_absence_doctor`
    FOREIGN KEY (`doctor_id`)
    REFERENCES `hemis_db`.`doctor` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_doctor_absence_doctor_idx` ON `hemis_db`.`doctor_absence` (`doctor_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`room`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`room` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(30) NOT NULL,
  `capacity` SMALLINT UNSIGNED NOT NULL,
  `type` VARCHAR(50) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `code_UNIQUE` ON `hemis_db`.`room` (`code` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`equipment_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`equipment_type` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(80) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `name_UNIQUE` ON `hemis_db`.`equipment_type` (`name` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`equipment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`equipment` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `equipment_type_id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_equipment_equipment_type`
    FOREIGN KEY (`equipment_type_id`)
    REFERENCES `hemis_db`.`equipment_type` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_equipment_equipment_type_idx` ON `hemis_db`.`equipment` (`equipment_type_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`room_equipment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`room_equipment` (
  `room_id` INT UNSIGNED NOT NULL,
  `equipment_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`room_id`, `equipment_id`),
  CONSTRAINT `fk_room_equipment_room`
    FOREIGN KEY (`room_id`)
    REFERENCES `hemis_db`.`room` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_room_equipment_equipment`
    FOREIGN KEY (`equipment_id`)
    REFERENCES `hemis_db`.`equipment` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_room_equipment_equipment_idx` ON `hemis_db`.`room_equipment` (`equipment_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`appointment_status`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`appointment_status` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(10) NOT NULL,
  `name` VARCHAR(50) NOT NULL,
  `flow_order` TINYINT UNSIGNED NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `code_UNIQUE` ON `hemis_db`.`appointment_status` (`code` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`appointment_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`appointment_type` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(60) NOT NULL,
  `requires_equipment` TINYINT(1) UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `uq_appointment_type_name` ON `hemis_db`.`appointment_type` (`name` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`triage_priority`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`triage_priority` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(40) NOT NULL,
  `level` TINYINT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `name_UNIQUE` ON `hemis_db`.`triage_priority` (`name` ASC) VISIBLE;

CREATE UNIQUE INDEX `uq_triage_priority_level` ON `hemis_db`.`triage_priority` (`level` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`appointment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`appointment` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `patient_id` INT UNSIGNED NOT NULL,
  `doctor_id` INT UNSIGNED NOT NULL,
  `specialty_id` INT UNSIGNED NOT NULL,
  `room_id` INT UNSIGNED NULL,
  `appointment_type_id` INT UNSIGNED NOT NULL,
  `triage_priority_id` INT UNSIGNED NOT NULL,
  `start_at` DATETIME NOT NULL,
  `end_at` DATETIME NOT NULL,
  `appointment_status_id` INT UNSIGNED NOT NULL,
  `reason` VARCHAR(255) NULL,
  `created_by` INT UNSIGNED NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_appointment_patient`
    FOREIGN KEY (`patient_id`)
    REFERENCES `hemis_db`.`patient` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_doctor`
    FOREIGN KEY (`doctor_id`)
    REFERENCES `hemis_db`.`doctor` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_specialty`
    FOREIGN KEY (`specialty_id`)
    REFERENCES `hemis_db`.`specialty` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_room`
    FOREIGN KEY (`room_id`)
    REFERENCES `hemis_db`.`room` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_appointment_type`
    FOREIGN KEY (`appointment_type_id`)
    REFERENCES `hemis_db`.`appointment_type` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_triage_priority`
    FOREIGN KEY (`triage_priority_id`)
    REFERENCES `hemis_db`.`triage_priority` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_appointment_status`
    FOREIGN KEY (`appointment_status_id`)
    REFERENCES `hemis_db`.`appointment_status` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_user`
    FOREIGN KEY (`created_by`)
    REFERENCES `hemis_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_appointment_doctor_idx` ON `hemis_db`.`appointment` (`doctor_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_specialty_idx` ON `hemis_db`.`appointment` (`specialty_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_room_idx` ON `hemis_db`.`appointment` (`room_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_appointment_type_idx` ON `hemis_db`.`appointment` (`appointment_type_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_triage_priority_idx` ON `hemis_db`.`appointment` (`triage_priority_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_appointment_status_idx` ON `hemis_db`.`appointment` (`appointment_status_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_user_idx` ON `hemis_db`.`appointment` (`created_by` ASC) VISIBLE;

CREATE INDEX `idx_appointment_patient_start` ON `hemis_db`.`appointment` (`patient_id` ASC, `start_at` ASC) VISIBLE;

CREATE INDEX `idx_appointment_doctor_start` ON `hemis_db`.`appointment` (`doctor_id` ASC, `start_at` ASC) VISIBLE;

CREATE INDEX `idx_appointment_room_start` ON `hemis_db`.`appointment` (`room_id` ASC, `start_at` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`appointment_status_history`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`appointment_status_history` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `appointment_id` INT UNSIGNED NOT NULL,
  `old_status_id` INT UNSIGNED NULL,
  `new_status_id` INT UNSIGNED NOT NULL,
  `changed_by` INT UNSIGNED NOT NULL,
  `changed_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_appointment_status_history_appointment`
    FOREIGN KEY (`appointment_id`)
    REFERENCES `hemis_db`.`appointment` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_status_history_old_status`
    FOREIGN KEY (`old_status_id`)
    REFERENCES `hemis_db`.`appointment_status` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_status_history_new_status`
    FOREIGN KEY (`new_status_id`)
    REFERENCES `hemis_db`.`appointment_status` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_status_history_user`
    FOREIGN KEY (`changed_by`)
    REFERENCES `hemis_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_appointment_status_history_appointment_idx` ON `hemis_db`.`appointment_status_history` (`appointment_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_status_history_old_status_idx` ON `hemis_db`.`appointment_status_history` (`old_status_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_status_history_new_status_idx` ON `hemis_db`.`appointment_status_history` (`new_status_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_status_history_user_idx` ON `hemis_db`.`appointment_status_history` (`changed_by` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`appointment_equipment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`appointment_equipment` (
  `appointment_id` INT UNSIGNED NOT NULL,
  `equipment_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`appointment_id`, `equipment_id`),
  CONSTRAINT `fk_appointment_equipment_appointment`
    FOREIGN KEY (`appointment_id`)
    REFERENCES `hemis_db`.`appointment` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_equipment_equipment`
    FOREIGN KEY (`equipment_id`)
    REFERENCES `hemis_db`.`equipment` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `appointment_equipment_equipment_idx` ON `hemis_db`.`appointment_equipment` (`equipment_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`appointment_note`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`appointment_note` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `appointment_id` INT UNSIGNED NOT NULL,
  `author_id` INT UNSIGNED NOT NULL,
  `text` TEXT NOT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_appointment_note_appointment`
    FOREIGN KEY (`appointment_id`)
    REFERENCES `hemis_db`.`appointment` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_note_user`
    FOREIGN KEY (`author_id`)
    REFERENCES `hemis_db`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_appointment_note_appointment_idx` ON `hemis_db`.`appointment_note` (`appointment_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_note_user_idx` ON `hemis_db`.`appointment_note` (`author_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`diagnosis_icd10`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`diagnosis_icd10` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(10) NOT NULL,
  `name` VARCHAR(180) NOT NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `code_UNIQUE` ON `hemis_db`.`diagnosis_icd10` (`code` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`appointment_diagnosis`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`appointment_diagnosis` (
  `appointment_id` INT UNSIGNED NOT NULL,
  `diagnosis_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`appointment_id`, `diagnosis_id`),
  CONSTRAINT `fk_appointment_diagnosis_appointment`
    FOREIGN KEY (`appointment_id`)
    REFERENCES `hemis_db`.`appointment` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_diagnosis_diagnosis_icd10`
    FOREIGN KEY (`diagnosis_id`)
    REFERENCES `hemis_db`.`diagnosis_icd10` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_appointment_diagnosis_diagnosis_icd10_idx` ON `hemis_db`.`appointment_diagnosis` (`diagnosis_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`prescription`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`prescription` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `appointment_id` INT UNSIGNED NOT NULL,
  `text` TEXT NOT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_prescription_appointment`
    FOREIGN KEY (`appointment_id`)
    REFERENCES `hemis_db`.`appointment` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_prescription_appointment_idx` ON `hemis_db`.`prescription` (`appointment_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`payment_status`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`payment_status` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(40) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `name_UNIQUE` ON `hemis_db`.`payment_status` (`name` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`appointment_invoice`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`appointment_invoice` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `appointment_id` INT UNSIGNED NOT NULL,
  `insurer_id` INT UNSIGNED NOT NULL,
  `copay_amount` DECIMAL(10,2) NOT NULL,
  `total_amount` DECIMAL(10,2) NOT NULL,
  `payment_status_id` INT UNSIGNED NOT NULL,
  `issued_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_appointment_invoice_appointment`
    FOREIGN KEY (`appointment_id`)
    REFERENCES `hemis_db`.`appointment` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_invoice_insurer`
    FOREIGN KEY (`insurer_id`)
    REFERENCES `hemis_db`.`insurer` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_appointment_invoice_payment_status`
    FOREIGN KEY (`payment_status_id`)
    REFERENCES `hemis_db`.`payment_status` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_appointment_invoice_insurer_idx` ON `hemis_db`.`appointment_invoice` (`insurer_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_invoice_appointment_idx` ON `hemis_db`.`appointment_invoice` (`appointment_id` ASC) VISIBLE;

CREATE UNIQUE INDEX `appointment_id_UNIQUE` ON `hemis_db`.`appointment_invoice` (`appointment_id` ASC) VISIBLE;

CREATE INDEX `fk_appointment_invoice_payment_status_idx` ON `hemis_db`.`appointment_invoice` (`payment_status_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`device`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`device` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `label` VARCHAR(40) NOT NULL,
  `patient_id` INT UNSIGNED NULL,
  `firmware` VARCHAR(40) NULL,
  `last_seen_at` DATETIME NULL,
  `active` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_device_patient`
    FOREIGN KEY (`patient_id`)
    REFERENCES `hemis_db`.`patient` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `label_UNIQUE` ON `hemis_db`.`device` (`label` ASC) VISIBLE;

CREATE INDEX `fk_device_patient_idx` ON `hemis_db`.`device` (`patient_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`metric`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`metric` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `code` VARCHAR(30) NOT NULL,
  `name` VARCHAR(60) NOT NULL,
  `unit` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `code_UNIQUE` ON `hemis_db`.`metric` (`code` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`reading`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`reading` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `device_id` INT UNSIGNED NOT NULL,
  `metric_id` INT UNSIGNED NOT NULL,
  `ts` DATETIME NOT NULL,
  `value` DECIMAL(7,2) NOT NULL,
  `quality_flag` VARCHAR(20) NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_reading_device`
    FOREIGN KEY (`device_id`)
    REFERENCES `hemis_db`.`device` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_reading_metric`
    FOREIGN KEY (`metric_id`)
    REFERENCES `hemis_db`.`metric` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `idx_reading_device_ts` ON `hemis_db`.`reading` (`device_id` ASC, `ts` ASC) VISIBLE;

CREATE INDEX `idx_reading_metric_ts` ON `hemis_db`.`reading` (`metric_id` ASC, `ts` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`rule`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`rule` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `metric_id` INT UNSIGNED NOT NULL,
  `rule_type` ENUM('threshold', 'trend') NOT NULL,
  `operator` ENUM('>', '<', '>=', '<=') NOT NULL,
  `threshold_value` DECIMAL(7,2) NOT NULL,
  `window_min` SMALLINT UNSIGNED NOT NULL,
  `severity` ENUM('High', 'Medium', 'Low') NOT NULL,
  `enabled` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `name` VARCHAR(80) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_rule_metric`
    FOREIGN KEY (`metric_id`)
    REFERENCES `hemis_db`.`metric` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `name_UNIQUE` ON `hemis_db`.`rule` (`name` ASC) VISIBLE;

CREATE INDEX `fk_rule_metric_idx` ON `hemis_db`.`rule` (`metric_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`rule_assignment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`rule_assignment` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `rule_id` INT UNSIGNED NOT NULL,
  `patient_id` INT UNSIGNED NULL,
  `device_id` INT UNSIGNED NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_rule_assignment_rule`
    FOREIGN KEY (`rule_id`)
    REFERENCES `hemis_db`.`rule` (`id`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_rule_assignment_patient`
    FOREIGN KEY (`patient_id`)
    REFERENCES `hemis_db`.`patient` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_rule_assignment_device`
    FOREIGN KEY (`device_id`)
    REFERENCES `hemis_db`.`device` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_rule_assignment_rule_idx` ON `hemis_db`.`rule_assignment` (`rule_id` ASC) VISIBLE;

CREATE INDEX `fk_rule_assignment_patient_idx` ON `hemis_db`.`rule_assignment` (`patient_id` ASC) VISIBLE;

CREATE INDEX `fk_rule_assignment_device_idx` ON `hemis_db`.`rule_assignment` (`device_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `hemis_db`.`incident`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hemis_db`.`incident` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `rule_id` INT UNSIGNED NOT NULL,
  `patient_id` INT UNSIGNED NULL,
  `device_id` INT UNSIGNED NULL,
  `metric` VARCHAR(30) NOT NULL,
  `severity` ENUM('High', 'Medium', 'Low') NOT NULL,
  `status` ENUM('open', 'in_progress', 'resolved') NOT NULL,
  `opened_at` DATETIME NOT NULL,
  `closed_at` DATETIME NULL,
  `details` TEXT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_incident_rule`
    FOREIGN KEY (`rule_id`)
    REFERENCES `hemis_db`.`rule` (`id`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_incident_patient`
    FOREIGN KEY (`patient_id`)
    REFERENCES `hemis_db`.`patient` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_incident_device`
    FOREIGN KEY (`device_id`)
    REFERENCES `hemis_db`.`device` (`id`)
    ON DELETE SET NULL
    ON UPDATE RESTRICT)
ENGINE = InnoDB;

CREATE INDEX `fk_incident_rule_idx` ON `hemis_db`.`incident` (`rule_id` ASC) VISIBLE;

CREATE INDEX `fk_incident_patient_idx` ON `hemis_db`.`incident` (`patient_id` ASC) VISIBLE;

CREATE INDEX `fk_incident_device_idx` ON `hemis_db`.`incident` (`device_id` ASC) VISIBLE;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
