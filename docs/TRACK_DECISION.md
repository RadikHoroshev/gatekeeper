# Track decision — Gatekeeper (human decision only; do not change Devpost)

**Prepared:** 2026-09-03  
**Project:** Gatekeeper (`RadikHoroshev/gatekeeper`)  
**Frozen SHAs:** local `92a491f` (ahead); public `origin/main` = `1463bc2` until `GO_PUSH_92A`

Official track blurbs (Devpost rules):

- **Best Apps and Agents:** any app/agent someone would use; Nemotron on Nebius Token Factory; Serverless Endpoints/Jobs encouraged, not required.
- **Personal AI:** always-on private assistant; persistent memory; reusable skills; tools you choose; daily workflows; NVIDIA open-source model; NemoClaw / OpenShell / Hermes / Nebius Serverless as assembly options.

## A. Personal AI Track

| Dimension | Assessment |
|---|---|
| Fit to official description | **Weak.** Gatekeeper is a hunt-discipline gate + optional cloud triage, not an always-on personal assistant. |
| Features that exist | Reusable Hermes skills (`gate0`, `park-gate`, `checkpoint-writer`, `tavily-ground`); local privacy boundary (secrets in gitignored `.env`, fail-closed without keys); CLI workflow. |
| Features only claimed / missing | Persistent memory across two independent runs — **not demonstrated**; background/periodic always-on agent — **not demonstrated**; NemoClaw/OpenShell personal runtime — **not used**; “works for you across daily workflows” beyond bounty CLI — **not shown**. |
| Required extra work | Persistent store + two-run demo; background loop or scheduler; clearer personal-assistant UX. High effort before Stage One narrative matches the track. |
| Stage One pass/fail risk | **High** if judged strictly as Personal AI (missing always-on + memory proof). |
| Recommendation | **Do not select** unless a separate GO builds and records persistent-state + background demos. |

## B. Best Apps and Agents Track

| Dimension | Assessment |
|---|---|
| Fit to official description | **Strong.** Gatekeeper is an agent workflow operators can run: local refuse → optional Tavily → Nemotron triage on Token Factory. |
| Features that exist | Working CLI; Nemotron Super 120B via Token Factory; Tavily grounding path; offline CI (`public_test.sh`); structured JSON outcomes; routing that avoids unnecessary cloud calls. |
| Features only claimed / missing | Hosted Nebius Serverless Endpoint — **not required**, also **not deployed**; new live demo video of golden Tavily+Nemotron path — **prepared, not recorded** (needs `GO_DEMO_RECORD`); live end-to-end public proof on SHA `92a491f` — **needs `GO_PUSH_92A` + `GO_RUNTIME_PROOF`**. |
| Required extra work | Push R3–R6 SHA; bounded live proof; optional new demo video; keep claims within measured evidence. |
| Stage One pass/fail risk | **Lower** if Stage One needs a working Nebius/Nemotron path: code + CI + prior local smoke exist; remaining gap is public SHA sync + honest live demo. |
| Recommendation | **Recommend Best Apps and Agents.** |

## Decision rule application

Personal AI requires demonstrated **persistent state between two runs**, **reusable skills**, **background/periodic workflow**, and **privacy boundary**.  
Gatekeeper has reusable skills + privacy boundary, but **lacks** measured persistent state and background always-on proof → **recommend Best Apps and Agents**.

## Human action (not performed here)

- Devpost track field: leave unchanged until `GO_DEVPOST_UPDATE`.
- This file is advisory only — no portal Save/Submit.
