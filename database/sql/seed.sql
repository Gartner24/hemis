-- Seed data para hemis_db
--
-- ESTRUCTURA DE ROLES Y PERMISOS:
-- ===================================
-- 1. super_admin    - Super Administrador (acceso total al sistema)
-- 2. admin_hr       - Admin de RRHH (gestión de usuarios, doctores, personal)
-- 3. admin_medical  - Admin Médico (gestión de especialidades, horarios médicos)
-- 4. admin_finance  - Admin Financiero (facturación, pagos, aseguradoras)
-- 5. admin_system   - Admin de Sistema (configuración técnica, equipos)
-- 6. doctor         - Doctor (consultas, diagnósticos, prescripciones)
-- 7. nurse          - Enfermera (apoyo médico, notas de citas)
-- 8. reception      - Recepción (citas, pacientes, check-in)
-- 9. coordinator    - Coordinador Médico (gestión de horarios + funciones de doctor)
--
-- Todas las contraseñas son 'admin123' por fines de demostración
--

-- Select the database
USE hemis_db;

SET NAMES utf8mb4;

START TRANSACTION;

-- ----------------------
-- Core catalogs
-- ----------------------
INSERT INTO identification_type (id, code, name, active) VALUES
  (1,'CC','Cédula de ciudadanía',1),
  (2,'TI','Tarjeta de identidad',1),
  (3,'CE','Cédula de extranjería',1),
  (4,'RC','Registro civil',1),
  (5,'PAS','Pasaporte',1),
  (6,'PEP','Permiso especial de permanencia',1)
ON DUPLICATE KEY UPDATE name=VALUES(name), active=VALUES(active);

INSERT INTO appointment_status (id, code, name, flow_order) VALUES
  (1,'PROG','Scheduled',1),
  (2,'LLEG','Checked-in',2),
  (3,'CONS','In consultation',3),
  (4,'FIN','Completed',NULL),
  (5,'CANC','Canceled',NULL),
  (6,'NOSHOW','No-show',NULL)
ON DUPLICATE KEY UPDATE name=VALUES(name), flow_order=VALUES(flow_order);

INSERT INTO appointment_type (id, name, requires_equipment) VALUES
  (1,'General consultation',0),
  (2,'Cardiology consult',0),
  (3,'Dentistry procedure',1)
ON DUPLICATE KEY UPDATE requires_equipment=VALUES(requires_equipment);

INSERT INTO triage_priority (id, name, level) VALUES
  (1,'High',1),
  (2,'Medium',2),
  (3,'Low',3)
ON DUPLICATE KEY UPDATE name=VALUES(name), level=VALUES(level);

INSERT INTO payment_status (id, name) VALUES
  (1,'Pending'),(2,'Paid'),(3,'Rejected')
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO equipment_type (id, name, active) VALUES
  (1,'General',1),(2,'Dentistry',1),(3,'Cardiology',1)
ON DUPLICATE KEY UPDATE name=VALUES(name), active=VALUES(active);

INSERT INTO specialty (id, name, active) VALUES
  (1,'General Medicine',1),
  (2,'Cardiology',1),
  (3,'Dentistry',1)
ON DUPLICATE KEY UPDATE name=VALUES(name), active=VALUES(active);

-- ----------------------
-- Users & roles
-- ----------------------
INSERT INTO role (id, name, active) VALUES
  (1,'super_admin',1),      -- Super administrador (acceso total)
  (2,'admin_hr',1),         -- Admin de RRHH (maneja usuarios/doctores)
  (3,'admin_medical',1),    -- Admin médico (gestión médica)
  (4,'admin_finance',1),    -- Admin financiero (facturación/pagos)
  (5,'admin_system',1),     -- Admin de sistema (configuración técnica)
  (6,'doctor',1),           -- Doctor
  (7,'nurse',1),            -- Enfermera
  (8,'reception',1),        -- Recepción
  (9,'coordinator',1)       -- Coordinador médico
ON DUPLICATE KEY UPDATE active=VALUES(active);

