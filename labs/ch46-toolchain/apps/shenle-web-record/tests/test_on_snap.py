import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock

from shenle_web_record.session import RecorderSession


PAYLOAD = {"module": "电商-用户中心", "func": "登录", "desc": "输入正确的用户名和密码能正确登录"}


def _make_session(tmp_path: Path) -> RecorderSession:
    s = RecorderSession(url="https://example.com", output_root=str(tmp_path))
    # Mock the page dependency; AsyncMock so `await page.evaluate(...)` works.
    s._page = AsyncMock()
    s._seq = 1
    return s


def test_happy_path_writes_files_and_advances_seq(tmp_path: Path):
    s = _make_session(tmp_path)

    # Make the mocked screenshot actually write an empty PNG so png.exists() holds.
    s._page.screenshot.side_effect = lambda path, **kw: Path(path).write_bytes(b"")

    snapshot = {"role": "WebArea", "name": "Example", "children": []}
    s._page.evaluate.side_effect = [None, None]      # hide + restore
    s._page.aria_snapshot.return_value = snapshot

    result = asyncio.run(s._on_snap(PAYLOAD))

    assert result == {"ok": True, "seq": "001"}
    assert s._seq == 2

    # Multi-level path: <batch>/电商/用户中心/登录/{img,json}
    target = s._batch_dir / "电商" / "用户中心" / "登录"
    png = target / "img" / "screenshot_001.png"
    dom = target / "json" / "dom_001.json"
    assert png.exists(), f"expected PNG at {png}"
    assert dom.exists(), f"expected JSON at {dom}"
    payload = json.loads(dom.read_text(encoding="utf-8"))
    assert payload == {
        "content": snapshot,
        "img": "img/screenshot_001.png",
        "module": "电商-用户中心",
        "func": "登录",
        "desc": "输入正确的用户名和密码能正确登录",
    }

    s._page.aria_snapshot.assert_called_once_with()
    s._page.screenshot.assert_called_once_with(
        path=str(png),
        full_page=False,
    )


def test_single_segment_module(tmp_path: Path):
    """module without '-' still creates a valid single-level folder."""
    s = _make_session(tmp_path)
    s._page.screenshot.side_effect = lambda path, **kw: Path(path).write_bytes(b"")
    s._page.evaluate.side_effect = [None, None]
    s._page.aria_snapshot.return_value = "snap"

    result = asyncio.run(s._on_snap({"module": "管理后台", "func": "用户列表", "desc": ""}))

    assert result == {"ok": True, "seq": "001"}
    target = s._batch_dir / "管理后台" / "用户列表"
    assert (target / "img" / "screenshot_001.png").exists()
    payload = json.loads((target / "json" / "dom_001.json").read_text(encoding="utf-8"))
    assert payload["desc"] == ""      # desc optional, allowed to be empty
    assert payload["module"] == "管理后台"


def test_validation_rejects_missing_module(tmp_path: Path):
    s = _make_session(tmp_path)
    result = asyncio.run(s._on_snap({"module": "", "func": "登录", "desc": ""}))
    assert result["ok"] is False
    assert "模块" in result["error"]
    assert s._seq == 1                 # not advanced


def test_validation_rejects_missing_func(tmp_path: Path):
    s = _make_session(tmp_path)
    result = asyncio.run(s._on_snap({"module": "电商-用户中心", "func": "  ", "desc": ""}))
    assert result["ok"] is False
    assert "功能" in result["error"]
    assert s._seq == 1


def test_validation_rejects_none_payload(tmp_path: Path):
    """Defensive: payload may arrive as None or missing entirely."""
    s = _make_session(tmp_path)
    result = asyncio.run(s._on_snap(None))
    assert result["ok"] is False
    assert s._seq == 1


def test_failure_does_not_increment_seq(tmp_path: Path, capsys):
    s = _make_session(tmp_path)
    s._page.evaluate.side_effect = [None, None]      # hide (ok), restore never reached
    s._page.aria_snapshot.side_effect = RuntimeError("boom")

    result = asyncio.run(s._on_snap(PAYLOAD))

    # Core promise: failure does NOT advance the sequence counter
    assert result["ok"] is False
    assert s._seq == 1
    # No files anywhere under the batch dir on failure.
    # (v3: the target dir is created before capture, so it may exist empty;
    # the screenshot may also be written. The contract is: no JSON, no
    # sequence advance, no leftover files with a higher seq number.)
    assert list((s._batch_dir / "电商" / "用户中心" / "登录" / "json").iterdir()) == []


def test_global_seq_advances_across_funcs(tmp_path: Path):
    """seq is global: clicking a different func still continues numbering."""
    s = _make_session(tmp_path)
    s._page.screenshot.side_effect = lambda path, **kw: Path(path).write_bytes(b"")
    s._page.evaluate.side_effect = [None, None, None, None]
    s._page.aria_snapshot.return_value = "snap"

    p1 = {"module": "电商-用户中心", "func": "登录", "desc": ""}
    p2 = {"module": "电商-用户中心", "func": "注册", "desc": ""}

    r1 = asyncio.run(s._on_snap(p1))
    r2 = asyncio.run(s._on_snap(p2))

    assert r1 == {"ok": True, "seq": "001"}
    assert r2 == {"ok": True, "seq": "002"}
    assert (s._batch_dir / "电商" / "用户中心" / "登录" / "img" / "screenshot_001.png").exists()
    assert (s._batch_dir / "电商" / "用户中心" / "注册" / "img" / "screenshot_002.png").exists()