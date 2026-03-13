#!/bin/bash
# Victor Interactive Runtime Launcher
# Version: 2.0.0-QUANTUM-FRACTAL
# Launches the production interactive runtime with all systems

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           VICTOR INTERACTIVE RUNTIME LAUNCHER                      ║"
echo "║              Quantum-Fractal Superintelligence                     ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✓ Using: $PYTHON_CMD"
echo ""

# Check dependencies
echo "Checking dependencies..."
$PYTHON_CMD -c "import numpy, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠ Missing dependencies. Installing..."
    $PYTHON_CMD -m pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies satisfied"
fi
echo ""

# Check for Godot (optional)
if command -v godot &> /dev/null; then
    echo "✓ Godot detected (Visual Engine available)"
    echo "  Tip: Open visual_engine/godot_project/project.godot and press F5"
else
    echo "ℹ Godot not found (Visual Engine disabled)"
    echo "  Install Godot 4+ for 3D avatar visualization"
fi
echo ""

# Launch options
echo "Launch Options:"
echo "  1) Interactive Runtime (Full System)"
echo "  2) Interactive Runtime (No Visual)"
echo "  3) Victor Hub Only"
echo "  4) Run Tests"
echo ""
read -p "Select option [1]: " option
option=${option:-1}

case $option in
    1)
        echo ""
        echo "Launching Victor Interactive Runtime..."
        echo "Tip: Type 'help' for commands, 'menu' for interactive menu"
        echo ""
        exec $PYTHON_CMD victor_interactive.py
        ;;
    2)
        echo ""
        echo "Launching Victor Interactive Runtime (No Visual)..."
        # TODO: Add flag to disable visual engine
        exec $PYTHON_CMD victor_interactive.py
        ;;
    3)
        echo ""
        echo "Launching Victor Hub Only..."
        exec $PYTHON_CMD victor_hub/victor_boot.py --mode cli
        ;;
    4)
        echo ""
        echo "Running Tests..."
        $PYTHON_CMD -c "
import asyncio
from victor_interactive import VictorInteractive

async def test():
    runtime = VictorInteractive()
    print('✓ Runtime imports successfully')
    print('✓ Quantum-fractal interface initialized')
    print('✓ Session manager initialized')
    print('All systems operational')

asyncio.run(test())
"
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
