#!/usr/bin/env bash
# Run all frontend tests with Jest and print a concise summary.
# Usage:
#   bash frontend/tests/run_all_tests.sh

set -euo pipefail

LOG(){ echo "[frontend-tests] $*"; }
ERR(){ echo "[frontend-tests][ERROR] $*" >&2; }

pushd "$(dirname "$0")/.." >/dev/null

LOG "Installing dependencies (if needed)..."
if ! npm ci >/dev/null 2>&1; then
  LOG "npm ci failed, falling back to npm install"
  npm install
fi

LOG "Running Jest tests..."
set +e
OUT=$(npm test --silent 2>&1)
CODE=$?
set -e
echo "$OUT"

# Summarize results
PASSED=$(echo "$OUT" | grep -Eo "\b[0-9]+ passed\b" | awk '{print $1}' | tail -n1)
FAILED=$(echo "$OUT" | grep -Eo "\b[0-9]+ failed\b" | awk '{print $1}' | tail -n1)
TOTAL=$(echo "$OUT" | grep -Eo "\b[0-9]+ total\b" | awk '{print $1}' | tail -n1)

LOG "Summary: passed=${PASSED:-0}, failed=${FAILED:-0}, total=${TOTAL:-0}"

popd >/dev/null

exit $CODE
