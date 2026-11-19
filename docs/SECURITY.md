# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.0   | ✅        |

## Reporting a Vulnerability

Please disclose security issues responsibly. Do not open public issues for security vulnerabilities.

## Secret Management

- GitHub tokens are least-privilege (`repo`, `workflow` scopes only).
- Tokens are never stored in plaintext or exposed to the frontend.
- Secret findings from scans are redacted; complete values are never displayed.

## Scanner Safety

Scanners run in isolated containers/restricted environments. Untrusted repository code is never executed on the host with unrestricted permissions.
