# Gatekeeper

Personal AI hunt-discipline assistant — **Nebius × NVIDIA Global AI Hackathon** (Personal AI track).

Refusal is the feature: static GO/PARK gates run locally. **NVIDIA Nemotron** (`nvidia/nemotron-3-super-120b-a12b`) on **[Nebius Token Factory](https://tokenfactory.nebius.com)** wakes only for a named mechanism or a `CANDIDATE_*` event — never for `GO A1 next` spray.

This slice is MIT-licensed: https://github.com/RadikHoroshev/gatekeeper

[![public-test](https://github.com/RadikHoroshev/gatekeeper/actions/workflows/public-test.yml/badge.svg)](https://github.com/RadikHoroshev/gatekeeper/actions/workflows/public-test.yml)

**Public test build (no secrets):** https://github.com/RadikHoroshev/gatekeeper/actions/workflows/public-test.yml — static `ALLOW_STATIC` + Instant `PARK` + fail-closed `BLOCKED_INFRA`. It does not call Nebius Token Factory and does not use `NEBIUS_API_KEY`.

Token Factory is the required runtime; Hermes stays on a local default model until an explicit triage session.

## Nebius Token Factory + NVIDIA Nemotron

| Piece | Value |
|---|---|
| Runtime | [Nebius Token Factory](https://tokenfactory.nebius.com) OpenAI-compatible API |
| Base URL | `https://api.tokenfactory.nebius.com/v1/` |
| Model | `nvidia/nemotron-3-super-120b-a12b` (NVIDIA OSS) |
| Smoke | `scripts/smoke_nemotron.py` — PASS only with `NEBIUS_API_KEY` |
| Call path | `src/gatekeeper/nemotron.py` after `gates.py` returns `ALLOW` |

Copy `.env.example` → `.env` on a machine where you created the Token Factory key. Do not commit `.env`.

## Requirements

- Python 3.11+
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) v0.19+ (named in hackathon rules)
- Nebius Token Factory API key + Builder Program credits
- Optional: a local KERNEL tree at `~/bounty` (read-only). The public demo uses `fixtures/instant_park_demo.txt` without it.

## Quick start

```bash
cd gatekeeper
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add NEBIUS_API_KEY

# Static gates only (no API key needed)
export PYTHONPATH=src
python3 -m gatekeeper.triage \
  --package com.example.app \
  --mechanism "SEND-extra-to-persist" \
  --dry-run

# Nemotron smoke (needs NEBIUS_API_KEY)
python3 scripts/smoke_nemotron.py

# Full demo script
bash scripts/demo_candidate.sh

# Public no-secret test build (same checks as GitHub Actions)
bash scripts/public_test.sh
```

## Hermes integration

Provider `nebius-token-factory` can be merged into `~/.hermes/config.yaml` (see `config/hermes-nebius-snippet.yaml`). Keep your daily default model local. Point only triage sessions at Nemotron.

Skills ship under `skills/` (read-only gate helpers). Copy or symlink them into `~/.hermes/skills/` — `hermes skills install` expects a registry URL, not a local folder.

See `BUILD.md` for Devpost registration and Builder Program.

## Hackathon compliance

| Requirement | How |
|---|---|
| Nebius Token Factory runtime | `scripts/smoke_nemotron.py`, `gatekeeper.nemotron` |
| NVIDIA OSS model (Nemotron) | `nvidia/nemotron-3-super-120b-a12b` default |
| Personal AI track | Hermes Agent + memory/skills + gate discipline |
| Public repo + OSS license | MIT — https://github.com/RadikHoroshev/gatekeeper |
| Public test build | GitHub Actions `public-test` — `scripts/public_test.sh` (no API key) |
| Demo video ≤3 min | https://youtu.be/_nyPil6cb_g (`scripts/demo_candidate.sh` flow) |

## Architecture

```
cron / user GO
      │
      ▼
┌─────────────┐     PARK/BLOCK     ┌──────────────┐
│ gates.py    │ ─────────────────► │ CHECKPOINT   │
│ (local,     │                    │ (no Nemotron)│
│  no LLM)    │                    └──────────────┘
└──────┬──────┘
       │ ALLOW + named mechanism
       ▼
┌─────────────┐
│ Nemotron    │  Nebius Token Factory API
│ triage      │
└─────────────┘
```

## Not in scope

- VRP submit, Pixel bind, Devpost auto-register (human steps in BUILD.md)
- Meta Hermes JS engine
- Nightly park-gate spray (KERNEL forbids)

## License

MIT — see LICENSE.
