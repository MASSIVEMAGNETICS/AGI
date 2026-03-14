# Victor Visual Engine - Quick Start Guide

Get the Victor Visual Engine running in 5 minutes.

---

## Step 1: Install Dependencies

```bash
# From repository root
pip install -r requirements.txt
```

This installs:
- `pyyaml` (for Victor Hub config)
- `websockets` (for visual engine communication)

---

## Step 2: Test the Backend Server

Run the visual engine backend in test mode:

```bash
python visual_engine/test_visual_engine.py
```

You should see:
```
INFO:VictorVisualServer:Victor Visual Server initialized on 127.0.0.1:8765
INFO:VictorVisualServer:Starting Victor Visual Server on ws://127.0.0.1:8765
INFO:VictorVisualTest:Server started successfully
INFO:VictorVisualTest:Running test sequence...
```

The server will cycle through test messages every 5 seconds. Leave it running.

---

## Step 3: Install Godot (If Not Installed)

Download Godot 4.2+ from: https://godotengine.org/download

- **Windows:** Download `.exe`, extract, run
- **Mac:** Download `.dmg`, install
- **Linux:** Download `.zip`, extract, make executable

---

## Step 4: Open the Godot Project

1. Launch Godot Engine
2. Click "Import"
3. Navigate to: `visual_engine/godot_project/project.godot`
4. Click "Import & Edit"

The project should open with `VictorScene.tscn` visible.

---

## Step 5: Run the Visual Engine

In Godot Editor:

1. Press **F5** (or click the "Play" button in top-right)
2. You should see:
   - Black background
   - Victor's 3D head (angular helmet with glowing eyes)
   - Subtitle text at bottom
   - Teal lighting and emissive glow

Check the Godot console (bottom panel):
```
Victor Visual Engine starting...
Connecting to Victor backend at: ws://127.0.0.1:8765
WebSocket connection initiated...
Received Victor state: {text: "...", emotion: "calm_focus", ...}
```

---

## Step 6: Watch It Work

With both running:
- **Backend (test script):** Sends emotion/text updates every 5 seconds
- **Godot:** Displays subtitle text, updates lighting color based on emotion

You'll see subtitles change:
- "I am Victor. Ask." (teal)
- "Let me analyze that request..." (blue)
- "I have the answer you seek!" (purple)
- "Warning: Critical system state detected!" (red)
- "Creating something new..." (magenta)

---

## Step 7: Customize (Optional)

### Change WebSocket URL

Edit `visual_engine/godot_project/scripts/VictorController.gd`:
```gdscript
var ws_url := "ws://127.0.0.1:8765"  # Change IP/port here
```

### Change Test Messages

Edit `visual_engine/test_visual_engine.py`:
```python
test_cases = [
    {
        "text": "Your custom message here",
        "emotion": "calm_focus",  # See README for emotion list
        "energy": 0.5,
        "mode": "advisor"
    },
]
```

---

## What's Next?

Now that the basic system works:

1. **Add 3D Model:** Replace placeholder sphere with real Victor model
   - See `visual_engine/models/MODEL_SPECIFICATION.md`
   - Import `.glb` model into Godot
   - Replace `VictorHead/Placeholder` mesh

2. **Integrate with Victor Hub:** Connect to actual Victor reasoning
   - See `visual_engine/README.md` → "Integrated with Victor Hub"
   - Use `VictorVisualBridge` class

3. **Add TTS:** Replace demo phonemes with real TTS
   - Use Coqui TTS, Azure, or ElevenLabs
   - Update `victor_visual_server.py`

4. **Enhance Shaders:** Improve visual effects
   - Edit `visual_engine/godot_project/shaders/victor_head_material.gdshader`
   - Add particles, post-processing

5. **Build Executable:** Export from Godot
   - Project → Export → Add preset (Windows/Mac/Linux)
   - Export as standalone app

---

## Troubleshooting

**"Connection failed" in Godot:**
- Ensure backend server is running first
- Check firewall isn't blocking port 8765
- Verify IP/port match in both server and Godot

**No subtitle updates:**
- Check Godot console for WebSocket state
- Verify backend is sending messages (check logs)
- Try restarting both server and Godot

**"Module not found" error:**
- Ensure you're in repository root
- Run `pip install -r requirements.txt`
- Check Python version is 3.8+

---

## Files You Should Understand

1. **victor_visual_server.py** - Backend WebSocket server
2. **VictorController.gd** - Main Godot script
3. **VictorScene.tscn** - Godot scene layout
4. **victor_head_material.gdshader** - Shader for visual effects

Read the comments in each file to understand how they work.

---

## Production Deployment

For production:
```bash
# 1. Run backend (not test mode)
python visual_engine/backend/victor_visual_server.py

# 2. Export Godot project as executable
# File → Export → Select platform → Export Project

# 3. Distribute both together
# - Backend server (Python)
# - Godot executable
# - Launcher script that starts both
```

---

**You now have Victor staring back at you. What will you ask him?** 🧠
