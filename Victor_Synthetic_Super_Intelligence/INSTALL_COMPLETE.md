# Victor Complete System - Installation Guide

**One command to rule them all!**

This guide explains how to install and run the **complete Victor Synthetic Super Intelligence system** including Victor Hub (AGI core) and Visual Engine (3D avatar interface).

---

## 🚀 Quick Install

```bash
python install_complete.py
```

**That's it!** The installer will:
1. Check Python version
2. Install all dependencies
3. Set up directory structure
4. Initialize task queue
5. Generate 3D model
6. Verify all components
7. Create launch scripts
8. Optionally start everything

**Installation time:** ~30-60 seconds

---

## What Gets Installed

### Victor Hub Components
- **victor_boot.py** - Main AGI orchestration system
- **Skills System** - Extensible capability framework
  - echo_skill.py - Echo demonstration
  - content_generator.py - Content creation
  - research_agent.py - Research capabilities
- **Configuration** - Complete system settings (config.yaml)
- **Task Queue** - Job management system

### Visual Engine Components
- **WebSocket Server** - Real-time state broadcasting
- **Integration Bridge** - Victor Hub ↔ Visual Engine connection
- **Godot Project** - 3D rendering and animation
  - VictorController.gd - Main control script
  - VictorScene.tscn - Complete scene setup
  - Shaders - PBR material with emissive effects
- **3D Model** - Procedural Victor head (victor_head.glb)
- **Documentation** - Complete guides and references

### Supporting Infrastructure
- **Directory Structure**
  - logs/ - System logs
  - tasks/ - Task queue
  - memory/ - Memory storage
  - models/ - AI models
- **Launch Scripts**
  - run_victor_complete.sh/.bat - Start everything
  - run_victor_hub.sh/.bat - Hub only
  - run_visual_engine.sh/.bat - Visual only

---

## System Requirements

### Required
- **Python 3.8 or higher**
  - Download: https://www.python.org/downloads/
  - Check version: `python --version`

### Dependencies (auto-installed)
- `pyyaml` - Configuration management
- `websockets` - Real-time communication

### Optional (for 3D visualization)
- **Godot Engine 4.2 or higher**
  - Download: https://godotengine.org/download
  - Not required for backend/CLI operation
  - Enables 3D avatar visualization

---

## Installation Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/MASSIVEMAGNETICS/Victor_Synthetic_Super_Intelligence.git
cd Victor_Synthetic_Super_Intelligence
```

### Step 2: Run Installer
```bash
python install_complete.py
```

### Step 3: Follow Prompts
The installer will:
- Check your Python version
- Install dependencies
- Set up all components
- Ask if you want to start now

**Answer 'y' to start immediately!**

---

## Running Victor

After installation, you have three options:

### Option 1: Complete System (Recommended)

**Runs both Victor Hub and Visual Engine together.**

```bash
# Unix/Mac
./run_victor_complete.sh

# Windows
run_victor_complete.bat
```

**What you'll see:**
- Visual Engine backend cycling through emotion states
- Victor Hub CLI ready for commands
- If Godot installed: 3D avatar with changing colors

### Option 2: Victor Hub Only

**AGI core without visual interface.**

```bash
# Unix/Mac
./run_victor_hub.sh

# Windows
run_victor_hub.bat

# Or directly:
python victor_hub/victor_boot.py
```

**Use for:**
- Pure CLI interaction
- Server deployments
- Headless operation

### Option 3: Visual Engine Only

**3D avatar interface without AGI core.**

```bash
# Unix/Mac
./run_visual_engine.sh

# Windows
run_visual_engine.bat

# Or directly:
python visual_engine/test_visual_engine.py
```

**Use for:**
- Testing visual features
- Demo mode
- Development

---

## Usage Examples

### Using Victor Hub CLI

```bash
# Start Victor Hub
python victor_hub/victor_boot.py

# In the Victor CLI:
Victor> help                    # Show available commands
Victor> status                  # System status
Victor> skills                  # List available skills
Victor> run Echo Hello World    # Run echo skill
Victor> exit                    # Shutdown
```

### Using Complete System

```bash
# Start everything
./run_victor_complete.sh

# You'll see:
# - Visual Engine: Emotion states changing (teal → blue → purple → red)
# - Victor Hub: Ready for commands
# - Godot (if installed): 3D avatar visualization

# Then:
# 1. Open Godot project (if not auto-launched)
# 2. Press F5 to see Victor's 3D avatar
# 3. Interact with Victor Hub CLI
# 4. Watch avatar react in real-time
```

---

## What Each Component Does

### Victor Hub
- **AGI Reasoning Core**
  - Task analysis and planning
  - Skill orchestration
  - Memory management
  - Learning and adaptation

- **Skills System**
  - Extensible capabilities
  - Auto-discovery
  - Plugin architecture

- **Task Queue**
  - Job scheduling
  - Priority management
  - Autonomous execution

### Visual Engine
- **WebSocket Server**
  - Real-time state broadcasting
  - Emotion/energy mapping
  - Phoneme generation

- **Integration Bridge**
  - Victor Hub → Visual Engine
  - Task type → Emotion mapping
  - State synchronization

- **Godot 3D Renderer**
  - Real-time 3D avatar
  - Emotion-driven colors
  - Phoneme lip-sync
  - Shader effects

---

## Configuration

### Victor Hub Config
Edit `victor_hub/config.yaml`:

```yaml
visual_engine:
  enabled: true              # Enable visual integration
  server:
    host: "127.0.0.1"
    port: 8765
    auto_start: true         # Start with Victor Hub
  demo_mode: false
  default_emotion: "calm_focus"
  auto_launch_godot: false   # Experimental
