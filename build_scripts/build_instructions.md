# OctopusFTP - Build Instructions

This document explains how to create standalone executables for OctopusFTP.

## Prerequisites

- Python 3.8 or higher installed
- pip (Python package installer)

## Building for Windows

1. Open Command Prompt or PowerShell
2. Navigate to the `build_scripts` directory:
   ```cmd
   cd path\to\OctopusFTP\build_scripts
   ```
3. Run the build script:
   ```cmd
   build_windows.bat
   ```
4. The executable will be created in `dist\OctopusFTP.exe`

### Windows Notes

- The first build may take several minutes
- You may see warnings from Windows Defender - this is normal for PyInstaller executables
- The executable is portable - no Python installation needed on target machines
- Typical size: ~15-25 MB

## Building for Mac

1. Open Terminal
2. Navigate to the `build_scripts` directory:
   ```bash
   cd path/to/OctopusFTP/build_scripts
   ```
3. Make the script executable (first time only):
   ```bash
   chmod +x build_mac.sh
   ```
4. Run the build script:
   ```bash
   ./build_mac.sh
   ```
5. The application will be created in `dist/OctopusFTP.app`

### Mac Notes

- The first build may take several minutes
- You can move the `.app` to your Applications folder
- On first run, right-click > Open to bypass security warning (unsigned app)
- The app is portable - no Python installation needed on target machines
- Typical size: ~30-40 MB (with bundled dependencies)

### Apple Silicon (M1/M2/M3) Notes

**Important**: The regular build script now automatically detects your architecture and builds accordingly:
- On Apple Silicon (M1/M2/M3): Builds native arm64 binary
- On Intel: Builds x86_64 binary

**For Universal Binaries** (works on both Intel and Apple Silicon):
```bash
chmod +x build_mac_universal.sh
./build_mac_universal.sh
```

**Troubleshooting Mac Silicon crashes**:
If the app crashes on launch:
1. Make sure you're using the latest PyInstaller: `pip install --upgrade pyinstaller`
2. Use the updated build script (includes `--target-arch arm64`)
3. Ensure you have Python installed via Homebrew (not Apple's bundled Python):
   ```bash
   brew install python-tk@3.12
   ```
4. Try the universal build script instead

## Building for Linux

1. Open Terminal
2. Navigate to the `build_scripts` directory:
   ```bash
   cd path/to/OctopusFTP/build_scripts
   ```
3. Make the script executable (first time only):
   ```bash
   chmod +x build_linux.sh
   ```
4. Run the build script:
   ```bash
   ./build_linux.sh
   ```
5. The executable will be created in `dist/OctopusFTP`

### Linux Notes

- The first build may take several minutes
- The executable is architecture-specific (x86_64, ARM, etc.)
- Users need the same architecture to run the executable
- No Python installation needed on target machines
- Typical size: ~15-25 MB
- For broader compatibility, consider distributing as source code

### Creating a Desktop Entry (Linux)

Create a `.desktop` file for application menu integration:

```bash
cat > ~/.local/share/applications/octopusftp.desktop <<EOF
[Desktop Entry]
Name=OctopusFTP
Comment=Multi-Connection FTP Downloader
Exec=/path/to/OctopusFTP
Icon=/path/to/icon.png
Terminal=false
Type=Application
Categories=Network;FileTransfer;
EOF
```

## Troubleshooting

### "Python not found"
- Ensure Python 3.8+ is installed and in your PATH
- Windows: Download from [python.org](https://www.python.org/)
- Mac: Use Homebrew: `brew install python3`

### "PyInstaller failed"
- Try upgrading pip: `python -m pip install --upgrade pip`
- Install PyInstaller manually: `pip install pyinstaller`
- Check for conflicting packages

### "Permission denied" (Mac)
- Make the script executable: `chmod +x build_mac.sh`
- Run with sudo if needed: `sudo ./build_mac.sh`

### Large executable size
- This is normal for PyInstaller - it bundles Python and all dependencies
- The final executable is self-contained and portable

## Distribution

### Windows
- Share the `OctopusFTP.exe` file
- Users can run it directly (no installation needed)
- May trigger antivirus warnings (false positive - common with PyInstaller)

### Mac
- Share the `OctopusFTP.app` bundle
- Users should move it to Applications folder
- First run requires right-click > Open (unsigned app warning)
- Consider creating a DMG for easier distribution:
  ```bash
  hdiutil create -volname "OctopusFTP" -srcfolder dist/OctopusFTP.app -ov -format UDZO OctopusFTP.dmg
  ```

### Console Version (for debugging)
Remove `--windowed` flag to see console output:
```bash
pyinstaller --onefile --name="OctopusFTP" main.py
```

### Optimize Size
Use UPX compression (if available):
```bash
pyinstaller --onefile --windowed --name="OctopusFTP" --upx-dir=/path/to/upx main.py
```

## Signing (Optional)

### Windows Code Signing
1. Obtain a code signing certificate
2. Sign the executable:
   ```cmd
   signtool sign /f certificate.pfx /p password /t http://timestamp.server.com dist\OctopusFTP.exe
   ```

### Mac Code Signing
1. Obtain an Apple Developer certificate
2. Sign the application:
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/OctopusFTP.app
   ```

## Support

For issues or questions:
- Check the main README.md
- Review Python and PyInstaller documentation
- Ensure all Python dependencies are satisfied
