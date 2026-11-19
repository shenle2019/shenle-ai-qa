# 第 26 章 · 页面对象与页面栈

上一章能点到控件，但用例里全是「找 id → 点 → 等文字」。这一章把「一个界面会做什么」收进类，用例只写业务动作。

## 1. 页面类的三条约定

| 约定 | 具体做法 | 为什么 |
| --- | --- | --- |
| 定位只出现在类里 | 用例不写 `et_username` | 界面改了只改一处 |
| 动作返回下一个页面 | `open_login()` 返回 `LoginPage` | 调用链读起来像用户操作 |
| 断言只留「可观察结果」 | `result_text()` 返回文字，断言在用例里 | 页面类不替业务做判断 |

## 2. 一个最小的页面类

```python
class LoginDemoPage:
    PACKAGE = "com.shenjiahang.logindemo"
    USERNAME = "et_username"

    def __init__(self, app):
        self.app = app

    def open(self):
        self.app.start(self.PACKAGE)
        self.app.wait_text("登录联调 Demo")
        return self

    def tap_correct(self):
        self.app.tap(text_contains="登录（正确密码）")
        return self

    def result_text(self):
        return self.app.text_of(class_name="TextView", text_contains="code")
```

三个细节：`open()` 返回 `self` 让调用链不断；`tap_correct()` 只负责点，不判断结果；`result_text()` 只取文字，由用例决定「等于 100 才算过」。

## 3. 页面栈：从哪来回哪去

真实用例常常「列表 → 详情 → 返回列表」。页面类提供 `back_to_list()` 这类方法，内部用 `press_back()` + `wait_text()`，用例就不必关心是返回键还是左上角箭头。

`current_activity()` 用来确认「我现在到底在哪个界面」。它比找控件更可靠：控件可能同名，Activity 不会。

## 4. 页面类不该做的事

- 不读配置文件（那是 runner 的事）；
- 不做数据准备（那是 fixture 的事）；
- 不吞异常（失败要带着界面信息抛出去）；
- 不写日志格式（交给统一封装）。

## 5. 本章实操

`labs/ch26-page-object/login_page.py`：`open` / `tap_correct` / `tap_wrong` / `tap_photo` / `set_credentials` / `result_text` / `wait_result` / `is_loaded` / `current_activity`。

```bash
.\.venv\Scripts\python.exe -m pytest labs/ch26-page-object -q
```

真机上三条断言：正确密码结果含 `"code": 100`、错误密码含 `"code": 101`、加载图片后出现宽高均大于 100 的 `ImageView`。

## 常见坑

1. **页面类里塞断言**：一旦断言写进页面类，换一个业务场景就得改页面类，复用性没了。
2. **`open()` 不等首屏**：直接点按钮时界面还没起来，随机失败。`open()` 里要有一次 `wait_text`。
3. **方法名写成 `click_login_button_1`**：名字要描述业务意图（`tap_correct`），不要描述控件。
4. **登录态没处理**：每次 `force-stop` 后都是未登录，页面类要么自己处理，要么明确「调用前需要已登录」。

## 自测

1. 为什么 `open()` 要返回 `self`？
2. 页面类里能不能写 `assert "100" in self.result_text()`？
3. `current_activity()` 相比「找某个控件」好在哪？
4. 一个页面有 40 个控件，全写成 property 好吗？

## 附：自测答案

1. 为了链式调用，让用例一行写完「打开 → 点 → 读结果」，读起来就是业务动作。
2. 不建议。断言属于用例，页面类只提供「可观察的结果」；写死断言会让这个页面类只能服务一个场景。
3. Activity 是系统层的唯一标识，不受控件文案变化影响；控件可能重名或延迟加载。
4. 不好。只封装用例真正会用的少数控件，其余留在方法内部，避免页面类变成「控件字典」。

## 学生常问

**Q：页面类要不要按屏幕拆？**

A：按「用户能感知到的界面」拆。同一个 Activity 里的不同弹层，如果行为差异大，可以拆成两个类，互相 `open()`。

**Q：PO 和 Screenplay 的区别？**

A：PO 把「界面」当对象，Screenplay 把「用户任务」当对象（Actor 执行 Task）。小型项目 PO 够用，大型项目 Screenplay 更好扩展。

**Q：页面类怎么处理加载中状态？**

A：`wait_result()` 这类方法里轮询「结果区出现」，而不是在构造函数里等；加载是动作的一部分，不是对象的状态。

## 面试题

**Q：PO 模式解决了什么问题？**

A：把「界面结构」和「业务用例」解耦。界面改动只影响页面类，用例表达的是业务意图，可读性和可维护性都提升。

**Q：怎么保证页面类不腐化？**

A：三条纪律：定位只在类里、动作返回下一页、断言不进页面类。再配合「用例里不出现 id」这条检查，腐化会立刻暴露。

**Q：页面类和 fixture 的边界在哪？**

A：fixture 负责「准备好一个可用的世界」（设备、后端、登录态），页面类负责「在这个世界里操作界面」。两者都不该替对方做事。

## 延伸知识

- 页面类可以有 `is_loaded()`，返回布尔而不是抛错，用于「可能在也可能不在」的场景。
- 多页面共享的导航（返回、首页、抽屉）放 `BasePage`。
- 页面类里避免 `time.sleep`，统一用 `app.wait_*`。
- 给页面类写一个「真实 dump 校验」的单测：断言类里用到的 id 都存在于 dump 中，能提前发现改版。
