"""device-record 补一个最小示例（bash 块），把 D8 补满。"""

from __future__ import annotations

from pathlib import Path

path = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "shenle-device-record" / "SKILL.md"
text = path.read_text(encoding="utf-8")
if "## 示例" in text:
    print("已有示例，跳过")
    raise SystemExit(0)

example = """## 示例

最小一次采集（单台设备，采完就能在产物目录看到时间戳批次）：

```bash
adb devices                                  # 确认状态是 device
shenle-device-record record                  # 抓当前屏幕 + 层级，写入时间戳批次
ls <产物目录>/<最新批次>                      # 应看到截图 PNG 与 JSON 各一份
```

多台设备时换成：

```bash
shenle-device-record record -s FA7B11A03073
```

"""
text = text.replace("## 报错对照", example + "## 报错对照", 1)
path.write_text(text, encoding="utf-8")
print("已补示例，正文", len(text.splitlines()), "行")
