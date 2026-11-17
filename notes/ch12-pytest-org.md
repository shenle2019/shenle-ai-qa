# 第 12 章 · 用 pytest 组织接口用例

单条用例写对不难，难的是**一百条用例还能一起跑、失败时一眼看懂**。这一章解决组织问题。

## 1. 目录就是架构

```
labs/ch12-pytest-org/
├── conftest.py          全局夹具：起 SUT、建会话、发 token
├── api_client.py        极简 client（第 11 章的缩水版）
├── data.py              用例数据（参数化表）
├── test_users_crud.py   增删改查主流程
├── test_auth.py         鉴权与权限
└── test_orders.py       订单状态机
```

一个文件一类关注点。判断标准：**改订单逻辑时，只会打开 `test_orders.py`。**

## 2. 夹具分四层，作用域从大到小

| 夹具 | 作用域 | 干什么 |
| --- | --- | --- |
| `sut` | session | 起一次被测服务，全轮复用 |
| `client` | session | 建连接池、统一超时 |
| `token` | session | 登录一次，全轮共用 |
| `users` | function | 每条用例一份干净数据 |

```python
@pytest.fixture(scope="session")
def sut():
    with serve() as base:
        yield base

@pytest.fixture(scope="session")
def client(sut):
    return HttpClient(sut, timeout=5)

@pytest.fixture(scope="session")
def token(client):
    return client.post("/api/login", json={"username": "alice", "password": "secret"}).json()["token"]

@pytest.fixture
def auth(client, token):
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
    client.headers.pop("Authorization", None)
```

`yield` 之后是清理：**清理必须放在 fixture 里**，不要写在用例末尾，否则用例失败就漏清理。

## 3. 参数化：一张表测一组边界

```python
@pytest.mark.parametrize(
    "size, expected",
    [(1, 200), (100, 200), (101, 422), (0, 422), (-1, 422)],
    ids=["min", "max", "over", "zero", "negative"],
)
def test_page_size_bounds(auth, size, expected):
    ...
```

`ids` 一定要写：失败时报告里显示 `test_page_size_bounds[over]`，比 `[2]` 有用得多。

## 4. 标记：让「想跑哪些」变成参数

```python
@pytest.mark.smoke
@pytest.mark.parametrize(...)
def test_list_users(...): ...

@pytest.mark.skipif(not HAS_UPLOAD, reason="环境不支持上传")
def test_upload(...): ...
```

`pytest.ini` 里注册标记，避免 `PytestUnknownMarkWarning`：

```ini
[pytest]
markers =
    smoke: 冒烟用例
    slow: 慢用例（>2s）
```

跑法：`pytest -m smoke`、`pytest -m "not slow"`。

## 5. 断言要给人看，不是给机器看

```python
# 差
assert resp.status_code == 200 and resp.json()["items"]

# 好
assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text[:200]}"
data = resp.json()
assert isinstance(data["items"], list)
assert len(data["items"]) <= 10, f"分页失效，返回 {len(data['items'])} 条"
```

三条经验：

1. **每个 assert 只断言一件事**，失败信息才准确。
2. **先断言状态码再解析 JSON**，否则 500 会让 `json()` 抛解析错，掩盖真因。
3. **把响应体截断后带进消息**，CI 里不用重新跑就能定位。

## 6. 顺序与隔离

pytest 默认按文件名字母序跑，**不要依赖顺序**。需要「先建后查」的，就在一条用例里走完；需要跨用例共享的数据，用 fixture 造。

```python
def test_create_then_get(auth):
    created = auth.post("/api/users", json={"name": "ivy"}).json()
    got = auth.get(f"/api/users/{created['id']}").json()
    assert got["name"] == "ivy"
```

## 7. 本章实操

`labs/ch12-pytest-org/`：四个测试文件，覆盖 CRUD、鉴权、参数化边界、状态机，共 23 条。

```powershell
.venv\Scripts\python.exe -m pytest labs\ch12-pytest-org -q
.venv\Scripts\python.exe -m pytest labs\ch12-pytest-org -q -m smoke
```

## 8. 自测

1. `scope="session"` 的夹具里能放可变状态吗？为什么？
2. 参数化的 `ids` 不写会怎样？
3. 为什么「先断言状态码，再解析 JSON」？
4. 两条用例都要「一个已存在的用户」，应该用 fixture 还是复制代码？
5. 加了 `-m smoke` 之后发现有依赖顺序的用例挂了，怎么定位？

## 附：自测答案

1. 能放，但只能是只读或幂等的状态（连接、配置、只读 token）。可变共享状态会在用例之间串味：前一条改了数据，后一条就时绿时红，最后变成「必须按顺序跑」。
2. 报告里显示的是参数元组的字符串表示，失败时看不出是哪组数据；写了 `ids` 才能一眼看出「是 size=101 这条挂了」。
3. 状态码不对时响应体很可能不是 JSON（HTML 错误页、空 body），先 `resp.json()` 会抛 `JSONDecodeError`，把真正的原因（比如 502）盖掉。
4. 用 fixture（最好是工厂 fixture），返回一个新用户。复制代码会导致两处数据不一致，改一处漏一处；fixture 还能统一做清理。
5. 先单独跑挂掉的那条（`pytest path::test_name`），它能过就说明依赖了别的用例造的数据；把那份数据改成 fixture 或显式造数，顺序依赖就消失了。

## 学生常问

**Q：`conftest.py` 要放几层？**

A：按作用域放：仓库根放全局的（SUT 启动、配置）；`labs/chXX/` 放本章共享的（client、token）；具体目录放只服务那几条用例的。就近原则，别把所有东西堆在根上。

**Q：fixture 之间能互相依赖吗？**

A：能，而且推荐。`client` 依赖 `sut`，`token` 依赖 `client`，`auth` 依赖 `token`——依赖关系写在签名里，pytest 自动按顺序建、按反序销毁。

**Q：参数化和循环有什么区别？**

A：参数化每条数据是独立用例，失败互不影响、报告分开统计；循环是一条用例，第一条失败后面就不跑了，报告里也看不出是哪组数据。

## 面试题

**Q：pytest 的夹具作用域有哪几种，怎么选？**

A：`function`（默认，每用例一次）、`class`、`module`、`package`、`session`。建连、启动服务用 `session`；需要干净数据用 `function`；中间态按模块用 `module`。选大了会串状态，选小了会慢。

**Q：怎么让用例可以按需筛选执行？**

A：打标记：`@pytest.mark.smoke`、`@pytest.mark.slow`，在 `pytest.ini` 注册避免 `PytestUnknownMarkWarning`，然后 `-m smoke` / `-m "not slow"`。CI 上跑全量，提交前跑 smoke。

**Q：测试之间有了顺序依赖，你怎么处理？**

A：先承认这是设计问题。做法：把前置数据抽成 fixture 或工厂，让每条用例自己造；确实需要顺序的（向导式流程）就合并成一条链路用例，而不是靠文件名排序。

## 延伸知识

- `pytest.ini` 里 `testpaths = labs`、`addopts = -q --strict-markers`，能避免误收集和拼错标记。
- 断言消息要带上下文：`assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}: {resp.text[:200]}"`。
- `--lf`（上次失败）、`-x`（首个失败即停）、`-k`（按名字筛）是日常最省时间的三个开关。
- 用例命名 `test_<对象>_<场景>_<期望>`，报告里直接读得懂，比 `test_1`、`test_2` 强太多。
