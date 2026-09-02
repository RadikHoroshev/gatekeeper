# Gatekeeper — start here (60 seconds)

## 1. Real problem

Bug-bounty and mobile-security hunts waste expensive model calls on spray commands, exhausted queues, and Instant-PARK packages. Gatekeeper refuses first, locally, with explicit GO/PARK discipline.

## 2. Why refusal is the feature

`GO A1 next` spray and unnamed mechanisms are blocked before any Tavily or Nemotron call. A named mechanism is the only path to optional grounding and triage. **Fail-closed is intentional.**

## 3. Architecture

```
local gates (gates.py)
    → optional Tavily grounding (tavily.py)
    → optional Nemotron triage (nemotron.py, Nebius Token Factory)
```

Public CI runs only static gates + `BLOCKED_INFRA` smoke (no API keys).

## 4. One offline command

```bash
cd gatekeeper
bash scripts/public_test.sh
```

No secrets required. Expect `ALLOW_STATIC`, `PARK_INSTANT`, and `BLOCKED_INFRA`.

## 5. Public links

| Artifact | URL |
|---|---|
| Source | https://github.com/RadikHoroshev/gatekeeper |
| Public test workflow | https://github.com/RadikHoroshev/gatekeeper/actions/workflows/public-test.yml |
| Latest public test run | https://github.com/RadikHoroshev/gatekeeper/actions/runs/33506576738 |
| Demo video (honest fail-closed) | https://youtu.be/_nyPil6cb_g |

## 6. Honest limitation

The published video shows `BLOCKED_INFRA` when `NEBIUS_API_KEY` is unset. **Live Nemotron smoke PASS happened after recording** (documented in `notes/smoke-nemotron-20260902.md`). The video demonstrates discipline, not a live model response on camera.

## 7. Judging criteria map

| Criterion | Evidence |
|---|---|
| Use of Nebius Token Factory / AI Cloud | `src/gatekeeper/nemotron.py`, `scripts/smoke_nemotron.py` |
| NVIDIA open-source Nemotron | default model `nvidia/nemotron-3-super-120b-a12b` |
| Personal AI track fit | Hermes skills + gate discipline; memory/always-on out of scope for this slice |
| Working test path | GitHub Actions `public-test` + `scripts/public_test.sh` (no hosted endpoint) |
| Best Use of Tavily (optional $3k) | `src/gatekeeper/tavily.py`, `skills/tavily-ground`, fail-closed without key |

## Next files

- `evidence/runtime-proof.example.json` — structured result shape
- `fixtures/benchmark_cases.json` + `scripts/benchmark_offline.py` — offline metrics
- `docs/JUDGE_DEMO_PLAN.md` — 90–120s live demo script (not recorded here)
