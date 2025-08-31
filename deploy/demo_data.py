"""
Seed demo data via authenticated API calls.

Env:
  API_BASE_URL=http://localhost:8000
  DEMO_JWT=...
Run:
  python deploy/demo_data.py
"""
import os
import json
import base64
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
JWT = os.getenv("DEMO_JWT")
HEADERS = {"Accept": "application/json"}
if JWT:
    HEADERS["Authorization"] = f"Bearer {JWT}"


def create_transaction(total, items, source="demo"):
    payload = {"source": source, "raw_input": "seed", "parsed_json": {"total": total, "items": items}}
    r = requests.post(
        f"{API_BASE_URL}/api/v1/transactions",
        headers={**HEADERS, "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    ok = r.status_code == 200
    return ok, r.json() if ok else {"error": r.text}


def run_simulation(query):
    r = requests.post(
        f"{API_BASE_URL}/api/v1/simulate",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"query": query},
        timeout=60,
    )
    ok = r.status_code == 200
    return ok, r.json() if ok else {"error": r.text}


if __name__ == "__main__":
    if not JWT:
        print("DEMO_JWT missing; set DEMO_JWT and retry.")
        raise SystemExit(1)

    print("Seeding demo transactions...")
    samples = [
        (199.99, [{"name": "Groceries", "price": 199.99}]),
        (49.5, [{"name": "Tea", "price": 19.5}, {"name": "Biscuits", "price": 30.0}]),
        (12.0, [{"name": "Bread", "price": 12.0}]),
    ]
    for total, items in samples:
        ok, res = create_transaction(total, items)
        print("tx:", ok, res)

    print("Running sample simulations...")
    queries = [
        "What if I increase coffee price by 10%?",
        "How would a 15% price hike affect tea sales?",
    ]
    for q in queries:
        ok, res = run_simulation(q)
        print("sim:", ok, res)

    print("Done.")
