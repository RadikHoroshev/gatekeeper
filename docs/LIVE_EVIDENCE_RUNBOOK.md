# Live evidence runbook — Gatekeeper

**Runtime smoke:** `evidence/live/20260903T075935Z/` — citation relevance **FAIL** (0/3 name collision).
**First live pair (in git):** `evidence/live/20260903T070111Z/` — same collision class **FAIL**.
**Citation-relevance live (`GO_TAVILY_RELEVANCE`):** `evidence/live/20260903T102852Z/` — **PASS** (3/3 WebView / `addJavascriptInterface`).
**Reviewer packet:** `docs/REVIEWER_PACKET.md`
**Review:** `evidence/reviews/tavily-relevance-20260903.md`
**Do not** record/publish video without `GO_DEMO_RECORD` / `GO_DEMO_PUBLISH`.

## Frozen git facts (audit snapshot)

| Ref | Value |
|---|---|
| HEAD / origin/main | `52d282158d894f89d3766a2658107d6416a66523` |
| CI | https://github.com/RadikHoroshev/gatekeeper/actions/runs/33781188328 |

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

`evidence/live/20260903T070111Z/` is in git as the first collision-FAIL pair (commit `52d2821`). Treat as **error evidence**, not Tavily quality.

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

- Live demo recorded and published 2026-09-04: https://youtu.be/WdnZCNe81LY (Public, 1:18).
- Devpost `GO_DEVPOST_VIDEO` project v17: video field only. Track **Best apps and agents**; Tavily=Yes. **Do not click Submit** (`submitted_at` 2026-09-01).

## Next GOs

1. No Submit click
2. Optional: keep GitHub docs in sync with Devpost video (this pin)
