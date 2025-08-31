"""
Production smoke test for BazaarBrain-Pro backend.

Usage:
  python deploy/test_backend_prod.py --base-url http://localhost:8000 --token <JWT_TOKEN>

It will call:
- GET /health
- GET /api/v1/transactions
- POST /api/v1/transactions (if available)
- POST /api/v1/upload_receipt (with a tiny PNG in-memory)

Note: Our backend currently exposes GET /api/v1/transactions and POST /api/v1/upload_receipt.
"""
import argparse
import json
import sys
import requests


def pretty(title: str, obj):
    print(f"\n=== {title} ===")
    try:
        print(json.dumps(obj, indent=2)[:4000])
    except Exception:
        print(obj)


def tiny_png_bytes() -> bytes:
    # 1x1 transparent PNG
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x02\x00\x01"
        b"\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base-url', default='http://localhost:8000')
    p.add_argument('--token', required=False, help='JWT bearer token for auth-protected endpoints')
    args = p.parse_args()

    s = requests.Session()
    headers = {"Accept": "application/json"}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"

    # Health
    try:
        r = s.get(f"{args.base_url}/health", headers=headers, timeout=15)
        pretty("GET /health", r.json())
    except Exception as e:
        print(f"Health check failed: {e}", file=sys.stderr)

    # GET /api/v1/transactions
    try:
        r = s.get(f"{args.base_url}/api/v1/transactions", headers=headers, timeout=30)
        pretty("GET /api/v1/transactions", r.json())
    except Exception as e:
        print(f"GET transactions failed: {e}", file=sys.stderr)

    # POST /api/v1/transactions (JSON-based creation for testing)
    try:
        body = {
            "source": "api_test",
            "parsed_json": {"items": [{"name": "Test Item", "price": 9.99}]},
            "raw_input": "test_payload"
        }
        r = s.post(f"{args.base_url}/api/v1/transactions", headers={**headers, 'Content-Type': 'application/json'}, json=body, timeout=30)
        pretty("POST /api/v1/transactions", r.json())
    except Exception as e:
        print(f"POST transactions failed: {e}", file=sys.stderr)

    # POST /api/v1/upload_receipt (image upload)
    try:
        files = {"file": ("tiny.png", tiny_png_bytes(), "image/png")}
        data = {"source": "image"}
        r = s.post(f"{args.base_url}/api/v1/upload_receipt", headers=headers, files=files, data=data, timeout=60)
        pretty("POST /api/v1/upload_receipt", r.json())
    except Exception as e:
        print(f"Upload receipt failed: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
