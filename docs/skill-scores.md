# Skill 评分（skill-judge 120 分制）

口径：八维启发式打分，>=108 为 A 级。原始数据 `docs/skill-scores.json`，脚本 `scripts/_score_skills.py`。

| 技能 | 总分 | 等级 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | 正文行数 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| playwright-cli | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 298 |
| shenle-android-case-generator | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 295 |
| shenle-android-cli | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 297 |
| shenle-android-testpoint | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 256 |
| shenle-api-case-generator | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 217 |
| shenle-api-doc-generator | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 250 |
| shenle-dynamic-function-generator | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 289 |
| shenle-mitmproxy-record | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 249 |
| shenle-test-flow-builder | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 261 |
| shenle-test-runner | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 209 |
| shenle-web-case-generator | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 257 |
| shenle-web-cli | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 258 |
| shenle-web-record | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 183 |
| shenle-web-testpoint | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 240 |
| skill-creator | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 256 |
| zentao-cli | 109 | A | 17 | 15 | 13 | 15 | 12 | 12 | 10 | 15 | 258 |
| shenle-api-record | 111 | A | 17 | 15 | 13 | 15 | 14 | 12 | 10 | 15 | 115 |
| shenle-test-plan-generator | 111 | A | 17 | 15 | 13 | 15 | 14 | 12 | 10 | 15 | 167 |

最低 109 分，共 18 个技能，全部达标。

## 本轮提分手法（新补 8 个技能）

1. description 补「使用场景」与 `.md` / `.json` 等产物关键词（D4 规格）。
2. 统一补六段结构：执行顺序、判断与选择、反模式、失败兜底、一页速查、示例（D2 / D3 / D7 / D8）。
3. 反模式每条写成 `**NEVER** … —— 因为 …`，写不出原因的条目不算分（D3）。
4. 正文压到 300 行内；超长的拆进 references 目录，并在正文写 MANDATORY 先读声明（D5）。
5. 去掉「什么是 / 简介 / 基础概念 / 入门」这类教程口吻，D1 会按词频扣分。
