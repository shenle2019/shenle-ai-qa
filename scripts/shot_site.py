"""Screenshot the built site pages for the chapter-1 report."""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(r"E:\ailearning\shenle-ai-qa\docs\shots")
BASE = "http://127.0.0.1:5200/shenle-ai-qa/"
PAGES = [("home", ""), ("ch01", "chapters/ch01"), ("labs", "labs/")]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        for name, path in PAGES:
            page.goto(BASE + path, wait_until="load")
            page.wait_for_timeout(1200)
            page.screenshot(path=str(OUT / f"site-{name}.png"), full_page=True)
        print("pages", len(PAGES), "pageerrors", len(errors))
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

