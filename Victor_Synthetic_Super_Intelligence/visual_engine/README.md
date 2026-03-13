# Victor Visual Engine

**Version:** 1.0.0  
**Status:** Initial Implementation  
**Author:** MASSIVEMAGNETICS

A real-time 3D visual interface for Victor AGI, styled as a cyberpunk avatar with emotion-driven animations, phoneme-based lip sync, and reactive visual effects.

---

## Overview

The Victor Visual Engine (VVE) provides a tangible presence for Victor AGI - think **Zordon + Jarvis + Ritual Altar**. It features:

- **Real-time 3D rendering** using Godot 4
- **Emotion-driven visual effects** (glow, color shifts, particles)
- **Phoneme-based lip sync** for natural speech
- **Eye tracking** and idle animations
- **WebSocket communication** between Victor Core and visual engine
- **Modular architecture** ready for expansion (AR, streaming, etc.)

---

## Architecture

```
┌─────────────────────┐
│   Victor Core       │  ← Python: Reasoning, Memory, Personality
│   (Victor Hub)      │
└──────────┬──────────┘
           │
           │ WebSocket (JSON messages)
           │
┌──────────▼──────────┐
│  Visual Server      │  ← Python: WebSocket server, State management
│  (Backend)          │
└──────────┬──────────┘
           │
           │ WebSocket
           │
┌──────────▼──────────┐
│  Godot Visual       │  ← Godot 4: 3D rendering, animations, shaders
│  Engine             │
└─────────────────────┘
```

### Components

1. **Victor Core (Python)**
   - Handles reasoning, personality, text generation
   - Determines emotion states based on context
   - Sends state updates via bridge

2. **Visual Server (Python WebSocket)**
   - Bridges Victor Core ↔ Godot
   - Manages WebSocket connections
   - Handles phoneme generation (or TTS integration)
   - Broadcasts state changes to clients

3. **Godot Visual Engine**
   - 3D scene with Victor's avatar
   - Shader-based visual effects
   - Animation system (lip sync, idle, emotion)
   - UI overlay (subtitles, status)

---

## Data Contract

### WebSocket Message Format

Victor → Visual Engine:
```json
{
  "text": "I am Victor. Ask.",
  "emotion": "calm_focus",
  "energy": 0.32,
  "aura": "teal",
  "mode": "advisor",
  "phonemes": [
    {"p": "AY", "t": 0.00},
    {"p": "AE", "t": 0.12},
    {"p": "M", "t": 0.24}
  ],
  "audio_path": "/path/to/audio.wav"
}
```

Visual Engine → Victor (optional):
```json
{
  "type": "user_input",
  "cursor_position": [0.5, 0.3],
  "mic_active": true
}
```

### Emotion States

- `calm_focus` - Default state (teal aura)
- `thinking` - Processing/analyzing (blue aura)
- `excited` - High energy response (gold aura)
- `concerned` - Error or warning (orange aura)
- `alert` - Critical state (red aura)
- `confident` - Successful completion (purple aura)
- `analyzing` - Deep analysis (cyan aura)
- `creative` - Generating content (magenta aura)
- `glitch` - System transition (white/flickering)
- `prophetic` - Deep insight mode (violet aura)

### Phoneme Codes

Standard phoneme codes for lip sync:
- `M`, `B`, `P` - Closed mouth sounds
- `AA`, `AE`, `AH`, `AO` - Open vowels
- `F`, `V` - Lip-teeth sounds
- `K`, `G` - Back sounds
- etc.

---

## Installation

### Prerequisites

1. **Python 3.8+** for backend
2. **Godot 4.2+** for visual engine
3. **websockets** Python library

### Setup

```bash
# 1. Install Python dependencies
pip install websockets

# 2. Install Godot 4.2+
# Download from: https://godotengine.org/download

# 3. Open Godot project
# Open visual_engine/godot_project/project.godot in Godot Editor
```

---

## Usage

### Running the Visual Engine

#### Option 1: Demo Mode (Standalone)

```bash
# Start WebSocket server in demo mode
python visual_engine/backend/victor_visual_server.py --demo

# In Godot Editor: Press F5 to run the scene
# Or export as executable and run
```

#### Option 2: Integrated with Victor Hub

```python
# In Victor Hub code
from visual_engine.backend.victor_visual_server import VictorVisualServer
from visual_engine.backend.victor_visual_bridge import VictorVisualBridge
import asyncio

# Create visual server
visual_server = VictorVisualServer()

# Create bridge
bridge = VictorVisualBridge(visual_server)

# Start server (in async context)
asyncio.create_task(visual_server.start())

# Send updates
await bridge.send_response(
    text="Hello, I am Victor",
    emotion="calm_focus",
    energy=0.5
)
```

### Testing WebSocket Server

```bash
# Test server
python visual_engine/backend/victor_visual_server.py --host 127.0.0.1 --port 8765

# In another terminal, test with websocat (if installed)
echo '{"type":"ping"}' | websocat ws://127.0.0.1:8765
```

---

## Directory Structure

