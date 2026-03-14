#!/usr/bin/env python3
"""
Victor Personal Runtime - Device Registry
==========================================

Manages registration and discovery of user's personal devices
for cross-device mesh communication.
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger('victor_runtime.device_registry')


@dataclass
class RegisteredDevice:
    """Information about a registered device"""
    device_id: str
    device_name: str
    platform: str
    os_version: str
    runtime_version: str
    registration_date: str
    last_seen: str
    capabilities: List[str] = field(default_factory=list)
    is_current: bool = False
    trusted: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'platform': self.platform,
            'os_version': self.os_version,
            'runtime_version': self.runtime_version,
            'registration_date': self.registration_date,
            'last_seen': self.last_seen,
            'capabilities': self.capabilities,
            'is_current': self.is_current,
            'trusted': self.trusted
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RegisteredDevice':
        return cls(
            device_id=data['device_id'],
            device_name=data['device_name'],
            platform=data['platform'],
            os_version=data['os_version'],
            runtime_version=data['runtime_version'],
            registration_date=data['registration_date'],
            last_seen=data['last_seen'],
            capabilities=data.get('capabilities', []),
            is_current=data.get('is_current', False),
            trusted=data.get('trusted', True)
        )


class DeviceRegistry:
    """
    Registry of user's personal devices.
    
    Manages device registration, trust, and discovery for
    cross-device mesh communication.
    
    Features:
    - Register new devices
    - Trust management
    - Device discovery
    - Heartbeat tracking
    - Device removal
    """
    
    VERSION = "1.0.0"
    STALE_THRESHOLD_DAYS = 30  # Devices not seen for this long are considered stale
    
    def __init__(self, data_dir: Path, user_id: str):
        """
        Initialize device registry.
        
        Args:
            data_dir: Directory for storing device data
            user_id: Unique user identifier
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.user_id = user_id
        
        self.registry_file = self.data_dir / 'devices.json'
        self.devices: Dict[str, RegisteredDevice] = {}
        self.current_device_id: Optional[str] = None
        
        self._load_registry()
    
    def _load_registry(self):
        """Load device registry from storage"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    for device_data in data.get('devices', []):
                        device = RegisteredDevice.from_dict(device_data)
                        self.devices[device.device_id] = device
                    self.current_device_id = data.get('current_device_id')
            except Exception as e:
                logger.error(f"Failed to load device registry: {e}")
    
    def _save_registry(self):
        """Save device registry to storage"""
        try:
            data = {
                'version': self.VERSION,
                'user_id': self.user_id,
                'current_device_id': self.current_device_id,
                'updated': datetime.now().isoformat(),
                'devices': [d.to_dict() for d in self.devices.values()]
            }
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save device registry: {e}")
    
    def register_device(
        self,
        device_id: str,
        device_name: str,
        platform: str,
        os_version: str,
        runtime_version: str,
        capabilities: Optional[List[str]] = None,
        is_current: bool = False
    ) -> RegisteredDevice:
        """
        Register a new device.
        
        Args:
            device_id: Unique device identifier
            device_name: Human-readable device name
            platform: Platform (windows, android, ios)
            os_version: Operating system version
            runtime_version: Victor runtime version
            capabilities: List of device capabilities
            is_current: Whether this is the current device
            
        Returns:
            RegisteredDevice instance
        """
        now = datetime.now().isoformat()
        
        device = RegisteredDevice(
            device_id=device_id,
            device_name=device_name,
            platform=platform,
            os_version=os_version,
            runtime_version=runtime_version,
            registration_date=now,
            last_seen=now,
            capabilities=capabilities or [],
            is_current=is_current,
            trusted=True
        )
        
        self.devices[device_id] = device
        
        if is_current:
            self.current_device_id = device_id
            # Mark other devices as not current
            for d in self.devices.values():
                if d.device_id != device_id:
                    d.is_current = False
        
        self._save_registry()
        logger.info(f"Device registered: {device_name} ({platform})")
        
        return device
    
    def update_heartbeat(self, device_id: str):
        """Update last seen timestamp for a device"""
        if device_id in self.devices:
            self.devices[device_id].last_seen = datetime.now().isoformat()
            self._save_registry()
    
    def get_device(self, device_id: str) -> Optional[RegisteredDevice]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_current_device(self) -> Optional[RegisteredDevice]:
        """Get the current device"""
        if self.current_device_id:
            return self.devices.get(self.current_device_id)
        return None
    
    def get_all_devices(self) -> List[RegisteredDevice]:
        """Get all registered devices"""
        return list(self.devices.values())
    
    def get_trusted_devices(self) -> List[RegisteredDevice]:
        """Get all trusted devices"""
        return [d for d in self.devices.values() if d.trusted]
    
    def get_active_devices(self) -> List[RegisteredDevice]:
        """Get devices seen within the stale threshold"""
        threshold = datetime.now() - timedelta(days=self.STALE_THRESHOLD_DAYS)
        active = []
        
        for device in self.devices.values():
            try:
                last_seen = datetime.fromisoformat(device.last_seen)
                if last_seen > threshold:
                    active.append(device)
            except (ValueError, AttributeError):
                pass
        
        return active
    
    def get_devices_by_platform(self, platform: str) -> List[RegisteredDevice]:
        """Get devices by platform"""
        return [d for d in self.devices.values() if d.platform == platform]
    
    def trust_device(self, device_id: str):
        """Mark a device as trusted"""
        if device_id in self.devices:
            self.devices[device_id].trusted = True
            self._save_registry()
            logger.info(f"Device trusted: {device_id}")
    
    def untrust_device(self, device_id: str):
        """Mark a device as untrusted"""
        if device_id in self.devices:
            self.devices[device_id].trusted = False
            self._save_registry()
            logger.info(f"Device untrusted: {device_id}")
    
    def remove_device(self, device_id: str) -> bool:
        """
        Remove a device from the registry.
        
        Args:
            device_id: Device to remove
            
        Returns:
            True if device was removed
        """
        if device_id in self.devices:
            del self.devices[device_id]
            if self.current_device_id == device_id:
                self.current_device_id = None
            self._save_registry()
            logger.info(f"Device removed: {device_id}")
            return True
        return False
    
    def remove_stale_devices(self) -> int:
        """
        Remove devices not seen within the stale threshold.
        
        Returns:
            Number of devices removed
        """
        active_devices = self.get_active_devices()
        active_ids = {d.device_id for d in active_devices}
        
        removed = 0
        for device_id in list(self.devices.keys()):
            if device_id not in active_ids and device_id != self.current_device_id:
                del self.devices[device_id]
                removed += 1
        
        if removed > 0:
            self._save_registry()
            logger.info(f"Removed {removed} stale devices")
        
        return removed
    
    def get_registry_summary(self) -> Dict:
        """Get summary of device registry"""
        return {
            'total_devices': len(self.devices),
            'active_devices': len(self.get_active_devices()),
            'trusted_devices': len(self.get_trusted_devices()),
            'current_device': self.current_device_id,
            'platforms': {
                'windows': len(self.get_devices_by_platform('windows')),
                'android': len(self.get_devices_by_platform('android')),
                'ios': len(self.get_devices_by_platform('ios')),
                'macos': len(self.get_devices_by_platform('macos')),
                'linux': len(self.get_devices_by_platform('linux'))
            }
        }
