"""screenshot / click / input / swipe / swipe-to / keyevent / recents /
notifications / current-app / get / batch / longpress / zoom / pinch / shell /
dump-ui / appinfo / stop 子命令实现。

所有命令以 `[OK] ...` 或 `[FAIL] ...` 单行输出 + exit 0/1 结束，
方便上层（人 / AI）parse。`shell` / `appinfo` 是透传，[OK] 走 stderr。

`get` 的 [OK] 状态行走 stderr，描述正文走 stdout（方便脚本 capture 正文）。

公共前置：选定设备（_resolve_serial）。
click / input / swipe --region / longpress / batch（含 click/longpress）多一步：
检查 AI 配置 → 截图 → 调 AI → 0-1000 → 像素 → tap/swipe。

--debug 时上述 AI 类命令会保存一张「AI 红框标注图」到
cwd/shenle-debug-<cmd>-<ts>.png（demo_2.py 的 ai_marked.png 思路）。
"""

from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
from pathlib import Path

from PIL import Image, ImageDraw

from . import ai, app_state, input_text, keyevent, screen, swipe
from .adb import run_adb, run_adb_relaxed
from .devices import list_devices, pick_device
from .errors import BatchOpParseError, CliError, DumpUiFailed


def _resolve_input_method(args) -> str:
    """解析 --input-method：CLI flag 优先，其次 INPUT_METHOD 环境变量，最后默认 clipboard。"""
    flag = getattr(args, "input_method", None)
    if flag:
        return flag
    return os.environ.get("INPUT_METHOD", "clipboard")


# ---------------------------------------------------------------------------
# 公共


def _resolve_serial(args) -> str:
    """根据 args.serial 选定并校验一台设备，返回 serial。"""
    devices = list_devices()
    serial = getattr(args, "serial", None)
    return pick_device(devices, serial).serial


def _bbox_1000_to_pixel(bbox: list[int], w: int, h: int) -> list[int]:
    """[xmin,ymin,xmax,ymax] 0-1000 → 真实像素。"""
    return [
        int(bbox[0] * w / 1000),
        int(bbox[1] * h / 1000),
        int(bbox[2] * w / 1000),
        int(bbox[3] * h / 1000),
    ]


