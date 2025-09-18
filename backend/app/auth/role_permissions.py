"""
Role-based Access Control for HEMIS
Based on actual database permissions defined in users.sql
"""

from typing import Dict, List, Set, Any, Optional
from enum import Enum

class Permission(Enum):
    """Available permissions based on actual database GRANT statements"""
    # Patient permissions
    VIEW_PATIENTS = "view_patients"
    EDIT_PATIENTS = "edit_patients"
    DELETE_PATIENTS = "delete_patients"
    
    # Medical records permissions
    VIEW_MEDICAL_RECORDS = "view_medical_records"
    EDIT_MEDICAL_RECORDS = "edit_medical_records"
    
    # IoT/Telemetry permissions (based on device, metric, reading tables)
    VIEW_DEVICES = "view_devices"
    VIEW_METRICS = "view_metrics"
    VIEW_READINGS = "view_readings"
    VIEW_INCIDENTS = "view_incidents"
    MANAGE_DEVICES = "manage_devices"
    MANAGE_METRICS = "manage_metrics"
    MANAGE_READINGS = "manage_readings"
    MANAGE_INCIDENTS = "manage_incidents"
    
    # Appointment permissions
    VIEW_APPOINTMENTS = "view_appointments"
    EDIT_APPOINTMENTS = "edit_appointments"
    DELETE_APPOINTMENTS = "delete_appointments"
    
    # User management permissions
    VIEW_USERS = "view_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    
    # Financial permissions
    VIEW_FINANCIAL_DATA = "view_financial_data"
    EDIT_FINANCIAL_DATA = "edit_financial_data"
    
    # HR permissions
    VIEW_HR_DATA = "view_hr_data"
    EDIT_HR_DATA = "edit_hr_data"
    
    # System permissions
    VIEW_SYSTEM_CONFIG = "view_system_config"
    EDIT_SYSTEM_CONFIG = "edit_system_config"

