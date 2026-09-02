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

Public CI (no API keys): offline unit tests + static gates + `BLOCKED_INFRA` smoke.

## 4. One offline command

```bash
cd gatekeeper
bash scripts/public_test.sh
```

No secrets required. Expect unittest OK, `ALLOW_STATIC`, `PARK_INSTANT`, `BLOCKED_INFRA`, and offline benchmark `false_allow=0` / `false_park=0`.

## 5. Public links

| Artifact | URL |
|---|---|
| Source | https://github.com/RadikHoroshev/gatekeeper |
| Public test workflow (latest runs) | https://github.com/RadikHoroshev/gatekeeper/actions/workflows/public-test.yml |
| Unittest-in-CI run (`7781d17`) | https://github.com/RadikHoroshev/gatekeeper/actions/runs/33622587681 |
| Demo video (gates / `BLOCKED_INFRA`, not live Nemotron) | https://youtu.be/_nyPil6cb_g |

## 6. Honest limitation

The published video shows `BLOCKED_INFRA` when `NEBIUS_API_KEY` is unset. **Live Nemotron smoke PASS happened after recording** — public record: `evidence/nemotron-smoke.md`. The video demonstrates discipline, not a live model response on camera.

## 7. Judging criteria map

| Criterion | Evidence |
|---|---|
| Use of Nebius Token Factory / AI Cloud | `src/gatekeeper/nemotron.py`, `scripts/smoke_nemotron.py`, `evidence/nemotron-smoke.md` |
| NVIDIA open-source Nemotron | default model `nvidia/nemotron-3-super-120b-a12b` |
| Personal AI track fit | Hermes skills + gate discipline; memory/always-on out of scope for this slice |
| Working test path | GitHub Actions `public-test` + `scripts/public_test.sh` (no hosted endpoint) |
| Best Use of Tavily (optional $3k) | `src/gatekeeper/tavily.py`, `skills/tavily-ground`, fail-closed without key |

## Next files

- `evidence/runtime-proof.example.json` — structured result shape
- `fixtures/benchmark_cases.json` + `scripts/benchmark_offline.py` — offline metrics (`NOT_MEASURED` is not a percent)
- `docs/JUDGE_DEMO_PLAN.md` — 90–120s live demo script (not recorded here)
