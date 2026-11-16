"""Open the playground page, run the first snippet in a real browser, screenshot it."""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SHOTS = Path(__file__).resolve().parents[1] / "docs" / "shots"
URL = "http://127.0.0.1:5199/shenle-ai-qa/labs/playground"


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(URL, wait_until="load")
        page.wait_for_selector(".pg", state="attached", timeout=60_000)
        page.wait_for_timeout(600)
        page.locator("details.pg-wrap").first.evaluate("el => { el.open = true }")
        page.wait_for_timeout(400)
        page.screenshot(path=str(SHOTS / "playground-before.png"), full_page=False)

        buttons = page.locator(".pg-btn", has_text="运行")
        print("run buttons:", buttons.count())
        buttons.first.click()

        # first run downloads ~10MB of wasm; give it time
        try:
            page.wait_for_function(
                "() => { const o = document.querySelector('.pg-out'); return o && o.textContent.includes('总分'); }",
                timeout=180_000,
            )
            print("output ok")
        except Exception as exc:  # noqa: BLE001
            print("wait failed:", exc.__class__.__name__)

        out = page.locator(".pg-out").first.inner_text()
        print("--- output ---")
        print(out[:400])
        page.screenshot(path=str(SHOTS / "playground-run.png"), full_page=False)
        print("pageerrors", len(errors))
        browser.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
