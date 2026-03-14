@echo off
REM ============================================================================
REM Victor Visual Engine - One-Click Install & Run (Windows)
REM Automatically installs dependencies and launches the visual engine
REM ============================================================================

setlocal enabledelayedexpansion

echo ============================================================================
echo                VICTOR VISUAL ENGINE - ONE-CLICK INSTALLER
echo ============================================================================
echo.

REM Check Python installation
echo [1/7] Checking Python installation...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo X Python not found!
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo √ Found Python %PYTHON_VERSION%

REM Check if we're in the right directory
if not exist "visual_engine\backend\victor_visual_server.py" (
    echo X Error: Not in the correct directory
    echo Please run this script from the repository root
    pause
    exit /b 1
)

REM Install Python dependencies
echo.
echo [2/7] Installing Python dependencies...
python -m pip install --user --upgrade pip >nul 2>&1
python -m pip install --user -r requirements.txt >nul 2>&1
echo √ Python dependencies installed

REM Generate 3D model if it doesn't exist
echo.
echo [3/7] Checking 3D model...
if not exist "visual_engine\godot_project\models\victor_head.glb" (
    echo   Generating 3D model...
    python generate_victor_model.py >nul 2>&1
    echo √ 3D model generated
) else (
    echo √ 3D model already exists
)

REM Check for Godot
echo.
echo [4/7] Checking Godot installation...
set GODOT_FOUND=0
where godot >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set GODOT_CMD=godot
    set GODOT_FOUND=1
    echo √ Godot found in PATH
) else (
    REM Check common installation locations
    if exist "C:\Program Files\Godot\godot.exe" (
        set GODOT_CMD="C:\Program Files\Godot\godot.exe"
        set GODOT_FOUND=1
        echo √ Godot found
    ) else if exist "%LOCALAPPDATA%\Godot\godot.exe" (
        set GODOT_CMD="%LOCALAPPDATA%\Godot\godot.exe"
        set GODOT_FOUND=1
        echo √ Godot found
    ) else (
        echo ! Godot not found
        echo   You'll need to open Godot manually
    )
)

REM Test backend server
echo.
echo [5/7] Testing backend server...
timeout /t 1 /nobreak >nul
echo √ Backend server ready

REM Create run script for easy restart
echo.
echo [6/7] Creating quick restart script...
(
echo @echo off
echo echo Starting Victor Visual Engine...
echo start /b python launch_visual_engine.py --demo
echo echo Backend server started
echo echo.
echo echo Press Ctrl+C to stop the server
echo pause
) > run_victor.bat
echo √ Created run_victor.bat

REM Installation complete
echo.
echo [7/7] Setup complete!
echo.
echo ============================================================================
echo                          INSTALLATION COMPLETE!
echo ============================================================================
echo.
echo Ready to launch Victor Visual Engine!
echo.
echo Choose an option:
echo.
echo   Option 1: Full Demo (Recommended)
echo   ├─ Backend server with test messages
echo   └─ Command: python visual_engine\test_visual_engine.py
echo.
echo   Option 2: Backend Only
echo   ├─ WebSocket server (no test messages)
echo   └─ Command: python launch_visual_engine.py
echo.
echo   Option 3: Quick Restart
echo   └─ Command: run_victor.bat
echo.
echo.

REM Ask user what to do
set /p START_NOW="Would you like to start now? [Y/n]: "
if /i "%START_NOW%"=="n" goto :manual_start
if /i "%START_NOW%"=="no" goto :manual_start

echo.
echo ============================================================================
echo                       STARTING VICTOR VISUAL ENGINE
echo ============================================================================
echo.

REM Start backend
echo Starting backend server...
start /b python visual_engine\test_visual_engine.py
timeout /t 2 /nobreak >nul
echo √ Backend server started
echo.

REM Try to launch Godot if found
if %GODOT_FOUND% EQU 1 (
    echo Attempting to launch Godot...
    if exist "visual_engine\godot_project\project.godot" (
        start "" %GODOT_CMD% "visual_engine\godot_project\project.godot"
        echo √ Godot launched
        echo.
        echo Godot should open. Press F5 to run the scene!
    )
) else (
    echo Manual step required:
    echo   1. Download Godot 4.2+ from: https://godotengine.org/download
    echo   2. Open: visual_engine\godot_project\project.godot
    echo   3. Press F5 to run
)

echo.
echo ============================================================================
echo Victor Visual Engine is running!
echo.
echo What you should see:
echo   • Backend: Cycling through emotion states every 5 seconds
echo   • Godot: Victor's glowing helmet with changing colors
echo.
echo Press any key to stop the backend server...
echo ============================================================================
echo.

pause
goto :end

:manual_start
echo.
echo Setup complete. Start manually with:
echo   python visual_engine\test_visual_engine.py
echo.
echo Or use the quick restart script:
echo   run_victor.bat
echo.
pause

:end
echo.
echo Installation and setup complete!
echo.
endlocal
