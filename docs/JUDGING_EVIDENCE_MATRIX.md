# Judging evidence matrix — Gatekeeper

**As of:** 2026-09-03 (Phase B Tavily relevance)
**Public tip:** [`bcbbbc1`](https://github.com/RadikHoroshev/gatekeeper/commit/bcbbbc1b642e69a420d03c347202027bc5f58977)
**CI:** https://github.com/RadikHoroshev/gatekeeper/actions/runs/33744965150 (**SUCCESS**)
**Runtime smoke:** `evidence/live/20260903T075935Z/`
**Citation-relevance live:** `evidence/live/20260903T102852Z/`
**Canonical video:** https://youtu.be/_nyPil6cb_g (gates / `BLOCKED_INFRA` — **not** live Nemotron)

Status legend: `CONFIRMED` | `PARTIAL` | `NOT_MEASURED` | `MISSING` | `OPEN`

| Rubric row | Exact claim | Local evidence | Public evidence | Live evidence | Status | Gap | Next action |
|---|---|---|---|---|---|---|---|
| Stage One viability / required runtime | Offline CI + live Nebius/Nemotron path | unittest, `public_test.sh`, routing 42 | tip + CI | golden_path JSON | `CONFIRMED` (plumbing) | Video still fail-closed | `GO_DEMO_RECORD` |
| Nebius Token Factory runtime | Real Token Factory calls | `nemotron.py` | tip | provider=`nebius-token-factory`, usage+request_id | `CONFIRMED` | — | keep |
| NVIDIA Nemotron runtime | Super 120B | default model | tip | model in live JSON | `CONFIRMED` | — | keep |
| Repeatability | Two live runs | — | tip (golden + repeat) | both exit 0 (smoke + relevance) | `CONFIRMED` | — | keep |
| Tavily functional runtime call | Search returns hits | `tavily.py` | tip | `tavily=grounded` hits=3 | `CONFIRMED` | — | keep |
| Tavily citation relevance | Citations support declared Android mechanism | review `tavily-relevance-20260903.md` | WebView live dir | **3/3** relevant (PASS) | `CONFIRMED` | Smoke `075935Z` still 0/3 (name collision) | keep both labeled |
| Best Use of Tavily ($3k) | Quality grounding | fixture EXECUTED_PASS | code + WebView citations | relevance JSON + review | `CONFIRMED` for fixture | Demo not yet filmed | `GO_DEMO_RECORD` |
| Technological Implementation | Token Factory + Nemotron + gates | code + CI + live | GitHub | live JSON | `CONFIRMED` plumbing + Tavily quality | Demo | `GO_DEMO_RECORD` |
| Design | Coherent product | CLI + docs | video fail-closed | live JSON public | `PARTIAL` | New terminal demo | `GO_DEMO_RECORD` |
| Potential Impact | Avoid wasted cloud calls | routing `cloud_calls_avoided=36` (synthetic) | concept | — | `PARTIAL` | Production tokens `NOT_MEASURED` | optional |
| Quality of the Idea | Refusal-first bounty agent | docs | README | — | `CONFIRMED` (idea) | — | avoid overclaim |
| Model / vulnerability accuracy | Nemotron detects real vulns | — | — | — | `NOT_MEASURED` | never claim from smoke | — |
| Production token savings | Real hunt token reduction | — | — | — | `NOT_MEASURED` | — | — |
| Reproducibility | Exact SHA + CI + offline cmd | scripts | Actions + live paths | tip | `CONFIRMED` | tip pinned post Phase B | keep docs honest |
| Submission compliance | Honest claims; no secrets | redaction tools | submitted portal; Submit disabled | secret_scan PASS | `PARTIAL` | Track + link refresh | `GO_DEVPOST_UPDATE` |

## Explicit non-claims

- Smoke `075935Z` citations are **retrieved**, not mechanism-grounded; use `102852Z` for Best Use of Tavily quality.
- Old video does **not** show live Nemotron.
- No guaranteed prize / Stage One outcome.
