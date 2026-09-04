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
| Audited tip SHA | [`52d2821`](https://github.com/RadikHoroshev/gatekeeper/commit/52d282158d894f89d3766a2658107d6416a66523) |
| Audited tip CI (SUCCESS) | https://github.com/RadikHoroshev/gatekeeper/actions/runs/33781188328 |
| Reviewer packet (FAIL + PASS proofs) | [`docs/REVIEWER_PACKET.md`](docs/REVIEWER_PACKET.md) |
| Collision FAIL JSON | [`evidence/live/20260903T075935Z/golden_path.json`](https://github.com/RadikHoroshev/gatekeeper/blob/52d282158d894f89d3766a2658107d6416a66523/evidence/live/20260903T075935Z/golden_path.json) |
| Relevance PASS JSON (WebView) | [`evidence/live/20260903T102852Z/golden_path.json`](https://github.com/RadikHoroshev/gatekeeper/blob/52d282158d894f89d3766a2658107d6416a66523/evidence/live/20260903T102852Z/golden_path.json) |
| Relevance review | `evidence/reviews/tavily-relevance-20260903.md` |
| Demo video (live 2026-09-04, Public) | https://youtu.be/WdnZCNe81LY |
| Archive fail-closed clip (not Devpost) | https://youtu.be/_nyPil6cb_g |

**How to read the live JSON:** `075935Z` / `070111Z` prove **runtime plumbing** and **document a real Tavily error**: citations collided on the word “Gatekeeper” (AOSP/GKE) — **0/3** mechanism-relevant. `102852Z` is the **citation-relevance** correction: `android.webkit.WebView` / `addJavascriptInterface` — **3/3** supporting, including `developer.android.com`. Full falsification table: `docs/REVIEWER_PACKET.md`.

## 6. Track recommendation

Prefer **Best Apps and Agents**. Personal AI (persistent memory + always-on) is **not demonstrated**. See `docs/TRACK_DECISION.md`. Devpost track updated under `GO_DEVPOST_UPDATE` to **Best apps and agents** (Save/re-submit update; Submit not newly clicked).

## 7. Honest limitation (video)

Canonical Devpost video is https://youtu.be/WdnZCNe81LY (1:18, Public, 2026-09-04): Instant PARK → named `ALLOW_STATIC` → live WebView `--tavily-mode required` with Tavily 3/3 (includes `developer.android.com`) and Nemotron Super 120B on Token Factory. On-camera live JSON is `finding=false` / `PARK` — a real model call, not a vuln. Archive `_nyPil6cb_g` remains fail-closed `BLOCKED_INFRA` only; do not treat it as the current embed.

## 8. Judging criteria map

| Criterion | Evidence |
|---|---|
| Nebius Token Factory / AI Cloud | live JSON provider=`nebius-token-factory`; `src/gatekeeper/nemotron.py` |
| NVIDIA Nemotron | model=`nvidia/nemotron-3-super-120b-a12b` in live JSON |
| Best Apps and Agents fit | refuse-first agent workflow + CI + live JSON |
| Personal AI | **not claimed** (memory/always-on missing) |
| Working test path | Actions run 33781188328 + `scripts/public_test.sh` |
| Best Use of Tavily ($3k) | functional call + **citation relevance PASS** on WebView fixture (`20260903T102852Z`, 3/3) |

## Next files

- `docs/REVIEWER_PACKET.md` — claim table, collision FAIL URLs, hash + request_id
- `docs/JUDGING_EVIDENCE_MATRIX.md` — rubric status table
- `docs/TRACK_DECISION.md` — track choice for humans
- `docs/LIVE_EVIDENCE_RUNBOOK.md` — how live evidence was produced
- `fixtures/benchmark_cases.json` — offline routing metrics only
