---
title: "安卓原生的uiautomator ，怎么获取微信中打开的拼多多链接，新页面的ui元素"
doc_id: 256211001
slug: in5mv4909wfsm7eg
book_id: 73651885
words: 1071
updated_at: 2026-02-06T06:53:18.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/in5mv4909wfsm7eg
---
以下是使用安卓原生的 uiautomator 来获取微信中打开的拼多多链接新页面的 UI 元素的步骤：

### 解决思路

1. 确保设备已连接到开发计算机，并且 ADB 工具已正确安装和配置。
2. 使用 `uiautomatorviewer` 工具来查看 UI 元素的层次结构和属性，以便确定元素的关键信息，如资源 ID、文本内容、类名等。
3. 通过编写 `uiautomator` 测试脚本，使用 Java 语言编写代码，调用 `UiDevice`、`UiObject` 等类来查找和操作相应的 UI 元素。

### 代码示例

### 代码解释

1. **导入必要的类**：

- `android.os.RemoteException`：处理远程操作异常。
- `InstrumentationRegistry`：获取测试环境的 `Instrumentation` 实例。
- `UiDevice`：表示设备，可用于操作设备上的 UI 元素。
- `UiObject` 和 `UiObject2`：用于查找和操作 UI 元素。
- `UiSelector`：用于创建查找元素的选择器。
- `Until`：提供等待条件的工具类。
- `org.junit.Before` 和 `org.junit.Test`：用于 JUnit 测试框架，`Before` 注解表示在测试方法执行前的操作，`Test` 注解表示测试方法。

1. `setUp` **方法**：

- 获取 `UiDevice` 实例，并等待设备空闲一段时间，确保设备准备好进行操作。

1. `testGetPinduoduoLinkElements` **方法**：

- 使用 `mDevice.wait` 等待微信打开拼多多链接的页面加载完成，等待条件是查找微信包名 `com.tencent.mm` 的深度为 0 的元素，超时时间为 10 秒。
- 使用 `By.textContains` 方法查找包含 "拼多多" 文本的元素，得到 `UiObject2` 实例。
- 如果元素存在，输出其文本内容，并可以执行点击操作。
- 可以继续使用 `By.textContains` 查找其他元素。
- 同时，使用 `UiObject` 和 `UiSelector` 提供另一种查找元素的方式，如果元素存在，输出其文本内容。

### 运行代码

1. 将上述代码保存为一个 Java 文件，例如 `WeChatPinduoduoTest.java`。
2. 确保设备已连接并处于开发者模式，开启 USB 调试。
3. 使用 `adb` 命令将测试代码推送到设备上，例如：

1. 编译并运行测试代码，可使用 Android 的测试框架，例如：

### 注意事项

1. 你可能需要根据拼多多页面的实际 UI 元素特征修改查找元素的方式，如使用不同的 `By` 条件，如 `By.resId`（根据资源 ID）、`By.desc`（根据描述）等。
2. 不同的微信版本和拼多多版本可能会导致 UI 元素有所不同，需要灵活调整代码。
3. 测试代码可能需要在合适的测试环境中运行，并且可能需要适当的权限，确保已正确配置测试环境和设备权限。

上述代码是一个基本的示例，实际使用时，你需要根据具体情况进行修改和扩展，以准确获取和操作拼多多页面的 UI 元素。
