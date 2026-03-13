"""
NeuroGrid Studio – Enterprise-grade synthetic neural network platform.

Provides a 1024×1024 GridNN architecture with real-time WebGL visualization,
FastAPI WebSocket streaming, and an intelligent auto-ML loop recommender.
"""

from .grid_nn import GridNN, NeuronSymbol, GridCell
from .training import TrainingLoop, AutoMLRecommender, TrainingConfig
from .api import create_app

__all__ = [
    "GridNN",
    "NeuronSymbol",
    "GridCell",
    "TrainingLoop",
    "AutoMLRecommender",
    "TrainingConfig",
    "create_app",
]

__version__ = "0.1.0"
