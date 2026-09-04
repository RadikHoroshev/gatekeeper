# Demo video script (≤3 minutes)

Canonical public URL (`GO_DEMO_PUBLISH` 2026-09-04, Devpost embed): https://youtu.be/WdnZCNe81LY  
Archive fail-closed working demo — do not restore to Devpost: https://youtu.be/_nyPil6cb_g  
Archive slideshow — do not restore to Devpost: https://youtu.be/HSIBGo0bEQc

Public YouTube is a hard Devpost requirement. The live 1:18 clip shows Instant PARK → named `ALLOW_STATIC` → WebView `--tavily-mode required` with Tavily 3/3 and Nemotron Super 120B on Token Factory. `_nyPil6cb_g` is fail-closed `BLOCKED_INFRA` only.

## Setup (off-camera)

```bash
cd gatekeeper
source .venv/bin/activate
export PYTHONPATH=src
# Optional live Nemotron:
# set -a && source .env && set +a
```

## On-camera (live 1:18, 2026-09-04)

1. **Title** — Gatekeeper live demo; Best Apps and Agents.
2. **Spray blocked** — Instant PARK (`provider` null); no LLM.
3. **Named GO** — `ALLOW_STATIC` for a named mechanism.
4. **Live WebView required-mode** — Tavily grounded 3/3 including `developer.android.com`; `provider=nebius-token-factory`; `nvidia/nemotron-3-super-120b-a12b`. On-camera JSON is `finding=false` / `PARK`.
5. **Close** — Refusal is the feature. MIT.

## Upload

- YouTube Public 2026-09-04: https://youtu.be/WdnZCNe81LY (`isUnlisted=false`).
- Devpost video field updated (`GO_DEVPOST_VIDEO`, project v17). Do **not** click Submit (already Submitted 2026-09-01).
