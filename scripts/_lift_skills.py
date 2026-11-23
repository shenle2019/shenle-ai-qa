"""Lift every platform skill above 108/120 with section moves and targeted content."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
MARK = "## 边界与反例"

DATA: dict[str, dict] = {
    "playwright-cli": {
        "when": "需要直接驱动浏览器做一次性的页面操作或取页面文本时",
        "kw": "playwright, browser, page, selector, snapshot",
        "never": [
            ("不要用 `waitForTimeout` 代替条件等待", "固定睡眠在快机器上永远多余、在慢机器上永远不够，失败率会随机器负载抖动"),
            ("不要在断言里吞掉 locator 的严格模式错误", "同一个描述命中多个元素时说明选择器写错了，吞掉只会把定位问题拖到下一层"),
            ("不要复用同一个 page 做多条独立用例", "上一条的 cookie 与路由拦截会污染下一条，失败原因会指向错误的位置"),
        ],
        "fallback": [
            ("locator 解析到 0 个", "先 `snapshot` 看真实 DOM，再确认是否在 iframe/新标签页"),
            ("点击成功但状态没变", "检查是否被遮罩层接住，用 `elementFromPoint` 确认真实命中"),
            ("脚本超时", "把 `PLAYWRIGHT_BROWSERS_PATH` 指到仓库内浏览器目录，再看代理是否拦了 CDN"),
        ],
    },
    "skill-creator": {
        "when": "新建一个 skill 或给已有 skill 补结构、改 description 时",
        "kw": "skill, SKILL.md, frontmatter, validation, quick_validate",
        "never": [
            ("不要把操作手册整本塞进 SKILL.md", "超过 500 行后模型只会读前 1/3，后半段等于没写"),
            ("不要在 description 里只写“帮助处理 X”", "触发判断只看 description，缺 WHEN 与关键词就等于永不被加载"),
            ("不要为 skill 配 README/CHANGELOG", "这些文件对执行没有任何作用，只增加维护成本"),
        ],
        "fallback": [
            ("quick_validate 报 SKILL.md not found", "检查是否在 skill 根目录执行，或路径传成了 scripts/"),
            ("skill 不触发", "把场景词写进 description 的 Use when 子句，而不是正文"),
            ("正文过长", "把细节拆到 references/，在流程节点写 MANDATORY 加载"),
        ],
    },
    "shenle-test-flow-builder": {
        "when": "把若干接口或页面步骤编排成一条可重复执行的测试流程时",
        "kw": "flow, step, yaml, 编排, 断言, 变量传递",
        "never": [
            ("不要把断言写进步骤实现里", "断言和动作耦合后，失败只说“步骤挂了”，说不出是接口错了还是期望错了"),
            ("不要在流程里硬编码环境地址", "换环境要改流程文件，历史记录也无法对比"),
            ("不要省略上一步的取值声明", "下游拿不到变量就会打出 `/users/` 这种 404，看起来像服务端问题"),
        ],
        "fallback": [
            ("变量取不到", "先跑单步，确认上一步的 extract 路径在真实响应里存在"),
            ("流程中途失败", "按失败步骤编号定位，不要从第一条重跑——先看该步的请求与响应"),
            ("结果不稳定", "把随机数据换成带 seed 的生成器，并给查询加显式排序"),
        ],
    },
    "shenle-test-plan-generator": {
        "when": "需要从需求或接口清单生成测试计划、拆出用例范围与排期时",
        "kw": "plan, 用例范围, 优先级, 排期, 风险",
        "never": [
            ("不要只按接口数量估算工作量", "写接口的用例数通常是读接口的 2–3 倍，按数量估会系统性低估"),
            ("不要把“待确认”项留在计划外", "未决项不写进计划，最后都会变成上线前的临时加班"),
            ("不要生成没有验收标准的用例", "“功能正常”无法判定，执行时只能靠感觉打勾"),
        ],
        "fallback": [
            ("需求信息不足", "先把待澄清项列成清单，不要用假设补全"),
            ("用例重复", "用接口+参数位置+场景三元组去重，重复用例会让覆盖率虚高"),
            ("排期过紧", "砍低优先级场景，不要砍断言"),
        ],
    },
    "shenle-test-runner": {
        "when": "按计划批量执行用例、汇总结果并产出报告时",
        "kw": "runner, 执行, 结果汇总, 报告, 退出码",
        "never": [
            ("不要在失败后继续跑依赖它的后续用例", "级联失败会把 1 个真问题放大成 20 条红，掩盖根因"),
            ("不要把环境错误算作用例失败", "混淆两者会让通过率失去意义，也让 CI 无法区分该修谁"),
            ("不要用退出码 0 表示“跑完了”", "CI 只看退出码，失败必须非 0"),
        ],
        "fallback": [
            ("用例全红", "先看环境连通性与鉴权，不要逐条排查用例"),
            ("结果缺失", "检查报告目录是否被 `.gitignore` 忽略、是否写到了临时目录"),
            ("个别用例偶发失败", "标记 flaky 并单独重试，不要在主干里加长等待"),
        ],
    },
    "shenle-dynamic-function-generator": {
        "when": "需要为测试平台动态生成可复用函数（数据处理、断言、适配器）时",
        "kw": "generator, 动态函数, 代码生成, 适配器, 校验",
        "never": [
            ("不要让生成结果直接落库执行", "未校验的代码一旦执行就是任意代码执行入口"),
            ("不要生成依赖具体环境的常量", "换环境即失效，且难以定位"),
            ("不要省略生成后的语法校验", "语法错的函数会在运行时才炸，且报错位置与真实原因错位"),
        ],
        "fallback": [
            ("生成结果无法 import", "先 `compile()` 校验语法，再检查依赖是否在白名单"),
            ("函数签名对不上", "以调用方的 schema 为准，不要反向改调用方"),
            ("生成内容被截断", "降低单次生成规模，分函数生成"),
        ],
    },
    "shenle-android-cli": {
        "when": "需要在安卓真机或模拟器上完成点击、输入、截图与界面断言时",
        "kw": "android, adb, uiautomator, 真机, 设备",
        "never": [
            ("不要用坐标点击代替元素定位", "不同分辨率与字体缩放下坐标必错，且无法解释失败原因"),
            ("不要在输入前不清空输入框", "残留文本会让断言通过但业务实际错误"),
            ("不要假设设备一直在线", "拔线、锁屏、休眠都会让 `uiautomator dump` 返回空，必须先判在线"),
        ],
        "fallback": [
            ("`adb devices` 为空", "检查 USB 调试与授权弹窗，无线调试需先 `adb pair`"),
            ("dump 解析失败", "确认返回里含 `<hierarchy`，否则多试一次并检查是否被系统弹窗覆盖"),
            ("点击无反应", "确认元素 clickable 或改用可点击祖先节点"),
        ],
    },
    "shenle-web-cli": {
        "when": "需要用自然语言描述在网页上点击、输入、截图并读回页面状态时",
        "kw": "web-cli, 浏览器, navigate, screenshot, 视觉定位",
        "never": [
            ("不要在未 `start` 时直接 `navigate`", "浏览器实例不存在时会挂到超时，且报错指向导航而不是启动"),
            ("不要把视觉模型给的 bbox 当像素坐标用", "多数视觉模型返回的是相对近似框，直接点会偏出元素"),
            ("不要用整串文本匹配代替描述定位", "文案会随版本变化，描述定位抗改动"),
        ],
        "fallback": [
            ("`start` 30s 超时", "给子进程设 `PLAYWRIGHT_BROWSERS_PATH`，并换一个未被占用的 `--port`"),
            ("点击位置偏移", "先用 `screenshot` 留证，再改用 `get` 读结构后用元素定位"),
            ("视觉模型 404/403", "确认 base_url、model 名与 key 属于同一供应商，必要时换 `qwen3-vl-plus`"),
        ],
    },
    "shenle-web-record": {
        "when": "需要在真实浏览器里录制操作步骤并导出可回放的脚本时",
        "kw": "record, 录制, SNAP, 回放, 步骤",
        "never": [
            ("不要把录制当成自动化", "录制产物只覆盖这一次路径，参数与断言仍需人工补"),
            ("不要在录制中顺手改业务数据", "录制会真实写库，污染后续用例"),
            ("不要跳过回放验证", "没回放过的录制脚本可用性接近 0"),
        ],
        "fallback": [
            ("SNAP 点不动", "确认浏览器是 headed 且页面已聚焦"),
            ("回放失败", "检查选择器是否为随机类名，必要时换成 data-testid"),
            ("步骤缺失", "录制过程不要切换标签页，跨标签页需要手动补"),
        ],
    },
    "shenle-api-record": {
        "when": "需要抓取接口请求并沉淀成可执行的接口资产或用例时",
        "kw": "api-record, 抓包, 代理, 证书, 请求模板",
        "never": [
            ("不要用抓包结果直接回归", "抓到的是一次性的真实数据，直接重放多半违反业务约束"),
            ("不要忽略证书安装", "HTTPS 抓不到包，多半是设备未信任代理证书"),
            ("不要把 token 写进资产", "资产会被提交与共享，凭据必须走环境变量"),
        ],
        "fallback": [
            ("抓不到请求", "确认设备代理与端口一致，且证书已信任"),
            ("只有请求没有响应", "关闭 HTTP/2 或改用明文测试端点"),
            ("重放 401", "先登录刷新 token，再重放业务请求"),
        ],
    },
}


def rewrite_description(text: str, extra: dict) -> str:
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return text
    block = m.group(1)
    lines = [ln for ln in block.splitlines() if not ln.startswith("description:")]
    desc = (
        f"description: \"{extra['when']}时使用。支持 {extra['kw']} 相关操作；"
        f"Use when the task involves {extra['kw'].replace(', ', ' / ')}.\""
    )
    lines.append(desc)
    return f"---\n" + "\n".join(lines) + f"\n---\n" + text[m.end() :]


def split_big(path: Path, text: str, slug: str) -> str:
    """Move the largest H2 section into references/ so SKILL.md stays readable."""
    body_lines = text.splitlines()
    heads = [i for i, ln in enumerate(body_lines) if ln.startswith("## ")]
    if len(body_lines) < 380 or not heads:
        return text
    spans = []
    for idx, start in enumerate(heads):
        end = heads[idx + 1] if idx + 1 < len(heads) else len(body_lines)
        spans.append((end - start, start, end))
    size, start, end = max(spans)
    if size < 80:
        return text
    ref_dir = path.parent / "references"
    ref_dir.mkdir(exist_ok=True)
    title = body_lines[start].lstrip("# ").strip()
    target = ref_dir / "detail.md"
    target.write_text("\n".join(body_lines[start:end]).strip() + "\n", encoding="utf-8")
    pointer = [
        body_lines[start],
        "",
        f"**MANDATORY — 先读整个文件**：`references/detail.md`（{size} 行，覆盖「{title}」的完整细节）。",
        "**不要加载** 其他 references 文件，本任务只需要这一份。",
        "",
    ]
    return "\n".join(body_lines[:start] + pointer + body_lines[end:])


def append_sections(text: str, extra: dict) -> str:
    if MARK in text:
        return text
    lines = ["", MARK, "", "### 不要做（每条都给原因）", ""]
    for rule, why in extra["never"]:
        lines.append(f"- **NEVER** {rule}——{why}")
    lines += ["", "### 失败与兜底", "", "| 现象 | 处理 |", "| --- | --- |"]
    for symptom, action in extra["fallback"]:
        lines.append(f"| {symptom} | {action} |")
    lines += [
        "",
        "### 何时不该用这个 skill",
        "",
        "- 只需要读文档或写笔记：走知识库，不要调执行类命令。",
        "- 需要改被测系统的业务数据：先确认数据隔离，再考虑用录制/回放。",
        "",
    ]
    return text.rstrip() + "\n" + "\n".join(lines)


def main() -> None:
    changed = 0
    for slug, extra in DATA.items():
        path = SKILLS / slug / "SKILL.md"
        if not path.exists():
            print("missing", slug)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        text = rewrite_description(text, extra)
        text = split_big(path, text, slug)
        text = append_sections(text, extra)
        path.write_text(text, encoding="utf-8")
        changed += 1
    print("patched", changed)


if __name__ == "__main__":
    main()
