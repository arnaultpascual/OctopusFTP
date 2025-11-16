# Creating Releases for OctopusFTP

This guide explains how to create and publish releases on GitHub with pre-built executables.

## 📋 Release Checklist

Before creating a release:

- [ ] All tests pass
- [ ] Version number updated in code (if applicable)
- [ ] CHANGELOG updated with new features/fixes
- [ ] All builds complete successfully on all platforms
- [ ] Executables tested on clean machines
- [ ] README reflects any new features or changes

## 🏗️ Building Executables

### 1. Build for Windows

**On a Windows machine:**

```cmd
cd build_scripts
build_windows.bat
```

**Output**: `dist\OctopusFTP.exe`

**Rename for release**: `OctopusFTP-Windows.exe`

### 2. Build for macOS

**On a macOS machine:**

#### Option A: Architecture-Specific Build (Recommended)

This automatically detects and builds for your architecture (Intel or Apple Silicon):

```bash
cd build_scripts
chmod +x build_mac.sh
./build_mac.sh
```

**Output**: `dist/OctopusFTP.app` (native to your Mac)

#### Option B: Universal Binary (Advanced)

Build once, works on both Intel and Apple Silicon:

```bash
cd build_scripts
chmod +x build_mac_universal.sh
./build_mac_universal.sh
```

**Output**: `dist/OctopusFTP.app` (universal binary)

**Package for release**:
```bash
cd dist
zip -r OctopusFTP-macOS.app.zip OctopusFTP.app
```

**Final files**:
- `OctopusFTP-macOS-AppleSilicon.app.zip` (for M1/M2/M3 Macs)
- `OctopusFTP-macOS-Intel.app.zip` (for Intel Macs)
- Or: `OctopusFTP-macOS-Universal.app.zip` (works on both)

**Note**: If providing architecture-specific builds, you need access to both Intel and Apple Silicon Macs, or use the universal build.

### 3. Build for Linux

**On a Linux machine (Ubuntu/Debian recommended):**

```bash
cd build_scripts
chmod +x build_linux.sh
./build_linux.sh
```

**Output**: `dist/OctopusFTP`

**Package for release**:
```bash
cd dist
tar -czf OctopusFTP-Linux.tar.gz OctopusFTP
```

**Final file**: `OctopusFTP-Linux.tar.gz`

**Alternative**: You can also just include the source code for Linux users to run with Python.

## 📦 Creating a GitHub Release

### Method 1: Via GitHub Web Interface (Recommended)

1. **Go to your repository**: https://github.com/arnaultpascual/OctopusFTP

2. **Navigate to Releases**:
   - Click on "Releases" in the right sidebar
   - Or go directly to: https://github.com/arnaultpascual/OctopusFTP/releases

3. **Create a new release**:
   - Click "Draft a new release"

