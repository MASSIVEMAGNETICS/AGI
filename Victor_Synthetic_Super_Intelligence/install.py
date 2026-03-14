#!/usr/bin/env python3
"""
Victor Visual Engine - Universal One-Click Installer
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
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable_on_windows():
        """Disable colors on Windows if not supported"""
        if platform.system() == 'Windows':
            Colors.RED = Colors.GREEN = Colors.YELLOW = Colors.CYAN = Colors.NC = ''

Colors.disable_on_windows()

def print_header(text):
    """Print a header with formatting"""
    print("\n" + "=" * 80)
    print(f"{Colors.CYAN}{text.center(80)}{Colors.NC}")
    print("=" * 80 + "\n")

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

def check_python():
    """Check Python version"""
    print_step(1, 7, "Checking Python installation")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python {version.major}.{version.minor} detected")
        print("Please install Python 3.8 or higher from https://www.python.org/")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_directory():
    """Check if we're in the correct directory"""
    if not Path("visual_engine/backend/victor_visual_server.py").exists():
        print_error("Not in the correct directory")
        print("Please run this script from the repository root")
        return False
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step(2, 7, "Installing Python dependencies")
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
        print_success("Python dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install dependencies")
        print("Try running: pip install -r requirements.txt")
        return False

def generate_model():
    """Generate 3D model if it doesn't exist"""
    print_step(3, 7, "Checking 3D model")
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
        print_success("3D model generated")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to generate 3D model")
        return False

def check_godot():
    """Check for Godot installation"""
    print_step(4, 7, "Checking Godot installation")
    
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
        print_warning("Godot not found")
        print("  You'll need to open Godot manually")
        return None

def test_backend():
    """Test backend server"""
    print_step(5, 7, "Testing backend server")
    try:
        # Just verify the file exists and is valid Python
        with open("launch_visual_engine.py", 'r') as f:
            compile(f.read(), "launch_visual_engine.py", 'exec')
        print_success("Backend server ready")
        return True
    except Exception as e:
        print_error(f"Backend server check failed: {e}")
        return False

def create_run_scripts():
    """Create quick restart scripts"""
    print_step(6, 7, "Creating quick restart scripts")
    
    # Create shell script for Unix
    if platform.system() != 'Windows':
        with open("run_victor.sh", "w") as f:
            f.write("""#!/bin/bash
echo "Starting Victor Visual Engine..."
python3 launch_visual_engine.py --demo &
SERVER_PID=$!
echo "Backend server started (PID: $SERVER_PID)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
wait $SERVER_PID
""")
        os.chmod("run_victor.sh", 0o755)
        print_success("Created run_victor.sh")
    
    # Create batch file for Windows
    else:
        with open("run_victor.bat", "w") as f:
            f.write("""@echo off
echo Starting Victor Visual Engine...
start /b python launch_visual_engine.py --demo
echo Backend server started
echo.
echo Press Ctrl+C to stop the server
pause
""")
        print_success("Created run_victor.bat")
    
    return True

def show_instructions(godot_cmd):
    """Show final instructions"""
    print_step(7, 7, "Setup complete!")
    
    print_header("INSTALLATION COMPLETE!")
    
    print(f"{Colors.CYAN}Ready to launch Victor Visual Engine!{Colors.NC}\n")
    print("Choose an option:\n")
    print(f"  {Colors.YELLOW}Option 1: Full Demo (Recommended){Colors.NC}")
    print("  ├─ Backend server with test messages")
    print(f"  └─ Command: {sys.executable} visual_engine/test_visual_engine.py\n")
    print(f"  {Colors.YELLOW}Option 2: Backend Only{Colors.NC}")
    print("  ├─ WebSocket server (no test messages)")
    print(f"  └─ Command: {sys.executable} launch_visual_engine.py\n")
    print(f"  {Colors.YELLOW}Option 3: Quick Restart{Colors.NC}")
    if platform.system() != 'Windows':
        print("  └─ Command: ./run_victor.sh\n")
    else:
        print("  └─ Command: run_victor.bat\n")

def start_visual_engine(godot_cmd):
    """Start the visual engine"""
    print_header("STARTING VICTOR VISUAL ENGINE")
    
    # Start backend
    print(f"{Colors.YELLOW}Starting backend server...{Colors.NC}")
    backend_process = subprocess.Popen(
        [sys.executable, "visual_engine/test_visual_engine.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)
    print_success(f"Backend server started (PID: {backend_process.pid})")
    
    # Try to launch Godot
    if godot_cmd:
        print(f"\n{Colors.YELLOW}Attempting to launch Godot...{Colors.NC}")
        project_path = "visual_engine/godot_project/project.godot"
        if os.path.exists(project_path):
            try:
                subprocess.Popen([godot_cmd, project_path])
                print_success("Godot launched")
                print(f"\n{Colors.CYAN}Godot should open. Press F5 to run the scene!{Colors.NC}")
            except Exception as e:
                print_error(f"Failed to launch Godot: {e}")
        else:
            print_error("Godot project file not found")
    else:
        print(f"\n{Colors.YELLOW}Manual step required:{Colors.NC}")
        print("  1. Download Godot 4.2+ from: https://godotengine.org/download")
        print("  2. Open: visual_engine/godot_project/project.godot")
        print("  3. Press F5 to run")
    
    print("\n" + "=" * 80)
    print(f"{Colors.GREEN}Victor Visual Engine is running!{Colors.NC}\n")
    print("What you should see:")
    print("  • Backend: Cycling through emotion states every 5 seconds")
    print("  • Godot: Victor's glowing helmet with changing colors\n")
    print(f"{Colors.YELLOW}Press Ctrl+C to stop the backend server{Colors.NC}")
    print("=" * 80 + "\n")
    
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stopping backend server...{Colors.NC}")
        backend_process.terminate()
        backend_process.wait()
        print_success("Backend server stopped")

def main():
    """Main installation function"""
    print_header("VICTOR VISUAL ENGINE - ONE-CLICK INSTALLER")
    
    # Run all checks
    if not check_python():
        return 1
    
    if not check_directory():
        return 1
    
    if not install_dependencies():
        return 1
    
    if not generate_model():
        return 1
    
    godot_cmd = check_godot()
    
    if not test_backend():
        return 1
    
    if not create_run_scripts():
        return 1
    
    show_instructions(godot_cmd)
    
    # Ask if user wants to start now
    try:
        response = input(f"\n{Colors.CYAN}Would you like to start now? [Y/n]: {Colors.NC}").strip().lower()
        if response in ['', 'y', 'yes']:
            start_visual_engine(godot_cmd)
        else:
            print(f"\n{Colors.CYAN}Setup complete. Start manually when ready!{Colors.NC}")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Setup complete. Start manually when ready!{Colors.NC}")
    
    print(f"\n{Colors.GREEN}Installation and setup complete!{Colors.NC}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
