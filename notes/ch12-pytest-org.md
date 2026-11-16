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

## 7. 本章实验

`labs/ch12-pytest-org/`：四个测试文件，覆盖 CRUD、鉴权、参数化边界、状态机，共 14 条。

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
