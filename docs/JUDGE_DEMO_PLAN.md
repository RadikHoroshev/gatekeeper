# Judge demo plan (90–120s) — do not record without separate GO

Prepared locally only. Existing public video (`_nyPil6cb_g`) shows fail-closed discipline; this plan is for a **new** live demo after keys are set in `gatekeeper/.env`.

## Setup (before camera)

```bash
cd gatekeeper
source .venv/bin/activate
export PYTHONPATH=src
# .env with NEBIUS_API_KEY (+ optional TAVILY_API_KEY), never shown on screen
```

## Scene 1 — Spray blocked (15s)

```bash
python3 -m gatekeeper.triage --package com.google.android.gms --mechanism ""
```

Show: `verdict=PARK`, `park_class=PARK_INSTANT`, `tavily=skipped`, `nemotron=skipped`, `network_calls=0`.

## Scene 2 — Named mechanism, static only (15s)

```bash
python3 -m gatekeeper.triage \
  --package com.example.fake.candidate \
  --mechanism SEND-extra-to-privileged-persist \
  --dry-run
```

Show: `ALLOW_STATIC`, both providers skipped.

## Scene 3 — Tavily grounding (20s)

```bash
python3 -m gatekeeper.triage \
  --package com.example.fake.candidate \
  --mechanism SEND-extra-to-privileged-persist \
  --tavily-only
```

Show: `TAVILY_GROUNDED`, `tavily_hits>=1`, citations with URLs (titles only on screen).

## Scene 4 — Nemotron structured verdict (30s)

```bash
python3 -m gatekeeper.triage \
  --package com.example.fake.candidate \
  --mechanism SEND-extra-to-privileged-persist \
  --static-notes "Synthetic judge demo; not a finding."
```

Show JSON: `verdict` ∈ {`ALLOW_PREFLIGHT`,`PARK`}, `usage`, `latency_ms`, `citations`, no secrets.

## Scene 5 — Summary slide (10s)

Display final JSON fields:

- `latency_ms.total`
- `usage.total_tokens` (if present)
- `tavily_hits`
- `verdict`

## Do not

- Click Devpost Submit
- Upload to YouTube without explicit GO
- Print `.env` or API keys
- Claim the old video shows live Nemotron PASS
