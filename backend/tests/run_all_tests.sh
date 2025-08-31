#!/usr/bin/env bash
# Run backend tests with pytest and coverage.
# Usage:
#   bash backend/tests/run_all_tests.sh

set -euo pipefail

LOG(){ echo "[backend-tests] $*"; }
ERR(){ echo "[backend-tests][ERROR] $*" >&2; }

pushd "$(dirname "$0")/.." >/dev/null

LOG "Creating virtual environment (optional)..."
python -m venv .venv >/dev/null 2>&1 || true
source .venv/bin/activate 2>/dev/null || true

LOG "Installing dependencies..."
pip install -r requirements.txt >/dev/null
pip install pytest-cov >/dev/null || true

LOG "Running pytest with coverage..."
pytest -q --maxfail=1 --disable-warnings --cov=backend --cov-report=term-missing

popd >/dev/null
