"""
Multi-language and accessibility checks for the frontend via Playwright.

Usage:
  python deploy/test_i18n_accessibility.py --frontend http://localhost:3000
"""
from __future__ import annotations
import argparse
import json

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

        # English, Hindi, Tamil, Telugu toggle checks
        langs = ['en', 'hi', 'ta', 'te']
        for lang in langs:
            page.goto(f"{args.frontend}?lang={lang}", wait_until='domcontentloaded')
            log(f'Loaded lang {lang}', page.title())

        # Basic accessibility spot checks: ARIA roles
        page.goto(args.frontend, wait_until='domcontentloaded')
        roles = page.locator('[role]')
        count = roles.count()
        log('Elements with role attribute', count)

        browser.close()


if __name__ == '__main__':
    main()
