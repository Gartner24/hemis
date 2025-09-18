"""
User and Role models for HEMIS
Defines data structures for users, roles, and related entities
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

@dataclass
class User:
    """User model representing a system user"""
    user_id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class Role:
    """Role model representing a user role"""
    role_id: int
    role_name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert role to dictionary"""
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class UserRole:
    """User-Role relationship model"""
    user_id: int
    role_id: int
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user role to dictionary"""
        return {
            'user_id': self.user_id,
            'role_id': self.role_id,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'assigned_by': self.assigned_by
        }

@dataclass
class Doctor:
    """Doctor model representing medical staff"""
    doctor_id: int
    user_id: int
    license_number: str
    specialization: Optional[str] = None
    years_experience: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert doctor to dictionary"""
        return {
            'doctor_id': self.doctor_id,
            'user_id': self.user_id,
            'license_number': self.license_number,
            'specialization': self.specialization,
            'years_experience': self.years_experience,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class Patient:
    """Patient model representing hospital patients"""
    patient_id: int
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    assigned_doctor_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def full_name(self) -> str:
        """Get patient's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> Optional[int]:
        """Calculate patient's age"""
        if self.date_of_birth:
            today = datetime.now()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert patient to dictionary"""
        return {
            'patient_id': self.patient_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'blood_type': self.blood_type,
            'allergies': self.allergies,
            'medical_history': self.medical_history,
            'assigned_doctor_id': self.assigned_doctor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class Nurse:
    """Nurse model representing nursing staff"""
    nurse_id: int
    user_id: int
    license_number: str
    department: Optional[str] = None
    shift: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert nurse to dictionary"""
        return {
            'nurse_id': self.nurse_id,
            'user_id': self.user_id,
            'license_number': self.license_number,
            'department': self.department,
            'shift': self.shift,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Factory functions for creating model instances from database rows
def create_user_from_db(row: Dict[str, Any]) -> User:
    """Create User instance from database row"""
    return User(
        user_id=row['user_id'],
        email=row['email'],
        first_name=row['first_name'],
        last_name=row['last_name'],
        phone=row.get('phone'),
        is_active=row.get('is_active', True),
        created_at=parse_datetime(row.get('created_at')),
        updated_at=parse_datetime(row.get('updated_at'))
    )

def create_patient_from_db(row: Dict[str, Any]) -> Patient:
    """Create Patient instance from database row"""
    return Patient(
        patient_id=row['patient_id'],
        first_name=row['first_name'],
        last_name=row['last_name'],
        date_of_birth=parse_datetime(row.get('date_of_birth')),
        gender=row.get('gender'),
        phone=row.get('phone'),
        email=row.get('email'),
        address=row.get('address'),
        emergency_contact=row.get('emergency_contact'),
        blood_type=row.get('blood_type'),
        allergies=row.get('allergies'),
        medical_history=row.get('medical_history'),
        assigned_doctor_id=row.get('assigned_doctor_id'),
        created_at=parse_datetime(row.get('created_at')),
        updated_at=parse_datetime(row.get('updated_at'))
    )

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse datetime string to datetime object"""
    if not dt_str:
        return None
    try:
        if 'T' in dt_str:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        else:
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None
