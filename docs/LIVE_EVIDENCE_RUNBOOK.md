# Live evidence runbook — Gatekeeper

**Runtime smoke (immutable path; still in tip):** `evidence/live/20260903T075935Z/` — citation relevance **FAIL** (0/3 name collision).
**Citation-relevance live (`GO_TAVILY_RELEVANCE`):** `evidence/live/20260903T102852Z/` — **PASS** (3/3 WebView / `addJavascriptInterface`).
**Review:** `evidence/reviews/tavily-relevance-20260903.md`
**Do not** record/publish video without `GO_DEMO_RECORD` / `GO_DEMO_PUBLISH`.

## Frozen git facts

| Ref | Value |
|---|---|
| HEAD / origin/main | `bcbbbc1b642e69a420d03c347202027bc5f58977` |
| CI | https://github.com/RadikHoroshev/gatekeeper/actions/runs/33744965150 |

## Confirmed vs open

| Claim | Status |
|---|---|
| Nebius runtime | **CONFIRMED** |
| NVIDIA Nemotron runtime | **CONFIRMED** |
| Repeatability (2 calls) | **CONFIRMED** |
| Tavily functional runtime call | **CONFIRMED** |
| Tavily citation relevance (WebView fixture) | **CONFIRMED** (3/3) |
| Best Use of Tavily evidence | **CONFIRMED** for published fixture run |
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

### 2) Published live smoke (immutable runtime proof)

Directory: `evidence/live/20260903T075935Z/`
Treat as **runtime / fail-closed proof**, not Tavily quality.

Older local leftover `evidence/live/20260903T070111Z/` is **not** for commit.

Independent review of citation fail: `evidence/reviews/runtime-proof-20260903.md`.

Manifest tool: `scripts/build_evidence_manifest.py` (sidecar `.sha256`; excludes manifest files from `evidence_sha256`).

### 3) Citation-relevance run (executed under `GO_TAVILY_RELEVANCE`)

Fixture: `fixtures/public_grounding_case.json` (`EXECUTED_PASS`)
Package has **no** `gatekeeper` substring.

```bash
set -a; source .env; set +a
export PYTHONPATH=src
.venv/bin/python3 -m gatekeeper.triage \
  --package android.webkit.WebView \
  --mechanism "addJavascriptInterface with untrusted web content" \
  --static-notes "Public Android documentation case for citation-relevance evaluation only. Synthetic/public; not a vulnerability finding." \
  --tavily-mode required
```

Acceptance met: 3/3 citations discuss WebView/`addJavascriptInterface` security; includes `developer.android.com`; 3 unique domains; no Gatekeeper/Kubernetes collision. Query builder **unchanged**.

### 4) Practical impact (routing only)

Offline `cloud_calls_avoided` is a **routing** metric. Production token savings remain `NOT_MEASURED`.

## Redaction rules

- Never print `.env` values, Bearer headers, or API keys.
- On secret detection, report **filename + key name only**.

## Demo / Devpost

- New ≤3 min terminal demo only after `GO_DEMO_RECORD` (show live JSON, not only `BLOCKED_INFRA`).
- Devpost updated 2026-09-03 under `GO_DEVPOST_UPDATE`: track **Best apps and agents**, tip CI `33745097096`, Tavily=Yes, video `_nyPil6cb_g`. **Do not click Submit** (already submitted).

## Next GOs

1. `GO_DEMO_RECORD` → `GO_DEMO_PUBLISH` (optional but strengthens Design)
2. No Submit click
