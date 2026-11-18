"""第 16 章演示：起浏览器、四种定位方式、自动等待、截图。

直接运行::

    .\.venv\Scripts\python.exe labs\ch16-web-basics\demo_basics.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from labs._shared.mini_site import serve  # noqa: E402

SHOT_DIR = ROOT / "docs" / "shots"


def main() -> int:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    with serve() as base, sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        started = time.perf_counter()
        page.goto(f"{base}/login")
        print(f"打开登录页耗时 {int((time.perf_counter() - started) * 1000)} ms")

        # 四种定位方式，按稳定性从高到低
        by_role = page.get_by_role("button", name="登录")
        by_label = page.get_by_label("用户名")
        by_testid = page.get_by_test_id("password")
        by_text = page.get_by_text("任务清单", exact=False).first
        print("role 命中：", by_role.inner_text())
        print("label 命中 placeholder/id：", by_label.get_attribute("id"))
        print("testid 命中元素：", by_testid.get_attribute("name"))
        print("text 命中标题：", by_text.inner_text())

        # 断言：用 expect 而不是 if
        page.get_by_test_id("error").wait_for(state="attached")

        by_label.fill("alice")
        by_testid.fill("secret")
        by_role.click()

        page.wait_for_url("**/todos")
        print("登录后地址：", page.url)
        print("当前用户：", page.get_by_test_id("current-user").inner_text())

        # 自动等待：点击后元素 600ms 才出现，expect 会自己轮询
        page.get_by_test_id("start").click()
        page.get_by_test_id("done").wait_for(timeout=3000)
        print("异步节点文本：", page.get_by_test_id("done").inner_text())

        # 加一条待办，断言列表条数
        before = page.get_by_test_id("todo-item").count()
        page.get_by_label("新任务").fill("冒烟通过")
        page.get_by_test_id("add-submit").click()
        page.wait_for_load_state("load")
        after = page.get_by_test_id("todo-item").count()
        print(f"待办条数：{before} -> {after}")

        shot = SHOT_DIR / "ch16-todos.png"
        page.screenshot(path=str(shot), full_page=True)
        print("截图：", shot)

        context.close()
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
