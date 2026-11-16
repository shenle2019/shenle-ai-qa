"""把 JUnit XML 渲染成一页 HTML：通过率、耗时、失败详情。"""

from __future__ import annotations

import html
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>接口测试报告</title>
<style>
  body{{font:14px/1.6 -apple-system,"Segoe UI",sans-serif;margin:32px;color:#1f2328;background:#f6f8fa}}
  h1{{font-size:22px;margin:0 0 4px}}
  .sub{{color:#57606a;margin-bottom:20px}}
  .cards{{display:flex;gap:12px;margin-bottom:20px}}
  .card{{background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:14px 18px;min-width:120px}}
  .num{{font-size:26px;font-weight:700}}
  .ok{{color:#1a7f37}} .bad{{color:#cf222e}}
  table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid #d0d7de;border-radius:10px;overflow:hidden}}
  th,td{{text-align:left;padding:8px 12px;border-bottom:1px solid #eaeef2;font-size:13px;vertical-align:top}}
  th{{background:#f6f8fa;font-weight:600}}
  tr:last-child td{{border-bottom:none}}
  code{{font-family:ui-monospace,Consolas,monospace;font-size:12px;white-space:pre-wrap}}
  .fail{{color:#cf222e;font-weight:600}}
</style></head><body>
<h1>接口测试报告</h1>
<div class="sub">{when} · {suite}</div>
<div class="cards">
  <div class="card"><div>用例</div><div class="num">{tests}</div></div>
  <div class="card"><div>通过</div><div class="num ok">{passed}</div></div>
  <div class="card"><div>失败</div><div class="num bad">{failed}</div></div>
  <div class="card"><div>总耗时</div><div class="num">{time}s</div></div>
  <div class="card"><div>通过率</div><div class="num {rate_class}">{rate}%</div></div>
</div>
<table><thead><tr><th>用例</th><th>耗时</th><th>结果</th><th>说明</th></tr></thead><tbody>
{rows}
</tbody></table>
</body></html>
"""


def parse(xml_path: Path) -> dict:
    root = ET.parse(xml_path).getroot()
    cases = []
    for case in root.iter("testcase"):
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        cases.append(
            {
                "name": f"{case.get('classname', '')}::{case.get('name', '')}".lstrip(":"),
                "time": float(case.get("time") or 0),
                "status": "failed" if (failure is not None or error is not None) else ("skipped" if skipped is not None else "passed"),
                "message": (failure.text if failure is not None else error.text if error is not None else "") or "",
            }
        )
    return {
        "suite": root.get("name", "pytest"),
        "time": float(root.get("time") or 0),
        "cases": cases,
    }


def render(data: dict, when: str = "") -> str:
    cases = data["cases"]
    total = len(cases)
    failed = sum(1 for c in cases if c["status"] == "failed")
    passed = total - failed
    rate = round(passed * 100 / total, 1) if total else 0.0
    rows = []
    for c in sorted(cases, key=lambda x: (x["status"] != "failed", -x["time"])):
        cls = "fail" if c["status"] == "failed" else ""
        msg = html.escape(c["message"][:400])
        rows.append(
            f'<tr><td><code>{html.escape(c["name"])}</code></td><td>{c["time"]:.2f}s</td>'
            f'<td class="{cls}">{c["status"]}</td><td><code>{msg}</code></td></tr>'
        )
    return TEMPLATE.format(
        when=html.escape(when),
        suite=html.escape(data["suite"]),
        tests=total,
        passed=passed,
        failed=failed,
        time=f'{data["time"]:.2f}',
        rate=rate,
        rate_class="ok" if rate >= 95 else "bad",
        rows="\n".join(rows),
    )


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("用法: report.py <junit.xml> <out.html>")
        return 2
    data = parse(Path(argv[1]))
    Path(argv[2]).write_text(render(data), encoding="utf-8")
    print(f"写入 {argv[2]}：{len(data['cases'])} 条用例")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
