-- =====================================================
-- HEMIS Database Views Documentation
-- =====================================================
-- 
-- This file contains database views that provide simplified access to complex
-- data relationships across the HEMIS (Hospital Electronic Medical Information System)
-- database. Views are organized by functional areas and serve different user roles.
--
-- =====================================================
-- VIEW CATEGORIES:
-- 1. Patient Management - Basic patient information and summaries
-- 2. Appointments & Scheduling - Calendar, schedules, and room management
-- 3. Medical Records - Vital signs, prescriptions, and diagnoses
-- 4. Incidents & Monitoring - Device monitoring and incident tracking
-- 5. Administration - Staff management and user roles
-- 6. Coordinator & Reports - Operational dashboards and reporting
-- =====================================================

-- -----------------------------------------------------
--  Patient Management Views
-- -----------------------------------------------------

-- view_patient_directory
-- Purpose: Basic patient contact information for reception and administrative staff
-- Usage: Patient lookup, contact lists, basic patient identification
-- Tables: patient
-- Access: reception, admin_hr, admin_medical
CREATE VIEW hemis_db.view_patient_directory AS
SELECT 
    p.id,
    p.full_name,
    p.birth_date,
    p.sex,
    p.phone,
    p.email
FROM patient p;



-- view_patient_summary  
-- Purpose: Patient overview including insurance information for medical staff
-- Usage: Patient intake, medical history review, insurance verification
-- Tables: patient, patient_insurer, insurer
-- Access: doctor, nurse, admin_medical, reception
CREATE VIEW hemis_db.view_patient_summary AS
SELECT 
    p.id,
    p.full_name,
    p.birth_date,
    p.sex,
    i.name AS insurer_name,
    pi.policy_number
FROM patient p
LEFT JOIN patient_insurer pi ON p.id = pi.patient_id
LEFT JOIN insurer i ON pi.insurer_id = i.id;



-- view_patient_medical
-- Purpose: Medical-specific patient information including allergies
-- Usage: Medical assessment, allergy alerts, clinical decision making
-- Tables: patient
-- Access: doctor, nurse, admin_medical
CREATE VIEW hemis_db.view_patient_medical AS
SELECT 
    p.id,
    p.full_name,
    p.birth_date,
    p.sex,
    p.allergies
FROM patient p;



-- view_patient_financial
-- Purpose: Patient financial status and insurance billing information
-- Usage: Billing, payment tracking, financial reporting
-- Tables: patient, patient_insurer, insurer, appointment_invoice, payment_status
-- Access: admin_finance, reception, coordinator
CREATE VIEW hemis_db.view_patient_financial AS
SELECT 
    p.id,
    p.full_name,
    i.name AS insurer_name,
    ai.total_amount,
    ai.copay_amount,
    ps.name AS payment_status
FROM patient p
JOIN patient_insurer pi ON p.id = pi.patient_id
JOIN insurer i ON pi.insurer_id = i.id
LEFT JOIN appointment_invoice ai ON ai.insurer_id = i.id
LEFT JOIN payment_status ps ON ai.payment_status_id = ps.id;



-- -----------------------------------------------------
--  Appointments & Scheduling Views
-- -----------------------------------------------------

-- view_appointment_calendar
-- Purpose: Comprehensive appointment information for calendar display
-- Usage: Daily/weekly scheduling, appointment management, room allocation
-- Tables: appointment, patient, doctor, specialty, room
-- Access: reception, coordinator, admin_medical, doctor
CREATE VIEW hemis_db.view_appointment_calendar AS
SELECT 
    a.id,
    a.start_at,
    a.end_at,
    a.appointment_status_id,
    d.user_id AS doctor_user_id,
    s.name AS specialty,
    p.full_name AS patient_name,
    r.code AS room
FROM appointment a
JOIN patient p ON a.patient_id = p.id
JOIN doctor d ON a.doctor_id = d.id
JOIN specialty s ON a.specialty_id = s.id
LEFT JOIN room r ON a.room_id = r.id;



