#!/usr/bin/env python3
"""
Victor Personal Runtime - Consent Manager
==========================================

Manages user consent for all runtime features. Ensures GDPR compliance
and respects user privacy choices.

All data collection and processing requires explicit user consent that
can be revoked at any time.
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger('victor_runtime.consent')


class ConsentType(Enum):
    """Types of consent that can be requested"""
    DATA_COLLECTION = "data_collection"
    LEARNING = "learning"
    SYNC = "sync"
    OVERLAY = "overlay"
    AUTOMATION = "automation"
    ANALYTICS = "analytics"
    THIRD_PARTY = "third_party"


@dataclass
class ConsentDetails:
    """Detailed consent record with audit trail"""
    consent_type: ConsentType
    granted: bool
    timestamp: str
    version: str
    user_id: str
    ip_hash: Optional[str] = None  # Hashed for privacy
    method: str = "explicit"  # explicit, implicit, inherited
    scope: str = "device"  # device, all_devices
    duration: Optional[str] = None  # None = indefinite
    can_revoke: bool = True
    revocation_history: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'consent_type': self.consent_type.value,
            'granted': self.granted,
            'timestamp': self.timestamp,
            'version': self.version,
            'user_id': self.user_id,
            'ip_hash': self.ip_hash,
            'method': self.method,
            'scope': self.scope,
            'duration': self.duration,
            'can_revoke': self.can_revoke,
            'revocation_history': self.revocation_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConsentDetails':
        return cls(
            consent_type=ConsentType(data['consent_type']),
            granted=data['granted'],
            timestamp=data['timestamp'],
            version=data['version'],
            user_id=data['user_id'],
            ip_hash=data.get('ip_hash'),
            method=data.get('method', 'explicit'),
            scope=data.get('scope', 'device'),
            duration=data.get('duration'),
            can_revoke=data.get('can_revoke', True),
            revocation_history=data.get('revocation_history', [])
        )


class ConsentManager:
    """
    Manages user consent for Victor Personal Runtime.
    
    Features:
    - Clear consent requests with explanations
    - Audit trail of all consent changes
    - Easy revocation of any consent
    - Consent inheritance across devices (optional)
    - Expiring consent support
    
    Usage:
        manager = ConsentManager(data_dir='/path/to/data', user_id='user123')
        
        # Request consent
        if await manager.request_consent(ConsentType.LEARNING, callback):
            # User consented
            pass
        
        # Check consent
        if manager.has_consent(ConsentType.LEARNING):
            # Can proceed with learning
            pass
        
        # Revoke consent
        manager.revoke_consent(ConsentType.LEARNING)
    """
    
    VERSION = "1.0"
    
    # Consent explanations for each type
    CONSENT_EXPLANATIONS = {
        ConsentType.DATA_COLLECTION: {
            'title': 'Data Collection',
            'description': (
                "Victor will collect usage data to improve your experience. "
                "This includes:\n"
                "• App usage patterns\n"
                "• Feature preferences\n"
                "• Interaction history\n\n"
                "All data is stored locally on your device and never shared "
                "without additional consent."
            ),
            'data_types': ['usage_patterns', 'preferences', 'history'],
            'storage': 'local',
            'retention': '90 days'
        },
        ConsentType.LEARNING: {
            'title': 'Personal Learning',
            'description': (
                "Victor can learn from your interactions to become more "
                "helpful over time. This includes:\n"
                "• Learning your preferences\n"
                "• Adapting to your workflow\n"
                "• Remembering your patterns\n\n"
                "All learning happens on your device. No data is sent to "
                "external servers."
            ),
            'data_types': ['preferences', 'patterns', 'interactions'],
            'storage': 'local',
            'retention': 'indefinite'
        },
        ConsentType.SYNC: {
            'title': 'Cross-Device Sync',
            'description': (
                "Sync your Victor settings and learned patterns across "
                "your personal devices. This includes:\n"
                "• Configuration settings\n"
                "• Learned preferences\n"
                "• Session history\n\n"
                "Data is encrypted before sync and only accessible by you."
            ),
            'data_types': ['settings', 'preferences', 'history'],
            'storage': 'encrypted_cloud',
            'retention': 'user_controlled'
        },
        ConsentType.OVERLAY: {
            'title': 'Screen Overlay',
            'description': (
                "Victor can display helpful overlays on your screen. "
                "This includes:\n"
                "• Floating assistant panel\n"
                "• Quick action buttons\n"
                "• Information tooltips\n\n"
                "You can disable this at any time from settings."
            ),
            'data_types': [],
            'storage': 'none',
            'retention': 'none'
        },
        ConsentType.AUTOMATION: {
            'title': 'Task Automation',
            'description': (
                "Victor can automate tasks on your behalf. This includes:\n"
                "• Filling forms\n"
                "• Navigating apps\n"
                "• Executing workflows\n\n"
                "Victor will always ask for confirmation before performing "
                "any automated action."
            ),
            'data_types': [],
            'storage': 'local_log',
            'retention': '30 days'
        },
        ConsentType.ANALYTICS: {
            'title': 'Anonymous Analytics',
            'description': (
                "Help improve Victor by sharing anonymous usage statistics. "
                "This includes:\n"
                "• Feature usage counts\n"
                "• Error reports\n"
                "• Performance metrics\n\n"
                "No personal information is ever collected or shared."
            ),
            'data_types': ['anonymous_stats'],
            'storage': 'external',
            'retention': 'aggregated'
        },
        ConsentType.THIRD_PARTY: {
            'title': 'Third-Party Integrations',
            'description': (
                "Enable integrations with third-party services. "
                "Each integration will request separate consent.\n\n"
                "You control which services Victor can interact with."
            ),
            'data_types': ['varies'],
            'storage': 'varies',
            'retention': 'varies'
        },
    }
    
    def __init__(
        self,
        data_dir: Path,
        user_id: str,
        on_consent_change: Optional[Callable[[ConsentType, bool], None]] = None
    ):
        """
        Initialize the consent manager.
        
        Args:
            data_dir: Directory for storing consent records
            user_id: Unique user identifier
            on_consent_change: Callback when consent status changes
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.user_id = user_id
        self.on_consent_change = on_consent_change
        
        self.consent_file = self.data_dir / 'consent_records.json'
        self.audit_file = self.data_dir / 'consent_audit.json'
        
        self.consents: Dict[ConsentType, ConsentDetails] = {}
        self.audit_log: List[Dict] = []
        
        self._load_consents()
    
    def _load_consents(self):
        """Load consent records from storage"""
        if self.consent_file.exists():
            try:
                with open(self.consent_file, 'r') as f:
                    data = json.load(f)
                    for consent_data in data.get('consents', []):
                        consent = ConsentDetails.from_dict(consent_data)
                        # Check for expiration
                        if self._is_consent_valid(consent):
                            self.consents[consent.consent_type] = consent
            except Exception as e:
                logger.error(f"Failed to load consents: {e}")
        
        if self.audit_file.exists():
            try:
                with open(self.audit_file, 'r') as f:
                    self.audit_log = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load audit log: {e}")
    
    def _save_consents(self):
        """Save consent records to storage"""
        try:
            data = {
                'version': self.VERSION,
                'user_id': self.user_id,
                'updated': datetime.now().isoformat(),
                'consents': [c.to_dict() for c in self.consents.values()]
            }
            with open(self.consent_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            with open(self.audit_file, 'w') as f:
                json.dump(self.audit_log[-1000:], f, indent=2)  # Keep last 1000 entries
                
        except Exception as e:
            logger.error(f"Failed to save consents: {e}")
    
    def _is_consent_valid(self, consent: ConsentDetails) -> bool:
        """Check if consent is still valid (not expired)"""
        if not consent.granted:
            return False
        
        if consent.duration:
            try:
                granted_time = datetime.fromisoformat(consent.timestamp)
                duration_days = int(consent.duration.replace('days', '').strip())
                if datetime.now() > granted_time + timedelta(days=duration_days):
                    return False
            except (ValueError, AttributeError):
                pass
        
        return True
    
    def _log_audit(self, action: str, consent_type: ConsentType, details: Dict):
        """Log consent action to audit trail"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'consent_type': consent_type.value,
            'user_id': self.user_id,
            'details': details
        }
        self.audit_log.append(entry)
        logger.info(f"Consent audit: {action} for {consent_type.value}")
    
    def has_consent(self, consent_type: ConsentType) -> bool:
        """
        Check if user has granted consent.
        
        Args:
            consent_type: Type of consent to check
            
        Returns:
            True if consent is granted and valid
        """
        if consent_type not in self.consents:
            return False
        
        return self._is_consent_valid(self.consents[consent_type])
    
    def get_consent_status(self) -> Dict[str, bool]:
        """Get status of all consent types"""
        return {
            ct.value: self.has_consent(ct)
            for ct in ConsentType
        }
    
    async def request_consent(
        self,
        consent_type: ConsentType,
        ui_callback: Optional[Callable] = None,
        scope: str = "device",
        duration: Optional[str] = None
    ) -> bool:
        """
        Request user consent for a specific type.
        
        Args:
            consent_type: Type of consent to request
            ui_callback: Callback to display consent UI
            scope: 'device' or 'all_devices'
            duration: Optional duration like '90 days'
            
        Returns:
            True if consent granted
        """
        # Get explanation for this consent type
        explanation = self.CONSENT_EXPLANATIONS.get(consent_type, {})
        
        if ui_callback:
            # Use provided UI callback
            granted = await ui_callback(
                title=explanation.get('title', consent_type.value),
                description=explanation.get('description', ''),
                data_types=explanation.get('data_types', []),
                storage=explanation.get('storage', 'local'),
                retention=explanation.get('retention', 'varies')
            )
        else:
            # Console-based fallback
            granted = await self._console_consent_request(consent_type, explanation)
        
        # Record consent
        consent = ConsentDetails(
            consent_type=consent_type,
            granted=granted,
            timestamp=datetime.now().isoformat(),
            version=self.VERSION,
            user_id=self.user_id,
            method='explicit',
            scope=scope,
            duration=duration
        )
        
        self.consents[consent_type] = consent
        self._log_audit('request', consent_type, {
            'granted': granted,
            'scope': scope,
            'duration': duration
        })
        self._save_consents()
        
        # Notify listeners
        if self.on_consent_change:
            try:
                self.on_consent_change(consent_type, granted)
            except Exception as e:
                logger.error(f"Consent change callback error: {e}")
        
        return granted
    
    async def _console_consent_request(
        self,
        consent_type: ConsentType,
        explanation: Dict
    ) -> bool:
        """Console-based consent request fallback"""
        print(f"\n{'='*60}")
        print(f"CONSENT REQUEST: {explanation.get('title', consent_type.value)}")
        print(f"{'='*60}")
        print(explanation.get('description', ''))
        
        if explanation.get('data_types'):
            print(f"\nData collected: {', '.join(explanation['data_types'])}")
        if explanation.get('storage'):
            print(f"Storage: {explanation['storage']}")
        if explanation.get('retention'):
            print(f"Retention: {explanation['retention']}")
        
        print("\nDo you consent? (yes/no)")
        response = input("> ").strip().lower()
        return response in ('yes', 'y', 'grant', 'allow', 'accept')
    
    def grant_consent(
        self,
        consent_type: ConsentType,
        scope: str = "device",
        duration: Optional[str] = None
    ):
        """
        Programmatically grant consent (for testing or migration).
        
        Args:
            consent_type: Type of consent to grant
            scope: 'device' or 'all_devices'
            duration: Optional duration
        """
        consent = ConsentDetails(
            consent_type=consent_type,
            granted=True,
            timestamp=datetime.now().isoformat(),
            version=self.VERSION,
            user_id=self.user_id,
            method='programmatic',
            scope=scope,
            duration=duration
        )
        
        self.consents[consent_type] = consent
        self._log_audit('grant', consent_type, {
            'method': 'programmatic',
            'scope': scope
        })
        self._save_consents()
        
        if self.on_consent_change:
            self.on_consent_change(consent_type, True)
    
    def revoke_consent(self, consent_type: ConsentType, reason: str = "user_request"):
        """
        Revoke previously granted consent.
        
        Args:
            consent_type: Type of consent to revoke
            reason: Reason for revocation
        """
        if consent_type not in self.consents:
            logger.warning(f"No consent record for {consent_type.value}")
            return
        
        consent = self.consents[consent_type]
        
        if not consent.can_revoke:
            logger.warning(f"Consent {consent_type.value} cannot be revoked")
            return
        
        # Add to revocation history
        consent.revocation_history.append({
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'previous_status': consent.granted
        })
        
        consent.granted = False
        consent.timestamp = datetime.now().isoformat()
        
        self._log_audit('revoke', consent_type, {'reason': reason})
        self._save_consents()
        
        if self.on_consent_change:
            self.on_consent_change(consent_type, False)
        
        logger.info(f"Consent revoked: {consent_type.value}")
    
    def revoke_all_consents(self, reason: str = "user_request"):
        """Revoke all granted consents"""
        for consent_type in list(self.consents.keys()):
            self.revoke_consent(consent_type, reason)
    
    def get_consent_details(self, consent_type: ConsentType) -> Optional[Dict]:
        """Get detailed information about a consent"""
        if consent_type not in self.consents:
            return None
        
        consent = self.consents[consent_type]
        explanation = self.CONSENT_EXPLANATIONS.get(consent_type, {})
        
        return {
            'type': consent_type.value,
            'granted': consent.granted,
            'valid': self._is_consent_valid(consent),
            'timestamp': consent.timestamp,
            'method': consent.method,
            'scope': consent.scope,
            'duration': consent.duration,
            'can_revoke': consent.can_revoke,
            'explanation': explanation,
            'history': consent.revocation_history
        }
    
    def get_audit_log(self, consent_type: Optional[ConsentType] = None) -> List[Dict]:
        """
        Get consent audit log.
        
        Args:
            consent_type: Filter by consent type (optional)
            
        Returns:
            List of audit entries
        """
        if consent_type:
            return [
                entry for entry in self.audit_log
                if entry.get('consent_type') == consent_type.value
            ]
        return self.audit_log
    
    def export_consents(self) -> Dict:
        """Export all consent data (for data portability)"""
        return {
            'version': self.VERSION,
            'user_id': self.user_id,
            'export_date': datetime.now().isoformat(),
            'consents': [c.to_dict() for c in self.consents.values()],
            'audit_log': self.audit_log
        }
    
    def delete_all_data(self):
        """
        Delete all consent data (right to be forgotten).
        
        This will:
        1. Delete all consent records
        2. Clear audit log
        3. Remove storage files
        """
        self.consents.clear()
        self.audit_log.clear()
        
        if self.consent_file.exists():
            self.consent_file.unlink()
        
        if self.audit_file.exists():
            self.audit_file.unlink()
        
        logger.info("All consent data deleted")
