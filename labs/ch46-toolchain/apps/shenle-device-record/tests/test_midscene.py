import base64
import subprocess

import pytest

from shenle_device_record import LOG_PREFIX as GLOBAL_LOG_PREFIX
from shenle_device_record import midscene


def test_log_prefix_unified_with_package():
    """三个模块的日志前缀必须统一指向 __init__.py 里的常量。"""
    assert midscene.LOG_PREFIX == GLOBAL_LOG_PREFIX == "[shenle-device-record]"


def test_midscene_timeout_is_generous_for_first_run():
    """首次跑 npx @midscene/android 要从 npm 拉大依赖树，给到 300s 兜底。"""
    assert midscene.MIDSCENE_TIMEOUT >= 300.0


def test_extract_image_path_windows_backslash():
    out = "Screenshot saved to: C:\\Users\\me\\AppData\\Local\\Temp\\midscene\\shot_1.png\nDone."
    assert midscene.extract_image_path(out) == "C:\\Users\\me\\AppData\\Local\\Temp\\midscene\\shot_1.png"


def test_extract_image_path_posix_with_spaces():
    out = "image: /var/folders/My Temp/shot 2.png"
    assert midscene.extract_image_path(out) == "/var/folders/My Temp/shot 2.png"


def test_extract_image_path_takes_last_match():
    out = "log /tmp/old.png\nresult: /tmp/new.png"
    assert midscene.extract_image_path(out) == "/tmp/new.png"


def test_extract_image_path_supports_jpeg():
    assert midscene.extract_image_path("saved /tmp/a.jpeg") == "/tmp/a.jpeg"


def test_extract_image_path_none_when_absent():
    assert midscene.extract_image_path("no image here") is None
    assert midscene.extract_image_path("") is None


def test_extract_hierarchy_with_xml_declaration():
    out = 'noise\n<?xml version="1.0"?><hierarchy rotation="0"><node text="a"/></hierarchy>\nbye'
    got = midscene.extract_hierarchy_xml(out)
    assert got.startswith("<?xml")
    assert got.endswith("</hierarchy>")
    assert "node" in got


def test_extract_hierarchy_without_declaration():
    out = '<hierarchy rotation="0"><node/></hierarchy>'
    assert midscene.extract_hierarchy_xml(out) == out


def test_extract_hierarchy_missing_returns_empty():
    assert midscene.extract_hierarchy_xml("UI hierchary dumped to: /sdcard/x.xml") == ""
    assert midscene.extract_hierarchy_xml("") == ""


def test_extract_base64_from_data_uri():
    payload = "A" * 300
    assert midscene.extract_image_base64(f"data:image/png;base64,{payload}") == payload


def test_extract_base64_bare_blob():
    payload = "B" * 1200
    assert midscene.extract_image_base64(f"result: {payload}") == payload


def test_extract_base64_none_for_short_output():
    assert midscene.extract_image_base64("short output") is None


# --- URL 解析：网络协议整段剔除；file:// 还原成本地路径 -------------------------


def test_extract_image_path_ignores_http_url():
    assert midscene.extract_image_path("report: http://example.com/foo.png") is None


def test_extract_image_path_ignores_https_url():
    assert midscene.extract_image_path("see https://cdn.example.com/a/b/c.jpeg") is None


def test_extract_image_path_ignores_ftp_url():
    assert midscene.extract_image_path("uploaded to ftp://files.example.com/x.png") is None


def test_extract_image_path_converts_posix_file_url():
    # midscene 真机上的典型输出：Saved to: file:///tmp/shot.png
    assert midscene.extract_image_path("Saved to: file:///tmp/shot.png") == "/tmp/shot.png"


def test_extract_image_path_converts_windows_drive_file_url():
    # Windows 盘符形式，刻意保留正斜杠与下游 _IMAGE_PATH_RE 兼容
    assert (
        midscene.extract_image_path("Saved to: file:///C:/Temp/shot.png")
        == "C:/Temp/shot.png"
    )


def test_extract_image_path_converts_file_url_with_percent_encoding():
    # 路径含空格，URL 里会被编码成 %20，必须解码
    assert (
        midscene.extract_image_path("Saved to: file:///tmp/my%20shot.png")
        == "/tmp/my shot.png"
    )


def test_extract_image_path_file_url_uppercase_scheme():
    # 大小写不敏感：macOS / 部分终端会输出 FILE://
    assert (
        midscene.extract_image_path("FILE:///tmp/shot.png").lower() == "/tmp/shot.png"
    )