```
visual_engine/
├── backend/
│   ├── victor_visual_server.py     # WebSocket server
│   └── victor_visual_bridge.py     # Integration bridge
├── godot_project/
│   ├── project.godot               # Godot project file
│   ├── scenes/
│   │   └── VictorScene.tscn        # Main scene
│   ├── scripts/
│   │   └── VictorController.gd     # Main GDScript controller
│   ├── shaders/
│   │   └── victor_head_material.gdshader  # Emissive shader
│   └── models/                     # 3D models
│       ├── victor_head.glb         # Victor 3D model (binary)
│       ├── victor_head.gltf        # Victor 3D model (text)
│       └── README.md               # Model documentation
├── models/                         # Model specifications
│   └── MODEL_SPECIFICATION.md      # Professional model specs
└── docs/                           # Additional documentation
```

---

## Next Steps - Production Readiness

### 1. 3D Model ✓

**Current:** Procedural geometric model  
**Status:** Basic 3D model included

A procedural 3D model has been generated and integrated:
- Angular 8-sided helmet (cyberpunk aesthetic)
- Basic eye geometry
- PBR metallic material with teal emissive glow
- ~144 triangles (optimized for real-time)
- Located at: `godot_project/models/victor_head.glb`

**For Production:** Professional model with:
- Detailed panel lines and surface features
- Blend shapes for phonemes: `mouth_open`, `mouth_closed`, `mouth_fv`, `jaw_open`
- Eye bones for tracking
- Higher polygon count (~30K-40K tris)
- PBR texture maps (see `models/MODEL_SPECIFICATION.md`)

**Regenerate model:**
```bash
python generate_victor_model.py
```

### 2. Voice/TTS Integration

**Current:** Demo phoneme generation  
**Needed:** Real TTS with phoneme timing

Options:
- **Coqui TTS** (open-source, phoneme support)
- **Azure Speech** (commercial, excellent quality)
- **Google Cloud TTS** (commercial)
- **ElevenLabs** (commercial, very high quality)

Integration point: Replace `_generate_demo_phonemes()` in `victor_visual_server.py`

### 3. Advanced Shaders

Current shader provides basic emissive glow. Enhance with:
- Scanline effects during "thinking"
- Fractal patterns for "prophetic" mode
- Glitch distortion for mode transitions
- Dynamic reflections
- Particle systems (aura rings, sparkles)

### 4. Background Scene

Add cyberpunk corridor background:
- Neon signs (static or animated)
- Volumetric fog
- Depth-of-field camera
- Parallax layers

### 5. Eye Tracking

Implement eye movement to track:
- User cursor position
- Microphone input direction
- Random idle scanning

### 6. Audio Playback

Connect audio_path to actual audio file loading:
```gdscript
var stream = load(audio_path)
if stream:
    audio_player.stream = stream
    audio_player.play()
```

### 7. Full Victor Hub Integration

Create skill/service in Victor Hub that:
- Starts visual server automatically
- Routes all responses through visual bridge
- Updates emotion based on task context

---

## Configuration

### Visual Server Configuration

Edit `victor_hub/config.yaml`:

```yaml
visual_engine:
  enabled: true
  server:
    host: "127.0.0.1"
    port: 8765
  auto_start: true
  demo_mode: false
```

### Godot Configuration

Edit in Godot Editor or `scripts/VictorController.gd`:

```gdscript
var ws_url := "ws://127.0.0.1:8765"  # Server URL
var retry_interval := 5.0            # Reconnect interval
```

---

## Deployment Options

### Desktop Application

1. Export from Godot as Windows/Mac/Linux executable
2. Bundle with Python backend
3. Create launcher script that starts both

### Fullscreen Control Room

Set in Godot:
- Window → Mode → Fullscreen
- Custom resolution (e.g., 3840x2160 for 4K)

### Stream Overlay

Export with transparent background:
- Set ClearColor alpha to 0
- Export as window with transparency
- Use OBS Virtual Camera to capture

### AR/VR (Future)

Godot 4 supports OpenXR:
- Replace Camera3D with XRCamera3D
- Add XR controllers
- Deploy to Quest/PSVR2

---

## Troubleshooting

### WebSocket connection fails

- Check server is running: `python visual_engine/backend/victor_visual_server.py`
- Verify port 8765 is not blocked by firewall
- Check console output for errors

### No visual updates in Godot

- Check WebSocket connection state in Godot console
- Verify server is sending messages (check server logs)
- Test with demo mode: `--demo` flag

### Animations not working

- Verify skeleton node exists and is correctly named
- Check blendshape names match model
- Ensure phoneme queue is populated

---

## Contributing

To extend the visual engine:

1. **Add new emotions:** Update `emotion_colors` in `VictorController.gd`
2. **Add effects:** Create new shader or particle system
3. **Improve animations:** Enhance `_update_idle_animations()` or add new animation states
4. **Add UI elements:** Modify `VictorScene.tscn` to add panels, graphs, etc.

---

## References

- [Godot 4 Documentation](https://docs.godotengine.org/en/stable/)
- [WebSocket API (Python)](https://websockets.readthedocs.io/)
- [Phoneme Reference](https://en.wikipedia.org/wiki/ARPABET)
- [PBR Material Guide](https://marmoset.co/posts/basic-theory-of-physically-based-rendering/)

---

**Built with 🧠 by MASSIVEMAGNETICS**  
**Version 1.0.0 - November 2025**
