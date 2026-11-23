"""shenle-report-generate-html：把 allure-results/ JSON 数据渲染成单文件静态 HTML 报告。

用法：
    python generate_html.py \
        --project-dir "D:\\示例项目-读书屋" \
        --plan-id "plan-20260610182912" \
        --timestamp "20260924-220724"

    # 自动选最近一次
    python generate_html.py \
        --project-dir "D:\\示例项目-读书屋" \
        --plan-id "plan-20260610182912" \
        --latest

输出：
    <project-dir>/AI-自动化测试报告/<plan-id>/<timestamp>/report.html

设计目标：
    - 零依赖：纯 Python 标准库（json / pathlib / html）
    - 单文件 HTML：所有 CSS 内联、所有附件 inline（base64 或直接文本），方便分享
    - 可打印：颜色友好 + 折叠式 case section

不需要 Allure CLI / Java 环境。
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# allure-results 读取
# ---------------------------------------------------------------------------


def parse_allure_results(results_dir: Path) -> list[dict[str, Any]]:
    """读 allure-results/ 下所有 *-result.json，返回 case list。

    每个 case 是 allure result.json 的内容（dict），含 steps / attachments / status 等。
    """
    cases: list[dict[str, Any]] = []
    for f in sorted(results_dir.glob("*-result.json")):
        try:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
            cases.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[WARN] 跳过损坏的 {f.name}: {e}", file=sys.stderr)
    return cases


def index_attachments(results_dir: Path) -> dict[str, Path]:
    """把 allure-results/ 下所有附件按 source 名索引。

    allure 文件命名：<uuid>-attachment.<ext>，step 里 attachments[].source 指向这个文件名。
    """
    index: dict[str, Path] = {}
    for f in results_dir.glob("*-attachment.*"):
        index[f.name] = f
    return index


def load_attachment_content(
    attachment: dict[str, Any],
    attachment_index: dict[str, Path],
) -> tuple[str, str]:
    """读单个附件，返回 (content_text, content_type)。

    - JSON 文件 → pretty-printed JSON
    - TXT 文件 → 原始文本
    - HTML 文件 → 原始 HTML（保留格式）
    - 不存在的附件 → "[附件文件丢失: <source>]"
    """
    source = attachment.get("source", "")
    att_type = attachment.get("type", "")
    if not source or source not in attachment_index:
        return f"[附件文件丢失: {source}]", att_type

    path = attachment_index[source]
    try:
        raw = path.read_bytes()
    except OSError:
        return f"[读取失败: {path}]", att_type

    # 尝试解码
    text: str | None = None
    for enc in ("utf-8", "utf-8-sig", "gbk", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = raw.decode("utf-8", errors="replace")

    # JSON 文件 pretty-print
    if "json" in att_type or source.endswith(".json"):
        try:
            obj = json.loads(text)
            text = json.dumps(obj, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            pass

    return text, att_type


# ---------------------------------------------------------------------------
# 统计
# ---------------------------------------------------------------------------


def summarize(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """统计 total / passed / failed / broken / skipped 等。"""
    status_counter: Counter[str] = Counter()
    total_duration_ms = 0
    for c in cases:
        status = c.get("status", "unknown")
        status_counter[status] += 1
        # allure 9.x: statusDetails 含 message
        # stop / start 在 result.json 里（毫秒时间戳）
        stop_ms = c.get("stop", 0)
        start_ms = c.get("start", 0)
        if stop_ms and start_ms:
            total_duration_ms += stop_ms - start_ms
    return {
        "total": len(cases),
        "by_status": dict(status_counter),
        "total_duration_ms": total_duration_ms,
    }


# ---------------------------------------------------------------------------
# HTML 渲染
# ---------------------------------------------------------------------------


_CSS = r"""
:root {
  --bg: #f6f8fa;
  --card-bg: #ffffff;
  --text: #1f2328;
  --muted: #6e7781;
  --border: #d0d7de;
  --green: #1a7f37;
  --green-bg: #dafbe1;
  --red: #cf222e;
  --red-bg: #ffebe9;
  --yellow: #9a6700;
  --yellow-bg: #fff8c5;
  --gray-bg: #f6f8fa;
  --code-bg: #f6f8fa;
  --link: #0969da;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  margin: 0;
  padding: 32px;
  line-height: 1.6;
}
.container { max-width: 1200px; margin: 0 auto; }
h1 { font-size: 28px; margin: 0 0 8px; }
h2 { font-size: 22px; margin: 32px 0 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
.meta { color: var(--muted); font-size: 14px; margin-bottom: 24px; }

/* 摘要卡片 */
.summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}
.metric {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}
.metric .num { font-size: 32px; font-weight: 600; line-height: 1.2; }
.metric .label { color: var(--muted); font-size: 13px; margin-top: 4px; }
.metric.passed .num { color: var(--green); }
.metric.failed .num { color: var(--red); }
.metric.broken .num { color: var(--yellow); }
.metric.skipped .num { color: var(--muted); }

