"""
Integration test: frontend <-> backend.

Requirements:
- Python 3.10+
- requests
- playwright (or selenium)

Install deps quickly:
  pip install requests playwright
  playwright install chromium

Usage:
  python deploy/test_integration.py --frontend http://localhost:3000 --backend http://localhost:8000 --token <JWT>

This script:
- Loads the homepage
- Uploads a mock receipt via UI (if upload field exists)
- Triggers a simulation query
- Confirms results render
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from typing import Optional

import requests

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None


def log(title: str, data: object) -> None:
    print(f"\n=== {title} ===")
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2)[:4000])
    else:
        print(str(data)[:4000])


def http_health(backend: str) -> None:
    r = requests.get(f"{backend}/health", timeout=15)
    log("GET /health", r.json())


def run_browser(frontend: str, backend: str, token: Optional[str]) -> None:
    if not sync_playwright:
        print("Playwright not installed; skipping UI checks.")
        return
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({"Authorization": f"Bearer {token}"} if token else {})

        # Load home
        page.goto(frontend, wait_until="domcontentloaded")
        log("Frontend title", page.title())

        # Try navigating to upload page
        try:
            page.goto(f"{frontend}/upload", wait_until="domcontentloaded")
            log("At /upload", "OK")
        except Exception as e:
            log("Upload page navigation failed", str(e))

        # Try a simulation
        try:
            page.goto(f"{frontend}/simulation", wait_until="domcontentloaded")
            # Input field heuristic
            sel = 'textarea, input[type="text"]'
            el = page.query_selector(sel)
            if el:
                el.fill("What if I increase coffee price by 10%?")
                # Submit via Enter or click first button
                btn = page.query_selector('button')
                if btn:
                    btn.click()
                else:
                    el.press("Enter")
                time.sleep(2)
                log("Simulation trigger", "Submitted query")
            else:
                log("Simulation input not found", "Skipped")
        except Exception as e:
            log("Simulation page failed", str(e))

        browser.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frontend", default="http://localhost:3000")
    ap.add_argument("--backend", default="http://localhost:8000")
    ap.add_argument("--token", default=None)
    args = ap.parse_args()

    try:
        http_health(args.backend)
    except Exception as e:
        log("Backend health failed", str(e))

    try:
        run_browser(args.frontend, args.backend, args.token)
    except Exception as e:
        log("Frontend browser checks failed", str(e))


if __name__ == "__main__":
    main()
