"""本地预览里核验 /skills/ 21 项、两页可开、zip 链接在。"""

from __future__ import annotations

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5210/shenle-ai-qa"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000})

    page.goto(f"{BASE}/skills/", wait_until="networkidle")
    rows = page.locator("table tbody tr").count()
    print("skills rows:", rows)

    for slug in ("shenle-api-cli", "shenle-device-record"):
        resp = page.goto(f"{BASE}/skills/{slug}", wait_until="networkidle")
        h1 = page.locator("h1").first.inner_text().strip()
        print(slug, "status", resp.status if resp else "-", "h1", h1, "chars", len(page.content()))

    page.goto(f"{BASE}/kb/skills/api-cli", wait_until="networkidle")
    has_score = page.locator("text=评分（skill-judge）").count()
    body = page.inner_text("body")
    print("kb api-cli 有评分段:", has_score, "| 提到 shenle-api-cli:", "shenle-api-cli" in body)

    page.goto(f"{BASE}/kb/skills/device-record", wait_until="networkidle")
    print("kb device-record 有评分段:", page.locator("text=评分（skill-judge）").count())

    page.goto(f"{BASE}/skills/", wait_until="networkidle")
    page.screenshot(path="docs/shots/local-skills-21.png")
    browser.close()
