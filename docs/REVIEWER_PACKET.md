# Reviewer packet — Gatekeeper (distrustful check)

**Audit ts:** 2026-09-03T16:55Z
**Repo:** https://github.com/RadikHoroshev/gatekeeper
**Audited tip:** [`52d2821`](https://github.com/RadikHoroshev/gatekeeper/commit/52d282158d894f89d3766a2658107d6416a66523)
**Audited CI:** https://github.com/RadikHoroshev/gatekeeper/actions/runs/33781188328 (**SUCCESS**, `public-test`)
**Devpost:** https://devpost.com/software/gatekeeper-g24e7o (submission **1163649**, status Submitted)
**Track on portal:** Best apps and agents
**Video:** https://youtu.be/_nyPil6cb_g — **fail-closed only** (`BLOCKED_INFRA`)

This file exists so a reviewer does not have to reverse-engineer three live directories. Every row below is a **claim + how to falsify it**.

## 0. What is proven vs what is not

| Claim | Verdict | Why a reviewer should believe it |
|---|---|---|
| Offline gates work without keys | **CONFIRMED** | CI `public-test` SUCCESS on tip; `scripts/public_test.sh` |
| Nebius Token Factory + Nemotron Super 120B ran | **CONFIRMED** | live JSON `provider` + `model` + `usage` + `request_id` |
| Tavily API returned hits | **CONFIRMED** | `tavily=grounded` hits=3 in all three live dirs |
| Tavily citations can be **wrong** (name collision) | **CONFIRMED FAIL** | `070111Z` and `075935Z` URLs are AOSP/GKE “Gatekeeper”, not the synthetic Android mechanism |
| Tavily citations can be **right** for a named mechanism | **CONFIRMED PASS** | `102852Z` WebView / `addJavascriptInterface`, 3/3, includes `developer.android.com` |
| Video shows live Nemotron | **FALSE** | oEmbed title is working demo; content is fail-closed. Do not treat as Token Factory camera proof |
| Nemotron finds real vulns | **NOT_MEASURED** | synthetic `finding=false` / `PARK` only |
| Production token savings | **NOT_MEASURED** | offline routing metric only |
| Personal AI (memory / always-on) | **NOT CLAIMED** | track is Best apps and agents |

## 1. How to reproduce the offline plane (no secrets)

```bash
git clone https://github.com/RadikHoroshev/gatekeeper.git
cd gatekeeper
git rev-parse HEAD   # expect 52d2821… or a later docs-only tip
bash scripts/public_test.sh
```

Expect: unittest OK, `ALLOW_STATIC`, `PARK_INSTANT`, `BLOCKED_INFRA`, offline routing benchmark. CI transcript: run **33781188328**.

## 2. Live evidence map (three directories, two stories)

| Dir | Role | Package (no secrets) | Citation verdict | SHA256(`golden_path.json`) | `request_id` |
|---|---|---|---|---|---|
| `evidence/live/20260903T070111Z/` | first live pair (now in git) | `com.example.synthetic.gatekeeper.demo` | **FAIL 0/3** name collision | `7f10fe4666b01b0cf6cf096e9fa03bb1ee6dd5e74bc8223468cfc0f0ed97bd08` | `chatcmpl-183cb34af09e499ba875f3f45a150e99` |
| `evidence/live/20260903T075935Z/` | published runtime smoke | same synthetic `gatekeeper.demo` | **FAIL 0/3** name collision | `536fadb114282a0260d661c3ba284f69cabeaaa61d1b6ccfe409b2fc9410ca10` | `chatcmpl-7014068622da45ad9aae524b88d1a382` |
| `evidence/live/20260903T102852Z/` | citation-relevance | `android.webkit.WebView` | **PASS 3/3** | `e0289b23da176b1de81de196c6aa39fea58bbba65f5180e7eb313ecad7215f7e` | `chatcmpl-26ec586deabb43aebcc76c5b002ba9ce` |

Hash check (must match bytes on disk / GitHub):

```bash
shasum -a 256 evidence/live/20260903T102852Z/golden_path.json
# e0289b23da176b1de81de196c6aa39fea58bbba65f5180e7eb313ecad7215f7e
```

Manifests for `075935Z` and `102852Z` include `evidence_sha256` + sidecar `.sha256`. Audit 2026-09-03: **all listed hashes matched file bytes**.

## 3. Confirmed error: Tavily name collision (do not hide)

**Input that caused the error:** package substring `gatekeeper` + synthetic mechanism `SEND-extra-to-privileged-persist`.

**Retrieved URLs (identical pattern on `070111Z` and `075935Z`):**

| # | URL | Why it is a FAIL |
|---|---|---|
| 1 | https://source.android.com/docs/security/features/authentication/gatekeeper | AOSP Gatekeeper HAL — name collision, not Intent/extra persist |
| 2 | https://docs.cloud.google.com/kubernetes-engine/docs/how-to/pod-security-policies-with-gatekeeper | GKE / OPA Gatekeeper — Kubernetes, not Android hunt mechanism |
| 3 | https://blog.google/security/whats-new-in-android-security-privacy-2026 (`075935Z`) or https://zimperium.com/blog (`070111Z`) | generic / not the named mechanism |

`tavily=grounded` is **true** (HTTP search worked). Mechanism grounding is **false**. Review: `evidence/reviews/runtime-proof-20260903.md`. Manifest `075935Z`: `citation_relevance=FAILED_MANUAL_REVIEW`.

This FAIL is the factual basis for not treating the first smoke as Best Use of Tavily quality.

## 4. Confirmed correction: WebView relevance PASS

**Input:** `--package android.webkit.WebView --mechanism "addJavascriptInterface with untrusted web content" --tavily-mode required`
**Query builder:** unchanged `{package} {mechanism} android security named hypothesis` (no rewrite).

**Retrieved URLs (golden + repeat identical):**

| # | URL | Why it is a PASS |
|---|---|---|
| 1 | https://ptkd.com/journal/android-webview-javascriptinterface-security | WebView + addJavascriptInterface risks |
| 2 | https://developer.android.com/privacy-and-security/risks/insecure-webview-native-bridges | authoritative Android docs, native bridges |
| 3 | https://stackoverflow.com/questions/6415882/android-javascriptinterface-security | JavascriptInterface + untrusted HTML |

Acceptance: ≥2/3 supporting, ≥1 docs domain, ≥2 unique domains, no Gatekeeper/K8s — **met (3/3)**.
Review: `evidence/reviews/tavily-relevance-20260903.md`. Manifest: `citation_relevance=PASSED_MANUAL_REVIEW`, `artifact_type=citation_relevance`.

Both runs: `provider=nebius-token-factory`, `model=nvidia/nemotron-3-super-120b-a12b`, `verdict=PARK`, `finding=false` (synthetic non-finding — correct). Distinct `request_id`s prove two Token Factory calls (`…26ec586d…` vs `…7e65c795…`).

## 5. Token Factory fields a reviewer can grep

From `evidence/live/20260903T102852Z/golden_path.json`:

- `provider`: `nebius-token-factory`
- `model`: `nvidia/nemotron-3-super-120b-a12b`
- `usage.total_tokens`: `1502`
- `nemotron`: `completed`
- `tavily`: `grounded`
- `tavily_hits`: `3`

Same shape on smoke JSON (`075935Z` usage `1413`).

## 6. Video honesty (expected question)

oEmbed title: “Gatekeeper working demo — Hermes + NVIDIA Nemotron on Nebius Token Factory”.
**On-camera behavior:** keys unset → `BLOCKED_INFRA`. That is fail-closed, not a live Super 120B reply. Live proof is the JSON in §2–§5.

## 7. Devpost (portal, 2026-09-03T17:12Z scrape after `GO_DEVPOST_UPDATE`)

| Check | Result |
|---|---|
| Embed `_nyPil6cb_g` | present |
| Working demo / test-build | Actions **`33781962888`** (SUCCESS, tip `45eacef` reviewer packet) |
| Writeup | Best Apps / Refuse-first / `JUDGE_START_HERE` / collision FAIL + WebView PASS |
| `docs/REVIEWER_PACKET.md` linked | present on public page |
| Old demo URL `33746517076` | **removed** |
| Submit | already Submitted; `submitted_at` 2026-09-01 — do not click Submit again |

## 8. Reviewer FAQ (pre-answered)

**Q: Is `tavily=grounded` enough for the $3k Tavily prize?**
A: No. Grounded means hits returned. Quality is `102852Z` (PASS) vs `075935Z`/`070111Z` (FAIL). Use the WebView JSON.

**Q: Why two FAIL directories?**
A: `070111Z` was the first live pair; `075935Z` is the published smoke with sidecar hashes. Both document the same collision class. Do not treat either as mechanism-relevant.

**Q: Why is `JUDGE_START_HERE` sometimes a commit behind `main`?**
A: Docs-only commits cannot contain their own SHA. Trust GitHub `main` HEAD + this packet’s **paths**. Audited code/evidence snapshot: `52d2821`.

**Q: Can I replay live Tavily/Nemotron from CI?**
A: No. Public CI has no API keys (intentional). Replay locally with your own keys using the argv in `102852Z/release-manifest.json`.

**Q: Is this a vulnerability report?**
A: No. `finding=false`. Fixtures are synthetic/public.

## 9. Files to open in order

1. `JUDGE_START_HERE.md` (this packet)
2. `evidence/live/20260903T102852Z/golden_path.json`
3. `evidence/reviews/tavily-relevance-20260903.md`
4. `evidence/live/20260903T075935Z/golden_path.json` (collision FAIL)
5. `docs/JUDGING_EVIDENCE_MATRIX.md`
6. Actions run on `main`
