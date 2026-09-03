#!/usr/bin/env bash
# One-judge-SHA live segment from INBOX_NEXT.md (adapted for corrected manifest CLI).
set -euo pipefail
ROOT=/Users/radik/bounty/research/hackathon-mail-20260831/agents/nebius-nvidia-hackathon/gatekeeper
cd "$ROOT"
test "$(git ls-remote origin refs/heads/main | awk '{print $1}')" = 92a491f54a991952d932b0c14e987077be0f8913
test "$(git rev-parse HEAD)" = 92a491f54a991952d932b0c14e987077be0f8913

set -a; source .env; set +a
export PYTHONPATH=src
GIT_SHA=$(git rev-parse HEAD)
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT="evidence/live/${TS}"
mkdir -p "$OUT"

golden() {
  local json="$1"
  local base="${json%.json}"
  .venv/bin/python3 -m gatekeeper.triage \
    --package com.example.synthetic.gatekeeper.demo \
    --mechanism SEND-extra-to-privileged-persist \
    --static-notes "Synthetic judge demo; not a finding; public fixture only." \
    --tavily-mode required \
    >"$json" 2>"${base}.stderr"
  echo $? >"${base}.exit"
}
golden "$OUT/golden_path.json"
golden "$OUT/golden_path_repeat.json"

python3 - "$OUT" <<'PY'
import json, pathlib, re, sys
out = pathlib.Path(sys.argv[1])
secret = re.compile(r"(?i)tvly-|sk-|NEBIUS_API_KEY|TAVILY_API_KEY|bearer\s+[A-Za-z0-9._\-]+")
need = ("verdict", "provider", "model", "tavily", "tavily_hits", "citations", "latency_ms")
for name in ("golden_path.json", "golden_path_repeat.json"):
    p = out / name
    text = p.read_text()
    if secret.search(text):
        sys.exit(f"SECRET in {p}")
    data = json.loads(text)
    rc = int((out / f"{name.replace('.json','')}.exit").read_text().strip() or "1")
    if rc != 0:
        sys.exit(f"exit {rc} {name}")
    missing = [k for k in need if k not in data]
    if missing:
        sys.exit(f"missing {missing} in {name}")
    if data.get("tavily") != "grounded" or int(data.get("tavily_hits") or 0) < 1:
        sys.exit(f"not grounded: {name} tavily={data.get('tavily')}")
    if data.get("provider") != "nebius-token-factory":
        sys.exit(f"provider={data.get('provider')}")
    if "nemotron" not in str(data.get("model") or "").lower():
        sys.exit(f"model={data.get('model')}")
    if data.get("verdict") not in {"ALLOW_PREFLIGHT", "PARK"}:
        sys.exit(f"verdict={data.get('verdict')}")
print("live_ok", out)
PY

.venv/bin/python3 scripts/build_evidence_manifest.py \
  --git-sha "$GIT_SHA" \
  --outdir "$OUT" \
  --ci-url "https://github.com/RadikHoroshev/gatekeeper/actions/runs/33725567243" \
  --demo-url "https://youtu.be/_nyPil6cb_g" \
  --citation-relevance "FAILED_MANUAL_REVIEW" \
  --limitation "synthetic package; retrieved citations not mechanism-relevant (see evidence/reviews)" \
  --limitation "demo_url is fail-closed video, not this live run" \
  --write "$OUT/release-manifest.json"

if grep -R --quiet '0000000000000000000000000000000000000000000000000000000000000000' "$OUT"; then
  echo "placeholder hash in $OUT"; exit 1
fi

printf '%s\n' "$OUT" > /tmp/gatekeeper-one-judge-out.txt
printf '%s\n' "$TS" > /tmp/gatekeeper-one-judge-ts.txt
echo "LIVE_DONE out=$OUT"
