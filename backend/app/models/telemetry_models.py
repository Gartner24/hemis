"""
Telemetry models for HEMIS IoT system
Defines data structures for devices, readings, and vital signs monitoring
"""

from typing import Optional, List, Dict, Any, Union, Sequence
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class DeviceStatus(Enum):
    """Device status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    OFFLINE = "offline"

class DeviceType(Enum):
    """Device type enumeration"""
    VITAL_SIGNS_MONITOR = "vital_signs_monitor"
    HEART_RATE_MONITOR = "heart_rate_monitor"
    OXYGEN_SATURATION_MONITOR = "oxygen_saturation_monitor"
    TEMPERATURE_MONITOR = "temperature_monitor"
    MULTI_PARAMETER_MONITOR = "multi_parameter_monitor"

class ReadingQuality(Enum):
    """Reading quality enumeration"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

@dataclass
class Device:
    """IoT device model"""
    device_id: int
    device_name: str
    device_type: str
    serial_number: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    firmware_version: Optional[str] = None
    status: str = "inactive"
    patient_id: Optional[int] = None
    room_id: Optional[int] = None
    last_reading_time: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def is_active(self) -> bool:
        """Check if device is active"""
        return self.status == DeviceStatus.ACTIVE.value
    
    def is_assigned(self) -> bool:
        """Check if device is assigned to a patient"""
        return self.patient_id is not None
    
    def needs_maintenance(self) -> bool:
        """Check if device needs maintenance"""
        if not self.next_maintenance:
            return False
        return datetime.now() > self.next_maintenance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary"""
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'serial_number': self.serial_number,
            'model': self.model,
            'manufacturer': self.manufacturer,
            'firmware_version': self.firmware_version,
            'status': self.status,
            'patient_id': self.patient_id,
            'room_id': self.room_id,
            'last_reading_time': self.last_reading_time.isoformat() if self.last_reading_time else None,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active(),
            'is_assigned': self.is_assigned(),
            'needs_maintenance': self.needs_maintenance()
        }

@dataclass
class Metric:
    """Metric definition model"""
    metric_id: int
    metric_name: str
    metric_unit: str
    description: Optional[str] = None
    normal_range_min: Optional[float] = None
    normal_range_max: Optional[float] = None
    critical_range_min: Optional[float] = None
    critical_range_max: Optional[float] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def is_normal(self, value: float) -> bool:
        """Check if a value is within normal range"""
        if self.normal_range_min is None or self.normal_range_max is None:
            return True
        return self.normal_range_min <= value <= self.normal_range_max
    
    def is_critical(self, value: float) -> bool:
        """Check if a value is in critical range"""
        if self.critical_range_min is None or self.critical_range_max is None:
            return False
        return value < self.critical_range_min or value > self.critical_range_max
    
    def get_status(self, value: float) -> str:
        """Get status based on value"""
        if self.is_critical(value):
            return "critical"
        elif not self.is_normal(value):
            return "warning"
        else:
            return "normal"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            'metric_id': self.metric_id,
            'metric_name': self.metric_name,
            'metric_unit': self.metric_unit,
            'description': self.description,
            'normal_range_min': self.normal_range_min,
            'normal_range_max': self.normal_range_max,
            'critical_range_min': self.critical_range_min,
            'critical_range_max': self.critical_range_max,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Reading:
    """Telemetry reading model"""
    reading_id: int
    device_id: int
    timestamp: datetime
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    temp_skin: Optional[float] = None
    is_simulated: bool = False
    quality: str = "good"
    notes: Optional[str] = None
    
    def has_vital_signs(self) -> bool:
        """Check if reading contains vital signs data"""
        return any([self.heart_rate is not None, self.spo2 is not None, self.temp_skin is not None])
    
    def get_vital_signs(self) -> Dict[str, Any]:
        """Get vital signs as dictionary"""
        vital_signs = {}
        if self.heart_rate is not None:
            vital_signs['heart_rate'] = self.heart_rate
        if self.spo2 is not None:
            vital_signs['spo2'] = self.spo2
        if self.temp_skin is not None:
            vital_signs['temp_skin'] = self.temp_skin
        return vital_signs
    
    def is_critical(self) -> bool:
        """Check if any vital sign is in critical range"""
        if self.heart_rate is not None and (self.heart_rate < 50 or self.heart_rate > 120):
            return True
        if self.spo2 is not None and self.spo2 < 90:
            return True
        if self.temp_skin is not None and (self.temp_skin < 35 or self.temp_skin > 38):
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reading to dictionary"""
        return {
            'reading_id': self.reading_id,
            'device_id': self.device_id,
            'timestamp': self.timestamp.isoformat(),
            'heart_rate': self.heart_rate,
            'spo2': self.spo2,
            'temp_skin': self.temp_skin,
            'is_simulated': self.is_simulated,
            'quality': self.quality,
            'notes': self.notes,
            'has_vital_signs': self.has_vital_signs(),
            'is_critical': self.is_critical(),
            'vital_signs': self.get_vital_signs()
        }

