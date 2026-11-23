"""编排一次采集：选设备 → 截图 → 抓层级 → 落盘。"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from shenle_device_record import LOG_PREFIX, devices as devices_mod
from shenle_device_record import midscene, paths

# 第一阶段没有输入通道，三个业务字段用固定占位；后续网页阶段接真实值。
PLACEHOLDER_MODULE = paths.DEFAULT_SEGMENT
PLACEHOLDER_FUNC = paths.DEFAULT_SEGMENT
PLACEHOLDER_DESC = ""


def _log(message: str) -> None:
    print(f"{LOG_PREFIX} {message}")


def _error(message: str) -> None:
    print(f"{LOG_PREFIX} 错误：{message}", file=sys.stderr)


def _warn(message: str) -> None:
    print(f"{LOG_PREFIX} 警告：{message}", file=sys.stderr)


def record_once(platform: str, device_id: str | None, output_root: str) -> int:
    """采集一次并落盘。返回进程退出码。"""
    try:
        found = devices_mod.list_devices()
    except devices_mod.AdbError as exc:
        _error(str(exc))
        return 1

    listing = ", ".join(d.describe() for d in found) or "无"
    _log(f"adb 检测到 {len(found)} 台设备：{listing}")
    if found:
        if device_id:
            _log(f"按 --device-id 指定：{device_id}")
        else:
            ready = [d for d in found if d.state == "device"]
            if len(ready) > 1:
                _log(
                    f"检测到 {len(ready)} 台可用设备，将使用第一台。"
                    f"如需指定其他设备，加 --device-id <serial>。"
                )

    try:
        device = devices_mod.pick_device(found, device_id)
    except devices_mod.DeviceSelectionError as exc:
        _error(str(exc))
        return 1
    _log(f"使用设备：{device.describe()}")

    try:
        shot = midscene.take_screenshot(device.serial)
    except midscene.MidsceneError as exc:
        _error(str(exc))
        return 1
    _log(f"截图临时文件：{shot}")

    content = midscene.dump_hierarchy(device.serial)
    if content:
        _log(f"界面层级已获取，{len(content)} 字符")
    else:
        _log("界面层级未获取，content 留空")

    # midscene 产生的临时截图必须删干净：从算批次目录开始，到写完 JSON 为止，
    # 任何一步抛异常都要在 finally 里把临时文件清掉。只捕获 Exception，
    # 让 KeyboardInterrupt / SystemExit 继续向上传播。
    try:
        batch_id = paths.generate_batch_id()
        batch_dir = paths.make_batch_dir(output_root, batch_id)
        target_dir = paths.build_target_dir(batch_dir, PLACEHOLDER_MODULE, PLACEHOLDER_FUNC)
        img_dir = target_dir / paths.IMG_SUBDIR
        json_dir = target_dir / paths.JSON_SUBDIR
        img_dir.mkdir(parents=True, exist_ok=True)
        json_dir.mkdir(parents=True, exist_ok=True)

        seq = paths.next_seq(target_dir)
        img_path = img_dir / paths.screenshot_filename(seq)
        json_path = json_dir / paths.json_filename(platform, seq)

        shutil.copyfile(shot, img_path)
        payload = paths.build_payload(
            content=content,
            img=paths.img_relpath(seq),
            module=PLACEHOLDER_MODULE,
            func=PLACEHOLDER_FUNC,
            desc=PLACEHOLDER_DESC,
        )
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as exc:
        _error(f"落盘失败：{exc}")
        return 1
    finally:
        try:
            Path(shot).unlink(missing_ok=True)
        except OSError as exc:
            _warn(f"临时截图删除失败（{shot}）：{exc}")

    _log(f"批次目录：{batch_dir}")
    _log(f"已保存截图：{img_path}")
    _log(f"已保存 JSON：{json_path}")
    return 0