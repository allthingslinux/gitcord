# Security Policy

## Supported Versions

> ⚠️ **Note**: GitCord is in **early development**. Many features are experimental or incomplete. Use only in controlled environments until a stable release is announced.

---

## Reporting a Vulnerability

If you discover a security vulnerability in GitCord, we strongly encourage responsible disclosure. Please follow the process below:

### 🔒 Private Disclosure Process

- Email the core maintainer directly at **security@allthingslinux.org**
- Do **not** open a public issue. This helps us address vulnerabilities before they're exploited.
- Include:
  - A detailed description of the issue
  - Steps to reproduce
  - The potential impact
  - Suggested fixes or mitigation (if any)

We aim to acknowledge all reports within **72 hours** and resolve verified issues within **7–14 days**, depending on severity.

### 🛡 What Happens Next

- The team will validate the vulnerability.
- If accepted, we’ll prioritize a fix and publish an update.
- Security reporters will be credited in release notes unless anonymity is requested.
- Low-risk or non-critical issues may be queued for a later release.

---

## Known Insecure Areas

As of now, the following parts of GitCord are **not secure** and should not be used in production:
- `!fetchurl`: Accepts unvalidated URLs and renders raw HTML
- Commands accessible to any server member
- Lack of permission validation and input sanitization

Until a secure permission and validation system is implemented, **do not deploy GitCord in public or untrusted servers**.

When a secure, production-ready built is ready, a large notice will be present in the repo's README

---

Thank you for keeping GitCord safe!
