import pytest

from shenle_device_record import devices

SAMPLE = """List of devices attached
emulator-5554          device product:sdk_gphone64_x86_64 model:sdk_gphone64_x86_64 device:emu64xa transport_id:1
ABC123XYZ              device product:raven model:Pixel_6_Pro device:raven transport_id:2
"""


def test_parse_two_devices():
    devs = devices.parse_adb_devices(SAMPLE)
    assert [d.serial for d in devs] == ["emulator-5554", "ABC123XYZ"]
    assert devs[0].state == "device"
    assert devs[1].model == "Pixel_6_Pro"


def test_parse_skips_daemon_noise_and_blank_lines():
    out = (
        "* daemon not running; starting now at tcp:5037\n"
        "* daemon started successfully\n"
        "List of devices attached\n"
        "\n"
    )
    assert devices.parse_adb_devices(out) == []


def test_parse_unauthorized_without_model():
    devs = devices.parse_adb_devices("List of devices attached\n1234567890\tunauthorized usb:1-2\n")
    assert devs[0].serial == "1234567890"
    assert devs[0].state == "unauthorized"
    assert devs[0].model == ""


def test_describe_includes_state_and_model():
    dev = devices.Device(serial="ABC", state="device", model="Pixel_6_Pro")
    text = dev.describe()
    assert "ABC" in text and "device" in text and "Pixel_6_Pro" in text


def test_pick_first_ready_device():
    devs = devices.parse_adb_devices(SAMPLE)
    assert devices.pick_device(devs).serial == "emulator-5554"


def test_pick_by_explicit_id():
    devs = devices.parse_adb_devices(SAMPLE)
    assert devices.pick_device(devs, "ABC123XYZ").serial == "ABC123XYZ"


def test_pick_unknown_id_raises_and_lists_available():
    devs = devices.parse_adb_devices(SAMPLE)
    with pytest.raises(devices.DeviceSelectionError) as err:
        devices.pick_device(devs, "NOPE")
    assert "找不到设备" in str(err.value)
    assert "ABC123XYZ" in str(err.value)


def test_pick_empty_list_raises():
    with pytest.raises(devices.DeviceSelectionError) as err:
        devices.pick_device([])
    assert "没有检测到" in str(err.value)


def test_pick_skips_when_all_unusable():
    devs = devices.parse_adb_devices("List of devices attached\nX\tunauthorized\n")
    with pytest.raises(devices.DeviceSelectionError) as err:
        devices.pick_device(devs)
    assert "均不可用" in str(err.value)


def test_pick_named_device_in_bad_state():
    devs = devices.parse_adb_devices("List of devices attached\nX\toffline\n")
    with pytest.raises(devices.DeviceSelectionError) as err:
        devices.pick_device(devs, "X")
    assert "offline" in str(err.value)


# --- 设备状态未识别时，错误信息不要带孤立的句号 / 空提示 --------------------------


def test_pick_named_device_unknown_state_no_empty_hint():
    devs = devices.parse_adb_devices("List of devices attached\nX\tsideload\n")
    with pytest.raises(devices.DeviceSelectionError) as err:
        devices.pick_device(devs, "X")
    msg = str(err.value)
    assert "sideload" in msg
    # 状态未识别时没有提示，错误信息不应以 "。 " 或 "。" 结尾
    assert not msg.rstrip().endswith("。 "), f"意外的孤立分隔符：{msg!r}"
    assert not msg.rstrip().endswith("。。"), f"出现了双重句号：{msg!r}"


def test_pick_all_unusable_unknown_state_no_empty_hint():
    devs = devices.parse_adb_devices("List of devices attached\nX\tsideload\n")
    with pytest.raises(devices.DeviceSelectionError) as err:
        devices.pick_device(devs)
    msg = str(err.value)
    assert "sideload" in msg
    assert "均不可用" in msg
    # 不应在没有 hint 的情况下以 "。 " 结尾
    assert not msg.rstrip().endswith("。 "), f"意外的孤立分隔符：{msg!r}"


def test_pick_named_device_known_state_keeps_hint():
    devs = devices.parse_adb_devices("List of devices attached\nX\tunauthorized\n")
    with pytest.raises(devices.DeviceSelectionError) as err:
        devices.pick_device(devs, "X")
    msg = str(err.value)
    assert "unauthorized" in msg
    assert "USB 调试" in msg  # 已知状态 hint 必须保留


# --- 关键排查步骤必须出现在错误文案里 --------------------------


def test_pick_empty_list_lists_kill_server_recovery():
    """空设备列表的报错必须引导到 USB 调试 / 弹窗 / kill-server 重连。"""
    with pytest.raises(devices.DeviceSelectionError) as err:
        devices.pick_device([])
    msg = str(err.value)
    assert "USB 调试" in msg, "应提示开启 USB 调试"
    assert "允许" in msg, "应提示在弹窗里点允许"
    assert "adb kill-server" in msg, "应提示 kill-server 重连"


def test_pick_named_device_unauthorized_mentions_kill_server():
    """unauthorized 状态的 hint 必须提到 kill-server 重连（用户明确要求）。"""
    devs = devices.parse_adb_devices("List of devices attached\nX\tunauthorized\n")
    with pytest.raises(devices.DeviceSelectionError) as err:
        devices.pick_device(devs, "X")
    msg = str(err.value)
    assert "USB 调试" in msg
    assert "adb kill-server" in msg


# --- list_devices：adb 退出非零且 stderr 为空时给兜底文案 --------------------------


def test_list_devices_adb_nonzero_with_empty_stderr(monkeypatch):
    """adb 退出非零、stderr 为空时，报错不能只冒号收尾。"""
    import subprocess

    from shenle_device_record import devices

    monkeypatch.setattr(devices.shutil, "which", lambda name: "/usr/bin/adb")
    monkeypatch.setattr(
        devices.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0] if args else [],
            returncode=1,
            stdout="",
            stderr="",
        ),
    )
    with pytest.raises(devices.AdbError) as err:
        devices.list_devices()
    msg = str(err.value)
    assert "退出码 1" in msg
    # 必须有兜底文案，不能以 "：" 收尾
    assert not msg.rstrip().endswith("："), f"末尾缺兜底文案：{msg!r}"
    assert "adb 未给出具体错误信息" in msg


def test_list_devices_adb_nonzero_with_stderr_keeps_stderr(monkeypatch):
    """stderr 非空时仍要把原始 stderr 透传出来。"""
    import subprocess

    from shenle_device_record import devices

    monkeypatch.setattr(devices.shutil, "which", lambda name: "/usr/bin/adb")
    monkeypatch.setattr(
        devices.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0] if args else [],
            returncode=2,
            stdout="",
            stderr="error: device unauthorized",
        ),
    )
    with pytest.raises(devices.AdbError) as err:
        devices.list_devices()
    msg = str(err.value)
    assert "退出码 2" in msg
    assert "error: device unauthorized" in msg
