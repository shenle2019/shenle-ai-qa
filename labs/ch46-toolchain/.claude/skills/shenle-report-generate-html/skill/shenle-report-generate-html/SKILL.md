---
name: shenle-report-generate-html
description: 把 shenle-ai-test-runner 跑出的 allure-results/ JSON 数据渲染成单文件静态 HTML 报告（无需 Allure CLI / Java 环境）。接受 plan-id 和 timestamp，输出 report.html 到对应 run 目录。
---

# shenle-report-generate-html

## 触发词
- "生成测试报告"
- "把 allure-results 转成 HTML"
- "生成静态报告"
- "shenle-report-generate-html"
- "report.html"

## 前置
- 已跑过 `shenle-ai-test-runner test ...` 至少一次（生成了 `AI-自动化测试报告/<plan-id>/<时间戳>/allure-results/`）
- 不需要 Allure CLI / Java 环境（脚本纯 Python 标准库）

## 输入

| 参数 | 必填 | 说明 |
|------|------|------|
| `--project-dir` | 是 | 项目工作目录（含 `AI-自动化测试报告/` 子目录） |
| `--plan-id` | 是 | 测试计划 ID（如 `plan-20260610182912`） |
| `--timestamp` | 否 | 时间戳 `YYYYMMDD-HHMMSS`；不填则取最新一次 |
| `--latest` | 否 | 等价于不填 timestamp 时取最新 |
| `--output` | 否 | 自定义输出 HTML 路径（默认 `<run-dir>/report.html`） |

## 输出

`<project-dir>/AI-自动化测试报告/<plan-id>/<timestamp>/report.html`

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
2. **单文件 HTML**：所有 CSS 内联到 `<style>`，所有附件 inline（不是 base64，HTML 里直接是文本，方便浏览器 view-source）
3. **可打印**：`@media print` 折叠默认展开，方便打印 PDF
4. **附件 inline**：JSON 自动 pretty-print，TXT/HTML 保留原格式
5. **嵌套步骤树**：allure 的 step 嵌套结构忠实展示，task 标题 → input/detail/result/output 4 个子步骤
6. **支持失败状态**：失败的 case 红色徽章 + 错误信息高亮（`statusDetails.message`）
7. **自动选最新**：不填 timestamp 时找 `<plan-dir>` 下字典序最大的子目录（YYYYMMDD-HHMMSS 格式）

## 常见问题

| 问题 | 解决 |
|------|------|
| `allure-results 不存在` | 先跑 `shenle-ai-test-runner test ...` 至少一次 |
| `没有 YYYYMMDD-HHMMSS 格式的子目录` | 检查 `AI-自动化测试报告/<plan-id>/` 下有没有跑过的 run |
| HTML 中文乱码 | 文件已 UTF-8 编码；浏览器要选 UTF-8 编码 |
| 附件 `[附件文件丢失: <source>]` | allure-results 文件被删了；从原始 test 报告目录重新跑 |
| 想批量生成所有 timestamp | 用 shell 循环：`for ts in $(ls); do python ... --timestamp $ts; done` |

## 关联

- 数据来源 → [shenle-ai-test-runner 6.0+](../../shenle-ai-test-runner/04-apps/shenle-ai-test-runner6.0/) 生成的 allure-results/
- 脚本源码 → [scripts/generate_html.py](../../scripts/generate_html.py)
- 项目 README → [README.md](../../README.md)
