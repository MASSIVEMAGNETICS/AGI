#!/usr/bin/env python3
"""
Victor Personal Runtime - Personal Learning Engine
===================================================

On-device machine learning that adapts to user behavior.
All learning happens locally - data never leaves the device.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger('victor_runtime.learning')


@dataclass
class LearningPattern:
    """A learned pattern about user behavior"""
    pattern_id: str
    pattern_type: str
    data: Dict
    confidence: float
    created: str
    last_updated: str
    observation_count: int = 1


class PersonalLearningEngine:
    """
    Personal Learning Engine for Victor.
    
    Learns user patterns and preferences locally on the device.
    No data is ever sent to external servers.
    
    Features:
    - Usage pattern learning
    - Preference inference
    - Behavior prediction
    - Context awareness
    - Privacy-preserving federated learning (opt-in)
    
    All learning is:
    - Local to the device
    - User-controllable (can be reset)
    - Transparent (user can see what was learned)
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, data_dir: Path, config: Dict):
        """
        Initialize learning engine.
        
        Args:
            data_dir: Directory for storing learned patterns
            config: Learning configuration
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config = config
        
        self.enabled = config.get('enabled', True)
        self.local_only = config.get('local_only', True)
        
        self.patterns_file = self.data_dir / 'patterns.json'
        self.patterns: Dict[str, LearningPattern] = {}
        
        self._running = False
        self._observation_queue: List[Dict] = []
        
        self._load_patterns()
    
    def _load_patterns(self):
        """Load learned patterns from storage"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                    for pattern_data in data.get('patterns', []):
                        pattern = LearningPattern(
                            pattern_id=pattern_data['pattern_id'],
                            pattern_type=pattern_data['pattern_type'],
                            data=pattern_data['data'],
                            confidence=pattern_data['confidence'],
                            created=pattern_data['created'],
                            last_updated=pattern_data['last_updated'],
                            observation_count=pattern_data.get('observation_count', 1)
                        )
                        self.patterns[pattern.pattern_id] = pattern
            except Exception as e:
                logger.error(f"Failed to load patterns: {e}")
    
    def _save_patterns(self):
        """Save learned patterns to storage"""
        try:
            data = {
                'version': self.VERSION,
                'updated': datetime.now().isoformat(),
                'patterns': [
                    {
                        'pattern_id': p.pattern_id,
                        'pattern_type': p.pattern_type,
                        'data': p.data,
                        'confidence': p.confidence,
                        'created': p.created,
                        'last_updated': p.last_updated,
                        'observation_count': p.observation_count
                    }
                    for p in self.patterns.values()
                ]
            }
            with open(self.patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")
    
    async def run(self):
        """Run learning engine"""
        if not self.enabled:
            logger.info("Learning engine disabled")
            return
        
        self._running = True
        logger.info("Learning engine started")
        
        while self._running:
            try:
                # Process queued observations
                await self._process_observations()
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Learning error: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop learning engine"""
        self._running = False
        self._save_patterns()
        logger.info("Learning engine stopped")
    
    def observe(self, observation_type: str, data: Dict):
        """
        Record an observation for learning.
        
        Args:
            observation_type: Type of observation (e.g., 'app_usage', 'command')
            data: Observation data
        """
        if not self.enabled:
            return
        
        self._observation_queue.append({
            'type': observation_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    async def _process_observations(self):
        """Process queued observations"""
        if not self._observation_queue:
            return
        
        # Process in batches
        batch = self._observation_queue[:100]
        self._observation_queue = self._observation_queue[100:]
        
        for obs in batch:
            await self._learn_from_observation(obs)
        
        self._save_patterns()
    
    async def _learn_from_observation(self, observation: Dict):
        """Learn from a single observation"""
        obs_type = observation['type']
        data = observation['data']
        
        if obs_type == 'app_usage':
            await self._learn_app_usage(data)
        elif obs_type == 'command':
            await self._learn_command_pattern(data)
        elif obs_type == 'time_pattern':
            await self._learn_time_pattern(data)
        elif obs_type == 'preference':
            await self._learn_preference(data)
    
    async def _learn_app_usage(self, data: Dict):
        """Learn from app usage patterns"""
        app_name = data.get('app_name', 'unknown')
        pattern_id = f"app_usage_{app_name}"
        
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.observation_count += 1
            pattern.confidence = min(1.0, pattern.confidence + 0.01)
            pattern.last_updated = datetime.now().isoformat()
        else:
            self.patterns[pattern_id] = LearningPattern(
                pattern_id=pattern_id,
                pattern_type='app_usage',
                data={'app_name': app_name, 'usage_count': 1},
                confidence=0.1,
                created=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
    
    async def _learn_command_pattern(self, data: Dict):
        """Learn from command patterns"""
        command = data.get('command', '')
        pattern_id = f"command_{hash(command) % 10000}"
        
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.observation_count += 1
            pattern.confidence = min(1.0, pattern.confidence + 0.05)
            pattern.last_updated = datetime.now().isoformat()
        else:
            self.patterns[pattern_id] = LearningPattern(
                pattern_id=pattern_id,
                pattern_type='command',
                data={'command_prefix': command[:50]},
                confidence=0.1,
                created=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
    
    async def _learn_time_pattern(self, data: Dict):
        """Learn from time-based patterns"""
        hour = data.get('hour', 0)
        pattern_id = f"time_{hour}"
        
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.observation_count += 1
            pattern.last_updated = datetime.now().isoformat()
        else:
            self.patterns[pattern_id] = LearningPattern(
                pattern_id=pattern_id,
                pattern_type='time_pattern',
                data={'hour': hour, 'activity_level': 1},
                confidence=0.1,
                created=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
    
    async def _learn_preference(self, data: Dict):
        """Learn from user preferences"""
        pref_key = data.get('key', '')
        pref_value = data.get('value', '')
        pattern_id = f"pref_{pref_key}"
        
        self.patterns[pattern_id] = LearningPattern(
            pattern_id=pattern_id,
            pattern_type='preference',
            data={'key': pref_key, 'value': pref_value},
            confidence=1.0,  # Explicit preference is high confidence
            created=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
    
    def get_patterns(self, pattern_type: Optional[str] = None) -> List[Dict]:
        """
        Get learned patterns.
        
        Args:
            pattern_type: Filter by type (optional)
            
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        for pattern in self.patterns.values():
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            patterns.append({
                'id': pattern.pattern_id,
                'type': pattern.pattern_type,
                'data': pattern.data,
                'confidence': pattern.confidence,
                'observations': pattern.observation_count
            })
        return patterns
    
    def predict(self, context: Dict) -> List[Dict]:
        """
        Make predictions based on learned patterns.
        
        Args:
            context: Current context
            
        Returns:
            List of predictions with confidence scores
        """
        predictions = []
        
        # Example: Predict based on time
        current_hour = datetime.now().hour
        time_pattern_id = f"time_{current_hour}"
        if time_pattern_id in self.patterns:
            pattern = self.patterns[time_pattern_id]
            predictions.append({
                'type': 'time_based',
                'confidence': pattern.confidence,
                'suggestion': f'Activity pattern detected for this time'
            })
        
        # Add more prediction logic as needed
        
        return sorted(predictions, key=lambda x: x['confidence'], reverse=True)
    
    def clear_patterns(self, pattern_type: Optional[str] = None):
        """
        Clear learned patterns.
        
        Args:
            pattern_type: Clear only this type (optional, clears all if None)
        """
        if pattern_type:
            self.patterns = {
                k: v for k, v in self.patterns.items()
                if v.pattern_type != pattern_type
            }
        else:
            self.patterns.clear()
        
        self._save_patterns()
        logger.info(f"Patterns cleared: {pattern_type or 'all'}")
    
    def get_summary(self) -> Dict:
        """Get learning summary"""
        types = {}
        for pattern in self.patterns.values():
            if pattern.pattern_type not in types:
                types[pattern.pattern_type] = 0
            types[pattern.pattern_type] += 1
        
        return {
            'enabled': self.enabled,
            'local_only': self.local_only,
            'total_patterns': len(self.patterns),
            'patterns_by_type': types,
            'pending_observations': len(self._observation_queue)
        }
