#!/usr/bin/env bash
# Cross-platform note: On Windows, run via Git Bash or WSL. macOS/Linux works out of the box.
# Purpose: Build the Next.js frontend for production using .env.production.
# Usage:
#   bash deploy/build_frontend.sh
#   DOTENV_FILE=frontend/.env.production bash deploy/build_frontend.sh

set -euo pipefail

LOG() { echo "[build_frontend] $*"; }
ERR() { echo "[build_frontend][ERROR] $*" >&2; }

pushd frontend >/dev/null

# Ensure NODE_ENV=production and .env.production are present
export NODE_ENV=production
if [ -f .env.production ]; then
  LOG "Using .env.production in frontend/"
else
  ERR ".env.production not found in frontend/. Create it before building."
  exit 1
fi

LOG "Installing dependencies..."
if ! npm ci >/dev/null 2>&1; then
  LOG "npm ci failed, falling back to npm install"
  npm install
fi

LOG "Building Next.js app..."
# Default build output to .next
npm run build

LOG "Build complete. Output is in frontend/.next"

popd >/dev/null
