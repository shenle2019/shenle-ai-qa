# -*- coding: utf-8 -*-
"""生成 43–45 章笔记、站点页，并同步计数。"""

from pathlib import Path

N43 = """# 第 43 章 · 用例与关键字执行器

平台的核心不是页面，是**执行器**：一条用例被拆成若干步骤，每一步是「关键字 + 参数」，执行器负责变量替换、按序执行、失败即停、把结果整理成可读结构。

## 1. 一条用例长什么样

```json
{"id": "login-and-read", "steps": [
  {"kw": "http", "method": "POST", "path": "/api/login", "body": {"user": "alice"}, "expect": 200},
  {"kw": "extract", "path": "data.id", "name": "uid"},
  {"kw": "http", "method": "GET", "path": "/api/users/${uid}"}
]}
```

五类关键字就够起步：`http`（发请求）、`status`（断言状态码）、`json`（断言字段）、`extract`（把响应里的值存进上下文）、`sleep`。要扩展时注册到 `KEYWORDS` 即可。

## 2. 三个必须做对的细节

- **变量取不到就报错**：`${uid}` 没有值时抛 `CaseError`，不能变成空串——否则请求打到 `/api/users/`，错误会以 404 的形式出现在很远的地方。
- **失败即停**：某一步失败后不再执行后续步骤，并在 `CaseResult.failed_step` 里给出是第几步、哪个关键字、什么原因。
- **单条失败不炸整批**：执行器内部捕获异常并转成结果对象，这样计划里其它用例还能继续跑。

## 3. 本章实操

`labs/ch43-executor/`：`executor.py`（`render` / `pick` / `KEYWORDS` / `run_case` / `summarise`）、`test_executor.py`（8 条，用 `FakeSession` 离线跑）。

```bash
python -m pytest labs/ch43-executor -q
```

## 4. 常见坑

1. 步骤之间靠全局变量传值——并发跑两条用例就串了，上下文必须是每条用例一份。
2. 断言写在 `http` 关键字里，导致「发了请求」和「验证结果」耦合，失败原因说不清。
3. 提取路径不支持下标，拿不到列表里的元素。
4. 步骤里出现未知关键字却静默跳过——要报错。
5. 结果只有 pass/fail，没有「第几步失败」，排查要重跑。

## 5. 自测

1. 为什么变量缺失要抛错而不是给空串？
2. 断言为什么要独立成关键字？
3. 上下文为什么必须按用例隔离？
4. 失败即停和继续执行，各自适合什么场景？
5. 结果里为什么要记录每一步而不仅是最终状态？

## 附：自测答案

1. 空串会让请求变成「路径不完整」或「参数为空」，错误在更远处爆发；早失败能定位到具体变量。
2. 分离之后，`http` 只负责发请求，`status/json` 只负责判断，失败原因一目了然，也便于复用。
3. 否则两条用例并行时会互相覆盖变量，出现「单独跑通过、一起跑失败」的偶发问题。
4. 同一业务链路内的步骤应失败即停（后续步骤依赖前一步结果）；互不依赖的用例应继续执行（一次跑出全部问题）。
5. 只有最终状态时，失败需要重跑复现；记录每一步能直接看出「卡在哪一步、实际返回什么」。

## 学生常问

Q：关键字和函数有什么区别？

A：关键字是「给平台用户用的」，参数是数据（可来自 YAML）；函数是给开发者用的。关键字要做参数校验、错误信息友好。

Q：要不要支持脚本步骤（写 Python 代码）？

A：可以留一个 `python` 关键字作为逃生口，但要限制在受控环境运行，否则平台就成了任意代码执行器。

## 面试题

Q：执行器怎么支持并发？

A：每条用例独立上下文 + 独立会话；执行器本身无共享可变状态；并发度由调度层控制，不在关键字里做。

Q：怎么保证用例可重复执行？

A：数据自己造、跑完自己清（fixture 思路）；不依赖执行顺序；断言只依赖本次请求的结果。

## 延伸知识

- `pick` 支持 `a.b.0.c` 就够了，过度实现 JSONPath 反而增加维护成本。
- 步骤上支持 `retry` 与 `timeout` 两个可选字段，比全局重试更精确。
- 把 `CaseResult` 直接序列化成 JSON 存库，报告与回放都用它。
"""

