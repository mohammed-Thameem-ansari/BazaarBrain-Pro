#!/usr/bin/env bash
# Cloud deployment helper (optional examples for Docker Hub / GCR / Cloud Run / Vercel)
# Usage:
#   bash deploy/deploy_cloud.sh <dockerhub-username> <project-id>
# Requires:
#   - Docker logged in (docker login)
#   - gcloud CLI configured if using GCR/Cloud Run

set -euo pipefail

USER="${1:-your-dockerhub-username}"
PROJECT="${2:-your-gcp-project}"

LOG(){ echo "[deploy_cloud] $*"; }

# Build images
LOG "Building frontend image..."
docker build -t ${USER}/bazaarbrain-frontend -f deploy/Dockerfile.frontend .
LOG "Building backend image..."
docker build -t ${USER}/bazaarbrain-backend -f deploy/Dockerfile .

# Push images to Docker Hub
LOG "Pushing images to Docker Hub..."
docker push ${USER}/bazaarbrain-frontend
docker push ${USER}/bazaarbrain-backend

# Example: Google Container Registry
# docker tag ${USER}/bazaarbrain-backend gcr.io/${PROJECT}/bazaarbrain-backend:latest
# docker push gcr.io/${PROJECT}/bazaarbrain-backend:latest

# Example: Cloud Run deployment
# gcloud run deploy bazaarbrain-backend \
#   --image gcr.io/${PROJECT}/bazaarbrain-backend:latest \
#   --platform managed --region us-central1 --allow-unauthenticated \
#   --set-env-vars "ENVIRONMENT=production,LOG_LEVEL=INFO"

LOG "For Vercel, connect the frontend directory and configure NEXT_PUBLIC_* env vars."
