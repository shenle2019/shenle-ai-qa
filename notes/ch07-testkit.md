# 第 7 章 · 实战：测试数据工具箱

> 本章目标：把前六章的东西拼成一个真能用的包——生成不重复的测试数据、校验格式、落成文件给用例读。
> 代码在 `labs/ch07-testkit/`，测试在 `labs/ch07-testkit/tests/`。

## 1. 为什么需要它

接口和 UI 用例最烦的三件事：

1. **数据重复**：手机号、邮箱写死，第二次跑就撞唯一索引；
2. **格式不合法**：随机拼的字符串过不了前端校验，用例失败原因却是「数据不对」；
3. **数据不可复用**：同一个订单要在接口用例、UI 用例、报告里各写一遍。

一个 100 行的工具箱就能解决：**生成（唯一 + 合法）→ 校验 → 落盘 → 复读**。

## 2. 结构

```text
labs/ch07-testkit/
├── testkit/
│   ├── validators.py    # is_phone / is_email / is_id_card / is_money / require
│   ├── datagen.py       # DataGen、unique_phone / unique_email / unique_order_no
│   └── fixtures.py      # dump_json / dump_csv / write_text / load_json
├── tests/test_testkit.py
├── demo.py              # 生成 → 校验 → 落盘 → 复读，一条命令跑完
└── conftest.py          # 让 pytest 从仓库根也能 import testkit
```

## 3. 校验：先判断，再抛错

```python
PHONE_RE = re.compile(r"^1[3-9]\d{9}$")

def is_phone(value) -> bool:
    return isinstance(value, str) and bool(PHONE_RE.match(value))

def require(field, value, check):
    if not check(value):
        raise ValidationError(field, value, "格式不符合要求")
    return value
```

设计取舍：

- `is_*` 只返回布尔，不打日志不抛异常 —— 方便在推导式、断言里用；
- 需要报错时用 `require`，异常里带 `field`，接口用例可以直接断言「哪个字段错了」；
- 正则用 `^...$` 锚定，`match` 只锚开头，不锚结尾会放进 `138001380001`。

## 4. 生成：唯一性靠 uuid，可复现靠种子

```python
def unique_phone(rng=None) -> str:
    rng = rng or random.Random()
    return f"1{rng.choice('3456789')}{_digits(9, rng)}"
```

```python
@dataclass
class DataGen:
    seed: int = 20261116
```

两个关键点：

- **唯一**：手机号只用 11 位随机数，跑一万条也会撞；真实项目里用 `uuid` 派生或加自增序列，本工具箱用「已用集合 + 重试」保证同实例内不重复；
- **可复现**：同一个 `seed` 生成同一批数据。失败用例能原地重放，不用截图存 Excel。

`orders()` 先生成结构化数据，再落盘：

```python
{"order_no": "SO20261116A1B2C3", "customer": "李静", "phone": "139...", "amount": 128.5, ...}
```

## 5. 落盘：json 与 csv 的分工

| 格式 | 适合 | 注意 |
| --- | --- | --- |
| JSON | 嵌套结构、接口请求体、给代码读 | `ensure_ascii=False`、日期用 `default=` |
| CSV | 给人看、给 Excel、参数化用例 | `utf-8-sig` 防乱码、`newline=""` 防空行 |

```python
dump_json("data/orders.json", orders)
dump_csv("data/orders.csv", orders)
```

`fixtures.dump_json` 里加了 `default=`，`date`/`datetime` 自动转 ISO 字符串 —— 否则 `TypeError: Object of type date is not JSON serializable`。

## 6. 在用例里怎么用

```python
def test_create_order(tmp_path):
    gen = DataGen(seed=1)
    payload = gen.order("SKU-9", qty=2)

    assert is_phone(payload["phone"])
    assert is_money(f"{payload['amount']:.2f}")

    path = dump_json(tmp_path / "order.json", payload)
    body = load_json(path)          # 当成「接口返回」来断言
    assert body["sku"] == "SKU-9"
```

