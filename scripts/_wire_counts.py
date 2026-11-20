"""把计数改成 39 章 / 417 条，并给索引表补 ch33–39。"""

from pathlib import Path

CH = [
    ("ch33", "场景设计：基准、负载、压力、稳定性", "labs/ch33-scenarios", "场景与拐点", 10),
    ("ch34", "压测脚本与参数化", "labs/ch34-scripts", "步骤/数据/思考时间", 10),
    ("ch35", "结果分析与瓶颈定位", "labs/ch35-analyze", "平台期与归因", 8),
    ("ch36", "中间件性能要点", "labs/ch36-middleware", "日志/池/队列", 8),
    ("ch37", "全链路压测与数据隔离", "labs/ch37-chain", "打标与隔离", 8),
    ("ch38", "AI 辅助性能分析", "labs/ch38-ai", "异常/聚类/提示词", 8),
    ("ch39", "性能平台收口", "labs/ch39-perf-platform", "配置/门槛/报告", 9),
]

CHAP_ROWS = "".join(f"| {s[2:]} | {t} | `{lab}` |\n" for s, t, lab, _, _ in CH)
LAB_ROWS = "".join(f"| {s[2:]} | `{lab}` | {files} | {n} |\n" for s, _, lab, files, n in CH)

files = Path("site/chapters/index.md")
body = files.read_text(encoding="utf-8")
if "| 33 |" not in body:
    anchor = "| 32 | 性能测试基础与指标 | `labs/ch32-perf-basics` |\n"
    if anchor in body:
        body = body.replace(anchor, anchor + CHAP_ROWS, 1)
    else:
        body = body.rstrip("\n") + "\n" + CHAP_ROWS
    files.write_text(body, encoding="utf-8")
    print("chapters/index rows added")

labs = Path("site/labs/index.md")
body = labs.read_text(encoding="utf-8")
if "| 33 |" not in body:
    body = body.rstrip("\n") + "\n" + LAB_ROWS
    labs.write_text(body, encoding="utf-8")
    print("labs/index rows added")

repl = [
    ("356 条 pytest 用例", "417 条 pytest 用例"),
    ("三十二个实操", "三十九个实操"),
    ("合计 **356 条测试**", "合计 **417 条测试**"),
    ("32 章 / 356 条", "39 章 / 417 条"),
    ("**32 章", "**39 章"),
    ("32 章 ·", "39 章 ·"),
]
for target in [Path("site/index.md"), Path("site/chapters/index.md"), Path("site/labs/index.md"), Path("README.md"), Path("STAGE-BRIEF.md")]:
    text = target.read_text(encoding="utf-8")
    original = text
    for old, new in repl:
        text = text.replace(old, new)
    text = text.replace("32 章", "39 章") if "32 章" in text and "39 章" not in text else text
    if text != original:
        target.write_text(text, encoding="utf-8")
        print("counts ->", target)
