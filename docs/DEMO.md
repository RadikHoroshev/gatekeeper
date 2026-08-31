# Demo video script (≤3 minutes)

Public YouTube is a hard Devpost requirement. Record this flow; do not claim a live Token Factory call unless `scripts/smoke_nemotron.py` already printed PASS.

## Setup (off-camera)

```bash
cd gatekeeper
source .venv/bin/activate
export PYTHONPATH=src
# Optional live Nemotron:
# set -a && source .env && set +a
```

## On-camera (~2 min)

1. **Title card (5s)** — “Gatekeeper — Hermes + NVIDIA Nemotron on Nebius Token Factory”.
2. **Spray blocked (30s)** — run `bash scripts/demo_candidate.sh` and pause on the `com.google.android.gms` PARK JSON. Say: Instant PARK denylist, no LLM call.
3. **Named GO (30s)** — pause on `ALLOW_STATIC` for `com.example.fake.candidate` + `SEND-extra-to-privileged-persist`. Say: named mechanism is the only wake condition.
4. **Nemotron (40s)** — if `.env` has a key, show the TRIAGED JSON and name `nvidia/nemotron-3-super-120b-a12b` + Token Factory. If key is missing, show `BLOCKED_INFRA` and say smoke is the remaining infra step — do not fake a model reply.
5. **Close (15s)** — “Refusal is the feature. MIT. Personal AI track.”

## Upload

- YouTube: public, ≤3:00, no private/unlisted if Devpost cannot play it.
- Navy 3:2 placeholder: `docs/thumbnail.png` (1500×1000). Replace with a real title card before Devpost if you have time.
- Paste the watch URL into Devpost → Project details → Demo video.
- Do **not** click Devpost **Submit** unless the human says `go`.
