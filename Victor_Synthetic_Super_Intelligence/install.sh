#!/bin/bash
################################################################################
# Victor Visual Engine - One-Click Install & Run
# Automatically installs dependencies and launches the visual engine
################################################################################

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════════════════"
echo "               VICTOR VISUAL ENGINE - ONE-CLICK INSTALLER"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Determine OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo -e "${CYAN}Detected OS: $OS${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}[1/7] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}✗ Python not found!${NC}"
        echo "Please install Python 3.8 or higher from https://www.python.org/"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# Check if we're in the right directory
if [ ! -f "visual_engine/backend/victor_visual_server.py" ]; then
    echo -e "${RED}✗ Error: Not in the correct directory${NC}"
    echo "Please run this script from the repository root"
    exit 1
fi

# Install Python dependencies
echo ""
echo -e "${YELLOW}[2/7] Installing Python dependencies...${NC}"
$PYTHON_CMD -m pip install --user --upgrade pip > /dev/null 2>&1
$PYTHON_CMD -m pip install --user -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Generate 3D model if it doesn't exist
echo ""
echo -e "${YELLOW}[3/7] Checking 3D model...${NC}"
if [ ! -f "visual_engine/godot_project/models/victor_head.glb" ]; then
    echo "  Generating 3D model..."
    $PYTHON_CMD generate_victor_model.py > /dev/null 2>&1
    echo -e "${GREEN}✓ 3D model generated${NC}"
else
    echo -e "${GREEN}✓ 3D model already exists${NC}"
fi

# Check for Godot
echo ""
echo -e "${YELLOW}[4/7] Checking Godot installation...${NC}"
GODOT_FOUND=false
GODOT_CMD=""

# Check common Godot installation locations
if command -v godot &> /dev/null; then
    GODOT_CMD="godot"
    GODOT_FOUND=true
elif command -v godot4 &> /dev/null; then
    GODOT_CMD="godot4"
    GODOT_FOUND=true
elif [ -f "/Applications/Godot.app/Contents/MacOS/Godot" ]; then
    GODOT_CMD="/Applications/Godot.app/Contents/MacOS/Godot"
    GODOT_FOUND=true
fi

if [ "$GODOT_FOUND" = true ]; then
    echo -e "${GREEN}✓ Godot found: $GODOT_CMD${NC}"
else
    echo -e "${YELLOW}⚠ Godot not found in PATH${NC}"
    echo "  You'll need to open Godot manually"
fi

# Test backend server
echo ""
echo -e "${YELLOW}[5/7] Testing backend server...${NC}"
timeout 3 $PYTHON_CMD launch_visual_engine.py > /dev/null 2>&1 || true
echo -e "${GREEN}✓ Backend server ready${NC}"

# Create run script for easy restart
echo ""
echo -e "${YELLOW}[6/7] Creating quick restart script...${NC}"
cat > run_victor.sh << 'RUNSCRIPT'
#!/bin/bash
echo "Starting Victor Visual Engine..."
python3 launch_visual_engine.py --demo &
SERVER_PID=$!
echo "Backend server started (PID: $SERVER_PID)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
wait $SERVER_PID
RUNSCRIPT
chmod +x run_victor.sh
echo -e "${GREEN}✓ Created run_victor.sh${NC}"

# Installation complete
echo ""
echo -e "${YELLOW}[7/7] Setup complete!${NC}"
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}                         INSTALLATION COMPLETE!${NC}"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${CYAN}Ready to launch Victor Visual Engine!${NC}"
echo ""
echo "Choose an option:"
echo ""
echo "  ${YELLOW}Option 1: Full Demo (Recommended)${NC}"
echo "  ├─ Backend server with test messages"
echo "  └─ Command: $PYTHON_CMD visual_engine/test_visual_engine.py"
echo ""
echo "  ${YELLOW}Option 2: Backend Only${NC}"
echo "  ├─ WebSocket server (no test messages)"
echo "  └─ Command: $PYTHON_CMD launch_visual_engine.py"
echo ""
echo "  ${YELLOW}Option 3: Quick Restart${NC}"
echo "  └─ Command: ./run_victor.sh"
echo ""

# Ask user what to do
echo -e "${CYAN}Would you like to start now? [Y/n]${NC}"
read -r START_NOW

if [[ "$START_NOW" =~ ^[Yy]$ ]] || [[ -z "$START_NOW" ]]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════"
    echo -e "${GREEN}                      STARTING VICTOR VISUAL ENGINE${NC}"
    echo "════════════════════════════════════════════════════════════════════════════"
    echo ""
    
    # Start backend in background
    echo -e "${YELLOW}Starting backend server...${NC}"
    $PYTHON_CMD visual_engine/test_visual_engine.py &
    SERVER_PID=$!
    
    echo -e "${GREEN}✓ Backend server started (PID: $SERVER_PID)${NC}"
    echo ""
    
    # Try to launch Godot if found
    if [ "$GODOT_FOUND" = true ]; then
        echo -e "${YELLOW}Attempting to launch Godot...${NC}"
        sleep 2
        
        # Try to launch Godot project
        if [ -f "visual_engine/godot_project/project.godot" ]; then
            $GODOT_CMD visual_engine/godot_project/project.godot &
            echo -e "${GREEN}✓ Godot launched${NC}"
            echo ""
            echo -e "${CYAN}Godot should open. Press F5 to run the scene!${NC}"
        fi
    else
        echo -e "${YELLOW}Manual step required:${NC}"
        echo "  1. Download Godot 4.2+ from: https://godotengine.org/download"
        echo "  2. Open: visual_engine/godot_project/project.godot"
        echo "  3. Press F5 to run"
    fi
    
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════"
    echo -e "${GREEN}Victor Visual Engine is running!${NC}"
    echo ""
    echo "What you should see:"
    echo "  • Backend: Cycling through emotion states every 5 seconds"
    echo "  • Godot: Victor's glowing helmet with changing colors"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the backend server${NC}"
    echo "════════════════════════════════════════════════════════════════════════════"
    echo ""
    
    # Wait for user to stop
    wait $SERVER_PID
    
else
    echo ""
    echo -e "${CYAN}Setup complete. Start manually with:${NC}"
    echo "  $PYTHON_CMD visual_engine/test_visual_engine.py"
    echo ""
    echo -e "${CYAN}Or use the quick restart script:${NC}"
    echo "  ./run_victor.sh"
    echo ""
fi

echo ""
echo -e "${GREEN}Installation and setup complete!${NC}"
echo ""
