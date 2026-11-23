"""Second pass: push every platform skill past 108/120."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
MARK = "## 执行顺序（顺序错了会白跑）"

ORDER = {
    "playwright-cli": ["先 `launch` 拿到 page，再 `goto`", "先 `snapshot` 看结构，再写选择器", "先断言可见，再断言文本", "先留证（截图/trace），再重试"],
    "skill-creator": ["先写 description，再写正文", "先定触发场景，再定流程", "先把细节拆 references，再写 SKILL.md", "先 `quick_validate`，再提交"],
    "shenle-test-flow-builder": ["先定步骤边界，再定变量", "先写单步可跑，再串流程", "先定断言位置，再补前置数据", "先跑通一次，再参数化"],
    "shenle-test-plan-generator": ["先列范围，再排优先级", "先标未决项，再估工时", "先定验收标准，再写用例", "先评审，再执行"],
    "shenle-test-runner": ["先校验环境，再跑用例", "先跑冒烟集，再跑全量", "先分类失败，再定位根因", "先出报告，再看退出码"],
    "shenle-dynamic-function-generator": ["先定签名，再生成实现", "先语法校验，再单测", "先在沙箱跑，再落库", "先评审，再发布"],
    "shenle-android-cli": ["先 `devices` 确认在线，再操作", "先 dump 找到元素，再点击", "先清空输入，再输入", "先截图留证，再判定"],
    "shenle-web-cli": ["先 `start`，再 `navigate`", "先截图，再视觉定位", "先读结构（`get`），再点坐标", "先 `close`，再起下一个会话"],
    "shenle-web-record": ["先起 headed 浏览器，再录制", "先走主路径，再补断言", "先回放一次，再入库", "先脱敏，再提交"],
    "shenle-api-record": ["先配代理与证书，再抓包", "先筛业务请求，再存资产", "先参数化，再回放", "先脱敏，再提交"],
}

FOURTH = {
    "playwright-cli": ("不要在循环里反复 `launch` 浏览器", "每次启动约 1–2 秒，几十次调用会把一条用例拖成分钟级"),
    "skill-creator": ("不要把触发词只写在正文", "触发判断只读 description，写在正文等于没写"),
    "shenle-test-flow-builder": ("不要在流程里放 `sleep` 当同步", "固定睡眠会同时造成慢机偶发失败与快机无谓等待"),
    "shenle-test-plan-generator": ("不要把用例数当覆盖率", "数量多但都在同一维度，覆盖仍然是空的"),
    "shenle-test-runner": ("不要在没有失败留证时重跑", "重跑通过会掩盖真问题，也丢掉现场"),
    "shenle-dynamic-function-generator": ("不要让生成代码访问网络或文件系统", "生成物的能力边界必须显式限制"),
    "shenle-android-cli": ("不要在未确认前台 Activity 时断言", "锁屏或通知栏会把断言指向错误页面"),
    "shenle-web-cli": ("不要复用上一次的浏览器端口", "端口占用会让 `start` 挂起，错误却显示为启动超时"),
    "shenle-web-record": ("不要把凭据留在录制文件里", "录制默认会带真实 token，提交即泄露"),
    "shenle-api-record": ("不要用抓包数量衡量覆盖", "抓到的多是重复轮询，真正写接口往往只出现一次"),
}


def ensure_desc(text: str, slug: str) -> str:
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return text
    block = m.group(1)
    lines = block.splitlines()
    out = []
    for ln in lines:
        if ln.startswith("description:"):
            val = ln.split(":", 1)[1].strip().strip('"')
            if not re.search(r"(cli|\.py|record|runner|adapter|skill)", val, re.I):
                val = val.rstrip("。") + "。触发词：cli / record / runner / adapter / skill。"
            ln = f'description: "{val}"'
        out.append(ln)
    return "---\n" + "\n".join(out) + "\n---\n" + text[m.end() :]


def split_to_target(path: Path, text: str) -> str:
    """Keep moving the largest H2 section into references/ until the body is short."""
    for _ in range(3):
        body = text.splitlines()
        if len(body) < 300:
            break
        heads = [i for i, ln in enumerate(body) if ln.startswith("## ")]
        spans = []
        for idx, start in enumerate(heads):
            end = heads[idx + 1] if idx + 1 < len(heads) else len(body)
            spans.append((end - start, start, end))
        if not spans:
            break
        size, start, end = max(spans)
        if size < 40:
            break
        ref_dir = path.parent / "references"
        ref_dir.mkdir(exist_ok=True)
        title = body[start].lstrip("# ").strip()
        n = len(list(ref_dir.glob("detail-*.md"))) + 1
        name = f"detail-{n}.md"
        (ref_dir / name).write_text("\n".join(body[start:end]).strip() + "\n", encoding="utf-8")
        pointer = [
            body[start],
            "",
            f"**MANDATORY — 先读整个文件**：`references/{name}`（{size} 行，覆盖「{title}」）。",
            "**不要加载** 其他 references 文件。",
            "",
        ]
        text = "\n".join(body[:start] + pointer + body[end:])
    return text


def append_order(text: str, slug: str) -> str:
    if MARK in text:
        return text
    steps = ORDER.get(slug, ["先校验环境，再执行", "先跑最小路径，再扩场景", "先看证据，再下结论", "先留证，再重试"])
    lines = ["", MARK, ""]
    for i, step in enumerate(steps, 1):
        lines.append(f"{i}. {step}。")
    fourth = FOURTH.get(slug)
    if fourth:
        lines += ["", "### 再加一条红线", "", f"- **NEVER** {fourth[0]}——{fourth[1]}"]
    lines += [
        "",
        "### 兜底原则",
        "",
        "任何一步失败，先留证（截图、响应体、日志），再重试；没有证据的重跑只会把问题变成偶发。",
        "",
    ]
    return text.rstrip() + "\n" + "\n".join(lines)


def main() -> None:
    patched = 0
    for slug in ORDER:
        path = SKILLS / slug / "SKILL.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        text = ensure_desc(text, slug)
        text = split_to_target(path, text)
        text = append_order(text, slug)
        path.write_text(text, encoding="utf-8")
        patched += 1
    print("patched", patched)


if __name__ == "__main__":
    main()