-- view_doctor_schedule
-- Purpose: Doctor availability and working hours for scheduling
-- Usage: Appointment booking, schedule planning, availability checking
-- Tables: doctor_schedule, doctor
-- Access: reception, coordinator, admin_medical
CREATE VIEW hemis_db.view_doctor_schedule AS
SELECT 
    d.id AS doctor_id,
    d.user_id,
    ds.weekday,
    ds.start_time,
    ds.end_time,
    ds.slot_minutes
FROM doctor_schedule ds
JOIN doctor d ON ds.doctor_id = d.id;



-- view_triage_queue
-- Purpose: Prioritized patient queue based on triage levels
-- Usage: Emergency triage, patient prioritization, workflow management
-- Tables: appointment, patient, triage_priority
-- Access: nurse, doctor, coordinator, admin_medical
CREATE VIEW hemis_db.view_triage_queue AS
SELECT 
    a.id AS appointment_id,
    p.full_name AS patient_name,
    tp.level AS triage_level,
    tp.name AS triage_name,
    a.start_at
FROM appointment a
JOIN patient p ON a.patient_id = p.id
JOIN triage_priority tp ON a.triage_priority_id = tp.id
WHERE a.appointment_status_id IS NOT NULL
ORDER BY tp.level ASC, a.start_at ASC;



-- view_room_allocation
-- Purpose: Current room assignments and availability status
-- Usage: Room management, equipment allocation, facility planning
-- Tables: room, appointment, patient, doctor
-- Access: coordinator, admin_medical, admin_system
CREATE VIEW hemis_db.view_room_allocation AS
SELECT 
    r.id AS room_id,
    r.code,
    r.type,
    a.id AS appointment_id,
    p.full_name AS patient_name,
    d.user_id AS doctor_user_id
FROM room r
LEFT JOIN appointment a ON r.id = a.room_id
LEFT JOIN patient p ON a.patient_id = p.id
LEFT JOIN doctor d ON a.doctor_id = d.id;



-- -----------------------------------------------------
--  Medical Records Views
-- -----------------------------------------------------

-- view_vital_signs_latest
-- Purpose: Most recent vital signs readings for each patient and metric
-- Usage: Current patient status, clinical assessment, monitoring
-- Tables: reading, device, metric (with subquery for latest readings)
-- Access: doctor, nurse, admin_medical
-- Note: Complex view using subquery to get latest timestamp per patient/metric
CREATE VIEW hemis_db.view_vital_signs_latest AS
SELECT 
    r1.patient_id,
    m.code,
    m.name,
    m.unit,
    r1.value,
    r1.ts
FROM (
    SELECT 
        d.patient_id,
        r.metric_id,
        MAX(r.ts) AS latest_ts
    FROM reading r
    JOIN device d ON r.device_id = d.id
    GROUP BY d.patient_id, r.metric_id
) last
JOIN reading r1 
    ON last.patient_id = (SELECT patient_id FROM device WHERE id = r1.device_id)
   AND last.metric_id = r1.metric_id
   AND last.latest_ts = r1.ts
JOIN metric m ON r1.metric_id = m.id;



-- view_vital_signs_history
-- Purpose: Complete history of all vital signs readings
-- Usage: Trend analysis, historical review, research data
-- Tables: reading, device, metric
-- Access: doctor, admin_medical, admin_system
CREATE VIEW hemis_db.view_vital_signs_history AS
SELECT 
    d.patient_id,
    m.code,
    m.name,
    m.unit,
    r.value,
    r.ts
FROM reading r
JOIN device d ON r.device_id = d.id
JOIN metric m ON r.metric_id = m.id;



-- view_prescriptions
-- Purpose: Prescription records linked to appointments and patients
-- Usage: Medication tracking, prescription history, clinical review
-- Tables: prescription, appointment, patient, doctor
-- Access: doctor, nurse, admin_medical, pharmacy
CREATE VIEW hemis_db.view_prescriptions AS
SELECT 
    pr.id AS prescription_id,
    p.full_name AS patient_name,
    d.user_id AS doctor_user_id,
    pr.text,
    pr.created_at
FROM prescription pr
JOIN appointment a ON pr.appointment_id = a.id
JOIN patient p ON a.patient_id = p.id
JOIN doctor d ON a.doctor_id = d.id;



