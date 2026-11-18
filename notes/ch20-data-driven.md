# 第 20 章 · 数据驱动与多用例管理

本章目标：把「一条用例一个函数」改成「一张表管一批用例」。做完你能说清什么该参数化、什么不该。

## 1. 什么该参数化

同一个动作、不同输入、不同期望——这是参数化的典型场景：

```yaml
- id: login-ok
  title: 正确账号能登录
  action: login
  params: { username: alice, password: secret }
  expect: { path: /todos, user: alice }
- id: login-bad-password
  title: 密码错误停在登录页
  action: login
  params: { username: alice, password: nope }
  expect: { path: /login, error: 用户名或密码错误 }
```

相反的，**流程不同、断言不同、前置不同**的用例不要硬塞进一张表，塞进去的结果是一堆 if/else。

判断标准：**处理器（action）能不能复用**。能复用就参数化，不能就单独写。

## 2. 表驱动的三个部件

| 部件 | 职责 | 出错时给什么 |
| --- | --- | --- |
| 数据（YAML） | id / 标题 / 动作 / 参数 / 期望 | 哪条用例、哪个字段缺 |
| 执行器（runner） | 按 action 分派，收集结果 | 哪条用例、哪一步、什么异常 |
| 报告 | total / passed / failed + 明细 | 失败的完整信息 |

关键设计：**执行器不认识业务，只认识 action 名**。加一条用例不需要改 Python，加一种新动作才需要。

```python
HANDLERS = {"login": do_login, "add_todo": do_add_todo, "search": do_search, "guard": do_guard}

def run_case(page, base_url, case):
    try:
        detail = HANDLERS[case["action"]](page, base_url, case["params"], case["expect"])
        return Result(case["id"], case["title"], True, detail)
    except Exception as exc:
        return Result(case["id"], case["title"], False, f"{type(exc).__name__}: {exc}")
```

`except Exception` 在这里是正确的：一条用例炸了不能中断整批，但必须把异常**收进结果**，不能吞掉。

## 3. 失败要能定位

三条硬要求：

1. **id 唯一且短**：`login-bad-password` 比 `test_3` 有用；
2. **失败不中断**：一条挂了继续跑，最后汇总；
3. **详情带类型**：`TimeoutError: Locator.click: Timeout 30000ms exceeded` 比 `失败` 有用。

## 4. 本章实操

`labs/ch20-data-driven/`：

| 文件 | 作用 |
| --- | --- |
| `cases.yaml` | 8 条：登录成功/失败、加待办、搜索命中/未命中、表格选中、看资料、未登录拦截 |
| `runner.py` | `load_cases`（校验 list + id 唯一）、`HANDLERS`、`run_case`、`run_all`、`summary` |
| `test_data_driven.py` | 13 条：8 条参数化 + schema 校验 + 未知 action + 失败捕获 + 批量不中断 + 汇总数字 |

跑法：

```powershell
.\.venv\Scripts\python.exe -m pytest labs/ch20-data-driven -q
```

**踩坑**：`open_anonymous` 在同一个 page 上跑时，前面用例已经登录过，不会被拦截。修法是处理器里先 `page.context.clear_cookies()` 再 `goto`——这也说明「未登录」是一个需要主动构造的状态，不是默认状态。

## 5. YAML 写用例的边界

| 适合 | 不适合 |
| --- | --- |
| 单动作 + 参数 + 期望 | 多步流程（改写 Python） |
| 同一动作的边界值批量 | 需要造数据的场景（工厂函数） |
| 冒烟与回归的分级（`smoke: true`） | 依赖上一条用例结果的链路 |

## 6. 自测

1. 为什么 `run_case` 要 `except Exception` 而不是让它冒出去？
2. 参数化时 `id` 重复会怎样？
3. 什么情况下不该用 YAML 驱动？
4. `summary` 里除了 total/passed/failed，还该有什么？

## 附：自测答案

1. 因为要「跑完整批再汇总」。异常冒出去会让后面的用例全被跳过，CI 只看到第一条失败，实际可能有五条要修。收进结果不等于吞掉——详情要写进报告。
2. `load_cases` 会直接报错（本章实现里校验了唯一性）。不校验的话，报告里两条同名结果，定位时不知道是哪条挂的。
3. 多步业务流、需要构造前置数据、断言依赖上一步返回值。这些放 YAML 会变成「用字符串描述逻辑」，比直接写 Python 更难维护。
4. 耗时分部（哪条最慢）与环境信息（base_url）。只看通过率看不出「这批变慢了 3 倍」，也可能把 staging 的失败当成 local 的问题。

## 学生常问

**Q：用例写在 YAML 里，IDE 没有补全，写错了要到跑的时候才知道？**

A：所以要 `load_cases` 做 schema 校验（字段、action 白名单、id 唯一），并在测试里单独校验一遍。更好的做法是给 YAML 写 JSON Schema，编辑器里就能提示。

**Q：参数化会不会让报告变得很难读？**

A：会，如果 id 起得随意。约定 `动作-场景` 命名（`login-bad-password`），报告按 id 排序后天然分组。另外失败详情要带输入值，否则「哪组参数挂了」还得回去翻 YAML。

**Q：一条 YAML 用例要不要支持「多步」？**

A：可以支持，但要限制步数（比如 ≤5）并禁止条件分支。一旦出现 `if`，就说明它该写成 Python 用例了。

## 面试题

**Q：你们的数据驱动是怎么做的？**

A：三层：数据层（YAML/CSV 存输入与期望）、执行层（action → handler 分派，异常收进结果）、报告层（汇总 + 明细）。新增用例只加数据，新增动作类型才改代码。

**Q：参数化和「用例复用」有什么区别？**

A：参数化是同一逻辑换输入；复用是把公共步骤抽成函数/夹具。两者解决不同问题：前者扩覆盖面，后者降重复。混着谈会出现「为了复用把三条不同流程塞进一个函数」。

**Q：批量跑时一条用例挂起（不是失败，是卡住）怎么办？**

A：给每个动作设显式超时（Playwright 默认 30 秒），并在执行器里加整批超时。卡住通常是等待条件写错（等一个永远不出现的元素），超时能把「卡住」变成「失败 + 明确位置」。

**Q：失败用例要不要自动重跑？**

A：只对「环境抖动」类重跑（网络、第三方）。断言失败重跑会把真实 bug 掩盖成「偶发」。重跑要在报告里标记，否则通过率会虚高。

## 延伸知识

- **`pytest.mark.parametrize` 的 `ids`**：不给 ids，报告里是 `test_case[case0]`；给了 ids 是 `test_case[login-bad-password]`，排查快一个数量级。
- **CSV 与 YAML 的分工**：CSV 适合「一张表几百行」的批量数据，YAML 适合「十几条结构化用例」。
- **用例分级**：加 `smoke: true` 字段，CI 只跑冒烟，回归放夜间——比维护两份用例列表可靠。
- **失败快照**：批量跑时给每个失败用例存一张截图 + 当前 URL，报告里带上路径，复现成本会低很多。
