# Contributing to OctopusFTP

Thank you for considering contributing to OctopusFTP! This document provides guidelines for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior via [GitHub Issues](https://github.com/arnaultpascual/OctopusFTP/issues).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

**Required Information:**
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**:
  - OS (Windows/macOS/Linux)
  - Python version (`python --version`)
  - OctopusFTP version
- **Logs/Screenshots**: Any relevant error messages or screenshots

**Example Bug Report:**
```markdown
**Bug**: Download freezes at 99%

**Steps to Reproduce:**
1. Connect to FTP server xyz.com
2. Download file larger than 5GB
3. Observe freeze at 99%

**Expected**: Download completes successfully
**Actual**: Freezes, no error message

**Environment**: Windows 11, Python 3.12, OctopusFTP v0.9.0
```

### Suggesting Features

Feature suggestions are welcome! When suggesting a feature:

- **Check existing issues** for similar requests
- **Describe the problem** your feature would solve
- **Describe your proposed solution** clearly
- **Describe alternatives** you've considered
- **Additional context**: Screenshots, mockups, examples

**Example Feature Request:**
```markdown
**Feature**: Resume failed downloads automatically

**Problem**: When downloads fail due to connection issues, users must manually restart

**Solution**: Add automatic retry with exponential backoff (3 retries, 5s/10s/20s delays)

**Alternatives**: Manual retry button only

**Context**: Common for unstable connections
```

### Pull Requests

We welcome pull requests! Please follow this process:

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our [coding standards](#coding-standards)
3. **Test your changes** thoroughly
4. **Update documentation** (README, docstrings) if needed
5. **Commit** following our [commit guidelines](#commit-guidelines)
6. **Submit a pull request** with a clear description

**Pull Request Checklist:**
- [ ] Code follows the project's coding standards
- [ ] All tests pass (if applicable)
- [ ] Documentation updated (README, docstrings)
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts with `main`
- [ ] Feature/fix is tested on at least one platform

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setup Steps

1. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/OctopusFTP.git
   cd OctopusFTP
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   # or
   ./run.sh  (macOS/Linux)
   run.bat   (Windows)
   ```

### Testing

- **Manual testing**: Test your changes with real FTP servers
- **Cross-platform**: If possible, test on Windows, macOS, and Linux
- **Edge cases**: Test with large files, slow connections, connection failures

## Coding Standards

### Python Style

- **PEP 8**: Follow Python's style guide
- **Type Hints**: Add type hints to function signatures
  ```python
  def download_file(remote_path: str, local_path: str) -> bool:
      """Download a file from FTP server"""
      ...
  ```

- **Docstrings**: Document all functions, classes, and modules
  ```python
  def calculate_speed(bytes_downloaded: int, elapsed_time: float) -> float:
      """
      Calculate download speed in bytes per second
      
      Args:
          bytes_downloaded: Number of bytes downloaded
          elapsed_time: Time elapsed in seconds
          
      Returns:
          Download speed in bytes/second
      """
      return bytes_downloaded / elapsed_time if elapsed_time > 0 else 0
  ```

- **Comments**: Explain complex logic, not obvious code
  ```python
  # Good
  # Use token-bucket algorithm to limit download speed
  speed_limit_bytes_transferred += written
  
  # Bad (obvious)
  # Add written bytes to counter
  speed_limit_bytes_transferred += written
  ```

### Code Organization

- Keep functions focused (single responsibility)
- Avoid magic numbers (use named constants)
- Handle errors gracefully with try/except
- Use meaningful variable names

### UI/UX Standards

- **Consistency**: Match existing UI patterns and colors
- **Feedback**: Provide clear feedback for user actions (progress, errors, success)
- **Accessibility**: Use readable fonts, colors with good contrast
- **Responsiveness**: UI should remain responsive during long operations

## Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding/updating tests
- `chore`: Build process, dependencies

**Examples:**

```
feat: Add SFTP support for secure file transfers

- Implement SSH/SFTP connection handling
- Add SFTP option to connection dialog
- Update documentation with SFTP usage

Closes #42
```

```
fix: Prevent UI freeze during large directory listings

- Implement batch rendering (150 items per batch)
- Add loading indicator with progress
- UI stays responsive for 1000+ files

Fixes #89
```

### Branch Naming

- Feature: `feature/feature-name`
- Bugfix: `fix/bug-description`
- Docs: `docs/what-changed`

## Questions?

If you have questions about contributing, feel free to:
- Open a [GitHub Issue](https://github.com/arnaultpascual/OctopusFTP/issues)
- Check existing documentation in the [README](README.md)

## License

By contributing to OctopusFTP, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to OctopusFTP!** 🐙
