# 第 13 章 · 业务链路与数据准备

单接口测的是「这个口对不对」，链路测的是「这条业务能不能走通」。这一章解决三件事：怎么串、数据哪来、跑完怎么收。

## 1. 链路用例的骨架

```
登录 → 建单 → 支付 → 查订单 → 断言状态与金额 → 清理
```

写成代码就是一个函数，**不要拆成四条互相依赖的用例**：

```python
def test_order_flow(client):
    token = login(client)
    order = create_order(client, token)
    pay(client, order["id"], token)
    got = get_order(client, order["id"], token)
    assert got["status"] == "paid"
```

拆成四条会让「支付失败」时前三条都绿，第四条才红，定位反而变慢。

## 2. 数据从哪来

三种来源，优先级从高到低：

| 来源 | 适用 | 风险 |
| --- | --- | --- |
| 接口自己造（推荐） | 大部分场景 | 造数接口本身可能有 bug |
| 数据库直插 | 造数接口缺失、需要脏数据 | 绕过业务校验，数据可能不合法 |
| 固定夹具数据 | 只读查询、字典表 | 多轮跑会互相污染 |

造数要带**唯一标识**，否则第二轮就撞 409：

```python
def unique_phone(seed: int) -> str:
    return f"13{seed:09d}"[-11:]
```

## 3. 清理必须自动

```python
@pytest.fixture
def order(client, token):
    created = create_order(client, token)
    yield created
    try:
        client.delete(f"/api/orders/{created['id']}")
    except ApiError:
        pass          # 已删除 / 不可删都算正常
```

三条规矩：

1. **不要放用例末尾**，用例一失败就漏；
2. **清理失败不要盖住原错误**，`except` 吞掉即可；
3. **造的数据带前缀**（如 `qa_`），方便定期批量清理。

## 4. 幂等与重试

链路里最贵的 bug 是「重复提交」。接口有 `Idempotency-Key` 时，用例要同时验两件事：

```python
first = post("/api/orders", json=payload, headers={"Idempotency-Key": "k1"})
second = post("/api/orders", json=payload, headers={"Idempotency-Key": "k1"})
assert first["id"] == second["id"]     # 同单
assert second.status_code == 200       # 第二次不是 201
```

没有幂等键的系统，客户端要自己保证：重试只对 GET/PUT/DELETE。

## 5. 并发不是「多跑几次」

真正要验的是「同时到达」：

```python
with ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(lambda _: pay(order_id), range(2)))
statuses = sorted(r.status_code for r in results)
assert statuses == [200, 409]
```

断言的是**状态组合**，不是「谁赢」。否则用例会随机红。

## 6. 本章实验

`labs/ch13-flows/`：

- `factories.py`：`unique_name`/`unique_phone`/`make_user`/`make_order`；
- `test_flow.py`：下单支付全链路、幂等键、重复支付冲突、并发支付、404 兜底；
- `conftest.py`：`token`/`client`/`created_orders`（自动清理）。

```powershell
.venv\Scripts\python.exe -m pytest labs\ch13-flows -q
```

## 7. 自测

1. 为什么链路用例不该拆成四条依赖用例？
2. 造数接口本身有 bug 时，怎么保证用例不背锅？
3. 清理为什么放在 fixture 的 `yield` 之后，而不是用例最后一行？
4. 幂等键重复提交，第二次应该返回 200 还是 201？为什么？
5. 并发用例断言「状态组合」而不是「谁赢」，好处是什么？
