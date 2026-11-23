import threading
import time

import pytest

from shenle_device_record.server.lifecycle import LifecycleManager


class _NoopWSFactory:
    async def __call__(self, websocket):
        pass


def _make_manager(tmp_path, *, process_enum=None):
    if process_enum is None:
        process_enum = lambda pid: []  # 默认：没有浏览器活着
    return LifecycleManager(
        host="127.0.0.1",
        port=18765,  # 测试专用端口
        device_id="ABC",
        output_root=str(tmp_path),
        platform="android",
        no_browser=True,  # 单测不起 Playwright
        ws_handler_factory=_NoopWSFactory(),
        static_root=str(tmp_path),
        process_enumerator=process_enum,
        browser_name_hint="chrom",
    )


def test_browser_alive_returns_false_when_no_processes(tmp_path):
    m = _make_manager(tmp_path)
    m._browser_proc_pid = 99999  # 模拟有 subprocess pid
    assert m._browser_alive() is False


def test_browser_alive_returns_true_when_chromium_listed(tmp_path):
    m = _make_manager(tmp_path, process_enum=lambda pid: ["chromium.exe", "node.exe"])
    m._browser_proc_pid = 99999
    assert m._browser_alive() is True


def test_browser_alive_ignores_unrelated_processes(tmp_path):
    m = _make_manager(tmp_path, process_enum=lambda pid: ["notepad.exe", "explorer.exe"])
    m._browser_proc_pid = 99999
    assert m._browser_alive() is False


def test_browser_alive_false_when_no_pid(tmp_path):
    """没起 Playwright subprocess 时（--no-browser），不能误判。"""
    m = _make_manager(tmp_path)
    m._browser_proc_pid = None
    # 即便外部有 chromium 进程，也不应该让本服务等它
    assert m._browser_alive() is False


def test_browser_alive_falls_back_to_recent_client_activity(tmp_path):
    """当没起 Playwright 时（--no-browser 或 Playwright 进程没了），
    改用 WebSocket 客户端最近活跃度：5s 内有活动视为活着。
    """
    m = _make_manager(tmp_path)
    m._browser_proc_pid = None
    # 模拟客户端刚发过消息
    m._last_client_activity = time.monotonic()
    assert m._browser_alive() is True
    # 模拟客户端 11 秒没活动
    m._last_client_activity = time.monotonic() - 11
    assert m._browser_alive() is False


def test_browser_alive_falls_back_to_ws_when_pid_set_but_enum_empty(tmp_path):
    """pid 已设但 process_enumerator 返回空（进程消失）时，
    应该降级看 WS 客户端最近活跃度（spec "双信号"）—— 5s 内活跃即视为 alive。
    """
    # 枚举器返回空列表 —— 模拟 Playwright 子进程全部退出
    m = _make_manager(tmp_path, process_enum=lambda pid: [])
    m._browser_proc_pid = 99999
    # 客户端最近 5s 内活跃
    m._last_client_activity = time.monotonic()
    assert m._browser_alive() is True


def test_browser_alive_returns_false_when_pid_set_enum_empty_and_client_idle(tmp_path):
    """pid 已设、枚举空、客户端超时 —— 必须判定为已死，等规格要求退出。
    """
    m = _make_manager(tmp_path, process_enum=lambda pid: [])
    m._browser_proc_pid = 99999
    # 客户端 11 秒没活动
    m._last_client_activity = time.monotonic() - 11
    assert m._browser_alive() is False


def test_wait_for_browser_exit_returns_when_browser_dead(tmp_path):
    m = _make_manager(tmp_path)
    m._browser_proc_pid = 99999
    # 立刻设 stop_event 模拟浏览器已关
    def _shutdown():
        time.sleep(0.05)
        m._stop_event.set()
    threading.Thread(target=_shutdown, daemon=True).start()
    result = m.wait_for_browser_exit(timeout=2.0)
    assert result is True