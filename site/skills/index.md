---
title: Skills 库
---

# Skills 库

平台在用的 10 个技能，全部可直接读全文、也可下载原始文件（zip 内含 `SKILL.md` 与 references）。

| 技能 | 一句话说明 | 正文 | references | 预览 | 下载 |
| --- | --- | --- | --- | --- | --- |
| `playwright-cli` | 需要直接驱动浏览器做一次性的页面操作或取页面文本时时使用。支持 playwright, browser, page, … | 302 行 | 11 | [预览](/skills/playwright-cli) | [zip](/skills/playwright-cli.zip) |
| `shenle-android-cli` | 需要在安卓真机或模拟器上完成点击、输入、截图与界面断言时时使用。支持 android, adb, uiautomato… | 301 行 | 2 | [预览](/skills/shenle-android-cli) | [zip](/skills/shenle-android-cli.zip) |
| `shenle-api-record` | 需要抓取接口请求并沉淀成可执行的接口资产或用例时时使用。支持 api-record, 抓包, 代理, 证书, 请求模板… | 118 行 | 1 | [预览](/skills/shenle-api-record) | [zip](/skills/shenle-api-record.zip) |
| `shenle-dynamic-function-generator` | 需要为测试平台动态生成可复用函数（数据处理、断言、适配器）时时使用。支持 generator, 动态函数, 代码生成,… | 293 行 | 2 | [预览](/skills/shenle-dynamic-function-generator) | [zip](/skills/shenle-dynamic-function-generator.zip) |
| `shenle-test-flow-builder` | 把若干接口或页面步骤编排成一条可重复执行的测试流程时时使用。支持 flow, step, yaml, 编排, 断言, … | 265 行 | 4 | [预览](/skills/shenle-test-flow-builder) | [zip](/skills/shenle-test-flow-builder.zip) |
| `shenle-test-plan-generator` | 需要从需求或接口清单生成测试计划、拆出用例范围与排期时时使用。支持 plan, 用例范围, 优先级, 排期, 风险 相… | 171 行 | 4 | [预览](/skills/shenle-test-plan-generator) | [zip](/skills/shenle-test-plan-generator.zip) |
| `shenle-test-runner` | 按计划批量执行用例、汇总结果并产出报告时时使用。支持 runner, 执行, 结果汇总, 报告, 退出码 相关操作；U… | 212 行 | 1 | [预览](/skills/shenle-test-runner) | [zip](/skills/shenle-test-runner.zip) |
| `shenle-web-cli` | 需要用自然语言描述在网页上点击、输入、截图并读回页面状态时时使用。支持 web-cli, 浏览器, navigate,… | 262 行 | 1 | [预览](/skills/shenle-web-cli) | [zip](/skills/shenle-web-cli.zip) |
| `shenle-web-record` | 需要在真实浏览器里录制操作步骤并导出可回放的脚本时时使用。支持 record, 录制, SNAP, 回放, 步骤 相关… | 186 行 | 0 | [预览](/skills/shenle-web-record) | [zip](/skills/shenle-web-record.zip) |
| `skill-creator` | 新建一个 skill 或给已有 skill 补结构、改 description 时时使用。支持 skill, SKIL… | 259 行 | 4 | [预览](/skills/skill-creator) | [zip](/skills/skill-creator.zip) |

## 怎么用

解开 zip，把整个目录放进项目的 `.claude/skills/` 下，重启会话即可被识别。

每个技能的评分与设计取舍见 [Skills 手册](/kb/skills/)，单次调用记录见 [Skills 单跑记录](/labs/skills/)。
