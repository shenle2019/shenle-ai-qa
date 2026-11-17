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

## 6. 本章实操

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

## 附：自测答案

1. 非幂等方法重试会产生重复副作用（重复下单、重复扣款）。POST 要重试必须有两个前提：请求带幂等键，且服务端按键去重。
2. `status` 划分问题类型（4xx 请求错、5xx 服务错、0 连接错），`body` 指出具体字段和规则。只带 message 的异常，到了用例层还得重新请求一遍才能定位。
3. 靠三样东西：响应码与业务码、请求 id（`X-Request-Id`）、token 的指纹（前 6 位 + 长度，或者解析出的 user_id/scope）。必要时在测试环境临时打开详细日志，但绝不进主干。
4. 加一个策略参数，比如 `status_policy="any"` 或 `expect_status={200, 202}`，默认行为保持不变；只有显式传入时才把 5xx 当成功，这样老用例一行都不用改。
5. 三类：重试策略错（次数、条件、退避）、异常包装错（该抛的吞了、类型不对、丢了上下文）、请求拼装错（base_url 拼接、路径重复斜杠、头合并覆盖）。

## 学生常问

**Q：封装到什么程度算合适？**

A：够用例写得干净就行：一个方法完成一次请求、抛统一的异常、返回结构化结果。不要为了「通用」加一堆没人用的参数和钩子，那是负债。

**Q：为什么不直接在用例里写 `requests.get`？**

A：三个原因：重试、日志、异常处理会散落在每个用例里；换域名/换鉴权方式要改几十处；封装本身能被单测覆盖，用例层就只关心业务。

**Q：封装要不要做「自动重试 + 自动断言」？**

A：重试可以，断言不行。断言属于用例的职责，封装里藏断言会让失败信息模糊，也让人无法选择「这个接口就该返回 400」。

## 面试题

**Q：你的接口框架分几层，各层职责是什么？**

A：配置层（环境、域名、超时）、客户端层（发请求、重试、日志、异常）、接口层（按业务域封装具体接口，如 `UserApi.login`）、用例层（组织场景与断言）。分层的目的是一处改动只影响一层。

**Q：怎么让封装本身可测？**

A：依赖注入：把「真正发请求的函数」作为参数传进来（`transport`），测试时传入假实现，就能断言重试次数、异常类型、URL 拼接，不用起服务。

**Q：框架里日志应该记什么、不该记什么？**

A：记方法、路径、状态码、耗时、重试次数、请求 id；不记 Authorization、Cookie、密码、完整身份证/手机号。响应体只在失败时记，且截断长度。

## 延伸知识

- 重试要配退避（指数或固定间隔），否则瞬间打满服务端；同时设最大次数，避免雪崩。
- 统一异常类型后，用例层可以只 `except ApiError`，再按 `status` 分流，不用认识 requests 的七八种异常。
- base_url 拼接用 `urljoin` 或统一去掉尾部斜杠，别用字符串相加，`//api` 这种路径会让网关 404。
- 把「调用记录」留在客户端上（`self.calls`），排查顺序依赖和多余请求时非常省事。
