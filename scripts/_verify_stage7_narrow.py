"""Narrow-viewport and chapter smoke checks on the live site."""

import json

from playwright.sync_api import sync_playwright

BASE = "https://shenle2019.github.io/shenle-ai-qa"


def main():
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()

        page = browser.new_page(viewport={"width": 390, "height": 844})
        for path, name in [("/labs/playground", "narrow-playground"), ("/chapters/ch47", "narrow-ch47")]:
            page.goto(BASE + path, wait_until="networkidle")
            page.wait_for_timeout(500)
            overflow = page.evaluate(
                "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
            )
            report[name] = {"overflow_px": overflow}
            page.screenshot(path=f"docs/shots/{name}.png", full_page=False)

        page.set_viewport_size({"width": 1440, "height": 1100})
        for path, name in [("/chapters/ch47", "live-ch47"), ("/chapters/ch53", "live-ch53"), ("/labs/", "live-labs-stage7")]:
            page.goto(BASE + path, wait_until="networkidle")
            page.wait_for_timeout(400)
            report[name] = {
                "title": page.title(),
                "h1": page.locator("h1").first.inner_text() if page.locator("h1").count() else "",
                "has_stage7": "第七阶段" in page.content(),
            }
            page.screenshot(path=f"docs/shots/{name}.png", full_page=False)

        browser.close()

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