/* Case 卡片 */
.case {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}
.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.case-title { font-size: 18px; font-weight: 600; margin: 0; }
.case-desc { color: var(--muted); font-size: 13px; margin-top: 4px; white-space: pre-wrap; }

/* 状态徽章 */
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}
.badge.passed { background: var(--green-bg); color: var(--green); }
.badge.failed { background: var(--red-bg); color: var(--red); }
.badge.broken { background: var(--yellow-bg); color: var(--yellow); }
.badge.skipped { background: var(--gray-bg); color: var(--muted); }
.badge.unknown { background: var(--gray-bg); color: var(--muted); }

/* 折叠 details */
details.case-steps { margin-top: 8px; }
details.case-steps > summary {
  cursor: pointer;
  color: var(--link);
  font-size: 14px;
  user-select: none;
  padding: 6px 0;
}
details[open].case-steps > summary::before { content: "▼ "; }
details:not([open]).case-steps > summary::before { content: "▶ "; }

/* 步骤树 */
.steps { margin-left: 8px; }
.step {
  border-left: 2px solid var(--border);
  padding: 4px 0 4px 12px;
  margin: 4px 0;
}
.step.failed { border-left-color: var(--red); }
.step.broken { border-left-color: var(--yellow); }
.step.passed { border-left-color: var(--green); }
.step-name { font-weight: 500; }
.step-status { font-size: 12px; color: var(--muted); margin-left: 8px; }

