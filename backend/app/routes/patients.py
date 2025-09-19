"""
Patient Management API endpoints
Provides patient data access and management for medic role
"""

from flask import Blueprint, request, jsonify, current_app
from ..auth.auth_service import medic_role_required, login_required, AuthService
from ..db.connection import execute_query
from ..models.user_models import Patient
import logging
from datetime import datetime
import json

bp = Blueprint('patients', __name__)
logger = logging.getLogger(__name__)

@bp.route('/', methods=['GET'])
@medic_role_required
def get_patients():
    """Get list of patients accessible to the current medic"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get query parameters
        search = request.args.get('search', '')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 patients
        offset = int(request.args.get('offset', 0))
        
        # Build query based on user role and search
        base_query = """
            SELECT 
                p.id as patient_id,
                p.full_name,
                p.birth_date,
                p.sex as gender,
                p.phone,
                p.email,
                p.allergies,
                p.emergency_contact,
                p.ident_number as medical_record_number,
                YEAR(CURDATE()) - YEAR(p.birth_date) as age,
                'active' as status,
                '101' as room_number,
                NOW() as admission_date,
                d.id as device_id,
                d.label as device_name,
                d.active as device_status
            FROM patient p
            LEFT JOIN device d ON p.id = d.patient_id AND d.active = 1
        """
        
        where_conditions = []
        params = []
        
        # Add search conditions
        if search:
            where_conditions.append("""
                (p.full_name LIKE %s OR p.email LIKE %s OR p.phone LIKE %s OR p.ident_number LIKE %s)
            """)
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        # Add role-based restrictions
        if current_user['role'] in ['doctor', 'nurse']:
            # Doctors and nurses can only see assigned patients
            where_conditions.append("p.id IN (SELECT patient_id FROM device WHERE patient_id IS NOT NULL)")
        elif current_user['role'] == 'admin_medical':
            # Medical admins can see all patients
            pass
        elif current_user['role'] == 'coordinator':
            # Coordinators can see all patients but with limited info
            pass
        
        # Combine query
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        # Add ordering and pagination
        base_query += """
            ORDER BY p.full_name
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        # Execute query
        patients = execute_query(current_user['role'], base_query, tuple(params))
        
        # Get total count for pagination
        count_query = """
            SELECT COUNT(*) as total
            FROM patient p
        """
        if where_conditions:
            count_query += " WHERE " + " AND ".join(where_conditions)
            count_params = params[:-2]  # Remove limit and offset
        else:
            count_params = []
        
        count_result = execute_query(current_user['role'], count_query, tuple(count_params))
        total_count = count_result[0]['total'] if count_result else 0
        
        return jsonify({
            'patients': patients,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting patients: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:patient_id>', methods=['GET'])
@medic_role_required
def get_patient(patient_id):
    """Get detailed information for a specific patient"""
    try:
        
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Check if user can access this patient
        from ..auth.role_permissions import RolePermissions
        if not RolePermissions.can_access_patient(current_user['role'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403
        
        # Get patient details
        query = """
            SELECT 
                p.patient_id,
                p.first_name,
                p.last_name,
                p.date_of_birth,
                p.gender,
                p.phone,
                p.email,
                p.address,
                p.emergency_contact,
                p.blood_type,
                p.allergies,
                p.medical_history,
                p.created_at,
                p.updated_at,
                d.doctor_id,
                CONCAT(d.first_name, ' ', d.last_name) as assigned_doctor,
                ds.specialty_name,
                i.insurer_name,
                pi.policy_number
            FROM patient p
            LEFT JOIN doctor d ON p.assigned_doctor_id = d.doctor_id
            LEFT JOIN doctor_specialty ds ON d.doctor_id = ds.doctor_id
            LEFT JOIN patient_insurer pi ON p.patient_id = pi.patient_id
            LEFT JOIN insurer i ON pi.insurer_id = i.insurer_id
            WHERE p.patient_id = %s
        """
        
        result = execute_query(current_user['role'], query, (patient_id,))
        
        if not result:
            return jsonify({'error': 'Patient not found'}), 404
        
        patient = result[0]
        
        # Get patient's recent appointments
        appointments_query = """
            SELECT 
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.status,
                at.appointment_type_name,
                tp.priority_name,
                CONCAT(d.first_name, ' ', d.last_name) as doctor_name
            FROM appointment a
            LEFT JOIN appointment_type at ON a.appointment_type_id = at.appointment_type_id
            LEFT JOIN triage_priority tp ON a.triage_priority_id = tp.triage_priority_id
            LEFT JOIN doctor d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            LIMIT 10
        """
        
        appointments = execute_query(current_user['role'], appointments_query, (patient_id,))
        
        # Get patient's assigned devices
        devices_query = """
            SELECT 
                d.device_id,
                d.device_name,
                d.device_type,
                d.status,
                d.last_reading_time
            FROM device d
            WHERE d.patient_id = %s
            ORDER BY d.device_id
        """
        
        devices = execute_query(current_user['role'], devices_query, (patient_id,))
        
        return jsonify({
            'patient': patient,
            'recent_appointments': appointments,
            'assigned_devices': devices,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:patient_id>/vital-signs', methods=['GET'])
@medic_role_required
def get_patient_vital_signs(patient_id):
    """Get vital signs history for a specific patient"""
    try:
        
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Check access
        from ..auth.role_permissions import RolePermissions
        if not RolePermissions.can_access_patient(current_user['role'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403
        
        # Get query parameters
        hours = int(request.args.get('hours', 24))  # Default to last 24 hours
        limit = min(int(request.args.get('limit', 100)), 500)  # Max 500 readings
        
        # Get vital signs readings
        query = """
            SELECT 
                r.reading_id,
                r.heart_rate,
                r.spo2,
                r.temp_skin,
                r.timestamp,
                r.is_simulated,
                d.device_id,
                d.device_name
            FROM reading r
            JOIN device d ON r.device_id = d.device_id
            WHERE d.patient_id = %s
            AND r.timestamp >= %s
            ORDER BY r.timestamp DESC
            LIMIT %s
        """
        
        # Calculate time range
        from datetime import timedelta
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        readings = execute_query(current_user['role'], query, (patient_id, start_time, limit))
        
        # Calculate vital signs statistics
        if readings:
            heart_rates = [r['heart_rate'] for r in readings if r['heart_rate'] is not None]
            spo2_values = [r['spo2'] for r in readings if r['spo2'] is not None]
            temperatures = [r['temp_skin'] for r in readings if r['temp_skin'] is not None]
            
            stats = {
                'heart_rate': {
                    'min': min(heart_rates) if heart_rates else None,
                    'max': max(heart_rates) if heart_rates else None,
                    'avg': round(sum(heart_rates) / len(heart_rates), 1) if heart_rates else None
                },
                'spo2': {
                    'min': min(spo2_values) if spo2_values else None,
                    'max': max(spo2_values) if spo2_values else None,
                    'avg': round(sum(spo2_values) / len(spo2_values), 1) if spo2_values else None
                },
                'temperature': {
                    'min': min(temperatures) if temperatures else None,
                    'max': max(temperatures) if temperatures else None,
                    'avg': round(sum(temperatures) / len(temperatures), 1) if temperatures else None
                }
            }
        else:
            stats = {}
        
        return jsonify({
            'patient_id': patient_id,
            'readings': readings,
            'statistics': stats,
            'time_range_hours': hours,
            'total_readings': len(readings),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting patient vital signs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:patient_id>/assign-device', methods=['POST'])
@medic_role_required
def assign_device_to_patient(patient_id):
    """Assign a device to a patient"""
    try:
        
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Check access
        from ..auth.role_permissions import RolePermissions
        if not RolePermissions.can_access_patient(current_user['role'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403
        
        data = request.get_json()
        if not data or 'device_id' not in data:
            return jsonify({'error': 'device_id is required'}), 400
        
        device_id = data['device_id']
        
        # Check if device is available
        device_query = """
            SELECT device_id, patient_id, status
            FROM device
            WHERE device_id = %s
        """
        
        device_result = execute_query(current_user['role'], device_query, (device_id,))
        
        if not device_result:
            return jsonify({'error': 'Device not found'}), 404
        
        device = device_result[0]
        
        if device['patient_id'] and device['patient_id'] != patient_id:
            return jsonify({'error': 'Device is already assigned to another patient'}), 400
        
        # Assign device to patient
        assign_query = """
            UPDATE device
            SET patient_id = %s, status = 'active', updated_at = %s
            WHERE device_id = %s
        """
        
        timestamp = datetime.now().isoformat()
        execute_query(current_user['role'], assign_query, (patient_id, timestamp, device_id))
        
        logger.info(f"Device {device_id} assigned to patient {patient_id} by user {current_user['user_id']}")
        
        return jsonify({
            'message': 'Device assigned successfully',
            'device_id': device_id,
            'patient_id': patient_id,
            'timestamp': timestamp
        }), 200
        
    except Exception as e:
        logger.error(f"Error assigning device: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:patient_id>/unassign-device/<int:device_id>', methods=['POST'])
@medic_role_required
def unassign_device_from_patient(patient_id, device_id):
    """Unassign a device from a patient"""
    try:
        
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Check access
        from ..auth.role_permissions import RolePermissions
        if not RolePermissions.can_access_patient(current_user['role'], patient_id):
            return jsonify({'error': 'Access denied to this patient'}), 403
        
        # Unassign device
        unassign_query = """
            UPDATE device
            SET patient_id = NULL, status = 'inactive', updated_at = %s
            WHERE device_id = %s AND patient_id = %s
        """
        
        timestamp = datetime.now().isoformat()
        result = execute_query(current_user['role'], unassign_query, (timestamp, device_id, patient_id))
        
        if not result:
            return jsonify({'error': 'Device not found or not assigned to this patient'}), 404
        
        logger.info(f"Device {device_id} unassigned from patient {patient_id} by user {current_user['user_id']}")
        
        return jsonify({
            'message': 'Device unassigned successfully',
            'device_id': device_id,
            'patient_id': patient_id,
            'timestamp': timestamp
        }), 200
        
    except Exception as e:
        logger.error(f"Error unassigning device: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/', methods=['POST'])
@medic_role_required
def create_patient():
    """Create a new patient (admin roles only)"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Only admin roles can create patients
        if current_user['role'] not in ['super_admin', 'admin_medical', 'admin_hr']:
            return jsonify({'error': 'Insufficient permissions to create patients'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['full_name', 'age', 'gender', 'room_number', 'medical_record_number']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        # Calculate birth_date from age
        from datetime import date, timedelta
        birth_date = date.today() - timedelta(days=data['age'] * 365)
        
        # Insert patient
        query = """
            INSERT INTO patient (identification_type_id, ident_number, full_name, birth_date, sex, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            1,  # Default identification type (CC)
            data['medical_record_number'],  # Use as ident_number
            data['full_name'],
            birth_date,
            data['gender'],
            data.get('phone', ''),
            data.get('email', '')
        )
        
        execute_query(current_user['role'], query, params)
        
        logger.info(f"Patient created by user {current_user['user_id']}: {data['full_name']}")
        
        return jsonify({
            'message': 'Patient created successfully',
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:patient_id>', methods=['PUT'])
@medic_role_required
def update_patient(patient_id):
    """Update an existing patient (admin roles only)"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Only admin roles can update patients
        if current_user['role'] not in ['super_admin', 'admin_medical', 'admin_hr']:
            return jsonify({'error': 'Insufficient permissions to update patients'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if patient exists
        check_query = "SELECT id FROM patient WHERE id = %s"
        patient_exists = execute_query(current_user['role'], check_query, (patient_id,))
        
        if not patient_exists:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Update patient
        update_fields = []
        params = []
        
        if 'full_name' in data:
            update_fields.append("full_name = %s")
            params.append(data['full_name'])
        
        if 'age' in data:
            from datetime import date, timedelta
            birth_date = date.today() - timedelta(days=data['age'] * 365)
            update_fields.append("birth_date = %s")
            params.append(birth_date)
        
        if 'gender' in data:
            update_fields.append("sex = %s")
            params.append(data['gender'])
        
        if 'phone' in data:
            update_fields.append("phone = %s")
            params.append(data['phone'])
        
        if 'email' in data:
            update_fields.append("email = %s")
            params.append(data['email'])
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        query = f"UPDATE patient SET {', '.join(update_fields)} WHERE id = %s"
        params.append(patient_id)
        
        execute_query(current_user['role'], query, tuple(params))
        
        logger.info(f"Patient {patient_id} updated by user {current_user['user_id']}")
        
        return jsonify({
            'message': 'Patient updated successfully',
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:patient_id>', methods=['DELETE'])
@medic_role_required
def delete_patient(patient_id):
    """Delete a patient (admin roles only)"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Only super admin can delete patients
        if current_user['role'] != 'super_admin':
            return jsonify({'error': 'Insufficient permissions to delete patients'}), 403
        
        # Check if patient exists
        check_query = "SELECT id, full_name FROM patient WHERE id = %s"
        patient_result = execute_query(current_user['role'], check_query, (patient_id,))
        
        if not patient_result:
            return jsonify({'error': 'Patient not found'}), 404
        
        patient_name = patient_result[0]['full_name']
        
        # Delete patient (cascade will handle related records)
        delete_query = "DELETE FROM patient WHERE id = %s"
        execute_query(current_user['role'], delete_query, (patient_id,))
        
        logger.info(f"Patient {patient_id} ({patient_name}) deleted by user {current_user['user_id']}")
        
        return jsonify({
            'message': 'Patient deleted successfully',
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/search', methods=['GET'])
@medic_role_required
def search_patients():
    """Search patients by various criteria"""
    try:
        
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get search parameters
        name = request.args.get('name', '')
        email = request.args.get('email', '')
        phone = request.args.get('phone', '')
        blood_type = request.args.get('blood_type', '')
        limit = min(int(request.args.get('limit', 20)), 50)
        
        if not any([name, email, phone, blood_type]):
            return jsonify({'error': 'At least one search parameter is required'}), 400
        
        # Build search query
        base_query = """
            SELECT 
                p.patient_id,
                p.first_name,
                p.last_name,
                p.date_of_birth,
                p.gender,
                p.phone,
                p.email,
                p.blood_type,
                d.doctor_id,
                CONCAT(d.first_name, ' ', d.last_name) as assigned_doctor
            FROM patient p
            LEFT JOIN doctor d ON p.assigned_doctor_id = d.doctor_id
            WHERE 1=1
        """
        
        params = []
        
        if name:
            base_query += " AND (p.first_name LIKE %s OR p.last_name LIKE %s)"
            name_param = f"%{name}%"
            params.extend([name_param, name_param])
        
        if email:
            base_query += " AND p.email LIKE %s"
            params.append(f"%{email}%")
        
        if phone:
            base_query += " AND p.phone LIKE %s"
            params.append(f"%{phone}%")
        
        if blood_type:
            base_query += " AND p.blood_type = %s"
            params.append(blood_type)
        
        # Add role-based restrictions
        if current_user['role'] in ['doctor', 'nurse']:
            base_query += " AND p.assigned_doctor_id = %s"
            params.append(current_user.get('doctor_id'))
        
        base_query += " ORDER BY p.last_name, p.first_name LIMIT %s"
        params.append(limit)
        
        patients = execute_query(current_user['role'], base_query, tuple(params))
        
        return jsonify({
            'patients': patients,
            'search_criteria': {
                'name': name,
                'email': email,
                'phone': phone,
                'blood_type': blood_type
            },
            'total_results': len(patients),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching patients: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
