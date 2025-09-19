"""
IoT Telemetry API endpoints
Handles real-time data from IoT devices and provides access for medic role
"""

from flask import Blueprint, request, jsonify, current_app
from ..auth.auth_service import medic_role_required, login_required, AuthService
from ..db.connection import execute_query
from ..models.telemetry_models import TelemetryData, DeviceStatus
import logging
from datetime import datetime, timedelta
import json
import threading
import time

bp = Blueprint('telemetry', __name__)
logger = logging.getLogger(__name__)

# Global variable to track polling state
_polling_active = False
_polling_thread = None

def start_telemetry_polling():
    """Start background polling for telemetry data every 1 second"""
    global _polling_active, _polling_thread
    
    if _polling_active:
        logger.info("Telemetry polling already active")
        return
    
    _polling_active = True
    logger.info("Starting telemetry polling every 1 second...")
    
    def poll_telemetry_data():
        while _polling_active:
            try:
                # Get latest readings for all active devices
                query = """
                    SELECT 
                        r.device_id,
                        m.code as metric_code,
                        r.value,
                        r.ts,
                        d.patient_id
                    FROM reading r
                    JOIN metric m ON r.metric_id = m.id
                    JOIN device d ON r.device_id = d.id
                    WHERE d.active = 1
                    AND r.ts >= %s
                    ORDER BY r.device_id, m.code, r.ts DESC
                """
                
                # Get readings from last 2 seconds to catch recent updates
                cutoff_time = datetime.now() - timedelta(seconds=2)
                readings = execute_query('admin_system', query, (cutoff_time,))
                
                if readings:
                    # Group readings by device
                    device_data = {}
                    for reading in readings:
                        device_id = reading['device_id']
                        if device_id not in device_data:
                            device_data[device_id] = {
                                'device_id': device_id,
                                'patient_id': reading['patient_id'],
                                'heart_rate': 0,
                                'spo2': 0,
                                'temperature': 0,
                                'timestamp': reading['ts'],
                                'is_simulated': False
                            }
                        
                        # Update the latest value for each metric
                        metric_code = reading['metric_code']
                        if metric_code == 'heart_rate':
                            device_data[device_id]['heart_rate'] = reading['value']
                        elif metric_code == 'spo2':
                            device_data[device_id]['spo2'] = reading['value']
                        elif metric_code == 'temp_skin':
                            device_data[device_id]['temperature'] = reading['value']
                            device_data[device_id]['timestamp'] = reading['ts']
                    
                    # Broadcast updates for each device
                    for device_id, telemetry_data in device_data.items():
                        try:
                            from ..services.websocket_service import get_websocket_service
                            websocket_service = get_websocket_service()
                            
                            # Broadcast to global room
                            websocket_service.broadcast_telemetry_update('global_all', telemetry_data)
                            
                            # Broadcast to device-specific room
                            websocket_service.broadcast_telemetry_update(f'device_{device_id}', telemetry_data)
                            
                            # Broadcast to patient room if device is assigned
                            if telemetry_data['patient_id']:
                                websocket_service.broadcast_telemetry_update(f'patient_{telemetry_data["patient_id"]}', telemetry_data)
                                
                        except Exception as ws_error:
                            logger.debug(f"WebSocket broadcast failed for device {device_id}: {str(ws_error)}")
                
            except Exception as e:
                logger.error(f"Error in telemetry polling: {str(e)}")
            
            time.sleep(1)  # Poll every 1 second
    
    _polling_thread = threading.Thread(target=poll_telemetry_data, daemon=True)
    _polling_thread.start()

def stop_telemetry_polling():
    """Stop background polling for telemetry data"""
    global _polling_active
    _polling_active = False
    logger.info("Stopped telemetry polling")

def is_polling_active():
    """Check if telemetry polling is active"""
    return _polling_active

