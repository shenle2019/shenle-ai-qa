# 第 11 章 · 封装 HttpClient

上一章的代码如果直接复制到二十个用例里，改一个超时就要改二十处。封装要解决的只有一件事：**让变化只发生在一个地方**。

## 1. 分四层，各管一件事

```
config     环境、超时、重试、日志级别      ← 改配置不改代码
client     HTTP 细节（会话、重试、异常）    ← 改传输不改用例
api        业务语义（login/create_order）  ← 改接口不改断言
case       断言与流程                      ← 改期望不改实现
```

判断分层对不对，用一个问题：**接口加了一个必填字段，要改几个文件？** 答案应该是「api 层一个，用例里补数据的地方若干」。

## 2. client 该暴露什么

```python
class HttpClient:
    def request(self, method, path, **kw) -> Response
    def get(self, path, **kw) -> Response
    def post(self, path, json=None, **kw) -> Response
```

关键设计：

| 点 | 做法 | 为什么 |
| --- | --- | --- |
| 基址 | `base_url` 拼在 client 里 | 用例里只写 `/api/users` |
| 超时 | 默认值 + 单次可覆盖 | 避免「忘记写」 |
| 重试 | 只对幂等方法与 5xx/连接错误 | 否则会重复下单 |
| 异常 | 统一抛 `ApiError(status, body)` | 用例只处理一种异常 |
| 日志 | 记方法/路径/状态/耗时，脱敏 token | 排障靠它 |
| 返回 | 包装 `Response`（含 json/text/elapsed） | 断言时不用记 requests 细节 |

## 3. 日志要能定位，又不能泄密

```python
def _log(self, method, path, status, ms, attempt):
    logger.info("%s %s -> %s in %.0fms (try %d)", method, path, status, ms, attempt)
```

三条规矩：

1. **不打印 `Authorization`**，只打印「有无 token」。
2. **body 超过 500 字符截断**，否则日志没人看。
3. **失败时打印响应体**，成功时不打（噪声）。

## 4. 异常要带上下文

```python
class ApiError(RuntimeError):
    def __init__(self, method, path, status, body):
        super().__init__(f"{method} {path} -> {status}: {body[:200]}")
        self.status = status
        self.body = body
```

只抛 `Exception("请求失败")` 的封装等于没封装：定位时还得回去读代码。

## 5. 让封装自己可测

HttpClient 也要有测试：给它一个假的 transport（函数），断言它「重试了几次」「异常信息是否包含状态码」。这样改封装时不会误伤用例。

```python
def fake(method, url, **kw):
    return Response(503, {"error": "x"})
client = HttpClient("http://x", transport=fake, retries=2)
```

## 6. 本章实验

`labs/ch11-httpclient/`：

- `http_client.py`：`HttpClient`（base_url、默认头、超时、重试、日志、`ApiError`）+ `Response` 包装；
- `api.py`：`UserApi` / `OrderApi`，把路径与参数收敛成语义方法；
- `test_http_client.py`：用 `transport` 假函数测重试与异常，用真 SUT 测端到端。

```powershell
.venv\Scripts\python.exe labs\ch11-httpclient\demo.py
.venv\Scripts\python.exe -m pytest labs\ch11-httpclient -q
```

## 7. 自测

1. 为什么重试只对幂等方法开放？POST 想重试需要什么前提？
2. `ApiError` 里为什么一定要带 `status` 与 `body`？
3. 日志里不打印 token，那排查鉴权问题靠什么？
4. 如果业务方要求「5xx 也当成功」（比如异步任务受理），封装该怎么改而不影响已有用例？
5. 用 `transport` 注入假响应，能测出封装的哪三类 bug？
