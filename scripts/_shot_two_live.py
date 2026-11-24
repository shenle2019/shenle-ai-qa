"""线上截图：Skills 库 21 项 + device-record 评分段。"""

from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "docs" / "shots"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    page.goto("https://shenle2019.github.io/shenle-ai-qa/skills/", wait_until="networkidle")
    page.screenshot(path=str(OUT / "live-skills-21.png"))
    page.goto(
        "https://shenle2019.github.io/shenle-ai-qa/kb/skills/device-record",
        wait_until="networkidle",
    )
    page.evaluate(
        "() => { const h = [...document.querySelectorAll('h2')].find(x => x.textContent.includes('评分')); h && h.scrollIntoView(); }"
    )
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT / "live-devrec-score.png"))
    print("ok")
    browser.close()
