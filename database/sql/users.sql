-- =====================================================
-- HEMIS Database Users and Permissions
-- =====================================================
-- 
-- This file contains MySQL user creation and permission management
-- for the HEMIS (Hospital Electronic Medical Information System) database.
-- 
-- USER ROLES AND PERMISSIONS:
-- ===========================
-- 1. super_admin    - Super Administrator (full access to all tables)
-- 2. admin_hr       - HR Administrator (user/doctor management)
-- 3. admin_medical  - Medical Administrator (medical operations)
-- 4. admin_finance  - Finance Administrator (billing and payments)
-- 5. admin_system   - System Administrator (technical configuration)
-- 6. doctor         - Doctor (patient care and medical records)
-- 7. nurse          - Nurse (medical support and patient care)
-- 8. reception      - Reception (patient management and scheduling)
-- 9. coordinator    - Medical Coordinator (scheduling and coordination)
-- =====================================================

-- -----------------------------------------------------
--  Super Administrator
-- -----------------------------------------------------
CREATE USER 'super_admin' IDENTIFIED BY 'sHjsbheV34^qhtd&';
GRANT DELETE, SELECT, INSERT, UPDATE ON TABLE hemis_db.* TO 'super_admin';

-- -----------------------------------------------------
--  HR Administrator
-- -----------------------------------------------------
CREATE USER 'admin_hr' IDENTIFIED BY 'sHjsbheV34^qhtd&';

-- Core data access
GRANT SELECT ON TABLE `hemis_db`.`identification_type` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`insurer` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`patient` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`patient_insurer` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`role` TO 'admin_hr';

-- User and role management (primary responsibility)
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE `hemis_db`.`user` TO 'admin_hr';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`user_role` TO 'admin_hr';

-- Doctor management
GRANT SELECT, INSERT, DELETE, UPDATE ON TABLE `hemis_db`.`doctor` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`doctor_specialty` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`doctor_schedule` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`doctor_absence` TO 'admin_hr';

-- Facility and equipment access
GRANT SELECT ON TABLE `hemis_db`.`room` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`equipment_type` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`equipment` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`room_equipment` TO 'admin_hr';

-- Appointment and medical data (read-only)
GRANT SELECT ON TABLE `hemis_db`.`appointment_status` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`appointment_type` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`triage_priority` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`appointment` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`appointment_status_history` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`appointment_equipment` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`appointment_note` TO 'admin_hr';
GRANT SELECT ON TABLE `hemis_db`.`diagnosis_icd10` TO 'admin_hr';

-- -----------------------------------------------------
--  Medical Administrator
-- -----------------------------------------------------
CREATE USER 'admin_medical' IDENTIFIED BY 'sHjsbheV34^qhtd&';

-- Core data access
GRANT SELECT ON TABLE `hemis_db`.`identification_type` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`insurer` TO 'admin_medical';
GRANT UPDATE, SELECT ON TABLE `hemis_db`.`patient` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`patient_insurer` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`role` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`user` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`user_role` TO 'admin_medical';

-- Medical operations management
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE `hemis_db`.`specialty` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`doctor` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`doctor_specialty` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`doctor_schedule` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`doctor_absence` TO 'admin_medical';

-- Facility access (read-only)
GRANT SELECT ON TABLE `hemis_db`.`room` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`equipment_type` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`equipment` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`room_equipment` TO 'admin_medical';

-- Appointment and medical data management
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment_status` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment_type` TO 'admin_medical';
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE `hemis_db`.`triage_priority` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`appointment_status_history` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`appointment_equipment` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment_note` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`diagnosis_icd10` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment_diagnosis` TO 'admin_medical';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`prescription` TO 'admin_medical';

-- Financial data (read-only)
GRANT SELECT ON TABLE `hemis_db`.`payment_status` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`appointment_invoice` TO 'admin_medical';

-- Monitoring and incidents (read-only)
GRANT SELECT ON TABLE `hemis_db`.`device` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`metric` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`reading` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`rule` TO 'admin_medical';
GRANT SELECT ON TABLE `hemis_db`.`incident` TO 'admin_medical';

-- -----------------------------------------------------
--  Finance Administrator
-- -----------------------------------------------------
CREATE USER 'admin_finance' IDENTIFIED BY 'sHjsbheV34^qhtd&';

-- Core data access
GRANT SELECT ON TABLE `hemis_db`.`identification_type` TO 'admin_finance';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`insurer` TO 'admin_finance';
GRANT SELECT ON TABLE `hemis_db`.`patient` TO 'admin_finance';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`patient_insurer` TO 'admin_finance';

-- Medical staff data (read-only)
GRANT SELECT ON TABLE `hemis_db`.`doctor` TO 'admin_finance';

-- Appointment data (read-only)
GRANT SELECT ON TABLE `hemis_db`.`appointment_status` TO 'admin_finance';
GRANT SELECT ON TABLE `hemis_db`.`appointment` TO 'admin_finance';
GRANT SELECT ON TABLE `hemis_db`.`appointment_status_history` TO 'admin_finance';

