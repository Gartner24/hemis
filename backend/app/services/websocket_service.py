"""
WebSocket Service for Real-time Telemetry Updates
Provides real-time communication for IoT device data and vital signs monitoring
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional, Any
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from ..db.connection import execute_query

logger = logging.getLogger(__name__)

class WebSocketService:
    """Manages WebSocket connections and real-time updates"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.connected_clients: Dict[str, Dict[str, Any]] = {}  # client_id -> client_info
        self.room_subscriptions: Dict[str, Set[str]] = {}  # room -> set of client_ids
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Set up WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.environ.get('socketio.sid')
            if not client_id:
                return
            self.connected_clients[client_id] = {
                'connected_at': datetime.now().isoformat(),
                'rooms': set(),
                'user_role': None,
                'user_id': None
            }
            logger.info(f"Client connected: {client_id}")
            emit('connected', {'client_id': client_id, 'timestamp': datetime.now().isoformat()})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.environ.get('socketio.sid')
            if not client_id:
                return
            if client_id in self.connected_clients:
                # Leave all rooms
                for room in self.connected_clients[client_id]['rooms']:
                    self.leave_telemetry_room(client_id, room)
                
                del self.connected_clients[client_id]
                logger.info(f"Client disconnected: {client_id}")
        
        @self.socketio.on('authenticate')
        def handle_authentication(data):
            """Handle client authentication"""
            client_id = request.environ.get('socketio.sid')
            if not client_id:
                return
            user_id = data.get('user_id')
            user_role = data.get('user_role')
            
            if client_id in self.connected_clients:
                self.connected_clients[client_id]['user_id'] = user_id
                self.connected_clients[client_id]['user_role'] = user_role
                logger.info(f"Client {client_id} authenticated as {user_role} (user_id: {user_id})")
                emit('authenticated', {'status': 'success', 'user_role': user_role})
            else:
                emit('error', {'message': 'Client not found'})
        
        @self.socketio.on('join_telemetry_room')
        def handle_join_telemetry_room(data):
            """Handle joining a telemetry monitoring room"""
            client_id = request.environ.get('socketio.sid')
            if not client_id:
                return
            room_type = data.get('room_type')  # 'device', 'patient', 'global'
            room_id = data.get('room_id')  # device_id, patient_id, or 'all'
            
            if room_type and room_id:
                room_name = f"{room_type}_{room_id}"
                self.join_telemetry_room(client_id, room_name, data)
            else:
                emit('error', {'message': 'Invalid room parameters'})
        
        @self.socketio.on('leave_telemetry_room')
        def handle_leave_telemetry_room(data):
            """Handle leaving a telemetry monitoring room"""
            client_id = request.environ.get('socketio.sid')
            if not client_id:
                return
            room_type = data.get('room_type')
            room_id = data.get('room_id')
            
            if room_type and room_id:
                room_name = f"{room_type}_{room_id}"
                self.leave_telemetry_room(client_id, room_name)
            else:
                emit('error', {'message': 'Invalid room parameters'})
    
    def join_telemetry_room(self, client_id: str, room_name: str, room_data: Dict[str, Any]):
        """Join a telemetry monitoring room"""
        if client_id not in self.connected_clients:
            logger.warning(f"Client {client_id} not found when trying to join room {room_name}")
            return
        
        # Join the room
        join_room(room_name)
        
        # Track room subscription
        if room_name not in self.room_subscriptions:
            self.room_subscriptions[room_name] = set()
        self.room_subscriptions[room_name].add(client_id)
        
        # Add room to client's room list
        self.connected_clients[client_id]['rooms'].add(room_name)
        
        logger.info(f"Client {client_id} joined room {room_name}")
        
        # Send room confirmation
        emit('room_joined', {
            'room_name': room_name,
            'room_data': room_data,
            'timestamp': datetime.now().isoformat()
        })
    
    def leave_telemetry_room(self, client_id: str, room_name: str):
        """Leave a telemetry monitoring room"""
        if client_id not in self.connected_clients:
            return
        
        # Leave the room
        leave_room(room_name)
        
        # Remove from room subscriptions
        if room_name in self.room_subscriptions:
            self.room_subscriptions[room_name].discard(client_id)
            if not self.room_subscriptions[room_name]:
                del self.room_subscriptions[room_name]
        
        # Remove room from client's room list
        self.connected_clients[client_id]['rooms'].discard(room_name)
        
        logger.info(f"Client {client_id} left room {room_name}")
    
    def broadcast_telemetry_update(self, room_name: str, telemetry_data: Dict[str, Any]):
        """Broadcast telemetry update to all clients in a room"""
        if room_name in self.room_subscriptions:
            self.socketio.emit('telemetry_update', {
                'room_name': room_name,
                'data': telemetry_data,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.debug(f"Broadcasted telemetry update to room {room_name}: {len(self.room_subscriptions[room_name])} clients")
    
    def broadcast_device_update(self, device_id: int, device_data: Dict[str, Any]):
        """Broadcast device update to device-specific room"""
        room_name = f"device_{device_id}"
        self.broadcast_telemetry_update(room_name, {
            'type': 'device_update',
            'device_id': device_id,
            'device_data': device_data
        })
    
    def broadcast_patient_update(self, patient_id: int, patient_data: Dict[str, Any]):
        """Broadcast patient update to patient-specific room"""
        room_name = f"patient_{patient_id}"
        self.broadcast_telemetry_update(room_name, {
            'type': 'patient_update',
            'patient_id': patient_id,
            'patient_data': patient_data
        })
    
    def broadcast_global_alert(self, alert_data: Dict[str, Any]):
        """Broadcast global alert to all connected clients"""
        self.socketio.emit('global_alert', {
            'alert': alert_data,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Broadcasted global alert: {alert_data.get('type', 'unknown')}")
    
    def get_room_clients(self, room_name: str) -> Set[str]:
        """Get all clients subscribed to a specific room"""
        return self.room_subscriptions.get(room_name, set())
    
    def get_client_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific client"""
        return self.connected_clients.get(client_id)
    
    def get_connected_clients_count(self) -> int:
        """Get total number of connected clients"""
        return len(self.connected_clients)
    
    def get_room_subscriptions_count(self) -> int:
        """Get total number of room subscriptions"""
        return sum(len(clients) for clients in self.room_subscriptions.values())

# Global WebSocket service instance
websocket_service: Optional[WebSocketService] = None

def initialize_websocket_service(socketio: SocketIO):
    """Initialize the global WebSocket service"""
    global websocket_service
    websocket_service = WebSocketService(socketio)
    logger.info("WebSocket service initialized")
    return websocket_service

def get_websocket_service() -> WebSocketService:
    """Get the global WebSocket service instance"""
    if websocket_service is None:
        raise RuntimeError("WebSocket service not initialized. Call initialize_websocket_service first.")
    return websocket_service

# Utility functions for broadcasting updates
def broadcast_device_telemetry(device_id: int, telemetry_data: Dict[str, Any]):
    """Broadcast device telemetry update"""
    try:
        service = get_websocket_service()
        service.broadcast_device_update(device_id, telemetry_data)
    except Exception as e:
        logger.error(f"Error broadcasting device telemetry: {str(e)}")

def broadcast_patient_telemetry(patient_id: int, telemetry_data: Dict[str, Any]):
    """Broadcast patient telemetry update"""
    try:
        service = get_websocket_service()
        service.broadcast_patient_update(patient_id, telemetry_data)
    except Exception as e:
        logger.error(f"Error broadcasting patient telemetry: {str(e)}")

def broadcast_critical_alert(alert_data: Dict[str, Any]):
    """Broadcast critical alert to all clients"""
    try:
        service = get_websocket_service()
        service.broadcast_global_alert(alert_data)
    except Exception as e:
        logger.error(f"Error broadcasting critical alert: {str(e)}")