@dataclass
class TelemetryData:
    """Combined telemetry data model"""
    device: Device
    reading: Reading
    patient: Optional[Dict[str, Any]] = None
    metrics: Optional[List[Metric]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert telemetry data to dictionary"""
        return {
            'device': self.device.to_dict(),
            'reading': self.reading.to_dict(),
            'patient': self.patient,
            'metrics': [metric.to_dict() for metric in self.metrics] if self.metrics else None,
            'timestamp': self.reading.timestamp.isoformat()
        }

@dataclass
class Incident:
    """Incident/alert model"""
    incident_id: int
    device_id: int
    incident_type: str
    severity: str
    description: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def is_resolved(self) -> bool:
        """Check if incident is resolved"""
        return self.resolved
    
    def get_duration_minutes(self) -> Optional[int]:
        """Get incident duration in minutes"""
        if self.resolved and self.resolved_at:
            return int((self.resolved_at - self.timestamp).total_seconds() / 60)
        elif not self.resolved:
            return int((datetime.now() - self.timestamp).total_seconds() / 60)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert incident to dictionary"""
        return {
            'incident_id': self.incident_id,
            'device_id': self.device_id,
            'incident_type': self.incident_type,
            'severity': self.severity,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'duration_minutes': self.get_duration_minutes()
        }

@dataclass
class VitalSignsSummary:
    """Vital signs summary for a patient"""
    patient_id: int
    device_id: int
    latest_reading: Reading
    heart_rate_trend: List[int]
    spo2_trend: List[int]
    temperature_trend: List[float]
    time_range_hours: int
    alerts_count: int = 0
    critical_readings_count: int = 0
    
    def get_trend_direction(self, values: Sequence[Union[int, float]]) -> str:
        """Get trend direction (increasing, decreasing, stable)"""
        if len(values) < 2:
            return "stable"
        
        # Calculate simple trend
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if not first_half or not second_half:
            return "stable"
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        diff = second_avg - first_avg
        if abs(diff) < 0.1:  # Threshold for stable
            return "stable"
        elif diff > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert vital signs summary to dictionary"""
        return {
            'patient_id': self.patient_id,
            'device_id': self.device_id,
            'latest_reading': self.latest_reading.to_dict(),
            'heart_rate_trend': self.heart_rate_trend,
            'spo2_trend': self.spo2_trend,
            'temperature_trend': self.temperature_trend,
            'trends': {
                'heart_rate': self.get_trend_direction(self.heart_rate_trend),
                'spo2': self.get_trend_direction(self.spo2_trend),
                'temperature': self.get_trend_direction(self.temperature_trend)
            },
            'time_range_hours': self.time_range_hours,
            'alerts_count': self.alerts_count,
            'critical_readings_count': self.critical_readings_count
        }

# Factory functions for creating model instances from database rows
def create_device_from_db(row: Dict[str, Any]) -> Device:
    """Create Device instance from database row"""
    return Device(
        device_id=row['device_id'],
        device_name=row['device_name'],
        device_type=row['device_type'],
        serial_number=row.get('serial_number'),
        model=row.get('model'),
        manufacturer=row.get('manufacturer'),
        firmware_version=row.get('firmware_version'),
        status=row.get('status', 'inactive'),
        patient_id=row.get('patient_id'),
        room_id=row.get('room_id'),
        last_reading_time=parse_datetime(row.get('last_reading_time')),
        last_maintenance=parse_datetime(row.get('last_maintenance')),
        next_maintenance=parse_datetime(row.get('next_maintenance')),
        created_at=parse_datetime(row.get('created_at')),
        updated_at=parse_datetime(row.get('updated_at'))
    )

def create_reading_from_db(row: Dict[str, Any]) -> Reading:
    """Create Reading instance from database row"""
    return Reading(
        reading_id=row['reading_id'],
        device_id=row['device_id'],
        timestamp=parse_datetime(row['timestamp']) or datetime.now(),
        heart_rate=row.get('heart_rate'),
        spo2=row.get('spo2'),
        temp_skin=row.get('temp_skin'),
        is_simulated=row.get('is_simulated', False),
        quality=row.get('quality', 'good'),
        notes=row.get('notes')
    )

def create_metric_from_db(row: Dict[str, Any]) -> Metric:
    """Create Metric instance from database row"""
    return Metric(
        metric_id=row['metric_id'],
        metric_name=row['metric_name'],
        metric_unit=row['metric_unit'],
        description=row.get('description'),
        normal_range_min=row.get('normal_range_min'),
        normal_range_max=row.get('normal_range_max'),
        critical_range_min=row.get('critical_range_min'),
        critical_range_max=row.get('critical_range_max'),
        is_active=row.get('is_active', True),
        created_at=parse_datetime(row.get('created_at'))
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
