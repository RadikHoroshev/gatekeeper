# Judging evidence matrix — Gatekeeper

**As of:** 2026-09-03 (post `GO_RUNTIME_PROOF`, pre-relevance run)  
**Public tip:** `92a491f`  
**CI:** https://github.com/RadikHoroshev/gatekeeper/actions/runs/33725567243 (**SUCCESS**)  
**Live smoke dir:** `evidence/live/20260903T070111Z/` (immutable)  
**Canonical video:** https://youtu.be/_nyPil6cb_g (gates / `BLOCKED_INFRA` — **not** live Nemotron)

Status legend: `CONFIRMED` | `PARTIAL` | `NOT_MEASURED` | `MISSING` | `OPEN`

| Rubric row | Exact claim | Local evidence | Public evidence | Live evidence | Status | Gap | Next action |
|---|---|---|---|---|---|---|---|
| Stage One viability / required runtime | Offline CI + live Nebius/Nemotron path | unittest, `public_test.sh`, routing 42 | CI on `92a491f` | Live smoke 2× exit 0 | `CONFIRMED` (plumbing) | Relevance / product demo still open | `GO_RUNTIME_PROOF_RELEVANCE` then demo |
| Nebius Token Factory runtime | Real Token Factory calls | `nemotron.py` | same on GitHub | provider=`nebius-token-factory`, request_id+usage present | `CONFIRMED` | — | keep |
| NVIDIA Nemotron runtime | `nvidia/nemotron-3-super-120b-a12b` | default model | public tip | model field on both live calls | `CONFIRMED` | — | keep |
| Repeatability | Two live runs same schema | — | — | golden + repeat | `CONFIRMED` | — | keep |
| Tavily functional runtime call | Search returns hits under `--tavily-mode required` | `tavily.py` | public tip | `tavily=grounded`, hits=3 ×2 | `CONFIRMED` | — | keep |
| Tavily citation relevance | Citations support declared mechanism | review `evidence/reviews/runtime-proof-20260903.md` | — | **0/3** relevant on smoke mechanism | `PARTIAL` / current run **FAIL** | Need public WebView case | `GO_RUNTIME_PROOF_RELEVANCE` |
| Best Use of Tavily | Quality grounding for the product story | fixture prepared | code only | smoke ≠ quality proof | `OPEN` | Pass relevance acceptance | after relevance GO |
| Technological Implementation | Token Factory + Nemotron + gates | code + CI + live | GitHub + CI | live smoke | `PARTIAL`→strong plumbing | Tavily quality OPEN | relevance + demo |
| Design | Coherent product experience | CLI + docs | video fail-closed | live JSON exists locally | `PARTIAL` | New terminal demo | `GO_DEMO_RECORD` |
| Potential Impact | Avoid wasted cloud calls | routing `cloud_calls_avoided=36` (synthetic) | concept | — | `PARTIAL` | Production token savings `NOT_MEASURED` | optional campaign telemetry |
| Quality of the Idea | Refusal-first bounty agent | docs | README | — | `CONFIRMED` (idea) | — | avoid overclaim |
| Model / vulnerability accuracy | Nemotron detects real vulns | — | — | — | `NOT_MEASURED` | never claim from smoke | — |
| Production token savings | Real hunt token reduction | — | — | — | `NOT_MEASURED` | — | — |
| Reproducibility | Exact SHA + CI + offline cmd | scripts | Actions `33725567243` | live dir local | `PARTIAL` | Evidence pack + live JSON not published | evidence commit GO after relevance |
| Submission compliance | Honest claims; no secrets | redaction tools | submitted portal state | secret_scan PASS | `PARTIAL` | Track + links update later | `GO_DEVPOST_UPDATE` |

## Explicit non-claims

- Current three smoke citations are **retrieved**, not mechanism-grounded evidence.
- Old video does **not** show live Nemotron.
- No guaranteed prize / Stage One outcome.
