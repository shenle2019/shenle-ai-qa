"""navigate / screenshot / click / input / scroll / get / batch / 原始坐标 等命令实现。

所有命令以 `[OK] ...` 或 `[FAIL] ...` 单行输出 + exit 0/1 结束，
方便上层（人 / AI）parse。
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import struct
import sys
import tempfile
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from .ai import (
    AIConfigError,
    AIRuntimeError,
    ask_vision_for_bbox_batch_norm_async,
    ask_vision_for_bbox_norm_async,
    ask_vision_describe_async,
    load_config,
)
from .browser_session import connect_page
from .errors import CliError


# ---------------------------------------------------------------------------
# 截图 + 尺寸探测（Phase 4 起 AI 截图走 JPEG q=80，~3x 小于 PNG）


async def _take_temp_screenshot(page) -> tuple[Path, int, int]:
    """截当前 viewport 到临时 JPEG，返回 (path, w, h)。调用方负责 unlink。"""
    fd, path_str = tempfile.mkstemp(suffix=".jpg", prefix="shenle-vision-")
    os.close(fd)
    shot = Path(path_str)
    await page.screenshot(path=str(shot), type="jpeg", quality=80)
    w, h = _jpeg_dimensions(shot)
    return shot, w, h


def _png_dimensions(path: Path) -> tuple[int, int]:
    try:
        with open(path, "rb") as f:
            f.read(16)  # 8B sig + 4B len + 4B 'IHDR'
            w, h = struct.unpack(">II", f.read(8))
        return w, h
    except (OSError, struct.error):
        return (0, 0)


def _jpeg_dimensions(path: Path) -> tuple[int, int]:
    """从 JPEG 的 SOF0/SOF2 marker 读宽高。失败返回 (0, 0)。"""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return (0, 0)
    if data[:2] != b"\xff\xd8":
        return (0, 0)
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            break
        marker = data[i + 1]
        # SOF markers except DHT(0xC4)/DAC(0xCC)/JPG(0xC8)
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h = (data[i + 5] << 8) | data[i + 6]
            w = (data[i + 7] << 8) | data[i + 8]
            return w, h
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7 or marker == 0x01:
            i += 2
            continue
        length = (data[i + 2] << 8) | data[i + 3]
        i += 2 + length
    return (0, 0)


# ---------------------------------------------------------------------------
# 弹窗处理（Playwright 的 alert/confirm/prompt）


async def _handle_dialog(dialog, action: str, prompt_text: str) -> None:
    """对一个 Dialog 对象执行 accept / dismiss，并打 [DIALOG] 行。"""
    dtype = dialog.type
    msg = dialog.message
    prefix = f"[DIALOG] type={dtype} message={msg!r}"
    try:
        if dtype == "prompt":
            text = prompt_text if prompt_text else (dialog.default_value or "")
            await dialog.accept(text)
            print(f"{prefix} → accept text={text!r}", flush=True)
        elif action == "accept":
            await dialog.accept()
            print(f"{prefix} → accept", flush=True)
        elif action == "dismiss":
            await dialog.dismiss()
            print(f"{prefix} → dismiss", flush=True)
        else:
            await dialog.dismiss()
            print(f"{prefix} → dismiss (未知 action={action!r})", flush=True)
    except Exception as e:
        print(f"{prefix} → 处理失败：{e}", file=sys.stderr, flush=True)


async def _run_with_dialog(page, args, fn):
    """执行 fn(page)；如果 args.on_dialog 存在，期间用 page.expect_event 同步接 dialog。

    fn 是 async def fn(page) -> None；返回 None 即可（结果自己打印）。
    """
    action = getattr(args, "on_dialog", None)
    prompt_text = getattr(args, "prompt_text", None) or ""
    if not action:
        await fn(page)
        return
    # page.expect_event('dialog') 会一直等到 dialog 出现或 timeout
    # 我们包住 fn 的执行：执行期间任何 dialog 都会被 capture
    try:
        async with page.expect_event("dialog", timeout=2000) as info:
            await fn(page)
        dialog = await info.value  # info.value 是 coroutine
        # 同步拿到 dialog 后立即处理；这时 page 还活着，Playwright 不会 race
        await _handle_dialog(dialog, action, prompt_text)
    except Exception as e:
        # expect_event 超时（无 dialog 触发）或其它异常
        # 如果 fn 自己抛异常，让上层正常处理；如果是 TimeoutError 静默
        if "Timeout" in type(e).__name__:
            # 无 dialog——OK，fn 早就执行完了
            await fn(page) if False else None  # fn 已经跑过
        else:
            raise


@asynccontextmanager
async def _with_dialog_handler(page, args):
    """兼容旧调用的占位——实际接 dialog 的逻辑在 _run_with_dialog 里。

    为了不破坏 7 个已有调用点，这里 yield 一个 dummy；
    真正的 dialog 处理走 _run_with_dialog。
    """
    yield


# ---------------------------------------------------------------------------
# navigate


_URL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://")


async def cmd_navigate(args) -> int:
    url = args.url
    if not _URL_SCHEME.match(url):
        url = "https://" + url

    title = ""

    async def _action(page):
        nonlocal title
        try:
            await page.set_viewport_size({"width": 1440, "height": 900})
        except Exception:
            pass
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        title = await page.title()

    try:
        async with connect_page(port=getattr(args, "port", None)) as page:
            await _run_with_dialog(page, args, _action)
    except Exception as e:
        print(f"[FAIL] navigate: {url} - {e}")
        return 1

    print(f'[OK] navigate: {url} → title="{title}"')
    return 0


# ---------------------------------------------------------------------------
# screenshot（用户视角的截图；Phase 4 加 JPEG 支持）


async def cmd_screenshot(args) -> int:
    out = Path(args.path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    fmt = (args.format or "auto").lower()
    if fmt == "auto":
        suf = out.suffix.lower()
        fmt = "jpeg" if suf in (".jpg", ".jpeg") else "png"

    async with connect_page(port=getattr(args, "port", None)) as page:
        if fmt == "jpeg":
            await page.screenshot(
                path=str(out), type="jpeg", quality=args.quality or 85
            )
            w, h = _jpeg_dimensions(out)
        else:
            await page.screenshot(path=str(out), type="png")
            w, h = _png_dimensions(out)

    print(f"[OK] screenshot: {out} ({w}x{h}) [{fmt}]")
    return 0


# ---------------------------------------------------------------------------
# click / input 共用


async def _locate_via_vision(
    page, cfg, description: str, debug_mark_path: Path | None = None,
) -> tuple[int, int, list[int], list[int], int, int]:
    """截当前 viewport → AI 返回 0-1000 bbox → 换算成像素中心。

    返回 (cx_px, cy_px, bbox_1000, bbox_px, img_w, img_h)。
    debug_mark_path 给出后，把带红框的标注图存到这个路径。
    """
    shot, img_w, img_h = await _take_temp_screenshot(page)
    bbox_1000: list[int] | None = None
    try:
        bbox_1000 = await ask_vision_for_bbox_norm_async(cfg, shot, description)
        if not bbox_1000:
            raise AIRuntimeError("AI 返回空 bbox")
        bbox_px = _bbox_1000_to_pixel(bbox_1000, img_w, img_h)
        cx, cy = _bbox_center(bbox_px)
    finally:
        if debug_mark_path is not None and bbox_1000 is not None:
            try:
                _save_marked_image(shot, [bbox_1000], debug_mark_path)
            except Exception as e:
                print(f"[DEBUG] 保存标注图失败：{e}", file=sys.stderr)
        try:
            shot.unlink()
        except OSError:
            pass

    if not (0 <= cx <= img_w and 0 <= cy <= img_h):
        raise AIRuntimeError(
            f"AI 坐标 ({cx}, {cy}) 超出截图 {img_w}x{img_h}"
        )
    return cx, cy, bbox_1000, bbox_px, img_w, img_h


async def _locate_bbox_via_vision(
    page, cfg, description: str, debug_mark_path: Path | None = None,
) -> tuple[list[int], list[int], int, int]:
    """截当前 viewport → AI 返回 0-1000 bbox → 换算成像素 bbox。

    返回 (bbox_1000, bbox_px, img_w, img_h)。
    """
    shot, img_w, img_h = await _take_temp_screenshot(page)
    bbox_1000: list[int] | None = None
    try:
        bbox_1000 = await ask_vision_for_bbox_norm_async(cfg, shot, description)
        if not bbox_1000:
            raise AIRuntimeError("AI 返回空 bbox")
        bbox_px = _bbox_1000_to_pixel(bbox_1000, img_w, img_h)
    finally:
        if debug_mark_path is not None and bbox_1000 is not None:
            try:
                _save_marked_image(shot, [bbox_1000], debug_mark_path)
            except Exception as e:
                print(f"[DEBUG] 保存标注图失败：{e}", file=sys.stderr)
        try:
            shot.unlink()
        except OSError:
            pass

    if bbox_px[0] < 0 or bbox_px[1] < 0 or bbox_px[2] > img_w or bbox_px[3] > img_h:
        raise AIRuntimeError(
            f"AI bbox {bbox_px} 超出截图 {img_w}x{img_h}"
        )
    if bbox_px[2] - bbox_px[0] < 5 or bbox_px[3] - bbox_px[1] < 5:
        raise AIRuntimeError(
            f"AI bbox {bbox_px} 太小（至少 5×5）"
        )
    return bbox_1000, bbox_px, img_w, img_h


def _bbox_1000_to_pixel(bbox_1000: list[int], img_w: int, img_h: int) -> list[int]:
    """[xmin,ymin,xmax,ymax] 0-1000 → 真实像素。"""
    return [
        int(bbox_1000[0] * img_w / 1000),
        int(bbox_1000[1] * img_h / 1000),
        int(bbox_1000[2] * img_w / 1000),
        int(bbox_1000[3] * img_h / 1000),
    ]


def _bbox_center(bbox: list[int]) -> tuple[int, int]:
    return (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2


def _save_marked_image(shot_path: Path, bboxes_1000: list[list[int]], output_path: Path) -> None:
    """在截图上画红框（多 bbox 用 #1 #2 编号），存到 output_path。

    需要 Pillow。失败抛回让调用方打印错误。
    """
    from PIL import Image, ImageDraw

    img = Image.open(shot_path)
    draw = ImageDraw.Draw(img)
    sx = img.width / 1000.0
    sy = img.height / 1000.0
    for i, bbox in enumerate(bboxes_1000):
        bbox_px = [
            int(bbox[0] * sx), int(bbox[1] * sy),
            int(bbox[2] * sx), int(bbox[3] * sy),
        ]
        draw.rectangle(bbox_px, outline="red", width=3)
        if len(bboxes_1000) > 1:
            label = f"#{i+1}"
            ty = max(bbox_px[1] - 18, 2)
            draw.text((bbox_px[0] + 2, ty), label, fill="red")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


async def _clear_then_type(page, text: str) -> None:
    """输入前先清空（Ctrl+A + Delete），再 insert_text。

    对 input / input_at / batch input 都适用。
    """
    await page.keyboard.press("Control+a")
    await asyncio.sleep(0.05)
    await page.keyboard.press("Delete")
    await asyncio.sleep(0.05)
    await page.keyboard.insert_text(text)


def _debug_mark_path(args, cmd_name: str) -> Path | None:
    """如果 --debug 在，返回一条标注图路径；否则 None。"""
    if not getattr(args, "debug", False):
        return None
    ts = int(time.time() * 1000)
    return (Path.cwd() / f"shenle-debug-{cmd_name}-{ts}.png").resolve()


def _debug_print_ai_result(
    desc: str, bbox_1000: list[int], bbox_px: list[int],
    img_w: int, img_h: int,
) -> None:
    """把 AI 坐标结果打到 stderr（--debug 时）。"""
    sx = img_w / 1000.0
    sy = img_h / 1000.0
    print(f"[DEBUG] AI 描述: {desc}", file=sys.stderr)
    print(f"[DEBUG] 截图尺寸: {img_w}x{img_h}", file=sys.stderr)
    print(f"[DEBUG] AI 返回 (0-1000): {bbox_1000}", file=sys.stderr)
    print(f"[DEBUG] 缩放因子: x={sx:.3f}, y={sy:.3f}", file=sys.stderr)
    print(f"[DEBUG] bbox (像素): {bbox_px}", file=sys.stderr)
    cx, cy = _bbox_center(bbox_px)
    print(f"[DEBUG] 中心 (像素): ({cx}, {cy})", file=sys.stderr)


def _compose_desc(args) -> str:
    desc = args.description
    if getattr(args, "enhanced", None):
        desc = f"{args.description}（{args.enhanced}）"
    return desc


# ---------------------------------------------------------------------------
# click


async def cmd_click(args) -> int:
    desc = _compose_desc(args)
    captured: dict = {}
    post_shot = getattr(args, "post_shot", None)
    debug_path = _debug_mark_path(args, "click")

    async def _action(page):
        cx, cy, bbox_1000, bbox_px, img_w, img_h = await _locate_via_vision(
            page, cfg, desc, debug_path
        )
        captured.update(
            cx=cx, cy=cy, bbox_1000=bbox_1000, bbox_px=bbox_px,
            img_w=img_w, img_h=img_h,
        )
        await page.mouse.click(cx, cy)
        if post_shot:
            ps = Path(post_shot).resolve()
            ps.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(ps), full_page=False)

    try:
        cfg = load_config()
        async with connect_page(port=getattr(args, "port", None)) as page:
            await _run_with_dialog(page, args, _action)
    except CliError as e:
        print(f'[FAIL] click "{desc}": {e.message}')
        return 1
    except Exception as e:
        print(f'[FAIL] click "{desc}": {e}')
        return 1

    if debug_path and captured:
        _debug_print_ai_result(
            desc,
            captured.get("bbox_1000", []),
            captured.get("bbox_px", []),
            captured.get("img_w", 0),
            captured.get("img_h", 0),
        )
        print(f"[DEBUG] 标注图: {debug_path}", file=sys.stderr)

    cx, cy = captured.get("cx", 0), captured.get("cy", 0)
    if post_shot:
        print(f'[OK] click "{desc}": ({cx}, {cy}); 截图 → {Path(post_shot).resolve()}')
    else:
        print(f'[OK] click "{desc}": ({cx}, {cy})')
    return 0


# ---------------------------------------------------------------------------
# input


async def cmd_input(args) -> int:
    desc = _compose_desc(args)
    text = args.text
    captured: dict = {}
    post_shot = getattr(args, "post_shot", None)
    debug_path = _debug_mark_path(args, "input")

    async def _action(page):
        cx, cy, bbox_1000, bbox_px, img_w, img_h = await _locate_via_vision(
            page, cfg, desc, debug_path
        )
        captured.update(
            cx=cx, cy=cy, bbox_1000=bbox_1000, bbox_px=bbox_px,
            img_w=img_w, img_h=img_h,
        )
        await page.mouse.click(cx, cy)
        # 清空现有内容再输入
        await _clear_then_type(page, text)
        if post_shot:
            ps = Path(post_shot).resolve()
            ps.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(ps), full_page=False)

    try:
        cfg = load_config()
        async with connect_page(port=getattr(args, "port", None)) as page:
            await _run_with_dialog(page, args, _action)
    except CliError as e:
        print(f'[FAIL] input "{desc}" "{text}": {e.message}')
        return 1
    except Exception as e:
        print(f'[FAIL] input "{desc}" "{text}": {e}')
        return 1

    if debug_path and captured:
        _debug_print_ai_result(
            desc,
            captured.get("bbox_1000", []),
            captured.get("bbox_px", []),
            captured.get("img_w", 0),
            captured.get("img_h", 0),
        )
        print(f"[DEBUG] 标注图: {debug_path}", file=sys.stderr)

    cx, cy = captured.get("cx", 0), captured.get("cy", 0)
    if post_shot:
        print(f'[OK] input "{desc}" "{text}": ({cx}, {cy}); 截图 → {Path(post_shot).resolve()}')
    else:
        print(f'[OK] input "{desc}" "{text}": ({cx}, {cy})')
    return 0


# ---------------------------------------------------------------------------
# scroll


_SCROLL_DELTAS = {
    "up": (0, -400),
    "down": (0, 400),
    "left": (-400, 0),
    "right": (400, 0),
}
_SCROLL_ARROWS = {"up": "↑", "down": "↓", "left": "←", "right": "→"}


async def cmd_scroll(args) -> int:
    direction = args.direction
    count = max(1, args.count or 1)
    region = args.region
    bbox_str = ""
    post_shot = getattr(args, "post_shot", None)
    cfg = load_config() if region else None
    debug_path = _debug_mark_path(args, "scroll") if region else None

    async def _action(page):
        nonlocal bbox_str
        if region:
            bbox_1000, bbox_px, img_w, img_h = await _locate_bbox_via_vision(
                page, cfg, region, debug_path
            )
            cx, cy = _bbox_center(bbox_px)
            await page.mouse.move(cx, cy)
            bbox_str = (
                f' in "{region}" '
                f'bbox_1000={bbox_1000} bbox_px={bbox_px} center=({cx},{cy})'
            )
            if debug_path:
                _debug_print_ai_result(region, bbox_1000, bbox_px, img_w, img_h)
                print(f"[DEBUG] 标注图: {debug_path}", file=sys.stderr)

        dx, dy = _SCROLL_DELTAS[direction]
        for _ in range(count):
            await page.mouse.wheel(dx, dy)
            await asyncio.sleep(0.05)

        if post_shot:
            ps = Path(post_shot).resolve()
            ps.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(ps), full_page=False)

    try:
        async with connect_page(port=getattr(args, "port", None)) as page:
            await _run_with_dialog(page, args, _action)
    except CliError as e:
        print(f'[FAIL] scroll: {direction} - {e.message}')
        return 1
    except Exception as e:
        print(f'[FAIL] scroll: {direction} - {e}')
        return 1

    if post_shot:
        print(
            f'[OK] scroll: {direction} {_SCROLL_ARROWS[direction]} × {count}'
            f'{bbox_str}; 截图 → {Path(post_shot).resolve()}'
        )
    else:
        print(
            f'[OK] scroll: {direction} {_SCROLL_ARROWS[direction]} × {count}'
            f'{bbox_str}'
        )
    return 0


# ---------------------------------------------------------------------------
# get


async def cmd_get(args) -> int:
    area = args.description
    description_text = ""
    post_shot = getattr(args, "post_shot", None)

    async def _action(page):
        nonlocal description_text
        shot, _w, _h = await _take_temp_screenshot(page)
        try:
            description_text = await ask_vision_describe_async(cfg, shot, area)
        finally:
            try:
                shot.unlink()
            except OSError:
                pass
        if post_shot:
            ps = Path(post_shot).resolve()
            ps.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(ps), full_page=False)

    try:
        cfg = load_config()
        async with connect_page(port=getattr(args, "port", None)) as page:
            await _run_with_dialog(page, args, _action)
    except CliError as e:
        print(f'[FAIL] get "{area}": {e.message}', file=sys.stderr)
        return 1
    except Exception as e:
        print(f'[FAIL] get "{area}": {e}', file=sys.stderr)
        return 1

    if post_shot:
        print(f'[OK] get "{area}": 截图 → {Path(post_shot).resolve()}', file=sys.stderr)
    else:
        print(f'[OK] get "{area}"', file=sys.stderr)
    print(description_text)
    return 0


# ---------------------------------------------------------------------------
# url / title


async def _page_meta(page):
    return page.url, await page.title()


async def cmd_url(args) -> int:
    try:
        async with connect_page(port=getattr(args, "port", None)) as page:
            url, title = await _page_meta(page)
    except Exception as e:
        print(f"[FAIL] url: {e}")
        return 1
    if args.format == "json":
        print(json.dumps({"url": url, "title": title}, ensure_ascii=False))
    else:
        print(url)
    return 0


async def cmd_title(args) -> int:
    try:
        async with connect_page(port=getattr(args, "port", None)) as page:
            url, title = await _page_meta(page)
    except Exception as e:
        print(f"[FAIL] title: {e}")
        return 1
    if args.format == "json":
        print(json.dumps({"url": url, "title": title}, ensure_ascii=False))
    else:
        print(title)
    return 0


# ---------------------------------------------------------------------------
# 原始坐标命令（无 AI）


async def cmd_click_at(args) -> int:
    async def _action(page):
        await page.mouse.click(args.x, args.y)

    try:
        async with connect_page(port=getattr(args, "port", None)) as page:
            await _run_with_dialog(page, args, _action)
    except CliError as e:
        print(f"[FAIL] click-at: ({args.x},{args.y}) - {e.message}")
        return 1
    except Exception as e:
        print(f"[FAIL] click-at: ({args.x},{args.y}) - {e}")
        return 1
    print(f"[OK] click-at: ({args.x}, {args.y})")
    return 0


async def cmd_input_at(args) -> int:
    async def _action(page):
        await page.mouse.click(args.x, args.y)
        await page.keyboard.insert_text(args.text)

    try:
        async with connect_page(port=getattr(args, "port", None)) as page:
            await _run_with_dialog(page, args, _action)
    except CliError as e:
        print(
            f'[FAIL] input-at: ({args.x},{args.y}) "{args.text}" - {e.message}'
        )
        return 1
    except Exception as e:
        print(f'[FAIL] input-at: ({args.x},{args.y}) "{args.text}" - {e}')
        return 1
    print(f'[OK] input-at: ({args.x}, {args.y}) "{args.text}"')
    return 0


async def cmd_swipe_to(args) -> int:
    try:
        async with connect_page(port=getattr(args, "port", None)) as page:
            await page.mouse.move(args.x1, args.y1)
            await page.mouse.down()
            # steps=10 让浏览器收到一组中间事件，更像真人拖拽
            await page.mouse.move(args.x2, args.y2, steps=10)
            await page.mouse.up()
    except Exception as e:
        print(
            f"[FAIL] swipe-to: ({args.x1},{args.y1})→({args.x2},{args.y2}) - {e}"
        )
        return 1
    print(
        f"[OK] swipe-to: ({args.x1},{args.y1}) → ({args.x2},{args.y2})"
    )
    return 0


# ---------------------------------------------------------------------------
# batch — 一次截图 + 一次 AI 识别多个元素，按顺序执行


_BATCH_OP_KEYWORDS = {"click", "input", "click-at", "input-at"}


def _parse_batch_ops(tokens: list[str]) -> list[dict[str, Any]]:
    """把 batch 的剩余参数解析成操作列表。

    例：`["click", "登录", "input", "用户名::admin", "click-at", "100", "200"]`
    → `[{"type": "click", "desc": "登录"},
        {"type": "input", "desc": "用户名", "text": "admin"},
        {"type": "click_at", "x": 100, "y": 200}]`
    """
    ops: list[dict[str, Any]] = []
    current: tuple[str, list[str]] | None = None
    for tok in tokens:
        if tok in _BATCH_OP_KEYWORDS:
            if current is not None:
                ops.append(_finalize_batch_op(*current))
            current = (tok, [])
        else:
            if current is None:
                raise ValueError(
                    f"参数 {tok!r} 前面没有任何操作类型"
                    f"（应为 click / input / click-at / input-at）"
                )
            current[1].append(tok)
    if current is not None:
        ops.append(_finalize_batch_op(*current))
    if not ops:
        raise ValueError("batch 至少需要一个操作")
    return ops


def _finalize_batch_op(op_type: str, args: list[str]) -> dict[str, Any]:
    if op_type == "click":
        if not args:
            raise ValueError("click 需要元素描述")
        return {"type": "click", "desc": " ".join(args)}
    if op_type == "input":
        joined = " ".join(args)
        if "::" not in joined:
            raise ValueError(
                f"input 格式应为 <描述>::<文本>，得到：{joined!r}"
            )
        desc, text = joined.split("::", 1)
        if not desc.strip():
            raise ValueError(f"input 描述为空：{joined!r}")
        return {"type": "input", "desc": desc.strip(), "text": text}
    if op_type == "click-at":
        if len(args) != 2:
            raise ValueError(
                f"click-at 需要 2 个整数坐标，得到 {len(args)} 个：{args!r}"
            )
        try:
            x, y = int(args[0]), int(args[1])
        except ValueError as e:
            raise ValueError(f"click-at 坐标非整数：{args!r}") from e
        return {"type": "click_at", "x": x, "y": y}
    if op_type == "input-at":
        if len(args) < 3:
            raise ValueError(
                f"input-at 需要 x y 文本，得到：{args!r}"
            )
        try:
            x, y = int(args[0]), int(args[1])
        except ValueError as e:
            raise ValueError(f"input-at 坐标非整数：{args!r}") from e
        return {
            "type": "input_at",
            "x": x,
            "y": y,
            "text": " ".join(args[2:]),
        }
    raise ValueError(f"未知 batch 操作类型：{op_type}")


async def cmd_batch(args) -> int:
    try:
        ops = _parse_batch_ops(list(args.ops))
    except ValueError as e:
        print(f"[FAIL] batch: {e}")
        return 1

    cfg = load_config()
    debug = getattr(args, "debug", False)
    debug_path = _debug_mark_path(args, "batch") if debug else None

    t_total0 = time.monotonic()
    ai_coords: dict[int, tuple[int, int]] = {}

    # 第一阶段：连接 → 一次性截图 → 一次性 AI 识别所有 AI 操作
    t_setup0 = time.monotonic()
    async with connect_page(port=getattr(args, "port", None)) as page, _with_dialog_handler(page, args):
        ai_descs: list[str] = []
        ai_indices: list[int] = []
        for i, op in enumerate(ops):
            if op["type"] in ("click", "input"):
                ai_descs.append(op["desc"])
                ai_indices.append(i)

        if ai_descs:
            shot, img_w, img_h = await _take_temp_screenshot(page)
            t_setup = time.monotonic() - t_setup0  # connect + screenshot
            try:
                t_ai0 = time.monotonic()
                bboxes_1000 = await ask_vision_for_bbox_batch_norm_async(
                    cfg, shot, ai_descs
                )
                t_ai = time.monotonic() - t_ai0
            finally:
                # debug 模式下保存带 N 个红框 + #1#2 编号的标注图
                if debug_path is not None:
                    try:
                        _save_marked_image(shot, bboxes_1000, debug_path)
                    except Exception as e:
                        print(f"[DEBUG] 保存标注图失败：{e}", file=sys.stderr)
                try:
                    shot.unlink()
                except OSError:
                    pass

            for idx, bbox_1000 in zip(ai_indices, bboxes_1000):
                bbox_px = _bbox_1000_to_pixel(bbox_1000, img_w, img_h)
                cx, cy = _bbox_center(bbox_px)
                if not (0 <= cx <= img_w and 0 <= cy <= img_h):
                    raise AIRuntimeError(
                        f"AI 坐标 ({cx},{cy}) 超出截图 {img_w}x{img_h}"
                    )
                ai_coords[idx] = (cx, cy)
                if debug:
                    print(
                        f"[DEBUG] #{idx+1} '{ai_descs[len(ai_coords)-1]}'"
                        f" → bbox_1000={bbox_1000} bbox_px={bbox_px}"
                        f" center=({cx},{cy})",
                        file=sys.stderr,
                    )
        else:
            t_setup = time.monotonic() - t_setup0
            t_ai = 0.0

        # 第二阶段：按顺序执行所有操作
        t_ops0 = time.monotonic()
        ok_count = 0
        for i, op in enumerate(ops):
            t_op0 = time.monotonic()
            if op["type"] == "click":
                x, y = ai_coords[i]
                await page.mouse.click(x, y)
                print(f'[OK] click "{op["desc"]}": ({x}, {y})')
            elif op["type"] == "input":
                x, y = ai_coords[i]
                await page.mouse.click(x, y)
                # 清空再输入
                await _clear_then_type(page, op["text"])
                print(
                    f'[OK] input "{op["desc"]}" "{op["text"]}": ({x}, {y})'
                )
            elif op["type"] == "click_at":
                await page.mouse.click(op["x"], op["y"])
                print(f"[OK] click-at: ({op['x']}, {op['y']})")
            elif op["type"] == "input_at":
                await page.mouse.click(op["x"], op["y"])
                # 清空再输入
                await _clear_then_type(page, op["text"])
                print(
                    f'[OK] input-at: ({op["x"]}, {op["y"]}) "{op["text"]}"'
                )
            ok_count += 1
        t_ops = time.monotonic() - t_ops0

    t_total = time.monotonic() - t_total0

    print(
        f"[OK] batch: {ok_count}/{len(ops)} ops"
        f" total={t_total:.2f}s"
        f" shot={t_setup * 1000:.0f}ms"
        f" ai={t_ai * 1000:.0f}ms"
        f" ops={t_ops * 1000:.0f}ms"
    )
    if debug and debug_path:
        print(f"[DEBUG] 标注图: {debug_path}", file=sys.stderr)
    return 0
