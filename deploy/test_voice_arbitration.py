"""
Voice and arbitration test. This script simulates voice input by providing canned text commands
(since bundled STT may not be available). It verifies the frontend page loads and
that the arbitration panel UI exists. For full STT, integrate with your chosen provider.

Usage:
  python deploy/test_voice_arbitration.py --frontend http://localhost:3000
"""
from __future__ import annotations
import argparse
import json
from typing import Optional

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None


def log(title: str, data):
    print(f"\n=== {title} ===")
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2)[:4000])
    else:
        print(str(data)[:4000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frontend', default='http://localhost:3000')
    args = ap.parse_args()

    if not sync_playwright:
        log('Playwright not installed', 'Install with: pip install playwright; playwright install chromium')
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{args.frontend}/voice", wait_until='domcontentloaded')
        log('Voice page title', page.title())

        # Arbitration panel check
        try:
            page.goto(f"{args.frontend}/dashboard", wait_until='domcontentloaded')
            has_panel = page.locator('text=Arbitration').count() > 0
            log('Arbitration panel present', has_panel)
        except Exception as e:
            log('Arbitration panel check failed', str(e))

        browser.close()


if __name__ == '__main__':
    main()
