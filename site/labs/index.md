# 实操记录

每条实操都是一个能直接运行的 `.py`（第二阶段起需要 `requests`），配一份 pytest。克隆下来就能跑。

> 想不装环境先看效果？打开 [在线运行 playground](/labs/playground)，代码直接在浏览器里跑。

## 第一阶段 · Python 与工程基础

| 章 | 实操目录 | 源文件 | 覆盖的知识点 | 测试 |
| --- | --- | --- | --- | --- |
| 01 | `labs/ch01-basics` | `basics.py` | 类型转换、`is` vs `==`、f-string、运算符优先级 | 10 |
| 02 | `labs/ch02-control-flow` | `flow.py` | 条件边界、循环、`for...else`、双层跳出、retry | 10 |
| 03 | `labs/ch03-collections` | `collections_demo.py` | 去重保序、词频、字典反转、嵌套聚合、切片浅拷贝 | 12 |
| 04 | `labs/ch04-functions` | `functions_demo.py` | 可变默认参数、`*args/**kwargs`、闭包、递归、深浅拷贝 | 13 |
| 05 | `labs/ch05-oop` | `oop_demo.py` | 类/实例属性、三种方法、`@property`、魔术方法、装饰器 | 12 |
| 06 | `labs/ch06-stdlib` | `stdlib_demo.py` | UTF-8 读写、JSON、CSV、唯一文件名、异常链 | 14 |
| 07 | `labs/ch07-testkit` | `testkit/`（3 个模块） | 校验器、数据生成（可复现 seed）、落盘夹具 | 20 |

## 第二阶段 · 接口自动化

| 章 | 实操目录 | 源文件 | 覆盖的知识点 | 测试 |
| --- | --- | --- | --- | --- |
| 08 | `labs/ch08-http-basics` | `explore_api.py` + `_shared/mini_api.py` | 契约七要素、状态码分组、鉴权、幂等、multipart | 15 |
| 09 | `labs/ch09-ai-cases` | `spec.py` / `matrix.py` / `prompt.py` | 7 维覆盖矩阵、提示词结构、生成后五道审 | 10 |
| 10 | `labs/ch10-requests` | `session_demo.py` | Session 复用、超时元组、选择性重试、流式下载 | 11 |
| 11 | `labs/ch11-httpclient` | `http_client.py` + `api.py` | 四层分层、统一异常、日志脱敏、transport 注入 | 10 |
| 12 | `labs/ch12-pytest-org` | `conftest.py` + 4 个测试文件 | 夹具四层、参数化、标记、断言消息 | 23 |
| 13 | `labs/ch13-flows` | `factories.py` + `test_order_flows.py` | 全链路、造数唯一性、自动清理、幂等、并发 | 6 |
| 14 | `labs/ch14-report-assert` | `assertkit.py` + `report.py` | 契约断言、软断言、JUnit→HTML、断言草稿 | 11 |
| 15 | `labs/ch15-framework` | `fw_config/fw_client/fw_api/run.py` | 多环境配置、上传下载、CSV 批量、CLI 入口 | 7 |

## 第三阶段 · Web 自动化

| 章 | 实操目录 | 源文件 | 覆盖的知识点 | 测试 |
| --- | --- | --- | --- | --- |
| 16 | `labs/ch16-web-basics` | `demo_basics.py` + `_shared/mini_site.py` | 浏览器/上下文/页面三层、四种定位、自动等待、expect 断言、截图留证 | 12 |
| 17 | `labs/ch17-po` | `po_pages.py` | 页面对象、动作返回下一页、断言进页面类 | 7 |
| 18 | `labs/ch18-locators` | `registry.py` + `locators.yaml` | 定位集中管理、按 key 取元素、换 YAML 不换代码 | 7 |
| 19 | `labs/ch19-fixtures` | `conftest.py` | 一次登录复用、storage_state 落盘、匿名上下文隔离 | 7 |
| 20 | `labs/ch20-data-driven` | `runner.py` + `cases.yaml` | 用例外部化、动作分发、失败不中断、汇总 | 13 |
| 21 | `labs/ch21-visual` | `visual.py` + `a11y.py` | 截图像素比对、容差、五类可访问性问题审计 | 9 |
| 22 | `labs/ch22-ai-cases` | `snapshot/llm/validate/execute` | 快照喂模型、输出校验、真跑生成的步骤 | 10 |
| 23 | `labs/ch23-framework` | `fw_*.py` + `run.py` | 配置驱动、CLI、Markdown 与 JUnit 双报告 | 10 |

## 第五阶段 · 性能测试

| 章 | 实操目录 | 源文件 | 覆盖的知识点 | 测试 |
| --- | --- | --- | --- | --- |
| 32 | labs/ch32-perf-basics | metrics_demo.py | 分位值、TPS、错误率、Little's Law | 11 |

合计 **356 条测试**（15 条真机用例需连接安卓设备）。

## 怎么跑

```powershell
# 全部
.venv\Scripts\python.exe -m pytest labs -q

# 单章
.venv\Scripts\python.exe -m pytest labs\ch12-pytest-org -q

# 只跑冒烟
.venv\Scripts\python.exe -m pytest labs -q -m smoke

# 单章直接看输出
.venv\Scripts\python.exe labs\ch08-http-basics\explore_api.py

# 框架入口（跑用例 + 出 HTML 报告）
.venv\Scripts\python.exe labs\ch15-framework\run.py --env local --report
```

## 每个实验长什么样

以第 5 章为例，`oop_demo.py` 里是「一个知识点一个小函数 + 一段 `__main__` 演示」：

```python
class Counter:
    total = 0                 # 类属性：所有实例共享

    def __init__(self, name="c"):
        self.name = name
        self.count = 0        # 实例属性：每个实例独立
        Counter.total += 1
```

`test_oop_demo.py` 里每个行为一条断言，失败信息能直接定位到「哪个知识点没掌握」。

第二阶段的实验都跑在同一个内存态被测服务上（`labs/_shared/mini_api.py`，纯标准库，`serve()` 起在随机端口），所以不需要你自己搭后台。

## 约定

- 第一阶段只依赖标准库；第二阶段只多一个 `requests`。
- 需要密钥的实验从环境变量读，缺省走 mock。
- 输出目录（`_out/`、`data/`、`report.xml`/`report.html`）不入库。
- 每个 `def` 都能单独被测试调用，不在模块顶层做副作用。
