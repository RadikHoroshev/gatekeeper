#!/usr/bin/env bash
# Public no-secret test build for judges.
# Static GO/PARK plus fail-closed BLOCKED_INFRA. Never calls Token Factory.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Refuse live inference even if a runner leaked a key.
unset NEBIUS_API_KEY OPENAI_API_KEY
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

if [[ -x "${ROOT}/.venv/bin/python3" && -z "${CI:-}" ]]; then
  PY="${ROOT}/.venv/bin/python3"
else
  PY="${PYTHON:-python3}"
fi

OUT="${PUBLIC_TEST_TRANSCRIPT:-${ROOT}/public-test-transcript.txt}"
: >"$OUT"
log() {
  printf '%s\n' "$*" | tee -a "$OUT"
}

expect_contains() {
  local file="$1"
  local needle="$2"
  if ! grep -F -q -- "$needle" "$file"; then
    log "FAIL: expected ${needle} in ${file}"
    exit 1
  fi
}

run_json() {
  local label="$1"
  local dest="$2"
  shift 2
  log ""
  log "=== ${label} ==="
  set +e
  "$PY" -B -m gatekeeper.triage "$@" >"$dest" 2>&1
  local rc=$?
  set -e
  tee -a "$OUT" <"$dest"
  log "exit=${rc}"
}

log "Gatekeeper public test (no secrets, no Token Factory call)"
log "python=$PY"
log "ci=${CI:-local}"
"$PY" -c "import openai, yaml; print('imports_ok')" | tee -a "$OUT"

ALLOW_JSON="$(mktemp)"
PARK_JSON="$(mktemp)"
trap 'rm -f "$ALLOW_JSON" "$PARK_JSON"' EXIT

run_json "named candidate ALLOW_STATIC" "$ALLOW_JSON" \
  --package com.example.fake.candidate \
  --mechanism SEND-extra-to-privileged-persist \
  --static-notes "Public test-build; synthetic candidate, not a finding." \
  --dry-run
expect_contains "$ALLOW_JSON" '"verdict": "ALLOW_STATIC"'
expect_contains "$ALLOW_JSON" '"nemotron": "skipped"'
expect_contains "$ALLOW_JSON" '"finding": false'

run_json "spray PARK_INSTANT" "$PARK_JSON" \
  --package com.google.android.gms \
  --mechanism ""
expect_contains "$PARK_JSON" '"verdict": "PARK"'
expect_contains "$PARK_JSON" '"park_class": "PARK_INSTANT"'
expect_contains "$PARK_JSON" '"finding": false'

log ""
log "=== fail-closed smoke (key unset) ==="
set +e
smoke="$("$PY" "${ROOT}/scripts/smoke_nemotron.py" 2>&1)"
smoke_rc=$?
set -e
printf '%s\n' "$smoke" | tee -a "$OUT"
log "exit=${smoke_rc}"
if ! grep -F -q -- "BLOCKED_INFRA" <<<"$smoke"; then
  log "FAIL: expected BLOCKED_INFRA"
  exit 1
fi
if [[ "$smoke_rc" -ne 3 ]]; then
  log "FAIL: smoke without key must exit 3"
  exit 1
fi

log ""
log "PASS public-test: ALLOW_STATIC + PARK_INSTANT + BLOCKED_INFRA"
echo "PASS"
