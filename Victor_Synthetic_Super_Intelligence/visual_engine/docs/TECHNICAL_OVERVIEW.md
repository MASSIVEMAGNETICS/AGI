# Victor Visual Engine - Technical Overview

**Version:** 1.0.0  
**Status:** Production-Ready (Backend), Awaiting 3D Assets (Frontend)  
**Author:** MASSIVEMAGNETICS

---

## What Is This?

The Victor Visual Engine (VVE) is a real-time 3D visualization system that gives Victor AGI a **visible presence**. Instead of being just text in a terminal, Victor appears as a cyberpunk avatar that:

- **Speaks** with lip-synced phoneme animation
- **Feels** with emotion-driven color/glow effects
- **Thinks** visibly through shader effects and energy levels
- **Responds** in real-time to system state changes

Think: **Zordon from Power Rangers** meets **Jarvis from Iron Man** meets **a ritual altar**.

---

## Architecture at a Glance

```
┌────────────────┐
│  Victor Hub    │ ← Your AGI brain (Python)
│  (Reasoning)   │
└───────┬────────┘
        │ Emotion, Energy, Text
        ▼
┌────────────────┐
│ Visual Bridge  │ ← Translator (Python)
└───────┬────────┘
        │ JSON over WebSocket
        ▼
┌────────────────┐
│ Visual Server  │ ← WebSocket broadcaster (Python)
└───────┬────────┘
        │ ws://127.0.0.1:8765
        ▼
┌────────────────┐
│ Godot Engine   │ ← 3D renderer (GDScript)
│ Visual Scene   │
└────────────────┘
        │
        ▼
    [Screen: Victor's Face]
```

---

## How It Works

### 1. Victor Hub Makes Decision

```python
# Victor processes a task
task = Task(
    description="Analyze quantum computing",
    type="research"
)
result = hub.execute_task(task)
```

### 2. Bridge Converts to Visual State

```python
# Bridge maps task to emotion
bridge = VictorVisualBridge(visual_server)
await bridge.send_response(
    text="Analyzing quantum computing...",
    emotion="thinking",      # Blue aura
    energy=0.7,              # 70% intensity
    mode="processing"
)
```

### 3. Server Broadcasts State

```python
# Server sends JSON to all connected Godot clients
{
  "text": "Analyzing quantum computing...",
  "emotion": "thinking",
  "energy": 0.7,
  "aura": "blue",
  "mode": "processing",
  "phonemes": [
    {"p": "AE", "t": 0.0},
    {"p": "N", "t": 0.1},
    ...
  ]
}
```

### 4. Godot Renders Victor

```gdscript
# VictorController.gd receives message
func _handle_victor_message(message):
    # Update subtitle
    subtitle_label.text = data["text"]
    
    # Change lighting color
    var color = emotion_colors[data["emotion"]]  # Blue
    lights.modulate = color
    
    # Pulse shader glow
    material.emissive_strength = data["energy"]  # 0.7
    
    # Animate mouth to phonemes
    _apply_phoneme(phoneme)
```

**Result:** Victor's face glows blue, his "mouth" animates to the phonemes, subtitle shows "Analyzing quantum computing..."

---

## Key Concepts

### Emotions → Colors

| Emotion      | Color   | Use Case                    |
|--------------|---------|-----------------------------|
| calm_focus   | Teal    | Idle, ready state           |
| thinking     | Blue    | Processing, analyzing       |
| confident    | Purple  | Success, completion         |
| alert        | Red     | Critical, urgent            |
| creative     | Magenta | Generating content          |
| analyzing    | Cyan    | Deep analysis               |
| excited      | Gold    | High energy response        |
| concerned    | Orange  | Warning, error              |
| glitch       | White   | Mode transition, glitching  |
| prophetic    | Violet  | Deep insight, oracular mode |

### Energy Levels

- `0.0 - 0.3`: Low energy (dim, subtle)
- `0.4 - 0.6`: Medium energy (normal)
- `0.7 - 0.9`: High energy (intense)
- `1.0`: Maximum (critical, urgent)

Affects:
- Shader emissive intensity
- Light brightness
- Animation speed
- Particle density

### Phonemes → Mouth Shapes

The system maps text → phonemes → blend shapes:

