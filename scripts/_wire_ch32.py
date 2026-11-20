"""第 32 章上站：章节页 + 侧栏第五阶段 + 索引表与计数。"""

from pathlib import Path

NUM, SLUG = 32, "perf-basics"
TITLE = "第 32 章 · 性能测试基础与指标"
TOTAL_TESTS = 356  # 345 + 11

page = Path(f"site/chapters/ch{NUM}.md")
page.write_text(
    "---\ntitle: " + TITLE + "\n---\n\n<!--@include: ../../notes/ch" + str(NUM) + "-" + SLUG + ".md-->\n",
    encoding="utf-8",
)
print("page", page)

cfg = Path("site/.vitepress/config.mts")
text = cfg.read_text(encoding="utf-8")
if "第五阶段 · 性能测试" not in text:
    block = (
        "        {\n"
        "          text: '第五阶段 · 性能测试',\n"
        "          items: [\n"
        f"            {{ text: '{NUM} 性能测试基础与指标', link: '/chapters/ch{NUM}' }}\n"
        "          ]\n"
        "        },\n"
    )
    needle = "        {\n          text: '延伸阅读',"
    assert text.count(needle) == 2
    cfg.write_text(text.replace(needle, block + needle), encoding="utf-8")
    print("sidebar stage 5 added")

row_index = f"| {NUM} | 性能测试基础与指标 | ch{NUM} | labs/ch{NUM}-{SLUG} |"
row_labs = f"| {NUM} | labs/ch{NUM}-{SLUG} | metrics_demo.py | 分位值、TPS、错误率、Little's Law | 11 |"

idx = Path("site/index.md")
s = idx.read_text(encoding="utf-8")
if "### 第五阶段" not in s:
    s = s.replace(
        f"\n{TOTAL_TESTS - 11} 条 pytest 用例全绿",
        f"\n### 第五阶段 · 性能测试\n\n| 章 | 主题 | 笔记 | 实操 |\n| --- | --- | --- | --- |\n{row_index}\n\n{TOTAL_TESTS} 条 pytest 用例全绿",
    )
idx.write_text(s, encoding="utf-8")

chap = Path("site/chapters/index.md")
s = chap.read_text(encoding="utf-8")
if "### 第五阶段" not in s:
    s = s.rstrip("\n") + (
        "\n\n### 第五阶段 · 性能测试\n\n| 章 | 主题 | 笔记 | 实操 |\n| --- | --- | --- | --- |\n"
        f"| {NUM} | 性能测试基础与指标 | [ch{NUM}](/chapters/ch{NUM}) | labs/ch{NUM}-{SLUG} |\n"
    )
    s = s.replace("345 条", f"{TOTAL_TESTS} 条")
chap.write_text(s, encoding="utf-8")

labs = Path("site/labs/index.md")
s = labs.read_text(encoding="utf-8")
if "第五阶段" not in s:
    s = s.replace(
        "合计 **345 条测试**。",
        "## 第五阶段 · 性能测试\n\n| 章 | 实操目录 | 源文件 | 覆盖的知识点 | 测试 |\n| --- | --- | --- | --- | --- |\n"
        + row_labs
        + f"\n\n合计 **{TOTAL_TESTS} 条测试**。",
    )
labs.write_text(s, encoding="utf-8")

readme = Path("README.md")
s = readme.read_text(encoding="utf-8")
if "### 第五阶段" not in s:
    s = s.rstrip("\n") + (
        "\n\n### 第五阶段 · 性能测试\n\n| 章 | 主题 | 笔记 | 实操 |\n| --- | --- | --- | --- |\n"
        f"| {NUM} | 性能测试基础与指标 | [ch{NUM}](notes/ch{NUM}-{SLUG}.md) | labs/ch{NUM}-{SLUG} |\n"
    )
    s = s.replace("345 passed", f"{TOTAL_TESTS} passed").replace("345 条", f"{TOTAL_TESTS} 条")
readme.write_text(s, encoding="utf-8")

brief = Path("STAGE-BRIEF.md")
s = brief.read_text(encoding="utf-8")
s = s.replace("**345 条 pytest 全绿**", f"**{TOTAL_TESTS} 条 pytest 全绿（性能阶段进行中）**")
brief.write_text(s, encoding="utf-8")
print("indices patched, total", TOTAL_TESTS)
