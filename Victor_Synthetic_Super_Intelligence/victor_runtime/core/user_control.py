#!/usr/bin/env python3
"""
Victor Personal Runtime - User Control Panel
=============================================

Provides full user control over the Victor runtime, including:
- Start/Stop/Pause runtime
- Permission management
- Feature toggles
- Data management
- Privacy controls

The user always has full control over Victor.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger('victor_runtime.control')


@dataclass
class FeatureToggle:
    """Represents a toggleable feature"""
    name: str
    enabled: bool
    description: str
    requires_permission: Optional[str] = None
    requires_restart: bool = False


class UserControlPanel:
    """
    User Control Panel for Victor Personal Runtime.
    
    Provides comprehensive controls for the user to manage
    all aspects of Victor's operation on their device.
    
    Features:
    - Start/Stop/Pause runtime
    - Enable/Disable individual features
    - Manage permissions
    - View and delete collected data
    - Export/Import settings
    
    Usage:
        from victor_runtime.core.user_control import UserControlPanel
        
        panel = UserControlPanel(runtime)
        
        # Check status
        status = panel.get_status()
        
        # Toggle feature
        panel.set_feature('overlay', False)
        
        # Stop runtime
        await panel.stop_runtime()
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, runtime=None, config_dir: Optional[Path] = None):
        """
        Initialize the user control panel.
        
        Args:
            runtime: VictorPersonalRuntime instance
            config_dir: Directory for control settings
        """
        self.runtime = runtime
        self.config_dir = config_dir or Path.home() / '.victor_runtime'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._features: Dict[str, FeatureToggle] = {}
        self._initialize_features()
        
        # Event callbacks
        self.on_feature_change: Optional[Callable[[str, bool], None]] = None
        self.on_runtime_state_change: Optional[Callable[[str], None]] = None
    
    def _initialize_features(self):
        """Initialize available features"""
        self._features = {
            'learning': FeatureToggle(
                name='learning',
                enabled=True,
                description='Allow Victor to learn from your interactions',
                requires_permission='data_collection'
            ),
            'sync': FeatureToggle(
                name='sync',
                enabled=True,
                description='Sync settings across your devices',
                requires_permission='network'
            ),
            'overlay': FeatureToggle(
                name='overlay',
                enabled=False,
                description='Show floating assistant overlay',
                requires_permission='accessibility'
            ),
            'automation': FeatureToggle(
                name='automation',
                enabled=False,
                description='Allow Victor to automate tasks',
                requires_permission='automation'
            ),
            'notifications': FeatureToggle(
                name='notifications',
                enabled=True,
                description='Receive notifications from Victor',
                requires_permission='notification'
            ),
            'background': FeatureToggle(
                name='background',
                enabled=True,
                description='Run Victor in the background',
                requires_permission='background'
            ),
            'voice': FeatureToggle(
                name='voice',
                enabled=False,
                description='Enable voice interaction',
                requires_permission='microphone'
            ),
            'analytics': FeatureToggle(
                name='analytics',
                enabled=False,
                description='Share anonymous usage statistics',
                requires_permission='analytics'
            )
        }
        
        self._load_feature_states()
    
    def _load_feature_states(self):
        """Load saved feature states"""
        state_file = self.config_dir / 'feature_states.json'
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    states = json.load(f)
                    for name, enabled in states.items():
                        if name in self._features:
                            self._features[name].enabled = enabled
            except Exception as e:
                logger.error(f"Failed to load feature states: {e}")
    
    def _save_feature_states(self):
        """Save feature states"""
        state_file = self.config_dir / 'feature_states.json'
        try:
            states = {name: f.enabled for name, f in self._features.items()}
            with open(state_file, 'w') as f:
                json.dump(states, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save feature states: {e}")
    
    # ========================
    # Runtime Control
    # ========================
    
    async def start_runtime(self) -> bool:
        """
        Start the Victor runtime.
        
        Returns:
            True if started successfully
        """
        if not self.runtime:
            logger.error("No runtime instance available")
            return False
        
        try:
            success = await self.runtime.initialize()
            if success:
                asyncio.create_task(self.runtime.run())
                logger.info("Runtime started")
                if self.on_runtime_state_change:
                    self.on_runtime_state_change('running')
            return success
        except Exception as e:
            logger.error(f"Failed to start runtime: {e}")
            return False
    
    async def stop_runtime(self) -> bool:
        """
        Stop the Victor runtime.
        
        This will gracefully shutdown all components and save state.
        
        Returns:
            True if stopped successfully
        """
        if not self.runtime:
            return True
        
        try:
            await self.runtime.shutdown()
            logger.info("Runtime stopped")
            if self.on_runtime_state_change:
                self.on_runtime_state_change('stopped')
            return True
        except Exception as e:
            logger.error(f"Failed to stop runtime: {e}")
            return False
    
    async def pause_runtime(self) -> bool:
        """
        Pause the Victor runtime.
        
        Victor will stop processing but maintain state.
        
        Returns:
            True if paused successfully
        """
        if not self.runtime:
            return False
        
        try:
            await self.runtime.pause()
            logger.info("Runtime paused")
            if self.on_runtime_state_change:
                self.on_runtime_state_change('paused')
            return True
        except Exception as e:
            logger.error(f"Failed to pause runtime: {e}")
            return False
    
    async def resume_runtime(self) -> bool:
        """
        Resume the Victor runtime from paused state.
        
        Returns:
            True if resumed successfully
        """
        if not self.runtime:
            return False
        
        try:
            await self.runtime.resume()
            logger.info("Runtime resumed")
            if self.on_runtime_state_change:
                self.on_runtime_state_change('running')
            return True
        except Exception as e:
            logger.error(f"Failed to resume runtime: {e}")
            return False
    
    async def restart_runtime(self) -> bool:
        """
        Restart the Victor runtime.
        
        Returns:
            True if restarted successfully
        """
        await self.stop_runtime()
        await asyncio.sleep(1)
        return await self.start_runtime()
    
    # ========================
    # Feature Control
    # ========================
    
    def get_features(self) -> Dict[str, Dict]:
        """
        Get all available features and their states.
        
        Returns:
            Dictionary of feature information
        """
        return {
            name: {
                'enabled': f.enabled,
                'description': f.description,
                'requires_permission': f.requires_permission,
                'requires_restart': f.requires_restart
            }
            for name, f in self._features.items()
        }
    
    def get_feature(self, name: str) -> Optional[Dict]:
        """Get information about a specific feature"""
        if name not in self._features:
            return None
        
        f = self._features[name]
        return {
            'enabled': f.enabled,
            'description': f.description,
            'requires_permission': f.requires_permission,
            'requires_restart': f.requires_restart
        }
    
    def is_feature_enabled(self, name: str) -> bool:
        """Check if a feature is enabled"""
        if name not in self._features:
            return False
        return self._features[name].enabled
    
    async def set_feature(self, name: str, enabled: bool) -> bool:
        """
        Enable or disable a feature.
        
        Args:
            name: Feature name
            enabled: True to enable, False to disable
            
        Returns:
            True if feature was set successfully
        """
        if name not in self._features:
            logger.warning(f"Unknown feature: {name}")
            return False
        
        feature = self._features[name]
        old_state = feature.enabled
        feature.enabled = enabled
        
        # Check permission if enabling
        if enabled and feature.requires_permission and self.runtime:
            from .runtime import PermissionType
            try:
                perm_type = PermissionType(feature.requires_permission)
                if perm_type not in self.runtime.consent_records or \
                   not self.runtime.consent_records[perm_type].granted:
                    # Request permission
                    granted = await self.runtime.request_consent(perm_type)
                    if not granted:
                        feature.enabled = False
                        logger.warning(f"Permission denied for feature: {name}")
                        return False
            except (ValueError, AttributeError):
                pass  # Permission type not defined, continue
        
        # Update runtime config if available
        if self.runtime and hasattr(self.runtime, 'config'):
            if name in self.runtime.config:
                self.runtime.config[name]['enabled'] = enabled
        
        self._save_feature_states()
        
        if old_state != enabled:
            logger.info(f"Feature {name}: {'enabled' if enabled else 'disabled'}")
            if self.on_feature_change:
                self.on_feature_change(name, enabled)
        
        return True
    
    async def enable_feature(self, name: str) -> bool:
        """Enable a feature"""
        return await self.set_feature(name, True)
    
    async def disable_feature(self, name: str) -> bool:
        """Disable a feature"""
        return await self.set_feature(name, False)
    
    # ========================
    # Status & Information
    # ========================
    
    def get_status(self) -> Dict:
        """
        Get comprehensive status of Victor runtime.
        
        Returns:
            Dictionary with full status information
        """
        status = {
            'version': self.VERSION,
            'runtime_state': 'stopped',
            'features': self.get_features(),
            'timestamp': datetime.now().isoformat()
        }
        
        if self.runtime:
            status['runtime_state'] = self.runtime.state.value
            status['device'] = self.runtime.device_info.to_dict() if self.runtime.device_info else None
            status['permissions'] = {
                k.value: v.granted
                for k, v in self.runtime.consent_records.items()
            }
        
        return status
    
    def get_runtime_state(self) -> str:
        """Get current runtime state"""
        if not self.runtime:
            return 'not_initialized'
        return self.runtime.state.value
    
    # ========================
    # Data Management
    # ========================
    
    def get_data_summary(self) -> Dict:
        """
        Get summary of data stored by Victor.
        
        Returns:
            Dictionary with data storage information
        """
        summary = {
            'config': {
                'path': str(self.config_dir),
                'size_bytes': self._get_dir_size(self.config_dir)
            }
        }
        
        if self.runtime:
            data_dir = self.runtime.data_dir
            summary['runtime_data'] = {
                'path': str(data_dir),
                'size_bytes': self._get_dir_size(data_dir)
            }
            
            # Check for learning data
            learning_dir = data_dir / 'learning'
            if learning_dir.exists():
                summary['learning_data'] = {
                    'path': str(learning_dir),
                    'size_bytes': self._get_dir_size(learning_dir)
                }
        
        return summary
    
    def _get_dir_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0
        try:
            for f in path.rglob('*'):
                if f.is_file():
                    total += f.stat().st_size
        except Exception:
            pass
        return total
    
    async def clear_learning_data(self) -> bool:
        """
        Clear all learning data.
        
        This will reset Victor's learned patterns for this device.
        
        Returns:
            True if data was cleared
        """
        if not self.runtime:
            return False
        
        try:
            learning_dir = self.runtime.data_dir / 'learning'
            if learning_dir.exists():
                import shutil
                shutil.rmtree(learning_dir)
                learning_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("Learning data cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear learning data: {e}")
            return False
    
    async def clear_all_data(self) -> bool:
        """
        Clear all Victor data from this device.
        
        This is a complete reset - use with caution.
        
        Returns:
            True if data was cleared
        """
        try:
            # Stop runtime first
            await self.stop_runtime()
            
            # Clear runtime data
            if self.runtime:
                import shutil
                if self.runtime.data_dir.exists():
                    shutil.rmtree(self.runtime.data_dir)
            
            # Clear config
            if self.config_dir.exists():
                import shutil
                shutil.rmtree(self.config_dir)
                self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Re-initialize features
            self._features.clear()
            self._initialize_features()
            
            logger.info("All Victor data cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear all data: {e}")
            return False
    
    async def export_data(self, export_path: Path) -> bool:
        """
        Export all Victor data (data portability).
        
        Args:
            export_path: Path to export to
            
        Returns:
            True if export successful
        """
        try:
            export_data = {
                'version': self.VERSION,
                'export_date': datetime.now().isoformat(),
                'features': self.get_features(),
                'status': self.get_status()
            }
            
            # Include consent records
            if self.runtime:
                export_data['consents'] = {
                    k.value: v.to_dict()
                    for k, v in self.runtime.consent_records.items()
                }
                export_data['config'] = self.runtime.config
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Data exported to: {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return False
    
    async def import_data(self, import_path: Path) -> bool:
        """
        Import Victor data from export file.
        
        Args:
            import_path: Path to import from
            
        Returns:
            True if import successful
        """
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
            
            # Import features
            if 'features' in data:
                for name, state in data['features'].items():
                    if name in self._features:
                        self._features[name].enabled = state.get('enabled', False)
                self._save_feature_states()
            
            # Import config
            if 'config' in data and self.runtime:
                self.runtime.config.update(data['config'])
                await self.runtime._save_config()
            
            logger.info(f"Data imported from: {import_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to import data: {e}")
            return False
    
    # ========================
    # Privacy Controls
    # ========================
    
    async def request_data_deletion(self) -> Dict:
        """
        Request deletion of all user data (GDPR right to erasure).
        
        Returns:
            Confirmation of deletion request
        """
        deletion_request = {
            'request_id': f"del_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'status': 'processing'
        }
        
        try:
            await self.clear_all_data()
            deletion_request['status'] = 'completed'
            deletion_request['message'] = 'All local data has been deleted'
        except Exception as e:
            deletion_request['status'] = 'failed'
            deletion_request['error'] = str(e)
        
        return deletion_request
    
    def get_privacy_summary(self) -> Dict:
        """
        Get summary of privacy-related settings.
        
        Returns:
            Dictionary with privacy information
        """
        summary = {
            'data_collection': self.is_feature_enabled('learning'),
            'sync_enabled': self.is_feature_enabled('sync'),
            'analytics_enabled': self.is_feature_enabled('analytics'),
            'data_stored_locally': True,
            'third_party_sharing': False
        }
        
        if self.runtime:
            summary['consents'] = {
                k.value: v.granted
                for k, v in self.runtime.consent_records.items()
            }
        
        return summary


# Quick access function
def create_control_panel(runtime=None) -> UserControlPanel:
    """Create a user control panel instance"""
    return UserControlPanel(runtime=runtime)
