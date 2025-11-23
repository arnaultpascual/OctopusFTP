# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.9.x   | :white_check_mark: |
| 0.8.x   | :white_check_mark: |
| < 0.8   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in OctopusFTP, please report it privately to protect users.

### How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report security issues via:

1. **GitHub Security Advisories** (Recommended):
   - Go to the [Security tab](https://github.com/arnaultpascual/OctopusFTP/security/advisories)
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **GitHub Issues** (for non-critical issues):
   - Open a private issue at https://github.com/arnaultpascual/OctopusFTP/issues
   - Mark it with the "security" label

### What to Include

Please include the following information in your report:

- **Description** of the vulnerability
- **Steps to reproduce** the issue
- **Impact** of the vulnerability (what can an attacker do?)
- **Affected versions** (which versions are vulnerable?)
- **Suggested fix** (if you have one)
- **Your contact information** (if you want credit for the discovery)

### What to Expect

**Note**: OctopusFTP is maintained by a solo developer. While I take security seriously, please understand response times may vary:

- **Response time**: I'll do my best to respond within a few days. This is a side project, so please be patient.
- **Fix timeline**: Critical issues will be prioritized, but timelines depend on severity and complexity
- **Credit**: You'll be credited in the security advisory (unless you prefer anonymity)
- **Updates**: I'll keep you informed throughout the process

### Security Best Practices for Users

When using OctopusFTP:

1. **Credentials**: Never hardcode FTP credentials in scripts
2. **Saved connections**: Passwords in `~/.octopusftp/connections.json` are stored in plain text - only use on trusted machines
3. **SSL/TLS**: Always use FTPS when connecting to servers over the internet
4. **Updates**: Keep OctopusFTP updated to the latest version
5. **Source**: Only download OctopusFTP from official sources (GitHub releases)

### Known Security Considerations

- **Plain text passwords**: Saved connections store passwords in plain text in `~/.octopusftp/connections.json`
  - **Mitigation**: Only save passwords on secure, personal computers
  - **Future**: Encrypted password storage is planned for a future version

Thank you for helping keep OctopusFTP secure!
