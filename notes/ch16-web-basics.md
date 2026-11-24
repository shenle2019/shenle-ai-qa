# 第 16 章 · 浏览器自动化基础与选择器

本章目标：能把浏览器用起来，能用稳定的方式找到页面元素，能在元素还没出现时正确地等它，而不是 `sleep(3)` 之后祈祷它已经在了。

## 1. 三个对象：浏览器、上下文、页面

Playwright 的模型是三层，先把这个记牢，后面所有坑都和它有关：

| 对象 | 是什么 | 生命周期 | 什么时候新建 |
| --- | --- | --- | --- |
| `Browser` | 一个浏览器进程 | 整个测试会话 | 会话开头起一次 |
| `BrowserContext` | 一套隔离的「浏览器身份」：cookie、localStorage、缓存、权限 | 一个用户 / 一组用例 | 每个测试用户起一个 |
| `Page` | 一个标签页 | 一条用例 | 每条用例新建 |

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    page.goto("https://example.com")
    print(page.title())
    context.close()      # 关上下文会连带关掉它下面的页面
    browser.close()
```

三条实践：

1. **context 就是「一个新用户」**。两条用例要互相隔离（比如各自登录成不同账号），就各开一个 context；要复用登录态，就在同一个 context 里开第二个 page。
2. **page 用完就关**。一个 context 下开三十个 page 不关，内存会一路涨，跑到后半程浏览器会变慢甚至崩。
3. **不要在用例里 `browser.close()`**。浏览器是会话级资源，关一次整个套件都废了；只在 fixture 的 `yield` 之后关。

## 2. 定位：按稳定性排序，不要按「能跑就行」排序

同一个按钮，能写出五六种定位。它们的稳定性差别很大，按下面的顺序选：

| 优先级 | 写法 | 命中依据 | 什么时候用 |
| --- | --- | --- | --- |
| 1 | `page.get_by_test_id("login-submit")` | `data-testid` 属性 | 自己能加属性时，永远首选 |
| 2 | `page.get_by_role("button", name="登录")` | 无障碍角色 + 可访问名 | 按钮、链接、输入框、标题 |
| 3 | `page.get_by_label("用户名")` | `<label for>` 关联 | 表单项 |
| 4 | `page.get_by_placeholder("请输入用户名")` | placeholder 文本 | 没有 label 的输入框 |
| 5 | `page.get_by_text("登录", exact=True)` | 可见文本 | 纯文案元素 |
| 6 | `page.locator("div > form > button:nth-child(3)")` | CSS / XPath 结构 | 前五种都不可用时 |

```python
page.get_by_role("button", name="登录").click()
page.get_by_label("用户名").fill("alice")
page.get_by_test_id("password").fill("secret")
page.get_by_text("任务清单", exact=False).first.is_visible()
```

**反例，以及为什么错：**

```python
# 错：按钮文字一改（「登录」→「立即登录」），用例全挂
page.locator("button").nth(2).click()

# 错：class 是样式名，前端重构一次就变
page.locator(".btn.btn-primary").click()

# 错：绝对 XPath 把整棵 DOM 结构写死，加个 div 就失效
page.locator("/html/body/div[2]/form/button").click()
```

**`name=` 默认是「包含」还是「相等」？** `get_by_role(name="登录")` 默认是**不区分大小写的子串匹配**，所以页面同时有「登录」和「登录帮助」时会把两个都命中。要精确匹配就加 `exact=True`。

**多个元素命中怎么办？** Playwright 遇到多个匹配时，`.click()` 会直接报 `strict mode violation`，不会自己挑第一个。要么把定位写精确，要么显式 `.first` / `.nth(i)`。这条设计是好事：它逼你在写的时候就确认「我到底要点哪个」。

## 3. 等待：三种超时，各管一段

Playwright 有自动等待：点击前会等元素「可见、稳定、能接收事件」，输入前会等元素「可编辑」。但**它不会等你自己的业务逻辑**（比如接口返回后列表才刷新）。所以要知道三个数：

| 超时 | 默认值 | 管什么 | 怎么改 |
| --- | --- | --- | --- |
| action timeout | 30 s | 单次 `click` / `fill` / `wait_for` 等操作 | `browser.new_context(...)` 里没有，用 `page.set_default_timeout(8000)` |
| navigation timeout | 30 s | `goto` / `wait_for_url` / 点击引发的跳转 | `page.set_default_navigation_timeout(15000)` |
| expect timeout | 5 s | `expect(...)` 断言的轮询上限 | `expect(locator).to_have_text(..., timeout=3000)` |

```python
page.set_default_timeout(8000)          # 操作类
page.set_default_navigation_timeout(15000)
page.get_by_test_id("start").click()
expect(page.get_by_test_id("done")).to_have_text("异步结果已返回", timeout=3000)
```

**为什么禁止 `time.sleep()`。** 三种情况它都错：

- 元素 200 ms 就出来了 → 白等 2.8 s，一百条用例多花五分钟；
- 元素 3.5 s 才出来 → 照样挂，而且是随机挂；
- CI 机器比本机慢 → 本机过、CI 挂，最难查。

正确做法只有一条：**断言「最终状态」**，让框架去轮询。`expect(locator).to_have_text()` / `to_have_count()` / `to_be_visible()` 都是轮询的，超时才失败。

## 4. 断言：用 expect，不要用 if

```python
from playwright.sync_api import expect

