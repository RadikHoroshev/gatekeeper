# Live evidence runbook — Gatekeeper

**Live smoke status:** executed under `GO_RUNTIME_PROOF` → `evidence/live/20260903T070111Z/` (**immutable**).  
**Citation relevance:** current smoke **FAIL** (0/3). Supplemental run requires `GO_RUNTIME_PROOF_RELEVANCE`.  
**Do not** record/publish video without `GO_DEMO_RECORD` / `GO_DEMO_PUBLISH`.

## Frozen git facts

| Ref | SHA |
|---|---|
| HEAD / origin/main | `92a491f54a991952d932b0c14e987077be0f8913` |
| CI | https://github.com/RadikHoroshev/gatekeeper/actions/runs/33725567243 |

## Confirmed vs open

| Claim | Status |
|---|---|
| Nebius runtime | **CONFIRMED** |
| NVIDIA Nemotron runtime | **CONFIRMED** |
| Repeatability (2 calls) | **CONFIRMED** |
| Tavily functional runtime call | **CONFIRMED** |
| Tavily citation relevance (smoke) | **PARTIAL / FAIL** |
| Best Use of Tavily evidence | **OPEN** until relevance run passes |
| Model / vulnerability accuracy | **NOT_MEASURED** |
| Production token savings | **NOT_MEASURED** |

## Three evidence planes

### 1) Deterministic offline (no keys)

```bash
cd gatekeeper
source .venv/bin/activate
export PYTHONPATH=src
unset NEBIUS_API_KEY OPENAI_API_KEY TAVILY_API_KEY
.venv/bin/python3 -m unittest discover -s tests -v
bash scripts/public_test.sh
.venv/bin/python3 scripts/benchmark_offline.py
```

### 2) Integrated live smoke (completed; do not mutate)

Directory: `evidence/live/20260903T070111Z/`  
Files `golden_path.json`, `golden_path_repeat.json`, `*.exit`, `*.stderr`, original `release-manifest.json`, and `notes/runtime-proof-20260903.md` are **immutable**.

Independent review: `evidence/reviews/runtime-proof-20260903.md`.

Future manifests (new dirs only) must use corrected `scripts/build_evidence_manifest.py`:

- `command_argv` array;
- `runs[]` + `run_count`;
- `citation_relevance`;
- `evidence_sha256` excludes `release-manifest*.json`, `manifest_stdout.json`, `*.sha256`;
- sidecar `release-manifest.json.sha256` after final serialization;
- fail-closed on `.env` value leakage / auth patterns / malformed JSON.

### 3) Citation-relevance run (only after `GO_RUNTIME_PROOF_RELEVANCE`)

Prepared fixture: `fixtures/public_grounding_case.json`

```bash
# DO NOT RUN without GO_RUNTIME_PROOF_RELEVANCE
set -a; source .env; set +a
export PYTHONPATH=src
.venv/bin/python3 -m gatekeeper.triage \
  --package android.webkit.WebView \
  --mechanism "addJavascriptInterface with untrusted web content" \
  --static-notes "Public Android documentation case for citation-relevance evaluation only. Synthetic/public; not a vulnerability finding; not tied to any unpublished bounty target." \
  --tavily-mode required
```

Acceptance (from fixture): ≥2/3 citations discuss WebView/`addJavascriptInterface` security; ≥1 authoritative docs domain; ≥2 unique domains; reject generic Gatekeeper/Kubernetes pages.

Query builder note: current `ground_candidate` template is **plausible** for this case; no silent Tavily rewrite in the corrections task.

### 4) Practical impact (routing only)

Offline `cloud_calls_avoided` is a **routing** metric. Production token savings remain `NOT_MEASURED`.

## Redaction rules

- Never print `.env` values, Bearer headers, or API keys.
- On secret detection, report **filename + key name only**.

## Demo

New ≤2:30 terminal demo only after `GO_DEMO_RECORD`. Do not replace `_nyPil6cb_g` without GO.

## Next GOs

1. Independent review of this corrections pack  
2. `GO_RUNTIME_PROOF_RELEVANCE`  
3. Evidence pack commit/push (after relevance PASS)  
4. `GO_DEMO_RECORD` → `GO_DEMO_PUBLISH` → `GO_DEVPOST_UPDATE`
