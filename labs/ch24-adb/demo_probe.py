"""第 24 章演示：接上手机就打印真实画像，没接就告诉你怎么接。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from labs._shared.adb import AdbError, Device  # noqa: E402

from probe import collect, report  # noqa: E402

SHOT = Path(__file__).resolve().parent / "out" / "device.png"


def main() -> int:
    try:
        device = Device.first_online(timeout=5)
    except AdbError as exc:
        print(f"没有可用设备：{exc}")
        print("检查顺序：数据线 → 开发者选项里的 USB 调试 → 手机上的「允许调试」弹窗 → adb devices")
        return 0

    SHOT.parent.mkdir(parents=True, exist_ok=True)
    info = collect(device, screenshot_to=SHOT)
    print(report(info))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
