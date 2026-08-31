#!/usr/bin/env bash
# Demo: fake CANDIDATE event — static gates + optional Nemotron
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -x "${ROOT}/.venv/bin/python3" ]]; then
  PY="${ROOT}/.venv/bin/python3"
else
  PY=python3
fi
export PYTHONPATH="${ROOT}/src:${PYTHONPATH:-}"

echo "=== Gatekeeper demo (dry-run) ==="
"$PY" -m gatekeeper.triage \
  --package "com.example.fake.candidate" \
  --mechanism "SEND-extra-to-privileged-persist" \
  --static-notes "Synthetic CANDIDATE for hackathon video; not a real finding." \
  --dry-run

echo ""
echo "=== Spray blocked ==="
"$PY" -m gatekeeper.triage \
  --package "com.google.android.gms" \
  --mechanism "" \
  --dry-run 2>/dev/null || true

echo ""
echo "=== With Nemotron (requires NEBIUS_API_KEY) ==="
"$PY" -m gatekeeper.triage \
  --package "com.example.fake.candidate" \
  --mechanism "SEND-extra-to-privileged-persist" \
  --static-notes "Synthetic CANDIDATE for hackathon video." \
  || true