-- view_diagnoses
-- Purpose: Patient diagnoses with ICD-10 codes and doctor information
-- Usage: Medical records, diagnosis tracking, clinical documentation
-- Tables: appointment_diagnosis, diagnosis_icd10, appointment, doctor
-- Access: doctor, admin_medical, medical records
CREATE VIEW hemis_db.view_diagnoses AS
SELECT 
    ad.appointment_id,
    di.code AS diagnosis_code,
    di.name AS diagnosis_name,
    d.user_id AS doctor_user_id
FROM appointment_diagnosis ad
JOIN diagnosis_icd10 di ON ad.diagnosis_id = di.id
JOIN appointment a ON ad.appointment_id = a.id
JOIN doctor d ON a.doctor_id = d.id;


-- -----------------------------------------------------
--  Incidents & Monitoring Views
-- -----------------------------------------------------

-- view_active_incidents
-- Purpose: Currently open or in-progress monitoring incidents
-- Usage: Real-time monitoring, incident response, alert management
-- Tables: incident
-- Access: admin_system, coordinator, doctor (for patient incidents)
-- Filter: Only incidents with status 'open' or 'in_progress'
CREATE VIEW hemis_db.view_active_incidents AS
SELECT 
    i.id,
    i.rule_id,
    i.patient_id,
    i.device_id,
    i.metric,
    i.severity,
    i.status,
    i.opened_at
FROM incident i
WHERE i.status IN ('open','in_progress');



-- view_incident_history
-- Purpose: Resolved incidents for historical analysis and reporting
-- Usage: Incident analysis, system improvement, compliance reporting
-- Tables: incident
-- Access: admin_system, coordinator, admin_medical
-- Filter: Only incidents with status 'resolved'
CREATE VIEW hemis_db.view_incident_history AS
SELECT 
    i.id,
    i.rule_id,
    i.patient_id,
    i.device_id,
    i.metric,
    i.severity,
    i.status,
    i.opened_at,
    i.closed_at
FROM incident i
WHERE i.status = 'resolved';



-- view_device_status
-- Purpose: Current status and configuration of monitoring devices
-- Usage: Device management, maintenance scheduling, system monitoring
-- Tables: device
-- Access: admin_system, coordinator, technical staff
CREATE VIEW hemis_db.view_device_status AS
SELECT 
    d.id,
    d.label,
    d.patient_id,
    d.firmware,
    d.last_seen_at,
    d.active
FROM device d;


-- -----------------------------------------------------
--  Administration Views
-- -----------------------------------------------------

-- view_staff_directory
-- Purpose: Complete staff information including roles and specialties
-- Usage: Staff management, role assignment, organizational structure
-- Tables: user, user_role, role, doctor, doctor_specialty, specialty
-- Access: admin_hr, super_admin, coordinator
-- Note: Uses LEFT JOINs to handle users without doctor records
CREATE VIEW hemis_db.view_staff_directory AS
SELECT 
    u.id AS user_id,
    u.full_name,
    r.name AS role,
    s.name AS specialty
FROM user u
LEFT JOIN user_role ur ON u.id = ur.user_id
LEFT JOIN role r ON ur.role_id = r.id
LEFT JOIN doctor d ON d.user_id = u.id
LEFT JOIN doctor_specialty ds ON d.id = ds.doctor_id
LEFT JOIN specialty s ON ds.specialty_id = s.id;



-- view_billing_summary
-- Purpose: Comprehensive billing information for financial management
-- Usage: Billing operations, payment tracking, financial reporting
-- Tables: appointment_invoice, appointment, patient, insurer, payment_status
-- Access: admin_finance, coordinator, reception
CREATE VIEW hemis_db.view_billing_summary AS
SELECT 
    ai.id AS invoice_id,
    p.full_name AS patient_name,
    i.name AS insurer_name,
    ai.total_amount,
    ai.copay_amount,
    ps.name AS payment_status,
    ai.issued_at
FROM appointment_invoice ai
JOIN appointment a ON ai.appointment_id = a.id
JOIN patient p ON a.patient_id = p.id
JOIN insurer i ON ai.insurer_id = i.id
JOIN payment_status ps ON ai.payment_status_id = ps.id;



