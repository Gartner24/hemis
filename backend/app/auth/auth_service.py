"""
Authentication Service for HEMIS
Handles cookie-based authentication and session management
"""

import hashlib
import secrets
import time
import logging
from typing import Optional, Dict, Any
from flask import request, session, current_app
from ..db.connection import execute_query

logger = logging.getLogger(__name__)
from .role_permissions import RolePermissions

class AuthService:
    """Handles user authentication and session management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using scrypt (matching seed.sql)"""
        import hashlib
        # For development, use simple hash to match seed.sql
        # In production, use proper scrypt with salt
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return AuthService.hash_password(password) == hashed_password
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email and password"""
        try:
            # Query user from database (using default connection for auth)
            query = """
                SELECT u.id, u.email, u.full_name, u.password_hash, u.active,
                       GROUP_CONCAT(r.name) as roles
                FROM user u
                JOIN user_role ur ON u.id = ur.user_id
                JOIN role r ON ur.role_id = r.id
                WHERE u.email = %s AND u.active = 1
                GROUP BY u.id
            """
            
            # For authentication, we can use any role that has access to user table
            # Let's try doctor first, then fallback to super_admin
            try:
                result = execute_query('doctor', query, (email,))
            except:
                # Fallback to super_admin if doctor role fails
                result = execute_query('super_admin', query, (email,))
            
            if not result:
                return None
            
            user_data = result[0]
            stored_password_hash = user_data['password_hash']
            
            # Verify password
            if not AuthService.verify_password(password, stored_password_hash):
                return None
            
            # Parse roles
            roles = user_data['roles'].split(',') if user_data['roles'] else []
            
            return {
                'id': user_data['id'],
                'email': user_data['email'],
                'full_name': user_data['full_name'],
                'roles': roles,
                'active': user_data['active']
            }
            
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return None
    
    @staticmethod
    def create_user_session(user_data: Dict[str, Any]) -> str:
        """Create a user session and return session token"""
        session_token = AuthService.generate_session_token()
        
        # Store user data in session
        session['user_id'] = user_data['id']
        session['email'] = user_data['email']
        session['full_name'] = user_data['full_name']
        session['roles'] = user_data['roles']
        session['session_token'] = session_token
        session['created_at'] = time.time()
        
        # Make session permanent for better persistence
        session.permanent = True
        
        return session_token
    
    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get current authenticated user from session"""
        if not session.get('user_id'):
            return None
        
        # Validate session data integrity
        required_fields = ['user_id', 'email', 'full_name', 'roles']
        for field in required_fields:
            if not session.get(field):
                # Session data is corrupted, clear it
                logger.warning(f"Session data corrupted - missing {field}, clearing session")
                AuthService.logout_user()
                return None
        
        return {
            'user_id': session.get('user_id'),
            'email': session.get('email'),
            'full_name': session.get('full_name'),
            'roles': session.get('roles', []),
            'role': session.get('roles', [])[0] if session.get('roles') else None,
            'session_token': session.get('session_token')
        }
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return session.get('user_id') is not None
    
    @staticmethod
    def has_role(role: str) -> bool:
        """Check if current user has a specific role"""
        user = AuthService.get_current_user()
        if not user:
            return False
        
        return role in user.get('roles', [])
    
    @staticmethod
    def has_any_role(roles: list) -> bool:
        """Check if current user has any of the specified roles"""
        user = AuthService.get_current_user()
        if not user:
            return False
        
        user_roles = set(user.get('roles', []))
        return bool(user_roles.intersection(set(roles)))
    
    @staticmethod
    def logout_user():
        """Logout current user by clearing session"""
        session.clear()
    
    @staticmethod
    def validate_session() -> bool:
        """Validate current session"""
        user = AuthService.get_current_user()
        if not user:
            return False
        
        # Check if session is expired (24 hours)
        created_at = session.get('created_at', 0)
        if time.time() - created_at > 86400:  # 24 hours
            AuthService.logout_user()
            return False
        
        return True
    
    @staticmethod
    def refresh_session():
        """Refresh session timestamp"""
        if session.get('user_id'):
            session['created_at'] = time.time()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data by ID"""
        try:
            query = """
                SELECT u.id, u.email, u.full_name, u.active,
                       GROUP_CONCAT(r.name) as roles
                FROM user u
                JOIN user_role ur ON u.id = ur.user_id
                JOIN role r ON ur.role_id = r.id
                WHERE u.id = %s AND u.active = 1
                GROUP BY u.id
            """
            
            # Try to use the user's role, fallback to doctor
            try:
                result = execute_query('doctor', query, (user_id,))
            except:
                result = execute_query('super_admin', query, (user_id,))
            
            if not result:
                return None
            
            user_data = result[0]
            roles = user_data['roles'].split(',') if user_data['roles'] else []
            
            return {
                'id': user_data['id'],
                'email': user_data['email'],
                'full_name': user_data['full_name'],
                'roles': roles,
                'active': user_data['active']
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting user by ID: {str(e)}")
            return None

# Convenience functions
def login_required(f):
    """Decorator to require authentication"""
    from functools import wraps
    from flask import jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthService.is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(required_roles):
    """Decorator to require specific roles"""
    from functools import wraps
    from flask import jsonify
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not AuthService.is_authenticated():
                return jsonify({'error': 'Authentication required'}), 401
            
            if not AuthService.has_any_role(required_roles):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def medic_role_required(f):
    """Decorator specifically for medic role (doctor, nurse)"""
    return role_required(['doctor', 'nurse', 'admin_medical', 'coordinator'])(f)
