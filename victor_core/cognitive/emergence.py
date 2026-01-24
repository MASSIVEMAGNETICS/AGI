"""
Emergence System
================

Detects and analyzes emergent patterns in complex systems.

Identifies phase transitions, self-organization, and emergent behaviors
in multi-agent systems and neural networks.

Author: Brandon Emery x Victor
License: Proprietary - Massive Magnetics
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class EmergentPattern:
    """
    Represents an detected emergent pattern.
    
    Attributes:
        name: Pattern name
        strength: Pattern strength (0.0 to 1.0)
        components: Participating components
        description: Human-readable description
    """
    name: str
    strength: float
    components: List[str]
    description: str = ""


class EmergenceSystem:
    """
    Emergence detection and analysis system.
    
    Monitors system states over time to detect emergent behaviors,
    self-organization, and phase transitions.
    
    Example:
        >>> emergence = EmergenceSystem()
        >>> for state in system_states:
        ...     emergence.observe(state)
        >>> patterns = emergence.detect_patterns()
        >>> print(f"Found {len(patterns)} emergent patterns")
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.state_history: List[Dict[str, Any]] = []
        self.patterns: List[EmergentPattern] = []
        
    def observe(self, state: Dict[str, Any]) -> None:
        """
        Observe a system state.
        
        Args:
            state: Dictionary with system state variables
        """
        self.state_history.append(state)
        
        # Keep only recent history
        if len(self.state_history) > self.window_size:
            self.state_history.pop(0)
    
    def detect_patterns(self) -> List[EmergentPattern]:
        """
        Detect emergent patterns in observed states.
        
        Returns:
            List of detected EmergentPattern objects
        """
        if len(self.state_history) < 10:
            return []
        
        patterns = []
        
        # Detect synchronization
        sync_pattern = self._detect_synchronization()
        if sync_pattern:
            patterns.append(sync_pattern)
        
        # Detect clustering
        cluster_pattern = self._detect_clustering()
        if cluster_pattern:
            patterns.append(cluster_pattern)
        
        # Detect phase transitions
        transition = self._detect_phase_transition()
        if transition:
            patterns.append(transition)
        
        self.patterns = patterns
        return patterns
    
    def _detect_synchronization(self) -> Optional[EmergentPattern]:
        """Detect synchronization among components."""
        # Extract numeric values
        values = self._extract_numeric_values()
        if not values or len(values) < 2:
            return None
        
        # Compute correlation matrix
        correlations = []
        keys = list(values.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                key1, key2 = keys[i], keys[j]
                if len(values[key1]) > 1 and len(values[key2]) > 1:
                    corr = np.corrcoef(values[key1], values[key2])[0, 1]
                    if not np.isnan(corr):
                        correlations.append(abs(corr))
        
        if correlations and np.mean(correlations) > 0.7:
            return EmergentPattern(
                name="synchronization",
                strength=float(np.mean(correlations)),
                components=list(values.keys()),
                description="Components showing synchronized behavior"
            )
        
        return None
    
    def _detect_clustering(self) -> Optional[EmergentPattern]:
        """Detect clustering of component values."""
        values = self._extract_numeric_values()
        if not values:
            return None
        
        # Check if values cluster into groups
        recent_values = {k: v[-1] if v else 0 for k, v in values.items()}
        if len(recent_values) < 3:
            return None
        
        vals = np.array(list(recent_values.values()))
        std = np.std(vals)
        mean = np.mean(vals)
        
        # Low variance indicates clustering
        if std < 0.2 * abs(mean) and mean != 0:
            return EmergentPattern(
                name="clustering",
                strength=1.0 - (std / (abs(mean) + 1e-8)),
                components=list(recent_values.keys()),
                description="Components clustering around common values"
            )
        
        return None
    
    def _detect_phase_transition(self) -> Optional[EmergentPattern]:
        """Detect phase transitions in system behavior."""
        if len(self.state_history) < 20:
            return None
        
        # Look for sudden changes in variance
        values = self._extract_numeric_values()
        if not values:
            return None
        
        for key, vals in values.items():
            if len(vals) < 20:
                continue
            
            # Split into two halves
            mid = len(vals) // 2
            first_half = vals[:mid]
            second_half = vals[mid:]
            
            var1 = np.var(first_half)
            var2 = np.var(second_half)
            
            # Significant change in variance indicates phase transition
            if var2 > 2 * var1 or var1 > 2 * var2:
                strength = abs(var2 - var1) / (var1 + var2 + 1e-8)
                return EmergentPattern(
                    name="phase_transition",
                    strength=min(1.0, strength),
                    components=[key],
                    description=f"Phase transition detected in {key}"
                )
        
        return None
    
    def _extract_numeric_values(self) -> Dict[str, List[float]]:
        """Extract numeric time series from state history."""
        values: Dict[str, List[float]] = {}
        
        for state in self.state_history:
            for key, value in state.items():
                if isinstance(value, (int, float)):
                    if key not in values:
                        values[key] = []
                    values[key].append(float(value))
        
        return values
    
    def get_complexity(self) -> float:
        """
        Compute system complexity measure.
        
        Returns:
            Complexity score (0.0 to 1.0)
        """
        if len(self.state_history) < 10:
            return 0.0
        
        values = self._extract_numeric_values()
        if not values:
            return 0.0
        
        # Complexity based on entropy and variance
        complexities = []
        for vals in values.values():
            if len(vals) > 1:
                # Normalized variance
                var = np.var(vals)
                mean = np.mean(vals)
                complexity = var / (mean ** 2 + 1) if mean != 0 else var
                complexities.append(min(1.0, complexity))
        
        return float(np.mean(complexities)) if complexities else 0.0
    
    def clear(self) -> None:
        """Clear observation history."""
        self.state_history.clear()
        self.patterns.clear()
