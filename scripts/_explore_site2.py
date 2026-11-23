"""Second, targeted read-only pass: the things a first-time visitor trips over."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://shenle2019.github.io/shenle-ai-qa"
OUT = Path("docs/explore/2026-11-23-site/shots")


def main() -> None:
    facts: dict[str, object] = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})

        # 1) 404 page wording
        pg.goto(BASE + "/chapters/ch99", wait_until="load")
        pg.wait_for_timeout(300)
        facts["404_text"] = pg.inner_text(".NotFound, #app").replace("\n", " | ")[:220]
        facts["404_links"] = pg.eval_on_selector_all("#app a", "els => els.map(e => e.innerText.trim()).filter(Boolean).slice(0,8)")
        pg.screenshot(path=str(OUT / "s404.png"))

        # 2) trailing slash on a skills page
        pg.goto(BASE + "/skills/shenle-web-cli", wait_until="load")
        pg.wait_for_timeout(200)
        good = {"title": pg.title(), "h1": pg.locator("h1").first.inner_text() if pg.locator("h1").count() else "", "words": len(pg.inner_text("body"))}
        pg.goto(BASE + "/skills/shenle-web-cli/", wait_until="load")
        pg.wait_for_timeout(200)
        bad = {"title": pg.title(), "h1": pg.locator("h1").first.inner_text() if pg.locator("h1").count() else "", "words": len(pg.inner_text("body"))}
        facts["no_slash"] = good
        facts["with_slash"] = bad
        pg.screenshot(path=str(OUT / "trailing-slash.png"))

        home = b.new_page(viewport={"width": 1440, "height": 900})
        # 3) is there any search affordance?
        home.goto(BASE + "/", wait_until="load")
        facts["search_ui"] = {
            "DocSearch": home.locator(".DocSearch").count(),
            "VPNavBarSearch": home.locator(".VPNavBarSearch").count(),
            "inputs": home.locator("input").count(),
            "search_buttons": home.locator("button[aria-label*='搜索'], button[aria-label*='Search']").count(),
        }
        # 4) what are the two switches
        facts["switches"] = home.eval_on_selector_all(
            ".VPSwitch", "els => els.map(e => ({cls: e.className, label: (e.getAttribute('aria-label')||e.title||''), parent: e.parentElement.className}))"
        )
        # 5) last-updated format
        home.goto(BASE + "/chapters/ch01", wait_until="load")
        lu = home.locator(".VPLastUpdated")
        facts["last_updated"] = lu.first.inner_text() if lu.count() else "none"

        # 6) playground really runs?
        home.goto(BASE + "/labs/playground", wait_until="load")
        for det in home.locator("details").all():
            if not det.get_attribute("open"):
                det.locator("summary").click()
        home.wait_for_timeout(300)
        before = home.inner_text(".pg-out, pre")
        home.locator("button.pg-btn", has_text="运行").first.click()
        home.wait_for_timeout(12000)
        out_text = home.eval_on_selector_all(".pg-out, .pg-console, pre", "els => els.map(e => e.innerText).join('\\n')")
        facts["playground_before_len"] = len(before)
        facts["playground_after"] = [ln for ln in out_text.splitlines() if ln.strip()][-6:]
        home.screenshot(path=str(OUT / "playground-after.png"))

        # 7) mobile nav opens?
        m = b.new_page(viewport={"width": 390, "height": 844})
        m.goto(BASE + "/chapters/ch01", wait_until="load")
        btn = m.locator(".VPNavBarHamburger")
        facts["hamburger"] = btn.count()
        if btn.count():
            btn.first.click()
            m.wait_for_timeout(400)
            facts["mobile_menu_open"] = m.locator(".VPNavScreen").is_visible()
            m.screenshot(path=str(OUT / "m-menu.png"))

        # 8) home CTA targets
        m.close()
        home.goto(BASE + "/", wait_until="load")
        facts["home_ctas"] = home.eval_on_selector_all(
            ".VPButton, .actions a", "els => els.map(e => ({t: e.innerText.trim(), h: e.getAttribute('href')})).slice(0,6)"
        )
        # 9) does the chapter list mention counts that match reality?
        home.goto(BASE + "/chapters/", wait_until="load")
        facts["chapters_index_text"] = home.inner_text("main")[:400].replace("\n", " | ")
        b.close()
    print(json.dumps(facts, ensure_ascii=False, indent=2))
    (Path("docs/explore/2026-11-23-site/facts2.json")).write_text(
        json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
