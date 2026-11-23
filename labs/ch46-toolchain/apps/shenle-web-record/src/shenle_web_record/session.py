"""RecorderSession: headed browser + SNAP button + capture loop.

Uses Playwright's *async* API because the sync API deadlocks when
`page.evaluate` / `page.screenshot` are called from inside an
`expose_function` callback (the sync event loop cannot service a second
request while the first is in flight).
"""
from __future__ import annotations

import asyncio
import json
import sys
import traceback
from pathlib import Path

from shenle_web_record.paths import (
    generate_batch_id,
    make_batch_dir,
    next_seq,
)

SNAP_BUTTON_JS_PATH = (
    Path(__file__).parent / "assets" / "snap_button.js"
)
SNAP_FN_NAME = "__shenle_snap__"


class RecorderSession:
    def __init__(self, url: str, output_root: str) -> None:
        self.url = url
        self.output_root = output_root
        self._batch_id = generate_batch_id()
        self._batch_dir = make_batch_dir(output_root, self._batch_id)
        self._seq = next_seq(self._batch_dir)
        self._initial_seq = self._seq
        self._browser = None
        self._page = None

    async def run(self) -> int:
        """Launch headed Chromium, attach button, block until browser closes."""
        from playwright.async_api import async_playwright

        snap_js = SNAP_BUTTON_JS_PATH.read_text(encoding="utf-8")

        try:
            async with async_playwright() as p:
                self._browser = await p.chromium.launch(headless=False)
                try:
                    self._page = await self._browser.new_page()
                    await self._page.add_init_script(snap_js)
                    await self._page.expose_function(SNAP_FN_NAME, self._on_snap)
                    try:
                        await self._page.goto(
                            self.url, wait_until="domcontentloaded", timeout=60_000
                        )
                    except Exception as exc:
                        print(
                            f"[shenle-web-record] navigation failed ({exc}); "
                            f"browser remains open",
                            file=sys.stderr,
                        )
                    # Block until browser is closed by user.
                    #
                    # On Windows, killing the chromium child from outside (or
                    # closing the browser window via the WM) does not reliably
                    # flip Playwright's `is_connected()` to False or fire the
                    # `disconnected` event — the Python driver keeps believing
                    # the browser is alive. So we also poll our own descendant
                    # chrome.exe processes via psutil and `os._exit(0)` as soon
                    # as none remain. That bypasses Playwright's hung cleanup.
                    import os
                    try:
                        import psutil
                        _HAS_PSUTIL = True
                    except ImportError:
                        psutil = None  # type: ignore
                        _HAS_PSUTIL = False
                        print(
                            "[shenle-web-record] psutil not installed; falling "
                            "back to disconnected-event only (browser close "
                            "may not auto-exit on Windows). "
                            "Install with: pip install psutil",
                            file=sys.stderr,
                        )

                    disconnected = asyncio.Event()
                    self._browser.on("disconnected", lambda _b: disconnected.set())
                    my_pid = os.getpid()

                    def _chromium_alive() -> bool:
                        if not _HAS_PSUTIL:
                            return self._browser.is_connected()
                        try:
                            for c in psutil.Process(my_pid).children(recursive=True):
                                if c.name().lower().startswith("chrome"):
                                    return True
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        return False

                    try:
                        while True:
                            if disconnected.is_set():
                                break
                            if not _chromium_alive():
                                # All chrome.exe gone → user closed the browser.
                                # Skip Playwright cleanup (which would hang) and
                                # exit the process directly.
                                os._exit(0)
                            try:
                                await asyncio.wait_for(
                                    disconnected.wait(), timeout=0.5
                                )
                            except asyncio.TimeoutError:
                                pass
                    except KeyboardInterrupt:
                        os._exit(0)
                finally:
                    try:
                        if self._browser.is_connected():
                            await self._browser.close()
                    except Exception:
                        pass
        except Exception as exc:
            msg = str(exc)
            hint = ""
            lower = msg.lower()
            if (
                "executable doesn't exist" in lower
                or "browser was not found" in lower
                or ("chromium" in lower and "found" in lower)
            ):
                hint = "\n  → run: playwright install chromium"
            print(
                f"[shenle-web-record] browser session ended: {exc}{hint}",
                file=sys.stderr,
            )
            return 1

        print(f"[shenle-web-record] batch dir: {self._batch_dir}")
        print(f"[shenle-web-record] captures  : {self._seq - self._initial_seq}")
        return 0

    async def _on_snap(self, payload: dict | None = None) -> dict:
        """Handle one SNAP click: hide panel, screenshot viewport, dump DOM, restore."""
        page = self._page
        if page is None:
            return {"ok": False, "error": "no page"}

        # ---- Validate and unpack payload ----
        payload = payload or {}
        module = (payload.get("module") or "").strip()
        func = (payload.get("func") or "").strip()
        desc = (payload.get("desc") or "").strip()
        if not module or not func:
            return {"ok": False, "error": "模块和功能必填"}

        # ---- Compute target directory under batch root ----
        # module may contain "-" to create multi-level folders, e.g.
        # "电商-用户中心" → ["电商", "用户中心"].
        module_parts = [p.strip() for p in module.split("-") if p.strip()]
        if not module_parts:
            return {"ok": False, "error": "模块不能为空"}
        func_parts = [func]  # func is treated as a single folder name
        target_dir = self._batch_dir.joinpath(*module_parts, *func_parts)
        img_dir = target_dir / "img"
        json_dir = target_dir / "json"
        img_dir.mkdir(parents=True, exist_ok=True)
        json_dir.mkdir(parents=True, exist_ok=True)

        new_seq = self._seq
        seq_str = f"{new_seq:03d}"
        img_path = img_dir / f"screenshot_{seq_str}.png"
        json_path = json_dir / f"dom_{seq_str}.json"
        img_relpath = f"img/screenshot_{seq_str}.png"

        # ---- Capture ----
        try:
            await page.evaluate(
                "document.getElementById('__shenle_panel__')?.classList.add('shenle-hidden')"
            )
            await page.screenshot(path=str(img_path), full_page=False)
            dom = await page.locator("body").aria_snapshot()
            await page.evaluate(
                "document.getElementById('__shenle_panel__')?.classList.remove('shenle-hidden')"
            )
        except Exception as exc:
            print(traceback.format_exc(), file=sys.stderr)
            return {"ok": False, "error": str(exc)}

        payload_out = {
            "content": dom,
            "img": img_relpath,
            "module": module,
            "func": func,
            "desc": desc,
        }
        json_path.write_text(
            json.dumps(payload_out, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._seq = new_seq + 1
        print(f"[shenle-web-record] saved {img_path} + {json_path}")
        return {"ok": True, "seq": seq_str}