# 好：失败信息里有「期望 vs 实际」，而且会重试
expect(page.get_by_test_id("current-user")).to_have_text("alice")
expect(page.get_by_test_id("todo-item")).to_have_count(3)
expect(page.get_by_test_id("login-submit")).to_be_enabled()
expect(page.get_by_test_id("error")).to_contain_text("密码错误")

# 差：等价于「取一次快照再比较」，元素还没渲染完就判死
assert page.get_by_test_id("current-user").inner_text() == "alice"
```

`expect` 失败时会打印定位器、期望值、实际值和调用栈，`assert` 只给你一行 `AssertionError`——排查成本差一个数量级。

## 5. 失败留证：截图、页面源码、trace

断言失败时最想知道的是「当时页面长什么样」。三个层次的证据，按需要选：

```python
page.screenshot(path="artifacts/login-failed.png", full_page=True)   # 一眼能看
print(page.content()[:2000])                                          # 看 DOM
# trace 最全：录下每一步的 DOM 快照、网络、控制台
context.tracing.start(screenshots=True, snapshots=True, sources=True)
# ... 跑用例 ...
context.tracing.stop(path="artifacts/trace.zip")
```

trace 用 `playwright show-trace artifacts/trace.zip` 打开，能像录像一样回放每一步，是排查「CI 挂、本机过」的终极手段。

## 6. 本章实操

`labs/ch16-web-basics/` 里有三个文件：

- `labs/_shared/mini_site.py`：一个纯标准库的迷你网站（登录、待办列表、异步按钮），测试跑在本机回环地址，断网也能过；
- `demo_basics.py`：把四种定位、登录、异步等待、加待办、截图走一遍，打印每步结果；
- `test_web_basics.py`：12 条用例，覆盖标题、四种定位、错误密码、未登录跳转、自动等待、超时负向、列表追加、截图落盘。

```powershell
# 演示：打印每一步的真实输出
.\.venv\Scripts\python.exe labs\ch16-web-basics\demo_basics.py

# 测试：12 条
.\.venv\Scripts\python.exe -m pytest labs/ch16-web-basics -q
```

通过标准：`12 passed`，且 `docs/shots/ch16-todos.png` 能打开看到三行待办。

浏览器只装一次（约 150 MB，装到仓库目录，不进 Git）：

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "E:\ailearning\shenle-ai-qa\.pw-browsers"
$env:PLAYWRIGHT_DOWNLOAD_HOST = "https://npmmirror.com/mirrors/playwright"
.\.venv\Scripts\python.exe -m playwright install chromium
```

## 7. 自测

1. 为什么两条用例之间要新建 context，而不是共用一个 page？
2. `get_by_role("button", name="登录")` 和 `get_by_text("登录")` 有什么区别？
3. `expect(locator).to_have_text(...)` 失败时默认等多久？怎么改？
4. 页面同时有两个「删除」按钮，`page.get_by_role("button", name="删除").click()` 会怎样？怎么修？
5. 什么情况下可以用 `page.wait_for_timeout(300)`？

## 附：自测答案

1. **一个 context 等于一个新用户，一个 page 等于一个标签页。** 共用 page 会让上一条用例留下的 cookie、localStorage、表单状态污染下一条；共用 context 也不够干净（cookie 会带过去）。要复用登录态时可以共用 context（那是有意的），但用例之间默认应该隔离。
2. **role 匹配的是无障碍角色 + 可访问名，text 匹配的是可见文本。** 同一个「登录」文字，写在 `<button>` 上是 `role=button`，写在 `<a>` 上是 `role=link`，写在 `<div>` 上就没有 role（`get_by_role` 找不到它）。role 定位天然排除了「长得像按钮但不是按钮」的元素，所以更稳。
3. **默认 5 秒**，从 `expect` 开始轮询到超时。改法有两种：单次传 `timeout=3000`；或全局 `from playwright.sync_api import expect` 之后用 `expect.set_options(timeout=10_000)` 改默认值。
4. **报错 `strict mode violation`，不会点第一个。** Playwright 认为「你以为点 A，结果点了 B」比「直接失败」更危险。三种修法：把定位写更精确（限定到某一行：`row.get_by_role(...)`）、用 `.nth(1)`、或给每个按钮加 `data-testid`。
5. **只在调试时用，且不能用它替代断言。** 例如想看清动画中间态、或者手工复现某个时序问题时可以临时加；提交前删掉，换成对最终状态的 `expect`。

