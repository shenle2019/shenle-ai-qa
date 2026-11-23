import inspect

import pytest

from shenle_device_record.server import http_server
from shenle_device_record.server.http_server import StaticHandler

# 模块级保证 run_server 是协程函数；单元测试不实际启动服务。
assert inspect.iscoroutinefunction(http_server.run_server)


@pytest.fixture
def static_root(tmp_path):
    (tmp_path / "index.html").write_bytes("<!doctype html><h1>hi</h1>".encode("utf-8"))
    (tmp_path / "app.css").write_bytes(b"body{color:red}")
    (tmp_path / "app.js").write_bytes(b"console.log('ok')")
    return tmp_path


def test_render_root_returns_index_html(static_root):
    h = StaticHandler(static_root)
    status, headers, body = h.render("/")
    assert status == 200
    assert any(k.lower() == "content-type" and "text/html" in v for k, v in headers)
    assert b"hi" in body


def test_render_static_file_with_content_type(static_root):
    h = StaticHandler(static_root)
    status, headers, body = h.render("/app.css")
    assert status == 200
    assert any(k.lower() == "content-type" and "text/css" in v for k, v in headers)
    assert body == b"body{color:red}"


def test_render_static_file_js(static_root):
    h = StaticHandler(static_root)
    status, headers, body = h.render("/app.js")
    assert status == 200
    assert any(k.lower() == "content-type" and "javascript" in v for k, v in headers)


def test_render_ws_path_signals_upgrade(static_root):
    """`/ws` 必须返回特殊 status=101（表示"交给 websockets 库升级"）。"""
    h = StaticHandler(static_root)
    status, headers, body = h.render("/ws")
    assert status == 101
    assert body == b""


def test_render_unknown_path_returns_404(static_root):
    h = StaticHandler(static_root)
    status, headers, body = h.render("/does/not/exist")
    assert status == 404
    assert any(k.lower() == "content-type" and "text/plain" in v for k, v in headers)


def test_render_path_traversal_blocked(static_root):
    """路径穿越必须被拒绝（防止读 static_root 之外的文件）。"""
    h = StaticHandler(static_root)
    status, _, _ = h.render("/../etc/passwd")
    assert status == 404


def test_render_rejects_absolute_path(static_root):
    h = StaticHandler(static_root)
    status, _, _ = h.render("/C:/Windows/System32/drivers/etc/hosts")
    assert status == 404


def test_run_server_signature_exists():
    """run_server 必须存在且为可导入符号；不实际启动服务。"""
    from shenle_device_record.server.http_server import run_server

    assert callable(run_server)
    assert inspect.iscoroutinefunction(run_server)


@pytest.mark.asyncio
async def test_http_process_request_returns_websockets_response_for_known_path(static_root):
    """已知路径（如 /）必须返回 websockets.http11.Response，且 status_code/body 正确。

    修复 websockets 14+ 的 process_request API（不再接受 tuple）后必须有这条断言。
    """
    import types

    import websockets.http11

    h = StaticHandler(static_root)
    fake_request = types.SimpleNamespace(path="/")
    result = await http_server.http_process_request(None, fake_request, h)

    assert isinstance(result, websockets.http11.Response)
    assert result.status_code == 200
    assert b"hi" in result.body
    # Content-Length 与 Content-Type 必须经 Response.headers 传出去
    assert any(h.lower() == "content-type" and "text/html" in v for h, v in result.headers.raw_items())
    assert any(h.lower() == "content-length" for h, _ in result.headers.raw_items())


@pytest.mark.asyncio
async def test_http_process_request_returns_none_for_ws_path(static_root):
    """/ws 必须返回 None（让 websockets 库走升级分支）。"""
    import types

    h = StaticHandler(static_root)
    fake_request = types.SimpleNamespace(path="/ws")
    result = await http_server.http_process_request(None, fake_request, h)
    assert result is None


@pytest.mark.asyncio
async def test_http_process_request_returns_404_response_for_unknown(static_root):
    """未知路径必须返回 404 Response。"""
    import types

    import websockets.http11

    h = StaticHandler(static_root)
    fake_request = types.SimpleNamespace(path="/does/not/exist")
    result = await http_server.http_process_request(None, fake_request, h)

    assert isinstance(result, websockets.http11.Response)
    assert result.status_code == 404