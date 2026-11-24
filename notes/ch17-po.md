# 第 17 章 · 页面对象：把选择器关进类里

本章目标：把「散在用例里的定位」收进页面类，用例只写业务动作。做完你能说清：为什么用例里不允许出现 `page.locator(...)`，以及一个页面类到底该有哪些方法。

## 1. 没有页面对象时，坏在哪

```python
def test_add_todo(page, site):
    page.goto(f"{site}/login")
    page.get_by_test_id("username").fill("alice")
    page.get_by_test_id("password").fill("secret")
    page.get_by_test_id("login-submit").click()
    page.wait_for_url("**/todos")
    page.get_by_test_id("new-title").fill("买牛奶")
    page.get_by_test_id("add-submit").click()
    assert "买牛奶" in page.get_by_test_id("todo-list").inner_text()
```

这条用例能跑，但有三处会反复折腾：

1. 后面 20 条用例都要重复前 8 行登录；
2. 按钮改名 → 20 条用例一起改；
3. 用例读起来像在操作 DOM，看不出「它在验证什么业务」。

页面对象解决的是这三件事，不是「代码整洁」这种虚的理由。

## 2. 一个页面类该长什么样

```python
class TodoPage:
    path = "/todos"

    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self):
        self.page.goto(self.base_url + self.path)
        return self

    @property
    def current_user(self):
        return self.page.get_by_test_id("current-user")

    def add(self, title):
        self.page.get_by_test_id("new-title").fill(title)
        self.page.get_by_test_id("add-submit").click()
        return self

    def titles(self):
        return [item.inner_text().strip() for item in self.page.get_by_test_id("todo-item").all()]
```

三条约定：

- **定位只在类里出现**，而且只出现在 `@property` 或方法的内部；
- **方法返回 `self`**，用例可以链式写 `TodoPage(page, site).open().add("买牛奶")`；
- **断言可以收进页面类**（如 `expect_user`），但要克制：业务断言留在用例里，页面类只做「结构断言」。

## 3. 继承能省什么

`BasePage` 放三样东西：`base_url`、`open()`、`expect_path()`。

```python
class BasePage:
    path = "/"

    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self):
        self.page.goto(self.base_url + self.path)
        return self

    def expect_path(self, suffix=None):
        expect(self.page).to_have_url(re.compile(re.escape(suffix or self.path) + r"$"))
```

`expect_path` 里为什么要 `re.escape`：`?`、`.`、`+`、`(` 是正则元字符（中文不是），URL 的查询串最常带 `?`；不转义会把它当正则语法，匹配到别的路径。

## 4. 页面类不该做的事

| 不该做 | 为什么 | 该放哪 |
| --- | --- | --- |
| 连数据库、造数据 | 页面类只负责「页面」 | 用例前置 / 工厂函数 |
| 断言业务规则（金额对不对） | 这不是页面的职责 | 用例里 |
| 保存全局状态 | 一个类实例对应一个页面 | 夹具 |
| 直接 `time.sleep` | 会拖慢且不稳 | `expect` / `wait_for_url` |

## 5. 本章实操

`labs/ch17-po/`：

| 文件 | 作用 |
| --- | --- |
| `po_pages.py` | `BasePage` + `LoginPage` / `TodoPage` / `ProfilePage` |
| `test_po.py` | 7 条：登录成功/失败、加待办、计数、页面跳转、类里没有裸 locator |

跑法：

```powershell
.\.venv\Scripts\python.exe -m pytest labs/ch17-po -q
```

其中 `test_locators_live_in_the_page_class` 会读源码文件，断言 `test_po.py` 里没有 `get_by_test_id(`。这条看着像元测试，但它是这一章唯一不会随时间失效的护栏。

## 6. 自测

1. 为什么 `open()` 要返回 `self`？
2. 页面类里能不能写 `assert "买牛奶" in page.content()`？
3. `expect_path` 为什么不能直接拼字符串做 `endswith` 判断？
4. 一个页面有 30 个元素，全写成 property 有什么问题？

