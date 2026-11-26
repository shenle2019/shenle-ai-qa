# -*- coding: utf-8 -*-
"""为什么改了共享运行时之后第一段反而卡住：抓 console、pageerror 与 Pyodide 内部状态。"""

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5210/shenle-ai-qa/labs/playground.html"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    logs: list[str] = []
    page.on("console", lambda m: logs.append(f"[{m.type}] {m.text}")[:300])
    page.on("pageerror", lambda e: logs.append(f"[pageerror] {e}")[:300])
    page.on("request", lambda r: logs.append(f"[req] {r.url.rsplit('/', 1)[-1]}") if "jsdelivr" in r.url else None)
    page.on("requestfailed", lambda r: logs.append(f"[failed] {r.url.rsplit('/', 1)[-1]} {r.failure}"))

    page.goto(BASE, wait_until="domcontentloaded")
    page.wait_for_timeout(1500)

    print("loadPyodide 存在:", page.evaluate("typeof window.loadPyodide"))
    page.locator("details.pg-wrap").first.locator("summary").click()
    page.locator("div.pg").first.locator("button.pg-btn:not(.ghost)").click()

    for i in range(20):
        page.wait_for_timeout(3000)
        state = page.evaluate(
            "() => ({shared: !!window.__pyodideShared, inst: !!(window.__pyodideShared||{}).instance,"
            " loading: !!(window.__pyodideShared||{}).loading, hasLoad: typeof window.loadPyodide})"
        )
        out = page.locator("div.pg").first.locator(".pg-out").inner_text().strip().replace("\n", " | ")
        print(f"{3 * (i + 1):>3}s {state} out={out[:110]}")
        if state["inst"]:
            break

    print("\n日志:")
    for line in logs[:40]:
        print("  ", line)
    browser.close()
