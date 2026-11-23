import pytest

from shenle_device_record import LOG_PREFIX as GLOBAL_LOG_PREFIX
from shenle_device_record import cli


def test_platform_constants():
    assert cli.ALL_PLATFORMS == ("android", "ios", "harmony", "pc")
    assert cli.SUPPORTED_PLATFORMS == ("android",)


def test_log_prefix_unified():
    """cli.LOG_PREFIX 必须等于 shenle_device_record.LOG_PREFIX（同一对象）。"""
    assert cli.LOG_PREFIX == GLOBAL_LOG_PREFIX == "[shenle-device-record]"


def test_parser_requires_platform():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["record"])


def test_parser_rejects_unknown_platform():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["record", "--platform", "windows"])


def test_parser_defaults():
    args = cli.build_parser().parse_args(["record", "--platform", "android"])
    assert args.command == "record"
    assert args.platform == "android"
    assert args.device_id is None
    assert args.output == "."


def test_parser_accepts_device_and_output():
    args = cli.build_parser().parse_args(
        ["record", "--platform", "android", "--device-id", "ABC", "-o", "/tmp/x"]
    )
    assert args.device_id == "ABC"
    assert args.output == "/tmp/x"


@pytest.mark.parametrize("platform", ["ios", "harmony", "pc"])
def test_main_rejects_unimplemented_platforms(platform, capsys):
    assert cli.main(["record", "--platform", platform]) == 2
    assert "暂未支持" in capsys.readouterr().err


def test_main_without_subcommand_prints_help(capsys):
    assert cli.main([]) == 1
    assert "usage" in capsys.readouterr().out.lower()


def test_record_once_writes_expected_layout(tmp_path, monkeypatch):
    """打桩掉 adb 与 midscene，验证落盘结构与 JSON 字段。"""
    from shenle_device_record import devices as devices_mod
    from shenle_device_record import midscene as midscene_mod
    from shenle_device_record import recorder

    fake_png = tmp_path / "fake_shot.png"
    fake_png.write_bytes(b"\x89PNG\r\n\x1a\n")

    monkeypatch.setattr(
        recorder.devices_mod,
        "list_devices",
        lambda: [devices_mod.Device(serial="ABC", state="device", model="Pixel")],
    )
    monkeypatch.setattr(recorder.midscene, "take_screenshot", lambda serial: fake_png)
    monkeypatch.setattr(
        recorder.midscene, "dump_hierarchy", lambda serial: "<hierarchy><node/></hierarchy>"
    )

    out_root = tmp_path / "out"
    out_root.mkdir()
    assert recorder.record_once("android", None, str(out_root)) == 0

    import json

    jsons = list((out_root / "AI-信息采集").rglob("android_001.json"))
    pngs = list((out_root / "AI-信息采集").rglob("screenshot_001.png"))
    assert len(jsons) == 1
    assert len(pngs) == 1
    assert jsons[0].parent.name == "json"
    assert pngs[0].parent.name == "img"
    assert jsons[0].parent.parent == pngs[0].parent.parent

    payload = json.loads(jsons[0].read_text(encoding="utf-8"))
    assert list(payload.keys()) == ["content", "img", "module", "func", "desc"]
    assert payload["img"] == "img/screenshot_001.png"
    assert payload["content"] == "<hierarchy><node/></hierarchy>"
    assert payload["module"] == "未分类"
    assert payload["func"] == "未分类"
    assert payload["desc"] == ""
    assert not fake_png.exists()  # 临时文件已清理


def test_record_once_multiple_devices_suggests_device_id(tmp_path, monkeypatch, capsys):
    """检测到多台可用设备、用户没传 --device-id 时，日志必须提示可用 --device-id 指定。"""
    from shenle_device_record import devices as devices_mod
    from shenle_device_record import recorder

    fake_png = tmp_path / "fake_shot.png"
    fake_png.write_bytes(b"\x89PNG\r\n\x1a\n")
    monkeypatch.setattr(
        recorder.devices_mod,
        "list_devices",
        lambda: [
            devices_mod.Device(serial="emulator-5554", state="device", model="Pixel_5"),
            devices_mod.Device(serial="ABC123XYZ", state="device", model="Pixel_6_Pro"),
        ],
    )
    monkeypatch.setattr(recorder.midscene, "take_screenshot", lambda serial: fake_png)
    monkeypatch.setattr(recorder.midscene, "dump_hierarchy", lambda serial: "")

    out_root = tmp_path / "out"
    out_root.mkdir()
    assert recorder.record_once("android", None, str(out_root)) == 0
    log = capsys.readouterr().out
    assert "--device-id" in log, f"多设备时日志应提示可用 --device-id 指定，实际：{log!r}"
    assert "ABC123XYZ" in log, "设备列表要打出每台 serial 方便用户挑选"


