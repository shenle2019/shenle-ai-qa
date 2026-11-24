"""应用 ch01–ch15 审校报告里的 ERROR 与较硬的 UNCERTAIN（逐行断言，改不到就报错）。"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (相对路径, 行号, 该行必须包含的片段, 新行；None 表示删除该行)
FIXES = [
    ("notes/ch01-basics.md", 98, "等价 `x = x + 1`",
     "| 赋值 | `= += -= *= /= %=` | 对数字/字符串，`x += 1` 等价 `x = x + 1`；对列表，`lst += [1]` 是就地扩展，`lst = lst + [1]` 才新建 |"),
    ("notes/ch01-basics.md", 168, "可变对象不能当字典键",
     "A：`list`、`dict`、`set` 可变；`int`、`str`、`tuple`、`frozenset` 不可变。影响有三处：**不可哈希**的对象不能当字典键（`list`/`dict`/`set` 不行，含这些元素的 `tuple` 也不行；反过来，自己实现了 `__hash__` 的可变类可以当键）；函数默认参数写成 `[]` 会被所有调用共享；多线程共享可变对象要加锁。"),
    ("notes/ch02-control-flow.md", 129, "continue 只是跳过", None),
    ("notes/ch04-functions.md", 176, "box = box or {}",
     "1. 第二次调用时 `box` 里有两个元素——默认参数只在函数定义时求值一次，`{}` 被所有调用共享。默认值写 `None`，函数体里用 `if box is None: box = {}` 判空再累加；写成 `box = box or {}` 会把「显式传进来的空 dict」也换成新对象，跟本节的正解不一致。"),
    ("notes/ch06-stdlib.md", 54, "Windows 默认是 gbk",
     "- **永远显式写 `encoding=\"utf-8\"`**：`open()` 不写时用系统 locale（中文 Windows 是 GBK/cp936，英文 Windows 是 cp1252），中文内容很容易乱码或直接报错；"),
    ("notes/ch07-testkit.md", 47, "正则用 `^...$` 锚定",
     "- 判断「整串都是手机号」用 `re.fullmatch`：`match` 只锚开头；`^...$` 里的 `$` 自己又会放过末尾一个换行（`\"13800138000\\n\"` 能过），只有 `re.fullmatch` 或 `\\Z` 才是真的整串。"),
    ("notes/ch07-testkit.md", 65, "跑一万条也会撞",
     "- **唯一**：手机号空间是 9×10^9，一万条随机样本按生日问题约 5% 的概率会撞（量再大必撞）；真实项目里用 `uuid` 派生或加自增序列，本工具箱用「已用集合 + 重试」保证同实例内不重复；"),
    ("notes/ch07-testkit.md", 130, "加 `$`（或直接用 `re.fullmatch`）",
     "1. `re.match` 只要求「从开头匹配」，不锚定结尾：`\"1380000000abc\"` 也会通过。用 `re.fullmatch`（或 `\\Z`）才能保证整串都是手机号；`$` 不够——它会放过末尾一个换行。"),
    ("notes/ch08-http-basics.md", 160, "断言第二次返回 200（不是 201）",
     "A：同一个幂等键连续提交两次，断言第二次响应与首次一致（同 id、同 body；状态码按你的契约——重放首次响应的实现第二次仍是 201，返回 200 的实现是另一种约定）、且数据库只有一条记录。没有幂等键的接口，测「重复提交会被拒绝（409）」。"),
    ("notes/ch09-ai-cases.md", 101, "不可判定的（「功能正常」",
     "3. 这条约束筛掉三类：只写「功能正常 / 返回正确」没有可观测结果的、只断状态码不写字段与值的、多个期望混成一句没法判成败的。"),
    ("notes/ch14-report-assert.md", 86, "`tests` 和 `failures`",
     "3. `failures`（含 `errors`）与 `time`：看失败率变化和耗时漂移；`tests` 只说明规模，单看通过数没意义。"),
    ("notes/ch14-report-assert.md", 87, "第三步「下结论 / 归因」不能交给模型",
     "4. 第二步「人审」不能交给模型——模型只能基于证据给候选原因，补业务语义、剔除受环境影响的断言必须人来做，否则会把「断言写错」误判成「服务端 bug」。"),
    ("notes/ch14-report-assert.md", 112, "模型只做前两步的加速",
     "A：三步：采集失败上下文（请求、响应、断言、历史同类结果）→ 与契约比对找出差异（字段缺失、类型变化、值越界）→ 给出候选归因与修复建议。模型负责第 1、2 步的加速和候选归因，结论由人下，固化成回归用例也要人确认。"),
    ("notes/ch15-framework.md", 54, "Excel 默认 GBK",
     "- **编码**：中文 Windows 上 Excel 另存的 CSV 常是 GBK，读时用 `encoding=\"gbk\"`；只有「CSV UTF-8」导出才带 BOM，那才用 `utf-8-sig` 去 BOM；"),
    ("notes/ch13-flows.md", 38, '[-11:]', '    return "13" + f"{seed % 10**9:09d}"'),
    ("labs/ch13-flows/factories.py", 19, '[-11:]', '    return "13" + f"{n % 10**9:09d}"'),
]


def apply() -> None:
    touched: dict[Path, int] = {}
    for rel, lineno, expect, new in FIXES:
        path = ROOT / rel
        lines = path.read_text(encoding="utf-8").splitlines()
        got = lines[lineno - 1]
        assert expect in got, f"{rel}:{lineno} 不含 {expect!r}，实际 {got!r}"
        if new is None:
            del lines[lineno - 1]
        else:
            lines[lineno - 1] = new
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        touched[path] = touched.get(path, 0) + 1
    for path, n in touched.items():
        print(f"ok {path.relative_to(ROOT)} x{n}")


VALIDATORS = ROOT / "labs/ch07-testkit/testkit/validators.py"


def fix_validators() -> None:
    text = VALIDATORS.read_text(encoding="utf-8")
    pairs = [
        (r'r"^1[3-9]\d{9}$"', r'r"1[3-9]\d{9}"'),
        (r'r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$"', r'r"[\w.+-]+@[\w-]+(\.[\w-]+)+"'),
        (r'r"^\d{17}[\dXx]$"', r'r"\d{17}[\dXx]"'),
        (r'r"^\d+(\.\d{1,2})?$"', r'r"\d+(\.\d{1,2})?"'),
    ]
    for old, new in pairs:
        assert old in text, old
        text = text.replace(old, new)
    n = text.count(".match(")
    text = text.replace(".match(", ".fullmatch(")
    VALIDATORS.write_text(text, encoding="utf-8")
    print(f"ok {VALIDATORS.relative_to(ROOT)} anchors removed, {n} match->fullmatch")
    leftover = [l for l in text.splitlines() if re.search(r'[$^]\$|r"\^', l)]
    print("leftover anchors:", leftover)


if __name__ == "__main__":
    apply()
    fix_validators()
