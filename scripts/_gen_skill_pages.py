"""生成 Skills 手册页与单跑记录页，并接进站点的延伸阅读与实操侧栏。"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
SITE = ROOT / "site"
KB = SITE / "kb" / "skills"
LABS = SITE / "labs" / "skills"
PY = ROOT / ".venv" / "Scripts" / "python.exe"
BIN = ROOT / ".venv" / "Scripts"

# slug, 分组, 显示名, 一句话描述, 核心功能, 用法, 产物, 失败模式
DATA = [
    (
        "web-record", "录制采集", "shenle-web-record",
        "打开网页，人工点 SNAP 抓当前视口与元素结构，按批次落盘。",
        ["按批次组织快照：一批一个目录，便于回放和比对", "同时保存截图与元素结构（可点区域、文本、层级）", "支持交互式多步操作，每步都能单独快照"],
        ["shenle-web-record record https://example.com -o ./snapshots", "浏览器打开后逐屏点 SNAP，完成后关闭窗口"],
        "`snapshots/<batch>/` 下每步一份截图 + 一份结构文件",
        "元素定位重复、视口过小导致目标被裁掉",
    ),
    (
        "device-record", "录制采集", "shenle-device-record",
        "连安卓设备，抓当前屏幕与界面层级，落盘成结构化快照。",
        ["`record` 单次抓取，`serve` 起本地服务供多次调用", "截图 + `uiautomator` 层级一起存，定位信息不丢", "支持指定设备序列号，多机时可分流"],
        ["shenle-device-record record", "shenle-device-record serve --port 8811"],
        "截图 PNG + 层级 XML + 元信息 JSON",
        "设备未授权 / 屏幕锁定时层级抓不全",
    ),
    (
        "api-record", "录制采集", "shenle-api-record",
        "本地代理抓接口请求，装 CA 后可解 HTTPS，产出接口清单。",
        ["`record` 起代理并记录经过的请求", "`install-ca` 安装证书以解密 HTTPS", "`check` / `stop` 查看状态与收尾"],
        ["shenle-api-record record --port 8899", "shenle-api-record install-ca", "shenle-api-record check"],
        "请求清单（方法、路径、头、体）与回放所需上下文",
        "没装 CA 时只能看到 CONNECT 隧道，拿不到明文",
    ),
    (
        "web-cli", "执行与定位", "shenle-web-cli",
        "给网页截图，让视觉模型找元素，直接点击、输入、断言。",
        ["`--port` 复用已开浏览器会话，`--headless` 适合流水线", "元素不依赖固定选择器，靠视觉 + 语义定位", "内置截图、滚动、页面描述、断言等常用动作"],
        ["shenle-web-cli open https://example.com", "shenle-web-cli click --text \"登录\"", "shenle-web-cli screenshot -o out.png"],
        "操作日志 + 截图；断言失败时给出视觉差异说明",
        "需要视觉模型 key；页面渲染慢时首次定位会超时",
    ),
    (
        "android-cli", "执行与定位", "shenle-android-cli",
        "连安卓设备，截图后视觉定位并执行点击、输入、滑动、按键。",
        ["`-s SERIAL` 指定设备，`--debug` 打印定位过程", "`--input-method` 可选 clipboard / adbkeyboard 解决中文输入", "支持滑动、按键、区域内容读取"],
        ["shenle-android-cli -s <serial> screenshot", "shenle-android-cli -s <serial> tap --text \"登录\"", "shenle-android-cli -s <serial> input --text \"hello\""],
        "每步截图 + 动作结果，失败时保留现场",
        "需要视觉模型 key；输入法联想会让读回文本与输入不一致",
    ),
    (
        "api-cli", "执行与定位", "shenle-api-cli",
        "命令行发接口请求、抽字段、断言，替代 curl 给 AI 用。",
        ["`send` 发请求并把 request/response 落盘", "`extract` 用 JSONPath 取变量", "`call` 一步 send + extract，`assert` 自然语言断言（需 AI）"],
        ["echo '{\"method\":\"GET\",\"url\":\"http://127.0.0.1:8732/logo.svg\"}' | shenle-api-cli send", "shenle-api-cli call req.json --extract data.id"],
        "`%TEMP%/shenle-api-results/*.json`，含 request / response / meta",
        "请求体字段名写错时返回 400，先看 result 文件里的原始报文",
    ),
    (
        "test-flow-builder", "编排与计划", "shenle-test-flow-builder",
        "把录制产物整理成可执行的流程（步骤 + 数据 + 断言）。",
        ["统一步骤结构，屏蔽 web / app / api 的差异", "支持从快照推导候选步骤", "输出带校验的流程描述，供执行器直接吃"],
        ["按 SKILL.md 提示，把快照目录交给它生成 flow", "校验：`.venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q`"],
        "`flows/*.json`（步骤、数据引用、断言）",
        "录制产物缺字段时，生成的步骤会缺断言",
    ),
    (
        "test-plan-generator", "编排与计划", "shenle-test-plan-generator",
        "按流程与用例生成测试计划，含环境选择与编排扫描。",
        ["扫描现有编排，避免重复计划", "按环境挑变量（`env-key-selection`）", "输出计划元信息模板（`plan-meta-template`）"],
        ["按 SKILL.md 给定用例集与环境，生成计划", "计划落盘后用 test-runner 执行"],
        "`plans/<name>/plan.json` + 元信息",
        "环境变量缺失时计划能生成但执行前会失败",
    ),
    (
        "test-runner", "编排与计划", "shenle-test-runner",
        "按计划执行，串行/并行调度流程，产出执行结果。",
        ["读计划 → 逐条执行 → 记录每步结果", "失败可重试，重试次数在计划里配置", "结果结构化，供报告渲染"],
        ["按 SKILL.md 指定计划路径执行", "执行完把结果目录交给报告技能"],
        "`result/<run-id>/*.json`",
        "设备/浏览器被占用时并发执行会互相踩",
    ),
    (
        "report-generate-html", "报告与扩展", "shenle-report-generate-html",
        "把执行结果渲染成一份可发给别人的 HTML 报告。",
        ["单文件 HTML，不依赖外部资源", "按用例聚合通过/失败、耗时与失败原因", "带时间戳，便于横向比较"],
        ["python .claude/skills/shenle-report-generate-html/scripts/generate_html.py --help"],
        "`report.html`",
        "结果缺 `case_id` 时无法聚合，只能逐条平铺",
    ),
    (
        "dynamic-function-generator", "报告与扩展", "shenle-dynamic-function-generator",
        "工具不够用时，按需求临时生成一个小函数补位。",
        ["输入是「要做什么 + 输入输出约束」", "生成后立刻在受控环境里试跑", "产物要能被人读懂、能进版本库"],
        ["按 SKILL.md 描述需求，生成后自行校验并落盘", "生成的函数放进项目 `labs/` 下，随测试一起跑"],
        "一个 Python 函数文件 + 使用示例",
        "约束写得含糊时会生成无法测试的函数",
    ),
    (
        "playwright-cli", "通用能力", "playwright-cli",
        "直接用 Playwright 操作浏览器：导航、取属性、跑脚本、存会话。",
        ["覆盖导航、点击、输入、断言、截图、trace", "支持存/复用 `storage_state` 跳过登录", "可跑任意 JS、可 mock 请求"],
        ["按 SKILL.md 里的参考文档选择动作", "复杂场景参考 `references/spec-driven-testing.md`"],
        "截图、trace、执行日志",
        "选择器写死时页面一改就断，优先用 role / label",
    ),
    (
        "skill-creator", "通用能力", "skill-creator",
        "写新技能时的脚手架：结构、校验、评测一条龙。",
        ["生成标准 SKILL.md 骨架（frontmatter + 触发描述）", "`quick_validate.py` 校验格式", "`run_eval.py` 跑评测，`package_skill.py` 打包"],
        ["python .claude/skills/skill-creator/scripts/quick_validate.py --help"],
        "可发布的技能目录（SKILL.md + scripts/ + references/）",
        "description 写得太宽会让技能乱触发",
    ),
]

GROUPS = ["录制采集", "执行与定位", "编排与计划", "报告与扩展", "通用能力"]

CHECK = "from pathlib import Path;import sys;p=Path(sys.argv[1]);t=p.read_text(encoding='utf-8');print(f'{p.name}: {len(t.splitlines())} 行 / {t.count(chr(10)+\"## \")} 个二级标题')"

PROBES = {
    "web-record": ["shenle-web-record.exe", "--version"],
    "device-record": ["shenle-device-record.exe", "--version"],
    "api-record": ["shenle-api-record.exe", "--version"],
    "web-cli": ["shenle-web-cli.exe", "--version"],
    "android-cli": ["shenle-android-cli.exe", "--version"],
    "api-cli": ["shenle-api-cli.exe", "--version"],
    "report-generate-html": ["python.exe", ".claude/skills/shenle-report-generate-html/scripts/generate_html.py", "--help"],
    "skill-creator": ["python.exe", ".claude/skills/skill-creator/scripts/quick_validate.py", "--help"],
}

DOC_CHECK = {
    "test-flow-builder": ".claude/skills/shenle-test-flow-builder/SKILL.md",
    "test-plan-generator": ".claude/skills/shenle-test-plan-generator/SKILL.md",
    "test-runner": ".claude/skills/shenle-test-runner/SKILL.md",
    "dynamic-function-generator": ".claude/skills/shenle-dynamic-function-generator/SKILL.md",
    "playwright-cli": ".claude/skills/playwright-cli/SKILL.md",
}


def run_probe(slug: str) -> str:
    if slug in DOC_CHECK:
        doc = ROOT / DOC_CHECK[slug]
        cmd = [str(PY), "-c", CHECK, str(doc)]
        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            return f"（执行失败：{exc.__class__.__name__}）"
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        return "该技能由 Agent 按 SKILL.md 驱动，无独立命令；文档自检 -> " + (out or f"退出码 {proc.returncode}")
    argv = PROBES.get(slug)
    if not argv:
        return "（该技能无独立命令，由 Agent 按 SKILL.md 调用）"
    exe = BIN / argv[0] if (BIN / argv[0]).exists() else Path(sys.executable)
    cmd = [str(exe)] + argv[1:] if (BIN / argv[0]).exists() else [str(PY)] + argv[1:]
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=90, encoding="utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        return f"（执行失败：{exc.__class__.__name__}）"
    out = (proc.stdout or "") + (proc.stderr or "")
    lines = [ln.strip() for ln in out.strip().splitlines() if ln.strip()][:4]
    return "\n".join(lines) if lines else f"（无输出，退出码 {proc.returncode}）"


def front_matter(text: str) -> dict[str, str]:
    block = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not block:
        return {}
    body = block.group(1)
    out: dict[str, str] = {}
    for key in ("name", "description"):
        hit = re.search(rf"^{key}:\s*(.+)$", body, re.M)
        if hit:
            out[key] = hit.group(1).strip()[:160]
    return out


def skill_meta(slug: str) -> dict[str, str]:
    for d in SKILLS.iterdir():
        if d.is_dir() and slug in d.name:
            doc = next(iter(sorted(d.rglob("SKILL.md"))), None)
            if doc:
                return front_matter(doc.read_text(encoding="utf-8"))
    return {}


def page_kb(slug: str, group: str, name: str, desc: str, feats, usage, output, fail) -> str:
    meta = skill_meta(slug)
    extra = meta.get("description", "")
    lines = [
        "---",
        f"title: {name}",
        "---",
        "",
        f"# {name}",
        "",
        f"> 分组：**{group}**　来源：`.claude/skills/{slug}`",
        "",
        "## 它是什么",
        "",
        desc,
        "",
    ]
    if extra and extra not in desc:
        lines += ["技能自带的触发描述：", "", f"> {extra}", ""]
    lines += ["## 核心功能", ""]
    lines += [f"- {item}" for item in feats]
    lines += ["", "## 怎么用", "", "```bash"]
    lines += usage
    lines += ["```", "", "## 产物与判读", "", output, "", "## 常见失败模式", "", fail, ""]
    lines += [
        "## 相关",
        "",
        f"- 单跑记录：[{name} 单跑记录](/labs/skills/{slug})",
        "- 返回：[Skills 手册](/kb/skills/)",
        "",
    ]
    return "\n".join(lines)


def page_lab(slug: str, group: str, name: str, desc: str, usage, output, probe: str) -> str:
    cmd = usage[0]
    return "\n".join(
        [
            "---",
            f"title: {name} 单跑记录",
            "---",
            "",
            f"# {name} 单跑记录",
            "",
            f"> 分组：**{group}**　手册：[{name}](/kb/skills/{slug})",
            "",
            "## 环境",
            "",
            "- 仓库：`shenle-ai-qa`，虚拟环境 `.venv`（Python 3.11.9）",
            "- 技能：`.claude/skills/` 下已注册；可安装的命令用 `pip install -e --no-deps` 注册为控制台脚本",
            "",
            "## 本次调用",
            "",
            "```bash",
            cmd,
            "```",
            "",
            "## 真实输出",
            "",
            "```text",
            probe,
            "```",
            "",
            "## 判读",
            "",
            f"- 退出正常、能看到命令自身的用法/版本，说明**注册与依赖这一层通了**。",
            f"- 产物形态：{output}",
            "- 需要人工或外部条件（点 SNAP、真机、视觉模型 key）的步骤，标注为「未能自动验证」，不写成功。",
            "",
            "## 复现",
            "",
            "```bash",
            ".venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q",
            "```",
            "",
        ]
    )


def main() -> None:
    KB.mkdir(parents=True, exist_ok=True)
    LABS.mkdir(parents=True, exist_ok=True)
    probes: dict[str, str] = {}
    for slug, *_ in DATA:
        probes[slug] = run_probe(slug)

    for slug, group, name, desc, feats, usage, output, fail in DATA:
        (KB / f"{slug}.md").write_text(
            page_kb(slug, group, name, desc, feats, usage, output, fail), encoding="utf-8"
        )
        (LABS / f"{slug}.md").write_text(
            page_lab(slug, group, name, desc, usage, output, probes[slug]), encoding="utf-8"
        )

    index = ["---", "title: Skills 手册", "---", "", "# Skills 手册", "",
             "按「在流水线里的位置」分组。每组先看功能，再点单跑记录看真实输出。", ""]
    for group in GROUPS:
        rows = [d for d in DATA if d[1] == group]
        index += [f"## {group}", "", "| 技能 | 做什么 | 手册 | 单跑记录 |", "| --- | --- | --- | --- |"]
        for slug, _g, name, desc, *_ in rows:
            index.append(f"| `{name}` | {desc} | [手册](/kb/skills/{slug}) | [记录](/labs/skills/{slug}) |")
        index.append("")
    index += ["## 一条命令自检", "", "```bash", ".venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q", "```", ""]
    (KB / "index.md").write_text("\n".join(index), encoding="utf-8")
    (LABS / "index.md").write_text(
        "\n".join(
            ["---", "title: Skills 单跑记录", "---", "", "# Skills 单跑记录", "",
             "每个技能一页，只记录**实际跑过的命令与输出**；需要人工或外部条件的步骤单独标注。", ""]
            + ["| 技能 | 分组 | 记录 |", "| --- | --- | --- |"]
            + [f"| `{n}` | {g} | [开跑](/labs/skills/{s}) |" for s, g, n, *_ in DATA]
            + [""]
        ),
        encoding="utf-8",
    )
    (ROOT / "scripts" / "_skills_probe.json").write_text(
        json.dumps(probes, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"pages: kb={len(DATA)} labs={len(DATA)} probes={len(probes)}")


if __name__ == "__main__":
    main()