def test_record_once_explicit_device_id_logged(tmp_path, monkeypatch, capsys):
    """用户传了 --device-id 时，启动日志里要明确写出来，避免用了别的设备用户一脸懵。"""
    from shenle_device_record import devices as devices_mod
    from shenle_device_record import recorder

    fake_png = tmp_path / "fake_shot.png"
    fake_png.write_bytes(b"\x89PNG\r\n\x1a\n")
    monkeypatch.setattr(
        recorder.devices_mod,
        "list_devices",
        lambda: [
            devices_mod.Device(serial="emulator-5554", state="device"),
            devices_mod.Device(serial="ABC123XYZ", state="device"),
        ],
    )
    monkeypatch.setattr(recorder.midscene, "take_screenshot", lambda serial: fake_png)
    monkeypatch.setattr(recorder.midscene, "dump_hierarchy", lambda serial: "")

    out_root = tmp_path / "out"
    out_root.mkdir()
    assert recorder.record_once("android", "ABC123XYZ", str(out_root)) == 0
    log = capsys.readouterr().out
    assert "--device-id" in log and "ABC123XYZ" in log, (
        f"传了 --device-id 时日志要打印出来，实际：{log!r}"
    )


def test_record_once_does_not_overwrite(tmp_path, monkeypatch):
    """同一功能目录采第二次，序号递增到 002，旧文件保留。"""
    from shenle_device_record import devices as devices_mod
    from shenle_device_record import recorder

    monkeypatch.setattr(
        recorder.devices_mod,
        "list_devices",
        lambda: [devices_mod.Device(serial="ABC", state="device")],
    )
    monkeypatch.setattr(recorder.midscene, "dump_hierarchy", lambda serial: "")

    out_root = tmp_path / "out"
    out_root.mkdir()
    fixed_batch = "20260829-171149"
    monkeypatch.setattr(recorder.paths, "generate_batch_id", lambda: fixed_batch)

    for index in range(2):
        shot = tmp_path / f"shot_{index}.png"
        shot.write_bytes(b"x")
        monkeypatch.setattr(recorder.midscene, "take_screenshot", lambda serial, s=shot: s)
        assert recorder.record_once("android", None, str(out_root)) == 0

    target = out_root / "AI-信息采集" / fixed_batch / "未分类" / "未分类"
    assert sorted(p.name for p in (target / "img").iterdir()) == [
        "screenshot_001.png",
        "screenshot_002.png",
    ]
    assert sorted(p.name for p in (target / "json").iterdir()) == [
        "android_001.json",
        "android_002.json",
    ]


def test_record_once_reports_adb_missing(tmp_path, monkeypatch, capsys):
    from shenle_device_record import devices as devices_mod
    from shenle_device_record import recorder

    def boom():
        raise devices_mod.AdbError("找不到 adb。")

    monkeypatch.setattr(recorder.devices_mod, "list_devices", boom)
    assert recorder.record_once("android", None, str(tmp_path)) == 1
    assert "找不到 adb" in capsys.readouterr().err


def test_record_once_reports_midscene_failure(tmp_path, monkeypatch, capsys):
    """midscene 截图失败：退出码 1，stderr 给出中文报错。"""
    from shenle_device_record import devices as devices_mod
    from shenle_device_record import midscene as midscene_mod
    from shenle_device_record import recorder

    monkeypatch.setattr(
        recorder.devices_mod,
        "list_devices",
        lambda: [devices_mod.Device(serial="ABC", state="device")],
    )

    def boom(serial):
        raise midscene_mod.MidsceneError("midscene 截图失败（退出码 1）。")

    monkeypatch.setattr(recorder.midscene, "take_screenshot", boom)

    out_root = tmp_path / "out"
    out_root.mkdir()
    assert recorder.record_once("android", None, str(out_root)) == 1
    assert "midscene 截图失败" in capsys.readouterr().err
    # 失败发生在落盘之前，不该留下任何批次产物
    assert not (out_root / "AI-信息采集").exists()


