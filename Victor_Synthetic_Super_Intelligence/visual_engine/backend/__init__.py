"""
Victor Visual Engine Backend
WebSocket server and integration bridge for Victor's 3D visual presence
"""

from .victor_visual_server import VictorVisualServer, VictorState
from .victor_visual_bridge import VictorVisualBridge

__version__ = "1.0.0"
__all__ = ["VictorVisualServer", "VictorState", "VictorVisualBridge"]