@bp.route('/', methods=['GET'])
@medic_role_required
def get_telemetry_overview():
    """Get overview of all telemetry data for medic"""
    try:
        # Get current user info
        current_user = AuthService.get_current_user()
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get all devices and their latest readings using the correct database schema
        query = """
            SELECT 
                d.id as device_id,
                d.label as device_name,
                d.firmware,
                d.last_seen_at,
                d.active as device_status,
                p.id as patient_id,
                p.full_name as patient_name,
                p.birth_date,
                p.sex,
                -- Get latest readings for each metric
                hr.value as heart_rate,
                spo2.value as spo2,
                temp.value as temp_skin,
                GREATEST(
                    COALESCE(hr.ts, '1900-01-01'),
                    COALESCE(spo2.ts, '1900-01-01'),
                    COALESCE(temp.ts, '1900-01-01')
                ) as latest_timestamp
            FROM device d
            LEFT JOIN patient p ON d.patient_id = p.id
            -- Get latest heart rate reading
            LEFT JOIN (
                SELECT device_id, value, ts
                FROM reading r1
                JOIN metric m1 ON r1.metric_id = m1.id
                WHERE m1.code = 'heart_rate'
                AND r1.ts = (
                    SELECT MAX(r2.ts)
                    FROM reading r2
                    JOIN metric m2 ON r2.metric_id = m2.id
                    WHERE r2.device_id = r1.device_id AND m2.code = 'heart_rate'
                )
            ) hr ON d.id = hr.device_id
            -- Get latest SpO2 reading
            LEFT JOIN (
                SELECT device_id, value, ts
                FROM reading r1
                JOIN metric m1 ON r1.metric_id = m1.id
                WHERE m1.code = 'spo2'
                AND r1.ts = (
                    SELECT MAX(r2.ts)
                    FROM reading r2
                    JOIN metric m2 ON r2.metric_id = m2.id
                    WHERE r2.device_id = r1.device_id AND m2.code = 'spo2'
                )
            ) spo2 ON d.id = spo2.device_id
            -- Get latest temperature reading
            LEFT JOIN (
                SELECT device_id, value, ts
                FROM reading r1
                JOIN metric m1 ON r1.metric_id = m1.id
                WHERE m1.code = 'temp_skin'
                AND r1.ts = (
                    SELECT MAX(r2.ts)
                    FROM reading r2
                    JOIN metric m2 ON r2.metric_id = m2.id
                    WHERE r2.device_id = r1.device_id AND m2.code = 'temp_skin'
                )
            ) temp ON d.id = temp.device_id
            WHERE d.active = 1
            ORDER BY d.id
        """
        
        devices = execute_query(current_user['role'], query)
        
        return jsonify({
            'devices': devices,
            'total_devices': len(devices),
            'active_devices': len([d for d in devices if d.get('device_status') == 1]),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting telemetry overview: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/patients-with-devices', methods=['GET'])
@login_required
def get_patients_with_devices():
    """Get all patients with their assigned devices and latest vital signs for frontend"""
    try:
        # Start polling if not already active
        if not is_polling_active():
            start_telemetry_polling()
        
        current_user = AuthService.get_current_user()
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get patients with their devices and latest readings - simplified query
        query = """
            SELECT 
                p.id as patient_id,
                p.full_name,
                p.birth_date,
                p.sex,
                p.phone,
                p.email,
                d.id as device_id,
                d.label as device_name,
                d.firmware,
                d.last_seen_at,
                d.active as device_status
            FROM patient p
            LEFT JOIN device d ON p.id = d.patient_id AND d.active = 1
            ORDER BY p.id, d.id
        """
        
        results = execute_query(current_user['role'], query)
        
        # Group results by patient
        patients = {}
        device_ids = []
        
        for row in results:
            patient_id = row['patient_id']
            if patient_id not in patients:
                # Calculate age from birth_date
                birth_date = datetime.strptime(str(row['birth_date']), '%Y-%m-%d').date()
                age = (datetime.now().date() - birth_date).days // 365
                
                patients[patient_id] = {
                    'patient_id': patient_id,
                    'full_name': row['full_name'],
                    'age': age,
                    'sex': row['sex'],
                    'phone': row['phone'],
                    'email': row['email'],
                    'assigned_devices': []
                }
            
            # Add device if exists
            if row['device_id']:
                device_ids.append(row['device_id'])
                device = {
                    'device_id': row['device_id'],
                    'device_name': row['device_name'],
                    'device_type': 'multi_parameter',
                    'status': 'active' if row['device_status'] == 1 else 'inactive',
                    'last_reading_time': row['last_seen_at'].isoformat() if row['last_seen_at'] else None,
                    'vital_signs': {
                        'heart_rate': 0,
                        'spo2': 0,
                        'temp_skin': 0,
                        'timestamp': None,
                        'is_simulated': False  # Real data from ESP32
                    }
                }
                patients[patient_id]['assigned_devices'].append(device)
        
        # Get latest readings for all devices
        if device_ids:
            readings_query = """
                SELECT 
                    r.device_id,
                    m.code as metric_code,
                    r.value,
                    r.ts
                FROM reading r
                JOIN metric m ON r.metric_id = m.id
                WHERE r.device_id IN ({})
                AND r.ts = (
                    SELECT MAX(r2.ts)
                    FROM reading r2
                    WHERE r2.device_id = r.device_id AND r2.metric_id = r.metric_id
                )
                ORDER BY r.device_id, m.code
            """.format(','.join(map(str, device_ids)))
            
            readings = execute_query(current_user['role'], readings_query)
            
            # Process readings and update devices
            device_readings = {}
            for reading in readings:
                device_id = reading['device_id']
                if device_id not in device_readings:
                    device_readings[device_id] = {}
                device_readings[device_id][reading['metric_code']] = {
                    'value': reading['value'],
                    'timestamp': reading['ts']
                }
            
            # Update patients with reading data
            for patient in patients.values():
                for device in patient['assigned_devices']:
                    device_id = device['device_id']
                    if device_id in device_readings:
                        readings = device_readings[device_id]
                        device['vital_signs'] = {
                            'heart_rate': readings.get('heart_rate', {}).get('value', 0),
                            'spo2': readings.get('spo2', {}).get('value', 0),
                            'temp_skin': readings.get('temp_skin', {}).get('value', 0),
                            'timestamp': readings.get('heart_rate', {}).get('timestamp', 
                                      readings.get('spo2', {}).get('timestamp',
                                      readings.get('temp_skin', {}).get('timestamp'))),
                            'is_simulated': False
                        }
                        if device['vital_signs']['timestamp']:
                            device['last_reading_time'] = device['vital_signs']['timestamp'].isoformat()
                            device['vital_signs']['timestamp'] = device['vital_signs']['timestamp'].isoformat()
        
        return jsonify({
            'patients': list(patients.values()),
            'total_patients': len(patients),
            'patients_with_devices': len([p for p in patients.values() if p['assigned_devices']]),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting patients with devices: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/device/<int:device_id>', methods=['GET'])
@medic_role_required
def get_device_telemetry(device_id):
    """Get telemetry data for a specific device"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get device info and recent readings
        query = """
            SELECT 
                d.device_id,
                d.device_name,
                d.device_type,
                d.status,
                d.patient_id,
                CONCAT(p.first_name, ' ', p.last_name) as patient_name,
                r.reading_id,
                r.heart_rate,
                r.spo2,
                r.temp_skin,
                r.timestamp
            FROM device d
            LEFT JOIN patient p ON d.patient_id = p.patient_id
            LEFT JOIN reading r ON d.device_id = r.device_id
            WHERE d.device_id = %s
            ORDER BY r.timestamp DESC
            LIMIT 100
        """
        
        readings = execute_query(current_user['role'], query, (device_id,))
        
        if not readings:
            return jsonify({'error': 'Device not found'}), 404
        
        device_info = {
            'device_id': readings[0]['device_id'],
            'device_name': readings[0]['device_name'],
            'device_type': readings[0]['device_type'],
            'status': readings[0]['status'],
            'patient_id': readings[0]['patient_id'],
            'patient_name': readings[0]['patient_name'],
            'readings': []
        }
        
        for reading in readings:
            if reading['reading_id']:  # Only add readings that have data
                device_info['readings'].append({
                    'heart_rate': reading['heart_rate'],
                    'spo2': reading['spo2'],
                    'temp_skin': reading['temp_skin'],
                    'timestamp': reading['timestamp']
                })
        
        return jsonify(device_info), 200
        
    except Exception as e:
        logger.error(f"Error getting device telemetry: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/device/<int:device_id>/realtime', methods=['GET'])
@medic_role_required
def get_device_realtime(device_id):
    """Get real-time telemetry data for a specific device (latest reading)"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get latest reading for the device
        query = """
            SELECT 
                d.device_id,
                d.device_name,
                d.status,
                p.patient_id,
                CONCAT(p.first_name, ' ', p.last_name) as patient_name,
                r.heart_rate,
                r.spo2,
                r.temp_skin,
                r.timestamp
            FROM device d
            LEFT JOIN patient p ON d.patient_id = p.patient_id
            LEFT JOIN reading r ON d.device_id = r.device_id
            WHERE d.device_id = %s
            ORDER BY r.timestamp DESC
            LIMIT 1
        """
        
        result = execute_query(current_user['role'], query, (device_id,))
        
        if not result:
            return jsonify({'error': 'Device not found'}), 404
        
        reading = result[0]
        
        # Check if device has recent data (within last 5 minutes)
        if reading['timestamp']:
            last_reading_time = datetime.fromisoformat(reading['timestamp'])
            if datetime.now() - last_reading_time > timedelta(minutes=5):
                reading['status'] = 'stale_data'
        else:
            reading['status'] = 'no_data'
        
        return jsonify({
            'device_id': reading['device_id'],
            'device_name': reading['device_name'],
            'device_status': reading['status'],
            'patient_id': reading['patient_id'],
            'patient_name': reading['patient_name'],
            'vital_signs': {
                'heart_rate': reading['heart_rate'],
                'spo2': reading['spo2'],
                'temperature': reading['temp_skin']
            },
            'timestamp': reading['timestamp'],
            'data_age_minutes': (datetime.now() - datetime.fromisoformat(reading['timestamp'])).total_seconds() / 60 if reading['timestamp'] else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting real-time telemetry: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/patient/<int:patient_id>/telemetry', methods=['GET'])
@medic_role_required
def get_patient_telemetry(patient_id):
    """Get all telemetry data for a specific patient"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get all devices and readings for the patient
        query = """
            SELECT 
                d.device_id,
                d.device_name,
                d.device_type,
                d.status,
                r.reading_id,
                r.heart_rate,
                r.spo2,
                r.temp_skin,
                r.timestamp
            FROM device d
            LEFT JOIN reading r ON d.device_id = r.device_id
            WHERE d.patient_id = %s
            ORDER BY r.timestamp DESC
            LIMIT 500
        """
        
        readings = execute_query(current_user['role'], query, (patient_id,))
        
        if not readings:
            return jsonify({'error': 'Patient not found or no telemetry data'}), 404
        
        # Group readings by device
        devices = {}
        for reading in readings:
            device_id = reading['device_id']
            if device_id not in devices:
                devices[device_id] = {
                    'device_id': device_id,
                    'device_name': reading['device_name'],
                    'device_type': reading['device_type'],
                    'status': reading['status'],
                    'readings': []
                }
            
            if reading['reading_id']:  # Only add readings with data
                devices[device_id]['readings'].append({
                    'heart_rate': reading['heart_rate'],
                    'spo2': reading['spo2'],
                    'temp_skin': reading['temp_skin'],
                    'timestamp': reading['timestamp']
                })
        
        return jsonify({
            'patient_id': patient_id,
            'devices': list(devices.values()),
            'total_readings': sum(len(d['readings']) for d in devices.values()),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting patient telemetry: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/receive', methods=['POST'])
def receive_iot_data():
    """Receive IoT device data from ESP32 (no authentication required for device communication)"""
    try:
        # Log essential request data
        logger.info("=== ESP32 TELEMETRY DATA RECEIVED ===")
        logger.debug(f"Request Headers: {dict(request.headers)}")
        logger.debug(f"Request Method: {request.method}")
        logger.debug(f"Request URL: {request.url}")
        logger.debug(f"Content-Type: {request.content_type}")
        
        # Handle both JSON and form data for ESP32 compatibility
        if request.is_json:
            data = request.get_json()
            logger.info(f"JSON Data received: {data}")
        else:
            # Handle form data (common with ESP32)
            data = request.form.to_dict()
            logger.info(f"Form Data received: {data}")
            
            # Try to parse JSON from form field if present
            if 'json_data' in data:
                try:
                    data = json.loads(data['json_data'])
                    logger.info(f"Parsed JSON from form field: {data}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from form field: {e}")
                    return jsonify({'error': 'Invalid JSON in form data'}), 400
        
        if not data:
            logger.error("No data provided in request")
            return jsonify({'error': 'No data provided'}), 400
        
        # Log all received fields for debugging
        logger.debug(f"All received fields: {list(data.keys())}")
        
        # Validate required fields with better error messages
        required_fields = ['device_id', 'heart_rate', 'spo2', 'temp_skin']
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        # Convert values to appropriate types and validate
        try:
            device_id = int(data['device_id'])
            heart_rate = float(data['heart_rate'])
            spo2 = float(data['spo2'])
            temp_skin = float(data['temp_skin'])
        except (ValueError, TypeError) as e:
            logger.error(f"Data type conversion error: {e}")
            return jsonify({'error': 'Invalid data types. All values must be numeric.'}), 400
        
        # Log the parsed values
        logger.info(f"Parsed values - Device ID: {device_id}, HR: {heart_rate}, SpO2: {spo2}, Temp: {temp_skin}")
        
        # Check if finger is placed (ESP32 returns 0 for HR and SpO2 when no finger detected)
        finger_detected = heart_rate > 0 and spo2 > 0
        
        # Validate data ranges with warnings for out-of-range values
        warnings = []
        if finger_detected:
            # Only validate ranges when finger is detected
            if not (40 <= heart_rate <= 200):
                warnings.append(f"Heart rate {heart_rate} is outside normal range (40-200)")
            if not (70 <= spo2 <= 100):
                warnings.append(f"SpO2 {spo2} is outside normal range (70-100)")
        else:
            # No finger detected - this is normal behavior
            logger.info("No finger detected on sensor - HR and SpO2 readings are 0")
        
        # Temperature validation (always check as it's independent of finger placement)
        if not (30 <= temp_skin <= 45):
            warnings.append(f"Temperature {temp_skin} is outside normal range (30-45)")
        
        if warnings:
            logger.warning(f"Data validation warnings: {'; '.join(warnings)}")
        
        # Insert readings into database using transaction for efficiency
        timestamp = datetime.now()
        logger.debug(f"Inserting data into database with timestamp: {timestamp}")
        
        # Prepare all queries for transaction
        queries = [
            # Insert heart rate reading
            ("INSERT INTO reading (device_id, metric_id, ts, value, quality_flag) VALUES (%s, %s, %s, %s, %s)", 
             (device_id, 1, timestamp, heart_rate, 'ok')),
            # Insert SpO2 reading
            ("INSERT INTO reading (device_id, metric_id, ts, value, quality_flag) VALUES (%s, %s, %s, %s, %s)", 
             (device_id, 2, timestamp, spo2, 'ok')),
            # Insert temperature reading
            ("INSERT INTO reading (device_id, metric_id, ts, value, quality_flag) VALUES (%s, %s, %s, %s, %s)", 
             (device_id, 3, timestamp, temp_skin, 'ok')),
            # Update device last seen time
            ("UPDATE device SET last_seen_at = %s, active = 1 WHERE id = %s", 
             (timestamp, device_id))
        ]
        
        # Execute all queries in a single transaction
        from ..db.connection import execute_transaction
        execute_transaction('admin_system', queries)
        
        # Broadcast real-time update via WebSocket
        try:
            from ..services.websocket_service import broadcast_device_telemetry, get_websocket_service
            telemetry_data = {
                'type': 'iot_data_update',
                'device_id': device_id,
                'patient_id': None,  # Will be set below if device is assigned
                'heart_rate': heart_rate,
                'spo2': spo2,
                'temperature': temp_skin,  # Frontend expects 'temperature'
                'timestamp': timestamp.isoformat(),
                'is_simulated': False
            }
            
            # Get patient_id for this device
            device_query = "SELECT patient_id FROM device WHERE id = %s"
            device_result = execute_query('admin_system', device_query, (device_id,))
            if device_result and device_result[0]['patient_id']:
                telemetry_data['patient_id'] = device_result[0]['patient_id']
            
            # Broadcast to device-specific room
            broadcast_device_telemetry(device_id, telemetry_data)
            
            # Broadcast to global room for real-time monitoring
            websocket_service = get_websocket_service()
            websocket_service.broadcast_telemetry_update('global_all', telemetry_data)
            
            # Also broadcast to patient room if device is assigned
            if telemetry_data['patient_id']:
                from ..services.websocket_service import broadcast_patient_telemetry
                broadcast_patient_telemetry(telemetry_data['patient_id'], telemetry_data)
                
        except Exception as ws_error:
            logger.warning(f"WebSocket broadcast failed: {str(ws_error)}")
        
        # Success logging
        logger.info("=== ESP32 DATA PROCESSED SUCCESSFULLY ===")
        logger.info(f"Device: {device_id} | HR: {heart_rate} | SpO2: {spo2} | Temp: {temp_skin}")
        logger.info(f"Finger detected: {'Yes' if finger_detected else 'No'}")
        logger.info(f"Timestamp: {timestamp}")
        if warnings:
            logger.info(f"Warnings: {'; '.join(warnings)}")
        logger.info("=========================================")
        
        return jsonify({
            'message': 'Data received successfully',
            'device_id': device_id,
            'timestamp': timestamp,
            'finger_detected': finger_detected,
            'warnings': warnings if warnings else None
        }), 201
        
    except Exception as e:
        logger.error(f"Error receiving IoT data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/test-esp32', methods=['POST'])
def test_esp32_endpoint():
    """Test endpoint to simulate ESP32 data for development"""
    try:
        logger.info("=== TESTING ESP32 ENDPOINT ===")
        
        # Generate test data
        import random
        test_data = {
            'device_id': random.randint(1, 3),  # Only devices 1-3 exist in seed data
            'heart_rate': random.randint(60, 120),
            'spo2': random.randint(95, 100),
            'temp_skin': round(random.uniform(36.0, 37.5), 1)
        }
        
        logger.info(f"Generated test data: {test_data}")
        
        # Simulate the same processing as the real endpoint
        # This helps test the data flow without real hardware
        
        return jsonify({
            'message': 'Test endpoint working',
            'test_data': test_data,
            'note': 'This is test data. Use /receive for real ESP32 data.',
            'database_info': {
                'reading_table_structure': 'device_id, metric_id, ts, value, quality_flag',
                'metric_ids': {
                    'heart_rate': 1,
                    'spo2': 2, 
                    'temp_skin': 3
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        return jsonify({'error': 'Test endpoint error'}), 500

@bp.route('/alerts', methods=['GET'])
@medic_role_required
def get_telemetry_alerts():
    """Get current telemetry alerts for medic"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get readings that exceed normal ranges
        query = """
            SELECT 
                r.reading_id,
                d.device_id,
                d.device_name,
                p.patient_id,
                CONCAT(p.first_name, ' ', p.last_name) as patient_name,
                r.heart_rate,
                r.spo2,
                r.temp_skin,
                r.timestamp,
                CASE 
                    WHEN r.heart_rate > 120 OR r.heart_rate < 50 THEN 'Critical Heart Rate'
                    WHEN r.spo2 < 90 THEN 'Low Oxygen'
                    WHEN r.temp_skin > 38 OR r.temp_skin < 35 THEN 'Temperature Alert'
                    ELSE 'Normal'
                END as alert_type
            FROM reading r
            JOIN device d ON r.device_id = d.device_id
            LEFT JOIN patient p ON d.patient_id = p.patient_id
            WHERE (r.heart_rate > 120 OR r.heart_rate < 50 OR r.spo2 < 90 OR r.temp_skin > 38 OR r.temp_skin < 35)
            AND r.timestamp >= %s
            ORDER BY r.timestamp DESC
            LIMIT 50
        """
        
        # Get alerts from last 24 hours
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        alerts = execute_query(current_user['role'], query, (yesterday,))
        
        return jsonify({
            'alerts': alerts,
            'total_alerts': len(alerts),
            'critical_count': len([a for a in alerts if 'Critical' in a['alert_type']]),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting telemetry alerts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/polling/start', methods=['POST'])
@login_required
def start_polling():
    """Start telemetry polling"""
    try:
        if is_polling_active():
            return jsonify({'message': 'Polling already active', 'status': 'active'}), 200
        
        start_telemetry_polling()
        return jsonify({'message': 'Telemetry polling started', 'status': 'started'}), 200
        
    except Exception as e:
        logger.error(f"Error starting polling: {str(e)}")
        return jsonify({'error': 'Failed to start polling'}), 500

@bp.route('/polling/stop', methods=['POST'])
@login_required
def stop_polling():
    """Stop telemetry polling"""
    try:
        stop_telemetry_polling()
        return jsonify({'message': 'Telemetry polling stopped', 'status': 'stopped'}), 200
        
    except Exception as e:
        logger.error(f"Error stopping polling: {str(e)}")
        return jsonify({'error': 'Failed to stop polling'}), 500

@bp.route('/polling/status', methods=['GET'])
@login_required
def polling_status():
    """Get telemetry polling status"""
    try:
        return jsonify({
            'polling_active': is_polling_active(),
            'status': 'active' if is_polling_active() else 'inactive'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting polling status: {str(e)}")
        return jsonify({'error': 'Failed to get polling status'}), 500
