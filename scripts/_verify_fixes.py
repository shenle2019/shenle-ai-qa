"""Verify the 14 fixes on the local preview build."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5210/shenle-ai-qa"
OUT = Path("docs/shots")
OUT.mkdir(parents=True, exist_ok=True)
facts: dict[str, object] = {}


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # 1) 未知路径 → 中文 404
        page.goto(f"{BASE}/zzz-missing", wait_until="networkidle")
        page.wait_for_timeout(600)
        facts["404_title"] = page.title()
        facts["404_h1"] = page.locator(".nf-title").inner_text(timeout=5000) if page.locator(".nf-title").count() else None
        facts["404_buttons"] = page.locator(".nf-btn").all_inner_texts()
        page.screenshot(path=str(OUT / "fix-404.png"))

        # 2) 短名别名 → 跳到正牌页
        page.goto(f"{BASE}/skills/web-cli", wait_until="networkidle")
        page.wait_for_timeout(900)
        facts["alias_url"] = page.url
        facts["alias_h1"] = page.locator("h1").first.inner_text(timeout=3000) if page.locator("h1").count() else page.locator("body").inner_text()[:120]

        # 3) 搜索：按钮在、能打开、能搜到内容
        page.goto(f"{BASE}/", wait_until="networkidle")
        page.wait_for_timeout(500)
        facts["search_button"] = page.locator(".VPNavBarSearch button, .VPNavBarSearch .DocSearch-Button").count()
        page.locator(".VPNavBarSearch button, .VPNavBarSearch .DocSearch-Button").first.click()
        page.wait_for_timeout(400)
        page.keyboard.type("playwright")
        page.wait_for_timeout(1200)
        facts["search_hits"] = page.locator(".VPLocalSearchBox .result, .VPLocalSearchBox a").count()
        page.screenshot(path=str(OUT / "fix-search.png"))
        page.keyboard.press("Escape")

        # 4) 侧栏章节名与 h1 一致 + 知识库索引可达
        page.goto(f"{BASE}/chapters/ch01", wait_until="networkidle")
        page.wait_for_timeout(400)
        facts["ch01_h1"] = page.locator("h1").first.inner_text()
        facts["sidebar_has_full_title"] = page.locator("a", has_text="环境、第一个程序与基础语法").count()
        page.goto(f"{BASE}/kb/", wait_until="networkidle")
        facts["kb_index_h1"] = page.locator("h1").first.inner_text()

        # 5) 技能页能跳手册、手册页能回技能页
        page.goto(f"{BASE}/skills/shenle-web-cli", wait_until="networkidle")
        page.wait_for_timeout(400)
        facts["skill_to_kb"] = page.locator("a[href*='/kb/skills/']").count()
        facts["zip_text"] = [t for t in page.locator("a").all_inner_texts() if "zip" in t.lower()][:3]

        # 6) 尾斜杠自动纠正：/chapters/ch01/ → /chapters/ch01
        page.goto(f"{BASE}/chapters/ch01/", wait_until="networkidle")
        page.wait_for_timeout(800)
        facts["trailing_slash_url"] = page.url

        # 7) playground：按钮与说明文案
        page.goto(f"{BASE}/labs/playground", wait_until="networkidle")
        page.wait_for_timeout(400)
        facts["playground_has_hint"] = page.locator(".pg-hint").count()

        browser.close()

    print(json.dumps(facts, ensure_ascii=False, indent=2))
    (OUT / "fix-facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