def _bbox_center(bbox: list[int]) -> tuple[int, int]:
    return (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2


def _debug_print_timing(t_shot: float, t_ai: float, t_total: float) -> None:
    print(
        f"[DEBUG] screencap={t_shot*1000:.0f}ms"
        f" ai={t_ai*1000:.0f}ms"
        f" total={t_total*1000:.0f}ms",
        file=sys.stderr,
    )


def _save_marked_image(
    img: Image.Image,
    bbox_px: list[int],
    cmd_name: str,
    desc: str,
) -> Path:
    """在 AI 用过的那张截图上画红框 + 标签，存到 cwd/shenle-debug-<cmd>-<ts>.png。

    跟 demo_2.py 的 ai_marked.png 思路一致——默认行为，不需要 --debug。
    路径返回后由 [OK] 行打出来，用户可以直接点开看 AI 把元素框在哪。
    """
    ts = int(time.time() * 1000)
    out = Path.cwd() / f"shenle-debug-{cmd_name}-{ts}.png"
    debug_img = img.copy()
    draw = ImageDraw.Draw(debug_img)
    draw.rectangle(bbox_px, outline="red", width=4)
    # label 放在 bbox 上方；bbox 贴顶（y 太小）时改成放在 bbox 下方
    label = f"{cmd_name}: {desc}"
    label_y = bbox_px[1] - 22
    if label_y < 2:
        label_y = bbox_px[3] + 4
    draw.text((bbox_px[0] + 2, label_y), label, fill="red")
    debug_img.save(out)
    return out


# ---------------------------------------------------------------------------
# screenshot


def cmd_screenshot(args) -> int:
    """截当前屏幕到文件。PNG 默认；按扩展名自动选 PNG / JPEG。"""
    serial = _resolve_serial(args)
    out = Path(args.path).resolve()

    fmt = (args.format or "auto").lower()
    if fmt == "auto":
        suf = out.suffix.lower()
        fmt = "jpeg" if suf in (".jpg", ".jpeg") else "png"
    quality = args.quality or 85

    t0 = time.monotonic()
    w, h = screen.screencap_to_file(serial, out, fmt=fmt, quality=quality)
    t = time.monotonic() - t0

    if getattr(args, "debug", False):
        print(f"[DEBUG] screencap={t*1000:.0f}ms → {out}", file=sys.stderr)

    print(f"[OK] screenshot: {out} ({w}x{h}) [{fmt}]")
    return 0


# ---------------------------------------------------------------------------
# click / input 共用


def _vision_locate(
    serial: str, desc: str, debug: bool,
) -> tuple[int, int, list[int], list[int], int, int, Image.Image, float, float, float]:
    """截图 → AI 定位 → 返回 (cx, cy, bbox_1000, bbox_px, w, h, img, t_shot, t_ai, t_total)。

    img 一并返回，方便调用方画红框生成标注图（不需要再 screencap 一次）。
    临时 JPEG 内部清理。
    """
    t_total0 = time.monotonic()
    t_shot0 = time.monotonic()
    img = screen.screencap_to_image(serial)
    w, h = img.size
    t_shot = time.monotonic() - t_shot0

    cfg = ai.load_config()  # 缺失 → AIConfigError
    tmp_path: Path | None = None
    try:
        t_ai0 = time.monotonic()
        tmp_path = screen.image_to_jpeg_tempfile(img)
        bbox_1000 = ai.ask_vision_for_bbox_norm(cfg, tmp_path, desc, w, h)
        t_ai = time.monotonic() - t_ai0
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink()
            except OSError:
                pass

    bbox_px = _bbox_1000_to_pixel(bbox_1000, w, h)
    cx, cy = _bbox_center(bbox_px)
    t_total = time.monotonic() - t_total0

    if debug:
        sx = w / 1000.0
        sy = h / 1000.0
        print(
            f"[DEBUG] bbox_1000={bbox_1000}"
            f" scale=({sx:.3f},{sy:.3f})"
            f" bbox_px={bbox_px}"
            f" center=({cx},{cy})",
            file=sys.stderr,
        )
        _debug_print_timing(t_shot, t_ai, t_total)

    return cx, cy, bbox_1000, bbox_px, w, h, img, t_shot, t_ai, t_total


def _post_shot_if_needed(serial: str, post_shot: str | None) -> Path | None:
    if not post_shot:
        return None
    ps = Path(post_shot).resolve()
    ps.parent.mkdir(parents=True, exist_ok=True)
    screen.screencap_to_file(serial, ps, fmt="png")
    return ps


# ---------------------------------------------------------------------------
# click


def cmd_click(args) -> int:
    """AI 视觉定位 + tap。"""
    serial = _resolve_serial(args)
    desc = args.description
    debug = getattr(args, "debug", False)

    cx, cy, _bbox_1000, bbox_px, _w, _h, img, t_shot, t_ai, t_total = _vision_locate(
        serial, desc, debug=debug,
    )

    # --debug 时画 AI 红框标注图，否则不画（避免每次跑都污染 cwd）
    marked = _save_marked_image(img, bbox_px, "click", desc) if debug else None

    run_adb(
        ["shell", "input", "tap", str(int(cx)), str(int(cy))],
        serial=serial,
    )

    ps = _post_shot_if_needed(serial, getattr(args, "post_shot", None))

    timing = f"shot={t_shot*1000:.0f}ms ai={t_ai*1000:.0f}ms total={t_total*1000:.0f}ms"
    parts = [
        f'[OK] click "{desc}": ({cx}, {cy})',
        timing,
    ]
    if marked is not None:
        parts.append(f'ai框={marked}')
    if ps is not None:
        parts.append(f'post={ps}')
    print("; ".join(parts))
    return 0


# ---------------------------------------------------------------------------
# input


def cmd_input(args) -> int:
    """AI 视觉定位输入框 + tap + 输入 text（中文走剪贴板 / ADBKeyboard）。"""
    serial = _resolve_serial(args)
    desc = args.description
    text = args.text
    debug = getattr(args, "debug", False)
    method = _resolve_input_method(args)

    cx, cy, _bbox_1000, bbox_px, _w, _h, img, t_shot, t_ai, t_total = _vision_locate(
        serial, desc, debug=debug,
    )

    # --debug 时画 AI 红框标注图
    marked = _save_marked_image(img, bbox_px, "input", desc) if debug else None

    # tap + 文本输入（input_text_at 内部处理 method 分支）
    t_type0 = time.monotonic()
    input_text.input_text_at(serial, cx, cy, text, clear=True, method=method)
    t_type = time.monotonic() - t_type0
    t_total2 = t_total + t_type

    ps = _post_shot_if_needed(serial, getattr(args, "post_shot", None))

    timing = f"shot={t_shot*1000:.0f}ms ai={t_ai*1000:.0f}ms type={t_type*1000:.0f}ms total={t_total2*1000:.0f}ms"
    parts = [
        f'[OK] input "{desc}" "{text}": ({cx}, {cy})',
        timing,
        f'method={method}',
    ]
    if marked is not None:
        parts.append(f'ai框={marked}')
    if ps is not None:
        parts.append(f'post={ps}')
    print("; ".join(parts))
    return 0


# ---------------------------------------------------------------------------
# swipe / swipe-to


def _get_screen_size(serial: str) -> tuple[int, int]:
    """走 wm size 拿屏幕尺寸（不截图，更快）。"""
    proc = run_adb(["shell", "wm", "size"], serial=serial)
    m = re.search(r"(\d+)\s*x\s*(\d+)", proc.stdout)
    if not m:
        raise RuntimeError(f"wm size 解析失败：{proc.stdout.strip()!r}")
    return int(m.group(1)), int(m.group(2))


def cmd_swipe(args) -> int:
    """滑动。无 --region 整屏（只读 wm size）；有 --region 走 AI 视觉定位区域。"""
    serial = _resolve_serial(args)
    direction = args.direction
    count = max(1, args.count or 1)
    distance = args.distance
    debug = getattr(args, "debug", False)
    region = getattr(args, "region", None)
    post_shot = getattr(args, "post_shot", None)

    marked = None
    if region:
        cx, cy, _bbox_1000, bbox_px, _w, _h, img, t_shot, t_ai, t_total = _vision_locate(
            serial, region, debug=debug,
        )
        if debug:
            marked = _save_marked_image(img, bbox_px, "swipe", region)
        start, end = swipe.compute_region_swipe(direction, bbox_px, distance)
    else:
        w, h = _get_screen_size(serial)
        start, end = swipe.compute_fullscreen_swipe(direction, w, h, distance)

    t0 = time.monotonic()
    for _ in range(count):
        run_adb(
            ["shell", "input", "swipe",
             str(start[0]), str(start[1]),
             str(end[0]), str(end[1]),
             "300"],  # 300ms = 自然的滑动速度
            serial=serial,
        )
        if count > 1:
            time.sleep(0.15)  # 让 UI 跟手
    t_swipe = time.monotonic() - t0

    ps = _post_shot_if_needed(serial, post_shot)

    parts = [
        f'[OK] swipe: {direction}',
        f'({start[0]},{start[1]})→({end[0]},{end[1]})',
        f'×{count}',
    ]
    if region:
        parts.append(f'region="{region}"')
    parts.append(f'swipe={t_swipe*1000:.0f}ms')
    if marked is not None:
        parts.append(f'ai框={marked}')
    if ps is not None:
        parts.append(f'post={ps}')
    print("; ".join(parts))
    return 0


def cmd_swipe_to(args) -> int:
    """显式坐标滑动（精确定位场景）。"""
    serial = _resolve_serial(args)
    x1, y1, x2, y2 = args.x1, args.y1, args.x2, args.y2
    duration = args.duration or 300
    post_shot = getattr(args, "post_shot", None)

    t0 = time.monotonic()
    run_adb(
        ["shell", "input", "swipe",
         str(x1), str(y1), str(x2), str(y2), str(duration)],
        serial=serial,
    )
    t = time.monotonic() - t0

    ps = _post_shot_if_needed(serial, post_shot)

    parts = [
        f'[OK] swipe-to: ({x1},{y1})→({x2},{y2})',
        f'duration={duration}ms',
        f'swipe={t*1000:.0f}ms',
    ]
    if ps is not None:
        parts.append(f'post={ps}')
    print("; ".join(parts))
    return 0


# ---------------------------------------------------------------------------
# keyevent / recents / notifications


def cmd_keyevent(args) -> int:
    """按键：支持数字键码 + 30+ 别名（back / home / recents / volume_* / ...）。"""
    serial = _resolve_serial(args)
    code = keyevent.resolve_keycode(args.code)
    run_adb(["shell", "input", "keyevent", str(code)], serial=serial)
    print(f"[OK] keyevent: {args.code} (code={code})")
    return 0


def cmd_recents(args) -> int:
    """最近任务（KEYCODE_APP_SWITCH = 187）。"""
    serial = _resolve_serial(args)
    run_adb(["shell", "input", "keyevent", "187"], serial=serial)
    print("[OK] recents: 已打开最近任务（keyevent 187）")
    return 0


def cmd_notifications(args) -> int:
    """下拉通知栏（Android 8+ 用 cmd statusbar expand-notifications）。"""
    serial = _resolve_serial(args)
    run_adb(
        ["shell", "cmd", "statusbar", "expand-notifications"],
        serial=serial,
    )
    print("[OK] notifications: 已下拉通知栏（cmd statusbar expand-notifications）")
    return 0


# ---------------------------------------------------------------------------
# current-app / get


def cmd_current_app(args) -> int:
    """当前前台 App。默认 text 输出 pkg/activity；--format json 输出结构化。"""
    serial = _resolve_serial(args)
    pkg, activity = app_state.get_current_app(serial)
    if (args.format or "text") == "json":
        print(json.dumps(
            {"package": pkg, "activity": activity},
            ensure_ascii=False,
        ))
    else:
        print(f"{pkg}/{activity}")
    return 0


def cmd_get(args) -> int:
    """AI 视觉描述区域内容（4 节 layout/icons/text/intro）。

    [OK] 状态行走 stderr，正文（4 节描述）走 stdout —— 方便脚本 capture 正文。
    """
    serial = _resolve_serial(args)
    area = args.description
    debug = getattr(args, "debug", False)
    post_shot = getattr(args, "post_shot", None)
    cfg = ai.load_config()

    t_shot0 = time.monotonic()
    img = screen.screencap_to_image(serial)
    _w, _h = img.size
    t_shot = time.monotonic() - t_shot0

    tmp: Path | None = None
    try:
        t_ai0 = time.monotonic()
        tmp = screen.image_to_jpeg_tempfile(img)
        description_text = ai.ask_vision_describe(cfg, tmp, area)
        t_ai = time.monotonic() - t_ai0
    finally:
        if tmp is not None:
            try:
                tmp.unlink()
            except OSError:
                pass

    if debug:
        print(
            f"[DEBUG] screencap={t_shot*1000:.0f}ms ai={t_ai*1000:.0f}ms",
            file=sys.stderr,
        )

    ps = _post_shot_if_needed(serial, post_shot)
    if ps is not None:
        print(f'[OK] get "{area}": post={ps}', file=sys.stderr)
    else:
        print(f'[OK] get "{area}"', file=sys.stderr)
    print(description_text)
    return 0


# ---------------------------------------------------------------------------
# batch


_BATCH_KEYWORDS = {"click", "input", "click-at", "input-at", "longpress"}


def _parse_batch_ops(tokens: list[str]) -> list[dict]:
    """把 batch 的剩余参数解析成操作列表。

    例：`["click", "登录", "input", "用户名::admin", "click-at", "100", "200"]`
    → `[{"type": "click", "desc": "登录"},
        {"type": "input", "desc": "用户名", "text": "admin"},
        {"type": "click_at", "x": 100, "y": 200}]`
    """
    ops: list[dict] = []
    current: tuple[str, list[str]] | None = None
    for tok in tokens:
        if tok in _BATCH_KEYWORDS:
            if current is not None:
                ops.append(_finalize_batch_op(*current))
            current = (tok, [])
        else:
            if current is None:
                raise BatchOpParseError(
                    f"参数 {tok!r} 前面没有任何操作类型"
                    f"（应为 click / input / click-at / input-at / longpress）"
                )
            current[1].append(tok)
    if current is not None:
        ops.append(_finalize_batch_op(*current))
    if not ops:
        raise BatchOpParseError("batch 至少需要一个操作")
    return ops


def _finalize_batch_op(op_type: str, args: list[str]) -> dict:
    if op_type == "click":
        if not args:
            raise BatchOpParseError("click 需要元素描述")
        return {"type": "click", "desc": " ".join(args)}
    if op_type == "input":
        joined = " ".join(args)
        if "::" not in joined:
            raise BatchOpParseError(
                f"input 格式应为 <描述>::<文本>，得到：{joined!r}"
            )
        desc, text = joined.split("::", 1)
        if not desc.strip():
            raise BatchOpParseError(f"input 描述为空：{joined!r}")
        return {"type": "input", "desc": desc.strip(), "text": text}
    if op_type == "click-at":
        if len(args) != 2:
            raise BatchOpParseError(
                f"click-at 需要 2 个整数坐标，得到 {len(args)} 个：{args!r}"
            )
        try:
            x, y = int(args[0]), int(args[1])
        except ValueError:
            raise BatchOpParseError(f"click-at 坐标非整数：{args!r}") from None
        return {"type": "click-at", "x": x, "y": y}
    if op_type == "input-at":
        if len(args) < 3:
            raise BatchOpParseError(f"input-at 需要 x y 文本，得到：{args!r}")
        try:
            x, y = int(args[0]), int(args[1])
        except ValueError:
            raise BatchOpParseError(f"input-at 坐标非整数：{args!r}") from None
        return {"type": "input-at", "x": x, "y": y, "text": " ".join(args[2:])}
    if op_type == "longpress":
        if not args:
            raise BatchOpParseError("longpress 需要元素描述")
        # 可选 --duration N
        duration = 1500
        cleaned: list[str] = []
        i = 0
        while i < len(args):
            if args[i] == "--duration" and i + 1 < len(args):
                try:
                    duration = int(args[i + 1])
                except ValueError:
                    raise BatchOpParseError(
                        f"longpress --duration 需要整数，得到：{args[i+1]!r}"
                    ) from None
                i += 2
            else:
                cleaned.append(args[i])
                i += 1
        if not cleaned:
            raise BatchOpParseError("longpress 需要元素描述")
        return {"type": "longpress", "desc": " ".join(cleaned), "duration": duration}
    raise BatchOpParseError(f"未知 batch 操作类型：{op_type}")


def _save_batch_marked_image(
    img: Image.Image, ops: list[dict], ai_op_indices: list[int],
) -> Path:
    """在 AI 用过的截图上画 N 个红框（多元素 batch 用）。"""
    ts = int(time.time() * 1000)
    out = Path.cwd() / f"shenle-debug-batch-{ts}.png"
    debug_img = img.copy()
    draw = ImageDraw.Draw(debug_img)
    w, h = img.size
    colors = ["red", "orange", "lime", "yellow", "magenta", "cyan"]
    for i, idx in enumerate(ai_op_indices):
        bbox_px = ops[idx]["bbox_px"]
        op = ops[idx]
        draw.rectangle(bbox_px, outline=colors[i % len(colors)], width=4)
        label = f"#{i+1} {op['type']}: {op['desc']}"
        label_y = bbox_px[1] - 22
        if label_y < 2:
            label_y = bbox_px[3] + 4
        draw.text((bbox_px[0] + 2, label_y), label, fill=colors[i % len(colors)])
    debug_img.save(out)
    return out


def cmd_batch(args) -> int:
    """一次截图 + 一次 AI 批量识别 + 按顺序执行多个操作。

    click / longpress / input 都走 AI 定位（与 demo_2.py 一致）：
    一次 screencap、一次 AI 调用同时找 N 个元素的 bbox，
    然后每个 op tap AI 框的中心 + 执行对应动作。
    input-at / click-at 用原始坐标，不调 AI。
    """
    serial = _resolve_serial(args)
    debug = getattr(args, "debug", False)
    post_shot = getattr(args, "post_shot", None)
    method = _resolve_input_method(args)

    try:
        ops = _parse_batch_ops(list(args.ops))
    except BatchOpParseError as e:
        raise

    # 需要 AI 定位的 op 类型（跟 demo_2.py 思路一致：AI 找元素 → tap 元素中心）
    ai_op_indices = [i for i, op in enumerate(ops)
                     if op["type"] in ("click", "longpress", "input")]

    img: Image.Image | None = None
    w = h = 0

    t_total0 = time.monotonic()

    # 第一阶段：AI op 才需要截图；纯 raw 坐标 op（click-at/input-at）连截图都省
    t_shot0 = time.monotonic()
    if ai_op_indices:
        img = screen.screencap_to_image(serial)
        w, h = img.size
    t_shot = time.monotonic() - t_shot0

    # 第二阶段：批量 AI（一次调用，N 个 bbox）
    t_ai0 = time.monotonic()
    if ai_op_indices and img is not None:
        cfg = ai.load_config()
        tmp: Path | None = None
        try:
            tmp = screen.image_to_jpeg_tempfile(img)
            descs = [ops[i]["desc"] for i in ai_op_indices]
            bboxes_1000 = ai.ask_vision_for_bbox_batch_norm(cfg, tmp, descs, w, h)
        finally:
            if tmp is not None:
                try:
                    tmp.unlink()
                except OSError:
                    pass
        # 把 AI 返回的 bbox 映射回每个 op
        for idx, bbox_1000 in zip(ai_op_indices, bboxes_1000):
            bbox_px = _bbox_1000_to_pixel(bbox_1000, w, h)
            cx, cy = _bbox_center(bbox_px)
            ops[idx]["bbox_px"] = bbox_px
            ops[idx]["cx"] = cx
            ops[idx]["cy"] = cy
    t_ai = time.monotonic() - t_ai0

    marked: Path | None = None
    if debug and img is not None and ai_op_indices:
        marked = _save_batch_marked_image(img, ops, ai_op_indices)

    # 第三阶段：按顺序执行
    t_ops0 = time.monotonic()
    for op in ops:
        if op["type"] == "click":
            cx, cy = op["cx"], op["cy"]
            run_adb(
                ["shell", "input", "tap", str(int(cx)), str(int(cy))],
                serial=serial,
            )
            print(f'[OK] batch click "{op["desc"]}": ({cx}, {cy})')
        elif op["type"] == "input":
            # batch input 也走 AI 定位（不是屏幕中心了）
            cx, cy = op["cx"], op["cy"]
            input_text.input_text_at(serial, cx, cy, op["text"], clear=True, method=method)
            print(f'[OK] batch input "{op["desc"]}" "{op["text"]}": ({cx}, {cy}) method={method}')
        elif op["type"] == "longpress":
            cx, cy = op["cx"], op["cy"]
            duration = op.get("duration", 1500)
            run_adb(
                ["shell", "input", "swipe",
                 str(cx), str(cy), str(cx), str(cy), str(duration)],
                serial=serial,
            )
            print(
                f'[OK] batch longpress "{op["desc"]}": ({cx}, {cy}) duration={duration}ms'
            )
        elif op["type"] == "click-at":
            run_adb(
                ["shell", "input", "tap", str(op["x"]), str(op["y"])],
                serial=serial,
            )
            print(f"[OK] batch click-at: ({op['x']}, {op['y']})")
        elif op["type"] == "input-at":
            input_text.input_text_at(serial, op["x"], op["y"], op["text"], clear=True, method=method)
            print(f'[OK] batch input-at: ({op["x"]}, {op["y"]}) "{op["text"]}" method={method}')
    t_ops = time.monotonic() - t_ops0
    t_total = time.monotonic() - t_total0

    # 总结
    parts = [
        f"[OK] batch: {len(ops)}/{len(ops)} ops",
        f"total={t_total*1000:.0f}ms",
        f"shot={t_shot*1000:.0f}ms",
        f"ai={t_ai*1000:.0f}ms",
        f"ops={t_ops*1000:.0f}ms",
    ]
    if marked is not None:
        parts.append(f"ai框={marked}")
    ps = _post_shot_if_needed(serial, post_shot)
    if ps is not None:
        parts.append(f"post={ps}")
    print("; ".join(parts))
    return 0


# ---------------------------------------------------------------------------
# longpress


def cmd_longpress(args) -> int:
    """AI 视觉定位 + 在中心点长按 duration ms（默认 1500）。"""
    serial = _resolve_serial(args)
    desc = args.description
    duration = args.duration or 1500
    debug = getattr(args, "debug", False)

    cx, cy, _b1000, bbox_px, _w, _h, img, t_shot, t_ai, t_total = _vision_locate(
        serial, desc, debug=debug,
    )

    marked = _save_marked_image(img, bbox_px, "longpress", desc) if debug else None

    run_adb(
        ["shell", "input", "swipe",
         str(cx), str(cy), str(cx), str(cy), str(duration)],
        serial=serial,
    )

    ps = _post_shot_if_needed(serial, getattr(args, "post_shot", None))

    timing = f"ai={t_ai*1000:.0f}ms"
    parts = [f'[OK] longpress "{desc}": ({cx}, {cy})', f'duration={duration}ms', timing]
    if marked is not None:
        parts.append(f"ai框={marked}")
    if ps is not None:
        parts.append(f"post={ps}")
    print("; ".join(parts))
    return 0


# ---------------------------------------------------------------------------
# zoom / pinch（双指近似：用两个线程并行跑 input swipe）


def _run_two_finger_gesture(
    serial: str, cx: int, cy: int, scale: float, duration: int = 300,
) -> None:
    """两个 input swipe 并行：模拟双指。

    r = 初始偏移（200px）；scale = 终止偏移 / 初始偏移。
    scale > 1 → 手指张开；scale < 1 → 手指合拢。

    这是「近似」实现——单线程的 adb input swipe 没法表达真正的多指，
    部分机型可能被识别为两次连续的单指滑动。
    """
    if scale <= 0:
        raise CliError(f"--scale 必须 > 0，得到 {scale}")
    r = 200
    f1_start = (cx - r, cy - r)
    f1_end = (cx - int(r * scale), cy - int(r * scale))
    f2_start = (cx + r, cy + r)
    f2_end = (cx + int(r * scale), cy + int(r * scale))

    def swipe(s: tuple[int, int], e: tuple[int, int]) -> None:
        run_adb(
            ["shell", "input", "swipe",
             str(s[0]), str(s[1]), str(e[0]), str(e[1]), str(duration)],
            serial=serial,
        )

    t1 = threading.Thread(target=swipe, args=(f1_start, f1_end))
    t2 = threading.Thread(target=swipe, args=(f2_start, f2_end))
    t1.start(); t2.start()
    t1.join(); t2.join()


def cmd_zoom(args) -> int:
    """双指 zoom（scale > 1 = 张开 = 内容放大；scale < 1 = 合拢 = 内容缩小）。"""
    serial = _resolve_serial(args)
    scale = args.scale
    duration = getattr(args, "duration", None) or 300
    _run_two_finger_gesture(serial, args.x, args.y, scale, duration)
    print(f"[OK] zoom: ({args.x},{args.y}) scale={scale} duration={duration}ms")
    return 0


def cmd_pinch(args) -> int:
    """双指 pinch（语义同 zoom，只是 --scale 给的是另一种命名习惯的倍数）。"""
    serial = _resolve_serial(args)
    scale = args.scale
    duration = getattr(args, "duration", None) or 300
    _run_two_finger_gesture(serial, args.x, args.y, scale, duration)
    print(f"[OK] pinch: ({args.x},{args.y}) scale={scale} duration={duration}ms")
    return 0


# ---------------------------------------------------------------------------
# shell / dump-ui / appinfo / stop


def cmd_shell(args) -> int:
    """adb shell 透传。原始 stdout/stderr 原样输出，退出码原样返回。

    --filter PATTERN：行级包含过滤（避免 Windows 没有 grep 的问题，
    在 cmd / PowerShell / Git Bash 上都能用）。
    """
    serial = _resolve_serial(args)
    cmd = list(args.cmd or [])
    if not cmd:
        raise CliError("用法：shenle-android-cli shell <任意 adb shell 命令>")
    proc = run_adb_relaxed(["shell", *cmd], serial=serial)
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    out = proc.stdout or ""
    flt = getattr(args, "filter", None)
    if flt:
        out = "\n".join(ln for ln in out.splitlines() if flt in ln)
    if out:
        print(out, end="")
    return proc.returncode


def cmd_dump_ui(args) -> int:
    """uiautomator dump → pull 到本地。"""
    serial = _resolve_serial(args)
    out = Path(args.path).resolve()

    # 1. dump 到设备文件
    proc = run_adb_relaxed(
        ["shell", "uiautomator", "dump", "/sdcard/window_dump.xml"],
        serial=serial,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        raise DumpUiFailed(
            f"uiautomator dump 失败：{stderr or '（无 stderr）'}"
        )

    # 2. pull 到本地
    out.parent.mkdir(parents=True, exist_ok=True)
    run_adb(["pull", "/sdcard/window_dump.xml", str(out)], serial=serial)
    print(f"[OK] dump-ui: {out}")
    return 0


def cmd_appinfo(args) -> int:
    """dumpsys package —— dumpsys 输出走 stdout，[OK] 走 stderr 方便 pipe。"""
    serial = _resolve_serial(args)
    pkg = args.pkg
    proc = run_adb(["shell", "dumpsys", "package", pkg], serial=serial)
    if proc.stdout:
        print(proc.stdout, end="")
    print(f"[OK] appinfo: {pkg}", file=sys.stderr)
    return 0


def cmd_stop(args) -> int:
    """am force-stop —— 杀进程，用于冷启动测试。和 close（Home 键保留进程）不同。"""
    serial = _resolve_serial(args)
    pkg = args.pkg
    run_adb(["shell", "am", "force-stop", pkg], serial=serial)
    print(f"[OK] stop: {pkg} 已强制停止（am force-stop）")
    return 0
