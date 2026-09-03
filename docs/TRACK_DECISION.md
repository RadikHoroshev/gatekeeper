# Track decision — Gatekeeper

**Prepared:** 2026-09-03
**Project:** Gatekeeper (`RadikHoroshev/gatekeeper`)
**Public tip:** [`bcbbbc1`](https://github.com/RadikHoroshev/gatekeeper/commit/bcbbbc1b642e69a420d03c347202027bc5f58977)
**CI:** https://github.com/RadikHoroshev/gatekeeper/actions/runs/33744965150 (**SUCCESS**)

Official track blurbs (Devpost rules):

- **Best Apps and Agents:** any app/agent someone would use; Nemotron on Nebius Token Factory; Serverless Endpoints/Jobs encouraged, not required.
- **Personal AI:** always-on private assistant; persistent memory; reusable skills; tools you choose; daily workflows; NVIDIA open-source model; NemoClaw / OpenShell / Hermes / Nebius Serverless as assembly options.

## A. Personal AI Track

| Dimension | Assessment |
|---|---|
| Fit to official description | **Weak.** Gatekeeper is a hunt-discipline gate + optional cloud triage, not an always-on personal assistant. |
| Features that exist | Reusable Hermes skills; local privacy boundary (gitignored `.env`, fail-closed without keys); CLI workflow. |
| Features only claimed / missing | Persistent memory across two independent runs — **not demonstrated**; background/periodic always-on — **not demonstrated**; NemoClaw/OpenShell — **not used**. |
| Required extra work | Persistent store + two-run demo; background loop; personal-assistant UX. High effort. |
| Stage One pass/fail risk | **High** under a strict Personal AI reading. |
| Recommendation | **Do not select** unless a separate GO builds persistent-state + background demos. |

## B. Best Apps and Agents Track

| Dimension | Assessment |
|---|---|
| Fit to official description | **Strong.** Operators can run: local refuse → optional Tavily → Nemotron on Token Factory. |
| Features that exist | CLI; Nemotron Super 120B via Token Factory; Tavily runtime call; offline CI; live golden-path JSON on tip `bcbbbc1`; routing benchmark. |
| Features only claimed / missing | Hosted Nebius Serverless Endpoint — **not required / not deployed**; new video of live JSON — needs `GO_DEMO_RECORD`. Tavily citation relevance — **PASS** on WebView fixture `20260903T102852Z`. |
| Required extra work | Optional new demo video (`GO_DEMO_RECORD`). Devpost Save done 2026-09-03. |
| Stage One pass/fail risk | **Lower** for Apps track if judges accept plumbing + CI + honest limits. |
| Recommendation | **Recommend Best Apps and Agents.** |

## Decision rule application

Personal AI needs demonstrated **persistent state between two runs**, **reusable skills**, **background/periodic workflow**, and **privacy boundary**.
Gatekeeper has reusable skills + privacy boundary, but **lacks** measured persistent state and background always-on → **recommend Best Apps and Agents**.

## Human action (not performed here)

- Devpost track field: updated 2026-09-03 under `GO_DEVPOST_UPDATE` → **Best apps and agents** (Save/re-submit; Submit not newly clicked).
- Working demo / test-build URL: Actions run `33745097096` (tip `78011f7`).
- Video remains `_nyPil6cb_g` (fail-closed); live Token Factory proof is tip JSON.
- This file remains advisory for humans; portal fields are source of truth after Save.
