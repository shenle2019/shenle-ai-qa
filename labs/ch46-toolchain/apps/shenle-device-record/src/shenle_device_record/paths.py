"""纯路径 / 批次 / 载荷工具。不碰子进程，不碰设备。"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

BATCH_CATEGORY = "AI-信息采集"
IMG_SUBDIR = "img"
JSON_SUBDIR = "json"
SCREENSHOT_PREFIX = "screenshot_"
DEFAULT_SEGMENT = "未分类"
MAX_SEGMENT_LEN = 100

# module 同时支持 "-" 和 "/" 两种分隔符拆多级目录
_MODULE_SEPARATORS = re.compile(r"[-/]")
# Windows 非法字符 + 反斜杠 + 正斜杠 + 控制字符，一律剔除
_ILLEGAL_CHARS = re.compile(r'[<>:"|?*\\/\x00-\x1f]')


def generate_batch_id(now: datetime | None = None) -> str:
    """批次 ID，格式 `YYYYMMDD-HHmmss`。"""
    moment = now if now is not None else datetime.now()
    return moment.strftime("%Y%m%d-%H%M%S")


def sanitize_segment(raw: str) -> str:
    """清洗单个路径段。脏到无内容时返回空串，由调用方决定回落。"""
    seg = (raw or "").strip()
    if seg in (".", ".."):
        return ""
    seg = _ILLEGAL_CHARS.sub("", seg)
    # Windows 会静默吞掉目录名尾部的空格和点，先自己去掉避免歧义
    seg = seg.strip(" .")[:MAX_SEGMENT_LEN]
    return seg.strip(" .")


def split_module(module: str) -> list[str]:
    """把 module 拆成多级目录段并逐段清洗；全被过滤掉则回落默认段。"""
    parts = [sanitize_segment(p) for p in _MODULE_SEPARATORS.split(module or "")]
    parts = [p for p in parts if p]
    return parts or [DEFAULT_SEGMENT]


def sanitize_func(func: str) -> str:
    """func 是单级目录名，清洗后为空则回落默认段。"""
    return sanitize_segment(func) or DEFAULT_SEGMENT


def make_batch_dir(root: str | Path, batch_id: str) -> Path:
    """创建并返回 `<root>/AI-信息采集/<batch_id>`。Module/func subdirs
    (and img/json siblings under them) are created later by `_on_snap`, not here."""
    batch_dir = Path(root).expanduser().resolve() / BATCH_CATEGORY / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)
    return batch_dir


def build_target_dir(batch_dir: str | Path, module: str, func: str) -> Path:
    """算出功能目录路径（不创建）。清洗保证结果一定在 batch_dir 之内。"""
    return Path(batch_dir).joinpath(*split_module(module), sanitize_func(func))


def next_seq(target_dir: str | Path) -> int:
    """扫 `<target_dir>/img/screenshot_*.png`，返回最大序号 + 1（1 起）。"""
    img_dir = Path(target_dir) / IMG_SUBDIR
    if not img_dir.is_dir():
        return 1
    max_n = 0
    for item in img_dir.glob(f"{SCREENSHOT_PREFIX}*.png"):
        suffix = item.stem[len(SCREENSHOT_PREFIX):]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return max_n + 1


def screenshot_filename(seq: int) -> str:
    return f"{SCREENSHOT_PREFIX}{seq:03d}.png"


def json_filename(platform: str, seq: int) -> str:
    return f"{platform}_{seq:03d}.json"


def img_relpath(seq: int) -> str:
    """JSON 里 img 字段的值，相对功能目录。"""
    return f"{IMG_SUBDIR}/{screenshot_filename(seq)}"


def build_payload(
    content: str,
    img: str,
    module: str,
    func: str,
    desc: str,
    ai: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """组装 JSON 载荷。

    原五字段顺序固定（content / img / module / func / desc），下游按这个顺序读；
    启用 AI 时追加 interface_desc / layout_desc / elements_desc 三个字段：
    - 前两个值是字符串（成功）或 None（AI 调用失败）
    - elements_desc 值是字符串列表 / 对象列表（成功）或 None（失败 / 类型不对）
    """
    payload: dict[str, Any] = {
        "content": content,
        "img": img,
        "module": module,
        "func": func,
        "desc": desc,
    }
    if ai is not None:
        for key in ("interface_desc", "layout_desc", "elements_desc"):
            payload[key] = ai.get(key)
    return payload
