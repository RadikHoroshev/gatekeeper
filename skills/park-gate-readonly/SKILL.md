---
name: park-gate-readonly
description: Read-only Instant PARK and do_not_repeat checks against ~/bounty KERNEL state. Never install APKs or run bind.
---

# park-gate-readonly

Read-only files:

- `~/bounty/state/android-park-queue/QUEUE_STATE.json`
- `~/bounty/research/_shared/ANDROID_INSTANT_PARK_PACKAGES.txt`
- `~/bounty/research/_shared/OPERATING_KERNEL.md`

Rules:

- `GO A1 next` / `GO GMS` without mechanism → **BLOCK**
- Package on denylist or `do_not_repeat` → **PARK_***
- `exhausted_idle` without A1 delta → **DRY_REPORT**, no deep audit
- `exported=true` alone → not a finding

Run `python3 -m gatekeeper.triage --dry-run` for structured JSON verdict.
