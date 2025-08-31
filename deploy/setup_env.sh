#!/usr/bin/env bash
# Setup environment files for local dev (Unix/macOS)
# - Copies .env.example to .env if missing
# - Creates frontend/.env.local with NEXT_PUBLIC_* vars
# Usage:
#   bash deploy/setup_env.sh http://localhost:8000 https://xyz.supabase.co sk_...
set -euo pipefail
API_BASE_URL=${1:-http://localhost:8000}
SUPABASE_URL=${2:-}
SUPABASE_ANON_KEY=${3:-}
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

# Root .env
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
  else
    echo ".env.example not found; skipping root .env creation"
  fi
fi

# Frontend .env.local
FRONTEND_DIR="$ROOT_DIR/frontend"
FRONTEND_ENV="$FRONTEND_DIR/.env.local"
cat > "$FRONTEND_ENV" <<EOF
NEXT_PUBLIC_SUPABASE_URL=$SUPABASE_URL
NEXT_PUBLIC_SUPABASE_KEY=$SUPABASE_ANON_KEY
NEXT_PUBLIC_API_BASE_URL=$API_BASE_URL
EOF

echo "Wrote frontend .env.local"
