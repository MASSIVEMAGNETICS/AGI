#!/usr/bin/env python3
"""
Victor Visual Engine Launcher
Starts the WebSocket server for the visual engine

Usage:
    python launch_visual_engine.py              # Normal mode
    python launch_visual_engine.py --demo       # Demo mode with test messages
    python launch_visual_engine.py --help       # Show help
"""

import sys
import os

# Add visual_engine to path
sys.path.insert(0, os.path.dirname(__file__))

from visual_engine.backend.victor_visual_server import main

if __name__ == "__main__":
    main()