/* 附件 */
.attachment {
  margin: 8px 0;
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
}
.attachment-name {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 6px;
  font-family: ui-monospace, SFMono-Regular, "Cascadia Code", "Source Code Pro", monospace;
}
.attachment pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, "Cascadia Code", "Source Code Pro", monospace;
  font-size: 12.5px;
  line-height: 1.5;
  max-height: 480px;
  overflow-y: auto;
}
.fail-msg {
  background: var(--red-bg);
  border-left: 4px solid var(--red);
  padding: 12px;
  border-radius: 4px;
  margin: 8px 0;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 12.5px;
  white-space: pre-wrap;
  word-break: break-word;
}
.footer { text-align: center; color: var(--muted); font-size: 12px; margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--border); }
@media print {
  body { background: white; padding: 8px; }
  details.case-steps { display: block !important; }
  details.case-steps > summary { display: none; }
}
"""


def status_label(status: str) -> str:
    return {"passed": "通过", "failed": "失败", "broken": "异常",
            "skipped": "跳过", "unknown": "未知"}.get(status, status)


def format_duration(ms: int) -> str:
    if ms < 1000:
        return f"{ms} ms"
    if ms < 60_000:
        return f"{ms / 1000:.2f} s"
    return f"{ms / 60_000:.1f} min"


def render_attachment(att: dict[str, Any], attachment_index: dict[str, Path]) -> str:
    """渲染单个附件为 HTML。"""
    name = html.escape(att.get("name", "?"))
    content, _ = load_attachment_content(att, attachment_index)
    content_escaped = html.escape(content)
    return (
        f'<div class="attachment">'
        f'<div class="attachment-name">📎 {name}</div>'
        f'<pre>{content_escaped}</pre>'
        f'</div>'
    )


def render_steps(steps: list[dict[str, Any]], attachment_index: dict[str, Path], depth: int = 0) -> str:
    """递归渲染步骤树。"""
    if not steps:
        return ""
    out: list[str] = ['<div class="steps">']
    for step in steps:
        name = html.escape(step.get("name", ""))
        status = step.get("status", "")
        status_class = status if status in ("passed", "failed", "broken") else ""
        status_html = f' <span class="step-status">[{status_label(status)}]</span>' if status_class else ""

        # step 自身的 attachments（allure 用 stop 标记，不挂在 statusDetails 里）
        att_html = "".join(
            render_attachment(att, attachment_index)
            for att in step.get("attachments", [])
        )

        sub_steps_html = render_steps(step.get("steps", []) or [], attachment_index, depth + 1)

        out.append(
            f'<div class="step {status_class}">'
            f'<div class="step-name">├─ {name}{status_html}</div>'
            f'{att_html}'
            f'{sub_steps_html}'
            f'</div>'
        )
    out.append('</div>')
    return "".join(out)


def render_case(case: dict[str, Any], attachment_index: dict[str, Path]) -> str:
    """渲染单个 case 为 HTML 卡片。"""
    name = html.escape(case.get("name", "?"))
    status = case.get("status", "unknown")
    status_cls = status if status in ("passed", "failed", "broken", "skipped") else "unknown"
    description = html.escape(case.get("description", "") or "")
    full_name = html.escape(case.get("fullName", "") or "")

    stop_ms = case.get("stop", 0) or 0
    start_ms = case.get("start", 0) or 0
    duration = format_duration(stop_ms - start_ms) if stop_ms and start_ms else "-"

    # 失败信息（statusDetails.message）
    fail_msg_html = ""
    sd = case.get("statusDetails") or {}
    if sd.get("message"):
        msg = html.escape(sd["message"])
        fail_msg_html = f'<div class="fail-msg">✗ {msg}</div>'

    steps_html = render_steps(case.get("steps", []) or [], attachment_index)

    return f"""
<div class="case">
  <div class="case-header">
    <div>
      <h3 class="case-title">{name}</h3>
      {f'<div class="case-desc">{description}</div>' if description else ''}
      <div class="case-desc">耗时 {duration} | {full_name}</div>
    </div>
    <span class="badge {status_cls}">{status_label(status)}</span>
  </div>
  {fail_msg_html}
  <details class="case-steps" open>
    <summary>执行步骤 ({len(case.get("steps", []) or [])})</summary>
    {steps_html}
  </details>
</div>
"""


def render_summary(metrics: dict[str, Any], plan_id: str, timestamp: str) -> str:
    by_status = metrics["by_status"]
    total = metrics["total"]
    duration = format_duration(metrics["total_duration_ms"])

    def metric(num: int, label: str, cls: str = "") -> str:
        return f'<div class="metric {cls}"><div class="num">{num}</div><div class="label">{label}</div></div>'

    metrics_html = [
        metric(total, "总用例", ""),
        metric(by_status.get("passed", 0), "通过", "passed"),
        metric(by_status.get("failed", 0), "失败", "failed"),
        metric(by_status.get("broken", 0), "异常", "broken"),
        metric(by_status.get("skipped", 0), "跳过", "skipped"),
    ]
    return f"""
<div class="summary">
  {''.join(metrics_html)}
