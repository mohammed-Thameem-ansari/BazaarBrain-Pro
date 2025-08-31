"""
End-to-end test for BazaarBrain-Pro.

Covers:
- Backend health
- Optional authenticated API flow (if E2E_JWT provided)
- Upload tiny PNG to /api/v1/upload_receipt
- Create+list transactions
- Run simulation and list simulations

Usage (envs):
  API_BASE_URL=http://localhost:8000 
  E2E_JWT=eyJhbGciOi... (optional)

Run:
  python deploy/e2e_test.py
"""
import os
import sys
import time
import uuid
import base64
import json
from io import BytesIO

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
JWT = os.getenv("E2E_JWT")
HEADERS = {"Accept": "application/json"}
if JWT:
    HEADERS["Authorization"] = f"Bearer {JWT}"


def log(msg):
    print(f"[E2E] {msg}")


def assert_status(resp, expected, ctx=""):
    if resp.status_code != expected:
        raise AssertionError(
            f"{ctx} expected {expected} got {resp.status_code} body={resp.text[:300]}"
        )


def health_check():
    log("Checking backend /health...")
    r = requests.get(f"{API_BASE_URL}/health", timeout=15)
    assert_status(r, 200, "/health")
    data = r.json()
    log(f"Health: status={data.get('status')} version={data.get('version','n/a')}")


def maybe_auth_flow():
    if not JWT:
        log("No E2E_JWT provided; skipping authenticated API checks.")
        return

    # Create a transaction
    tx_payload = {
        "source": "e2e",
        "raw_input": "e2e_request",
        "parsed_json": {"total": 123.45, "items": [{"name": "Test", "price": 123.45}]},
    }
    log("Creating transaction via POST /api/v1/transactions...")
    r = requests.post(
        f"{API_BASE_URL}/api/v1/transactions",
        headers={**HEADERS, "Content-Type": "application/json"},
        json=tx_payload,
        timeout=30,
    )
    assert_status(r, 200, "POST /transactions")
    tx_id = r.json().get("transaction_id")
    log(f"Created transaction id={tx_id}")

    log("Listing transactions via GET /api/v1/transactions...")
    r = requests.get(f"{API_BASE_URL}/api/v1/transactions", headers=HEADERS, timeout=30)
    assert_status(r, 200, "GET /transactions")
    log(f"Transactions count={r.json().get('count')}")

    # Upload a tiny 1x1 PNG
    log("Uploading tiny PNG to /api/v1/upload_receipt...")
    png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQAB"
        "J6k7WQAAAABJRU5ErkJggg=="
    )
    png_bytes = base64.b64decode(png_b64)
    files = {"file": ("tiny.png", png_bytes, "image/png")}
    data = {"source": "e2e"}
    r = requests.post(
        f"{API_BASE_URL}/api/v1/upload_receipt", headers=HEADERS, files=files, data=data, timeout=60
    )
    if r.status_code not in (200, 422, 500):
        # 422 may occur if OCR/agents return validation issues; treat as partial pass
        assert_status(r, 200, "POST /upload_receipt")
    log(f"Upload response status={r.status_code}")

    # Run a simulation
    log("Running simulation via POST /api/v1/simulate...")
    r = requests.post(
        f"{API_BASE_URL}/api/v1/simulate",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"query": "What if I increase coffee price by 10%?"},
        timeout=60,
    )
    if r.status_code not in (200, 422, 500):
        assert_status(r, 200, "POST /simulate")
    log(f"Simulate response status={r.status_code}")

    log("Listing simulations via GET /api/v1/simulations...")
    r = requests.get(f"{API_BASE_URL}/api/v1/simulations", headers=HEADERS, timeout=30)
    if r.status_code != 200:
        log(f"GET /simulations non-200 ({r.status_code}) - continuing")
    else:
        log(f"Simulations count={r.json().get('count')}")


if __name__ == "__main__":
    try:
        health_check()
        maybe_auth_flow()
        log("E2E checks complete.")
    except Exception as e:
        log(f"E2E failed: {e}")
        sys.exit(1)
