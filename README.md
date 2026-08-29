# Assay

> Precision testing tool for AI agents: semantic purity & behavioral integrity verification

**Assay** is the regression testing framework for AI. AI agents and LLM-powered applications are inherently non-deterministic. Traditional testing tools cannot evaluate semantic alignment, fuzzy constraints, or probabilistic model behaviors across commits.

**Assay bridges the gap.**

## Features

- ✅ **Deterministic Assertions:** Regex patterns, HTTP status codes, latency thresholds, JSON schema validation
- ✅ **LLM-as-a-Judge:** Score semantic alignment with Claude, GPT-4, or local LLMs
- ✅ **Baseline Tracking:** Detect regressions across commits
- ✅ **Multi-Format Reporting:** Rich CLI, JUnit XML, PR comments
- ✅ **Model Agnostic:** Works with any HTTP-accessible AI agent

## Quick Start

```bash
pip install assay-cli
assay run --config suite.yaml
```

### GitHub Actions

```yaml
- uses: craftedwithintent/assay-action@v1
  with:
    config: suite.yaml
```

## Product Tiers

| Tier | Features | Cost |
|------|----------|------|
| **Community** | Open-source CLI, GitHub Action | Free |
| **Assay Cloud** | Web dashboard, managed judge compute | $49–$199/mo |
| **Enterprise** | Self-hosted, SAML/RBAC, compliance packs | $20k–$80k+ ACV |

## License

MIT License (open-source tier). Proprietary for commercial tiers.

---

Made with 🎯 by [CraftedWithIntent](https://craftedwithintent.com)
