---
title: shenle-report-generate-html 单跑记录
---

# shenle-report-generate-html 单跑记录

> 分组：**报告与扩展**　手册：[shenle-report-generate-html](/kb/skills/report-generate-html)

## 环境

- 仓库：`shenle-ai-qa`，虚拟环境 `.venv`（Python 3.11.9）
- 技能：`.claude/skills/` 下已注册；可安装的命令用 `pip install -e --no-deps` 注册为控制台脚本

## 本次调用

```bash
python .claude/skills/shenle-report-generate-html/scripts/generate_html.py --help
```

## 真实输出

```text
usage: shenle-report-generate-html [-h] --project-dir PROJECT_DIR --plan-id
PLAN_ID [--timestamp TIMESTAMP] [--latest]
[--output OUTPUT]
把 allure-results/ 渲染成单文件静态 HTML 报告。
```

## 判读

- 退出正常、能看到命令自身的用法/版本，说明**注册与依赖这一层通了**。
- 产物形态：`report.html`
- 需要人工或外部条件（点 SNAP、真机、视觉模型 key）的步骤，标注为「未能自动验证」，不写成功。

## 复现

```bash
.venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q
```