def test_extract_image_path_takes_last_when_mixing_file_and_http():
    out = "log: file:///tmp/old.png\nreport: http://x.com/ignored.png\nsaved: file:///tmp/new.png"
    assert midscene.extract_image_path(out) == "/tmp/new.png"


def test_extract_image_path_local_path_after_url_still_found():
    out = "report: http://example.com/foo.png\nScreenshot saved to: /tmp/real.png"
    assert midscene.extract_image_path(out) == "/tmp/real.png"


def test_extract_image_path_realistic_midscene_saved_to():
    """midscene 真机上最常见的输出形态。"""
    out = "[midscene] connecting...\nSaved to: file:///data/local/tmp/midscene/abc123.png\nDone in 1.2s"
    assert (
        midscene.extract_image_path(out)
        == "/data/local/tmp/midscene/abc123.png"
    )


# --- AI 模型配置缺失识别（不要真起进程，只用打桩的输出） ------------------------


@pytest.mark.parametrize(
    "stderr_text",
    [
        "Error: OPENAI_API_KEY is not set",
        "missing api key for provider",
        "config.api_key is required",
        "MIDSCENE_MODEL not configured",
        "please provide model name in env",
        "modelName must be set (modelName field)",
    ],
)
def test_looks_like_ai_config_error_matches_known_keywords(stderr_text):
    assert midscene._looks_like_ai_config_error(stderr_text) is True


@pytest.mark.parametrize(
    "stderr_text",
    [
        "device offline",
        "permission denied",
        "command timed out",
    ],
)
def test_looks_like_ai_config_error_rejects_unrelated_output(stderr_text):
    assert midscene._looks_like_ai_config_error(stderr_text) is False


def test_looks_like_ai_config_error_handles_empty():
    assert midscene._looks_like_ai_config_error("") is False
    assert midscene._looks_like_ai_config_error(None) is False  # type: ignore[arg-type]


def test_ai_config_hint_mentions_required_env_vars():
    hint = midscene._ai_config_hint()
    assert "OPENAI_API_KEY" in hint
    assert "MIDSCENE_MODEL_NAME" in hint
    assert "midscene" in hint.lower()


def test_take_screenshot_appends_ai_hint_when_output_suggests_missing_config(monkeypatch):
    """子进程退出非零、输出含关键字时，错误信息要附加中文 AI 配置提示。"""
    monkeypatch.setattr(
        midscene,
        "_run",
        lambda args, timeout: _completed(
            returncode=1, stderr="Error: OPENAI_API_KEY is not set in env"
        ),
    )
    with pytest.raises(midscene.MidsceneError) as err:
        midscene.take_screenshot("SERIAL")
    msg = str(err.value)
    # 原始输出不能丢
    assert "OPENAI_API_KEY" in msg
    # 中文提示要附在后面
    assert "OPENAI_API_KEY" in msg and "MIDSCENE_MODEL_NAME" in msg
    assert "https://midscenejs.com" in msg


def test_take_screenshot_no_ai_hint_when_failure_unrelated(monkeypatch):
    monkeypatch.setattr(
        midscene,
        "_run",
        lambda args, timeout: _completed(returncode=1, stderr="device offline"),
    )
    with pytest.raises(midscene.MidsceneError) as err:
        midscene.take_screenshot("SERIAL")
    msg = str(err.value)
    assert "device offline" in msg
    # 不相关失败不应附带 AI 配置提示，避免误导
    assert "OPENAI_API_KEY" not in msg
    assert "MIDSCENE_MODEL_NAME" not in msg


# --- base64 兜底必须校验图片魔数 --------------------------------------------------


def test_take_screenshot_rejects_base64_that_is_not_an_image(monkeypatch, tmp_path):
    """stderr 里夹带的长 base64 日志（请求体 dump 等）不能被当成图片落盘。"""
    # 构造一段解码后不是 PNG/JPEG 的 base64（纯 ASCII "AAAAAAAA..."）
    fake_blob = "A" * 1200
    stdout = f"dump: {fake_blob}"
    monkeypatch.setattr(
        midscene,
        "_run",
        lambda args, timeout: _completed(returncode=0, stdout=stdout),
    )

    # 记录 mkstemp 是否被调用，避免落盘垃圾文件
    mkstemp_called = []

    real_mkstemp = midscene.tempfile.mkstemp

    def spy_mkstemp(*args, **kwargs):
        mkstemp_called.append((args, kwargs))
        return real_mkstemp(*args, **kwargs)

    monkeypatch.setattr(midscene.tempfile, "mkstemp", spy_mkstemp)

    with pytest.raises(midscene.MidsceneError) as err:
        midscene.take_screenshot("SERIAL")

    assert mkstemp_called == [], "不应创建任何临时文件"
    msg = str(err.value)
    assert "没找到图片路径或图片数据" in msg


