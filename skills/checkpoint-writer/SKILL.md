---
name: checkpoint-writer
description: Write A2A CHECKPOINT after gate verdict. Sign with a2a-sign, lint with a2a-lint --strict, then STOP.
---

# checkpoint-writer

After gate or triage:

1. Write `CHECKPOINT_$(date -u +%Y%m%dT%H%M%SZ).md` with STEP_0..STEP_n lines.
2. Include `A2A_TRACE` with `finding=false` unless live proof exists.
3. Run `~/bounty/bin/a2a-sign` with `--verdict PASS|BLOCK|WARN`.
4. Run `~/bounty/bin/a2a-lint --strict` on checkpoint.
5. **STOP** — no second GO, no submit, no bind.

Hackathon checkpoints live under `gatekeeper/` or agent folder — do not mix with VRP submit bundles.
