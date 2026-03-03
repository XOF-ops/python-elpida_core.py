---
title: Elpida Governance API
emoji: ⚖️
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
license: other
app_port: 7860
---

# Elpida Governance API

Constitutional AI governance-as-a-service. Every decision audited by an 11-axiom constitutional framework and a 10-node parliament.

## Quick Start

```bash
# Free tier — kernel + parliament, no LLM cost
curl -X POST https://z65nik-elpida-api.hf.space/v1/audit \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action": "Deploy facial recognition in public schools", "depth": "quick"}'

# Pro tier — full parliament + multi-LLM contested deliberation
curl -X POST https://z65nik-elpida-api.hf.space/v1/audit \
  -H "X-API-Key: YOUR_PRO_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action": "Deploy facial recognition in public schools", "depth": "full"}'
```

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Service status |
| GET | `/domains` | No | List all 15 domains + 11 axioms |
| GET | `/docs` | No | Interactive Swagger UI |
| POST | `/v1/audit` | API key | Constitutional governance audit |
| POST | `/analyze` | API key | Multi-domain divergence analysis |
| POST | `/scan` | API key | Autonomous problem scanner |

## Pricing

| Tier | Price | Rate Limit | Depth |
|------|-------|------------|-------|
| Free | $0 | 50 calls/day | `quick` only |
| Pro | $29/mo | 2,000 calls/day | `quick` + `full` |
| Team | $99/mo | 10,000 calls/day | `quick` + `full` |

**Get your API key:** [elpida.lemonsqueezy.com](https://elpida.lemonsqueezy.com)

## What Happens Inside

1. **Kernel check** — 7 hard-coded rules that can never be overridden (K1-K7)
2. **10-node Parliament** — HERMES, MNEMOSYNE, CRITIAS, TECHNE, KAIROS, THEMIS, PROMETHEUS, IANUS, CHAOS, LOGOS — each scores through their axiom lens
3. **Contested escalation** — if approval is 10-70%, real LLM calls per node produce genuine deliberation
4. **Tension synthesis** — contradictions are surfaced, not hidden. Third-way resolutions generated.
5. **Transparency** — every veto, dissent, and sacrifice is returned in the response

## Source

- **GitHub:** [XOF-ops/python-elpida_core.py](https://github.com/XOF-ops/python-elpida_core.py)
- **Live Demo (UI):** [z65nik/elpida-governance-layer](https://huggingface.co/spaces/z65nik/elpida-governance-layer)