真实项目里把 `tmp_path` 换成 `data/fixtures/`，一次生成、多个用例共享，跑完不删——出问题能直接翻文件。

## 7. 一条命令验证

```powershell
python labs/ch07-testkit/demo.py
python -m pytest labs/ch07-testkit -q
```

`demo.py` 做四件事并自检：生成 5 条订单 → 校验手机号/邮箱 → 写 json 与 csv → 读回求和。

## 8. 还能往哪长

- **参数化**：把 `orders()` 的结果喂给 `@pytest.mark.parametrize`，一个用例覆盖 5 组数据；
- **落库**：`fixtures` 再加一个 `dump_sqlite()`，测试前灌数据、测试后清表；
- **清理**：加 `cleanup(path)` 或直接用 `tmp_path`，别把脏数据留在仓库里；
- **契约校验**：用 `jsonschema` 校验「接口返回结构」，比逐字段断言更省事。

## 9. 自测

1. 为什么 `is_phone` 用 `re.match` 还要写 `$`？
2. `DataGen(seed=1)` 两次生成的手机号一样吗？为什么？
3. `dump_csv` 为什么要用 `utf-8-sig`？
4. 想让 5 条数据驱动同一个用例，改哪一处最少？

## 附：自测答案

1. `re.match` 只要求「从开头匹配」，不锚定结尾：`"1380000000abc"` 也会通过。加 `$`（或直接用 `re.fullmatch`）才能保证整串都是手机号。
2. 一样。`random.Random(seed)` 是确定性伪随机：同一个种子、同一台机器、同一个 Python 版本，序列完全相同。要每次不同就别固定 seed，或用时间戳做种子。
3. Excel 打开 UTF-8 文件时若没有 BOM，会把中文当本地编码解释成乱码；`utf-8-sig` 会写入 BOM，Excel 才认。
4. 只改一处：把数据抽成一个列表，用例上加 `@pytest.mark.parametrize("case", CASES)`，用例体不动。

## 学生常问

**Q：造数为什么要「唯一」，直接写死 alice 不行吗？**

A：写死的数据会被上一次运行留下，第二次跑就撞 409 或读到脏数据。唯一化的目的不是好看，是让用例可重复执行——同一个用例连跑十次结果一致。

**Q：正则写不出来怎么办？**

A：别硬憋。先把「必须匹配」和「必须不匹配」各写三个样例，再挑最简单的表达式；能用 `str` 方法（`startswith`、`isdigit`）就别上正则，正则只留给形态固定又复杂的字段。

**Q：测试数据要不要入库管理？**

A：少量固定数据放代码里的常量或 CSV；大量组合数据用生成器现造；需要跨用例共享的才放夹具。把几百条数据塞进仓库，最后没人敢改。

## 面试题

**Q：测试数据设计要考虑哪些维度？**

A：有效等价类、无效等价类、边界值、特殊字符与超长、类型错配、业务状态（未支付/已支付/已取消）、权限维度、并发与重复提交。造数时还要考虑「唯一性」和「可清理」。

**Q：断言写太严和太松，各自的风险？**

A：太严（全等、写死时间戳和自增 id）会在环境变化时大面积误报，团队开始无视红灯；太松（只断言 200）会漏掉业务错误，接口返回错误码也算通过。正确做法是断言契约里稳定的字段，加上业务语义。

**Q：为什么测试代码也要评审？**

A：测试代码的 bug 会让你「以为测过了」。评审关注：断言是否可判定、是否依赖执行顺序、数据是否可重复、失败信息是否足够定位。

## 延伸知识

- 金额用整数分或 `Decimal`，别用 `float` 比较；`Decimal("0.1") + Decimal("0.2") == Decimal("0.3")` 才成立。
- 手机号、身份证这类有校验位的字段，生成时按规则算校验位，别用随机数字糊弄，否则第一轮就被服务端拒。
- 数据工厂用固定 `seed` 便于复现问题，用随机 `seed` 便于发现边界，两套都留着。
- 清理数据和造数据要成对出现，`yield` 之后统一清理，别指望用例自己收尾。