## 附：自测答案

1. 返回 `self` 是为了链式调用，用例一行写完「打开 → 操作 → 断言」，读起来就是业务动作；不返回也能跑，但调用方要重复写变量名。
2. 不建议。`page.content()` 拿整页 HTML，断言会在无关元素里误命中；业务断言用可见文本或接口返回值，页面类只提供「拿到那个元素」的方法。
3. `endswith` 对带查询串的 URL 会误判（`/todos?page=2` 不以 `/todos` 结尾），而且中文路径容易被编码成 `%E4%B8%AD`；用 `expect(page).to_have_url(re.compile(...))` 让 Playwright 自己等、自己重试。
4. 会变成一个「元素字典」，用例仍然要自己组织顺序，等于把 locator 换了个写法。property 只留「会被多条用例反复用到的元素」，其余收进方法内部。

## 学生常问

**Q：页面类要不要按「页面」拆，还是按「组件」拆？**

A：先按页面拆，出现「同一块区域在三个页面重复」时再抽组件（导航栏、弹窗）。一上来就拆组件，通常拆出一堆只有一个方法的小类，反而更难找。

**Q：登录这种每条用例都要做的动作，放页面类还是夹具？**

A：动作放页面类（`LoginPage.login`），「什么时候登录」放夹具。本章的 `labs/ch17-po` 用夹具起浏览器、用例里显式调 `login()`；第 19 章会把登录态做成会话级夹具。

**Q：`base_url` 存类里还是存夹具里？**

A：存类里，但由夹具传进来。这样换环境只改一个变量，页面类不需要知道 `local` 还是 `staging`。

## 面试题

**Q：说说你对 PO 模式的理解，它解决了什么问题？**

A：PO 把「页面结构」和「测试逻辑」分开：页面类封装定位与页面动作，用例只表达业务步骤。解决的问题是变更成本——元素变了只改页面类；以及可读性——用例读起来是业务语言。代价是多一层间接，页面少的时候会显得啰嗦。

**Q：页面类里放断言，你觉得合适吗？**

A：分两种。结构断言（这个元素可见、URL 到了某页）放页面类合适，因为它是「页面处于某状态」的定义；业务断言（金额、库存、状态机）留在用例里，因为它依赖业务规则，页面类不该知道。

**Q：PO 和 Screenplay 模式的区别？**

A：PO 以「页面」为中心，Screenplay 以「角色 + 任务」为中心（Actor 执行 Task，Task 由 Interaction 组成）。页面流程分支多、角色多时 Screenplay 更好扩展；页面数量有限、流程线性时 PO 更省事。多数团队用 PO 就够了。

**Q：怎么保证页面类不会退化成 locator 仓库？**

A：两条：一是用例里禁止出现 `page.locator/get_by_test_id`，用 lint 或一条元测试卡住；二是页面类只暴露「业务动作」（`add`、`login`），不暴露「元素」（`title_input`）——需要暴露元素说明动作没抽象到位。

## 延伸知识

- **`expect` 自带重试**：`expect(locator).to_contain_text()` 默认 5 秒内轮询，比 `assert locator.inner_text() == ...` 稳得多，页面类里的结构断言优先用它。
- **`page.wait_for_url` 的匹配规则**：字符串走 glob（`**/todos`），正则走 `re.compile`。混用是最常见的「明明到了却超时」。
- **页面类的组合优于继承**：`ProfilePage` 里持有一个 `NavBar` 组件对象，比继承 `BasePage` 再复制方法更清晰；本章为了讲继承才用 `BasePage`。
- **locator 实例可以缓存**：Locator 只保存选择器与过滤链，每次动作/断言都重新解析 DOM，元素被替换后仍命中新节点（实测）。会「指向旧节点」的是 ElementHandle——那个才该换成 locator 或缓存选择器字符串。
