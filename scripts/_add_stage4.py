"""Insert the APP stage into both sidebars of config.mts."""

from pathlib import Path

ITEMS = [
    (24, "ADB 与设备连接"),
    (25, "元素定位与窗口树"),
    (26, "页面对象与页面栈"),
    (27, "手势与输入"),
    (28, "数据驱动与多用例"),
    (29, "稳定性与失败留证"),
    (30, "logcat 与崩溃定位"),
    (31, "框架收口（APP CLI）"),
]

BLOCK = (
    "        {\n"
    "          text: '第四阶段 · APP 终端 UI 自动化',\n"
    "          items: [\n"
    + "".join(
        "            { text: '" + str(n) + " " + t + "', link: '/chapters/ch" + str(n) + "' },\n"
        for n, t in ITEMS
    )
    + "          ]\n"
    "        },\n"
)

path = Path("site/.vitepress/config.mts")
text = path.read_text(encoding="utf-8")
needle = "        {\n          text: '延伸阅读',"
count = text.count(needle)
if count != 2:
    raise SystemExit("unexpected sidebar blocks: " + str(count))
if "第四阶段" in text:
    raise SystemExit("stage 4 already present")
path.write_text(text.replace(needle, BLOCK + needle), encoding="utf-8")
print("inserted stage 4 blocks:", count)
