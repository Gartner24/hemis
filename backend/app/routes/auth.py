"""
Authentication routes for HEMIS
Handles login, logout, and user authentication
"""

from flask import Blueprint, request, jsonify, session
from ..auth.auth_service import AuthService, login_required
from ..db.connection import execute_query
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('auth', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Authenticate user
        user_data = AuthService.authenticate_user(email, password)
        
        if not user_data:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create user session
        session_token = AuthService.create_user_session(user_data)
        
        # Get user's primary role for database connection
        primary_role = user_data['roles'][0] if user_data['roles'] else 'doctor'
        
        logger.info(f"User {email} logged in successfully with role: {primary_role}")
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user_data['id'],
                'email': user_data['email'],
                'full_name': user_data['full_name'],
                'roles': user_data['roles'],
                'primary_role': primary_role
            },
            'session_token': session_token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout endpoint"""
    try:
        user_email = session.get('email', 'Unknown')
        AuthService.logout_user()
        
        logger.info(f"User {user_email} logged out successfully")
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user information"""
    try:
        # Check if user is authenticated first
        if not AuthService.is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        user = AuthService.get_current_user()
        
        if not user:
            logger.error("get_current_user: No user data returned from AuthService")
            return jsonify({'error': 'User not found'}), 404
        
        logger.info(f"get_current_user: Processing user {user.get('user_id')} with role {user.get('role')}")
        
        # Get additional user details from database
        # Map session roles to database users with proper fallbacks
        session_role = user.get('role', 'doctor')
        
        # Map session roles to database users
        role_to_db_user = {
            'doctor': 'doctor',
            'nurse': 'nurse', 
            'admin_medical': 'admin_medical',
            'admin_hr': 'admin_hr',
            'admin_finance': 'admin_finance',
            'admin_system': 'admin_system',
            'coordinator': 'coordinator',
            'reception': 'reception'
        }
        
        # Use mapped database user, fallback to doctor, then super_admin
        db_user = role_to_db_user.get(session_role, 'doctor')
        
        logger.info(f"get_current_user: Using database user '{db_user}' for session role '{session_role}'")
        
        query = """
            SELECT u.id, u.email, u.full_name, u.active,
                   GROUP_CONCAT(r.name) as roles
            FROM user u
            JOIN user_role ur ON u.id = ur.user_id
            JOIN role r ON ur.role_id = r.id
            WHERE u.id = %s AND u.active = 1
            GROUP BY u.id
        """
        
        # Try with mapped role first, then fallback to doctor, then super_admin
        result = None
        db_error = None
        
        for attempt_user in [db_user, 'doctor', 'super_admin']:
            try:
                logger.info(f"get_current_user: Attempting database query with user '{attempt_user}'")
                result = execute_query(attempt_user, query, (user['user_id'],))
                if result:
                    logger.info(f"get_current_user: Successfully queried with user '{attempt_user}'")
                    break
            except Exception as e:
                db_error = e
                logger.warning(f"get_current_user: Failed with user '{attempt_user}': {str(e)}")
                continue
        
        if not result:
            logger.error(f"get_current_user: All database attempts failed. Last error: {str(db_error)}")
            return jsonify({'error': 'Database connection failed'}), 500
        
        if not result:
            logger.error(f"get_current_user: No database result for user {user['user_id']}")
            return jsonify({'error': 'User not found'}), 404
        
        user_data = result[0]
        roles = user_data['roles'].split(',') if user_data['roles'] else []
        
        # Get doctor information if user is a doctor
        doctor_info = None
        if 'doctor' in roles:
            doctor_query = """
                SELECT d.id, d.license_number, d.active,
                       GROUP_CONCAT(s.name) as specialties
                FROM doctor d
                LEFT JOIN doctor_specialty ds ON d.id = ds.doctor_id
                LEFT JOIN specialty s ON ds.specialty_id = s.id
                WHERE d.user_id = %s
                GROUP BY d.id
            """
            
            # Use the same database user that worked for the main query
            doctor_result = None
            for attempt_user in [db_user, 'doctor', 'super_admin']:
                try:
                    doctor_result = execute_query(attempt_user, doctor_query, (user['user_id'],))
                    if doctor_result:
                        break
                except Exception as e:
                    logger.warning(f"get_current_user: Doctor query failed with user '{attempt_user}': {str(e)}")
                    continue
            
            if doctor_result:
                doctor_data = doctor_result[0]
                doctor_info = {
                    'id': doctor_data['id'],
                    'license_number': doctor_data['license_number'],
                    'active': doctor_data['active'],
                    'specialties': doctor_data['specialties'].split(',') if doctor_data['specialties'] else []
                }
        
        return jsonify({
            'user': {
                'id': user_data['id'],
                'email': user_data['email'],
                'full_name': user_data['full_name'],
                'roles': roles,
                'active': user_data['active'],
                'doctor_info': doctor_info
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/validate', methods=['GET'])
def validate_session():
    """Validate current session"""
    try:
        if not AuthService.is_authenticated():
            return jsonify({'authenticated': False}), 401
        
        if not AuthService.validate_session():
            return jsonify({'authenticated': False, 'error': 'Session expired'}), 401
        
        # Refresh session
        AuthService.refresh_session()
        
        return jsonify({'authenticated': True}), 200
        
    except Exception as e:
        logger.error(f"Session validation error: {str(e)}")
        return jsonify({'authenticated': False, 'error': 'Internal server error'}), 500

@bp.route('/roles', methods=['GET'])
@login_required
def get_user_roles():
    """Get current user's roles and permissions"""
    try:
        user = AuthService.get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        roles = user.get('roles', [])
        
        # Get role descriptions and permissions
        role_info = []
        for role in roles:
            from ..auth.role_permissions import RolePermissions
            
            role_data = {
                'name': role,
                'description': RolePermissions.get_role_description(role),
                'permissions': [perm.value for perm in RolePermissions.get_role_permissions(role)],
                'database_tables': RolePermissions.get_role_database_tables(role),
                'restrictions': RolePermissions.get_role_restrictions(role)
            }
            role_info.append(role_data)
        
        return jsonify({
            'roles': role_info,
            'primary_role': roles[0] if roles else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user roles: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