def test_take_screenshot_accepts_valid_png_base64(monkeypatch, tmp_path):
    """合法的 PNG base64 必须能落盘并返回。"""
    import base64 as _b64

    # 真实 PNG 头部 + 凑足 _BARE_B64_RE 要求的 1000+ 字符
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 1024
    payload = _b64.b64encode(png_bytes).decode("ascii")
    monkeypatch.setattr(
        midscene,
        "_run",
        lambda args, timeout: _completed(returncode=0, stdout=f"result: {payload}"),
    )

    result = midscene.take_screenshot("SERIAL")
    try:
        assert result.is_file()
        assert result.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    finally:
        result.unlink(missing_ok=True)


def test_take_screenshot_accepts_valid_jpeg_base64(monkeypatch):
    """合法的 JPEG base64 也必须能落盘。"""
    import base64 as _b64

    jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 1024
    payload = _b64.b64encode(jpeg_bytes).decode("ascii")
    monkeypatch.setattr(
        midscene,
        "_run",
        lambda args, timeout: _completed(returncode=0, stdout=f"data: {payload}"),
    )

    result = midscene.take_screenshot("SERIAL")
    try:
        assert result.is_file()
        assert result.read_bytes()[:3] == b"\xff\xd8\xff"
    finally:
        result.unlink(missing_ok=True)


# --- dump_hierarchy 的异常安全契约：永不抛异常，失败返回空串 + stderr 警告 ---------


def _completed(returncode: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(
        args=["npx"], returncode=returncode, stdout=stdout, stderr=stderr
    )


def _assert_warned_and_empty(result, capsys):
    err = capsys.readouterr().err
    assert result == ""
    assert midscene.LOG_PREFIX in err
    assert err.lstrip().startswith(midscene.LOG_PREFIX)


def test_dump_hierarchy_swallows_midscene_error(monkeypatch, capsys):
    def boom(args, timeout):
        raise midscene.MidsceneError("找不到 npx。")

    monkeypatch.setattr(midscene, "_run", boom)
    _assert_warned_and_empty(midscene.dump_hierarchy("SERIAL"), capsys)


def test_dump_hierarchy_swallows_os_error(monkeypatch, capsys):
    def boom(args, timeout):
        raise OSError(13, "Permission denied")

    monkeypatch.setattr(midscene, "_run", boom)
    _assert_warned_and_empty(midscene.dump_hierarchy("SERIAL"), capsys)


def test_dump_hierarchy_swallows_unexpected_exception(monkeypatch, capsys):
    def boom(args, timeout):
        raise ValueError("完全没预料到的错误")

    monkeypatch.setattr(midscene, "_run", boom)
    _assert_warned_and_empty(midscene.dump_hierarchy("SERIAL"), capsys)


def test_dump_hierarchy_returns_empty_on_nonzero_exit(monkeypatch, capsys):
    monkeypatch.setattr(
        midscene,
        "_run",
        lambda args, timeout: _completed(returncode=1, stderr="device offline"),
    )
    _assert_warned_and_empty(midscene.dump_hierarchy("SERIAL"), capsys)


def test_dump_hierarchy_returns_empty_when_no_xml(monkeypatch, capsys):
    monkeypatch.setattr(
        midscene,
        "_run",
        lambda args, timeout: _completed(
            returncode=0, stdout="UI hierchary dumped to: /sdcard/x.xml"
        ),
    )
    _assert_warned_and_empty(midscene.dump_hierarchy("SERIAL"), capsys)


def test_dump_hierarchy_happy_path(monkeypatch, capsys):
    xml = '<hierarchy rotation="0"><node text="a"/></hierarchy>'
    monkeypatch.setattr(
        midscene, "_run", lambda args, timeout: _completed(returncode=0, stdout=xml)
    )
    assert midscene.dump_hierarchy("SERIAL") == xml
    assert capsys.readouterr().err == ""


def test_dump_hierarchy_propagates_keyboard_interrupt(monkeypatch):
    """契约细化：KeyboardInterrupt / SystemExit 属于 BaseException，不能吞。"""
    def boom(args, timeout):
        raise KeyboardInterrupt()

    monkeypatch.setattr(midscene, "_run", boom)
    with pytest.raises(KeyboardInterrupt):
        midscene.dump_hierarchy("SERIAL")


def test_dump_hierarchy_propagates_system_exit(monkeypatch):
    """SystemExit 同理，必须放行，否则 sys.exit() 会被静默吞掉。"""
    def boom(args, timeout):
        raise SystemExit(0)

    monkeypatch.setattr(midscene, "_run", boom)
    with pytest.raises(SystemExit):
        midscene.dump_hierarchy("SERIAL")


# --- take_screenshot 的错误策略与 dump_hierarchy 相反：失败必须抛 MidsceneError -----


def test_take_screenshot_raises_on_nonzero_exit(monkeypatch):
    monkeypatch.setattr(
        midscene,
        "_run",
        lambda args, timeout: _completed(returncode=1, stderr="device offline"),
    )
    with pytest.raises(midscene.MidsceneError):
        midscene.take_screenshot("SERIAL")


def test_take_screenshot_raises_when_no_image_in_output(monkeypatch):
    monkeypatch.setattr(
        midscene, "_run", lambda args, timeout: _completed(returncode=0, stdout="done")
    )
    with pytest.raises(midscene.MidsceneError):
        midscene.take_screenshot("SERIAL")


def test_take_screenshot_propagates_run_error(monkeypatch):
    def boom(args, timeout):
        raise midscene.MidsceneError("超时")

    monkeypatch.setattr(midscene, "_run", boom)
    with pytest.raises(midscene.MidsceneError):
        midscene.take_screenshot("SERIAL")


# --- _run 把 OSError 在源头转换成 MidsceneError（不起真实子进程） -------------------


def test_run_converts_os_error_to_midscene_error(monkeypatch):
    monkeypatch.setattr(midscene.shutil, "which", lambda name: "/usr/bin/npx")

    def boom(*args, **kwargs):
        raise OSError(13, "Permission denied")

    monkeypatch.setattr(midscene.subprocess, "run", boom)
    with pytest.raises(midscene.MidsceneError):
        midscene._run(["take_screenshot"], 1.0)


def test_run_converts_timeout_to_midscene_error(monkeypatch):
    monkeypatch.setattr(midscene.shutil, "which", lambda name: "/usr/bin/npx")

    def boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="npx", timeout=1.0)

    monkeypatch.setattr(midscene.subprocess, "run", boom)
    with pytest.raises(midscene.MidsceneError):
        midscene._run(["take_screenshot"], 1.0)


