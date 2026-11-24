---
title: shenle-report-generate-html
---

# shenle-report-generate-html

> 使用场景：跑完 shenle-ai-test-runner 之后，要把 allure-results 的 JSON 渲成一份能直接发人的单文件 HTML 报告时用。触发词：「生成测试报告」「把 allure-results 转成 HTML」「生成静态报告」「report.html」「报告要能发给别人」。纯 Python 标准库脚本 scripts/generate_html.py，不依赖 All…

正文 188 行，随包 references 1 个。

读完想直接用：[下载 zip（SKILL.md+references）](/skills/shenle-report-generate-html.zip)　·　看说明与评分：[Skills 手册 · shenle-report-generate-html](/kb/skills/shenle-report-generate-html)

---

# shenle-report-generate-html

## 触发词
- "生成测试报告"
- "把 allure-results 转成 HTML"
- "生成静态报告"
- "shenle-report-generate-html"
- "report.html"

## 前置
- 已跑过 `shenle-ai-test-runner test ...` 至少一次（生成了 `AI-自动化测试报告/&lt;plan-id&gt;/&lt;时间戳&gt;/allure-results/`）
- 不需要 Allure CLI / Java 环境（脚本纯 Python 标准库）

## 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| `--project-dir` | 是 | 项目工作目录（含 `AI-自动化测试报告/` 子目录） |
| `--plan-id` | 是 | 测试计划 ID（如 `plan-20260610182912`） |
| `--timestamp` | 否 | 时间戳 `YYYYMMDD-HHMMSS`；不填则取最新一次 |
| `--latest` | 否 | 等价于不填 timestamp 时取最新 |
| `--output` | 否 | 自定义输出 HTML 路径（默认 `&lt;run-dir&gt;/report.html`） |

## 输出

`&lt;project-dir&gt;/AI-自动化测试报告/&lt;plan-id&gt;/&lt;timestamp&gt;/report.html`

HTML 内容：
- 顶部：测试计划 ID / 时间戳 / 总耗时 / 通过率
- 摘要卡片：总用例 / 通过 / 失败 / 异常 / 跳过
- 每个 case 卡片：
  - 标题、状态徽章、耗时、描述
  - 失败时显示错误信息（红色高亮）
  - 折叠的步骤树（每个 task 4 个嵌套子步骤：input / detail / result / output）
  - 附件直接内嵌显示（JSON pretty-print / 文本原样）

零依赖：单文件 HTML，所有 CSS 内联，所有附件内嵌。方便邮件分享 / 离线查看。

## 用法

### 1. CLI 调用（最常用）

```bash
# 自动选最新一次
python apps/shenle-report-generate-html/scripts/generate_html.py \
    --project-dir "D:\示例项目-读书屋" \
    --plan-id "plan-20260610182912" \
    --latest

# 指定 timestamp
python apps/shenle-report-generate-html/scripts/generate_html.py \
    --project-dir "D:\示例项目-读书屋" \
    --plan-id "plan-20260610182912" \
    --timestamp "20260924-220724"

# 自定义输出路径
python apps/shenle-report-generate-html/scripts/generate_html.py \
    --project-dir "D:\示例项目-读书屋" \
    --plan-id "plan-20260610182912" \
    --latest \
    --output "D:\share\latest-report.html"
```

### 2. 交互流程（agent 帮你跑）

```
用户：帮我把最新的测试报告生成静态 HTML
agent：需要确认两点：
      1. plan-id（测试计划 ID）
      2. timestamp（可选；不填取最新）

用户：plan-id 是 plan-20260610182912
agent：[自动选最新 timestamp] [调脚本] [返回 report.html 路径]
```

### 3. 输出示例

```
[INFO] 自动选最新时间戳：20260924-225340
[INFO] 读 1 个 case, 7 个附件
[OK] HTML 报告已生成：D:\...\AI-自动化测试报告\plan-20260610182912\20260924-225340\report.html
     大小 9.6 KB · 1 case · 1 通过
```

## 项目目录约定