def test_record_once_reports_device_selection_error(tmp_path, monkeypatch, capsys):
    """设备列表为空 → pick_device 抛 DeviceSelectionError：退出码 1 + 中文报错。"""
    from shenle_device_record import recorder

    monkeypatch.setattr(recorder.devices_mod, "list_devices", lambda: [])

    def unreachable(serial):  # pragma: no cover - 断言不会走到截图这一步
        raise AssertionError("选设备失败后不应该再调用 midscene")

    monkeypatch.setattr(recorder.midscene, "take_screenshot", unreachable)

    out_root = tmp_path / "out"
    out_root.mkdir()
    assert recorder.record_once("android", None, str(out_root)) == 1
    assert "没有检测到任何安卓设备" in capsys.readouterr().err
    assert not (out_root / "AI-信息采集").exists()


def test_record_once_writes_payload_when_hierarchy_empty(tmp_path, monkeypatch):
    """核心契约：抓层级失败（返回空串）只警告不中断，照常落盘。"""
    import json

    from shenle_device_record import devices as devices_mod
    from shenle_device_record import recorder

    fake_png = tmp_path / "fake_shot.png"
    fake_png.write_bytes(b"\x89PNG\r\n\x1a\n")

    monkeypatch.setattr(
        recorder.devices_mod,
        "list_devices",
        lambda: [devices_mod.Device(serial="ABC", state="device")],
    )
    monkeypatch.setattr(recorder.midscene, "take_screenshot", lambda serial: fake_png)
    monkeypatch.setattr(recorder.midscene, "dump_hierarchy", lambda serial: "")

    out_root = tmp_path / "out"
    out_root.mkdir()
    assert recorder.record_once("android", None, str(out_root)) == 0

    jsons = list((out_root / "AI-信息采集").rglob("android_001.json"))
    pngs = list((out_root / "AI-信息采集").rglob("screenshot_001.png"))
    assert len(jsons) == 1
    assert len(pngs) == 1

    payload = json.loads(jsons[0].read_text(encoding="utf-8"))
    assert list(payload.keys()) == ["content", "img", "module", "func", "desc"]
    assert payload["content"] == ""
    assert payload["img"] == "img/screenshot_001.png"
    assert not fake_png.exists()


def test_record_once_cleans_temp_screenshot_on_copy_failure(tmp_path, monkeypatch, capsys):
    """落盘中途失败（copyfile 抛 OSError）时，退出码 1、中文报错、临时截图被删。"""
    from shenle_device_record import devices as devices_mod
    from shenle_device_record import recorder

    fake_png = tmp_path / "fake_shot.png"
    fake_png.write_bytes(b"\x89PNG\r\n\x1a\n")

    monkeypatch.setattr(
        recorder.devices_mod,
        "list_devices",
        lambda: [devices_mod.Device(serial="ABC", state="device")],
    )
    monkeypatch.setattr(recorder.midscene, "take_screenshot", lambda serial: fake_png)
    monkeypatch.setattr(recorder.midscene, "dump_hierarchy", lambda serial: "")

    def boom(src, dst, **kwargs):
        raise OSError("磁盘写入失败")

    monkeypatch.setattr(recorder.shutil, "copyfile", boom)

    out_root = tmp_path / "out"
    out_root.mkdir()
    assert recorder.record_once("android", None, str(out_root)) == 1

    err = capsys.readouterr().err
    assert "落盘失败" in err
    assert "磁盘写入失败" in err
    assert not fake_png.exists()  # 失败路径同样不泄漏临时文件


def test_recorder_log_prefix_unified():
    """recorder.LOG_PREFIX 必须等于 shenle_device_record.LOG_PREFIX。"""
    from shenle_device_record import recorder

    assert recorder.LOG_PREFIX == GLOBAL_LOG_PREFIX == "[shenle-device-record]"


# --- serve 子命令 -----------------------------------------------------------


def test_parser_serve_basic():
    args = cli.build_parser().parse_args(
        ["serve", "--platform", "android", "--port", "9000", "--no-browser"]
    )
    assert args.command == "serve"
    assert args.platform == "android"
    assert args.port == 9000
    assert args.no_browser is True
    assert args.device_id is None
    assert args.output == "."


def test_parser_serve_defaults():
    args = cli.build_parser().parse_args(["serve", "--platform", "android"])
    assert args.port == 8765
    assert args.no_browser is False


@pytest.mark.parametrize("platform", ["ios", "harmony", "pc"])
def test_serve_rejects_unimplemented_platforms(platform, capsys):
    assert cli.main(["serve", "--platform", platform, "--no-browser"]) == 2
    assert "暂未支持" in capsys.readouterr().err