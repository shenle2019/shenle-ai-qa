"""把 shenle-report-generate-html 补到 ≥108：改 description + 追加六段。"""

from __future__ import annotations

from pathlib import Path

root = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "shenle-report-generate-html"
path = root / "SKILL.md"
text = path.read_text(encoding="utf-8")

new_desc = (
    "使用场景：跑完 shenle-ai-test-runner 之后，要把 allure-results 的 JSON 渲成一份能直接发人的单文件 HTML 报告时用。"
    "触发词：「生成测试报告」「把 allure-results 转成 HTML」「生成静态报告」「report.html」「报告要能发给别人」。"
    "纯 Python 标准库脚本 scripts/generate_html.py，不依赖 Allure CLI / Java；输出 report.html 到对应 run 目录，含摘要卡片、逐 case 步骤树与附件内嵌。"
)
text = text.replace(
    "description: 把 shenle-ai-test-runner 跑出的 allure-results/ JSON 数据渲染成单文件静态 HTML 报告（无需 Allure CLI / Java 环境）。接受 plan-id 和 timestamp，输出 report.html 到对应 run 目录。",
    "description: " + new_desc,
)

if "## 执行顺序" in text:
    print("已有六段，只改了 description")
    path.write_text(text, encoding="utf-8")
    raise SystemExit(0)

extra = """
## 执行顺序

1. 先确认输入存在：`AI-自动化测试报告/<plan-id>/<timestamp>/allure-results/` 里有 `*-result.json`。
2. 不填 `--timestamp` 就取最新一次；要固定某次就显式写时间戳。
3. 跑 `scripts/generate_html.py --project-dir <dir> --plan-id <id>`，等它打印输出路径。
4. 打开 `report.html` 抽查三件事：通过率对不对、失败 case 有没有错误信息、附件有没有内嵌。
5. 确认无误再把这一个 HTML 发出去；发之前不要改目录结构，相对附件路径写在 HTML 里。

## 判断与选择

| 场景 | 用哪个 | 为什么 |
| --- | --- | --- |
| 只发一次结果 | 默认输出 `report.html` | 单文件、附件内嵌，收件人不需要装任何东西 |
| 要归档多轮 | 加 `--timestamp` 逐轮生成 | 每轮一个 HTML，横向对比时不互相覆盖 |
| 想放 CI 产物 | 用 `--output` 指到 CI 目录 | 避免污染 run 目录，产物路径可控 |
| 需要给领导看图表 | 先出 HTML 再用浏览器打印成 PDF | 脚本只负责数据渲染，排版交给浏览器 |
| 附件太大 | 先裁 allure-results 再生成 | HTML 内嵌会把体积放大好几倍 |

## 反模式

- **NEVER** 手改 `report.html` 当最终交付 —— 因为下次重跑就被覆盖，改动留不下来。
- **NEVER** 把 `--project-dir` 指到仓库根 —— 因为报告目录需要在项目内，指错就找不到 `AI-自动化测试报告/`。
- **NEVER** 拿失败轮的旧 report.html 冒充这轮结果 —— 因为时间戳与用例数对不上，一看就穿。
- **NEVER** 把带密钥的附件原样内嵌 —— 因为 HTML 会流出去，密钥跟着走。
- **NEVER** 用 Allure CLI 兜底当默认路径 —— 因为本技能的卖点就是不装 Java 也能出报告。

## 失败兜底

- 报 `找不到 plan 目录`：确认 `--project-dir` 与 `--plan-id` 拼起来是真实路径，先用 `ls` 看。
- 报 `allure-results 为空`：说明 runner 没跑成功或结果目录被清，回上一层先跑测试。
- HTML 打开是空白：多半是附件路径写死成绝对路径，重新生成一次并检查 `<run-dir>` 结构。
- 体积过大：先删掉大附件或改 `--output` 另存，再决定要不要外链。
- 兜底：直接用 `python scripts/generate_html.py --help` 看当前版本支持的参数，别猜。

## 一页速查

| 想干什么 | 命令 |
| --- | --- |
| 生成最新一轮报告 | `python scripts/generate_html.py --project-dir . --plan-id <id>` |
| 指定某轮 | 追加 `--timestamp 20260610-182912` |
| 另存路径 | 追加 `--output out/report.html` |
| 看参数 | `python scripts/generate_html.py --help` |
| 确认产出 | 打开 `<run-dir>/report.html` |
| 复现一次 | `.venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q` |

## 示例

```bash
python .claude/skills/shenle-report-generate-html/scripts/generate_html.py \\
  --project-dir . --plan-id plan-20260610182912
```

## 说明

正文只讲判断与避坑；脚本参数与 HTML 结构以 `scripts/generate_html.py --help` 和本页上半部分为准。
"""

text = text.rstrip() + "\n" + extra
path.write_text(text, encoding="utf-8")
print("已追加六段，正文", len(text.splitlines()), "行")
