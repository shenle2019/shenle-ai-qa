from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "docs" / "shots"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto(
        "https://shenle2019.github.io/shenle-ai-qa/chapters/ch32",
        wait_until="networkidle",
    )
    page.evaluate("() => { const h = [...document.querySelectorAll('h2')].find(x => x.textContent.includes('延伸知识')); h && h.scrollIntoView(); }")
    page.wait_for_timeout(600)
    page.screenshot(path=str(OUT / "live-ch32-timeout.png"))

    page.goto("https://shenle2019.github.io/shenle-ai-qa/kb/rules", wait_until="networkidle")
    page.evaluate("() => { const h = [...document.querySelectorAll('h2')].find(x => x.textContent.includes('复核与台账')); h && h.scrollIntoView(); }")
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT / "live-rules-audit.png"))
    print("ok", page.title())
    browser.close()
