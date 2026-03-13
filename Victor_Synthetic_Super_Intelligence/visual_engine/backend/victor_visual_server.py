"""
Victor Visual Engine - WebSocket Server
Version: 1.0.0
Author: MASSIVEMAGNETICS

WebSocket server that bridges Victor Core with the Godot Visual Engine.
Provides real-time state updates for emotion, energy, and phoneme data.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import websockets
from websockets.server import WebSocketServerProtocol

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VictorVisualServer")


@dataclass
class Phoneme:
    """Phoneme timing data for lip sync"""
    p: str  # Phoneme code (e.g., "AY", "AE", "M", "B")
    t: float  # Time in seconds


@dataclass
class VictorState:
    """Victor's current visual state"""
    text: str
    emotion: str = "calm_focus"
    energy: float = 0.5
    aura: str = "teal"
    mode: str = "advisor"
    phonemes: List[Dict[str, Any]] = None
    audio_path: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if self.phonemes is None:
            data['phonemes'] = []
        return data


class VictorVisualServer:
    """WebSocket server for Victor Visual Engine"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: set = set()
        self.current_state = VictorState(text="", emotion="calm_focus")
        self.running = False
        logger.info(f"Victor Visual Server initialized on {host}:{port}")
    
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send current state to new client
        await websocket.send(json.dumps(self.current_state.to_dict()))
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a client connection"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast_state(self, state: VictorState):
        """Broadcast state to all connected clients"""
        self.current_state = state
        message = json.dumps(state.to_dict())
        
        if self.clients:
            logger.info(f"Broadcasting to {len(self.clients)} clients: {state.emotion}")
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle client connection and messages"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                # Handle incoming messages from Godot client
                try:
                    data = json.loads(message)
                    await self.process_client_message(websocket, data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from client: {e}")
                    await websocket.send(json.dumps({"error": "Invalid JSON"}))
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        finally:
            await self.unregister_client(websocket)
    
    async def process_client_message(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Process messages from Godot client"""
        msg_type = data.get("type", "unknown")
        
        if msg_type == "ping":
            # Respond to ping
            await websocket.send(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
        elif msg_type == "request_state":
            # Send current state
            await websocket.send(json.dumps(self.current_state.to_dict()))
        elif msg_type == "update_user_input":
            # Handle user input from Godot UI (e.g., cursor position, mic input)
            logger.info(f"User input: {data}")
            # TODO: Forward to Victor Core for processing
        else:
            logger.warning(f"Unknown message type: {msg_type}")
    
    async def update_victor_state(self, text: str, emotion: str = "calm_focus", 
                                   energy: float = 0.5, mode: str = "advisor",
                                   phonemes: Optional[List[Dict[str, Any]]] = None,
                                   audio_path: str = ""):
        """Update Victor's state (called by Victor Core)"""
        state = VictorState(
            text=text,
            emotion=emotion,
            energy=energy,
            aura=self._get_aura_color(emotion),
            mode=mode,
            phonemes=phonemes or [],
            audio_path=audio_path
        )
        await self.broadcast_state(state)
    
    def _get_aura_color(self, emotion: str) -> str:
        """Map emotion to aura color"""
        emotion_to_color = {
            "calm_focus": "teal",
            "thinking": "blue",
            "excited": "gold",
            "concerned": "orange",
            "alert": "red",
            "confident": "purple",
            "analyzing": "cyan",
            "creative": "magenta",
            "glitch": "white",
            "prophetic": "violet"
        }
        return emotion_to_color.get(emotion, "teal")
    
    async def simulate_speech(self, text: str):
        """Simulate Victor speaking (demo mode)"""
        # Generate simple phoneme timing for demo
        # In production, this would come from TTS engine
        phonemes = self._generate_demo_phonemes(text)
        
        await self.update_victor_state(
            text=text,
            emotion="calm_focus",
            energy=0.6,
            mode="speaking",
            phonemes=phonemes,
            audio_path=""  # Would be actual path in production
        )
    
    def _generate_demo_phonemes(self, text: str) -> List[Dict[str, Any]]:
        """Generate demo phoneme timing (placeholder for real TTS)"""
        # Simple heuristic: map characters to phoneme timing
        phonemes = []
        time = 0.0
        
        for char in text.lower():
            if char in 'aeiou':
                phonemes.append({"p": "AA", "t": time})
                time += 0.15
            elif char in 'mbp':
                phonemes.append({"p": "M", "t": time})
                time += 0.10
            elif char in 'fv':
                phonemes.append({"p": "F", "t": time})
                time += 0.10
            elif char.isalpha():
                phonemes.append({"p": "K", "t": time})
                time += 0.12
            elif char == ' ':
                time += 0.05
        
        return phonemes
    
    async def start(self):
        """Start the WebSocket server"""
        self.running = True
        logger.info(f"Starting Victor Visual Server on ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info("Server is running. Press Ctrl+C to stop.")
            await asyncio.Future()  # Run forever
    
    def run(self):
        """Run the server (blocking)"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        finally:
            self.running = False


# Demo/test functionality
async def demo_mode():
    """Run server in demo mode with simulated updates"""
    server = VictorVisualServer()
    
    # Start server in background
    server_task = asyncio.create_task(server.start())
    
    # Wait a bit for server to start
    await asyncio.sleep(2)
    
    # Simulate Victor speaking
    demo_phrases = [
        ("I am Victor. Ask.", "calm_focus", 0.3),
        ("Analyzing your request...", "thinking", 0.7),
        ("I have the answer.", "confident", 0.5),
        ("This is critical!", "alert", 0.9),
        ("Exploring possibilities...", "creative", 0.6),
    ]
    
    logger.info("Starting demo sequence...")
    
    for text, emotion, energy in demo_phrases:
        await asyncio.sleep(5)
        logger.info(f"Demo: '{text}' ({emotion})")
        await server.update_victor_state(
            text=text,
            emotion=emotion,
            energy=energy,
            phonemes=server._generate_demo_phonemes(text)
        )
    
    # Keep running
    await server_task


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Victor Visual Engine WebSocket Server")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    
    args = parser.parse_args()
    
    if args.demo:
        logger.info("Running in DEMO mode")
        asyncio.run(demo_mode())
    else:
        server = VictorVisualServer(host=args.host, port=args.port)
        server.run()


if __name__ == "__main__":
    main()