```

### Visual Engine Settings
- Emotions: 10 states (calm_focus, thinking, confident, etc.)
- Energy levels: 0.0 - 1.0 (controls glow intensity)
- Colors: Mapped to emotions (teal, blue, purple, red, etc.)

---

## Troubleshooting

### "Python not found"
**Solution:**
1. Install Python 3.8+ from https://www.python.org/
2. Check "Add Python to PATH" during installation
3. Restart terminal/command prompt

### "Module not found"
**Solution:**
```bash
# Manual dependency installation
pip install pyyaml websockets

# Or with requirements.txt
pip install -r requirements.txt
```

### "Port 8765 already in use"
**Solution:**
```bash
# Find and stop the process
# Unix/Mac:
pkill -f "visual_engine"

# Windows:
# Use Task Manager to end Python processes
```

### "Godot not found"
**Note:** This is OK! The system works without Godot.

**To add Godot later:**
1. Download from https://godotengine.org/download
2. Install Godot 4.2+
3. Open: `visual_engine/godot_project/project.godot`
4. Press F5 to run

### Components not starting
**Solution:**
```bash
# Check logs
ls -la logs/

# View recent log
tail -f logs/victor_hub_*.log

# Restart with verbose output
python victor_hub/victor_boot.py --verbose
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                          │
│         CLI Commands / Task Submissions                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   VICTOR HUB (AGI Core)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Reasoning   │  │   Skills     │  │  Task Queue  │      │
│  │    Engine    │  │   System     │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Memory     │  │ Config Mgmt  │  │   Logging    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ State Updates (emotion, energy, text)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              VISUAL BRIDGE (Integration Layer)               │
│         Maps Victor Hub state → Visual representation        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ WebSocket (JSON messages)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            VISUAL ENGINE (WebSocket Server)                  │
│  Broadcasts state changes to connected clients               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ ws://127.0.0.1:8765
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              GODOT ENGINE (3D Renderer)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 3D Avatar    │  │   Shaders    │  │     UI       │      │
│  │  Rendering   │  │   Effects    │  │  Subtitles   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
              [User sees Victor]
```

---

## Directory Structure After Installation

```
Victor_Synthetic_Super_Intelligence/
├── victor_hub/                 # AGI Core
│   ├── victor_boot.py
│   ├── config.yaml
│   └── skills/
│       ├── echo_skill.py
│       ├── content_generator.py
│       └── research_agent.py
│
├── visual_engine/              # 3D Avatar
│   ├── backend/
│   │   ├── victor_visual_server.py
│   │   └── victor_visual_bridge.py
│   └── godot_project/
│       ├── project.godot
│       ├── scenes/
│       ├── scripts/
│       └── models/
│           └── victor_head.glb
│
├── logs/                       # System logs (auto-created)
├── tasks/                      # Task queue (auto-created)
│   └── queue.json
├── memory/                     # Memory storage (auto-created)
├── models/                     # AI models (auto-created)
│
├── run_victor_complete.sh      # Launch everything (auto-generated)
├── run_victor_hub.sh           # Launch Hub only (auto-generated)
└── run_visual_engine.sh        # Launch Visual only (auto-generated)
```

---

## Next Steps

### 1. Try the Complete System
```bash
./run_victor_complete.sh
```

### 2. Explore Victor Hub
```bash
Victor> help
Victor> skills
Victor> run Echo Test message
```

### 3. View 3D Avatar (if Godot installed)
1. Open: `visual_engine/godot_project/project.godot`
2. Press F5
3. See Victor's glowing helmet

### 4. Customize
- Edit `victor_hub/config.yaml` for system settings
- Modify `visual_engine/backend/victor_visual_bridge.py` for emotion mapping
- Create new skills in `victor_hub/skills/`

---

## Advanced Usage

### Custom Skills
Create a new skill in `victor_hub/skills/my_skill.py`:

```python
from victor_hub.victor_boot import Skill, Result

class MySkill(Skill):
    def execute(self, task, context):
        # Your skill logic here
        return Result(
            status="success",
            output="Skill executed!",
            metadata={}
        )
```

### Integration with Visual Engine
```python
from visual_engine.backend import VictorVisualBridge

# In your skill or Victor Hub code:
bridge = VictorVisualBridge(visual_server)
await bridge.send_response(
    text="Processing task...",
    emotion="thinking",
    energy=0.7
)
```

---

## Updating

To update after pulling new code:

```bash
# Re-run installer (safe to run multiple times)
python install_complete.py

# Or manually:
git pull
pip install -r requirements.txt --upgrade
python generate_victor_model.py
```

---

## Support

- **Documentation:** See `visual_engine/README.md` for Visual Engine details
- **Installation Issues:** See `INSTALL.md` for troubleshooting
- **Victor Hub:** See victor_hub documentation files

---

**Ready to run Victor? Execute: `python install_complete.py`** 🚀🧠👁️