-- NOTE: password_hash uses SHA-256 hashes. All passwords are 'admin123' for demo purposes.
INSERT INTO user (id, email, full_name, password_hash, active) VALUES
  -- Super Administrador
  (1,'superadmin@clinic.test','Super Admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  
  -- Administradores especializados
  (2,'hr.admin@clinic.test','María Rodriguez - HR Admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  (3,'medical.admin@clinic.test','Dr. Carlos Mendoza - Medical Admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  (4,'finance.admin@clinic.test','Ana Torres - Finance Admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  (5,'system.admin@clinic.test','Tech Admin - IT Support','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  
  -- Coordinador médico
  (6,'coordinator@clinic.test','Dr. Patricia Silva - Medical Coordinator','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  
  -- Doctores
  (7,'greg.house@clinic.test','Dr. Greg House','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  (8,'meredith.grey@clinic.test','Dr. Meredith Grey','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  (9,'miranda.bailey@clinic.test','Dr. Miranda Bailey','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  
  -- Enfermeras
  (10,'nurse1@clinic.test','Carolina Ruiz - Head Nurse','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  (11,'nurse2@clinic.test','Luis Herrera - Nurse','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  
  -- Recepción
  (12,'reception1@clinic.test','Ellie Sato - Reception','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1),
  (13,'reception2@clinic.test','Sofia Martinez - Reception','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',1)
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name), active=VALUES(active);

INSERT INTO user_role (user_id, role_id) VALUES
  -- Super Administrador (acceso total)
  (1,1),  -- super_admin
  
  -- Administradores especializados
  (2,2),  -- hr_admin (María Rodriguez)
  (3,3),  -- medical_admin (Dr. Carlos Mendoza)
  (4,4),  -- finance_admin (Ana Torres)
  (5,5),  -- system_admin (Tech Admin)
  
  -- Coordinador médico (también puede tener permisos de doctor)
  (6,9),  -- coordinator (Dr. Patricia Silva)
  (6,6),  -- también doctor
  
  -- Doctores
  (7,6),  -- doctor (Dr. House)
  (8,6),  -- doctor (Dr. Grey)
  (9,6),  -- doctor (Dr. Bailey)
  
  -- Enfermeras
  (10,7), -- nurse (Carolina Ruiz - Head Nurse)
  (11,7), -- nurse (Luis Herrera)
  
  -- Recepción
  (12,8), -- reception (Ellie Sato)
  (13,8)  -- reception (Sofia Martinez)
ON DUPLICATE KEY UPDATE user_id=VALUES(user_id);

-- ----------------------
-- Doctors & schedules
-- ----------------------
INSERT INTO doctor (id, user_id, license_number, active) VALUES
  (1,6,'MED-CO-1001',1),   -- Dr. Patricia Silva (Coordinador médico)
  (2,7,'MED-CO-1002',1),   -- Dr. Greg House
  (3,8,'MED-CO-1003',1),   -- Dr. Meredith Grey
  (4,9,'MED-CO-1004',1)    -- Dr. Miranda Bailey
ON DUPLICATE KEY UPDATE license_number=VALUES(license_number), active=VALUES(active);

INSERT INTO doctor_specialty (doctor_id, specialty_id) VALUES
  -- Dr. Patricia Silva (Coordinador) - General Medicine
  (1,1),
  -- Dr. Greg House - General Medicine y Cardiology
  (2,1),(2,2),
  -- Dr. Meredith Grey - General Medicine
  (3,1),
  -- Dr. Miranda Bailey - General Medicine y Dentistry
  (4,1),(4,3)
ON DUPLICATE KEY UPDATE doctor_id=VALUES(doctor_id);

-- Weekday: 1=Mon .. 7=Sun
INSERT INTO doctor_schedule (id, doctor_id, weekday, start_time, end_time, slot_minutes) VALUES
  -- Dr. Patricia Silva (Coordinador)
  (1,1,1,'08:00:00','12:00:00',30),  -- Lunes mañana
  (2,1,3,'14:00:00','18:00:00',30),  -- Miércoles tarde
  -- Dr. Greg House
  (3,2,2,'08:00:00','12:00:00',45),  -- Martes mañana
  (4,2,4,'14:00:00','17:00:00',45),  -- Jueves tarde
  -- Dr. Meredith Grey
  (5,3,1,'14:00:00','18:00:00',30),  -- Lunes tarde
  (6,3,5,'08:00:00','12:00:00',30),  -- Viernes mañana
  -- Dr. Miranda Bailey
  (7,4,2,'14:00:00','18:00:00',20),  -- Martes tarde
  (8,4,3,'08:00:00','12:00:00',20)   -- Miércoles mañana
ON DUPLICATE KEY UPDATE start_time=VALUES(start_time), end_time=VALUES(end_time), slot_minutes=VALUES(slot_minutes);

-- ----------------------
-- Rooms & equipment
-- ----------------------
INSERT INTO room (id, code, capacity, type, active) VALUES
  (1,'A-101',1,'General',1),
  (2,'A-102',1,'Cardiology',1),
  (3,'B-201',1,'Dentistry',1)
ON DUPLICATE KEY UPDATE capacity=VALUES(capacity), type=VALUES(type), active=VALUES(active);

INSERT INTO equipment (id, equipment_type_id, name, active) VALUES
  (1,1,'General exam kit',1),
  (2,2,'Dental chair',1),
  (3,3,'ECG monitor',1)
ON DUPLICATE KEY UPDATE name=VALUES(name), active=VALUES(active);

INSERT INTO room_equipment (room_id, equipment_id) VALUES
  (1,1),(2,3),(3,2)
ON DUPLICATE KEY UPDATE room_id=VALUES(room_id);

-- ----------------------
-- Insurers
-- ----------------------
INSERT INTO insurer (id, name, active) VALUES
  (1,'SURA',1),
  (2,'Sanitas',1),
  (3,'Compensar',1)
ON DUPLICATE KEY UPDATE active=VALUES(active);

-- ----------------------
-- Patients
-- ----------------------
INSERT INTO patient (id, identification_type_id, ident_number, full_name, birth_date, sex, phone, email, allergies, emergency_contact) VALUES
  (1,1,'1001001001','Juan Pérez','1990-05-12','M','3001112233','juan.perez@test.com','Penicillin','María Pérez'),
  (2,1,'1002003004','Ana Gómez','1988-09-21','F','3009998877','ana.gomez@test.com','', 'Carlos Gómez'),
  (3,5,'PA1234567','Michael Smith','1975-01-03','M','3012223344','michael.smith@test.com','Latex','Laura Smith')
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name), email=VALUES(email);

INSERT INTO patient_insurer (patient_id, insurer_id, policy_number, valid_from, valid_to) VALUES
  (1,1,'SURA-001-2024','2024-01-01','2025-12-31'),
  (2,2,'SAN-009-2024','2024-01-01','2025-12-31'),
  (3,3,'COMP-777-2024','2024-01-01','2025-12-31')
ON DUPLICATE KEY UPDATE policy_number=VALUES(policy_number), valid_to=VALUES(valid_to);

-- ----------------------
-- Catálogos de IoT y dispositivos
-- ----------------------
INSERT INTO metric (id, code, name, unit) VALUES
  (1,'heart_rate','Heart rate','bpm'),
  (2,'spo2','Oxygen saturation','%'),
  (3,'temp_skin','Skin temperature','C')
ON DUPLICATE KEY UPDATE name=VALUES(name), unit=VALUES(unit);

INSERT INTO device (id, label, patient_id, firmware, last_seen_at, active) VALUES
  (1,'ESP32-A1',1,'v1.0.0',NOW(),1),
  (2,'ESP32-B2',2,'v1.0.0',NOW(),1),
  (3,'ESP32-C3',NULL,'v1.0.0',NULL,1)
ON DUPLICATE KEY UPDATE patient_id=VALUES(patient_id), firmware=VALUES(firmware), last_seen_at=VALUES(last_seen_at);

-- ----------------------
-- Algunas citas para demostrar
-- ----------------------
-- Hoy: dos programadas, una finalizada en el pasado
INSERT INTO appointment (id, patient_id, doctor_id, specialty_id, room_id, appointment_type_id, triage_priority_id,
                         start_at, end_at, appointment_status_id, reason, created_by, created_at, updated_at)
VALUES
  (1,1,2,1,1,1,2, CONCAT(CURDATE(),' 09:00:00'), CONCAT(CURDATE(),' 09:30:00'), 1,'Routine check',12,NOW(),NOW()),
  (2,2,4,3,3,3,2, CONCAT(CURDATE(),' 10:00:00'), CONCAT(CURDATE(),' 10:30:00'), 1,'Dental cleaning',12,NOW(),NOW()),
  (3,1,2,2,2,2,1, DATE_SUB(CONCAT(CURDATE(),' 08:00:00'), INTERVAL 1 DAY), DATE_SUB(CONCAT(CURDATE(),' 08:30:00'), INTERVAL 1 DAY),
     4,'ECG follow-up',13,NOW(),NOW())
ON DUPLICATE KEY UPDATE appointment_status_id=VALUES(appointment_status_id), updated_at=VALUES(updated_at);

INSERT INTO appointment_status_history (id, appointment_id, old_status_id, new_status_id, changed_by, changed_at) VALUES
  (1,3,1,2,12, DATE_SUB(CONCAT(CURDATE(),' 07:50:00'), INTERVAL 1 DAY)),
  (2,3,2,3,12, DATE_SUB(CONCAT(CURDATE(),' 08:00:00'), INTERVAL 1 DAY)),
  (3,3,3,4,12, DATE_SUB(CONCAT(CURDATE(),' 08:35:00'), INTERVAL 1 DAY))
ON DUPLICATE KEY UPDATE new_status_id=VALUES(new_status_id), changed_at=VALUES(changed_at);

INSERT INTO appointment_note (id, appointment_id, author_id, text, created_at) VALUES
  (1,3,12,'Patient tolerated ECG test well.', DATE_SUB(NOW(), INTERVAL 1 DAY))
ON DUPLICATE KEY UPDATE text=VALUES(text);

INSERT INTO appointment_equipment (appointment_id, equipment_id) VALUES
  (2,2)
ON DUPLICATE KEY UPDATE appointment_id=VALUES(appointment_id);

-- ----------------------
-- Ejemplo de lecturas de IoT
-- ----------------------
INSERT INTO reading (id, device_id, metric_id, ts, value, quality_flag) VALUES
  (1,1,1, DATE_SUB(NOW(), INTERVAL 5 MINUTE), 78.0,'ok'),
  (2,1,2, DATE_SUB(NOW(), INTERVAL 5 MINUTE), 97.0,'ok'),
  (3,1,3, DATE_SUB(NOW(), INTERVAL 5 MINUTE), 36.4,'ok'),
  (4,2,1, DATE_SUB(NOW(), INTERVAL 10 MINUTE), 84.0,'ok'),
  (5,2,2, DATE_SUB(NOW(), INTERVAL 10 MINUTE), 95.0,'ok')
ON DUPLICATE KEY UPDATE value=VALUES(value), ts=VALUES(ts);

-- ----------------------
-- Reglas y asignaciones
-- ----------------------
INSERT INTO rule (id, metric_id, rule_type, operator, threshold_value, window_min, severity, enabled, name) VALUES
  (1,1,'threshold','>',110,10,'High',1,'Tachycardia >110 bpm'),
  (2,2,'threshold','<',90,10,'Medium',1,'Low SpO2 <90%'),
  (3,3,'threshold','>',38.0,15,'Medium',1,'Fever >38C')
ON DUPLICATE KEY UPDATE threshold_value=VALUES(threshold_value), enabled=VALUES(enabled);

INSERT INTO rule_assignment (id, rule_id, patient_id, device_id) VALUES
  (1,1,1,NULL),
  (2,2,1,NULL),
  (3,3,NULL,2)
ON DUPLICATE KEY UPDATE rule_id=VALUES(rule_id), patient_id=VALUES(patient_id), device_id=VALUES(device_id);

COMMIT;
