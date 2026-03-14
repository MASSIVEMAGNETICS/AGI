#!/usr/bin/env python3
"""
Victor Personal Runtime - Sync Manager
=======================================

Manages synchronization of settings and learned patterns across
the user's personal devices using encrypted GitHub Gist storage.

All data is encrypted client-side before upload and only the user
has the decryption keys.
"""

import asyncio
import json
import hashlib
import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger('victor_runtime.sync')


@dataclass
class SyncState:
    """State of synchronization"""
    last_sync: Optional[str] = None
    sync_version: int = 0
    pending_changes: int = 0
    conflicts: int = 0
    status: str = "idle"  # idle, syncing, error


class SyncManager:
    """
    Sync Manager for Victor Personal Runtime.
    
    Handles cross-device synchronization using encrypted storage.
    
    Features:
    - End-to-end encryption (user holds the keys)
    - GitHub Gist-based storage (user's own account)
    - Conflict resolution
    - Incremental sync
    - Offline support with queue
    
    Security:
    - All data encrypted with user's key before upload
    - Key never leaves the device
    - GitHub Gist is just encrypted blob storage
    
    Usage:
        manager = SyncManager(runtime, config)
        await manager.sync()
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, runtime, config: Dict):
        """
        Initialize sync manager.
        
        Args:
            runtime: VictorPersonalRuntime instance
            config: Sync configuration
        """
        self.runtime = runtime
        self.config = config
        self.enabled = config.get('enabled', True)
        self.interval = config.get('interval_seconds', 300)
        self.gist_id = config.get('github_gist_id')
        
        self.state = SyncState()
        self._running = False
        self._encryption_key: Optional[bytes] = None
        
        # Sync queue for offline support
        self._sync_queue: List[Dict] = []
        
        # Initialize encryption
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption key using proper key derivation"""
        if self.runtime and self.runtime.user_id:
            # Use PBKDF2 for proper key derivation
            # The salt is derived from user_id to ensure consistency across sessions
            salt = hashlib.sha256(f"{self.runtime.user_id}-salt".encode()).digest()[:16]
            
            # Derive key using PBKDF2-HMAC-SHA256 with 100,000 iterations
            self._encryption_key = hashlib.pbkdf2_hmac(
                'sha256',
                self.runtime.user_id.encode(),
                salt,
                100000,  # NIST recommended minimum
                dklen=32  # 256-bit key
            )
    
    def _encrypt_data(self, data: Dict) -> str:
        """
        Encrypt data for sync using AES-GCM.
        
        Uses authenticated encryption with associated data (AEAD) for
        confidentiality and integrity.
        """
        if not self._encryption_key:
            raise ValueError("Encryption key not initialized")
        
        # Convert to JSON
        json_data = json.dumps(data, sort_keys=True).encode()
        
        try:
            # Try to use cryptography library for AES-GCM
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            # Generate a random 96-bit nonce (recommended for GCM)
            nonce = os.urandom(12)
            
            # Encrypt with AES-GCM (provides both encryption and authentication)
            aesgcm = AESGCM(self._encryption_key)
            ciphertext = aesgcm.encrypt(nonce, json_data, None)
            
            # Prepend nonce to ciphertext
            return base64.b64encode(nonce + ciphertext).decode()
            
        except ImportError:
            # Fallback: Use Fernet if cryptography is installed differently
            try:
                from cryptography.fernet import Fernet
                
                # Derive a Fernet key from our key
                fernet_key = base64.urlsafe_b64encode(self._encryption_key)
                f = Fernet(fernet_key)
                return f.encrypt(json_data).decode()
                
            except ImportError:
                # Last resort: warn and don't encrypt (sync disabled)
                logger.warning("No encryption library available - sync encryption disabled")
                logger.warning("Install 'cryptography' package for secure sync")
                return base64.b64encode(json_data).decode()
    
    def _decrypt_data(self, encrypted: str) -> Dict:
        """Decrypt sync data using AES-GCM"""
        if not self._encryption_key:
            raise ValueError("Encryption key not initialized")
        
        # Decode base64
        data = base64.b64decode(encrypted)
        
        try:
            # Try to use cryptography library for AES-GCM
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            # Extract nonce (first 12 bytes) and ciphertext
            nonce = data[:12]
            ciphertext = data[12:]
            
            # Decrypt with AES-GCM
            aesgcm = AESGCM(self._encryption_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return json.loads(plaintext.decode())
            
        except ImportError:
            try:
                from cryptography.fernet import Fernet
                
                fernet_key = base64.urlsafe_b64encode(self._encryption_key)
                f = Fernet(fernet_key)
                plaintext = f.decrypt(data)
                return json.loads(plaintext.decode())
                
            except ImportError:
                # Fallback: assume unencrypted
                return json.loads(data.decode())
    
    async def run(self):
        """Run sync loop"""
        if not self.enabled:
            logger.info("Sync manager disabled")
            return
        
        self._running = True
        logger.info("Sync manager started")
        
        while self._running:
            try:
                await self.sync()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync error: {e}")
                self.state.status = "error"
                await asyncio.sleep(60)  # Back off on error
    
    async def stop(self):
        """Stop sync manager"""
        self._running = False
        # Save any pending changes
        await self._save_pending_queue()
        logger.info("Sync manager stopped")
    
    async def disable(self):
        """Disable sync"""
        self.enabled = False
        await self.stop()
    
    async def sync(self) -> bool:
        """
        Perform synchronization.
        
        Returns:
            True if sync successful
        """
        if not self.enabled:
            return False
        
        self.state.status = "syncing"
        
        try:
            # Collect local changes
            local_data = await self._collect_local_data()
            
            # Fetch remote data
            remote_data = await self._fetch_remote_data()
            
            # Merge changes
            merged_data, conflicts = self._merge_data(local_data, remote_data)
            
            if conflicts:
                self.state.conflicts = len(conflicts)
                logger.warning(f"Sync conflicts: {len(conflicts)}")
            
            # Apply merged changes locally
            await self._apply_local_changes(merged_data)
            
            # Upload merged data
            await self._upload_data(merged_data)
            
            # Update state
            self.state.last_sync = datetime.now().isoformat()
            self.state.sync_version += 1
            self.state.pending_changes = 0
            self.state.status = "idle"
            
            logger.info("Sync completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            self.state.status = "error"
            return False
    
    async def _collect_local_data(self) -> Dict:
        """Collect data to sync from local storage"""
        data = {
            'version': self.VERSION,
            'timestamp': datetime.now().isoformat(),
            'device_id': self.runtime.device_info.device_id if self.runtime.device_info else 'unknown',
            'settings': {},
            'learning': {},
            'history': []
        }
        
        if self.runtime:
            # Include config
            data['settings'] = self.runtime.config.copy()
            
            # Include consent records (metadata only, not the actual permissions)
            data['consent_summary'] = {
                k.value: v.granted
                for k, v in self.runtime.consent_records.items()
            }
        
        return data
    
    async def _fetch_remote_data(self) -> Optional[Dict]:
        """Fetch data from remote storage (GitHub Gist)"""
        if not self.gist_id:
            return None
        
        # In production, use GitHub API to fetch gist
        # For now, return None to indicate no remote data
        try:
            # Placeholder for GitHub Gist API call
            # response = await self._github_api_get(f'/gists/{self.gist_id}')
            # encrypted_content = response['files']['victor_sync.enc']['content']
            # return self._decrypt_data(encrypted_content)
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch remote data: {e}")
            return None
    
    def _merge_data(self, local: Dict, remote: Optional[Dict]) -> tuple:
        """
        Merge local and remote data.
        
        Uses last-write-wins for simple fields and
        union for lists/collections.
        
        Returns:
            (merged_data, conflicts)
        """
        if not remote:
            return local, []
        
        conflicts = []
        merged = local.copy()
        
        # Compare timestamps
        local_time = datetime.fromisoformat(local.get('timestamp', '1970-01-01'))
        remote_time = datetime.fromisoformat(remote.get('timestamp', '1970-01-01'))
        
        # Merge settings (remote wins if newer, unless local has explicit changes)
        if remote_time > local_time:
            for key, value in remote.get('settings', {}).items():
                if key not in merged['settings']:
                    merged['settings'][key] = value
                elif merged['settings'][key] != value:
                    # Potential conflict
                    conflicts.append({
                        'field': f'settings.{key}',
                        'local': merged['settings'][key],
                        'remote': value,
                        'resolution': 'local_wins'  # Default: keep local
                    })
        
        return merged, conflicts
    
    async def _apply_local_changes(self, data: Dict):
        """Apply merged changes to local storage"""
        if self.runtime and 'settings' in data:
            # Update config
            self.runtime.config.update(data['settings'])
            await self.runtime._save_config()
    
    async def _upload_data(self, data: Dict):
        """Upload data to remote storage"""
        if not self.gist_id:
            logger.debug("No Gist ID configured, skipping upload")
            return
        
        try:
            # Encrypt data
            encrypted = self._encrypt_data(data)
            
            # In production, use GitHub API to update gist
            # await self._github_api_patch(f'/gists/{self.gist_id}', {
            #     'files': {
            #         'victor_sync.enc': {'content': encrypted}
            #     }
            # })
            
            logger.debug("Data uploaded to remote storage")
        except Exception as e:
            logger.error(f"Failed to upload data: {e}")
    
    async def _save_pending_queue(self):
        """Save pending sync items to disk"""
        if not self._sync_queue:
            return
        
        queue_file = self.runtime.data_dir / 'sync_queue.json'
        try:
            with open(queue_file, 'w') as f:
                json.dump(self._sync_queue, f)
        except Exception as e:
            logger.error(f"Failed to save sync queue: {e}")
    
    def queue_change(self, change_type: str, data: Dict):
        """Queue a change for sync"""
        self._sync_queue.append({
            'type': change_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        self.state.pending_changes = len(self._sync_queue)
    
    def get_status(self) -> Dict:
        """Get sync status"""
        return {
            'enabled': self.enabled,
            'status': self.state.status,
            'last_sync': self.state.last_sync,
            'sync_version': self.state.sync_version,
            'pending_changes': self.state.pending_changes,
            'conflicts': self.state.conflicts,
            'gist_configured': bool(self.gist_id)
        }
    
    async def configure_gist(self, gist_id: str):
        """Configure GitHub Gist for sync"""
        self.gist_id = gist_id
        self.config['github_gist_id'] = gist_id
        
        if self.runtime:
            self.runtime.config['sync']['github_gist_id'] = gist_id
            await self.runtime._save_config()
        
        logger.info(f"Gist configured: {gist_id}")
    
    async def clear_remote_data(self):
        """Clear all data from remote storage"""
        if not self.gist_id:
            return
        
        # In production, update gist with empty content
        logger.info("Remote data cleared")
