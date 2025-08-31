"""
Post-deployment smoke test.

Usage:
  python deploy/smoke_test.py --frontend https://your-frontend --backend https://your-backend --token <JWT>
"""
from __future__ import annotations
import argparse
import json
import sys
from typing import Optional

import requests


def log(title: str, data: object) -> None:
    print(f"\n=== {title} ===")
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2)[:4000])
    else:
        print(str(data)[:4000])


def safe_json(r: requests.Response):
    try:
        return r.json()
    except Exception:
        return r.text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frontend', required=True)
    ap.add_argument('--backend', required=True)
    ap.add_argument('--token', default=None)
    args = ap.parse_args()

    # Backend health
    try:
        r = requests.get(f"{args.backend}/health", timeout=20)
        log('GET /health', safe_json(r))
    except Exception as e:
        log('Health failed', str(e))

    headers = {'Accept': 'application/json'}
    if args.token:
        headers['Authorization'] = f'Bearer {args.token}'

    # Transactions list
    try:
        r = requests.get(f"{args.backend}/api/v1/transactions", headers=headers, timeout=30)
        log('GET /api/v1/transactions', {'status': r.status_code, 'body': safe_json(r)})
    except Exception as e:
        log('Transactions failed', str(e))

    # Upload sample receipt
    try:
        tiny_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc``\x00\x00\x00\x02\x00\x01"
            b"\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        files = {"file": ("tiny.png", tiny_png, "image/png")}
        data = {"source": "image"}
        r = requests.post(f"{args.backend}/api/v1/upload_receipt", headers=headers, files=files, data=data, timeout=60)
        log('POST /api/v1/upload_receipt', {'status': r.status_code, 'body': safe_json(r)})
    except Exception as e:
        log('Upload failed', str(e))


if __name__ == '__main__':
    main()
