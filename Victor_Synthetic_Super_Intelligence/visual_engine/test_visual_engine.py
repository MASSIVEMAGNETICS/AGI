"""
Test script for Victor Visual Engine
Tests WebSocket server and basic functionality
"""

import sys
import os
import asyncio
import json
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visual_engine.backend.victor_visual_server import VictorVisualServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VictorVisualTest")


async def test_server():
    """Test the visual server with simulated messages"""
    logger.info("Starting Victor Visual Engine Test")
    
    # Create server
    server = VictorVisualServer(host="127.0.0.1", port=8765)
    
    # Start server in background
    server_task = asyncio.create_task(server.start())
    
    # Wait for server to initialize
    await asyncio.sleep(2)
    logger.info("Server started successfully")
    
    # Simulate Victor speaking different phrases with different emotions
    test_cases = [
        {
            "text": "I am Victor. Ask.",
            "emotion": "calm_focus",
            "energy": 0.3,
            "mode": "idle"
        },
        {
            "text": "Let me analyze that request...",
            "emotion": "thinking",
            "energy": 0.7,
            "mode": "processing"
        },
        {
            "text": "I have the answer you seek!",
            "emotion": "confident",
            "energy": 0.6,
            "mode": "advisor"
        },
        {
            "text": "Warning: Critical system state detected!",
            "emotion": "alert",
            "energy": 0.9,
            "mode": "alert"
        },
        {
            "text": "Creating something new...",
            "emotion": "creative",
            "energy": 0.6,
            "mode": "generating"
        },
    ]
    
    logger.info("Running test sequence...")
    
    for i, test_case in enumerate(test_cases):
        await asyncio.sleep(5)  # Wait between messages
        
        logger.info(f"\n--- Test {i+1}/{len(test_cases)} ---")
        logger.info(f"Text: {test_case['text']}")
        logger.info(f"Emotion: {test_case['emotion']} (Energy: {test_case['energy']})")
        
        # Generate phonemes
        phonemes = server._generate_demo_phonemes(test_case['text'])
        
        # Send update
        await server.update_victor_state(
            text=test_case['text'],
            emotion=test_case['emotion'],
            energy=test_case['energy'],
            mode=test_case['mode'],
            phonemes=phonemes,
            audio_path=""
        )
        
        logger.info(f"Sent {len(phonemes)} phonemes")
    
    logger.info("\n✓ Test sequence complete")
    logger.info("Server will continue running. Press Ctrl+C to stop.")
    logger.info("Connect Godot client to ws://127.0.0.1:8765 to see visualizations")
    
    # Keep server running
    await server_task


def main():
    """Run the test"""
    try:
        asyncio.run(test_server())
    except KeyboardInterrupt:
        logger.info("\nTest stopped by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
