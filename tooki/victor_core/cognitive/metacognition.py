"""
Metacognitive Loop
==================

Self-monitoring and adaptive strategy system.

Implements metacognitive monitoring, performance assessment, and dynamic
strategy adjustment based on task performance and confidence levels.

Author: Brandon Emery x Victor
License: Proprietary - Massive Magnetics
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time


class PerformanceLevel(Enum):
    """Performance classification levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for a task or operation.
    
    Attributes:
        accuracy: Accuracy score (0.0 to 1.0)
        confidence: Confidence score (0.0 to 1.0)
        latency: Response time in seconds
        error_rate: Error rate (0.0 to 1.0)
        level: Performance level classification
    """
    accuracy: float = 0.0
    confidence: float = 0.0
    latency: float = 0.0
    error_rate: float = 0.0
    level: PerformanceLevel = PerformanceLevel.ADEQUATE
    
    def score(self) -> float:
        """Compute overall performance score."""
        return (self.accuracy * 0.4 + 
                self.confidence * 0.3 + 
                (1 - self.error_rate) * 0.2 +
                max(0, 1 - self.latency / 10) * 0.1)


@dataclass
class Strategy:
    """
    Cognitive strategy configuration.
    
    Attributes:
        name: Strategy name
        learning_rate: Learning rate adjustment
        exploration_rate: Exploration vs exploitation
        attention_focus: Attention allocation weights
        confidence_threshold: Minimum confidence for actions
    """
    name: str
    learning_rate: float = 0.01
    exploration_rate: float = 0.1
    attention_focus: Dict[str, float] = field(default_factory=dict)
    confidence_threshold: float = 0.7


class MetacognitiveLoop:
    """
    Metacognitive monitoring and adaptation system.
    
    Monitors system performance, tracks confidence, and dynamically
    adjusts strategies based on task results.
    
    Example:
        >>> metacog = MetacognitiveLoop()
        >>> results = execute_tasks()
        >>> performance = metacog.monitor(results)
        >>> if performance.confidence < 0.7:
        ...     metacog.adjust_strategy()
        >>> metacog.reflect()
    """
    
    def __init__(self):
        self.current_strategy = Strategy("default")
        self.performance_history: List[PerformanceMetrics] = []
        self.reflections: List[str] = []
        self.adjustments: int = 0
        
    def monitor(self, task_results: Dict[str, Any]) -> PerformanceMetrics:
        """
        Monitor task performance and compute metrics.
        
        Args:
            task_results: Dictionary with task outcomes
            
        Returns:
            PerformanceMetrics object
        """
        accuracy = task_results.get('accuracy', 0.0)
        confidence = task_results.get('confidence', 0.0)
        latency = task_results.get('latency', 0.0)
        errors = task_results.get('errors', 0)
        total = task_results.get('total', 1)
        
        error_rate = errors / max(total, 1)
        
        # Classify performance level
        score = accuracy * 0.6 + confidence * 0.4
        if score >= 0.9:
            level = PerformanceLevel.EXCELLENT
        elif score >= 0.75:
            level = PerformanceLevel.GOOD
        elif score >= 0.6:
            level = PerformanceLevel.ADEQUATE
        elif score >= 0.4:
            level = PerformanceLevel.POOR
        else:
            level = PerformanceLevel.CRITICAL
        
        metrics = PerformanceMetrics(
            accuracy=accuracy,
            confidence=confidence,
            latency=latency,
            error_rate=error_rate,
            level=level
        )
        
        self.performance_history.append(metrics)
        return metrics
    
    def adjust_strategy(self, target_metric: Optional[str] = None) -> Strategy:
        """
        Adjust cognitive strategy based on performance.
        
        Args:
            target_metric: Specific metric to optimize (accuracy, confidence, latency)
            
        Returns:
            Updated strategy
        """
        if not self.performance_history:
            return self.current_strategy
        
        recent_perf = self.performance_history[-5:]  # Last 5 measurements
        avg_confidence = sum(p.confidence for p in recent_perf) / len(recent_perf)
        avg_accuracy = sum(p.accuracy for p in recent_perf) / len(recent_perf)
        
        # Adjust learning rate
        if avg_accuracy < 0.6:
            self.current_strategy.learning_rate *= 1.5
            self.reflections.append(f"Increased learning rate to {self.current_strategy.learning_rate:.4f}")
        elif avg_accuracy > 0.9:
            self.current_strategy.learning_rate *= 0.8
            self.reflections.append(f"Decreased learning rate to {self.current_strategy.learning_rate:.4f}")
        
        # Adjust exploration
        if avg_confidence < 0.5:
            self.current_strategy.exploration_rate = min(0.3, self.current_strategy.exploration_rate * 1.2)
            self.reflections.append(f"Increased exploration to {self.current_strategy.exploration_rate:.2f}")
        
        # Adjust confidence threshold
        if avg_accuracy < avg_confidence - 0.2:  # Overconfident
            self.current_strategy.confidence_threshold += 0.05
            self.reflections.append("Increased confidence threshold (overconfidence detected)")
        
        self.adjustments += 1
        return self.current_strategy
    
    def reflect(self) -> List[str]:
        """
        Generate metacognitive reflections on performance.
        
        Returns:
            List of reflection strings
        """
        if len(self.performance_history) < 2:
            return ["Insufficient data for reflection"]
        
        recent = self.performance_history[-10:]
        trend_confidence = self._compute_trend([p.confidence for p in recent])
        trend_accuracy = self._compute_trend([p.accuracy for p in recent])
        
        reflections = []
        
        if trend_confidence > 0.1:
            reflections.append("Confidence is improving - strategy working well")
        elif trend_confidence < -0.1:
            reflections.append("Confidence declining - may need strategy adjustment")
        
        if trend_accuracy > 0.05:
            reflections.append("Accuracy improving - learning is effective")
        elif trend_accuracy < -0.05:
            reflections.append("Accuracy declining - investigate root cause")
        
        avg_score = sum(p.score() for p in recent) / len(recent)
        if avg_score > 0.8:
            reflections.append("Overall performance is strong")
        elif avg_score < 0.5:
            reflections.append("Performance below target - intervention needed")
        
        self.reflections.extend(reflections)
        return reflections
    
    def _compute_trend(self, values: List[float]) -> float:
        """Compute simple linear trend."""
        if len(values) < 2:
            return 0.0
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        return numerator / denominator if denominator != 0 else 0.0
    
    def get_current_strategy(self) -> Strategy:
        """Get current cognitive strategy."""
        return self.current_strategy
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance history."""
        if not self.performance_history:
            return {"status": "no_data"}
        
        recent = self.performance_history[-20:]
        return {
            "avg_accuracy": sum(p.accuracy for p in recent) / len(recent),
            "avg_confidence": sum(p.confidence for p in recent) / len(recent),
            "avg_latency": sum(p.latency for p in recent) / len(recent),
            "total_adjustments": self.adjustments,
            "recent_level": recent[-1].level.value,
            "measurements": len(self.performance_history)
        }
