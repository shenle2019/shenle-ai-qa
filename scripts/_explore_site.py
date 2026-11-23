"""Read-only exploratory pass over the public site, as a first-time visitor.

Records objective facts only (status, titles, console errors, overflow, click outcomes);
no form posts, no data writes. Screenshots land in docs/explore/<slug>/.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://shenle2019.github.io/shenle-ai-qa"
OUT = Path("docs/explore/2026-11-23-site")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "shots").mkdir(exist_ok=True)

sessions: list[dict] = []


def slug(path: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", path.strip("/")) or "home"
    return s[:60]


def visit(pg, path: str, note: str = "", shot: bool = False, full: bool = False) -> dict:
    errors: list[str] = []
    failed: list[str] = []
    pg.on("console", lambda m: errors.append(f"{m.type}: {m.text[:120]}") if m.type == "error" else None)
    pg.on("requestfailed", lambda r: failed.append(f"{r.url[:90]} {r.failure}"))
    resp = pg.goto(BASE + path, wait_until="load", timeout=45000)
    pg.wait_for_timeout(350)
    info = {
        "path": path,
        "note": note,
        "status": resp.status if resp else None,
        "title": pg.title(),
        "h1": (pg.locator("h1").first.inner_text() if pg.locator("h1").count() else ""),
        "console": errors[:4],
        "failed": failed[:4],
        "chars": len(pg.inner_text("body")),
        "toc": pg.locator(".VPDocOutlineItem, .VPDocAsideOutline").count(),
        "pager": pg.locator(".pager-link").count(),
        "overflow": pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"),
    }
    if shot:
        pg.screenshot(path=str(OUT / "shots" / f"{slug(path)}.png"), full_page=full)
    sessions.append(info)
    (OUT / "sessions.json").write_text(
        json.dumps(sessions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{info['status']} {path:44s} {info['title'][:34]:34s} h1={info['h1'][:18]:18s} err={len(info['console'])} of={info['overflow']}")
    return info


def links_on(pg) -> list[str]:
    hrefs = pg.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
    out = []
    for h in hrefs:
        if not h or h.startswith("#") or h.startswith("http") or h.startswith("mailto"):
            continue
        out.append(h)
    return out


def main() -> None:
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})

        visit(pg, "/", shot=True, full=True)
        seed = ["/chapters/", "/labs/", "/skills/", "/kb/skills/", "/kb/interview-api", "/kb/rules"]
        for s in seed:
            visit(pg, s, shot=True)
        found = set(seed)
        found.add("/")
        for s in seed:
            pg.goto(BASE + s, wait_until="load")
            for h in links_on(pg):
                if h.startswith("/shenle-ai-qa/"):
                    h = h[len("/shenle-ai-qa"):]
                if h.startswith("/") and not h.startswith("//"):
                    found.add(h.split("#")[0].rstrip("/") or "/")

        want_chapters = [f"/chapters/ch{i:02d}" for i in (1, 2, 7, 8, 16, 24, 32, 40, 43, 46)]
        want_labs = sorted(x for x in found if x.startswith("/labs/") and x != "/labs/")
        want_kb = sorted(x for x in found if x.startswith("/kb/") and x != "/kb/skills/")
        plan = want_chapters + want_labs[:6] + want_kb[:4]
        for path in plan:
            visit(pg, path, shot=path in ("/chapters/ch01", "/labs/playground"))

        # 404 / guessed URLs a first-time visitor would try
        for guess in ["/chapters/ch99", "/skills/web-cli", "/kb/skills/web-cli", "/chapters",
                      "/kb", "/skills/shenle-web-cli/", "/lab/", "/kb/skills/index"]:
            visit(pg, guess, note="guessed url", shot=guess == "/skills/web-cli", full=False)

        # pager at both ends
        visit(pg, "/chapters/ch01")
        nxt = pg.locator(".pager-link.next")
        print("ch01 next:", nxt.count(), nxt.first.inner_text().replace("\n", " ") if nxt.count() else "-")
        visit(pg, "/chapters/ch46")
        print("ch46 next:", pg.locator(".pager-link.next").count())

        # dark mode toggle
        visit(pg, "/chapters/ch01", shot=False)
        toggles = pg.locator(".VPSwitch").count()
        print("theme toggles:", toggles)
        if toggles:
            before = pg.evaluate("document.documentElement.className")
            pg.locator(".VPSwitch").first.click()
            pg.wait_for_timeout(400)
            after = pg.evaluate("document.documentElement.className")
            print("theme class:", repr(before), "->", repr(after))
            pg.screenshot(path=str(OUT / "shots" / "dark-ch01.png"))

        # keyboard focus visibility on nav
        pg.goto(BASE + "/", wait_until="load")
        pg.keyboard.press("Tab")
        pg.keyboard.press("Tab")
        foc = pg.evaluate("""() => {
            const el = document.activeElement;
            const s = getComputedStyle(el);
            return {tag: el.tagName, text: (el.innerText||'').slice(0,20), outline: s.outlineWidth + ' ' + s.outlineStyle};
        }""")
        print("focus:", json.dumps(foc, ensure_ascii=False))

        # mobile pass
        m = b.new_page(viewport={"width": 390, "height": 844})
        for path in ["/", "/chapters/ch01", "/skills/", "/kb/skills/"]:
            m.goto(BASE + path, wait_until="load")
            m.wait_for_timeout(300)
            ov = m.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            print(f"mobile {path:16s} overflow={ov}")
            m.screenshot(path=str(OUT / "shots" / f"m-{slug(path)}.png"), full_page=False)

        # playground: run once, measure
        m.close()
        pg.goto(BASE + "/labs/playground", wait_until="load")
        for det in pg.locator("details").all():
            if not det.get_attribute("open"):
                det.locator("summary").click()
        pg.wait_for_timeout(300)
        run = pg.locator("button.pg-btn", has_text="运行")
        print("details opened, run buttons:", run.count())
        if run.count():
            t0 = datetime.now()
            run.first.click()
            try:
                pg.wait_for_function("() => document.body.innerText.includes('总分')", timeout=90000)
                print("playground output seconds:", round((datetime.now() - t0).total_seconds(), 1))
            except Exception as exc:  # noqa: BLE001
                print("playground timeout", type(exc).__name__)
            pg.screenshot(path=str(OUT / "shots" / "playground-ran.png"))

        b.close()

    (OUT / "sessions.json").write_text(json.dumps(sessions, ensure_ascii=False, indent=2), encoding="utf-8")
    bad = [s for s in sessions if s["status"] and s["status"] >= 400]
    print("visited", len(sessions), ">=400:", [(s["path"], s["status"]) for s in bad])
    print("with console errors:", [(s["path"], s["console"][:1]) for s in sessions if s["console"]][:6])


if __name__ == "__main__":
    main()
