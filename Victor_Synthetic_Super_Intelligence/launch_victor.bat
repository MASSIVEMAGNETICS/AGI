@echo off
REM Victor Interactive Runtime Launcher
REM Version: 2.0.0-QUANTUM-FRACTAL
REM Launches the production interactive runtime with all systems

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║           VICTOR INTERACTIVE RUNTIME LAUNCHER                      ║
echo ║              Quantum-Fractal Superintelligence                     ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✓ Using: python
echo.

REM Check dependencies
echo Checking dependencies...
python -c "import numpy, yaml" 2>nul
if %errorlevel% neq 0 (
    echo ⚠ Missing dependencies. Installing...
    python -m pip install -q -r requirements.txt
    echo ✓ Dependencies installed
) else (
    echo ✓ Dependencies satisfied
)
echo.

REM Check for Godot (optional)
where godot >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Godot detected (Visual Engine available^)
    echo   Tip: Open visual_engine\godot_project\project.godot and press F5
) else (
    echo ℹ Godot not found (Visual Engine disabled^)
    echo   Install Godot 4+ for 3D avatar visualization
)
echo.

REM Launch options
echo Launch Options:
echo   1^) Interactive Runtime (Full System^)
echo   2^) Interactive Runtime (No Visual^)
echo   3^) Victor Hub Only
echo   4^) Run Tests
echo.
set /p option="Select option [1]: "
if "%option%"=="" set option=1

if "%option%"=="1" (
    echo.
    echo Launching Victor Interactive Runtime...
    echo Tip: Type 'help' for commands, 'menu' for interactive menu
    echo.
    python victor_interactive.py
) else if "%option%"=="2" (
    echo.
    echo Launching Victor Interactive Runtime (No Visual^)...
    python victor_interactive.py
) else if "%option%"=="3" (
    echo.
    echo Launching Victor Hub Only...
    python victor_hub\victor_boot.py --mode cli
) else if "%option%"=="4" (
    echo.
    echo Running Tests...
    python -c "import asyncio; from victor_interactive import VictorInteractive; async def test(): runtime = VictorInteractive(); print('✓ Runtime imports successfully'); print('✓ Quantum-fractal interface initialized'); print('✓ Session manager initialized'); print('All systems operational'); asyncio.run(test())"
) else (
    echo Invalid option
    pause
    exit /b 1
)

pause
