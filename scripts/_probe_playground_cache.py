# -*- coding: utf-8 -*-
"""查一个具体现象：第二段还打印「首次运行：正在下载…」，到底是真又下了一遍，还是文案没改。

判据：
- 记录对 cdn.jsdelivr.net 的请求次数（pyodide.js / pyodide.asm.wasm 各几次）
- 第二段输出里有没有「首次运行」
- 第二段耗时
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5210/shenle-ai-qa/labs/playground.html"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    cdn: list[str] = []
    page.on("request", lambda r: cdn.append(r.url) if "jsdelivr" in r.url else None)

    page.goto(BASE, wait_until="domcontentloaded")
    for box in page.locator("details.pg-wrap").all():
        box.locator("summary").click(timeout=3000)

    blocks = page.locator("div.pg")
    for i in range(2):
        blocks.nth(i).locator("button.pg-btn:not(.ghost)").click()
        blocks.nth(i).locator(".pg-out").wait_for(state="visible")
        for _ in range(120):
            if blocks.nth(i).locator(".pg-out").get_attribute("data-state") == "done":
                break
            page.wait_for_timeout(500)
        out = blocks.nth(i).locator(".pg-out").inner_text()
        print(f"#{i + 1} 含「首次运行」: {'首次运行' in out}  cdn 请求累计: {len(cdn)}")
        print("   ", out.replace("\n", " | ")[:200])

    print("\ncdn 请求明细:")
    for url in cdn:
        print("  -", url.split("?")[0][-70:])
    browser.close()
