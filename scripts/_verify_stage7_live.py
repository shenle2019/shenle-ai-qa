"""Verify the deployed site after stage 7 went live."""

import json
import time
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

BASE = "https://shenle2019.github.io/shenle-ai-qa"
CHUNKS = [f"/chapters/ch{n}" for n in range(47, 55)]


def head(url):
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            return resp.status, resp.headers.get("content-type", ""), len(body), body
    except urllib.error.HTTPError as exc:
        return exc.code, "", 0, b""


def main():
    report = {}
    for path in ["/", "/labs/", "/labs/playground"] + CHUNKS:
        status, ctype, size, body = head(BASE + path)
        text = body.decode("utf-8", "ignore") if body else ""
        report[path] = {"status": status, "size": size}

    status, ctype, size, body = head(BASE + "/pyodide/v0.26.4/pyodide.asm.wasm")
    report["wasm"] = {"status": status, "type": ctype, "size": size}

    status, _, size, body = head(BASE + "/")
    home = body.decode("utf-8", "ignore")
    report["home_has_570"] = "570" in home
    report["home_has_stage7"] = "第七阶段" in home

    status, _, size, body = head(BASE + "/labs/")
    labs = body.decode("utf-8", "ignore")
    report["labs_has_stage7"] = "第七阶段" in labs
    report["labs_has_54"] = "ch54" in labs

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        page.goto(BASE + "/labs/playground", wait_until="networkidle")
        page.wait_for_timeout(600)

        details = page.locator("details")
        if details.count():
            details.first.locator("summary").click()
            page.wait_for_timeout(300)

        started = time.time()
        page.get_by_role("button", name="运行").first.click()
        out = ""
        for _ in range(60):
            page.wait_for_timeout(1000)
            out = page.locator("pre, .console, .out, .output").all_inner_texts()
            joined = "\n".join(out)
            if "总分" in joined or "Traceback" in joined:
                break
        elapsed = round(time.time() - started, 1)
        page.screenshot(path="docs/shots/live-playground-stage7.png")
        report["playground_elapsed_s"] = elapsed
        report["playground_output_has_result"] = any("总分" in t for t in out)
        report["playground_errors"] = page.evaluate("() => window.__pyodideShared ? 'shared-ok' : 'no-store'")

        page.goto(BASE + "/chapters/ch52", wait_until="networkidle")
        page.wait_for_timeout(400)
        page.evaluate(
            "() => { const h = [...document.querySelectorAll('h2')].find(x => x.textContent.includes('5.')); h && h.scrollIntoView(); }"
        )
        page.wait_for_timeout(300)
        page.screenshot(path="docs/shots/live-ch52-stage7.png")
        report["ch52_title"] = page.title()
        browser.close()

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
