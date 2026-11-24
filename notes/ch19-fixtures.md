# 第 19 章 · 前后置与浏览器复用

本章目标：让登录只做一次、浏览器只起一次，同时保证用例之间互不污染。做完你能说清 `storage_state` 到底存了什么。

## 1. 为什么「每条用例都登录」不能接受

10 条用例、每条登录 1.5 秒，就是 15 秒纯等待；100 条就是 2.5 分钟。更麻烦的是**不稳定**：登录接口抖一下，全线飘红，看起来像「测试挂了」。

所以要复用两样东西：

| 复用对象 | 生命周期 | 手段 |
| --- | --- | --- |
| 浏览器进程 | 整个会话 | session 级夹具 |
| 登录态 | 整个会话 | `context.storage_state()` |

## 2. storage_state 存了什么

```json
{
  "cookies": [{"name": "sid", "value": "...", "domain": "127.0.0.1", "path": "/"}],
  "origins": [{"origin": "http://127.0.0.1:8000", "localStorage": [{"name": "token", "value": "..."}]}]
}
```

顶层两块：**cookies** 和 **origins**（`origins` 里带 `localStorage`，Playwright 1.51 起还包含 `indexedDB`）。所以它既能恢复「服务端会话」，也能恢复「前端自己存的 token」。

用法就两步：

```python
# 存：登录一次
context.storage_state(path="auth.json")

# 用：每条用例新建 context 时套上
context = browser.new_context(storage_state="auth.json")
```

## 3. 三条隔离原则

1. **context 每条用例一个**，browser 会话级共享。context 相当于一个独立浏览器配置，cookie / localStorage / 缓存都隔离。
2. **写操作要能被感知**：某条用例改了自己的待办，不能影响下一条——靠 context 隔离，不靠「跑的时候小心点」。
3. **匿名场景单独开 context**：测「未登录被拦截」时不能复用带 cookie 的 context，否则永远测不出问题。

## 4. 本章实操

`labs/ch19-fixtures/`：

| 文件 | 作用 |
| --- | --- |
| `conftest.py` | `auth_state`（会话级、只登录一次）、`page`（恢复登录态）、`anon_page`（干净上下文） |
| `test_reuse.py` | 7 条：state 里有 `sid`、page 直接进待办、匿名被跳登录、写入不串台、下一条用例干净、browser 复用、只登录一次 |

跑法：

```powershell
.\.venv\Scripts\python.exe -m pytest labs/ch19-fixtures -q
```

`test_login_only_happened_once` 用一个计数器校验「登录接口真的只被调了一次」，而不是靠肉眼相信夹具。

## 5. 常见坑

- **`storage_state` 是快照不是引用**：存完再登录，文件不会变；要更新得重新存。
- **cookie 的 domain 要对得上**：`127.0.0.1` 和 `localhost` 是两个域，混用会出现「明明登录了却还是跳登录」。
- **会话级夹具里的失败会拖垮整批**：登录夹具挂了，全部用例 error。可以在夹具里加一次重试，并把失败信息写清楚（「登录接口返回 401」）。
- **别把 state 文件提交进 Git**：里面是活 token。写进 `.gitignore`。

## 6. 自测

1. `storage_state` 保存了哪两类数据？
2. 为什么 `page` 是函数级、`browser` 是会话级？
3. 测「未登录被拦截」时直接复用 `page` 会怎样？
4. state 文件为什么不能进 Git？

## 附：自测答案

1. `cookies` 和 `origins[].localStorage`。前者恢复服务端会话，后者恢复前端自己存的 token/开关。
2. `browser` 启动一次成本高（1–2 秒），会话级复用；`page`/`context` 承载可变状态（cookie、页面数据），函数级才能保证用例之间互不污染。
3. 会一直「已登录」，用例永远通过——测的是假象。必须用干净 context（本章的 `anon_page`）。
4. 里面是活会话 cookie，提交等于把测试环境账号给所有人；而且过期后会让别人本地跑出莫名其妙的失败。

## 学生常问

**Q：登录态多久会过期？用例跑一半失效怎么办？**

A：取决于服务端 session TTL（本章 SUT 是 1 小时）。工程做法是：夹具里记录存 state 的时间，超过阈值就重新登录；或者干脆每条用例前 ping 一次「当前用户」接口，401 就重登。

**Q：能不能用 API 登录拿 token，再塞进 localStorage，跳过 UI 登录？**

A：可以，而且更快更稳。前提是「登录 UI 本身不在被测范围」。如果这轮要测登录页，就必须走 UI 登录，不能抄近路。

**Q：并发跑用例时，共享一个 auth_state 会有问题吗？**

A：读没问题，写有问题——多条用例同时刷新同一个 state 文件会互相覆盖。并发场景下让每个 worker 自己登录、自己存，文件名带上 worker id。

## 面试题

**Q：你们怎么做测试用例之间的数据隔离？**

A：三层：进程层（每 worker 独立 browser）、上下文层（每条用例新 context，套 storage_state 恢复登录）、数据层（造数据带唯一前缀，用例结束删掉自己造的）。只做其中一层都会出现「单独跑过、一起跑挂」。

**Q：浏览器复用能省多少时间？有什么风险？**

A：以本章实测，登录 1.5 秒/次起步，100 条用例能省 2 分钟以上。风险是状态泄漏：上一条用例改动没被清理，下一条看到脏数据。所以复用 browser 必须配 context 隔离，两者是绑定的。

**Q：session 级夹具失败了，怎么让报错更可读？**

A：在夹具里显式断言并带上上下文（接口返回码、URL、截图路径），而不是让 `AttributeError: 'NoneType'` 冒到用例里。夹具失败信息是整批用例唯一的线索，值得多写两行。

**Q：`context.storage_state()` 和手动 `add_cookies()` 怎么选？**

A：要恢复「完整登录态」（cookie + localStorage）用 `storage_state`；只需要塞一个 token 进 cookie 时 `add_cookies` 更直接。手动塞的风险是漏掉 localStorage，出现「cookie 有但页面还是未登录」。

## 延伸知识

- **`browser.new_context()` 的隔离级别**：cookie、localStorage、sessionStorage、缓存、权限全部独立；但共享同一浏览器进程与网络栈。
- **`--headed` 调试**：`pw.chromium.launch(headless=False)` 能看到真实操作过程，排查「元素点了没反应」比读日志快。
- **trace 比截图强**：`context.tracing.start(screenshots=True, snapshots=True)` 会记录每一步 DOM 快照，`playwright show-trace` 能时间轴回放。
- **`storage_state` 也能喂给 API 请求**：把 cookie 拼到 `requests` 的 header 里，UI 登录一次、接口复用同一会话，省掉二次鉴权。