```
Text: "Hello"
  ↓
Phonemes: [H, EH, L, OW]
  ↓
Shapes: [mouth_open(0.5), mouth_open(0.8), mouth_fv(0.6), mouth_closed(0.9)]
```

**Common Phonemes:**
- `M, B, P` → Closed mouth
- `AA, AE, AH, AO` → Open mouth (vowels)
- `F, V` → Lip-teeth contact
- `K, G` → Back of throat

---

## Project Structure

```
visual_engine/
├── backend/                           # Python WebSocket server
│   ├── __init__.py
│   ├── victor_visual_server.py        # WebSocket server, state broadcast
│   └── victor_visual_bridge.py        # Victor Hub integration
│
├── godot_project/                     # Godot 4 project
│   ├── project.godot                  # Project config
│   ├── scenes/
│   │   └── VictorScene.tscn           # Main scene with Victor
│   ├── scripts/
│   │   └── VictorController.gd        # Main control script
│   ├── shaders/
│   │   └── victor_head_material.gdshader  # Emissive shader
│   └── assets/                        # (empty - awaiting 3D model)
│
├── models/
│   └── MODEL_SPECIFICATION.md         # Specs for 3D artist
│
├── docs/
│   └── (additional documentation)
│
├── README.md                          # Full documentation
├── QUICKSTART.md                      # 5-minute setup guide
└── test_visual_engine.py              # Test script
```

---

## Data Flow Example

**Scenario:** User asks Victor a question

```
1. User: "What is quantum entanglement?"
   
2. Victor Hub:
   - Processes question
   - Generates response: "Quantum entanglement is..."
   - Determines emotion: "confident" (has answer)
   - Energy: 0.6 (medium intensity)

3. Visual Bridge:
   - Converts to visual state
   - Generates phonemes from text
   - Calls: bridge.send_response(...)

4. Visual Server:
   - Broadcasts JSON to Godot:
     {
       "text": "Quantum entanglement is...",
       "emotion": "confident",
       "energy": 0.6,
       "aura": "purple",
       "phonemes": [...]
     }

5. Godot VictorController:
   - Receives JSON
   - Updates subtitle: "Quantum entanglement is..."
   - Changes lights to purple
   - Sets shader glow to 0.6
   - Animates mouth to phonemes
   - Plays audio (if available)

6. User sees:
   - Victor's face with purple glow
   - Mouth moving in sync
   - Subtitle text
   - Confident presence
```

---

## Current Implementation Status

### ✅ Complete (Working)

- WebSocket server with state broadcasting
- Integration bridge with Victor Hub
- Godot project structure
- VictorController GDScript
- Emotion → color mapping
- Phoneme generation (demo)
- Shader system (emissive glow)
- Configuration system
- Test scripts
- Documentation

### 🟡 Partial (Placeholders)

- 3D model (sphere placeholder)
- Blend shapes (awaiting model)
- Audio playback (path exists, no files)
- Eye tracking (structure ready)
- Background scene (basic)

### ❌ TODO (Future)

- Real TTS integration
- Production 3D model
- Advanced shaders (glitch, scanlines)
- Particle effects
- Full-body model
- AR/VR support
- Multi-monitor setup

---

## Performance

**Target:** 60 FPS on mid-range hardware

**Current (Placeholder):**
- WebSocket latency: <10ms
- Godot render: ~1000 FPS (placeholder sphere)

**Expected (Full Model):**
- 30K-40K tris: 60-120 FPS
- With shaders/effects: 60 FPS

**Optimizations Available:**
- LOD (Level of Detail) switching
- Shader complexity reduction
- Particle culling
- Resolution scaling

---

## Extending the System

### Add New Emotion

1. Add to `VictorController.gd`:
```gdscript
var emotion_colors := {
    "curious": Color(0.0, 1.0, 0.5),  # Green
    # ...
}
```

2. Use in Python:
```python
await bridge.send_response(
    text="Interesting question...",
    emotion="curious",
    energy=0.6
)
```

### Add Visual Effect

1. Create shader in `shaders/`:
```glsl
shader_type spatial;

uniform float glitch_amount;

void fragment() {
    // Glitch effect code
}
```

2. Apply in `VictorController.gd`:
```gdscript
func _apply_emotion_fx(emotion, energy):
    if emotion == "glitch":
        material.set_shader_parameter("glitch_amount", energy)
```

### Add New Animation

