"""
Vital Signs Simulation API endpoints
Provides simulation controls for testing IoT device behavior with three states
"""

from flask import Blueprint, request, jsonify, current_app
from ..auth.auth_service import medic_role_required, login_required, AuthService
from ..db.connection import execute_query
from ..models.telemetry_models import TelemetryData
import logging
from datetime import datetime, timedelta
import random
import json

bp = Blueprint('vital_signs', __name__)
logger = logging.getLogger(__name__)

# Simulation state constants
SIMULATION_STATES = {
    'normal': {
        'heart_rate': {'min': 60, 'max': 100},
        'spo2': {'min': 95, 'max': 100},
        'temp_skin': {'min': 36.0, 'max': 37.5}
    },
    'critical': {
        'heart_rate': {'min': 120, 'max': 180},
        'spo2': {'min': 70, 'max': 89},
        'temp_skin': {'min': 38.5, 'max': 42.0}
    },
    'death': {
        'heart_rate': {'min': 0, 'max': 30},
        'spo2': {'min': 0, 'max': 50},
        'temp_skin': {'min': 30.0, 'max': 35.0}
    }
}

@bp.route('/', methods=['GET'])
@medic_role_required
def get_simulation_status():
    """Get current simulation status and available states"""
    try:
        return jsonify({
            'simulation_active': True,
            'available_states': list(SIMULATION_STATES.keys()),
            'current_state': 'normal',  # Default state
            'description': 'Vital signs simulation system for testing IoT device behavior',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting simulation status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/simulate/<state>', methods=['POST'])
@medic_role_required
def simulate_vital_signs(state):
    """Simulate vital signs for a specific state (normal, critical, death)"""
    try:
        if state not in SIMULATION_STATES:
            return jsonify({
                'error': f'Invalid state. Available states: {list(SIMULATION_STATES.keys())}'
            }), 400
        
        # Get request data
        data = request.get_json() or {}
        device_id = data.get('device_id')
        patient_id = data.get('patient_id')
        duration_minutes = data.get('duration_minutes', 5)
        
        if not device_id:
            return jsonify({'error': 'device_id is required'}), 400
        
        # Generate simulated vital signs for the specified state
        vital_signs = generate_simulated_vitals(state)
        
        # Insert simulated reading into database
        query = """
            INSERT INTO reading (device_id, heart_rate, spo2, temp_skin, timestamp, is_simulated)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        timestamp = datetime.now().isoformat()
        execute_query('admin_system', query, (
            device_id,
            vital_signs['heart_rate'],
            vital_signs['spo2'],
            vital_signs['temp_skin'],
            timestamp,
            True  # Mark as simulated data
        ))
        
        # Update device status
        update_query = """
            UPDATE device 
            SET last_reading_time = %s, status = 'active'
            WHERE device_id = %s
        """
        execute_query('admin_system', update_query, (timestamp, device_id))
        
        logger.info(f"Simulated {state} state vital signs for device {device_id}: HR={vital_signs['heart_rate']}, SpO2={vital_signs['spo2']}, Temp={vital_signs['temp_skin']}")
        
        return jsonify({
            'message': f'Simulation activated for {state} state',
            'device_id': device_id,
            'patient_id': patient_id,
            'state': state,
            'vital_signs': vital_signs,
            'timestamp': timestamp,
            'duration_minutes': duration_minutes,
            'simulated': True
        }), 201
        
    except Exception as e:
        logger.error(f"Error simulating vital signs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/simulate/<state>/continuous', methods=['POST'])
@medic_role_required
def start_continuous_simulation(state):
    """Start continuous simulation for a specific state"""
    try:
        if state not in SIMULATION_STATES:
            return jsonify({
                'error': f'Invalid state. Available states: {list(SIMULATION_STATES.keys())}'
            }), 400
        
        data = request.get_json() or {}
        device_id = data.get('device_id')
        patient_id = data.get('patient_id')
        interval_seconds = data.get('interval_seconds', 30)  # Data every 30 seconds
        duration_minutes = data.get('duration_minutes', 10)
        
        if not device_id:
            return jsonify({'error': 'device_id is required'}), 400
        
        # Use the vital signs simulator service
        from ..services.vital_signs_simulator import start_device_simulation
        
        try:
            simulation_id = start_device_simulation(
                device_id=device_id,
                state=state,
                duration_minutes=duration_minutes,
                interval_seconds=interval_seconds
            )
            
            logger.info(f"Continuous simulation {simulation_id} started for {state} state on device {device_id}")
            
            return jsonify({
                'message': f'Continuous simulation started for {state} state',
                'simulation_id': simulation_id,
                'device_id': device_id,
                'patient_id': patient_id,
                'state': state,
                'interval_seconds': interval_seconds,
                'duration_minutes': duration_minutes,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as sim_error:
            logger.error(f"Error starting simulation: {str(sim_error)}")
            return jsonify({'error': f'Failed to start simulation: {str(sim_error)}'}), 500
        
    except Exception as e:
        logger.error(f"Error starting continuous simulation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/simulate/stop/<simulation_id>', methods=['POST'])
@medic_role_required
def stop_simulation(simulation_id):
    """Stop a running simulation"""
    try:
        # Use the vital signs simulator service
        from ..services.vital_signs_simulator import stop_device_simulation
        
        success = stop_device_simulation(simulation_id)
        
        if success:
            logger.info(f"Simulation {simulation_id} stopped successfully")
            return jsonify({
                'message': 'Simulation stopped successfully',
                'simulation_id': simulation_id,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': 'Simulation not found or already stopped',
                'simulation_id': simulation_id
            }), 404
        
    except Exception as e:
        logger.error(f"Error stopping simulation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/device/<int:device_id>/simulation-history', methods=['GET'])
@medic_role_required
def get_simulation_history(device_id):
    """Get simulation history for a specific device"""
    try:
        current_user = AuthService.get_current_user()
        
        if not current_user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Get simulated readings for the device
        query = """
            SELECT 
                r.reading_id,
                r.heart_rate,
                r.spo2,
                r.temp_skin,
                r.timestamp,
                r.is_simulated,
                p.patient_id,
                CONCAT(p.first_name, ' ', p.last_name) as patient_name
            FROM reading r
            LEFT JOIN device d ON r.device_id = d.device_id
            LEFT JOIN patient p ON d.patient_id = p.patient_id
            WHERE r.device_id = %s AND r.is_simulated = 1
            ORDER BY r.timestamp DESC
            LIMIT 100
        """
        
        readings = execute_query(current_user['role'], query, (device_id,))
        
        if not readings:
            return jsonify({'error': 'No simulation history found for this device'}), 404
        
        # Analyze the readings to determine simulation states
        simulation_analysis = analyze_simulation_states(readings)
        
        return jsonify({
            'device_id': device_id,
            'simulation_history': readings,
            'total_simulations': len(readings),
            'simulation_analysis': simulation_analysis,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting simulation history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/test-scenarios', methods=['GET'])
@medic_role_required
def get_test_scenarios():
    """Get available test scenarios for IoT device testing"""
    try:
        scenarios = {
            'normal_flow': {
                'name': 'Normal Patient Flow',
                'description': 'Simulate a healthy patient with normal vital signs',
                'state': 'normal',
                'duration': '5 minutes',
                'expected_behavior': 'Device should show stable readings within normal ranges'
            },
            'critical_escalation': {
                'name': 'Critical Patient Escalation',
                'description': 'Simulate patient deterioration with critical vital signs',
                'state': 'critical',
                'duration': '3 minutes',
                'expected_behavior': 'Device should trigger alerts and show warning indicators'
            },
            'cardiac_arrest': {
                'name': 'Cardiac Arrest Simulation',
                'description': 'Simulate extreme critical state (near death)',
                'state': 'death',
                'duration': '2 minutes',
                'expected_behavior': 'Device should show critical alerts and emergency indicators'
            },
            'recovery_cycle': {
                'name': 'Patient Recovery Cycle',
                'description': 'Simulate patient recovery from critical to normal',
                'sequence': ['death', 'critical', 'normal'],
                'duration': '10 minutes',
                'expected_behavior': 'Device should show gradual improvement in vital signs'
            }
        }
        
        return jsonify({
            'test_scenarios': scenarios,
            'total_scenarios': len(scenarios),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting test scenarios: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def generate_simulated_vitals(state):
    """Generate simulated vital signs for a specific state"""
    if state not in SIMULATION_STATES:
        raise ValueError(f"Invalid state: {state}")
    
    ranges = SIMULATION_STATES[state]
    
    # Generate random values within the specified ranges
    heart_rate = random.randint(ranges['heart_rate']['min'], ranges['heart_rate']['max'])
    spo2 = random.randint(ranges['spo2']['min'], ranges['spo2']['max'])
    temp_skin = round(random.uniform(ranges['temp_skin']['min'], ranges['temp_skin']['max']), 1)
    
    return {
        'heart_rate': heart_rate,
        'spo2': spo2,
        'temp_skin': temp_skin,
        'state': state,
        'simulated': True
    }

def analyze_simulation_states(readings):
    """Analyze simulation readings to determine state patterns"""
    if not readings:
        return {}
    
    analysis = {
        'total_readings': len(readings),
        'state_distribution': {},
        'vital_ranges': {
            'heart_rate': {'min': float('inf'), 'max': 0},
            'spo2': {'min': float('inf'), 'max': 0},
            'temp_skin': {'min': float('inf'), 'max': 0}
        }
    }
    
    for reading in readings:
        # Analyze heart rate patterns
        hr = reading['heart_rate']
        if hr < 50:
            state = 'bradycardia'
        elif hr > 120:
            state = 'tachycardia'
        else:
            state = 'normal'
        
        analysis['state_distribution'][state] = analysis['state_distribution'].get(state, 0) + 1
        
        # Track vital sign ranges
        analysis['vital_ranges']['heart_rate']['min'] = min(analysis['vital_ranges']['heart_rate']['min'], hr)
        analysis['vital_ranges']['heart_rate']['max'] = max(analysis['vital_ranges']['heart_rate']['max'], hr)
        
        analysis['vital_ranges']['spo2']['min'] = min(analysis['vital_ranges']['spo2']['min'], reading['spo2'])
        analysis['vital_ranges']['spo2']['max'] = max(analysis['vital_ranges']['spo2']['max'], reading['spo2'])
        
        analysis['vital_ranges']['temp_skin']['min'] = min(analysis['vital_ranges']['temp_skin']['min'], reading['temp_skin'])
        analysis['vital_ranges']['temp_skin']['max'] = max(analysis['vital_ranges']['temp_skin']['max'], reading['temp_skin'])
    
    return analysis
