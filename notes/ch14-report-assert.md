# 第 14 章 · 报告与智能断言

用例跑完只有一行 `23 passed`，对团队没用。这一章解决两件事：**结果怎么给人看**，**断言怎么既严格又不脆**。

## 1. 报告的三层

| 层 | 给谁看 | 内容 |
| --- | --- | --- |
| 终端摘要 | 写代码的人 | `-q` 的点和 F，`--tb=short` 的栈 |
| JUnit XML | CI / 平台 | 机器可读的用例、耗时、失败原因 |
| HTML | 团队 / 汇报 | 通过率、耗时分布、失败详情、环境信息 |

pytest 自带前两层（`--junitxml=report.xml`），HTML 用插件或自己渲染。本章用 stdlib 写一个 40 行的渲染器，不引依赖也能出报告。

## 2. JUnit XML 里有什么

```xml
<testsuite name="pytest" tests="23" failures="1" errors="0" time="0.57">
  <testcase classname="labs.ch12.test_users" name="test_crud_roundtrip" time="0.05">
    <failure message="期望 200，实际 422">...栈...</failure>
  </testcase>
</testsuite>
```

渲染时最该突出的是 **`failures` 与 `time`**，不是用例总数。

## 3. 断言为什么会脆

| 脆的写法 | 为什么脆 | 改法 |
| --- | --- | --- |
| `assert body == {...}` 全等 | 服务端加字段就挂 | 断言子集 |
| `assert ts == "2026-11-16"` | 日期一变就挂 | 断言格式/范围 |
| `assert id == 1` | 依赖自增 | 断言 `isinstance(int) and > 0` |
| `assert "成功" in text` | 文案改字就挂 | 断言 code 枚举 |
| 只断 200 | 业务错误也 200 | 断状态 + 关键字段 |

一句话：**断言契约，不断言实现**。

## 4. 断言工具箱

```python
def assert_subset(actual, expected, path=""): ...      # 只要求包含这些键
def assert_schema(obj, schema): ...                    # 类型与必填
def assert_iso8601(value): ...                         # 时间格式而非具体值
def assert_in_range(value, low, high): ...            # 数值范围
def soft_assert(collector, cond, msg): ...             # 收集多条失败，一次报完
```

`soft_assert` 的价值：一个响应体有 5 个字段要验，硬断言只能看到第一个失败，软断言能一次列全。

## 5. 「智能断言」到底是什么

不是让模型随口说「看起来对」，而是三步：

1. **规则先生成候选**：从响应体里抽出字段、类型、枚举，生成「可判定」的断言草稿；
2. **人审**：把 `status: paid` 这类业务语义补进断言，去掉 `elapsed < 3ms` 这种环境相关的；
3. **回归固化**：审过的断言写回测试文件，之后不再让模型介入。

模型擅长的是「从一份响应里看出该断言哪些字段」，不擅长「知道这个业务的正确值」。

## 6. 本章实验

`labs/ch14-report-assert/`：

- `assertkit.py`：`assert_subset` / `assert_schema` / `assert_iso8601` / `assert_in_range` / `SoftAssert` / `suggest_assertions`（从响应体推断言草稿）；
- `report.py`：读 JUnit XML → 生成自包含 HTML（通过率环、失败列表、慢用例 Top 5）；
- `test_assertkit.py`：断言工具箱自身的测试（用坏数据证明它会报错）。

```powershell
.venv\Scripts\python.exe -m pytest labs --junitxml=report.xml -q
.venv\Scripts\python.exe labs\ch14-report-assert\report.py report.xml report.html
```

## 7. 自测

1. 为什么「全等断言」在接口测试里几乎总是错的？
2. `soft_assert` 适合什么场景？什么时候反而该用硬断言立即中断？
3. JUnit XML 里哪两个字段最能反映质量趋势？
4. 「智能断言」的三步里，哪一步不能交给模型？
5. 一个 `elapsed_ms < 50` 的断言，为什么在 CI 上会随机失败？
