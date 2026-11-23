"""Third pass: playground completion, the empty search slot, stale copy."""

from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://shenle2019.github.io/shenle-ai-qa"
OUT = Path("docs/explore/2026-11-23-site/shots")


def main() -> None:
    facts: dict[str, object] = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        logs: list[str] = []
        pg.on("console", lambda m: logs.append(f"{m.type}: {m.text[:150]}"))

        pg.goto(BASE + "/", wait_until="load")
        facts["nav_search_html"] = pg.eval_on_selector(".VPNavBarSearch", "e => e.outerHTML.slice(0,300)") if pg.locator(".VPNavBarSearch").count() else "none"
        facts["sidebar_skill_count_copy"] = [
            t for t in pg.eval_on_selector_all(".VPSidebarItem .text", "els => els.map(e => e.innerText.trim())")
            if "技能" in t or "Skills" in t
        ]

        # playground with a long wait
        pg.goto(BASE + "/labs/playground", wait_until="load")
        for det in pg.locator("details").all():
            if not det.get_attribute("open"):
                det.locator("summary").click()
        pg.wait_for_timeout(300)
        t0 = time.time()
        pg.locator("button.pg-btn", has_text="运行").first.click()
        done = False
        while time.time() - t0 < 75:
            txt = pg.inner_text("body")
            if "运行时就绪" in txt or "总分" in txt.split("点「运行」")[-1]:
                done = True
                break
            pg.wait_for_timeout(2000)
        facts["playground_seconds"] = round(time.time() - t0, 1) if done else None
        facts["playground_console"] = logs[-6:]
        facts["playground_tail"] = [ln for ln in pg.inner_text("body").splitlines() if ln.strip()][-6:]
        pg.screenshot(path=str(OUT / "playground-final.png"))

        # kb index: how many skills are listed vs how the sidebar describes them
        pg.goto(BASE + "/kb/skills/", wait_until="load")
        facts["kb_index_rows"] = pg.locator("table tr").count()
        facts["kb_index_skill_links"] = pg.locator("table a[href*='/kb/skills/']").count()
        b.close()
    print(json.dumps(facts, ensure_ascii=False, indent=2))
    (Path("docs/explore/2026-11-23-site/facts3.json")).write_text(
        json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
