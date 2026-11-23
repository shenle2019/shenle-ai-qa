"""滑动坐标计算：整屏 + 区域。

方向语义：
- up    手指向上滑（屏幕内容向下走 → 露出上方）
- down  手指向下滑（屏幕内容向上走 → 露出下方）
- left  手指向左滑（屏幕内容向右走 → 露出左侧）
- right 手指向右滑（屏幕内容向左走 → 露出右侧）

distance: 0.1~1.0，移动距离占屏幕（区域）的比例，默认 0.5。
"""

from __future__ import annotations

from .errors import CliError


VALID_DIRECTIONS = ("up", "down", "left", "right")


def _check_direction(direction: str) -> None:
    if direction not in VALID_DIRECTIONS:
        raise CliError(
            f"不支持的滑动方向：{direction!r}（应为 {', '.join(VALID_DIRECTIONS)}）"
        )


def _check_distance(distance: float) -> None:
    if not (0.1 <= distance <= 1.0):
        raise CliError(
            f"--distance 必须在 0.1~1.0 之间，得到 {distance}。"
            "0.1 = 移动屏幕的 10%，1.0 = 移动屏幕的 100%（基本等于滑到底）"
        )


def compute_fullscreen_swipe(
    direction: str, w: int, h: int, distance: float,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """整屏滑动：根据方向 + 距离比例算出 (start, end) 两个像素点。

    distance=0.5 表示移动屏幕的 50%：起点在中线 + 25%，终点在中线 - 25%。
    """
    _check_direction(direction)
    _check_distance(distance)
    cx, cy = w // 2, h // 2
    half = distance / 2.0

    if direction == "up":
        start = (cx, int(cy + h * half))
        end = (cx, int(cy - h * half))
    elif direction == "down":
        start = (cx, int(cy - h * half))
        end = (cx, int(cy + h * half))
    elif direction == "left":
        start = (int(cx + w * half), cy)
        end = (int(cx - w * half), cy)
    else:  # right
        start = (int(cx - w * half), cy)
        end = (int(cx + w * half), cy)

    start = _clamp_to_screen(start, w, h)
    end = _clamp_to_screen(end, w, h)
    return start, end


def compute_region_swipe(
    direction: str,
    bbox_px: list[int],
    distance: float,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """区域滑动：在 bbox 内部按方向滑动，distance 控制覆盖比例。

    起点 = bbox 中心 + distance/2 朝反方向偏移
    终点 = bbox 中心 - distance/2 朝反方向偏移
    """
    _check_direction(direction)
    _check_distance(distance)
    x1, y1, x2, y2 = bbox_px
    bw, bh = x2 - x1, y2 - y1
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    half = distance / 2.0

    if direction == "up":
        start = (cx, int(cy + bh * half))
        end = (cx, int(cy - bh * half))
    elif direction == "down":
        start = (cx, int(cy - bh * half))
        end = (cx, int(cy + bh * half))
    elif direction == "left":
        start = (int(cx + bw * half), cy)
        end = (int(cx - bw * half), cy)
    else:  # right
        start = (int(cx - bw * half), cy)
        end = (int(cx + bw * half), cy)

    # clamp 到 bbox 内部（保留 5 像素边距）
    pad = 5
    start = (
        max(x1 + pad, min(start[0], x2 - pad)),
        max(y1 + pad, min(start[1], y2 - pad)),
    )
    end = (
        max(x1 + pad, min(end[0], x2 - pad)),
        max(y1 + pad, min(end[1], y2 - pad)),
    )
    return start, end


def _clamp_to_screen(pt: tuple[int, int], w: int, h: int) -> tuple[int, int]:
    return (max(0, min(pt[0], w - 1)), max(0, min(pt[1], h - 1)))