```
{project-dir}/
└── AI-自动化测试报告/
    └── {plan-id}/
        └── {YYYYMMDD-HHMMSS}/
            ├── allure-results/      # shenle-ai-test-runner test 输出的 JSON
            ├── allure-report/       # （可选）allure generate 出的 HTML
            ├── test_xxx.py          # 生成的 pytest 测试
            ├── environment.properties
            └── report.html          # ← 本 skill 的输出
```

## 设计要点

1. **零依赖**：纯 Python 标准库（json / pathlib / html / datetime）
2. **单文件 HTML**：所有 CSS 内联到 `&lt;style&gt;`，所有附件 inline（不是 base64，HTML 里直接是文本，方便浏览器 view-source）
3. **可打印**：`@media print` 折叠默认展开，方便打印 PDF
4. **附件 inline**：JSON 自动 pretty-print，TXT/HTML 保留原格式
5. **嵌套步骤树**：allure 的 step 嵌套结构忠实展示，task 标题 → input/detail/result/output 4 个子步骤
6. **支持失败状态**：失败的 case 红色徽章 + 错误信息高亮（`statusDetails.message`）
7. **自动选最新**：不填 timestamp 时找 `&lt;plan-dir&gt;` 下字典序最大的子目录（YYYYMMDD-HHMMSS 格式）

## 常见问题

| 问题 | 解决 |
|------|------|
| `allure-results 不存在` | 先跑 `shenle-ai-test-runner test ...` 至少一次 |
| `没有 YYYYMMDD-HHMMSS 格式的子目录` | 检查 `AI-自动化测试报告/&lt;plan-id&gt;/` 下有没有跑过的 run |
| HTML 中文乱码 | 文件已 UTF-8 编码；浏览器要选 UTF-8 编码 |
| 附件 `[附件文件丢失: &lt;source&gt;]` | allure-results 文件被删了；从原始 test 报告目录重新跑 |
| 想批量生成所有 timestamp | 用 shell 循环：`for ts in $(ls); do python ... --timestamp $ts; done` |

## 关联

- 数据来源 → [shenle-ai-test-runner 6.0+](../../shenle-ai-test-runner/04-apps/shenle-ai-test-runner6.0/) 生成的 allure-results/
- 脚本源码 → [scripts/generate_html.py](../../scripts/generate_html.py)
- 项目 README → [README.md](../../README.md)

## 先读约定

MANDATORY：动手前先读 `references/report-structure.md`，HTML 结构与体积约定都在那里；正文只讲判断与避坑。

## 执行顺序

1. 先确认输入存在：`AI-自动化测试报告/&lt;plan-id&gt;/&lt;timestamp&gt;/allure-results/` 里有 `*-result.json`。
2. 不填 `--timestamp` 就取最新一次；要固定某次就显式写时间戳。
3. 跑 `scripts/generate_html.py --project-dir &lt;dir&gt; --plan-id &lt;id&gt;`，等它打印输出路径。
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
- HTML 打开是空白：多半是附件路径写死成绝对路径，重新生成一次并检查 `&lt;run-dir&gt;` 结构。
- 体积过大：先删掉大附件或改 `--output` 另存，再决定要不要外链。
- 兜底：直接用 `python scripts/generate_html.py --help` 看当前版本支持的参数，别猜。

## 一页速查

| 想干什么 | 命令 |
| --- | --- |
| 生成最新一轮报告 | `python scripts/generate_html.py --project-dir . --plan-id &lt;id&gt;` |
| 指定某轮 | 追加 `--timestamp 20260610-182912` |
| 另存路径 | 追加 `--output out/report.html` |
| 看参数 | `python scripts/generate_html.py --help` |
| 确认产出 | 打开 `&lt;run-dir&gt;/report.html` |
| 复现一次 | `.venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q` |

## 示例

```bash
python .claude/skills/shenle-report-generate-html/scripts/generate_html.py \
  --project-dir . --plan-id plan-20260610182912
```

## 说明

正文只讲判断与避坑；脚本参数与 HTML 结构以 `scripts/generate_html.py --help` 和本页上半部分为准。

