# OctopusFTP Release Workflow

## Overview

This project uses GitHub Actions to automatically build executables for Windows, macOS, and Linux whenever you create a new version tag.

## How to Create a Release

### Method 1: Create a Tag (Recommended)

1. **Commit all your changes** to the `main` branch

2. **Create and push a version tag:**
   ```bash
   git tag v0.8
   git push origin v0.8
   ```

3. **GitHub Actions will automatically:**
   - Build Windows .exe on Windows runner
   - Build macOS .app on macOS runner
   - Build Linux executable on Linux runner
   - Create a **draft release** with all three files attached

4. **Review and publish:**
   - Go to: https://github.com/arnaultpascual/OctopusFTP/releases
   - Find your draft release
   - Edit the release notes (add changelog, features, etc.)
   - Click "Publish release"

### Method 2: Manual Trigger

You can also manually trigger builds without creating a tag:

1. Go to: https://github.com/arnaultpascual/OctopusFTP/actions
2. Click "Build Release" workflow
3. Click "Run workflow"
4. Select the branch (usually `main`)
5. Click "Run workflow"

**Note:** Manual triggers will build the executables but **won't create a release** (only tags do that). The executables will be available as artifacts for 7 days.

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **v0.8** - Beta release
- **v1.0.0** - First stable release
- **v1.1.0** - New features (minor)
- **v1.0.1** - Bug fixes (patch)

## Pre-release vs Stable

The workflow automatically detects pre-releases:

- **Pre-release** (marked as beta): `v0.8`, `v1.0.0-beta`, `v1.0.0-rc1`, `v1.0.0-alpha`
- **Stable release**: `v1.0.0`, `v1.1.0`, `v2.0.0`

## Testing Locally on Mac

You can still test builds locally before pushing:

### macOS:
```bash
cd build_scripts
./build_mac.sh
# App will be at: dist/OctopusFTP.app
```

### Test Windows .exe on Mac:
❌ **Not possible** - You need Windows to build Windows .exe

**Solution:** Use GitHub Actions! Just push a tag and the workflow will build the .exe for you.

### Test Linux on Mac:
❌ **Not recommended** - Linux builds may not work correctly on macOS

**Solution:** Use GitHub Actions or a Linux VM

## Workflow Files

- **Workflow:** `.github/workflows/build-release.yml`
- **Build Scripts:**
  - Windows: `build_scripts/build_windows.bat`
  - macOS: `build_scripts/build_mac.sh`
  - Linux: `build_scripts/build_linux.sh`

## Troubleshooting

### Build Fails
1. Check the Actions tab: https://github.com/arnaultpascual/OctopusFTP/actions
2. Click on the failed workflow run
3. Expand the failed step to see error details
4. Fix the issue and push a new tag

### Release Not Created
- Make sure you pushed a **tag** (not just a commit)
- Tags must start with `v` (e.g., `v0.8`, `v1.0.0`)
- Check if the workflow completed successfully

### Manual Build on PC
If you need to build Windows .exe manually on a PC:
1. Install Python 3.8+ from https://python.org
2. Run: `build_scripts\build_windows.bat`

## Example: Creating v0.8 Beta

```bash
# 1. Make sure all changes are committed
git add .
git commit -m "Prepare v0.8 beta release"
git push

# 2. Create and push tag
git tag v0.8
git push origin v0.8

# 3. Wait ~5-10 minutes for builds to complete
# 4. Go to https://github.com/arnaultpascual/OctopusFTP/releases
# 5. Edit the draft release and add release notes
# 6. Publish!
```

## Benefits of GitHub Actions

✅ **Cross-platform builds** without needing Windows/Linux machines
✅ **Automated** - just push a tag
✅ **Consistent** builds on clean environments
✅ **Free** for public repositories
✅ **Fast** - builds run in parallel

---

**Ready to release? Just push a tag and GitHub will do the rest! 🚀**
