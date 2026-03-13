#!/usr/bin/env python3
"""
Victor Personal Runtime - Main Runtime Engine
==============================================

Cross-platform personal AI assistant runtime with:
- User consent verification before any operation
- Platform-specific adapters for Windows, Android, iOS
- Federated learning across personal devices
- Full user control and shutdown capabilities

SECURITY: This runtime is designed for PERSONAL USE ONLY on devices
you own. All operations require explicit user consent and can be
disabled at any time through standard platform controls.
"""

import os
import sys
import json
import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

from victor_runtime.logging_utils import VERBOSE_LOGGING, configure_logger

logger = configure_logger('victor_runtime')


class RuntimeState(Enum):
    """Runtime operational states"""
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    AWAITING_CONSENT = "awaiting_consent"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"


class PermissionType(Enum):
    """Types of permissions that can be requested"""
    ACCESSIBILITY = "accessibility"  # Screen reading, overlay
    AUTOMATION = "automation"        # App automation/control
    BACKGROUND = "background"        # Background execution
    NETWORK = "network"              # Network access for sync
    STORAGE = "storage"              # Local data storage
    NOTIFICATION = "notification"    # Push notifications


@dataclass
class ConsentRecord:
    """Record of user consent for a specific permission"""
    permission: PermissionType
    granted: bool
    timestamp: str
    consent_version: str
    user_id: str
    revocable: bool = True
    expiry: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'permission': self.permission.value,
            'granted': self.granted,
            'timestamp': self.timestamp,
            'consent_version': self.consent_version,
            'user_id': self.user_id,
            'revocable': self.revocable,
            'expiry': self.expiry
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConsentRecord':
        return cls(
            permission=PermissionType(data['permission']),
            granted=data['granted'],
            timestamp=data['timestamp'],
            consent_version=data['consent_version'],
            user_id=data['user_id'],
            revocable=data.get('revocable', True),
            expiry=data.get('expiry')
        )


@dataclass
class DeviceInfo:
    """Information about the current device"""
    device_id: str
    platform: str  # windows, android, ios
    device_name: str
    os_version: str
    runtime_version: str
    registration_date: str
    last_seen: str
    capabilities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'device_id': self.device_id,
            'platform': self.platform,
            'device_name': self.device_name,
            'os_version': self.os_version,
            'runtime_version': self.runtime_version,
            'registration_date': self.registration_date,
            'last_seen': self.last_seen,
            'capabilities': self.capabilities
        }


