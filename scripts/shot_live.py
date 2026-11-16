"""Screenshot the deployed GitHub Pages site."""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(r"E:\ailearning\shenle-ai-qa\docs\shots")
BASE = "https://shenle2019.github.io/shenle-ai-qa/"
PAGES = [("live-home", ""), ("live-ch01", "chapters/ch01"), ("live-labs", "labs/")]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        for name, path in PAGES:
            page.goto(BASE + path, wait_until="load")
            page.wait_for_timeout(1500)
            title = page.title()
            h1 = page.locator("h1").first.inner_text(timeout=5000) if page.locator("h1").count() else ""
            print(f"{name}: title={title!r} h1={h1[:40]!r}")
            page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
        print("pageerrors", len(errors))
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
