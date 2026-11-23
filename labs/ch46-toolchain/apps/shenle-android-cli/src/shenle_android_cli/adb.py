"""adb 子进程封装：自动 prepend `-s <serial>`，统一 timeout / encoding。

所有 adb 调用都走 `run_adb`，不要在子命令里直接 subprocess.run：
- 找不到 adb → AdbNotFound（友好提示）
- 超时 → AdbCommandFailed（带秒数）
- 退出非零 → AdbCommandFailed（带 stderr 摘要）
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Sequence

from .errors import AdbCommandFailed, AdbNotFound

ADB_TIMEOUT = 15.0


def find_adb() -> str:
    """返回 adb 可执行文件的绝对路径；找不到时抛 AdbNotFound。"""
    p = shutil.which("adb")
    if p is None:
        raise AdbNotFound()
    return p


def run_adb(
    args: Sequence[str],
    *,
    serial: str | None = None,
    timeout: float = ADB_TIMEOUT,
) -> subprocess.CompletedProcess:
    """跑 `adb [ -s serial ] <args...>`，失败抛 AdbCommandFailed。

    返回的 CompletedProcess 保留 stdout / stderr 原文（utf-8 / replace），
    调用方需要的话可以自行解析。
    """
    adb = find_adb()
    cmd: list[str] = [adb]
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    proc = _run(adb, cmd, timeout)
    if proc.returncode != 0:
        stderr_text = (proc.stderr or "").strip()
        # adb 退出非零但 stderr 为空时给个兜底文案，避免尾巴只剩冒号。
        tail = stderr_text or "（adb 未给出具体错误信息）"
        raise AdbCommandFailed(" ".join(args), tail)
    return proc


def run_adb_relaxed(
    args: Sequence[str],
    *,
    serial: str | None = None,
    timeout: float = ADB_TIMEOUT,
) -> subprocess.CompletedProcess:
    """和 `run_adb` 一样，但 **不** 因 returncode != 0 抛错。

    适用场景：调用方需要根据输出 / 退出码自行决定怎么解读结果。
    例如 `monkey -p <pkg> -c LAUNCHER 1` 找不到 launcher activity 时会
    退出非零 + 输出 Java 堆栈——这种情况应该交给业务层翻译成 PackageNotFound，
    而不是当作通用 adb 失败暴露给用户。
    """
    adb = find_adb()
    cmd: list[str] = [adb]
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    return _run(adb, cmd, timeout)


def run_adb_bytes(
    args: Sequence[str],
    *,
    serial: str | None = None,
    timeout: float = ADB_TIMEOUT,
) -> subprocess.CompletedProcess:
    """跑 `adb [ -s serial ] <args...>`，返回 **bytes**（用于 screencap -p 等二进制）。

    和 `run_adb` 的差别：不开 text 模式 / 不做编码转换。
    """
    adb = find_adb()
    cmd: list[str] = [adb]
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise AdbCommandFailed(
            " ".join(args), f"执行超时（{timeout}s）"
        ) from exc


def _run(adb: str, cmd: list[str], timeout: float) -> subprocess.CompletedProcess:
    """子进程执行的公共部分：仅负责超时 / 编码 / 捕获。"""
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise AdbCommandFailed(
            " ".join(cmd[1:]),  # 去掉 adb 本身
            f"执行超时（{timeout}s）",
        ) from exc


def summarize_output(proc: subprocess.CompletedProcess) -> str:
    """从 am start / monkey 的输出里挑一行最有信息量的。

    - am start 的关键信息在 stdout：`Starting: Intent { ... }`
    - monkey 的 stdout 是参数回显（`bash arg: ...`），关键信息 `Events injected: N` 在 stderr

    优先级：`Starting:` > `Events injected:` > 第一行非 meta 内容。
    """
    combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    if not combined:
        return ""
    lines = [ln.strip() for ln in combined.splitlines() if ln.strip()]
    # 1. am start 的标志性行
    for ln in lines:
        if ln.startswith("Starting:"):
            return ln
    # 2. monkey 的标志性行
    for ln in lines:
        if "Events injected:" in ln:
            return ln
    # 3. 跳过 meta 行，取第一个真正有信息量的
    _META_PREFIXES = (":", "bash arg:", "args:", "//", "**")
    for ln in lines:
        if not ln.startswith(_META_PREFIXES):
            return ln
    # 兜底：第一行
    return lines[0]
