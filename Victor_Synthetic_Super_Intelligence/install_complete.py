#!/usr/bin/env python3
"""
Victor Synthetic Super Intelligence - Complete System Installer
One-click installation for the entire Victor ecosystem
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable_on_windows():
        """Disable colors on Windows if not supported"""
        if platform.system() == 'Windows':
            Colors.RED = Colors.GREEN = Colors.YELLOW = Colors.CYAN = Colors.MAGENTA = Colors.NC = ''

Colors.disable_on_windows()

def print_header(text):
    """Print a header with formatting"""
    print("\n" + "=" * 80)
    print(f"{Colors.CYAN}{text.center(80)}{Colors.NC}")
    print("=" * 80 + "\n")

def print_subheader(text):
    """Print a subheader with formatting"""
    print(f"\n{Colors.MAGENTA}{'─' * 80}{Colors.NC}")
    print(f"{Colors.MAGENTA}{text}{Colors.NC}")
    print(f"{Colors.MAGENTA}{'─' * 80}{Colors.NC}\n")

def print_step(step, total, message):
    """Print a step message"""
    print(f"{Colors.YELLOW}[{step}/{total}] {message}...{Colors.NC}")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.NC}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")

def print_info(message):
    """Print an info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.NC}")

def check_python():
    """Check Python version"""
    print_step(1, 10, "Checking Python installation")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python {version.major}.{version.minor} detected")
        print("Please install Python 3.8 or higher from https://www.python.org/")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_directory():
    """Check if we're in the correct directory"""
    required_files = [
        "victor_hub/victor_boot.py",
        "visual_engine/backend/victor_visual_server.py",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print_error(f"Missing required file: {file_path}")
            print("Please run this script from the repository root")
            return False
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step(2, 10, "Installing Python dependencies")
    try:
        # Upgrade pip
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "--upgrade", "pip"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        # Install requirements
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        print_success("Python dependencies installed (pyyaml, websockets)")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install dependencies")
        print("Try running: pip install -r requirements.txt")
        return False

def setup_directories():
    """Create necessary directories"""
    print_step(3, 10, "Setting up directory structure")
    
    directories = [
        "logs",
        "tasks",
        "memory",
        "models",
        "visual_engine/godot_project/models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print_success(f"Created {len(directories)} directories")
    return True

def initialize_task_queue():
    """Initialize task queue"""
    print_step(4, 10, "Initializing task queue")
    
    task_queue_path = Path("tasks/queue.json")
    if not task_queue_path.exists():
        import json
        with open(task_queue_path, 'w') as f:
            json.dump({"tasks": [], "completed": []}, f, indent=2)
        print_success("Task queue initialized")
    else:
        print_success("Task queue already exists")
    
    return True

def generate_model():
    """Generate 3D model if it doesn't exist"""
    print_step(5, 10, "Checking Victor 3D model")
    model_path = Path("visual_engine/godot_project/models/victor_head.glb")
    
    if model_path.exists():
        print_success("3D model already exists")
        return True
    
    print("  Generating 3D model...")
    try:
        subprocess.run(
            [sys.executable, "generate_victor_model.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        print_success("3D model generated (victor_head.glb)")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to generate 3D model")
        return False

def verify_victor_hub():
    """Verify Victor Hub components"""
    print_step(6, 10, "Verifying Victor Hub components")
    
    components = {
        "Victor Boot": "victor_hub/victor_boot.py",
        "Config": "victor_hub/config.yaml",
        "Skills": "victor_hub/skills/__init__.py"
    }
    
    all_present = True
    for name, path in components.items():
        if Path(path).exists():
            print_success(f"{name} found")
        else:
            print_error(f"{name} missing: {path}")
            all_present = False
    
    return all_present

def verify_visual_engine():
    """Verify Visual Engine components"""
    print_step(7, 10, "Verifying Visual Engine components")
    
    components = {
        "WebSocket Server": "visual_engine/backend/victor_visual_server.py",
        "Integration Bridge": "visual_engine/backend/victor_visual_bridge.py",
        "Godot Project": "visual_engine/godot_project/project.godot",
        "Godot Scene": "visual_engine/godot_project/scenes/VictorScene.tscn",
        "Godot Script": "visual_engine/godot_project/scripts/VictorController.gd"
    }
    
    all_present = True
    for name, path in components.items():
        if Path(path).exists():
            print_success(f"{name} found")
        else:
            print_error(f"{name} missing: {path}")
            all_present = False
    
    return all_present

def check_godot():
    """Check for Godot installation"""
    print_step(8, 10, "Checking Godot installation")
    
    # Try to find Godot
    godot_cmd = None
    
    # Check in PATH
    for cmd in ['godot', 'godot4', 'Godot']:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            if result.returncode == 0:
                godot_cmd = cmd
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    # Check common installation paths
    if not godot_cmd:
        common_paths = {
            'Darwin': ['/Applications/Godot.app/Contents/MacOS/Godot'],
            'Windows': [
                'C:\\Program Files\\Godot\\godot.exe',
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Godot', 'godot.exe')
            ],
            'Linux': ['/usr/bin/godot', '/usr/local/bin/godot']
        }
        
        system = platform.system()
        for path in common_paths.get(system, []):
            if os.path.exists(path):
                godot_cmd = path
                break
    
    if godot_cmd:
        print_success(f"Godot found: {godot_cmd}")
        return godot_cmd
    else:
        print_warning("Godot not found (optional for visual features)")
        print_info("  Visual Engine will run in backend-only mode")
        print_info("  Download from: https://godotengine.org/download")
        return None

def create_run_scripts():
    """Create quick restart scripts"""
    print_step(9, 10, "Creating launch scripts")
    
    scripts_created = []
    
    # Create unified run script for Unix
    if platform.system() != 'Windows':
        with open("run_victor_complete.sh", "w") as f:
            f.write("""#!/bin/bash
################################################################################
# Victor Complete System Launcher
# Starts both Victor Hub and Visual Engine
################################################################################

echo "════════════════════════════════════════════════════════════════════════════"
echo "                    STARTING VICTOR COMPLETE SYSTEM"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Start Visual Engine backend in background
echo "[1/3] Starting Visual Engine backend..."
python3 visual_engine/test_visual_engine.py &
VISUAL_PID=$!
echo "✓ Visual Engine started (PID: $VISUAL_PID)"

# Wait a moment for server to initialize
sleep 2

# Start Victor Hub in background
echo ""
echo "[2/3] Starting Victor Hub..."
python3 victor_hub/victor_boot.py &
HUB_PID=$!
echo "✓ Victor Hub started (PID: $HUB_PID)"

echo ""
echo "[3/3] System ready!"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "Victor Complete System is running!"
echo ""
echo "Components:"
echo "  • Visual Engine: http://127.0.0.1:8765 (PID: $VISUAL_PID)"
echo "  • Victor Hub: Running (PID: $HUB_PID)"
echo ""
echo "Next steps:"
echo "  1. Open Godot: visual_engine/godot_project/project.godot"
echo "  2. Press F5 in Godot to see Victor's visual presence"
echo "  3. Interact with Victor Hub via the CLI"
echo ""
echo "Press Ctrl+C to stop both systems"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Wait for both processes
wait $VISUAL_PID $HUB_PID
""")
        os.chmod("run_victor_complete.sh", 0o755)
        scripts_created.append("run_victor_complete.sh")
        
        # Also create individual run scripts
        with open("run_victor_hub.sh", "w") as f:
            f.write("""#!/bin/bash
echo "Starting Victor Hub..."
python3 victor_hub/victor_boot.py
""")
        os.chmod("run_victor_hub.sh", 0o755)
        scripts_created.append("run_victor_hub.sh")
        
        with open("run_visual_engine.sh", "w") as f:
            f.write("""#!/bin/bash
echo "Starting Visual Engine..."
python3 visual_engine/test_visual_engine.py
""")
        os.chmod("run_visual_engine.sh", 0o755)
        scripts_created.append("run_visual_engine.sh")
    
    # Create batch files for Windows
    else:
        with open("run_victor_complete.bat", "w") as f:
            f.write("""@echo off
REM ============================================================================
REM Victor Complete System Launcher
REM Starts both Victor Hub and Visual Engine
REM ============================================================================

echo ============================================================================
echo                     STARTING VICTOR COMPLETE SYSTEM
echo ============================================================================
echo.

echo [1/3] Starting Visual Engine backend...
start /b python visual_engine\\test_visual_engine.py
timeout /t 2 /nobreak >nul
echo √ Visual Engine started

echo.
echo [2/3] Starting Victor Hub...
start /b python victor_hub\\victor_boot.py
timeout /t 1 /nobreak >nul
echo √ Victor Hub started

echo.
echo [3/3] System ready!
echo.
echo ============================================================================
echo Victor Complete System is running!
echo.
echo Components:
echo   • Visual Engine: http://127.0.0.1:8765
echo   • Victor Hub: Running
echo.
echo Next steps:
echo   1. Open Godot: visual_engine\\godot_project\\project.godot
echo   2. Press F5 in Godot to see Victor's visual presence
echo   3. Interact with Victor Hub via the CLI
echo.
echo Press any key to stop both systems
echo ============================================================================
echo.

pause
""")
        scripts_created.append("run_victor_complete.bat")
        
        with open("run_victor_hub.bat", "w") as f:
            f.write("""@echo off
echo Starting Victor Hub...
python victor_hub\\victor_boot.py
pause
""")
        scripts_created.append("run_victor_hub.bat")
        
        with open("run_visual_engine.bat", "w") as f:
            f.write("""@echo off
echo Starting Visual Engine...
python visual_engine\\test_visual_engine.py
pause
""")
        scripts_created.append("run_visual_engine.bat")
    
    for script in scripts_created:
        print_success(f"Created {script}")
    
    return True

def show_final_instructions(godot_cmd):
    """Show final instructions"""
    print_step(10, 10, "Installation complete!")
    
    print_header("VICTOR COMPLETE SYSTEM - READY TO RUN!")
    
    print(f"{Colors.CYAN}Three ways to run Victor:{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}Option 1: Complete System (Recommended){Colors.NC}")
    print("  Runs both Victor Hub and Visual Engine together")
    if platform.system() != 'Windows':
        print(f"  Command: {Colors.GREEN}./run_victor_complete.sh{Colors.NC}\n")
    else:
        print(f"  Command: {Colors.GREEN}run_victor_complete.bat{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}Option 2: Victor Hub Only{Colors.NC}")
    print("  Run just the AGI core without visual interface")
    if platform.system() != 'Windows':
        print(f"  Command: {Colors.GREEN}./run_victor_hub.sh{Colors.NC}")
    else:
        print(f"  Command: {Colors.GREEN}run_victor_hub.bat{Colors.NC}")
    print(f"  Or: {Colors.GREEN}python victor_hub/victor_boot.py{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}Option 3: Visual Engine Only{Colors.NC}")
    print("  Run just the 3D visual interface")
    if platform.system() != 'Windows':
        print(f"  Command: {Colors.GREEN}./run_visual_engine.sh{Colors.NC}")
    else:
        print(f"  Command: {Colors.GREEN}run_visual_engine.bat{Colors.NC}")
    print(f"  Or: {Colors.GREEN}python visual_engine/test_visual_engine.py{Colors.NC}\n")
    
    print(f"{Colors.CYAN}System Components Installed:{Colors.NC}")
    print("  ✓ Victor Hub - AGI reasoning core")
    print("  ✓ Skills System - Extensible capabilities")
    print("  ✓ Visual Engine - 3D avatar interface")
    print("  ✓ Task Queue - Job management")
    print("  ✓ WebSocket Server - Real-time communication")
    print("  ✓ Configuration - Full system settings")
    
    if godot_cmd:
        print(f"\n{Colors.CYAN}Godot Integration:{Colors.NC}")
        print(f"  ✓ Godot detected: {godot_cmd}")
        print("  ✓ Ready to launch visual interface")
    else:
        print(f"\n{Colors.YELLOW}Godot (Optional):{Colors.NC}")
        print("  ⚠ Not detected - visual interface runs in backend mode")
        print("  ℹ Download: https://godotengine.org/download")
        print("  ℹ After installing, open: visual_engine/godot_project/project.godot")

def start_complete_system(godot_cmd):
    """Start the complete Victor system"""
    print_header("STARTING VICTOR COMPLETE SYSTEM")
    
    print(f"{Colors.YELLOW}Starting components...{Colors.NC}\n")
    
    # Start Visual Engine backend
    print("[1/3] Starting Visual Engine backend...")
    visual_process = subprocess.Popen(
        [sys.executable, "visual_engine/test_visual_engine.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)
    print_success(f"Visual Engine started (PID: {visual_process.pid})")
    
    # Start Victor Hub
    print("\n[2/3] Starting Victor Hub...")
    hub_process = subprocess.Popen(
        [sys.executable, "victor_hub/victor_boot.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)
    print_success(f"Victor Hub started (PID: {hub_process.pid})")
    
    # Try to launch Godot
    print("\n[3/3] Setting up visual interface...")
    if godot_cmd:
        project_path = "visual_engine/godot_project/project.godot"
        if os.path.exists(project_path):
            try:
                subprocess.Popen([godot_cmd, project_path])
                print_success("Godot launched")
                print_info("Press F5 in Godot to see Victor's visual presence")
            except Exception as e:
                print_error(f"Failed to launch Godot: {e}")
        else:
            print_error("Godot project file not found")
    else:
        print_warning("Godot not found - visual interface running in backend mode")
    
    print("\n" + "=" * 80)
    print(f"{Colors.GREEN}Victor Complete System is running!{Colors.NC}\n")
    print("What you should see:")
    print("  • Visual Engine: Cycling through emotion states")
    print("  • Victor Hub: Processing tasks and running skills")
    if godot_cmd:
        print("  • Godot: Victor's glowing helmet with changing colors\n")
    else:
        print("  • Backend: Running (Godot optional for visuals)\n")
    
    print("Components running:")
    print(f"  • Visual Engine (PID: {visual_process.pid})")
    print(f"  • Victor Hub (PID: {hub_process.pid})")
    
    print(f"\n{Colors.YELLOW}Press Ctrl+C to stop all systems{Colors.NC}")
    print("=" * 80 + "\n")
    
    try:
        visual_process.wait()
        hub_process.wait()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stopping Victor systems...{Colors.NC}")
        visual_process.terminate()
        hub_process.terminate()
        visual_process.wait()
        hub_process.wait()
        print_success("All systems stopped")

def main():
    """Main installation function"""
    print_header("VICTOR SYNTHETIC SUPER INTELLIGENCE - COMPLETE SYSTEM INSTALLER")
    
    print(f"{Colors.CYAN}This installer will set up the entire Victor ecosystem:{Colors.NC}")
    print("  • Victor Hub - AGI reasoning and orchestration")
    print("  • Skills System - Extensible capabilities")
    print("  • Visual Engine - Real-time 3D avatar interface")
    print("  • Task Queue - Job management system")
    print("  • Configuration - Full system settings")
    print()
    
    # Run all checks
    if not check_python():
        return 1
    
    if not check_directory():
        return 1
    
    if not install_dependencies():
        return 1
    
    if not setup_directories():
        return 1
    
    if not initialize_task_queue():
        return 1
    
    if not generate_model():
        return 1
    
    if not verify_victor_hub():
        return 1
    
    if not verify_visual_engine():
        return 1
    
    godot_cmd = check_godot()
    
    if not create_run_scripts():
        return 1
    
    show_final_instructions(godot_cmd)
    
    # Ask if user wants to start now
    try:
        response = input(f"\n{Colors.CYAN}Would you like to start the complete system now? [Y/n]: {Colors.NC}").strip().lower()
        if response in ['', 'y', 'yes']:
            start_complete_system(godot_cmd)
        else:
            print(f"\n{Colors.CYAN}Installation complete! Start the system when ready.{Colors.NC}")
            print(f"\nQuick start: {Colors.GREEN}./run_victor_complete.sh{Colors.NC if platform.system() != 'Windows' else 'run_victor_complete.bat'}")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Installation complete! Start the system when ready.{Colors.NC}")
    
    print(f"\n{Colors.GREEN}Victor Synthetic Super Intelligence is ready to run!{Colors.NC}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
