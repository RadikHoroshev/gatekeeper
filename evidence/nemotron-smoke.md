# Live Nemotron smoke (after the public video)

The YouTube demo (`https://youtu.be/_nyPil6cb_g`) shows fail-closed `BLOCKED_INFRA` with no API key. A later local smoke against Nebius Token Factory passed.

| Field | Value |
|---|---|
| Date | 2026-09-02 |
| Script | `scripts/smoke_nemotron.py` |
| Model | `nvidia/nemotron-3-super-120b-a12b` |
| Observed | exact match `Gatekeeper smoke OK`, exit 0 |
| Secrets | `NEBIUS_API_KEY` only in gitignored `.env` (mode 600); not logged, not in CI |

This file is the public record. Do not treat the video as a live model PASS.
