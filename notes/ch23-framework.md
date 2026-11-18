# 第 23 章 · 框架收口：一个能交给别人的 CLI

本章目标：把前七章拼成一个「别人拿到能跑」的框架——配置驱动、命令行入口、两种报告、退出码正确。

## 1. 交付标准

一个测试框架能不能交给别人，看四件事：

| 标准 | 本章怎么满足 |
| --- | --- |
| 不改代码就能换环境 | `config.yaml` 的 `envs` + `--env` |
| 不改代码就能挑用例 | `--only login` 按 id 过滤 |
| 跑完有可读结论 | Markdown 报告（人看）+ JUnit XML（CI 看） |
| 退出码可判断 | 0 全通过 / 1 有失败 / 2 配置错误 |

## 2. 分层

```
config.yaml   →  fw_runner.py  →  fw_pages.py  →  浏览器
                       ↓
                  fw_report.py  →  .md / .xml
```

- **config**：环境、用例，纯数据；
- **runner**：分派 action、收集 `Result`、汇总 `Report`；
- **pages**：业务动作，不出现选择器；
- **report**：把 `Report` 渲染成两种格式，不做业务判断。

## 3. 命令行

```powershell
# 跑默认环境
.\.venv\Scripts\python.exe labs/ch23-framework/run.py

# 只跑登录相关，出 Markdown 报告
.\.venv\Scripts\python.exe labs/ch23-framework/run.py --only login --report reports/login.md

# 指定地址 + JUnit 报告（给 CI）
.\.venv\Scripts\python.exe labs/ch23-framework/run.py --base-url http://127.0.0.1:9000 --report reports/junit.xml
```

输出长这样：

```
[PASS] login-ok               412 ms  登录成功
[FAIL] search-hit             118 ms  AssertionError: 只命中 0 条

合计 5 条，通过 4，失败 1（环境 local · http://127.0.0.1:8000）
报告已写入：reports/login.md
```

## 4. 两个容易做错的地方

**配置校验要放在启动浏览器之前**。否则 `--env nope` 这种低级错误会先花 1 秒起浏览器再报错，CI 里尤其浪费。本章的实现是：`load_config` → `pick_env` → 校验 `--only` 是否命中 → 再启动 Playwright。

**CLI 的测试要用子进程**。在 pytest 里直接调 `main()`，会和已经启动的 `sync_playwright` 撞「Sync API inside asyncio loop」——因为 CLI 自己也开了一个 Playwright 上下文。用 `subprocess.run([sys.executable, "run.py", ...])` 才是真的在测 CLI。

## 5. 本章实操

`labs/ch23-framework/`：

| 文件 | 作用 |
| --- | --- |
| `config.yaml` | 2 个环境 + 5 条用例 |
| `fw_pages.py` | `LoginPage` / `TodoPage` / `SearchPage` |
| `fw_runner.py` | `load_config` / `pick_env` / `HANDLERS` / `run` / `Result` / `Report` |
| `fw_report.py` | `to_markdown` / `to_junit` / `write` |
| `run.py` | CLI：`--env` `--only` `--base-url` `--report` `--headed` |
| `tests/test_runner.py` | 10 条：配置校验（默认环境、id 重复）、环境解析、`--only` 过滤、全量跑通、失败被记录且不中断、两种报告格式、CLI 退出码 0/2、子进程跑真 CLI |

跑法：

```powershell
.\.venv\Scripts\python.exe -m pytest labs/ch23-framework -q
```

## 6. 自测

1. 为什么配置校验要放在启动浏览器之前？
2. `Report.ok` 为什么要单独做成属性？
3. 为什么 CLI 的测试要用子进程？
4. 报告里除了通过率，还该有什么？

## 附：自测答案

1. 因为「环境名写错」这类错误不需要浏览器就能发现。先起浏览器再报错，等于每次配置错误都多花 1–2 秒，而且 CI 里会显示成「测试失败」而不是「配置错误」。
2. 因为「整批是否通过」和「有没有失败」是同一件事的两个表达，重复写 `failed == 0` 容易在某处写成 `passed > 0`。收成一个属性，调用方只读它。
3. 因为 pytest 进程里可能已经有 Playwright 上下文，而 CLI 会再开一个，同线程双开 sync API 会直接报错。子进程还能顺带验证「真实退出码」和「真实 stdout」。
4. 耗时分布与环境信息。只有通过率，看不出「这批慢了 3 倍」，也分不清 staging 的失败是不是环境问题。

## 学生常问

**Q：为什么不直接用 pytest 当框架，非要自己写 CLI？**

A：两者都要：pytest 管「用例级断言」与 IDE/CI 集成，CLI 管「按配置跑一批、出报告、给非技术同学用」。本章的 CLI 是一种「业务视角入口」，内部照样可以调 pytest。

**Q：JUnit XML 为什么还要支持？**

A：因为 CI 都认它。GitHub Actions、Jenkins、GitLab 都能把 JUnit 渲染成「哪些用例失败」，比自己解析 Markdown 省事。

**Q：`--only` 用子串匹配会不会误伤？**

A：会（`login` 会匹配到 `login-ok` 和 `relogin`）。本章故意保持简单，生产里建议用精确 id 或标签（`--tag smoke`）——标签比子串稳。

## 面试题

**Q：一个测试框架你怎么分层？**

A：四层：配置（环境/用例数据）、驱动（浏览器与 HTTP 客户端）、页面对象（业务动作）、执行与报告（调度、汇总、输出）。分层的判断标准是「改一层不影响上层」：换浏览器只改驱动，加用例只加配置。

**Q：框架交付给别人，你最在意什么？**

A：文档里三行能跑起来（安装 → 配置 → 一条命令），以及失败信息能自己说话。别人跑挂了第一件事是看你留下的报错，报错里没有「哪条用例、哪一步、什么值」，框架就等于没交付。

**Q：怎么让框架在 CI 里稳定？**

A：四件事：固定浏览器版本（`playwright install --with-deps chromium` 锁版本）、固定测试数据（唯一前缀 + 清理）、给整批设超时、失败自动上传截图与 trace。缺一件就会开始出现「本地过 CI 不过」。

**Q：测试报告你会放哪些信息？**

A：环境（base_url、浏览器版本）、用例（id、标题、结果、耗时）、失败详情（异常类型、关键值、截图/trace 路径）、汇总（通过率、慢用例 Top3）。报告是给人排查用的，不是给领导看数字的。

## 延伸知识

- **`exit code 2` 的约定**：多数 CLI 用 2 表示「用法/配置错误」，把它和「测试失败」区分开，CI 才能给出不同提示。
- **报告目录进 `.gitignore`**：`reports/` 是运行产物，每次跑都变，提交会把 diff 撑爆。
- **`--headed` 与 `--slowmo`**：演示与排错时打开，`slowmo=200` 能看清每一步；日常必须 headless。
- **配置的「环境矩阵」**：`--env local,staging` 跑两遍是常见需求，实现只需在外层循环，但报告要按环境分开，否则通过率会混在一起。