class RolePermissions:
    """Manages role-based permissions based on actual database GRANT statements"""
    
    # Define permissions for each role based on users.sql
    ROLE_PERMISSIONS = {
        'super_admin': {
            'permissions': [
                # Full access to all tables (based on users.sql)
                Permission.VIEW_PATIENTS, Permission.EDIT_PATIENTS, Permission.DELETE_PATIENTS,
                Permission.VIEW_MEDICAL_RECORDS, Permission.EDIT_MEDICAL_RECORDS,
                Permission.VIEW_DEVICES, Permission.VIEW_METRICS, Permission.VIEW_READINGS, Permission.VIEW_INCIDENTS,
                Permission.MANAGE_DEVICES, Permission.MANAGE_METRICS, Permission.MANAGE_READINGS, Permission.MANAGE_INCIDENTS,
                Permission.VIEW_APPOINTMENTS, Permission.EDIT_APPOINTMENTS, Permission.DELETE_APPOINTMENTS,
                Permission.VIEW_USERS, Permission.EDIT_USERS, Permission.DELETE_USERS,
                Permission.VIEW_FINANCIAL_DATA, Permission.EDIT_FINANCIAL_DATA,
                Permission.VIEW_HR_DATA, Permission.EDIT_HR_DATA
            ],
            'description': 'Full access to all system features and data',
            'database_tables': {
                'full_access': ['*']  # All tables
            }
        },
        
        'admin_hr': {
            'permissions': [
                # Based on users.sql GRANT statements
                Permission.VIEW_USERS, Permission.EDIT_USERS, Permission.DELETE_USERS,
                Permission.VIEW_HR_DATA, Permission.EDIT_HR_DATA,
                Permission.VIEW_PATIENTS,  # Basic patient info for HR purposes
                Permission.VIEW_DEVICES, Permission.VIEW_METRICS, Permission.VIEW_READINGS,  # Equipment monitoring
                Permission.VIEW_APPOINTMENTS  # For scheduling purposes
            ],
            'description': 'Human Resources management and user administration',
            'database_tables': {
                'full_access': ['user', 'user_role', 'doctor', 'doctor_specialty', 'doctor_schedule', 'doctor_absence'],
                'read_only': ['patient', 'patient_insurer', 'identification_type', 'insurer', 'room', 'equipment_type', 'equipment', 'room_equipment', 'appointment_status', 'appointment_type', 'triage_priority', 'appointment', 'appointment_status_history', 'appointment_equipment', 'appointment_note', 'diagnosis_icd10']
            }
        },
        
        'admin_medical': {
            'permissions': [
                # Based on users.sql GRANT statements
                Permission.VIEW_PATIENTS, Permission.EDIT_PATIENTS,
                Permission.VIEW_MEDICAL_RECORDS, Permission.EDIT_MEDICAL_RECORDS,
                Permission.VIEW_DEVICES, Permission.VIEW_METRICS, Permission.VIEW_READINGS, Permission.VIEW_INCIDENTS,
                Permission.VIEW_APPOINTMENTS, Permission.EDIT_APPOINTMENTS, Permission.DELETE_APPOINTMENTS,
                Permission.VIEW_USERS, Permission.EDIT_USERS,  # Can manage medical staff
                Permission.VIEW_FINANCIAL_DATA  # Read-only for billing purposes
            ],
            'description': 'Medical administration and doctor management',
            'database_tables': {
                'full_access': ['specialty', 'doctor', 'doctor_specialty', 'doctor_schedule', 'doctor_absence', 'appointment_status', 'appointment_type', 'triage_priority', 'appointment', 'appointment_note', 'diagnosis_icd10', 'appointment_diagnosis', 'prescription'],
                'read_only': ['patient', 'patient_insurer', 'identification_type', 'insurer', 'room', 'equipment_type', 'equipment', 'room_equipment', 'device', 'metric', 'reading', 'rule', 'incident', 'payment_status', 'appointment_invoice']
            }
        },
        
        'admin_finance': {
            'permissions': [
                # Based on users.sql GRANT statements
                Permission.VIEW_FINANCIAL_DATA, Permission.EDIT_FINANCIAL_DATA,
                Permission.VIEW_PATIENTS,  # For billing purposes
                Permission.VIEW_APPOINTMENTS  # For billing purposes
            ],
            'description': 'Financial management and billing',
            'database_tables': {
                'full_access': ['insurer', 'patient_insurer', 'payment_status', 'appointment_invoice'],
                'read_only': ['patient', 'doctor', 'appointment_status', 'appointment', 'appointment_status_history', 'identification_type']
            }
        },
        
        'admin_system': {
            'permissions': [
                # Based on users.sql GRANT statements
                Permission.VIEW_SYSTEM_CONFIG, Permission.EDIT_SYSTEM_CONFIG,
                Permission.MANAGE_DEVICES, Permission.MANAGE_METRICS, Permission.MANAGE_READINGS, Permission.MANAGE_INCIDENTS,
                Permission.VIEW_USERS, Permission.EDIT_USERS, Permission.DELETE_USERS
            ],
            'description': 'Technical system administration and equipment management',
            'database_tables': {
                'full_access': ['identification_type', 'role', 'user', 'user_role', 'device', 'metric', 'reading', 'rule', 'rule_assignment', 'incident'],
                'read_only': ['patient', 'appointment', 'appointment_status_history']
            }
        },
        
        'doctor': {  # MEDIC ROLE - PRIMARY FOCUS
            'permissions': [
                # Based on users.sql GRANT statements
                Permission.VIEW_PATIENTS, Permission.EDIT_PATIENTS,  # Can view and edit assigned patients
                Permission.VIEW_MEDICAL_RECORDS, Permission.EDIT_MEDICAL_RECORDS,  # Full medical record access
                Permission.VIEW_DEVICES, Permission.VIEW_METRICS, Permission.VIEW_READINGS, Permission.VIEW_INCIDENTS,  # IoT monitoring
                Permission.VIEW_APPOINTMENTS, Permission.EDIT_APPOINTMENTS, Permission.DELETE_APPOINTMENTS,  # Full appointment management
                Permission.VIEW_FINANCIAL_DATA  # Read-only for patient billing info
            ],
            'description': 'Medical professional with patient care and IoT monitoring access',
            'database_tables': {
                'full_access': ['patient', 'appointment', 'appointment_note', 'appointment_diagnosis', 'prescription'],
                'read_only': ['identification_type', 'insurer', 'patient_insurer', 'specialty', 'doctor', 'doctor_specialty', 'doctor_schedule', 'doctor_absence', 'room', 'appointment_status', 'appointment_type', 'triage_priority', 'appointment_status_history', 'device', 'metric', 'reading', 'incident']
            },
            'restrictions': {
                'patients': 'assigned_only',  # Can only see assigned patients
                'telemetry': 'patient_data_only'  # Can only see patient telemetry
            }
        },
        
        'nurse': {
            'permissions': [
                # Based on users.sql GRANT statements
                Permission.VIEW_PATIENTS, Permission.EDIT_PATIENTS,  # Can view and edit assigned patients
                Permission.VIEW_MEDICAL_RECORDS,  # Can view medical records
                Permission.VIEW_DEVICES, Permission.VIEW_METRICS, Permission.VIEW_READINGS, Permission.VIEW_INCIDENTS,  # IoT monitoring
                Permission.VIEW_APPOINTMENTS, Permission.EDIT_APPOINTMENTS,  # Can view and update appointments
                Permission.VIEW_FINANCIAL_DATA  # Read-only for patient info
            ],
            'description': 'Nursing staff with patient care and IoT monitoring access',
            'database_tables': {
                'full_access': ['patient', 'appointment', 'appointment_note'],
                'read_only': ['identification_type', 'insurer', 'patient_insurer', 'specialty', 'doctor', 'doctor_specialty', 'room', 'appointment_status', 'appointment_type', 'triage_priority', 'appointment_status_history', 'appointment_diagnosis', 'prescription', 'device', 'metric', 'reading', 'incident']
            },
            'restrictions': {
                'patients': 'assigned_only',
                'telemetry': 'patient_data_only'
            }
        },
        
        'reception': {
            'permissions': [
                # Based on users.sql GRANT statements
                Permission.VIEW_PATIENTS, Permission.EDIT_PATIENTS, Permission.DELETE_PATIENTS,  # Full patient management
                Permission.VIEW_APPOINTMENTS, Permission.EDIT_APPOINTMENTS, Permission.DELETE_APPOINTMENTS,  # Full appointment management
                Permission.VIEW_FINANCIAL_DATA  # Read-only for billing purposes
            ],
            'description': 'Reception staff with patient and appointment management',
            'database_tables': {
                'full_access': ['patient', 'patient_insurer', 'appointment', 'appointment_equipment', 'appointment_invoice'],
                'read_only': ['identification_type', 'insurer', 'specialty', 'doctor', 'doctor_specialty', 'doctor_schedule', 'doctor_absence', 'room', 'equipment_type', 'equipment', 'room_equipment', 'appointment_status', 'appointment_type', 'triage_priority', 'appointment_status_history']
            },
            'restrictions': {
                'patients': 'basic_info_only',
                'medical_records': 'no_access',  # Cannot see medical records
                'telemetry': 'no_access'  # Cannot see IoT data
            }
        },
        
        'coordinator': {
            'permissions': [
                # Based on users.sql GRANT statements
                Permission.VIEW_PATIENTS,  # Can view all patients
                Permission.VIEW_MEDICAL_RECORDS,  # Can view medical records
                Permission.VIEW_DEVICES, Permission.VIEW_INCIDENTS,  # Can monitor equipment and incidents
                Permission.VIEW_APPOINTMENTS, Permission.EDIT_APPOINTMENTS, Permission.DELETE_APPOINTMENTS,  # Full appointment management
                Permission.VIEW_USERS, Permission.EDIT_USERS,  # Can manage medical staff schedules
                Permission.VIEW_FINANCIAL_DATA  # Read-only for coordination purposes
            ],
            'description': 'Medical coordination and doctor management',
            'database_tables': {
                'full_access': ['doctor_schedule', 'doctor_absence', 'room', 'appointment', 'appointment_equipment'],
                'read_only': ['patient', 'patient_insurer', 'identification_type', 'insurer', 'specialty', 'doctor', 'doctor_specialty', 'equipment_type', 'equipment', 'room_equipment', 'appointment_status', 'appointment_type', 'triage_priority', 'appointment_status_history', 'appointment_note', 'diagnosis_icd10', 'appointment_diagnosis', 'incident']
            },
            'restrictions': {
                'users': 'medical_staff_only',
                'telemetry': 'limited_access'  # Can see incidents but not detailed readings
            }
        }
    }
    
    @classmethod
    def get_role_permissions(cls, role: str) -> Set[Permission]:
        """Get permissions for a specific role"""
        role_data = cls.ROLE_PERMISSIONS.get(role, {})
        return set(role_data.get('permissions', []))
    
    @classmethod
    def get_role_description(cls, role: str) -> str:
        """Get description for a specific role"""
        role_data = cls.ROLE_PERMISSIONS.get(role, {})
        return role_data.get('description', 'Unknown role')
    
    @classmethod
    def get_role_database_tables(cls, role: str) -> Dict[str, List[str]]:
        """Get database table access for a specific role"""
        role_data = cls.ROLE_PERMISSIONS.get(role, {})
        return role_data.get('database_tables', {})
    
    @classmethod
    def get_role_restrictions(cls, role: str) -> Dict[str, Any]:
        """Get restrictions for a specific role"""
        role_data = cls.ROLE_PERMISSIONS.get(role, {})
        return role_data.get('restrictions', {})
    
    @classmethod
    def has_permission(cls, role: str, permission: Permission) -> bool:
        """Check if a role has a specific permission"""
        role_permissions = cls.get_role_permissions(role)
        return permission in role_permissions
    
    @classmethod
    def can_access_table(cls, role: str, table_name: str, operation: str = 'SELECT') -> bool:
        """Check if a role can access a specific table with specific operation"""
        role_data = cls.ROLE_PERMISSIONS.get(role, {})
        database_tables = role_data.get('database_tables', {})
        
        # Super admin has access to everything
        if role == 'super_admin':
            return True
        
        # Check full access tables
        full_access = database_tables.get('full_access', [])
        if table_name in full_access:
            return True
        
        # Check read-only tables
        read_only = database_tables.get('read_only', [])
        if table_name in read_only and operation.upper() == 'SELECT':
            return True
        
        return False
    
    @classmethod
    def can_access_patient(cls, role: str, patient_id: int, assigned_doctor_id: Optional[int] = None) -> bool:
        """Check if a role can access a specific patient"""
        if cls.has_permission(role, Permission.VIEW_PATIENTS):
            restrictions = cls.get_role_restrictions(role)
            
            # Super admin and medical admins can access all patients
            if role in ['super_admin', 'admin_medical', 'coordinator']:
                return True
            
            # Doctors and nurses can only access assigned patients
            if role in ['doctor', 'nurse'] and restrictions.get('patients') == 'assigned_only':
                return assigned_doctor_id is not None
            
            # Reception can access basic patient info
            if role == 'reception' and restrictions.get('patients') == 'basic_info_only':
                return True
                
        return False
    
    @classmethod
    def can_access_telemetry(cls, role: str, patient_id: Optional[int] = None) -> bool:
        """Check if a role can access telemetry data"""
        if cls.has_permission(role, Permission.VIEW_DEVICES) or cls.has_permission(role, Permission.VIEW_READINGS):
            restrictions = cls.get_role_restrictions(role)
            
            # System admins can access all telemetry
            if role == 'admin_system':
                return True
            
            # Medical roles can access patient telemetry
            if role in ['doctor', 'nurse', 'admin_medical', 'coordinator']:
                return patient_id is not None
                
        return False
    
    @classmethod
    def can_simulate_vital_signs(cls, role: str) -> bool:
        """Check if a role can simulate vital signs (based on device management permissions)"""
        return cls.has_permission(role, Permission.MANAGE_DEVICES) or role == 'super_admin'
    
    @classmethod
    def get_accessible_roles(cls, current_role: str) -> List[str]:
        """Get list of roles that the current role can manage"""
        if current_role == 'super_admin':
            return list(cls.ROLE_PERMISSIONS.keys())
        elif current_role == 'admin_hr':
            return ['nurse', 'reception', 'doctor']
        elif current_role == 'admin_medical':
            return ['doctor', 'nurse', 'coordinator']
        elif current_role == 'coordinator':
            return ['doctor', 'nurse']
        else:
            return []

def check_permission(role: str, permission: Permission) -> bool:
    """Convenience function to check permissions"""
    return RolePermissions.has_permission(role, permission)

def check_table_access(role: str, table_name: str, operation: str = 'SELECT') -> bool:
    """Convenience function to check table access"""
    return RolePermissions.can_access_table(role, table_name, operation)

def check_patient_access(role: str, patient_id: int, assigned_doctor_id: Optional[int] = None) -> bool:
    """Convenience function to check patient access"""
    return RolePermissions.can_access_patient(role, patient_id, assigned_doctor_id)

def check_telemetry_access(role: str, patient_id: Optional[int] = None) -> bool:
    """Convenience function to check telemetry access"""
    return RolePermissions.can_access_telemetry(role, patient_id)
