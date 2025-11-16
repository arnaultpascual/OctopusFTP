@echo off
REM OctopusFTP - Windows Build Script
REM This script creates a standalone executable for Windows

echo ========================================
echo OctopusFTP - Windows Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Installing PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo [2/3] Building executable...
cd ..
pyinstaller --onefile --windowed --name="OctopusFTP" --icon=NONE main.py
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [3/3] Cleaning up...
REM Keep the executable, remove build artifacts
if exist build rmdir /s /q build
if exist OctopusFTP.spec del OctopusFTP.spec

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\OctopusFTP.exe
echo.
echo You can now distribute this file to any Windows computer.
echo No Python installation required on target machines!
echo.
pause