N44 = """# 第 44 章 · 测试计划与异步执行

一次跑几百条用例，不能让 HTTP 请求一直挂着。平台需要「提交即返回、后台跑、可查状态」，也就是一个队列 + 一个 worker。

## 1. 状态机

```
queued -> running -> passed
                 \\-> failed（重试次数用尽）
                 \\-> queued（还有重试机会）
```

三个状态对外暴露：提交后前端轮询的是 `summary()`，不是逐条结果。

## 2. 为什么用队列

- **解耦**：接口层只负责入队，响应时间与用例数量无关。
- **削峰**：一次提交 500 条不会瞬间打出 500 个请求。
- **可重试**：失败任务重新入队即可，不需要调用方感知。

`Runner` 用一个 daemon 线程消费 `queue.Queue`，`close()` 放入哨兵 `None` 让线程退出——这是 Python 里最省事的「优雅停止」。

## 3. 重试的两个细节

1. **重试次数记在任务上**，不是记在计划上；否则同一个计划里不同用例会互相影响。
2. **重试不是万能的**：断言失败重试只会更慢，只有网络抖动、依赖未就绪才值得重试。

## 4. 本章实操

`labs/ch44-plans/`：`plans.py`（`Plan` / `Task` / `Runner` / `wait_idle` / `summary` / `close`）、`test_plans.py`（8 条）。

```bash
python -m pytest labs/ch44-plans -q
```

## 5. 常见坑

1. worker 线程不是 daemon，进程退出时挂住。
2. `wait_idle` 用固定 `sleep` 而不是轮询状态，慢且不稳。
3. 重试时没有上限，坏用例永久占着队列。
4. 计划空用例也能提交，跑完显示「0/0 通过」。
5. 通知与执行耦合在同一个线程里，通知慢就拖慢执行。

## 6. 自测

1. 为什么提交接口要立即返回而不是同步跑完？
2. 重试次数为什么记在任务上？
3. `close()` 里放 `None` 的作用是什么？
4. 什么错误值得重试？
5. 前端应该轮询什么？

## 附：自测答案

1. 用例多时同步跑会让请求超时；异步化后调用方拿到 task_id 就能返回，结果靠轮询。
2. 同一计划里不同用例的稳定性不同，记在计划上会让「坏用例的重试」挤占「好用例的次数」。
3. 作为哨兵，让 worker 从阻塞的 `get()` 里醒来并退出循环，否则线程永远等下去。
4. 网络超时、连接被重置、依赖刚启动还没就绪；断言失败、参数错误这类确定性失败不该重试。
5. 计划的汇总状态（total/passed/failed/queued），必要时再拉逐条明细，避免每次都传全量。

## 学生常问

Q：为什么不用线程池而用一个队列？

A：队列天然是单消费者、顺序可控；要并发就开多个 worker 消费同一个队列，调度策略不用改。

Q：任务状态存内存还是数据库？

A：演示用内存即可；生产要落库，因为进程重启后内存状态会丢，用户看到的是「任务消失」。

## 面试题

Q：异步执行的接口怎么设计？

A：POST 提交返回 202 + task_id；GET 查询状态与结果；失败可重试；结果有 TTL。

Q：跑批任务怎么防止重复提交？

A：计划维度加幂等键（plan_id + 时间窗），重复提交返回已有 task_id。

## 延伸知识

- 多 worker 时把 `tasks` 换成带锁的字典或外部存储，避免读写竞争。
- 通知用独立的回调或队列，不要占用执行线程。
- 给任务加 `created_at`，便于清理僵尸任务。
"""

