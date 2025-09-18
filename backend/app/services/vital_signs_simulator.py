"""
Vital Signs Simulator Service
Generates simulated patient vital signs data for testing IoT device behavior
"""

import random
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from threading import Thread, Event
from ..db.connection import execute_query
from ..models.telemetry_models import Reading, Device

logger = logging.getLogger(__name__)

class VitalSignsSimulator:
    """Simulates vital signs data for testing purposes"""
    
    # Vital signs ranges for different states
    VITAL_SIGNS_RANGES = {
        'normal': {
            'heart_rate': {'min': 60, 'max': 100, 'trend': 'stable'},
            'spo2': {'min': 95, 'max': 100, 'trend': 'stable'},
            'temp_skin': {'min': 36.0, 'max': 37.5, 'trend': 'stable'}
        },
        'critical': {
            'heart_rate': {'min': 120, 'max': 180, 'trend': 'increasing'},
            'spo2': {'min': 70, 'max': 89, 'trend': 'decreasing'},
            'temp_skin': {'min': 38.5, 'max': 42.0, 'trend': 'increasing'}
        },
        'death': {
            'heart_rate': {'min': 0, 'max': 30, 'trend': 'decreasing'},
            'spo2': {'min': 0, 'max': 50, 'trend': 'decreasing'},
            'temp_skin': {'min': 30.0, 'max': 35.0, 'trend': 'decreasing'}
        }
    }
    
    def __init__(self):
        self.active_simulations: Dict[str, Dict[str, Any]] = {}
        self.simulation_threads: Dict[str, Thread] = {}
        self.stop_events: Dict[str, Event] = {}
    
    def start_simulation(self, simulation_id: str, device_id: int, state: str, 
                        duration_minutes: int = 10, interval_seconds: int = 30) -> Dict[str, Any]:
        """Start a continuous simulation for a device"""
        
        if state not in self.VITAL_SIGNS_RANGES:
            raise ValueError(f"Invalid state: {state}. Available states: {list(self.VITAL_SIGNS_RANGES.keys())}")
        
        # Stop existing simulation if running
        if simulation_id in self.active_simulations:
            self.stop_simulation(simulation_id)
        
        # Create simulation configuration
        simulation_config = {
            'simulation_id': simulation_id,
            'device_id': device_id,
            'state': state,
            'duration_minutes': duration_minutes,
            'interval_seconds': interval_seconds,
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(minutes=duration_minutes),
            'status': 'running',
            'readings_count': 0,
            'last_reading': None
        }
        
        self.active_simulations[simulation_id] = simulation_config
        
        # Create stop event
        stop_event = Event()
        self.stop_events[simulation_id] = stop_event
        
        # Start simulation thread
        simulation_thread = Thread(
            target=self._simulation_worker,
            args=(simulation_id, device_id, state, interval_seconds, stop_event),
            daemon=True
        )
        
        self.simulation_threads[simulation_id] = simulation_thread
        simulation_thread.start()
        
        logger.info(f"Started simulation {simulation_id} for device {device_id} in {state} state")
        
        return simulation_config
    
    def stop_simulation(self, simulation_id: str) -> bool:
        """Stop a running simulation"""
        
        if simulation_id not in self.active_simulations:
            return False
        
        # Signal thread to stop
        if simulation_id in self.stop_events:
            self.stop_events[simulation_id].set()
        
        # Wait for thread to finish
        if simulation_id in self.simulation_threads:
            self.simulation_threads[simulation_id].join(timeout=5.0)
        
        # Update simulation status
        if simulation_id in self.active_simulations:
            self.active_simulations[simulation_id]['status'] = 'stopped'
            self.active_simulations[simulation_id]['end_time'] = datetime.now()
        
        # Clean up
        self.stop_events.pop(simulation_id, None)
        self.simulation_threads.pop(simulation_id, None)
        
        logger.info(f"Stopped simulation {simulation_id}")
        return True
    
    def _simulation_worker(self, simulation_id: str, device_id: int, state: str, 
                          interval_seconds: int, stop_event: Event):
        """Worker thread for continuous simulation"""
        
        try:
            while not stop_event.is_set():
                # Generate simulated vital signs
                vital_signs = self._generate_vital_signs(state)
                
                # Store in database
                self._store_simulated_reading(device_id, vital_signs)
                
                # Update simulation status
                if simulation_id in self.active_simulations:
                    self.active_simulations[simulation_id]['readings_count'] += 1
                    self.active_simulations[simulation_id]['last_reading'] = vital_signs
                
                # Check if simulation duration has expired
                if simulation_id in self.active_simulations:
                    if datetime.now() >= self.active_simulations[simulation_id]['end_time']:
                        logger.info(f"Simulation {simulation_id} duration expired")
                        break
                
                # Wait for next interval
                stop_event.wait(interval_seconds)
                
        except Exception as e:
            logger.error(f"Error in simulation worker {simulation_id}: {str(e)}")
            if simulation_id in self.active_simulations:
                self.active_simulations[simulation_id]['status'] = 'error'
                self.active_simulations[simulation_id]['error'] = str(e)
        finally:
            # Clean up simulation
            if simulation_id in self.active_simulations:
                self.active_simulations[simulation_id]['status'] = 'completed'
                self.active_simulations[simulation_id]['end_time'] = datetime.now()
    
    def _generate_vital_signs(self, state: str) -> Dict[str, Any]:
        """Generate simulated vital signs for a specific state"""
        
        ranges = self.VITAL_SIGNS_RANGES[state]
        
        # Generate base values
        heart_rate = random.randint(ranges['heart_rate']['min'], ranges['heart_rate']['max'])
        spo2 = random.randint(ranges['spo2']['min'], ranges['spo2']['max'])
        temp_skin = round(random.uniform(ranges['temp_skin']['min'], ranges['temp_skin']['max']), 1)
        
        # Add some realistic variation
        heart_rate += random.randint(-5, 5)
        spo2 += random.randint(-2, 2)
        temp_skin += round(random.uniform(-0.3, 0.3), 1)
        
        # Ensure values stay within reasonable bounds
        heart_rate = max(0, min(200, heart_rate))
        spo2 = max(0, min(100, spo2))
        temp_skin = max(30.0, min(45.0, temp_skin))
        
        return {
            'heart_rate': heart_rate,
            'spo2': spo2,
            'temp_skin': temp_skin,
            'state': state,
            'simulated': True,
            'quality': 'excellent'
        }
    
    def _store_simulated_reading(self, device_id: int, vital_signs: Dict[str, Any]):
        """Store simulated reading in database"""
        
        try:
            query = """
                INSERT INTO reading (device_id, heart_rate, spo2, temp_skin, timestamp, is_simulated, quality)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            timestamp = datetime.now().isoformat()
            execute_query('admin_system', query, (
                device_id,
                vital_signs['heart_rate'],
                vital_signs['spo2'],
                vital_signs['temp_skin'],
                timestamp,
                True,  # is_simulated
                vital_signs['quality']
            ))
            
            # Update device last reading time
            update_query = """
                UPDATE device 
                SET last_reading_time = %s, status = 'active'
                WHERE device_id = %s
            """
            execute_query('admin_system', update_query, (timestamp, device_id))
            
            logger.debug(f"Stored simulated reading for device {device_id}: HR={vital_signs['heart_rate']}, SpO2={vital_signs['spo2']}, Temp={vital_signs['temp_skin']}")
            
        except Exception as e:
            logger.error(f"Error storing simulated reading: {str(e)}")
    
    def get_simulation_status(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific simulation"""
        return self.active_simulations.get(simulation_id)
    
    def get_all_simulations(self) -> List[Dict[str, Any]]:
        """Get all active simulations"""
        return list(self.active_simulations.values())
    
    def stop_all_simulations(self):
        """Stop all running simulations"""
        simulation_ids = list(self.active_simulations.keys())
        for simulation_id in simulation_ids:
            self.stop_simulation(simulation_id)
        logger.info(f"Stopped all simulations: {len(simulation_ids)}")
    
    def cleanup_completed_simulations(self):
        """Clean up completed simulations older than 1 hour"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        simulations_to_remove = []
        for simulation_id, config in self.active_simulations.items():
            if config['status'] in ['completed', 'stopped', 'error'] and config['end_time'] < cutoff_time:
                simulations_to_remove.append(simulation_id)
        
        for simulation_id in simulations_to_remove:
            self.active_simulations.pop(simulation_id, None)
            self.stop_events.pop(simulation_id, None)
            self.simulation_threads.pop(simulation_id, None)
        
        if simulations_to_remove:
            logger.info(f"Cleaned up {len(simulations_to_remove)} completed simulations")

# Global simulator instance
vital_signs_simulator = VitalSignsSimulator()

def get_vital_signs_simulator() -> VitalSignsSimulator:
    """Get the global vital signs simulator instance"""
    return vital_signs_simulator

def start_device_simulation(device_id: int, state: str, duration_minutes: int = 10, 
                           interval_seconds: int = 30) -> str:
    """Start a simulation for a specific device"""
    simulator = get_vital_signs_simulator()
    simulation_id = f"sim_{device_id}_{int(time.time())}"
    
    try:
        simulator.start_simulation(simulation_id, device_id, state, duration_minutes, interval_seconds)
        return simulation_id
    except Exception as e:
        logger.error(f"Error starting simulation: {str(e)}")
        raise

def stop_device_simulation(simulation_id: str) -> bool:
    """Stop a specific simulation"""
    simulator = get_vital_signs_simulator()
    return simulator.stop_simulation(simulation_id)

def get_simulation_status(simulation_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a specific simulation"""
    simulator = get_vital_signs_simulator()
    return simulator.get_simulation_status(simulation_id)