-- Financial operations management
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`payment_status` TO 'admin_finance';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment_invoice` TO 'admin_finance';

-- -----------------------------------------------------
--  System Administrator
-- -----------------------------------------------------
CREATE USER 'admin_system' IDENTIFIED BY 'sHjsbheV34^qhtd&';

-- Core data management
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`identification_type` TO 'admin_system';
GRANT SELECT ON TABLE `hemis_db`.`patient` TO 'admin_system';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`role` TO 'admin_system';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`user` TO 'admin_system';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`user_role` TO 'admin_system';

-- Appointment data (read-only)
GRANT SELECT ON TABLE `hemis_db`.`appointment` TO 'admin_system';
GRANT SELECT ON TABLE `hemis_db`.`appointment_status_history` TO 'admin_system';

-- Technical infrastructure management
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`device` TO 'admin_system';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`metric` TO 'admin_system';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`reading` TO 'admin_system';
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE `hemis_db`.`rule` TO 'admin_system';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`rule_assignment` TO 'admin_system';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`incident` TO 'admin_system';

-- -----------------------------------------------------
--  Doctor
-- -----------------------------------------------------
CREATE USER 'doctor' IDENTIFIED BY 'sHjsbheV34^qhtd&';

-- Core data access
GRANT SELECT ON TABLE `hemis_db`.`identification_type` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`insurer` TO 'doctor';
GRANT SELECT, UPDATE ON TABLE `hemis_db`.`patient` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`patient_insurer` TO 'doctor';

-- Medical operations
GRANT SELECT ON TABLE `hemis_db`.`specialty` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`doctor` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`doctor_specialty` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`doctor_schedule` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`doctor_absence` TO 'doctor';

-- Facility access
GRANT SELECT ON TABLE `hemis_db`.`room` TO 'doctor';

-- Appointment and medical data management
GRANT SELECT ON TABLE `hemis_db`.`appointment_status` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`appointment_type` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`triage_priority` TO 'doctor';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`appointment_status_history` TO 'doctor';
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE `hemis_db`.`appointment_note` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`diagnosis_icd10` TO 'doctor';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment_diagnosis` TO 'doctor';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`prescription` TO 'doctor';

-- Monitoring data (read-only)
GRANT SELECT ON TABLE `hemis_db`.`device` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`metric` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`reading` TO 'doctor';
GRANT SELECT ON TABLE `hemis_db`.`incident` TO 'doctor';

-- -----------------------------------------------------
--  Nurse
-- -----------------------------------------------------
CREATE USER 'nurse' IDENTIFIED BY 'sHjsbheV34^qhtd&';

-- Core data access
GRANT SELECT ON TABLE `hemis_db`.`identification_type` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`insurer` TO 'nurse';
GRANT SELECT, UPDATE ON TABLE `hemis_db`.`patient` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`patient_insurer` TO 'nurse';

-- Medical operations
GRANT SELECT ON TABLE `hemis_db`.`specialty` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`doctor` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`doctor_specialty` TO 'nurse';

-- Facility access
GRANT SELECT ON TABLE `hemis_db`.`room` TO 'nurse';

-- Appointment and medical data
GRANT SELECT ON TABLE `hemis_db`.`appointment_status` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`appointment_type` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`triage_priority` TO 'nurse';
GRANT UPDATE ON TABLE `hemis_db`.`appointment` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`appointment_status_history` TO 'nurse';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment_note` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`diagnosis_icd10` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`appointment_diagnosis` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`prescription` TO 'nurse';

-- Monitoring data (read-only)
GRANT SELECT ON TABLE `hemis_db`.`device` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`metric` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`reading` TO 'nurse';
GRANT SELECT ON TABLE `hemis_db`.`incident` TO 'nurse';

-- -----------------------------------------------------
--  Reception
-- -----------------------------------------------------
CREATE USER 'reception' IDENTIFIED BY 'sHjsbheV34^qhtd&';

-- Core data access
GRANT SELECT ON TABLE `hemis_db`.`identification_type` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`insurer` TO 'reception';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`patient` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`patient_insurer` TO 'reception';

-- Medical operations
GRANT SELECT ON TABLE `hemis_db`.`specialty` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`doctor` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`doctor_specialty` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`doctor_schedule` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`doctor_absence` TO 'reception';

-- Facility and equipment access
GRANT SELECT ON TABLE `hemis_db`.`room` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`equipment_type` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`equipment` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`room_equipment` TO 'reception';

-- Appointment management
GRANT SELECT ON TABLE `hemis_db`.`appointment_status` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`appointment_type` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`triage_priority` TO 'reception';
GRANT UPDATE, SELECT, DELETE, INSERT ON TABLE `hemis_db`.`appointment` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`appointment_status_history` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`appointment_equipment` TO 'reception';
GRANT SELECT ON TABLE `hemis_db`.`appointment_invoice` TO 'reception';

-- -----------------------------------------------------
--  Coordinator
-- -----------------------------------------------------
CREATE USER 'coordinator' IDENTIFIED BY 'sHjsbheV34^qhtd&';

-- Core data access
GRANT SELECT ON TABLE `hemis_db`.`identification_type` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`insurer` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`patient` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`patient_insurer` TO 'coordinator';

-- Medical operations
GRANT SELECT ON TABLE `hemis_db`.`specialty` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`doctor` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`doctor_specialty` TO 'coordinator';
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE `hemis_db`.`doctor_schedule` TO 'coordinator';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`doctor_absence` TO 'coordinator';

-- Facility and equipment management
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`room` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`equipment_type` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`equipment` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`room_equipment` TO 'coordinator';

-- Appointment and medical data
GRANT SELECT ON TABLE `hemis_db`.`appointment_status` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`appointment_type` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`triage_priority` TO 'coordinator';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`appointment_status_history` TO 'coordinator';
GRANT UPDATE, SELECT, INSERT, DELETE ON TABLE `hemis_db`.`appointment_equipment` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`appointment_note` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`diagnosis_icd10` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`appointment_diagnosis` TO 'coordinator';
GRANT SELECT ON TABLE `hemis_db`.`incident` TO 'coordinator';
