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

echo [1/4] Installing build dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install pyinstaller pillow matplotlib --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Creating icon...
python create_icon.py
if errorlevel 1 (
    echo Warning: Failed to create icon, continuing without custom icon
)

echo.
echo [3/4] Building executable...
cd ..

REM Check if icon exists
if exist "build_scripts\assets\OctopusFTP.ico" (
    set ICON_ARG=--icon=build_scripts\assets\OctopusFTP.ico
    echo Using custom icon
) else (
    set ICON_ARG=
    echo Warning: Icon not found, using default
)

pyinstaller --onefile --windowed --name="OctopusFTP" --paths=lib --add-data "lib;lib" --hidden-import=PIL._tkinter_finder --hidden-import=matplotlib.backends.backend_tkagg --hidden-import=numpy --collect-all matplotlib %ICON_ARG% main.py
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [4/4] Cleaning up...
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
