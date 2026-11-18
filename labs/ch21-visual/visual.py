"""视觉回归：两张截图比像素，输出「差了多少」而不是一句「不一样」。

口径：
- 只比同尺寸的图，尺寸不同直接报错（比出个 100% 没有意义）；
- 单像素通道差超过 `tolerance`（默认 16/255）才算「变了」，压掉抗锯齿和字体渲染的抖动；
- 结果给「差异像素占比」，阈值由调用方定，一般 0.2% 以内算通过。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import Page


def shot(page: Page, path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(target), full_page=True)
    return target


def diff_ratio(baseline: Path | str, current: Path | str, tolerance: int = 16) -> tuple[float, tuple[int, int, int, int] | None]:
    left = Image.open(baseline).convert("RGB")
    right = Image.open(current).convert("RGB")
    if left.size != right.size:
        raise ValueError(f"尺寸不一致：{left.size} vs {right.size}，请先统一 viewport 和 full_page")

    diff = ImageChops.difference(left, right)
    # 每个像素取三通道最大值，超过 tolerance 计为「变了」
    mask = diff.convert("L").point(lambda value: 255 if value > tolerance else 0)
    changed = sum(1 for value in mask.getdata() if value)
    ratio = changed / (left.size[0] * left.size[1])
    return round(ratio, 6), mask.getbbox()


def assert_visual(page: Page, baseline: Path | str, current: Path | str, tolerance: float = 0.002) -> float:
    shot(page, current)
    ratio, box = diff_ratio(baseline, current)
    if ratio > tolerance:
        raise AssertionError(f"视觉差异 {ratio:.4%} 超过阈值 {tolerance:.2%}，变化区域 {box}")
    return ratio
