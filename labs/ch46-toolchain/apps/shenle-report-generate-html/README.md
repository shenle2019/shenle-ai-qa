# shenle-report-generate-html

把 `shenle-ai-test-runner test` 跑出的 `allure-results/` JSON 数据渲染成单文件静态 HTML 报告。

**零依赖**：纯 Python 标准库，**不需要** Allure CLI / Java 环境。

## 功能

- 读 `AI-自动化测试报告/<plan-id>/<时间戳>/allure-results/*.json`
- 渲染成单文件 HTML，所有 CSS 内联、附件 inline
- 输出 `AI-自动化测试报告/<plan-id>/<时间戳>/report.html`

## 安装 / 使用

无需安装，直接调脚本：

```bash
python apps/shenle-report-generate-html/scripts/generate_html.py \
    --project-dir "D:\示例项目-读书屋" \
    --plan-id "plan-20260610182912" \
    --latest
```

## CLI 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--project-dir` | 是 | 项目工作目录 |
| `--plan-id` | 是 | 测试计划 ID |
| `--timestamp` | 否 | 时间戳 YYYYMMDD-HHMMSS（不填取最新） |
| `--latest` | 否 | 取最新一次 run |
| `--output` | 否 | 自定义输出路径 |

详见 [skill/shenle-report-generate-html/SKILL.md](skill/shenle-report-generate-html/SKILL.md)。

## 项目结构

```
apps/shenle-report-generate-html/
├── README.md
├── skill/
│   └── shenle-report-generate-html/
│       └── SKILL.md
└── scripts/
    └── generate_html.py    # 核心脚本（单文件，纯标准库）
```

## 与 shenle-ai-test-runner 的关系

```
shenle-ai-test-runner test ...
   ↓
生成 AI-自动化测试报告/<plan>/<时间戳>/allure-results/*.json
   ↓
shenle-report-generate-html ...
   ↓
生成 AI-自动化测试报告/<plan>/<时间戳>/report.html（单文件，可分享）
```

`shenle-ai-test-runner` 也能调 `allure generate` 出 HTML（需要 Allure CLI + Java），但本工具更轻量，单文件输出方便分享。

## 关联

- 数据来源 → [shenle-ai-test-runner 6.0+](../../shenle-ai-test-runner/04-apps/shenle-ai-test-runner6.0/)
- 触发方式 → [skill/shenle-report-generate-html/SKILL.md](skill/shenle-report-generate-html/SKILL.md)
