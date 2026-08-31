# Security Policy

## Reporting a Vulnerability

The Panner AI team takes security vulnerabilities seriously. If you discover a security vulnerability in Panner AI, please report it to us responsibly.

### How to Report

**Do not** file a public GitHub issue for security vulnerabilities. Instead, please email your report to **security@craftedwithintent.com** with the following information:

1. **Type of vulnerability** — (e.g., injection, authentication bypass, data exposure)
2. **Location** — Specific file(s), module(s), or API endpoint(s) affected
3. **Description** — Clear explanation of the vulnerability and its impact
4. **Proof of Concept** — Minimal reproducible example (code snippet, YAML test case, etc.)
5. **Suggested Fix** — If you have one (optional but appreciated)

### Response Timeline

- **Acknowledgment** — Within 24 hours
- **Initial assessment** — Within 48 hours
- **Patch or mitigation** — Within 7-14 days (depending on severity)
- **Public disclosure** — After patch is released and users have had time to upgrade

### Supported Versions

| Version | Status | Security Updates |
|---------|--------|------------------|
| 0.1.x   | Beta   | Yes (active development) |
| < 0.1.0 | EOL    | No |

### Security Best Practices

When using Panner AI in production:

1. **API Keys** — Never commit API keys (LiteLLM keys, OpenAI/Anthropic credentials) to git. Use environment variables or secure secret management.
2. **Baseline Files** — Keep `baseline.json` in `.gitignore` if it contains sensitive test data.
3. **Test Data** — Avoid hardcoding production credentials in test suites. Use environment variables.
4. **Dependencies** — Regularly run `pip install --upgrade panner-ai` to get security updates.
5. **CI/CD Integration** — Use GitHub Secrets for API keys in `.github/workflows/` (never commit to public repos).

### Scope

Panner AI is a testing framework designed to run in controlled environments (CI/CD, local development). It is **not** intended for:

- Handling sensitive user data directly
- Serving as a security scanning tool
- Operating as a network daemon exposed to untrusted networks

Security vulnerabilities in **dependencies** (typer, httpx, pydantic, litellm, etc.) should be reported to those projects directly.

### Acknowledgments

We credit security researchers and contributors who report vulnerabilities responsibly. With your permission, we will acknowledge you in the release notes.

---

**Questions?** Open an issue (non-security) or contact us at **team@craftedwithintent.com**.
