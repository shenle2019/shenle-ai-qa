"""第 29 章：让失败的用例自己留下证据。

两个工具：`retry` 处理瞬时抖动，`capture_on_failure` 在失败瞬间截图 + 抓日志。
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass
class Attempt:
    index: int
    ok: bool
    error: str = ""


def retry(
    func: Callable[[], T],
    *,
    attempts: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0,
    on_attempt: Callable[[Attempt], None] | None = None,
) -> T:
    """失败就等一会再试，最多 attempts 次；最后一次仍失败就把原异常抛出去。"""
    if attempts < 1:
        raise ValueError("attempts 至少是 1")
    wait = delay
    last: Exception | None = None
    for index in range(1, attempts + 1):
        try:
            value = func()
        except Exception as exc:  # noqa: BLE001 - 重试的边界就在这里
            last = exc
            if on_attempt:
                on_attempt(Attempt(index, False, f"{type(exc).__name__}: {exc}"))
            if index < attempts:
                time.sleep(wait)
                wait *= backoff
        else:
            if on_attempt:
                on_attempt(Attempt(index, True))
            return value
    assert last is not None
    raise last


def capture_on_failure(app, out_dir: str | Path, name: str, func: Callable[[], T]) -> T:
    """执行 func；抛异常时把截图、日志、异常栈一起落到 out_dir，再把异常抛给上层。"""
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    try:
        return func()
    except Exception:
        stamp = time.strftime("%Y%m%d-%H%M%S")
        shot = directory / f"{name}-{stamp}.png"
        log = directory / f"{name}-{stamp}.log"
        trace = directory / f"{name}-{stamp}.txt"
        try:
            app.screenshot(shot)
        except Exception as exc:  # noqa: BLE001 - 截图失败不能掩盖原始错误
            shot = Path(f"<截图失败：{exc}>")
        try:
            log.write_text(app.device.logcat(lines=300), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            log = Path(f"<日志抓取失败：{exc}>")
        trace.write_text(traceback.format_exc(), encoding="utf-8")
        raise


def wait_until(predicate: Callable[[], bool], *, timeout: float = 10, interval: float = 0.3) -> bool:
    """同步等待一个布尔条件，返回是否在超时前成立。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False
