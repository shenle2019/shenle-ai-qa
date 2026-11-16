"""Verify the playground runs the code on the live GitHub Pages site."""

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

SHOTS = Path(__file__).resolve().parents[1] / "docs" / "shots"
URL = "https://shenle2019.github.io/shenle-ai-qa/labs/playground"


def main() -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(URL, wait_until="load")
        page.wait_for_selector(".pg", state="attached", timeout=60_000)
        page.locator("details.pg-wrap").first.evaluate("el => { el.open = true }")
        page.wait_for_timeout(400)
        page.locator(".pg-btn", has_text="运行").first.click()

        out = ""
        deadline = time.time() + 180
        while time.time() < deadline:
            out = page.locator(".pg-out").first.inner_text()
            if "总分" in out:
                break
            time.sleep(2)

        print("LIVE OUT:", out.replace("\n", " | ")[:240])
        ok = "总分" in out
        page.screenshot(path=str(SHOTS / "live-playground.png"), full_page=False)
        print("pageerrors", len(errors), "| ok", ok)
        browser.close()
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
