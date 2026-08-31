# BUILD — go nebius-build checklist

**Track:** Personal AI · **Deadline:** 30 Oct 2026 10:00 PDT  
**Project:** Gatekeeper (Hermes + Nemotron + KERNEL gates)

## §1 Nebius Token Factory (required for smoke)

1. Open https://nebiusglobalaihackathon.devpost.com/ → **Join Hackathon** (Devpost account).
2. Join **Nebius Builder Program** from hackathon page (credits for Token Factory + Tavily).
3. https://tokenfactory.nebius.com → **API keys** → Create → save `NEBIUS_API_KEY`.
4. Local:
   ```bash
   cd gatekeeper
   cp .env.example .env
   # paste key into .env
   source .env
   pip install -r requirements.txt
   python3 scripts/smoke_nemotron.py   # expect PASS
   ```

## §2 Hermes → Nemotron provider

Provider `nebius-token-factory` is already merged into `~/.hermes/config.yaml`. Default remains `custom:ollama-launch` / ornith — do not switch it.

To use Nemotron for a triage session only: `hermes model` → select `nebius-token-factory` / `nvidia/nemotron-3-super-120b-a12b` (needs `NEBIUS_API_KEY` in the environment).

Snippet reference: `config/hermes-nebius-snippet.yaml`

## §3 Skills (Week 2)

`hermes skills install` wants a registry URL. Local install is a symlink:

```bash
cd gatekeeper
ln -sfn "$(pwd)/skills/gate0-eligibility" ~/.hermes/skills/gate0-eligibility
ln -sfn "$(pwd)/skills/park-gate-readonly" ~/.hermes/skills/park-gate-readonly
ln -sfn "$(pwd)/skills/checkpoint-writer" ~/.hermes/skills/checkpoint-writer
hermes skills list | rg 'gate0-eligibility|park-gate-readonly|checkpoint-writer'
```

## §4 Demo + submit (Week 3–5)

- [ ] Public GitHub repo with MIT license visible in About (`RadikHoroshev/gatekeeper`)
- [x] README highlights Nemotron + Token Factory usage
- [ ] Record ≤3 min YouTube demo: spray blocked → named GO → Nemotron triage (`docs/DEMO.md`)
- [ ] Working demo URL (optional: `hermes serve` or static dashboard)
- [x] Devpost **draft** 1163649: track Personal AI, city Tel Aviv — **Submit not clicked**
- [x] Feedback paragraph on Nebius + NVIDIA tools (honest: smoke not run)

## §5 Current build status (2026-08-31)

| Step | Status |
|---|---|
| Gatekeeper code scaffold | **DONE** |
| Static gate dry-run | **DONE** (no API key) |
| Portable Instant PARK fixture | **DONE** (`fixtures/instant_park_demo.txt`) |
| Hermes provider `nebius-token-factory` | **DONE** (default model still ollama-launch/ornith) |
| Nemotron smoke | **BLOCKED_INFRA** — `NEBIUS_API_KEY` unset (no TF login on this host) |
| Devpost join + draft | **DONE** — submission 1163649; Submit blocked until GitHub + YouTube |
| Public GitHub repo | **IN_PROGRESS** this session |
| Demo video | **PENDING** — see `docs/DEMO.md` |

## Human / other-machine only

- Token Factory login + API key → `.env` (see `.env.example`)
- YouTube upload (`docs/DEMO.md`)
- Devpost remaining checkboxes + **Submit** only after explicit human `go`
- Do not put a Devpost JWT in `.env`
