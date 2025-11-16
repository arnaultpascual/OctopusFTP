@echo off
REM OctopusFTP Launcher Script for Windows

echo Starting OctopusFTP...

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

python main.py
if errorlevel 1 (
    pause
)
