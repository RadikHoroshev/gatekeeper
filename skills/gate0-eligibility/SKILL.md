---
name: gate0-eligibility
description: Check Google VRP payout eligibility (G0). Fail-closed on Russia/Belarus residency. Use before any Google hunt or Titan recon.
---

# gate0-eligibility

Before Google Devices/Mobile work:

1. Confirm operator is **not** resident in Russia or Belarus (Devices rules).
2. If unknown → **BLOCK** all Google $ lanes.
3. Israel and other non-excluded jurisdictions → **PASS**.

Do not infer residency from phone carrier or Gmail locale — ask the human once.

Output one line: `G0 PASS` or `G0 BLOCK: <reason>`.