## 学生常问

**Q：headless 和 headed 跑出来的结果不一样，怎么办？**

A：先确认差异是不是「视口大小」和「字体」引起的：headless 默认视口 1280×720，headed 是窗口大小，页面在两种宽度下可能换行、元素互相遮挡。固定 `viewport={"width":1440,"height":900}`，并给字体加载留出等待（`page.wait_for_load_state("networkidle")` 或显式等目标元素）。如果仍然不一致，八成是页面里有「按 UA 或按屏幕宽度分支」的逻辑，直接用 headless 复现并把它当 bug 提给前端。

**Q：元素明明在页面上，`click()` 还是超时，报 `element is not stable` / `intercepts pointer events` 是什么意思？**

A：前者是元素还在动（有动画、有轮播），Playwright 会等它停下来再点；给动画加 `prefers-reduced-motion` 或等动画结束的类名变化更稳。后者是有别的元素盖在上面（弹窗遮罩、固定头部），此时用 `page.locator(...).click(force=True)` 能绕过，但那是掩盖问题——正确做法是先把遮罩关掉，再点目标。

**Q：iframe 里的元素怎么点？**

A：先拿 frame，再在 frame 里定位。`frame = page.frame_locator("iframe#pay")`，然后 `frame.get_by_role("button", name="确认")`。注意 frame 加载是异步的，`frame_locator` 会在定位时重试，不需要 sleep。

**Q：`get_by_text` 命中了父节点怎么办？**

A：Text 引擎默认只命中「包含这段文字的最小元素」：`<div><span>登录</span></div>` 只命中 span（实测 count=1），不会命中 div；只有当文字被拆到多个子节点（`<div><span>登</span><span>录</span></div>`）时才会命中父节点。要限定到某个后代，直接 `page.get_by_text("登录").locator("span")`，能换 role/testid 就别靠文本。

## 面试题

**Q：Playwright 和 Selenium 的核心区别是什么？**

A：三层。① 等待模型：Playwright 是自动等待 + 断言轮询，Selenium 需要显式 `WebDriverWait`，隐式等待和显式等待混用还会互相干扰；② 通信模型：Playwright 走 CDP/私有协议，一次调用可以在浏览器内执行多步，Selenium 走 WebDriver HTTP，每步一次往返，慢且容易有时序缝隙；③ 隔离模型：Playwright 的 context 是廉价的（毫秒级），可以每条用例一个新 context，Selenium 换 cookie 要手动清。

**Q：为什么说「用 text 定位不稳定」？什么情况下反而要用 text？**

A：text 不稳定是因为文案会改、会被翻译、会被 A/B 实验替换。但有两种情况它最合适：一是**测试目标本身就是文案**（比如验证提示语、错误信息）；二是**没有其他锚点**的第三方页面（改不了 DOM，加不了 testid），这时用 text 比用 nth-child 稳。

**Q：一条 UI 用例应该断言什么？**

A：断「用户能感知的结果」，不断「实现细节」。可接受的：URL 变了、某个业务字段的文案、列表条数、按钮可用状态、跳转后的页面标题。不可接受的：某个 div 的 class、某个请求被发出（那是接口测试该管的）、元素的具体像素位置。前者改样式就挂，后者和用户价值无关。

**Q：UI 自动化的用例数量应该怎么定？**

A：按金字塔：接口层覆盖 70–80% 的逻辑分支，UI 层只覆盖「接口测不到的部分」——渲染、交互、跳转、权限在界面上的表现。一个业务流写 5–8 条 UI 用例通常够了；写到 30 条说明你在用 UI 测接口。

## 延伸知识

- **多窗口与多标签**：点击 `target="_blank"` 的链接会开新页，正确写法是 `with context.expect_page() as new_page_info: page.get_by_text("打开").click()`，然后 `new_page = new_page_info.value`，再 `new_page.wait_for_load_state()`。直接 `context.pages[-1]` 有竞态。
- **上传与下载**：上传用 `page.get_by_label("文件").set_input_files("a.csv")`；下载用 `with page.expect_download() as info: page.get_by_text("导出").click()`，再 `info.value.save_as("out.csv")`。不要试图点开系统文件选择框，Playwright 直接给 input 塞文件。
- **CI 里的浏览器**：CI 机器没有图形界面，必须 `playwright install --with-deps chromium`；Windows 上要设 `PLAYWRIGHT_BROWSERS_PATH` 到固定目录，否则每次构建都重新下载 150 MB。缓存这个目录能把构建时间从 3 分钟压到 40 秒。
- **可访问性顺带就测了**：`get_by_role` 能命中的元素，屏幕阅读器也能读到；反过来，`get_by_role` 定位不到、只能靠 nth-child 的按钮，往往是真的可访问性问题（缺 `role`、缺可访问名）。写用例时遇到这种元素，顺手记一笔给前端。
