# Backend (FastAPI) Guide

This document explains how the BazaarBrain-Pro backend is configured, run, and observed in development and production.

## Overview
- Framework: FastAPI + Uvicorn
- Auth: JWT (Supabase-compatible HS256, audience=authenticated)
- DB: Supabase PostgREST client (via `supabase` Python SDK)
- CORS: Configurable via env (FRONTEND_ORIGIN / ALLOWED_ORIGINS)
- Logging: Structured request logs + global exception handler

## Key Files
- `backend/main.py`: App factory, CORS, middlewares, routers, health
- `backend/auth.py`: JWT verification helpers and auth middleware
- `backend/config.py`: Env loading (.env/.env.production) and validation
- `backend/routers/*`: Feature routers for health, receipts, simulations
- `backend/requirements.txt`: Locked deps (aligned with Supabase/httpx)

## Environment
Primary variables (see `.env.example`):
- OPENAI_API_KEY, GOOGLE_API_KEY
- SUPABASE_URL, SUPABASE_ANON_KEY (or SUPABASE_KEY), SUPABASE_SERVICE_ROLE_KEY
- ENVIRONMENT, DEBUG, LOG_LEVEL
- FRONTEND_ORIGIN, ALLOWED_ORIGINS, ALLOW_ALL_CORS

In production set `ENVIRONMENT=production` and disable docs by setting `DEBUG=false`.

## Endpoints
- `GET /health`: API + DB health summary
- `GET /api/v1/health/*`: health, detailed, ready, live
- `POST /api/v1/upload_receipt`: multipart image upload (JWT required)
- `GET/POST/DELETE /api/v1/transactions`: manage parsed receipt transactions (JWT)
- `POST /api/v1/simulate`: run “what-if” simulation (JWT)
- `GET/DELETE /api/v1/simulations`: view/remove simulations (JWT)
- `GET /api/v1/scenarios`: list available simulation scenarios

## Auth
- Bearer token in `Authorization` header
- Token decoded with HS256 using Supabase JWT secret (service role key for dev)
- Required claims: `sub` (user id), `email`, audience `authenticated`

## Logging & Observability
- Request logging middleware emits: method, path, status, duration_ms, request_id, user_email
- Global exception handler returns stable 500 JSON schema with timestamp
- Health endpoints support liveness/readiness for container orchestration

## Docker
- Backend Dockerfile in `deploy/Dockerfile` (python:3.11-slim)
- Copies repo and launches `backend.main:app`
- Compose file in `deploy/docker-compose.yml` for local stacks

## Tests
- Back-end runner: `backend/tests/run_all_tests.sh` (pytest + coverage)
- Deploy smoke/integration: `deploy/smoke_test.py`, `deploy/test_docker_api.py`, `deploy/e2e_test.py`

## Notes
- If Supabase creds are placeholders, health may report `degraded` but API remains responsive.
- Protected endpoints return 401 without a valid JWT.
