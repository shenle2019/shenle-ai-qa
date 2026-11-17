# 第 10 章 · 用 requests 发请求

`requests` 只有五个东西需要记：**方法、URL、参数放哪、头、超时**。剩下的坑都在「看起来成功了，其实是错的」这一类里。

## 1. 最小可用集

```python
import requests

r = requests.get("http://127.0.0.1:8010/api/health", timeout=5)
r = requests.post(url, json={"name": "dave"}, headers={"X-Trace": "1"}, timeout=5)
r = requests.post(url, data={"user": "a"}, timeout=5)          # 表单
r = requests.post(url, files={"file": ("a.txt", b"hi")}, timeout=5)  # multipart
```

四条准则：

1. **永远带 `timeout`**。不写就是无限等，CI 上会挂到天荒地老。
2. **JSON 用 `json=`，表单用 `data=`**。用错服务端收不到，且不报错。
3. **状态码不会自己抛异常**。要 `raise_for_status()` 或自己判。
4. **`r.text` 的编码可能猜错**。中文乱码时先看 `r.encoding`，或直接用 `r.content.decode("utf-8")`。

## 2. Session：别每次请求都重新握手

```python
s = requests.Session()
s.headers.update({"Authorization": f"Bearer {token}"})
s.get(url, timeout=5)   # 复用 TCP 连接与 cookie
```

三个好处：连接复用（快）、cookie 自动带、默认头只写一次。接口自动化里**一个用户一个 Session**，别全局共用一个——否则越权用例会互相污染。

## 3. 参数放错位置，是最常见的手工 bug

| 想传 | 写法 | 结果 |
| --- | --- | --- |
| query | `params={"page": 1}` | `?page=1` |
| JSON body | `json={"name": "a"}` | `Content-Type: application/json` |
| 表单 | `data={"name": "a"}` | `application/x-www-form-urlencoded` |
| 头 | `headers={...}` | 原样发送 |
| 文件 | `files={...}` | `multipart/form-data` |

`params` 里的中文会被 requests 自动 URL 编码；如果服务端收到乱码，先打印 `r.request.url` 看实际发出去的地址。

## 4. 超时、重试与幂等

```python
timeout=(3.05, 10)          # (连接超时, 读超时)
```

重试只对**幂等**请求安全。GET/PUT/DELETE 可以重试；POST 要看有没有 `Idempotency-Key`。

```python
for attempt in range(3):
    r = s.get(url, timeout=5)
    if r.status_code < 500:
        break
    time.sleep(0.2 * (attempt + 1))
```

生产里用 `urllib3.util.Retry` 配 `HTTPAdapter`，但要记得：**重试会把失败藏起来**，日志里必须记 `attempt`。

## 5. 异常分三类，处理方式不同

| 异常 | 含义 | 处理 |
| --- | --- | --- |
| `ConnectionError` | 连不上（服务没起、端口错、DNS） | 检查环境，不要重试到死 |
| `Timeout` | 连上了但没按时回 | 可重试，记指标 |
| `HTTPError`（`raise_for_status`） | 4xx/5xx | 4xx 是用例失败，5xx 可能是环境抖动 |

写用例时，**不要让异常直接冒到 pytest 外面**：它会把「服务没起」和「断言失败」混在一起，排查成本翻倍。

## 6. 下载大文件用流式

```python
with s.get(url, stream=True, timeout=30) as r:
    for chunk in r.iter_content(8192):
        f.write(chunk)
```

`r.content` 会一次性读进内存，几百 MB 的导出文件会直接把进程撑爆。

## 7. 本章实操

`labs/ch10-requests/`：

- `session_demo.py`：登录一次复用 token、量耗时、对 503 做有限重试、流式下载、把异常收敛成 `(ok, payload, error)`；
- `test_session_demo.py`：验证「复用会话比每次登录快」「重试能穿透 503」「超时会抛 Timeout」「中文参数正确编码」「下载字节一致」。

