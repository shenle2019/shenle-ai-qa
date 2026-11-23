"""后台浏览器状态：per-port 状态文件 + per-port user_data 目录。

设计要点
--------
- 每个端口一份 state 文件：`<app_dir>/state/<port>.json`
- 每个端口一份 user_data 目录：`<cwd_at_start_time>/user_data/<port>/`
- 支持多个后台浏览器同时跑（不同端口、不同 profile）

旧单文件 `state.json` 不再读写；如残留可忽略或手动删除。
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

_APP_DIR_NAME = "shenle-web-cli"


# ---------------------------------------------------------------------------
# 路径


def app_dir() -> Path:
    """返回存放 state.json / profile / daemon.log 的根目录。"""
    if sys.platform == "win32":
        base = Path(__import__("os").environ.get("LOCALAPPDATA")
                    or Path.home())
    else:
        base = Path(__import__("os").environ.get("XDG_STATE_HOME")
                    or Path.home() / ".local" / "state")
    return base / _APP_DIR_NAME


def state_dir() -> Path:
    """存放所有 per-port state 文件的目录。"""
    d = app_dir() / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def state_file(port: int) -> Path:
    return state_dir() / f"{port}.json"


def log_file() -> Path:
    return app_dir() / "daemon.log"


# ---------------------------------------------------------------------------
# 读写


def _read_state(port: int) -> dict | None:
    p = state_file(port)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_state(port: int, payload: dict) -> None:
    """原子写 state 文件。"""
    p = state_file(port)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp.replace(p)


def clear_state(port: int) -> None:
    """删掉某个端口的 state 文件。"""
    try:
        state_file(port).unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


# ---------------------------------------------------------------------------
# 健康检查


def _pid_alive(pid: int) -> bool:
    if pid is None or pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        kernel32 = ctypes.windll.kernel32
        h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return False
        try:
            code = ctypes.c_ulong()
            ok = kernel32.GetExitCodeProcess(h, ctypes.byref(code))
            return bool(ok) and code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(h)
    else:
        import os as _os
        try:
            _os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True


@dataclass(frozen=True)
class BrowserStatus:
    running: bool
    port: int | None
    pid: int | None
    detail: str | None  # failed 时携带的错误信息


def inspect(port: int) -> BrowserStatus:
    s = _read_state(port)
    if not s:
        return BrowserStatus(False, port, None, None)
    status = s.get("status")
    pid = s.get("pid")
    if status == "running" and _pid_alive(pid):
        return BrowserStatus(True, port, pid, None)
    if status == "failed":
        return BrowserStatus(False, port, pid, s.get("error") or "未知原因")
    # spawning 但 pid 已死 / 状态陈旧 → 当作不存在
    return BrowserStatus(False, port, pid, None)


def is_running(port: int) -> bool:
    return inspect(port).running


def list_running_ports() -> list[int]:
    """返回所有正在跑的端口（升序）。"""
    ports = []
    for f in state_dir().glob("*.json"):
        try:
            port = int(f.stem)
        except ValueError:
            continue
        if is_running(port):
            ports.append(port)
    return sorted(ports)


def data_dir_for(port: int) -> Path:
    """拿这个端口的 user_data 目录。优先用 state 里保存的（start 时的 cwd），
    fallback 到当前 cwd/user_data/<port>/。
    """
    s = _read_state(port)
    if s and s.get("data_dir"):
        return Path(s["data_dir"])
    return Path.cwd() / "user_data" / str(port)


# ---------------------------------------------------------------------------
# 等待 + 杀进程


def wait_for_running(port: int, timeout_s: float = 30.0) -> BrowserStatus:
    """轮询某端口的 state，直到 running / failed / 超时。"""
    deadline = time.monotonic() + timeout_s
    last = inspect(port)
    while time.monotonic() < deadline:
        last = inspect(port)
        if last.running or last.detail:
            return last
        time.sleep(0.2)
    return BrowserStatus(
        False, last.port, last.pid, f"启动超时（{timeout_s:.0f}s）"
    )


def kill(pid: int, grace_s: float = 5.0) -> bool:
    """关掉后台 daemon 进程。Windows 走 taskkill /T；其它平台先 SIGTERM 再 SIGKILL。"""
    if pid is None or pid <= 0 or not _pid_alive(pid):
        return True

    if sys.platform == "win32":
        import subprocess

        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=grace_s,
            )
        except subprocess.TimeoutExpired:
            pass
        for _ in range(int(grace_s / 0.2)):
            if not _pid_alive(pid):
                break
            time.sleep(0.2)
        if _pid_alive(pid):
            try:
                subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid), "/T"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                )
            except subprocess.TimeoutExpired:
                pass
    else:
        import os as _os
        import signal

        try:
            _os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            return True
        except PermissionError:
            pass
        deadline = time.monotonic() + grace_s
        while time.monotonic() < deadline and _pid_alive(pid):
            time.sleep(0.2)
        if _pid_alive(pid):
            try:
                _os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    for _ in range(25):
        if not _pid_alive(pid):
            return True
        time.sleep(0.2)
    return not _pid_alive(pid)