4. **Tag the release**:
   - Click "Choose a tag"
   - Enter version number (e.g., `v0.8`, `v0.9`, `v1.0.0`)
   - Follow [Semantic Versioning](https://semver.org/):
     - `v0.x` - Beta releases (pre-1.0)
     - `v1.0.0` - Major release (stable)
     - `v1.1.0` - Minor release (new features, backwards compatible)
     - `v1.0.1` - Patch release (bug fixes)

5. **Set release title**:
   - Format: `OctopusFTP v0.8 Beta`
   - Example: `OctopusFTP v0.8 Beta - Initial Release`

6. **Write release notes**:
   ```markdown
   ## 🎉 OctopusFTP v0.8 Beta - First Public Release!

   This is the initial beta release of OctopusFTP. Feedback and bug reports are welcome!

   ### ✨ Features

   - **Multi-connection downloads** with configurable parallel connections (1-16)
   - **Connection rotation** to prevent timeouts and throttling
   - **FTP & FTPS support** with SSL session reuse
   - **Modern GUI** built with CustomTkinter
   - **Connection presets** - save and manage FTP server configurations
   - **Individual download controls** - pause, resume, stop each file independently
   - **Cross-platform** - Windows, macOS (Intel + Apple Silicon), Linux

   ### 📥 Downloads

   - **Windows**: Download `OctopusFTP-Windows.exe` and run
   - **macOS**: Download `OctopusFTP-macOS.app.zip`, extract, and run
   - **Linux**: Download `OctopusFTP-Linux.tar.gz` or use source code

   ### ⚠️ Beta Notes

   - This is a beta release - testing needed across different FTP servers
   - Please report any issues on [GitHub Issues](https://github.com/arnaultpascual/OctopusFTP/issues)
   - Feedback welcome for improvements before v1.0

   ### 📖 Documentation

   See the [README](https://github.com/arnaultpascual/OctopusFTP#readme) for detailed installation and usage instructions.

   ### 🙏 Thanks

   Thank you for testing OctopusFTP beta!
   ```

7. **Attach binaries**:
   - Drag and drop or click to upload:
     - `OctopusFTP-Windows.exe`
     - `OctopusFTP-macOS.app.zip`
     - `OctopusFTP-Linux.tar.gz` (optional)
   - Files will appear in the "Attach binaries" section

8. **Set as pre-release (for beta)**:
   - ✅ Check "Set as a pre-release" (for v0.x beta versions)
   - ⚠️ Do NOT check "Set as the latest release" for beta
   - For stable v1.0.0+: uncheck pre-release and check "Set as the latest release"

9. **Publish**:
   - Click "Publish release"

### Method 2: Via GitHub CLI

```bash
# Install GitHub CLI if needed
# https://cli.github.com/

# Create release
gh release create v0.8 \
  --title "OctopusFTP v0.8 Beta - Initial Release" \
  --notes "First beta release - feedback welcome!" \
  --prerelease \
  OctopusFTP-Windows.exe \
  OctopusFTP-macOS.app.zip \
  OctopusFTP-Linux.tar.gz
```

## 🔄 Release Workflow

### For Major/Minor Releases (v1.0.0, v1.1.0)

1. Create a release branch: `git checkout -b release/v1.1.0`
2. Update version numbers in code
3. Update CHANGELOG.md
4. Build all executables
5. Test on clean machines
6. Merge to main: `git checkout main && git merge release/v1.1.0`
7. Tag the release: `git tag v1.1.0`
8. Push: `git push && git push --tags`
9. Create GitHub release with binaries
10. Announce on social media / discussions

### For Patch Releases (v1.0.1)

1. Fix bugs on main branch
2. Build executables
3. Test fixes
4. Tag: `git tag v1.0.1`
5. Push: `git push --tags`
6. Create GitHub release with binaries

## 📝 Release Notes Template

```markdown
## 🎉 What's New in v1.X.0

### ✨ New Features
- Feature 1 description
- Feature 2 description

### 🔧 Improvements
- Improvement 1
- Improvement 2

### 🐛 Bug Fixes
- Fix for issue #123
- Fix for issue #456

### 📖 Documentation
- Updated installation guide
- Added troubleshooting section

## 📥 Installation

Download the appropriate file for your platform:

- **Windows**: `OctopusFTP-Windows.exe` - No installation required
- **macOS**: `OctopusFTP-macOS.app.zip` - Extract and run
- **Linux**: `OctopusFTP-Linux.tar.gz` - Extract and run or use Python source

See the [README](https://github.com/arnaultpascual/OctopusFTP#readme) for detailed instructions.

## 🙏 Thanks

Thank you to all contributors and users who helped make this release possible!

---

**Full Changelog**: https://github.com/arnaultpascual/OctopusFTP/compare/v1.0.0...v1.1.0
```

## 🤖 Automated Releases with GitHub Actions (Optional)

Create `.github/workflows/release.yml` for automated builds:

```yaml
name: Build Release

on:
  release:
    types: [created]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Build
        run: |
          cd build_scripts
          ./build_windows.bat
      - name: Upload
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./dist/OctopusFTP.exe
          asset_name: OctopusFTP-Windows.exe
          asset_content_type: application/octet-stream

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Build
        run: |
          cd build_scripts
          chmod +x build_mac.sh
          ./build_mac.sh
          cd ../dist
          zip -r OctopusFTP-macOS.app.zip OctopusFTP.app
      - name: Upload
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./dist/OctopusFTP-macOS.app.zip
          asset_name: OctopusFTP-macOS.app.zip
          asset_content_type: application/zip

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y python3-tk
      - name: Build
        run: |
          cd build_scripts
          chmod +x build_linux.sh
          ./build_linux.sh
          cd ../dist
          tar -czf OctopusFTP-Linux.tar.gz OctopusFTP
      - name: Upload
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./dist/OctopusFTP-Linux.tar.gz
          asset_name: OctopusFTP-Linux.tar.gz
          asset_content_type: application/gzip
```

## 🏷️ Version Numbering Guide

Follow [Semantic Versioning](https://semver.org/):

- **Major** (v2.0.0): Breaking changes, major rewrites
- **Minor** (v1.1.0): New features, backwards compatible
- **Patch** (v1.0.1): Bug fixes, small improvements

Examples:
- `v1.0.0` - Initial release
- `v1.1.0` - Added SFTP support
- `v1.1.1` - Fixed connection timeout bug
- `v2.0.0` - Complete UI redesign (breaking changes)

## 📊 Release Checklist

- [ ] All platforms built successfully
- [ ] Executables tested on clean machines
- [ ] Version numbers consistent across all files
- [ ] Release notes written
- [ ] CHANGELOG.md updated
- [ ] Binaries uploaded to GitHub release
- [ ] Release marked as "latest"
- [ ] Social media announcement prepared
- [ ] Discussions/issues monitored for feedback

## 🎯 First Release Checklist

For the initial v0.8 beta release:

- [ ] Create comprehensive README
- [ ] Add LICENSE file
- [ ] Create .gitignore
- [ ] Test on Windows, macOS, and Linux
- [ ] Take screenshots for README
- [ ] Write detailed installation instructions
- [ ] Create this RELEASE.md guide
- [ ] Build all three platform executables
- [ ] Create GitHub release
- [ ] Announce on relevant communities

---

**Ready to release? Follow the steps above and share OctopusFTP with the world! 🐙🚀**
