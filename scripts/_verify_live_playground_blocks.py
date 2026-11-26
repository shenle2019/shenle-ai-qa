"""Run every playground block on the live site and report per-block state."""

import json
import time

from playwright.sync_api import sync_playwright

import os
BASE = os.environ.get(
    "PG_BASE", "https://shenle2019.github.io/shenle-ai-qa/labs/playground"
)


def main():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        console = []
        page.on("console", lambda m: console.append(f"{m.type}:{m.text[:120]}"))
        page.goto(BASE, wait_until="networkidle")
        page.wait_for_timeout(500)

        # 展开所有折叠块，否则按钮不可点
        summaries = page.locator("details > summary")
        for i in range(summaries.count()):
            details = page.locator("details").nth(i)
            if not details.get_attribute("open"):
                summaries.nth(i).click()
                page.wait_for_timeout(150)

        total = page.locator(".pg").count()
        print(f"blocks={total}")

        for index in range(total):
            block = page.locator(".pg").nth(index)
            block.scroll_into_view_if_needed()
            page.wait_for_timeout(150)

            if index == 0:
                page.screenshot(path="docs/shots/live-playground-first.png")

            started = time.time()
            block.get_by_role("button", name="运行").click()

            state = "loading"
            out = ""
            for _ in range(120):
                page.wait_for_timeout(1000)
                state = block.locator(".pg-dot").get_attribute("data-state")
                out = block.locator(".pg-out").inner_text()
                if state in ("done", "error"):
                    break
            elapsed = round(time.time() - started, 1)
            results.append(
                {
                    "block": index + 1,
                    "state": state,
                    "elapsed_s": elapsed,
                    "out_head": [line for line in out.strip().splitlines() if line][:3],
                }
            )
            print(results[-1])

        page.screenshot(path="docs/shots/live-playground-stage7.png")
        browser.close()

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print("console errors:", [c for c in console if c.startswith("error")])


if __name__ == "__main__":
    main()
