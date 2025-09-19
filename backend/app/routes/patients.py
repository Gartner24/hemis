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