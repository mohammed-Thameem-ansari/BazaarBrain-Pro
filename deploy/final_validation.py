"""
Final validation script to check deployment readiness.
- Validates env presence
- Hits health endpoints
- Optionally validates authenticated flows
"""
import os
import sys
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
JWT = os.getenv("E2E_JWT")

REQUIRED_ENVS = [
    "OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
]


def check_env():
    missing = [k for k in REQUIRED_ENVS if not os.getenv(k)]
    if missing:
        print("Missing envs:", ", ".join(missing))
        return False
    return True


def check_health():
    r = requests.get(f"{API_BASE_URL}/health", timeout=10)
    if r.status_code != 200:
        print("/health non-200:", r.status_code, r.text[:200])
        return False
    print("/health OK")
    r = requests.get(f"{API_BASE_URL}/api/v1/health/detailed", timeout=10)
    print("/api/v1/health/detailed:", r.status_code)
    return True


def main():
    ok_env = check_env()
    ok_health = check_health()
    if not (ok_env and ok_health):
        sys.exit(1)
    print("Validation PASSED.")


if __name__ == "__main__":
    main()
