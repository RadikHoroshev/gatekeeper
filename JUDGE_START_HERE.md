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

No secrets required. Expect unittest OK, `ALLOW_STATIC`, `PARK_INSTANT`, `BLOCKED_INFRA`, and offline routing benchmark.

## 5. Public links (tip SHA)

| Artifact | URL |
|---|---|
| Source | https://github.com/RadikHoroshev/gatekeeper |
| Public tip SHA | [`bcbbbc1`](https://github.com/RadikHoroshev/gatekeeper/commit/bcbbbc1b642e69a420d03c347202027bc5f58977) |
| Public tip CI (SUCCESS) | https://github.com/RadikHoroshev/gatekeeper/actions/runs/33744965150 |
| Live golden-path JSON (runtime plumbing) | [`evidence/live/20260903T075935Z/golden_path.json`](https://github.com/RadikHoroshev/gatekeeper/blob/bcbbbc1b642e69a420d03c347202027bc5f58977/evidence/live/20260903T075935Z/golden_path.json) |
| Live citation-relevance JSON (WebView) | `evidence/live/20260903T102852Z/golden_path.json` |
| Relevance review | `evidence/reviews/tavily-relevance-20260903.md` |
| Demo video (gates / `BLOCKED_INFRA` only) | https://youtu.be/_nyPil6cb_g |

**How to read the live JSON:** `20260903T075935Z` proves **runtime plumbing** (Tavily hits + Token Factory Nemotron). Its citations collided on the word “Gatekeeper” (AOSP/GKE) — **0/3** mechanism-relevant. `20260903T102852Z` is the **citation-relevance** run: package `android.webkit.WebView` / `addJavascriptInterface` — **3/3** supporting, including `developer.android.com` (no query rewrite).

## 6. Track recommendation

Prefer **Best Apps and Agents**. Personal AI (persistent memory + always-on) is **not demonstrated**. See `docs/TRACK_DECISION.md`. Devpost track updated under `GO_DEVPOST_UPDATE` to **Best apps and agents** (Save/re-submit update; Submit not newly clicked).

## 7. Honest limitation (video)

The published video shows `BLOCKED_INFRA` when keys are unset. It demonstrates fail-closed discipline, **not** a live Nemotron response on camera. Live Token Factory evidence is the JSON above.

## 8. Judging criteria map

| Criterion | Evidence |
|---|---|
| Nebius Token Factory / AI Cloud | live JSON provider=`nebius-token-factory`; `src/gatekeeper/nemotron.py` |
| NVIDIA Nemotron | model=`nvidia/nemotron-3-super-120b-a12b` in live JSON |
| Best Apps and Agents fit | refuse-first agent workflow + CI + live JSON |
| Personal AI | **not claimed** (memory/always-on missing) |
| Working test path | Actions run 33744965150 + `scripts/public_test.sh` |
| Best Use of Tavily ($3k) | functional call + **citation relevance PASS** on WebView fixture (`20260903T102852Z`, 3/3) |

## Next files

- `docs/JUDGING_EVIDENCE_MATRIX.md` — rubric status table
- `docs/TRACK_DECISION.md` — track choice for humans
- `docs/LIVE_EVIDENCE_RUNBOOK.md` — how live evidence was produced
- `fixtures/benchmark_cases.json` — offline routing metrics only
