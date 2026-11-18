"""两种报告：给人看的 Markdown，给 CI 看的 JUnit XML。都不引第三方库。"""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from fw_runner import Report


def to_markdown(report: Report) -> str:
    lines = [
        f"# 执行报告 · {report.env}",
        "",
        f"- 地址：{report.base_url}",
        f"- 合计：{report.total} 条，通过 {report.passed}，失败 {report.failed}",
        "",
        "| 用例 | 标题 | 结果 | 耗时 | 说明 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in report.results:
        flag = "通过" if item.ok else "失败"
        detail = item.detail.replace("|", "\\|")
        lines.append(f"| {item.case_id} | {item.title} | {flag} | {item.duration_ms} ms | {detail} |")
    return "\n".join(lines) + "\n"


def to_junit(report: Report) -> str:
    suite = ET.Element(
        "testsuite",
        {
            "name": f"web-{report.env}",
            "tests": str(report.total),
            "failures": str(report.failed),
            "errors": "0",
        },
    )
    for item in report.results:
        case = ET.SubElement(
            suite,
            "testcase",
            {"classname": f"web.{report.env}", "name": item.case_id, "time": f"{item.duration_ms / 1000:.3f}"},
        )
        if not item.ok:
            failure = ET.SubElement(case, "failure", {"message": item.detail[:200]})
            failure.text = f"{item.title}\n{item.detail}"
    return ET.tostring(suite, encoding="unicode")


def write(report: Report, path: Path | str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix.lower() == ".xml":
        target.write_text(to_junit(report), encoding="utf-8")
    else:
        target.write_text(to_markdown(report), encoding="utf-8")
    return target