```powershell
.venv\Scripts\python.exe labs\ch10-requests\session_demo.py
.venv\Scripts\python.exe -m pytest labs\ch10-requests -q
```

SUT 里有个 `/api/flaky?key=xxx`：前两次返回 503，第三次 200，专门用来练重试。

## 8. 自测

1. `json=` 和 `data=` 在请求里分别变成什么 `Content-Type`？
2. 为什么「重试」对 POST 是危险的？什么条件下可以安全重试？
3. `r.status_code == 200` 能不能说明接口没问题？还应该看什么？
4. 中文返回值乱码，你会按什么顺序排查？
5. 服务没启动时，`requests.get` 抛的是哪个异常？和断言失败怎么区分？

## 附：自测答案

1. `json=` 会序列化并设 `Content-Type: application/json`；`data=` 传字典时会编码成表单并设 `application/x-www-form-urlencoded`。传 `files=` 则是 `multipart/form-data`。
2. POST 非幂等，失败重试可能造成重复下单、重复扣款。只有两种前提可以安全重试：请求带幂等键且服务端按幂等处理，或服务端明确保证同一请求重复提交结果一致。
3. 不能。200 只说明 HTTP 层通了，业务可能返回 `code=500`。还要看业务码、关键字段、数组长度，必要时看响应时间。
4. 顺序：先看响应头 `Content-Type` 的 charset → 检查 `resp.encoding` → 用 `resp.apparent_encoding` 探测 → 手动 `resp.content.decode("utf-8")` → 最后才怀疑服务端返回的就是错的。
5. 抛 `requests.exceptions.ConnectionError`（底层是 `NewConnectionError`/`MaxRetryError`）。断言失败是 `AssertionError`。两者要分开报：前者是环境问题，后者是业务不符合预期。

## 学生常问

**Q：`Session` 和直接 `requests.get` 差别大吗？**

A：大。`Session` 复用 TCP 连接和 cookie，还能统一挂 headers、超时、重试和代理。用例里几十个请求，用 Session 快很多，也不会因为丢 cookie 导致偶发 401。

**Q：超时该设多少？**

A：分连接超时和读超时，写元组 `timeout=(3, 10)`。连接 3 秒够用（本地可以 1 秒），读超时按接口 P99 的两三倍设。不设超时是最危险的写法——CI 会卡死。

**Q：为什么只对 5xx 重试，4xx 不重试？**

A：5xx 是服务端临时故障，重试有意义；4xx 是请求本身有问题（参数错、没权限），重试一百次结果一样，只是浪费时间和日志。

## 面试题

**Q：`requests` 的常见异常有哪些，分别代表什么？**

A：`ConnectionError`（连不上/连接被重置）、`Timeout`（连接或读超时，`ConnectTimeout`/`ReadTimeout`）、`HTTPError`（`raise_for_status` 抛出）、`TooManyRedirects`（重定向过多）、`RequestException`（基类，兜底用）。

**Q：怎么处理需要登录态的接口？**

A：优先走登录接口拿 token，放在 Session 的 headers 里复用；如果系统用 cookie，Session 会自动保存。不要从浏览器复制 token 写死在代码里，也不要每次请求都重新登录。

**Q：接口返回 gzip 压缩内容，requests 要特殊处理吗？**

A：不用，`requests` 默认会带 `Accept-Encoding: gzip, deflate` 并自动解压。只有在手动用 `urllib` 或拿 `raw` 流时才需要自己解压。

## 延伸知识

- `resp.json()` 在响应不是 JSON 时抛 `JSONDecodeError`，断言前先看 `Content-Type` 或包一层 try。
- 大文件下载用 `stream=True` + `iter_content`，否则会整个读进内存。
- 代理用 `proxies={"http": ..., "https": ...}`，抓包调试时配合 Charles/Fiddler。
- 关掉 `verify=False` 只应出现在临时调试，且要单独提示，不能进主流程。