</div>
<div class="meta">
  <strong>plan-id:</strong> {html.escape(plan_id)} &nbsp;|&nbsp;
  <strong>时间戳:</strong> {html.escape(timestamp)} &nbsp;|&nbsp;
  <strong>总耗时:</strong> {duration} &nbsp;|&nbsp;
  <strong>生成时间:</strong> {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
</div>
"""


def render_html(
    cases: list[dict[str, Any]],
    plan_id: str,
    timestamp: str,
    attachment_index: dict[str, Path],
) -> str:
    metrics = summarize(cases)
    summary_html = render_summary(metrics, plan_id, timestamp)
    cases_html = "".join(render_case(c, attachment_index) for c in cases)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>shenle-ai-test-runner 报告 — {html.escape(plan_id)} — {html.escape(timestamp)}</title>
<style>{_CSS}</style>
</head>
<body>
<div class="container">
  <h1>shenle-ai-test-runner 测试报告</h1>
  {summary_html}
  <h2>用例详情 ({metrics['total']})</h2>
  {cases_html if cases_html else '<p style="color:var(--muted);">无测试结果</p>'}
  <div class="footer">
    由 shenle-report-generate-html 生成 · 基于 allure-results/*.json
  </div>
</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 自动选最新 timestamp
# ---------------------------------------------------------------------------


def find_latest_timestamp(plan_dir: Path) -> str | None:
    """在 <plan_dir> 下找最大的时间戳子目录名（YYYYMMDD-HHMMSS 格式）。"""
    candidates = []
    for d in plan_dir.iterdir():
        if not d.is_dir():
            continue
        # YYYYMMDD-HHMMSS 14 位
        if len(d.name) == 15 and d.name[8] == "-" and d.name[:8].isdigit() and d.name[9:].isdigit():
            candidates.append(d.name)
    if not candidates:
        return None
    return max(candidates)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="shenle-report-generate-html",
        description="把 allure-results/ 渲染成单文件静态 HTML 报告。",
    )
    parser.add_argument("--project-dir", required=True, help="项目工作目录（含 AI-自动化测试报告/）")
    parser.add_argument("--plan-id", required=True, help="测试计划 ID")
    parser.add_argument("--timestamp", help="时间戳 YYYYMMDD-HHMMSS（不填则取最新）")
    parser.add_argument("--latest", action="store_true", help="等价于不填 timestamp 时取最新")
    parser.add_argument("--output", help="自定义输出 HTML 路径（默认 <run-dir>/report.html）")
    args = parser.parse_args(argv)

    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.is_dir():
        print(f"[FAIL] 项目目录不存在：{project_dir}", file=sys.stderr)
        return 1

    plan_dir = project_dir / "AI-自动化测试报告" / args.plan_id
    if not plan_dir.is_dir():
        print(f"[FAIL] plan 目录不存在：{plan_dir}", file=sys.stderr)
        return 1

    # 决定 timestamp
    timestamp = args.timestamp
    if not timestamp or args.latest:
        timestamp = find_latest_timestamp(plan_dir)
        if not timestamp:
            print(f"[FAIL] {plan_dir} 下没有 YYYYMMDD-HHMMSS 格式的子目录", file=sys.stderr)
            return 1
        print(f"[INFO] 自动选最新时间戳：{timestamp}")

    run_dir = plan_dir / timestamp
    results_dir = run_dir / "allure-results"
    if not results_dir.is_dir():
        print(f"[FAIL] allure-results 不存在：{results_dir}", file=sys.stderr)
        return 1

    # 读取
    cases = parse_allure_results(results_dir)
    attachment_index = index_attachments(results_dir)
    print(f"[INFO] 读 {len(cases)} 个 case, {len(attachment_index)} 个附件")

    # 渲染
    html_content = render_html(cases, args.plan_id, timestamp, attachment_index)

    # 输出
    if args.output:
        out_path = Path(args.output).expanduser().resolve()
    else:
        out_path = run_dir / "report.html"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_content, encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024
    print(f"[OK] HTML 报告已生成：{out_path}")
    print(f"     大小 {size_kb:.1f} KB · {len(cases)} case · {metrics_total(cases)} 通过")
    return 0


def metrics_total(cases: list[dict[str, Any]]) -> int:
    return sum(1 for c in cases if c.get("status") == "passed")


if __name__ == "__main__":
    sys.exit(main())