N45 = """# 第 45 章 · 平台收口：报告、门槛与部署

前面五章是零件，这一章把它们装成一台能交给别人的机器：一份报告、一个门槛、一条启动命令。

## 1. 报告要回答三个问题

| 问题 | 字段 |
| --- | --- |
| 跑了多少、过了多少 | `total` / `passed` / `pass_rate` |
| 哪些没过、为什么 | 逐条 `status` + `error` |
| 结论是什么 | `gate()` 的 `(ok, reasons)` |

`to_markdown()` 给人看（能贴进 PR 与工单），`to_junit()` 给 CI 看（Jenkins、GitHub Actions 都能直接渲染失败用例）。

## 2. 门槛要可判定

`thresholds` 两个维度：`pass_rate`（比例）与 `max_duration_ms`（单条耗时上限）。`gate()` 返回「是否通过 + 原因列表」，原因必须带具体数值，例如 `通过率 0.5 低于门槛 0.95`、`超时用例：slow`。

这和性能阶段第 39 章是同一套思路：**退出码 0/1 由门槛决定，不由人判断**。

## 3. 部署三件事

1. **一条命令起服务**：`uvicorn app:app --host 0.0.0.0 --port 8000`，配置从环境变量来。
2. **健康检查**：`GET /health` 返回版本与依赖状态，容器编排靠它判断就绪。
3. **数据落盘**：SQLite 文件要挂卷，否则每次部署数据清零。

## 4. 本章实操

`labs/ch45-report/`：`report.py`（`Outcome` / `Report` / `gate` / `to_markdown` / `to_junit`）、`test_report.py`（8 条）。

```bash
python -m pytest labs/ch45-report -q
```

## 5. 常见坑

1. 报告只给总数，失败原因靠人翻日志。
2. JUnit 不转义特殊字符，CI 解析报错。
3. 门槛写死在代码里，换个项目就要改代码。
4. 部署时不挂卷，重启后「历史任务全没了」。
5. 平台自己没监控，挂了没人知道。

## 6. 自测

1. 为什么报告要两种格式？
2. 门槛为什么返回原因列表而不是布尔？
3. JUnit 为什么要转义？
4. 部署时数据为什么要挂卷？
5. 平台自身的健康检查应该包含什么？

## 附：自测答案

1. Markdown 给人看、能贴进 PR；JUnit 给 CI 解析、能标红失败用例。两者消费方不同。
2. 布尔只能告诉「没过」，列表能说明「哪条、越了多少」，直接指向修复动作。
3. 用例名与错误信息里可能有 `<`、`&`，不转义会让 XML 结构损坏，CI 直接解析失败。
4. 容器重建会清空文件系统，SQLite 不挂卷等于每次部署丢数据。
5. 进程存活、数据库可连接、依赖服务可达、版本号；有队列的还要看积压。

## 学生常问

Q：报告要存多久？

A：至少保留最近若干次与关键版本；长期可用对象存储，只留摘要。

Q：门槛卡在 CI 里会不会误伤？

A：先用 warning 级别观察一段时间，稳定后再设成阻断；阈值按服务分级。

## 面试题

Q：一个测试平台怎么算「可用」？

A：三件事：能提交、能看到结果、结果可信。前两件是工程问题，第三件靠数据隔离与断言质量。

Q：平台怎么做权限？

A：项目维度分角色（管理员/测试/开发/只读），接口层校验，前端只做展示控制。

## 延伸知识

- 报告加「与上次对比」比绝对值更有用，需要落历史。
- `to_junit` 可扩展 `<system-out>` 放执行日志。
- 部署用 Docker 时把 `.venv` 排除，镜像只装 `requirements.txt`。
"""

N = {"ch43-executor": ("43 · 用例与关键字执行器", N43), "ch44-plans": ("44 · 测试计划与异步执行", N44), "ch45-report": ("45 · 平台收口：报告、门槛与部署", N45)}

for slug, (title, note) in N.items():
    num = slug.split("-")[0]
    Path(f"notes/{slug}.md").write_text(note.strip() + "\n", encoding="utf-8")
    Path(f"site/chapters/{num}.md").write_text(f"---\ntitle: {title}\n---\n\n<!--@include: ../../notes/{slug}.md-->\n", encoding="utf-8")

cfg = Path("site/.vitepress/config.mts")
text = cfg.read_text(encoding="utf-8")
anchor = "            { text: '42 接口资产与一致性校验', link: '/chapters/ch42' },\n"
assert text.count(anchor) == 2, text.count(anchor)
add = (
    "            { text: '43 用例与关键字执行器', link: '/chapters/ch43' },\n"
    "            { text: '44 测试计划与异步执行', link: '/chapters/ch44' },\n"
    "            { text: '45 平台收口', link: '/chapters/ch45' },\n"
)
if "/chapters/ch43" not in text:
    cfg.write_text(text.replace(anchor, anchor + add), encoding="utf-8")

ROWS = "".join(
    f"| {slug.split('-')[0]} | {title.split(' · ')[1]} | `labs/{slug}` |\n" for slug, (title, _) in N.items()
)
LABROWS = "| 43 | `labs/ch43-executor` | 关键字与执行链 | 8 |\n| 44 | `labs/ch44-plans` | 队列/重试/状态 | 8 |\n| 45 | `labs/ch45-report` | 报告与门槛 | 8 |\n"

for target in [Path("site/index.md"), Path("site/chapters/index.md")]:
    body = target.read_text(encoding="utf-8")
    if "| 43 |" in body:
        continue
    last = "| 42 | 接口资产与一致性校验 | `labs/ch42-assets` |\n"
    if last in body:
        body = body.replace(last, last + ROWS, 1)
    else:
        body = body.rstrip("\n") + "\n" + ROWS
    target.write_text(body, encoding="utf-8")

labs_page = Path("site/labs/index.md")
body = labs_page.read_text(encoding="utf-8")
if "| 43 |" not in body:
    body = body.rstrip("\n") + "\n" + LABROWS
    labs_page.write_text(body, encoding="utf-8")

for target in [Path("site/index.md"), Path("site/chapters/index.md"), Path("site/labs/index.md"), Path("README.md"), Path("STAGE-BRIEF.md")]:
    body = target.read_text(encoding="utf-8")
    new = body.replace("417 条", "469 条").replace("三十九个实操", "四十五个实操").replace("39 章", "45 章")
    if new != body:
        target.write_text(new, encoding="utf-8")

print("notes + site + counts ok")
