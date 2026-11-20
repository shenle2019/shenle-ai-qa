# -*- coding: utf-8 -*-
"""把 40–45 章从「性能测试」里拆出来，单独立为第六阶段。"""

import re
from pathlib import Path

ROWS = {
    "40": "平台架构与最小可用",
    "41": "项目配置与环境上下文",
    "42": "接口资产与一致性校验",
    "43": "用例与关键字执行器",
    "44": "测试计划与异步执行",
    "45": "平台收口",
}

# 1) 侧栏：把 40–45 从第五阶段移出，单独成组
cfg = Path("site/.vitepress/config.mts")
text = cfg.read_text(encoding="utf-8")

old = "".join(
    f"            {{ text: '{num} {title}', link: '/chapters/ch{num}' }},\n"
    for num, title in ROWS.items()
)
assert text.count(old) == 2, text.count(old)

new = (
    "          ]\n"
    "        },\n"
    "        {\n"
    "          text: '第六阶段 · AI 测试平台与工具',\n"
    "          items: [\n"
    + "".join(f"            {{ text: '{num} {title}', link: '/chapters/ch{num}' }},\n" for num, title in ROWS.items())
    + "          ]\n"
    "        },\n"
)
# 把「39 行 + 40–45 行 + ] },」替换为「39 行 + ] }, + 新组」
text = text.replace(
    "            { text: '39 性能平台收口', link: '/chapters/ch39' },\n" + old + "          ]\n        },\n",
    "            { text: '39 性能平台收口', link: '/chapters/ch39' },\n" + new,
)
cfg.write_text(text, encoding="utf-8")
assert text.count("第六阶段 · AI 测试平台与工具") == 2


# 2) 三个索引页：把 40–45 的行从原位剪掉，另起一节
def strip_rows(body: str) -> str:
    for num in ROWS:
        body = re.sub(rf"^\| {num} \|[^\n]*\n", "", body, flags=re.M)
    return body


def fence(body: str, anchor: str) -> str:
    rows = "".join(
        f"| {num} | {title} | `labs/ch{num}-*` |\n" for num, title in ROWS.items()
    )
    section = "## 第六阶段 · AI 测试平台与工具\n\n| 章 | 主题 | 实操目录 |\n| --- | --- | --- |\n" + rows + "\n"
    return body.replace(anchor, section + anchor, 1)


for path, anchor in [
    ("site/labs/index.md", "## 怎么跑"),
    ("site/index.md", "## 仓库结构"),
    ("site/chapters/index.md", "## 后续规划"),
]:
    p = Path(path)
    body = strip_rows(p.read_text(encoding="utf-8"))
    if "第六阶段 · AI 测试平台与工具" not in body:
        body = fence(body, anchor)
    p.write_text(body, encoding="utf-8")

print("split stage six ok")
