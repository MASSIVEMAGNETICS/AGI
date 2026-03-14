# Victor Synthetic Super Intelligence - Installation Guide

**Quick Start:** Choose your installation method based on what you need!

---

## 📋 Table of Contents

- [Complete System Installation (Recommended)](#-complete-system-installation-recommended)
- [Quick Verification](#-quick-verification)
- [Visual Engine Installation](#-visual-engine-installation)
- [Prerequisites](#-prerequisites)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Complete System Installation (Recommended)

For the **full Victor experience**, use the complete installer:

```bash
# Install everything
python install_complete.py

# Then verify with the demo
python full_demo.py
```

**What gets installed:**
- ✅ All Python dependencies (numpy, pyyaml, websockets)
- ✅ Victor Hub (AGI Core)
- ✅ Genesis Engine (Quantum-Fractal Cognition)
- ✅ Advanced AI (Tensor Core, Holon Omega)
- ✅ Visual Engine Backend
- ✅ Directory structure and launch scripts

**Installation time:** ~30-60 seconds

---

## ✅ Quick Verification

After installation, verify everything works:

```bash
# Run the complete demonstration
python full_demo.py

# Expected output:
# ✓ Tensor Core: success
# ✓ Genesis Engine: success
# ✓ Victor Hub: success
# ✓ NLP Integration: success
# ✓ Advanced AI: success
# ✓ Unified System: success
# 🎉 All demos completed successfully!
```

If all tests pass, Victor is ready!

---

## 🎨 Visual Engine Installation

For just the 3D visual interface:

### Option 1: Universal Python Installer (Recommended)
Works on **Windows, macOS, and Linux**

```bash
python install.py
```

or

```bash
python3 install.py
```

**What it does:**
- ✓ Checks Python version (requires 3.8+)
- ✓ Installs all Python dependencies
- ✓ Generates 3D model
- ✓ Detects Godot installation
- ✓ Tests backend server
- ✓ Creates quick restart scripts
- ✓ Optionally starts everything for you

---

### Option 2: Bash Script (macOS & Linux)

```bash
chmod +x install.sh
./install.sh
```

**Features:**
- Colored terminal output
- Automatic dependency installation
- Godot auto-detection and launch
- Interactive startup option

---

### Option 3: Batch Script (Windows)

**Double-click:** `install.bat`

or

```cmd
install.bat
```

**Features:**
- Windows-friendly interface
- Automatic dependency installation
- Godot detection in common locations
- One-click startup

---

## 📋 Prerequisites

### Required
- **Python 3.8 or higher**
  - Download: https://www.python.org/downloads/
  - During installation, check "Add Python to PATH"

### Optional (for 3D visualization)
- **Godot Engine 4.2 or higher**
  - Download: https://godotengine.org/download
  - Not required to run backend server
  - Can install later and still use the system

---

## 🎯 What Gets Installed

The installer will set up:

1. **Python Dependencies:**
   - `pyyaml` - Configuration management
   - `websockets` - Real-time communication

2. **3D Model:**
   - `victor_head.glb` - Procedural 3D model
   - Automatically generated if missing

3. **Helper Scripts:**
   - `run_victor.sh` (Unix) or `run_victor.bat` (Windows)
   - Quick restart without re-running installer

---

## 💻 Usage After Installation

### Start Full Demo
```bash
python visual_engine/test_visual_engine.py
```

Then open Godot and press F5.

**You'll see:**
- Backend cycling through emotion states every 5 seconds
- Godot showing Victor's helmet with changing colors

### Start Backend Only
```bash
python launch_visual_engine.py
```

For integration with Victor Hub or custom clients.

### Quick Restart

**Unix/Mac:**
```bash
./run_victor.sh
```

**Windows:**
```cmd
run_victor.bat
```

---

## 🎨 Opening the Godot Project

### If Godot Installed:
The installer will attempt to open it automatically.

### Manual Steps:
1. Launch Godot Engine
2. Click "Import"
3. Navigate to: `visual_engine/godot_project/project.godot`
4. Click "Import & Edit"
5. Press **F5** to run the scene

---

## 🔧 Troubleshooting

### "Python not found"
- Install Python 3.8+ from https://www.python.org/
- Make sure "Add to PATH" was checked during installation
- Restart terminal/command prompt after installation

### "pip install failed"
Try manual installation:
```bash
pip install pyyaml websockets
```

or

```bash
pip install --user pyyaml websockets
```

### "Module not found" errors
Make sure you're in the repository root directory:
```bash
cd Victor_Synthetic_Super_Intelligence
python install.py
```

### "Godot not found"
- Installer works without Godot (backend only)
- Download Godot later: https://godotengine.org/download
- Open project manually when ready

### Port 8765 already in use
Stop any existing Victor servers:
```bash
# Unix/Mac
pkill -f "launch_visual_engine"

# Windows (in Task Manager)
# End any Python processes running launch_visual_engine.py
```

---

## 📁 What Each Installer Does

### `install.py` (Universal)
```
1. Check Python version (3.8+)
2. Install pip dependencies
3. Generate 3D model if missing
4. Detect Godot in PATH and common locations
5. Test backend server
6. Create OS-specific run script
7. Optionally start everything
```

### `install.sh` (Unix/Mac)
```
1. Detect OS (Linux/Mac/Windows)
2. Check Python installation
3. Install dependencies via pip
4. Generate 3D model
5. Search for Godot installation
6. Create run_victor.sh script
7. Interactive startup option
```

### `install.bat` (Windows)
```
1. Check Python in PATH
2. Install dependencies
3. Generate 3D model
4. Check common Godot locations
5. Create run_victor.bat script
6. Interactive startup option
```

---

## 🎮 Expected Behavior After Start

### Backend Server:
```
Victor Visual Server initialized on 127.0.0.1:8765
Starting Victor Visual Server on ws://127.0.0.1:8765
Server is running. Press Ctrl+C to stop.

--- Test 1/5 ---
Text: I am Victor. Ask.
Emotion: calm_focus (Energy: 0.3)
```

### Godot Window:
- Black background
- Angular metallic helmet (Victor's head)
- Glowing teal eyes
- Subtitle text at bottom
- Colors change every 5 seconds:
  - Teal → Blue → Purple → Red → Magenta

---

## 🌟 Quick Command Reference

```bash
# Full installation
python install.py

# Backend demo (test messages)
python visual_engine/test_visual_engine.py

# Backend only (no test messages)
python launch_visual_engine.py

# Victor Hub integration
python run_victor_with_visual.py --mode demo

# Regenerate 3D model
python generate_victor_model.py

# Quick restart
./run_victor.sh          # Unix/Mac
run_victor.bat           # Windows
```

---

## 📖 Documentation

After installation, see:
- `visual_engine/QUICKSTART.md` - 5-minute setup guide
- `visual_engine/README.md` - Complete documentation
- `visual_engine/DEPLOYMENT.md` - Production deployment
- `visual_engine/MODEL_VISUAL_DESCRIPTION.md` - 3D model details

---

## 🚦 Installation Status Indicators

### ✓ Success Messages
- Green checkmarks indicate completed steps
- System is ready to use

### ⚠ Warning Messages  
- Yellow warnings indicate optional components
- System will still work (e.g., Godot can be installed later)

### ✗ Error Messages
- Red X indicates critical failures
- Installation cannot proceed without fixing

---

## 🔄 Updating

To update after pulling new code:

```bash
# Re-run installer (safe to run multiple times)
python install.py

# Or manually update
pip install -r requirements.txt --upgrade
python generate_victor_model.py
```

---

## 💡 Tips

1. **First time?** Use `python install.py` - it's the most compatible

2. **Running multiple times is safe** - installer checks what's already installed

3. **Don't have Godot?** Backend works standalone, install Godot later

4. **Want to customize?** Edit `generate_victor_model.py` and regenerate

5. **Need help?** Check `visual_engine/QUICKSTART.md` for step-by-step guide

---

## 🎉 Success!

If you see:
```
✓ Python 3.x.x detected
✓ Python dependencies installed
✓ 3D model generated
✓ Backend server ready
```

**You're ready to run Victor Visual Engine!** 🧠👁️✨

---

**Questions?** See the main documentation in `visual_engine/README.md`

**Created by MASSIVEMAGNETICS**
