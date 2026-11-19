"""Append the APP stage to the site index, chapter index, labs index and README."""

from pathlib import Path

ROWS = [
    (24, "ADB 与设备连接", "ch24", "ch24-adb"),
    (25, "元素定位与窗口树", "ch25", "ch25-locators"),
    (26, "页面对象与页面栈", "ch26", "ch26-page-object"),
    (27, "手势与输入", "ch27", "ch27-gestures"),
    (28, "数据驱动与多用例", "ch28", "ch28-data-driven"),
    (29, "稳定性与失败留证", "ch29", "ch29-stability"),
    (30, "logcat 与崩溃定位", "ch30", "ch30-logcat"),
    (31, "框架收口（APP CLI）", "ch31", "ch31-framework"),
]

TOPICS = {
    24: "设备状态、系统版本、分辨率、端口反代",
    25: "id/文字/描述/类型四种定位，歧义检测",
    26: "页面类、动作返回下一页、Activity 校验",
    27: "输入清空、长按、滑动、返回、收键盘",
    28: "yaml 用例 + 动作表 + 失败不中断",
    29: "条件等待、带退避的重试、三样失败证据",
    30: "FATAL/ANR 特征行、按包名过滤、日志摘要",
    31: "配置校验、CLI 参数、Markdown 报告、退出码",
}

TESTS = {24: 6, 25: 8, 26: 7, 27: 9, 28: 8, 29: 8, 30: 8, 31: 8}
SHARED = 24
TOTAL = 259 + SHARED + sum(TESTS.values())


def stage_table() -> str:
    lines = ["", "### 第四阶段 · APP 终端 UI 自动化", "", "| 章 | 主题 | 笔记 | 实操 |", "| --- | --- | --- | --- |"]
    for num, title, note, lab in ROWS:
        lines.append("| " + f"{num:02d}" + " | " + title + " | " + note + " | " + "labs/" + lab + " |")
    return "\n".join(lines) + "\n"


def patch_index() -> None:
    p = Path("site/index.md")
    s = p.read_text(encoding="utf-8")
    if "### 第四阶段 · APP 终端 UI 自动化" in s:
        return
    marker = "\n259 条 pytest 用例全绿，二十三个实操都能单独运行："
    assert marker in s
    s = s.replace(marker, stage_table() + f"\n{TOTAL} 条 pytest 用例全绿，三十一个实操都能单独运行：")
    s = s.replace(
        "第三阶段：Web 与 APP 自动化无关的收尾",
        "第五阶段：Agent 与大模型评估",
    )
    p.write_text(s, encoding="utf-8")
    print("index patched")


def patch_chapters_index() -> None:
    p = Path("site/chapters/index.md")
    s = p.read_text(encoding="utf-8")
    if "### 第四阶段 · APP 终端 UI 自动化" in s:
        return
    rows = "\n".join(
        "| " + f"{num:02d}" + " | " + title + " | " + "[" + note + "](/chapters/" + note + ") | " + "labs/" + lab + " |"
        for num, title, note, lab in ROWS
    )
    block = "\n### 第四阶段 · APP 终端 UI 自动化\n\n| 章 | 主题 | 笔记 | 实操 |\n| --- | --- | --- | --- |\n" + rows + "\n"
    s = s.rstrip("\n") + "\n" + block
    s = s.replace("259 条", str(TOTAL) + " 条")
    p.write_text(s, encoding="utf-8")
    print("chapters index patched")


def patch_labs_index() -> None:
    p = Path("site/labs/index.md")
    s = p.read_text(encoding="utf-8")
    if "### 第四阶段 · APP 终端 UI 自动化" in s:
        return
    rows = "\n".join(
        "| " + f"{num:02d}" + " | " + "labs/" + lab + " | " + lab + ".py | " + TOPICS[num] + " | " + str(TESTS[num]) + " |"
        for num, title, note, lab in ROWS
    )
    block = (
        "\n## 第四阶段 · APP 终端 UI 自动化\n\n"
        "| 章 | 实操目录 | 源文件 | 覆盖的知识点 | 测试 |\n| --- | --- | --- | --- | --- |\n"
        + rows
        + "\n"
    )
    s = s.replace("合计 259 条测试。", block.strip() + f"\n\n合计 {TOTAL} 条测试。")
    p.write_text(s, encoding="utf-8")
    print("labs index patched")


def patch_readme() -> None:
    p = Path("README.md")
    s = p.read_text(encoding="utf-8")
    if "### 第四阶段 · APP 终端 UI 自动化" in s:
        return
    rows = "\n".join(
        "| " + f"{num:02d}" + " | " + title + " | " + "[" + note + "](notes/" + note + ".md) | " + "labs/" + lab + " |"
        for num, title, note, lab in ROWS
    )
    block = "\n### 第四阶段 · APP 终端 UI 自动化\n\n| 章 | 主题 | 笔记 | 实操 |\n| --- | --- | --- | --- |\n" + rows + "\n"
    s = s.rstrip("\n") + "\n" + block
    s = s.replace("259 passed", str(TOTAL) + " passed").replace("259 条", str(TOTAL) + " 条")
    p.write_text(s, encoding="utf-8")
    print("readme patched")


def patch_brief() -> None:
    p = Path("STAGE-BRIEF.md")
    s = p.read_text(encoding="utf-8")
    s = s.replace("第 16 章（Web 自动化起点），**196 条 pytest 全绿**", f"第 16–31 章（Web + APP 自动化），**{TOTAL} 条 pytest 全绿**")
    s = s.replace("第 01–07 章（Python 与工程基础）、第 08–15 章（接口自动化）、第 16 章（Web 自动化起点），**196 条 pytest 全绿**",
                  f"第 01–07 章（Python 与工程基础）、第 08–15 章（接口自动化）、第 16–23 章（Web 自动化）、第 24–31 章（APP 终端 UI 自动化），**{TOTAL} 条 pytest 全绿**")
    p.write_text(s, encoding="utf-8")
    print("stage brief patched")


patch_index()
patch_chapters_index()
patch_labs_index()
patch_readme()
patch_brief()
print("total", TOTAL)
