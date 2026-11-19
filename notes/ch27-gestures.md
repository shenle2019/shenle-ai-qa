# 第 27 章 · 手势与输入

点击只是最基础的操作。真实用例还要输入、清空、滑动、长按、返回、收键盘。

## 1. 输入：最容易被低估的坑

`adb shell input text` 有三个硬限制：

| 限制 | 表现 | 对策 |
| --- | --- | --- |
| 空格 | 命令被截断 | 传 `%s` |
| 中文/emoji | 直接失败或乱码 | 剪贴板方案或改用 App 内输入 |
| 输入法联想 | `qa_user` 变成「去啊＿」 | 先切英文输入法，或只断言「内容变了」 |

密码框还要额外注意：读回来的是掩码（`••••`），断言只能比较长度，不能比较内容。

## 2. 清空再输入

```python
def clear_and_type(app, id_short, text):
    field = app.wait_for(lambda t: t.find(id_short=id_short))
    field.click()                      # 先聚焦
    app.device.keyevent("KEYCODE_MOVE_END")
    for _ in range(30):
        app.device.keyevent("KEYCODE_DEL")
    app.device.input_text(text)        # 输入
    return app.text_of(id_short=id_short)
```

「先聚焦」这一步不能省：不聚焦时按键事件发给了当前焦点控件，删除键删的是别人的内容。

## 3. 手势

| 动作 | 实现 | 用途 |
| --- | --- | --- |
| 点击 | `input tap x y` | 控件可点时优先用 `tap(**criteria)` |
| 长按 | `input swipe x y x y 800` | 起点终点相同 + 时长，就是长按 |
| 滑动 | `input swipe x1 y1 x2 y2 300` | 列表翻页、下拉刷新 |
| 返回 / 主页 | `input keyevent 4` / `3` | 关闭弹层、回到桌面 |

滑动的方向要按屏幕比例算，不要写死像素：`y1` 取 0.7 屏高、`y2` 取 0.3 屏高，换设备也不会滑出屏幕。

## 4. 键盘与遮挡

软键盘弹出会遮住下半屏，导致「控件存在但点不到」。两个办法：`keyevent 111`（ESC）或 `input keyevent 4` 先收键盘；更稳的是点一下空白区域，让焦点离开输入框。

## 5. 本章实操

`labs/ch27-gestures/gestures.py`：`clear_and_type` / `hide_keyboard` / `press_back` / `press_home` / `swipe_up` / `long_press_text` / `tap_coordinates` / `foreground_package`。

```bash
.\.venv\Scripts\python.exe -m pytest labs/ch27-gestures -q
```

## 常见坑

1. **删除键删不掉**：焦点不在目标输入框，先 `click()` 再发按键。
2. **`input text` 输入中文失败**：adb 的 text 只支持 ASCII，中文要走「推送剪贴板 + 粘贴」或改用 App 内接口。
3. **滑动没反应**：时长太短被识别成 fling，`300` 毫秒左右比较稳。
4. **返回键关掉了整个 App**：某些页面按返回直接退出，需要用页面内的「取消」按钮。

## 自测

1. `input text "hello world"` 为什么会失败，怎么写才对？
2. 长按是怎么用 `input swipe` 实现的？
3. 密码框为什么不能断言具体内容？
4. 键盘遮挡导致控件点不到，有哪两种处理方式？

## 附：自测答案

1. 空格会被命令解析截断；用 `hello%sworld`（`%s` 代表空格）。
2. 起点终点相同、时长设为 800ms 左右，系统会判定为长按。
3. 密码框显示的是掩码，读回来是 `••••`；只能比较长度或断言「非空」。
4. 先收键盘（`keyevent 4` / 点空白）再点；或改用 `tap` 坐标前先把键盘收起。

## 学生常问

**Q：为什么不用 `set_text` 这类 API？**

A：这里只用 adb，没有 App 进程内的接口权限。`set_text` 属于 UiAutomator/Appium 的能力，底层仍然要注入事件。

**Q：输入法联想可以彻底避免吗？**

A：最稳的是把设备输入法切成「英文/无联想」；退一步是把断言改成「内容非空且长度合理」，不要断言具体字符串。

**Q：滑动查找列表项怎么做？**

A：循环「在当前树里找 → 找不到就 `swipe_up` → 再 dump」，同时设置最大次数，避免死循环。

## 面试题

**Q：移动端自动化的「不稳定」主要来自哪里？**

A：异步渲染（界面没出来）、输入法（文本被改写）、动画（坐标在动）、网络（结果延迟）。四类各有对策：等待、切输入法、等动画结束、轮询结果。

**Q：怎么保证输入类用例可重复？**

A：每次先清空并确认已聚焦，输入后读回校验（或校验长度），不依赖上一条用例留下的内容。

**Q：坐标点击和控件点击怎么选？**

A：控件可点就点控件；控件不可点但父容器可点时点父容器；只有在 dump 拿不到结构（WebView、游戏）时才用坐标，并按屏幕比例换算。

## 延伸知识

- `adb shell input keyevent KEYCODE_MOVE_END`：光标移到行尾，配合删除更可靠。
- `adb shell settings put secure default_input_method <ime>`：切换输入法。
- `adb shell wm size` 得到的宽高，是坐标换算的基准。
- 长按也可以用于「拖拽排序」：起点终点不同、时长较长。