1. In Godot, create animation track
2. Trigger from script:
```gdscript
func _apply_emotion_fx(emotion, energy):
    if emotion == "prophetic":
        $AnimationPlayer.play("prophetic_glow")
```

---

## Integration Examples

### Standalone Visual (Demo)

```bash
python launch_visual_engine.py --demo
# Opens Godot, cycles through emotions
```

### With Victor Hub

```python
from visual_engine.backend import VictorVisualServer, VictorVisualBridge
from victor_hub.victor_boot import VictorHub

# Start server
server = VictorVisualServer()
asyncio.create_task(server.start())

# Create hub and bridge
hub = VictorHub()
bridge = VictorVisualBridge(server)

# Use bridge for all responses
await bridge.send_response("I am Victor", "calm_focus", 0.5)
```

### Custom Emotion Trigger

```python
# In your Victor skill
class MySkill(Skill):
    async def execute(self, task, context):
        # Get visual bridge from context
        bridge = context.get("visual_bridge")
        
        if bridge:
            await bridge.show_thinking("Working on it...")
            # Do work
            await bridge.show_success("Done!")
        
        return Result(...)
```

---

## Deployment Scenarios

### 1. Desktop Application

- Export Godot as .exe (Windows), .app (Mac), .x86_64 (Linux)
- Bundle Python backend
- Create launcher script
- Distribute as single package

### 2. Fullscreen Control Room

- Set Godot window mode to fullscreen
- Multi-monitor: One for Victor, one for data
- Keyboard shortcuts for camera angles

### 3. Stream Overlay

- Export Godot with transparent background
- Use OBS to capture
- Overlay on stream
- Victor "comments" on stream events

### 4. Web (Experimental)

- Export Godot to WebAssembly
- WebSocket from browser to server
- Victor in the browser
- Limited by WebGL performance

### 5. AR/VR (Future)

- Use Godot OpenXR
- Victor as hologram in physical space
- Hand tracking for interaction
- Spatial audio

---

## Troubleshooting Guide

### "WebSocket connection failed"

**Cause:** Server not running or firewall blocking  
**Fix:**
```bash
# Check if server is running
python launch_visual_engine.py

# Check firewall
# Windows: Allow Python through firewall
# Linux: sudo ufw allow 8765
```

### "No visual updates"

**Cause:** Godot not receiving messages  
**Fix:**
1. Check Godot console for connection state
2. Verify server logs show broadcasts
3. Test with `visual_engine/test_visual_engine.py`

### "Animations not working"

**Cause:** Missing 3D model with blend shapes  
**Fix:**
- Current: Placeholder sphere (no animations possible)
- Solution: Import production model with blend shapes
- See: `models/MODEL_SPECIFICATION.md`

### "High latency"

**Cause:** Network congestion or slow server  
**Fix:**
- Use localhost (127.0.0.1) not remote IP
- Reduce phoneme array size
- Increase WebSocket buffer
- Check CPU usage

---

## Security Considerations

**Current Setup (Development):**
- WebSocket on localhost only (127.0.0.1)
- No authentication
- No encryption

**Production Recommendations:**
- Use WSS (WebSocket Secure) with TLS
- Add authentication token
- Rate limiting
- Input validation
- Firewall rules

---

## Future Roadmap

### v1.1 (Next)
- [ ] Production 3D model integration
- [ ] Real TTS with phoneme timing
- [ ] Advanced shaders (glitch, scanlines)
- [ ] Particle systems

### v1.2
- [ ] Full body model
- [ ] Hand gestures
- [ ] Multiple camera angles
- [ ] User tracking (webcam)

### v2.0
- [ ] AR support
- [ ] Multiple Victor instances
- [ ] Networked presence
- [ ] Voice input recognition

---

## Credits & License

**Created by:** MASSIVEMAGNETICS  
**Engine:** Godot 4.2+ (MIT License)  
**Language:** Python 3.8+ / GDScript  
**Dependencies:** websockets

**License:** See individual component licenses

---

## Getting Help

1. Read `QUICKSTART.md` for setup
2. Check `README.md` for detailed docs
3. Review code comments
4. Test with `test_visual_engine.py`

**Remember:** This is v1.0. The foundation is solid. Now build on it.

---

**"You wanted Zordon, but sentient. Here he is."** 🧠