def test_run_raises_midscene_error_when_npx_missing(monkeypatch):
    monkeypatch.setattr(midscene.shutil, "which", lambda name: None)
    with pytest.raises(midscene.MidsceneError):
        midscene._run(["take_screenshot"], 1.0)


# --- device_id 空串时不传 --device-id（避免 midscene yargs 解析成 boolean） ---


def test_take_screenshot_empty_device_id_omits_flag(monkeypatch):
    captured: dict[str, list[str]] = {}

    def fake_run(args, timeout):
        captured["args"] = args
        # 让后续 _run 假成功但最终 raise "no image"——我们只关心 args 内容
        import subprocess
        return subprocess.CompletedProcess(
            args=args, returncode=1, stdout="", stderr="",
        )

    monkeypatch.setattr(midscene, "_run", fake_run)
    with pytest.raises(midscene.MidsceneError):
        midscene.take_screenshot("")

    assert "--device-id" not in captured["args"], (
        f"device_id 为空时不应传 --device-id，实际：{captured['args']!r}"
    )
    assert "take_screenshot" in captured["args"]


def test_take_screenshot_nonempty_device_id_passes_flag(monkeypatch):
    captured: dict[str, list[str]] = {}

    def fake_run(args, timeout):
        captured["args"] = args
        import subprocess
        return subprocess.CompletedProcess(
            args=args, returncode=1, stdout="", stderr="",
        )

    monkeypatch.setattr(midscene, "_run", fake_run)
    with pytest.raises(midscene.MidsceneError):
        midscene.take_screenshot("ABC123")

    assert "--device-id" in captured["args"]
    idx = captured["args"].index("--device-id")
    assert captured["args"][idx + 1] == "ABC123"


def test_dump_hierarchy_empty_device_id_omits_flag(monkeypatch):
    """dump_hierarchy 在 device_id 空时也不传 --device-id。"""
    captured: dict[str, list[str]] = {}

    def fake_run(args, timeout):
        captured["args"] = args
        import subprocess
        return subprocess.CompletedProcess(
            args=args, returncode=1, stdout="", stderr="",
        )

    monkeypatch.setattr(midscene, "_run", fake_run)
    midscene.dump_hierarchy("")  # 永不抛
    assert "--device-id" not in captured["args"], (
        f"device_id 为空时不应传 --device-id，实际：{captured['args']!r}"
    )

