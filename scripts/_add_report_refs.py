"""给 report 技能补 references/ 并加触发声明，把 D5 补到 14。"""

from __future__ import annotations

from pathlib import Path

root = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "shenle-report-generate-html"
refs = root / "references"
refs.mkdir(exist_ok=True)
doc = refs / "report-structure.md"
if not doc.exists():
    doc.write_text(
        """# report.html 的结构约定

生成脚本按这个结构渲染，改版时先读这份，别只改 HTML 模板。

## 顶部信息区

- 计划 ID、时间戳、总耗时、通过率
- 数据来源：`allure-results/*-result.json` 的聚合结果，不是渲染时现算

## 摘要卡片

| 卡片 | 含义 |
| --- | --- |
| 总数 | 本轮 case 数 |
| 通过 | status 为 passed |
| 失败 | status 为 failed，含断言失败 |
| 异常 | status 为 broken，环境或脚本异常 |
| 跳过 | status 为 skipped，含未满足前置 |

## 逐 case 卡片

- 标题、状态徽章、耗时、描述
- 失败时展示错误信息（红色高亮）
- 步骤树：每个 task 四个嵌套子步骤 input / detail / result / output
- 附件内嵌：JSON pretty-print，文本原样，图片转 base64

## 体积约定

附件内嵌会把体积放大数倍；单个 HTML 超过 5 MB 就先裁附件或改外链。
""",
        encoding="utf-8",
    )
    print("写入", doc)

path = root / "SKILL.md"
text = path.read_text(encoding="utf-8")
if "references/report-structure.md" not in text:
    text = text.replace(
        "## 执行顺序",
        "## 先读约定\n\nMANDATORY：动手前先读 `references/report-structure.md`，HTML 结构与体积约定都在那里；"
        "正文只讲判断与避坑。\n\n## 执行顺序",
        1,
    )
    path.write_text(text, encoding="utf-8")
print("正文", len(text.splitlines()), "行")
