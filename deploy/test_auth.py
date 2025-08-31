"""
Auth and role tests for BazaarBrain-Pro backend.

Note: Backend relies on Supabase auth. This script assumes you have a service that issues JWTs
or you supply a valid TEST_JWT_TOKEN via env/arg.

Usage:
  python deploy/test_auth.py --backend http://localhost:8000 --token <JWT>
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from typing import Dict
import requests


def log(title: str, data):
    print(f"\n=== {title} ===")
    try:
        print(json.dumps(data, indent=2)[:4000])
    except Exception:
        print(data)


def check_protected(backend: str, token: str) -> None:
    h = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    r = requests.get(f"{backend}/api/v1/transactions", headers=h, timeout=20)
    log("GET /api/v1/transactions", {"status": r.status_code, "body": safe_json(r)})

    body = {"source": "auth_test", "parsed_json": {"items": [{"name": "X", "price": 1.0}]}, "raw_input": "auth"}
    r2 = requests.post(f"{backend}/api/v1/transactions", headers={**h, 'Content-Type': 'application/json'}, json=body, timeout=20)
    log("POST /api/v1/transactions", {"status": r2.status_code, "body": safe_json(r2)})


def safe_json(resp: requests.Response):
    try:
        return resp.json()
    except Exception:
        return resp.text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', default='http://localhost:8000')
    ap.add_argument('--token', default=os.getenv('TEST_JWT_TOKEN'))
    args = ap.parse_args()

    if not args.token:
        print("Provide --token or set TEST_JWT_TOKEN. Skipping protected checks.")
        sys.exit(0)

    check_protected(args.backend, args.token)


if __name__ == '__main__':
    main()
