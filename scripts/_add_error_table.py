"""给 device-record 补一张 ≥6 行的报错对照表，把 D8 补回来。"""

from __future__ import annotations

from pathlib import Path

path = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "shenle-device-record" / "SKILL.md"
text = path.read_text(encoding="utf-8")
if "## 报错对照" in text:
    print("已有报错对照，跳过")
    raise SystemExit(0)

table = """
## 报错对照

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `device unauthorized` | 手机上没点允许调试 | 点允许；还不行进 `adb kill-server` 重插 |
| `device offline` | 线材或 USB 口不稳 | 换线换口，再 `adb devices` 复核 |
| `more than one device/emulator` | 多设备没带 `-s` | 加 `-s <serial>` |
| 层级里只有 `com.android.systemui` | 锁屏或系统弹窗盖住 | 解锁、关弹窗再采 |
| JSON 里 `elements` 为空 | 页面是自绘或 WebView | 改走截图 + 视觉描述 |
| 找不到产物目录 | 工作目录不可写 | 换可写目录或显式指定输出根 |
| `record` 秒退无输出 | 依赖缺失或版本不匹配 | 先 `--version` 与 `--help` 各跑一次定位 |
"""

text = text.replace("## 速查表在 references 里", table.strip() + "\n\n## 速查表在 references 里", 1)
path.write_text(text, encoding="utf-8")
print("已补报错对照，正文", len(text.splitlines()), "行")
