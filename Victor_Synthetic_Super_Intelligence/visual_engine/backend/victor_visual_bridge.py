"""
Victor Hub <-> Visual Engine Integration Bridge
Connects the Victor Hub reasoning system to the Visual Engine WebSocket server
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("VictorVisualBridge")


class VictorVisualBridge:
    """Bridge between Victor Hub and Visual Engine"""
    
    def __init__(self, visual_server):
        """
        Args:
            visual_server: Instance of VictorVisualServer
        """
        self.visual_server = visual_server
        self.current_state = {
            "emotion": "calm_focus",
            "energy": 0.5,
            "mode": "advisor"
        }
        logger.info("Victor Visual Bridge initialized")
    
    async def send_response(self, text: str, emotion: str = "calm_focus", 
                           energy: float = 0.5, mode: str = "advisor"):
        """
        Send Victor's response to the visual engine
        
        Args:
            text: Victor's response text
            emotion: Current emotional state
            energy: Energy level (0.0 to 1.0)
            mode: Operational mode
        """
        # Generate phonemes (in production, use actual TTS)
        phonemes = self.visual_server._generate_demo_phonemes(text)
        
        # Update visual state
        await self.visual_server.update_victor_state(
            text=text,
            emotion=emotion,
            energy=energy,
            mode=mode,
            phonemes=phonemes,
            audio_path=""  # Would be actual audio file path
        )
        
        # Update internal state
        self.current_state = {
            "emotion": emotion,
            "energy": energy,
            "mode": mode
        }
        
        logger.info(f"Sent to visual: '{text}' ({emotion}, {energy})")
    
    def map_task_to_emotion(self, task_type: str, complexity: str) -> tuple:
        """
        Map task characteristics to visual emotion and energy
        
        Returns:
            (emotion, energy) tuple
        """
        emotion_map = {
            "general": ("calm_focus", 0.5),
            "analysis": ("thinking", 0.7),
            "research": ("analyzing", 0.8),
            "creative": ("creative", 0.6),
            "urgent": ("alert", 0.9),
            "error": ("concerned", 0.4)
        }
        
        complexity_energy = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.8
        }
        
        base_emotion, base_energy = emotion_map.get(task_type, ("calm_focus", 0.5))
        energy_modifier = complexity_energy.get(complexity, 0.5)
        
        return base_emotion, min(1.0, (base_energy + energy_modifier) / 2)
    
    async def show_thinking(self, message: str = "Processing..."):
        """Show Victor in thinking state"""
        await self.send_response(
            text=message,
            emotion="thinking",
            energy=0.7,
            mode="processing"
        )
    
    async def show_success(self, message: str):
        """Show Victor in confident/success state"""
        await self.send_response(
            text=message,
            emotion="confident",
            energy=0.6,
            mode="complete"
        )
    
    async def show_error(self, message: str):
        """Show Victor in concerned/error state"""
        await self.send_response(
            text=message,
            emotion="concerned",
            energy=0.4,
            mode="error"
        )
    
    async def show_idle(self):
        """Show Victor in idle/ready state"""
        await self.send_response(
            text="I am Victor. Ask.",
            emotion="calm_focus",
            energy=0.3,
            mode="idle"
        )


# Integration with Victor Hub Task Execution
async def wrap_task_execution(hub, task, bridge: VictorVisualBridge):
    """
    Wrap task execution with visual feedback
    
    Args:
        hub: VictorHub instance
        task: Task to execute
        bridge: VictorVisualBridge instance
    """
    # Show thinking state
    await bridge.show_thinking(f"Processing: {task.description}")
    
    # Execute task
    result = hub.execute_task(task)
    
    # Show result
    if result.status == "success":
        await bridge.show_success(f"Complete: {result.output}")
    else:
        await bridge.show_error(f"Error: {result.error}")
    
    return result


# Example integration function
async def run_visual_victor_hub(hub, visual_server):
    """
    Run Victor Hub with visual engine integration
    
    Args:
        hub: VictorHub instance
        visual_server: VictorVisualServer instance
    """
    # Create bridge
    bridge = VictorVisualBridge(visual_server)
    
    # Start visual server
    server_task = asyncio.create_task(visual_server.start())
    
    # Wait for server to start
    await asyncio.sleep(1)
    
    # Show idle state
    await bridge.show_idle()
    
    # Process tasks with visual feedback
    # This would integrate with hub's task queue
    # For now, just keep server running
    
    await server_task