class VictorPersonalRuntime:
    """
    Victor Personal Runtime - Cross-Platform Personal AI Assistant
    
    This is the main runtime that coordinates all Victor functionality
    across your personal devices. It operates with full user consent
    and can be controlled/shutdown at any time.
    
    Features:
    - Cross-platform support (Windows, Android, iOS)
    - Personal device mesh learning
    - User-controlled overlay and automation
    - GitHub-synced configuration
    - Full shutdown capability
    
    Usage:
        runtime = VictorPersonalRuntime()
        await runtime.initialize()
        await runtime.run()
    """
    
    VERSION = "1.0.0"
    CONSENT_VERSION = "1.0"
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        user_id: Optional[str] = None,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the Victor Personal Runtime.
        
        Args:
            config_path: Path to configuration file
            user_id: Unique user identifier (generated if not provided)
            data_dir: Directory for storing runtime data
        """
        self.user_id = user_id or self._generate_user_id()
        self.data_dir = Path(data_dir or self._get_default_data_dir())
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_path = config_path
        self.config: Dict = {}
        
        # State
        self.state = RuntimeState.STOPPED
        self.device_info: Optional[DeviceInfo] = None
        self.consent_records: Dict[PermissionType, ConsentRecord] = {}
        
        # Platform adapter (set during initialization)
        self.platform_adapter = None
        
        # Components (initialized lazily)
        self._mesh_client = None
        self._sync_manager = None
        self._learning_engine = None
        self._overlay_manager = None
        self._automation_engine = None
        
        # Event handlers
        self.on_state_change: Optional[Callable[[RuntimeState], None]] = None
        self.on_learning_update: Optional[Callable[[Dict], None]] = None
        
        # Shutdown flag
        self._shutdown_requested = False
        
        logger.info(f"Victor Personal Runtime v{self.VERSION} initialized")
        logger.info(f"User ID: {self.user_id[:8]}...")
        logger.info(f"Data directory: {self.data_dir}")
    
    def _generate_user_id(self) -> str:
        """Generate a unique user identifier"""
        return hashlib.sha256(
            f"{uuid.getnode()}-{datetime.now().isoformat()}".encode()
        ).hexdigest()[:32]
    
    def _get_default_data_dir(self) -> str:
        """Get default data directory based on platform"""
        if sys.platform == 'win32':
            base = os.environ.get('APPDATA', os.path.expanduser('~'))
            return os.path.join(base, 'VictorRuntime')
        elif sys.platform == 'darwin':
            return os.path.expanduser('~/Library/Application Support/VictorRuntime')
        else:
            return os.path.expanduser('~/.victor_runtime')
    
    def _detect_platform(self) -> str:
        """Detect the current platform"""
        if sys.platform == 'win32':
            return 'windows'
        elif sys.platform == 'darwin':
            # Could be iOS or macOS
            return 'ios' if self._is_ios() else 'macos'
        elif 'android' in sys.platform.lower() or self._is_android():
            return 'android'
        else:
            return 'linux'
    
    def _is_android(self) -> bool:
        """Check if running on Android"""
        try:
            import android
            return True
        except ImportError:
            return os.environ.get('ANDROID_ROOT') is not None
    
    def _is_ios(self) -> bool:
        """Check if running on iOS"""
        try:
            import objc
            from Foundation import NSBundle
            bundle = NSBundle.mainBundle()
            return 'iPhone' in str(bundle.bundleIdentifier()) or \
                   'iPad' in str(bundle.bundleIdentifier())
        except ImportError:
            return False
    
    async def initialize(self) -> bool:
        """
        Initialize the runtime.
        
        This must be called before run(). It will:
        1. Load configuration
        2. Detect platform and initialize adapter
        3. Check and request necessary permissions
        4. Load previous consent records
        5. Initialize components
        
        Returns:
            True if initialization successful, False otherwise
        """
        self._set_state(RuntimeState.INITIALIZING)
        
        try:
            # Load configuration
            await self._load_config()
            
            # Detect platform
            platform = self._detect_platform()
            logger.info(f"Detected platform: {platform}")
            
            # Create device info
            self.device_info = DeviceInfo(
                device_id=self._generate_device_id(),
                platform=platform,
                device_name=self._get_device_name(),
                os_version=self._get_os_version(),
                runtime_version=self.VERSION,
                registration_date=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
                capabilities=self._detect_capabilities()
            )
            
            # Initialize platform adapter
            self.platform_adapter = self._create_platform_adapter(platform)
            
            # Load consent records
            await self._load_consent_records()
            
            # Check required permissions
            self._set_state(RuntimeState.AWAITING_CONSENT)
            if not await self._verify_consent():
                logger.warning("User consent not granted for required permissions")
                return False
            
            # Initialize components
            await self._initialize_components()
            
            logger.info("Runtime initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self._set_state(RuntimeState.STOPPED)
            return False
    
    def _generate_device_id(self) -> str:
        """Generate unique device identifier"""
        return hashlib.sha256(
            f"{uuid.getnode()}-{sys.platform}".encode()
        ).hexdigest()[:16]
    
    def _get_device_name(self) -> str:
        """Get device name"""
        import socket
        return socket.gethostname()
    
    def _get_os_version(self) -> str:
        """Get OS version string"""
        import platform
        return f"{platform.system()} {platform.release()}"
    
    def _detect_capabilities(self) -> List[str]:
        """Detect device capabilities"""
        capabilities = []
        
        # Check for GPU
        try:
            import torch
            if torch.cuda.is_available():
                capabilities.append('cuda')
        except ImportError:
            pass
        
        # Check for neural engine (Apple Silicon)
        try:
            import coreml
            capabilities.append('coreml')
        except ImportError:
            pass
        
        return capabilities
    
    def _create_platform_adapter(self, platform: str):
        """Create the appropriate platform adapter"""
        # Import adapters lazily to avoid dependency issues
        if platform == 'windows':
            from victor_runtime.platforms.windows import WindowsAdapter
            return WindowsAdapter(self)
        elif platform == 'android':
            from victor_runtime.platforms.android import AndroidAdapter
            return AndroidAdapter(self)
        elif platform == 'ios':
            from victor_runtime.platforms.ios import IOSAdapter
            return IOSAdapter(self)
        else:
            from victor_runtime.platforms.base import BasePlatformAdapter
            return BasePlatformAdapter(self)
    
    async def _load_config(self):
        """Load configuration from file or create default"""
        config_file = self.data_dir / 'config.json'
        
        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.debug("Loaded config from explicit path %s", self.config_path)
        elif config_file.exists():
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            logger.debug("Loaded config from data dir %s", config_file)
        else:
            self.config = self._get_default_config()
            await self._save_config()
            logger.debug("Created default config at %s", config_file)
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'version': self.VERSION,
            'sync': {
                'enabled': True,
                'interval_seconds': 300,  # 5 minutes
                'github_gist_id': None,  # Set by user
            },
            'learning': {
                'enabled': True,
                'local_only': True,  # Data stays on device by default
                'model_sync': False,  # Don't sync models by default
            },
            'overlay': {
                'enabled': False,  # Disabled by default
                'opacity': 0.9,
                'position': 'bottom_right',
            },
            'automation': {
                'enabled': False,  # Disabled by default
                'require_confirmation': True,
            },
            'privacy': {
                'telemetry': False,
                'crash_reports': False,
                'usage_analytics': False,
            }
        }
    
    async def _save_config(self):
        """Save configuration to file"""
        config_file = self.data_dir / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.debug("Saved config to %s", config_file)
    
    async def _load_consent_records(self):
        """Load previous consent records"""
        consent_file = self.data_dir / 'consent.json'
        
        if consent_file.exists():
            with open(consent_file, 'r') as f:
                data = json.load(f)
                for record_data in data.get('records', []):
                    record = ConsentRecord.from_dict(record_data)
                    self.consent_records[record.permission] = record
    
    async def _save_consent_records(self):
        """Save consent records to file"""
        consent_file = self.data_dir / 'consent.json'
        
        data = {
            'version': self.CONSENT_VERSION,
            'user_id': self.user_id,
            'last_updated': datetime.now().isoformat(),
            'records': [r.to_dict() for r in self.consent_records.values()]
        }
        
        with open(consent_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def _verify_consent(self) -> bool:
        """
        Verify user has consented to required permissions.
        
        This method checks if the user has granted consent for each
        permission required by enabled features. If consent is missing,
        it will request consent through the platform adapter.
        
        Returns:
            True if all required permissions are consented
        """
        required_permissions = [PermissionType.STORAGE, PermissionType.BACKGROUND]
        
        # Add optional permissions based on config
        if self.config.get('sync', {}).get('enabled'):
            required_permissions.append(PermissionType.NETWORK)
        
        if self.config.get('overlay', {}).get('enabled'):
            required_permissions.append(PermissionType.ACCESSIBILITY)
        
        if self.config.get('automation', {}).get('enabled'):
            required_permissions.append(PermissionType.AUTOMATION)
        
        # Check each permission
        for permission in required_permissions:
            if permission not in self.consent_records or \
               not self.consent_records[permission].granted:
                
                # Request consent
                logger.debug("Requesting consent for %s", permission.value)
                granted = await self.request_consent(permission)
                if not granted:
                    logger.warning(f"Consent not granted for: {permission.value}")
                    return False
        
        return True
    
    async def request_consent(self, permission: PermissionType) -> bool:
        """
        Request user consent for a specific permission.
        
        This will display a consent dialog explaining what the
        permission is used for and allow the user to grant or deny.
        
        Args:
            permission: The permission to request consent for
            
        Returns:
            True if consent granted, False otherwise
        """
        # Get permission description
        descriptions = {
            PermissionType.ACCESSIBILITY: (
                "Victor needs accessibility permission to provide overlay "
                "features like floating assistant panels. This allows Victor "
                "to display helpful information over other apps."
            ),
            PermissionType.AUTOMATION: (
                "Victor needs automation permission to help you with tasks "
                "like filling forms or navigating apps. Victor will always "
                "ask for confirmation before performing actions."
            ),
            PermissionType.BACKGROUND: (
                "Victor needs to run in the background to provide continuous "
                "assistance and learn from your usage patterns to become more "
                "helpful over time."
            ),
            PermissionType.NETWORK: (
                "Victor needs network access to sync your preferences and "
                "learned patterns across your devices. Your data is encrypted "
                "and only synced to storage you control."
            ),
            PermissionType.STORAGE: (
                "Victor needs storage access to save your preferences, learned "
                "patterns, and session data locally on this device."
            ),
            PermissionType.NOTIFICATION: (
                "Victor can send notifications to alert you about important "
                "events or suggestions. You can customize notification settings."
            ),
        }
        
        description = descriptions.get(permission, f"Victor needs {permission.value} permission.")
        
        # Show consent dialog through platform adapter
        if self.platform_adapter:
            granted = await self.platform_adapter.show_consent_dialog(
                title=f"Grant {permission.value.title()} Permission",
                description=description,
                permission=permission
            )
        else:
            # Fallback: console-based consent
            print(f"\n{'='*60}")
            print(f"CONSENT REQUEST: {permission.value.upper()}")
            print(f"{'='*60}")
            print(description)
            print("\nDo you grant this permission? (yes/no)")
            response = input("> ").strip().lower()
            granted = response in ('yes', 'y', 'grant', 'allow')
        
        # Record consent
        record = ConsentRecord(
            permission=permission,
            granted=granted,
            timestamp=datetime.now().isoformat(),
            consent_version=self.CONSENT_VERSION,
            user_id=self.user_id
        )
        self.consent_records[permission] = record
        await self._save_consent_records()
        
        logger.info(f"Consent for {permission.value}: {'granted' if granted else 'denied'}")
        return granted
    
    async def revoke_consent(self, permission: PermissionType):
        """
        Revoke consent for a specific permission.
        
        This allows users to revoke previously granted consent at any time.
        The runtime will disable features that depend on the revoked permission.
        
        Args:
            permission: The permission to revoke
        """
        if permission in self.consent_records:
            record = self.consent_records[permission]
            if record.revocable:
                record.granted = False
                record.timestamp = datetime.now().isoformat()
                await self._save_consent_records()
                
                # Disable dependent features
                await self._disable_features_for_permission(permission)
                
                logger.info(f"Consent revoked for: {permission.value}")
            else:
                logger.warning(f"Permission {permission.value} is not revocable")
    
    async def _disable_features_for_permission(self, permission: PermissionType):
        """Disable features that depend on a revoked permission"""
        if permission == PermissionType.ACCESSIBILITY:
            self.config['overlay']['enabled'] = False
            if self._overlay_manager:
                await self._overlay_manager.disable()
        
        elif permission == PermissionType.AUTOMATION:
            self.config['automation']['enabled'] = False
            if self._automation_engine:
                await self._automation_engine.disable()
        
        elif permission == PermissionType.NETWORK:
            self.config['sync']['enabled'] = False
            if self._sync_manager:
                await self._sync_manager.disable()
        
        await self._save_config()
    
    async def _initialize_components(self):
        """Initialize runtime components based on configuration"""
        # Initialize mesh client for cross-device communication
        if self.config.get('sync', {}).get('enabled'):
            from victor_runtime.mesh.client import MeshClient
            self._mesh_client = MeshClient(
                device_info=self.device_info,
                config=self.config.get('sync', {})
            )
        
        # Initialize sync manager
        if self.config.get('sync', {}).get('enabled'):
            from victor_runtime.core.sync_manager import SyncManager
            self._sync_manager = SyncManager(
                runtime=self,
                config=self.config.get('sync', {})
            )
        
        # Initialize learning engine
        if self.config.get('learning', {}).get('enabled'):
            from victor_runtime.core.learning import PersonalLearningEngine
            self._learning_engine = PersonalLearningEngine(
                data_dir=self.data_dir / 'learning',
                config=self.config.get('learning', {})
            )
        
        logger.info("Components initialized")
    
    async def run(self):
        """
        Start the main runtime loop.
        
        This will run continuously until shutdown() is called or
        a keyboard interrupt is received.
        """
        if self.state != RuntimeState.AWAITING_CONSENT:
            if not await self.initialize():
                raise RuntimeError("Runtime initialization failed")
        
        self._set_state(RuntimeState.RUNNING)
        logger.info("Victor Personal Runtime started")
        
        try:
            # Start background tasks
            tasks = [
                asyncio.create_task(self._main_loop()),
            ]
            
            if self._sync_manager:
                tasks.append(asyncio.create_task(self._sync_manager.run()))
            
            if self._mesh_client:
                tasks.append(asyncio.create_task(self._mesh_client.run()))
            
            if self._learning_engine:
                tasks.append(asyncio.create_task(self._learning_engine.run()))
            
            # Wait for all tasks or shutdown
            await asyncio.gather(*tasks)
            
        except asyncio.CancelledError:
            logger.info("Runtime tasks cancelled")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
        finally:
            await self._cleanup()
    
    async def _main_loop(self):
        """Main processing loop"""
        while not self._shutdown_requested and self.state == RuntimeState.RUNNING:
            try:
                # Process pending events
                if self.platform_adapter:
                    await self.platform_adapter.process_events()
                
                # Update device heartbeat
                if self.device_info:
                    self.device_info.last_seen = datetime.now().isoformat()
                
                # Small sleep to prevent CPU spinning
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(1)  # Back off on error
    
    def _set_state(self, new_state: RuntimeState):
        """Set runtime state and notify listeners"""
        old_state = self.state
        self.state = new_state
        
        if self.on_state_change and old_state != new_state:
            try:
                self.on_state_change(new_state)
            except Exception as e:
                logger.error(f"State change callback error: {e}")
        
        logger.info(f"State changed: {old_state.value} -> {new_state.value}")
    
    async def pause(self):
        """Pause the runtime"""
        if self.state == RuntimeState.RUNNING:
            self._set_state(RuntimeState.PAUSED)
            logger.info("Runtime paused")
    
    async def resume(self):
        """Resume the runtime from paused state"""
        if self.state == RuntimeState.PAUSED:
            self._set_state(RuntimeState.RUNNING)
            logger.info("Runtime resumed")
    
    async def shutdown(self):
        """
        Gracefully shutdown the runtime.
        
        This will:
        1. Save all pending state
        2. Close connections
        3. Stop all background tasks
        4. Release all resources
        
        The runtime can be restarted by calling initialize() and run() again.
        """
        logger.info("Shutdown requested")
        self._shutdown_requested = True
        self._set_state(RuntimeState.SHUTTING_DOWN)
        
        # Allow cleanup to run
        await self._cleanup()
        
        self._set_state(RuntimeState.STOPPED)
        logger.info("Runtime shutdown complete")
    
    async def _cleanup(self):
        """Cleanup resources"""
        try:
            # Save config
            await self._save_config()
            
            # Stop components
            if self._sync_manager:
                await self._sync_manager.stop()
            
            if self._mesh_client:
                await self._mesh_client.stop()
            
            if self._learning_engine:
                await self._learning_engine.stop()
            
            if self._overlay_manager:
                await self._overlay_manager.stop()
            
            if self._automation_engine:
                await self._automation_engine.stop()
            
            if self.platform_adapter:
                await self.platform_adapter.cleanup()
            
            logger.info("Cleanup complete")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def get_status(self) -> Dict:
        """Get current runtime status"""
        return {
            'version': self.VERSION,
            'state': self.state.value,
            'user_id': self.user_id[:8] + '...',
            'device': self.device_info.to_dict() if self.device_info else None,
            'permissions': {
                k.value: v.granted for k, v in self.consent_records.items()
            },
            'components': {
                'mesh_client': self._mesh_client is not None,
                'sync_manager': self._sync_manager is not None,
                'learning_engine': self._learning_engine is not None,
                'overlay_manager': self._overlay_manager is not None,
                'automation_engine': self._automation_engine is not None,
            }
        }


# Convenience function for running the runtime
async def run_victor_runtime(config_path: Optional[str] = None):
    """
    Convenience function to run the Victor Personal Runtime.
    
    Args:
        config_path: Optional path to configuration file
    """
    runtime = VictorPersonalRuntime(config_path=config_path)
    
    try:
        if await runtime.initialize():
            await runtime.run()
        else:
            print("Failed to initialize runtime - consent may not have been granted")
    except KeyboardInterrupt:
        print("\nShutdown requested...")
        await runtime.shutdown()


if __name__ == "__main__":
    asyncio.run(run_victor_runtime())
