---
name: tavily-ground
description: After ALLOW, optionally ground a named hypothesis with one Tavily Search call. Never spray. Fail-closed without TAVILY_API_KEY.
---

# tavily-ground

Use Tavily only after static gates return ALLOW for a named mechanism.

- No key → skip (`tavily=skipped`) or `scripts/smoke_tavily.py` prints `BLOCKED_INFRA`.
- Public GitHub Actions `public-test` must not set `TAVILY_API_KEY`.
- Do not call Tavily on Instant PARK / spray paths.

```bash
export PYTHONPATH=src
python3 scripts/smoke_tavily.py
python3 -m gatekeeper.triage --package com.example.fake.candidate \
  --mechanism SEND-extra-to-privileged-persist --tavily-only
```
