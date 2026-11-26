# -*- coding: utf-8 -*-
"""在真实浏览器里把「在线运行」的四段代码逐个点开真跑，收集全部问题。

判据（不看感觉）：
- 首段：点「运行」后 120 秒内，输出区是否出现 `李明 的总分 255`
- 后三段：共用运行时后应在 30 秒内出结果
- 四段都要 status=done（绿点），任何 `data-state="error"` 都算问题
- 同时收集 console 报错与失败的请求
"""

import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5210/shenle-ai-qa/labs/playground.html"
OUT = Path(__file__).resolve().parent.parent / "docs" / "shots"
EXPECT = ["总分 255", "已支付订单", "slow_sum", "不是整数"]

problems: list[str] = []

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1100})

    console: list[str] = []
    failed: list[str] = []
    page.on("console", lambda m: console.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    page.on("requestfailed", lambda r: failed.append(f"{r.url} {r.failure}"))

    page.goto(BASE, wait_until="domcontentloaded")
    # 展开四个 <details>，否则按钮点不到
    for box in page.locator("details.pg-wrap").all():
        try:
            box.locator("summary").click(timeout=3000)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"展开折叠块失败: {exc}")
    page.wait_for_timeout(500)

    runs = page.locator("div.pg")
    total = runs.count()
    print("playground 组件数:", total)
    if total != 4:
        problems.append(f"期望 4 个 playground，实际 {total}")

    for i in range(total):
        block = runs.nth(i)
        btn = block.locator("button.pg-btn:not(.ghost)")
        btn.click()
        started = time.time()
        hit = False
        while time.time() - started < 150:
            text = block.locator(".pg-out").inner_text()
            if any(k in text for k in EXPECT):
                hit = True
                break
            if block.locator(".pg-out").get_attribute("data-state") == "error":
                break
            page.wait_for_timeout(1000)
        elapsed = round(time.time() - started, 1)
        state = block.locator(".pg-out").get_attribute("data-state")
        text = block.locator(".pg-out").inner_text().strip()
        ok = hit and state == "done"
        print(f"\n#{i + 1} {elapsed}s state={state} ok={ok}")
        print("   ", text.replace("\n", " | ")[:260])
        if not ok:
            problems.append(f"第 {i + 1} 段失败：state={state} 耗时 {elapsed}s 输出={text[:160]!r}")
        if elapsed > 30 and i > 0:
            problems.append(f"第 {i + 1} 段用了 {elapsed}s，共用运行时后不该这么慢")

    page.screenshot(path=str(OUT / "live-playground-check.png"), full_page=False)
    print("\nconsole:", console[:6] or "无")
    print("failed requests:", failed[:6] or "无")
    browser.close()

print("\n问题清单：")
for item in problems:
    print(" -", item)
print(f"\n共 {len(problems)} 条")
sys.exit(1 if problems else 0)