-- view_payment_status
-- Purpose: Payment status summary with counts and totals
-- Usage: Financial reporting, cash flow analysis, payment tracking
-- Tables: payment_status, appointment_invoice
-- Access: admin_finance, coordinator
-- Note: Aggregates data with GROUP BY for summary statistics
CREATE VIEW hemis_db.view_payment_status AS
SELECT 
    ps.id,
    ps.name,
    COUNT(ai.id) AS invoice_count,
    SUM(ai.total_amount) AS total_amount
FROM payment_status ps
LEFT JOIN appointment_invoice ai ON ai.payment_status_id = ps.id
GROUP BY ps.id, ps.name;



-- view_user_roles
-- Purpose: User authentication and role assignment information
-- Usage: User management, access control, security administration
-- Tables: user, user_role, role
-- Access: admin_hr, super_admin, admin_system
CREATE VIEW hemis_db.view_user_roles AS
SELECT 
    u.id AS user_id,
    u.full_name,
    u.email,
    r.name AS role
FROM user u
JOIN user_role ur ON u.id = ur.user_id
JOIN role r ON ur.role_id = r.id;


-- -----------------------------------------------------
--  Coordinator & Reports Views
-- -----------------------------------------------------

-- view_operations_dashboard
-- Purpose: Key performance indicators for operational management
-- Usage: Daily operations overview, management reporting, decision making
-- Tables: patient, appointment, incident
-- Access: coordinator, super_admin, admin_medical
-- Note: Uses subqueries to calculate real-time counts
CREATE VIEW hemis_db.view_operations_dashboard AS
SELECT 
    (SELECT COUNT(*) FROM patient) AS total_patients,
    (SELECT COUNT(*) FROM appointment WHERE DATE(start_at) = CURDATE()) AS appointments_today,
    (SELECT COUNT(*) FROM incident WHERE status = 'open') AS active_incidents;



-- view_daily_report
-- Purpose: Daily activity summary for operational reporting
-- Usage: Daily operations review, trend analysis, performance tracking
-- Tables: appointment, patient, prescription
-- Access: coordinator, admin_medical, super_admin
-- Note: Groups data by date for daily aggregation
CREATE VIEW hemis_db.view_daily_report AS
SELECT 
    DATE(a.start_at) AS report_date,
    COUNT(a.id) AS appointments_count,
    COUNT(DISTINCT p.id) AS patients_count,
    COUNT(pr.id) AS prescriptions_count
FROM appointment a
JOIN patient p ON a.patient_id = p.id
LEFT JOIN prescription pr ON pr.appointment_id = a.id
GROUP BY DATE(a.start_at);



-- view_finance_report
-- Purpose: Financial summary by insurer for financial management
-- Usage: Financial reporting, insurer performance analysis, billing review
-- Tables: appointment_invoice, insurer
-- Access: admin_finance, coordinator, super_admin
-- Note: Aggregates financial data by insurer
CREATE VIEW hemis_db.view_finance_report AS
SELECT 
    i.name AS insurer_name,
    COUNT(ai.id) AS invoice_count,
    SUM(ai.total_amount) AS total_billed,
    SUM(ai.copay_amount) AS total_copay
FROM appointment_invoice ai
JOIN insurer i ON ai.insurer_id = i.id
GROUP BY i.name;



-- view_medical_report
-- Purpose: Patient medical activity summary for clinical management
-- Usage: Patient care analysis, clinical reporting, medical management
-- Tables: patient, appointment, appointment_diagnosis, prescription, incident
-- Access: admin_medical, coordinator, doctor
-- Note: Provides comprehensive patient activity metrics
CREATE VIEW hemis_db.view_medical_report AS
SELECT 
    p.full_name,
    COUNT(ad.diagnosis_id) AS diagnosis_count,
    COUNT(pr.id) AS prescription_count,
    COUNT(i.id) AS incident_count
FROM patient p
LEFT JOIN appointment a ON p.id = a.patient_id
LEFT JOIN appointment_diagnosis ad ON a.id = ad.appointment_id
LEFT JOIN prescription pr ON a.id = pr.appointment_id
LEFT JOIN incident i ON p.id = i.patient_id
GROUP BY p.id;
