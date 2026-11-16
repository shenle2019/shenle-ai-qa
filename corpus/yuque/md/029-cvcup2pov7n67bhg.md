---
title: "MidScene使用教程"
doc_id: 256211603
slug: cvcup2pov7n67bhg
book_id: 73651885
words: 15372
updated_at: 2026-04-07T06:06:05.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/cvcup2pov7n67bhg
---
# 项目自动化

# 概念

## 简介

由字节跳动公司开发的一个基于 AI 的自动化测试框架

官网地址：<https://midscenejs.com/zh/>

## 环境搭建

### 前提环境

> NodeJS 要求最低版本是 v18，最好是 v20

，安装 v18 以上版本很麻烦，不建议在 centos7 上安装 v18 或以上

### 安装

执行下面的命令，二选一即可，一般用第一个

执行成功日志如下

### 卸载

## 模型配置

官网教程：<https://midscenejs.com/zh/choose-a-model>

### 阿里云

<https://www.aliyun.com/product/tongyi?spm=a2c4g.11186623.J_4VYgf18xNlTAyFFbOuOQe.d_menu_0.574065c5W07NRT>

- 申请 key：

点击创建

## 运行示例

在一个目录中，创建如下两个文件

### .env

模型配置文件

### OPENAI\_API\_KEY 申请

申请地址：<https://bailian.console.aliyun.com/?spm=5176.29597918.J_SEsSjsNv72yRuRFS2VknO.2.71d87b0835ITPT&tab=model#/api-key>

将复制的 Key 粘贴到`.env`文件中

### 创建示例 yaml

### 运行脚本

注意图片中命令执行时所在的目录。

> 运行时，也可能出现如下错误，主要在 mac 系统可能会发生，可以使用下面的 Chrome 桥接模式来解决
>
> 也可以使用配置文件来解决，添加配置文件`puppeteer.config.js`，保持如下目录位置

- 错误 2，大模型配置找不到

- 错误 3：账号欠费了

### 查看报告

在工具打开，就需要安装插件

## 常见问题

### 使用的大模型与申请的 key 不匹配

### 不明原因问题

### yaml 中只能使用空格缩进

# 基于`yaml`测试

在 `.yaml` 文件中，有两个部分：`web/android/ios` 和 `tasks`。

`web/android/ios` 部分定义了任务的基本信息，浏览器下的自动化使用 `web` 参数（曾用参数名 `target`），安卓设备下的自动化使用 `android` 参数，二者是互斥的。

## `web` 部分

## `android` 部分

## `ios` 部分

## 全局 agent 配置

如需使用 `aiActionContext` 参数，可以通过全局的 `agent` 配置来设置：

aiActionContext 配置说明

- **适用环境**：Web、iOS 和 Android 环境都可以通过全局的 `agent` 配置来设置 `aiActionContext`
- **作用**：为 AI 模型提供背景知识，例如处理弹窗、业务介绍等常见场景

### 使用示例

## `tasks` 部分

`tasks` 部分是一个数组，定义了脚本执行的步骤。记得在每个步骤前添加 `-` 符号，表明这些步骤是个数组。

`flow` 部分的接口与 [API](https://midscenejs.com/zh/api.html) 几乎相同，除了一些参数的嵌套层级。基本使用 ai 即可，其它可能会有 bug，导致无法生效

### 使用图像提示

对于支持在提示词中附带图像的步骤，可以把提示词改写为对象，并通过设置 `images` 字段（一个包含 `name` 和 `url` 的对象数组）来附加图像。该对象包含以下字段：

- `prompt`：发送给模型的文本描述。
- `images`（可选）：提示词引用的参考图像，每一项需要提供 `name` 和 `url`。
- `convertHttpImage2Base64`（可选）：在图片链接无法公开访问时，将 HTTP 链接转换为 Base64 再发送给模型。

图片 URL 可以是本地路径、Base64 字符串或远程链接。如果图片链接无法被模型访问，请设置 `convertHttpImage2Base64: true`，Midscene 会将图像下载后以 Base64 字符串的形式发送给模型。

对于 `aiTap`、`aiHover`、`aiDoubleClick`、`aiRightClick` 等交互操作，请把文本和图像配置写在 `locate` 字段中。

对于视觉问答类步骤，例如 `aiAsk`、`aiQuery`、`aiBoolean`、`aiNumber`、`aiString`、`aiAssert`，可以直接设置 `prompt` 和 `images` 字段。

## WebUI 测试

以读书屋为演示项目

### 登录示例

### 运行在有界面(Headed)模式下

仅 `web` 场景下支持

'headed' 模式意味着浏览器窗口是可见的。默认情况下，脚本会在无界面模式下运行。

如果你想运行在有界面模式下，你可以使用 `--headed` 选项。此外，如果你想在脚本运行结束后保持浏览器窗口打开，你可以使用 `--keep-window` 选项。`--keep-window` 选项会自动开启 `--headed` 模式。

headed 模式会消耗更多资源，所以建议你仅在本地使用。

## Android 测试

### 前置条件

### 示例

​

## IOS 测试

### 前置条件

- 项目准备

如下图中的 app，如果不会开发，可以使用 Trae 这个 ai 工具进行开发。但必须要有 mac 电脑才可以。安装 xcode 就可以开发了

- 环境搭建

环境没有搭建好，会报错如下。解决办法可以直接在 trae 中将错误发给 ai，然后让 ai 来修复

- `npm install -g appium-webdriveragent`：执行命令
- 修改过程中，可能会出现如下图中的警告，这是因为 nodejs18 导致的，可以不用管，也可以使用 nodejs20，就不会有了

修复过程会比如久，要留意是否需要让用户输入的内容。基本上全程自动操作

- 然后在浏览器中输入，下图中的地址，可以看到如下效果

接下来就可以尝试下面的示例了。

### 示例

运行之前一定先启动 WebDriverAgent 这个应用。

如果没有启动，会报错如下

保证有`.env`文件

​

如果有错误就发给 ai 给解决修复。中间可能会需要进行多次。多积累经验

# Chrome 插件

## 安装插件

1. 前往 Chrome 扩展商店安装 Midscene 扩展：[Midscene](https://chromewebstore.google.com/detail/midscene/gbldofcpkknbggpkmbdaefngejllnief)，需要 vpn 才可以
2. 下载安装包手动安装（**无法获得自动更新**）：[Releases](https://github.com/web-infra-dev/midscene/releases)，离线包

### 商店下载

国内无法访问需要翻墙

> 出现如下情况就是无法访问，需要开启 vpn 才可以。如果没有就用另一种方式

## 离线包安装

离线包下载地址：<https://github.com/web-infra-dev/midscene/releases>

如果无法打开，就在群里问老师要

下面是更新的版本，可以使用

无法下载就问老师要。

## 配置与使用

按下图方式打开插件

### 配置

模型选择与 key 的申请在前面已经介绍过了

### PlayGround 使用

演示网站地址：<http://novel.hctestedu.com/user/login.html>

## 桥接模式使用

使用 Midscene 的 Chrome 插件桥接模式（Bridge Mode），你可以用本地脚本控制桌面版本的 Chrome。你的脚本可以连接到新标签页或当前已激活的标签页。

使用桌面版本的 Chrome 可以让你复用已有的 cookie、插件、页面状态等。你可以使用自动化脚本与操作者互动，来完成你的任务。

开启桥接模式，可以通过代码脚本来操作，也可以通过 ai 工具的 mcp 来操作，还有 yaml 来运行

### yaml 的桥接模式

### mcp 使用（了解）

在此通过`trae`工具来演示

安装`Midscene MCP`

复制以下配置到输入框加

将上面的内容添加到对话框加，然后按回车执行

执行日志如下图

浏览器会陆续执行操作

### TS 代码使用

- 安装依赖

在终端中进入项目路径，然后执行依赖下载命令

- 编辑测试脚本

- 添加`.env`配置文件

- 浏览器要启动桥接模式
- 运行脚本

执行成功日志如下，执行过程可能要 20 秒左右，看实际情况

> 当桥接模式的端口被其它程序占用了，就会报错如下。解决办法在 chrome 中重新打开桥接模式

浏览器执行效果和日志如下

TS 的使用，需要有 TypeScript 基础才能进入高级使用，更多的内容查看后面的 Api 参考部分

# 集成到 Playwright

## 安装依赖

执行终端命令一定要注意终端所在的目录

## Demo 演示

- 编写脚本

- 添加`.env`配置文件

## 运行

在脚本所在的目录执行命令，`npx tsx demo.ts`

报告内容

# Api 参考

## 构造器

Midscene 中每个 Agent 都有自己的构造函数。

- 在 Puppeteer 中，使用 [PuppeteerAgent](https://midscenejs.com/zh/integrate-with-puppeteer.html)
- 在桥接模式（Bridge Mode）中，使用 [AgentOverChromeBridge](https://midscenejs.com/zh/bridge-mode-by-chrome-extension.html#constructor)
- 在 Android 中，使用 [AndroidAgent](https://midscenejs.com/zh/integrate-with-android.html)
- 如果你为自定义界面创建 GUI Agent，请参考 [集成到任意界面](https://midscenejs.com/zh/integrate-with-any-interface.html)

这些 Agent 有一些相同的构造参数：

- `generateReport: boolean`: 如果为 true，则生成报告文件。默认值为 true。
- `reportFileName: string`: 报告文件的名称，默认值由 midscene 内部生成。
- `autoPrintReportMsg: boolean`: 如果为 true，则打印报告消息。默认值为 true。
- `cacheId: string | undefined`: 如果配置，则使用此 cacheId 保存或匹配缓存。默认值为 undefined，也就是不启用缓存。
- `actionContext: string`: 调用 `agent.aiAction()` 时，发送给 AI 模型的背景知识，比如 '有 cookie 对话框时先关闭它'，默认值为空。
- `onTaskStartTip: (tip: string) => void | Promise<void>`：可选回调，在每个子任务执行开始前收到一条可读的任务描述提示。默认值为 undefined。

在 Playwright 和 Puppeteer 中，有以下共同的参数：

- `forceSameTabNavigation: boolean`: 如果为 true，则限制页面在当前 tab 打开。默认值为 true。
- `waitForNavigationTimeout: number`: 在页面跳转后等待页面加载完成的超时时间，默认值为 5000ms，设置为 0 则不做等待。

在 Puppeteer 中，还有以下参数：

- `waitForNetworkIdleTimeout: number`: 在执行每个操作后等待网络空闲的超时时间，默认值为 2000ms，设置为 0 则不做等待。

## 交互方法

这些是 Midscene 中各类 Agent 的主要 API。

自动规划 v.s. 即时操作

在 Midscene 中，你可以选择使用自动规划（Auto Planning）或即时操作（Instant Action）。

- `agent.ai()` 是自动规划（Auto Planning）：Midscene 会自动规划操作步骤并执行。它更智能，更像流行的 AI Agent 风格，但可能较慢，且效果依赖于 AI 模型的质量。
- `agent.aiTap()`, `agent.aiHover()`, `agent.aiInput()`, `agent.aiKeyboardPress()`, `agent.aiScroll()`, `agent.aiDoubleClick()`, `agent.aiRightClick()` 是即时操作（Instant Action）：Midscene 会直接执行指定的操作，而 AI 模型只负责底层任务，如定位元素等。这种接口形式更快、更可靠。当你完全确定自己想要执行的操作时，推荐使用这种接口形式。

### `agent.aiAction()` 或 `.ai()`

这个方法允许你通过自然语言描述一系列 UI 操作步骤。Midscene 会自动规划这些步骤并执行。

- 类型

- 参数：

- `prompt: string` - 用自然语言描述的操作内容
- `options?: Object` - 可选，一个配置对象，包含：

- `cacheable?: boolean` - 当启用 [缓存功能](https://midscenejs.com/zh/caching.html) 时，是否允许缓存当前 API 调用结果。默认值为 true

- 返回值：

- 返回一个 Promise。当所有步骤执行完成时解析为 void；若执行失败，则抛出错误。

- 示例：

TIP

在实际运行时，Midscene 会将用户指令规划（Planning）成多个步骤，然后逐步执行。如果 Midscene 认为无法执行，将抛出一个错误。

为了获得最佳效果，请尽可能提供清晰、详细的步骤描述。具体可以参考这篇文档：[编写提示词的技巧](https://midscenejs.com/zh/prompting-tips.html)

关联文档：

- [选择 AI 模型](https://midscenejs.com/zh/choose-a-model.html)

### `agent.aiTap()`

点击某个元素。

- 类型

- 参数：

- `locate: string | Object` - 用自然语言描述的元素定位，或[使用图片作为提示词](https://midscenejs.com/zh/api.html#%E4%BD%BF%E7%94%A8%E5%9B%BE%E7%89%87%E4%BD%9C%E4%B8%BA%E6%8F%90%E7%A4%BA%E8%AF%8D)。
- `options?: Object` - 可选，一个配置对象，包含：

- `deepThink?: boolean` - 是否开启深度思考。如果为 true，Midscene 会调用 AI 模型两次以精确定位元素。默认值为 false
- `xpath?: string` - 目标元素的 xpath 路径，用于执行当前操作。如果提供了这个 xpath，Midscene 会优先使用该 xpath 来找到元素，然后依次使用缓存和 AI 模型。默认值为空
- `cacheable?: boolean` - 当启用 [缓存功能](https://midscenejs.com/zh/caching.html) 时，是否允许缓存当前 API 调用结果。默认值为 true

- 返回值：

- `Promise<void>`

- 示例：

### `agent.aiHover()`

仅在 web 页面中可用，在 Android 下不可用

鼠标悬停某个元素上。

- 类型

- 参数：

- `locate: string | Object` - 用自然语言描述的元素定位，或[使用图片作为提示词](https://midscenejs.com/zh/api.html#%E4%BD%BF%E7%94%A8%E5%9B%BE%E7%89%87%E4%BD%9C%E4%B8%BA%E6%8F%90%E7%A4%BA%E8%AF%8D)。
- `options?: Object` - 可选，一个配置对象，包含：

- `deepThink?: boolean` - 是否开启深度思考。如果为 true，Midscene 会调用 AI 模型两次以精确定位元素。默认值为 false
- `xpath?: string` - 目标元素的 xpath 路径，用于执行当前操作。如果提供了这个 xpath，Midscene 会优先使用该 xpath 来找到元素，然后依次使用缓存和 AI 模型。默认值为空
- `cacheable?: boolean` - 当启用 [缓存功能](https://midscenejs.com/zh/caching.html) 时，是否允许缓存当前 API 调用结果。默认值为 true

- 返回值：

- `Promise<void>`

- 示例：

### `agent.aiInput()`

在某个元素中输入文本。

- 类型

- 参数：

- `text: string` - 要输入的文本内容。使用空字符串可以清空输入框。
- `locate: string | Object` - 用自然语言描述的元素定位，或使用图片作为提示词。
- `options?: Object` - 可选，一个配置对象，包含：

- `deepThink?: boolean` - 是否开启深度思考。如果为 true，Midscene 会调用 AI 模型两次以精确定位元素。默认值为 false
- `xpath?: string` - 目标元素的 xpath 路径，用于执行当前操作。如果提供了这个 xpath，Midscene 会优先使用该 xpath 来找到元素，然后依次使用缓存和 AI 模型。默认值为空
- `cacheable?: boolean` - 当启用 缓存功能 时，是否允许缓存当前 API 调用结果。默认值为 true
- `autoDismissKeyboard?: boolean` - 如果为 true，则键盘会在输入文本后自动关闭，仅在 Android 中有效。默认值为 true。

- 返回值：

- `Promise<void>`

- 示例：

### `agent.aiKeyboardPress()`

按下键盘上的某个键。

- 类型

- 参数：

- `key: string` - 要按下的键，如 `Enter`、`Tab`、`Escape` 等。不支持组合键。
- `locate?: string | Object` - 用自然语言描述的元素定位，，或使用图片作为提示词。
- `options?: Object` - 可选，一个配置对象，包含：

- `deepThink?: boolean` - 是否开启深度思考。如果为 true，Midscene 会调用 AI 模型两次以精确定位元素。默认值为 false
- `xpath?: string` - 目标元素的 xpath 路径，用于执行当前操作。如果提供了这个 xpath，Midscene 会优先使用该 xpath 来找到元素，然后依次使用缓存和 AI 模型。默认值为空
- `cacheable?: boolean` - 当启用 缓存功能 时，是否允许缓存当前 API 调用结果。默认值为 true

- 返回值：

- `Promise<void>`

- 示例：

### `agent.aiScroll()`

滚动页面或某个元素。

- 类型

- 参数：

- `scrollParam: PlanningActionParamScroll` - 滚动参数

- `direction: 'up' | 'down' | 'left' | 'right'` - 滚动方向。不论是 Android 还是 Web，这里的滚动方向都是指页面哪个方向的内容会进入屏幕。比如当滚动方向是 `down` 时，页面下方被隐藏的内容会从屏幕底部开始逐渐向上露出。
- `scrollType: 'once' | 'untilBottom' | 'untilTop' | 'untilRight' | 'untilLeft'` - 滚动类型
- `distance: number` - 滚动距离，单位为像素。

- `locate?: string | Object` - 用自然语言描述的元素定位，或使用图片作为提示词。如果未传入，Midscene 会在当前鼠标位置滚动。
- `options?: Object` - 可选，一个配置对象，包含：

- `deepThink?: boolean` - 是否开启深度思考。如果为 true，Midscene 会调用 AI 模型两次以精确定位元素。默认值为 false
- `xpath?: string` - 目标元素的 xpath 路径，用于执行当前操作。如果提供了这个 xpath，Midscene 会优先使用该 xpath 来找到元素，然后依次使用缓存和 AI 模型。默认值为空
- `cacheable?: boolean` - 当启用 缓存功能 时，是否允许缓存当前 API 调用结果。默认值为 true

- 返回值：

- `Promise<void>`

- 示例：

### `agent.aiDoubleClick()`

双击某个元素。

- 类型

- 参数：

- `locate: string | Object` - 用自然语言描述的元素定位，或使用图片作为提示词。
- `options?: Object` - 可选，一个配置对象，包含：

- `deepThink?: boolean` - 是否开启深度思考。如果为 true，Midscene 会调用 AI 模型两次以精确定位元素。默认值为 false
- `xpath?: string` - 目标元素的 xpath 路径，用于执行当前操作。如果提供了这个 xpath，Midscene 会优先使用该 xpath 来找到元素，然后依次使用缓存和 AI 模型。默认值为空
- `cacheable?: boolean` - 当启用 缓存功能 时，是否允许缓存当前 API 调用结果。默认值为 true

- 返回值：

- `Promise<void>`

- 示例：

### `agent.aiRightClick()`

仅在 web 页面中可用，在 Android 下不可用

右键点击某个元素。请注意，Midscene 在右键点击后无法与浏览器原生上下文菜单交互。这个接口通常用于已经监听了右键点击事件的元素。

- 类型

- 参数：

- `locate: string | Object` - 用自然语言描述的元素定位，或使用图片作为提示词。
- `options?: Object` - 可选，一个配置对象，包含：

- `deepThink?: boolean` - 是否开启深度思考。如果为 true，Midscene 会调用 AI 模型两次以精确定位元素。默认值为 false
- `xpath?: string` - 目标元素的 xpath 路径，用于执行当前操作。如果提供了这个 xpath，Midscene 会优先使用该 xpath 来找到元素，然后依次使用缓存和 AI 模型。默认值为空
- `cacheable?: boolean` - 当启用 缓存功能 时，是否允许缓存当前 API 调用结果。默认值为 true

- 返回值：

- `Promise<void>`

- 示例：

关于

`deepThink` （深度思考）特性

`deepThink` 是一个强大的特性，它允许 Midscene 调用 AI 模型两次以精确定位元素。这在目标元素面积较小、难以和周围元素区分时非常有用。

## 数据提取

### `agent.aiAsk()`

使用此方法，你可以针对当前页面，直接向 AI 模型发起提问，并获得字符串形式的回答。

- 类型

- 参数：

- `prompt: string | Object` - 用自然语言描述的询问内容，或[使用图片作为提示词](https://midscenejs.com/zh/api.html#%E4%BD%BF%E7%94%A8%E5%9B%BE%E7%89%87%E4%BD%9C%E4%B8%BA%E6%8F%90%E7%A4%BA%E8%AF%8D)。
- `options?: Object` - 可选，一个配置对象，包含：

- `domIncluded?: boolean | 'visible-only'` - 是否向模型发送精简后的 DOM 信息，一般用于提取 UI 中不可见的属性，比如图片的链接。如果设置为 `'visible-only'`，则只发送可见的元素。默认值为 false。
- `screenshotIncluded?: boolean` - 是否向模型发送截图。默认值为 true。

- 返回值：

- 返回一个 Promise。返回 AI 模型的回答。

- 示例：

除了 `aiAsk` 方法，你还可以使用 `aiQuery` 方法，直接从 UI 提取结构化的数据。

### `agent.aiQuery()`

使用此方法，你可以直接从 UI 提取结构化的数据。只需在 `dataDemand` 中描述期望的数据格式（如字符串、数字、JSON、数组等），Midscene 即返回相应结果。

- 类型

- 参数：

- `dataDemand: T`: 描述预期的返回值和格式。
- `options?: Object` - 可选，一个配置对象，包含：

- `domIncluded?: boolean | 'visible-only'` - 是否向模型发送精简后的 DOM 信息，一般用于提取 UI 中不可见的属性，比如图片的链接。如果设置为 `'visible-only'`，则只发送可见的元素。默认值为 false。
- `screenshotIncluded?: boolean` - 是否向模型发送截图。默认值为 true。

- 返回值：

- 返回值可以是任何合法的基本类型，比如字符串、数字、JSON、数组等。
- 你只需在 `dataDemand` 中描述它，Midscene 就会给你满足格式的返回。

- 示例：

此外，我们还提供了 `aiBoolean()`, `aiNumber()`, `aiString()` 三个便捷方法，用于直接提取布尔值、数字和字符串。

### `agent.aiBoolean()`

从 UI 中提取一个布尔值。

- 类型

- 参数：

- `prompt: string` - 用自然语言描述的期望值，或[使用图片作为提示词](https://midscenejs.com/zh/api.html#%E4%BD%BF%E7%94%A8%E5%9B%BE%E7%89%87%E4%BD%9C%E4%B8%BA%E6%8F%90%E7%A4%BA%E8%AF%8D)。
- `options?: Object` - 可选，一个配置对象，包含：

- `domIncluded?: boolean | 'visible-only'` - 是否向模型发送精简后的 DOM 信息，一般用于提取 UI 中不可见的属性，比如图片的链接。如果设置为 `'visible-only'`，则只发送可见的元素。默认值为 false。
- `screenshotIncluded?: boolean` - 是否向模型发送截图。默认值为 true。

- 返回值：

- 返回一个 Promise。当 AI 返回结果时解析为布尔值。

- 示例：

### `agent.aiNumber()`

从 UI 中提取一个数字。

- 类型

- 参数：

- `prompt: string | Object` - 用自然语言描述的期望值，或[使用图片作为提示词](https://midscenejs.com/zh/api.html#%E4%BD%BF%E7%94%A8%E5%9B%BE%E7%89%87%E4%BD%9C%E4%B8%BA%E6%8F%90%E7%A4%BA%E8%AF%8D)。
- `options?: Object` - 可选，一个配置对象，包含：

- `domIncluded?: boolean | 'visible-only'` - 是否向模型发送精简后的 DOM 信息，一般用于提取 UI 中不可见的属性，比如图片的链接。如果设置为 `'visible-only'`，则只发送可见的元素。默认值为 false。
- `screenshotIncluded?: boolean` - 是否向模型发送截图。默认值为 true。

- 返回值：

- 返回一个 Promise。当 AI 返回结果时解析为数字。

- 示例：

### `agent.aiString()`

从 UI 中提取一个字符串。

- 类型

- 参数：

- `prompt: string | Object` - 用自然语言描述的期望值，或[使用图片作为提示词](https://midscenejs.com/zh/api.html#%E4%BD%BF%E7%94%A8%E5%9B%BE%E7%89%87%E4%BD%9C%E4%B8%BA%E6%8F%90%E7%A4%BA%E8%AF%8D)。
- `options?: Object` - 可选，一个配置对象，包含：

- `domIncluded?: boolean | 'visible-only'` - 是否向模型发送精简后的 DOM 信息，一般用于提取 UI 中不可见的属性，比如图片的链接。如果设置为 `'visible-only'`，则只发送可见的元素。默认值为 false。
- `screenshotIncluded?: boolean` - 是否向模型发送截图。默认值为 true。

- 返回值：

- 返回一个 Promise。当 AI 返回结果时解析为字符串。

- 示例：

## 更多方法

### `agent.aiAssert()`

通过自然语言描述一个断言条件，让 AI 判断该条件是否为真。当条件不满足时，SDK 会抛出错误，并在错误信息中追加 AI 返回的详细原因。

- 类型

- 参数：

- assertion: string | Object - 用自然语言描述的断言条件，或[使用图片作为提示词](https://midscenejs.com/zh/api.html#%E4%BD%BF%E7%94%A8%E5%9B%BE%E7%89%87%E4%BD%9C%E4%B8%BA%E6%8F%90%E7%A4%BA%E8%AF%8D)。
- errorMsg?: string - 当断言失败时附加的可选错误提示信息。
- options?: Object - 可选，一个配置对象，包含：

- `domIncluded?: boolean | 'visible-only'` - 是否向模型发送精简后的 DOM 信息，一般用于提取 UI 中不可见的属性，比如图片的链接。如果设置为 `'visible-only'`，则只发送可见的元素。默认值为 false。
- `screenshotIncluded?: boolean` - 是否向模型发送截图。默认值为 true。

- 返回值：

- 返回一个 Promise。当断言成功时解析为 void；若断言失败，则抛出一个错误，错误信息包含 `errorMsg` 以及 AI 生成的原因。

- 示例：

TIP

断言在测试脚本中非常重要。为了降低因 AI 幻觉导致错误断言的风险（例如遗漏错误），你也可以使用 `.aiQuery` 加上常规的 JavaScript 断言来替代 `.aiAssert`。

例如，你可以这样替代上面的断言代码：

### `agent.aiLocate()`

通过自然语言描述一个元素的定位。

- 类型

- 参数：

- `locate: string | Object` - 用自然语言描述的元素定位，或[使用图片作为提示词](https://midscenejs.com/zh/api.html#%E4%BD%BF%E7%94%A8%E5%9B%BE%E7%89%87%E4%BD%9C%E4%B8%BA%E6%8F%90%E7%A4%BA%E8%AF%8D)。
- `options?: Object` - 可选，一个配置对象，包含：

- `deepThink?: boolean` - 是否开启深度思考。如果为 true，Midscene 会调用 AI 模型两次以精确定位元素。默认值为 false
- `xpath?: string` - 目标元素的 xpath 路径，用于执行当前操作。如果提供了这个 xpath，Midscene 会优先使用该 xpath 来找到元素，然后依次使用缓存和 AI 模型。默认值为空
- `cacheable?: boolean` - 当启用 [缓存功能](https://midscenejs.com/zh/caching.html) 时，是否允许缓存当前 API 调用结果。默认值为 true

- 返回值：

- 返回一个 Promise。当元素定位成功时解析为元素定位信息。

- 示例：

### `agent.aiWaitFor()`

等待某个条件达成。考虑到 AI 服务的成本，检查间隔不会超过 `checkIntervalMs` 毫秒。

- 类型

- 参数：

- `assertion: string` - 用自然语言描述的断言条件
- `options?: object` - 可选的配置对象

- `timeoutMs?: number` - 超时时间（毫秒），默认为 15000
- `checkIntervalMs?: number` - 检查间隔（毫秒），默认为 3000

- 返回值：

- 返回一个 Promise。当断言成功时解析为 void；若超时，则抛出错误。

- 示例：

TIP

考虑到 AI 服务的时间消耗，`.aiWaitFor` 并不是一个特别高效的方法。使用一个普通的 `sleep` 可能是替代 `waitFor` 的另一种方式。

### `agent.runYaml()`

执行一个 YAML 格式的自动化脚本。脚本中的 `tasks` 部分会被执行，并返回所有 `.aiQuery` 调用的结果。

- 类型

- 参数：

- `yamlScriptContent: string` - YAML 格式的脚本内容

- 返回值：

- 返回一个包含 `result` 属性的对象，其中包含所有 `aiQuery` 调用的结果

- 示例：

TIP

更多关于 YAML 脚本的信息，请参考 [Automate with Scripts in YAML](https://midscenejs.com/zh/automate-with-scripts-in-yaml.html)。

### `agent.setAIActionContext()`

设置在调用 `agent.aiAction()` 或 `agent.ai()` 时，发送给 AI 模型的背景知识。这个设置会覆盖之前的设置。

对于即时操作类型的 API，比如 `aiTap()`，这个设置不会生效。

- 类型

- 参数：

- `actionContext: string` - 要发送给 AI 模型的背景知识。

- 示例：

### `agent.evaluateJavaScript()`

仅在 web 页面中可用，在 Android 下不可用

这个方法允许你在 web 页面上下文中执行一段 JavaScript 代码，并返回执行结果。

- 类型

- 参数：

- `script: string` - 要执行的 JavaScript 代码。

- 返回值：

- 返回执行结果。

- 示例：

### `agent.logScreenshot()`

在报告文件中记录当前截图，并添加描述。

- 类型

- 参数：

- `title?: string` - 可选，截图的标题，如果未提供，则标题为 'untitled'。
- `options?: Object` - 可选，一个配置对象，包含：

- `content?: string` - 截图的描述。

- 返回值：

- `Promise<void>`

- 示例：

### `agent.freezePageContext()`

冻结当前页面上下文，使后续所有的操作都复用同一个页面快照，避免多次重复获取页面状态。在执行大量并发操作时，它可以显著提升性能。

一些注意点：

- 通常情况下，你不需要使用这个方法，除非你确定“页面状态获取”是脚本性能瓶颈。
- 需要及时调用 `agent.unfreezePageContext()` 来恢复实时页面状态。
- 不要在交互类操作中使用这个方法，它会让 AI 模型无法感知到页面的最新状态，产生令人困惑的错误。
- 类型

- 返回值：

- `Promise<void>`

- 示例：

TIP

在报告中，使用冻结上下文的操作会在 Insight tab 中显示 🧊 图标。

### `agent.unfreezePageContext()`

解冻页面上下文，恢复使用实时的页面状态。

- 类型

- 返回值：

- `Promise<void>`

### `agent._unstableLogContent()`

从报告文件中获取日志内容。日志内容的结构可能会在未来发生变化。

- 类型

- 返回值：

- 返回一个对象，包含日志内容。

- 示例：

## 属性

### `.reportFile`

报告文件的路径。

## 更多配置

### 在运行时设置环境变量

你可以通过 `overrideAIConfig` 方法在运行时设置环境变量。

### 打印 AI 性能信息

设置 `DEBUG=midscene:ai:profile:stats` 环境变量，你可以看到每次调用 AI 的时间和 token 数量。

### 自定义运行产物目录

设置 `MIDSCENE_RUN_DIR` 变量，你可以自定义运行产物目录。

### 自定义重新规划循环限制

设置 `MIDSCENE_REPLANNING_CYCLE_LIMIT` 变量，你可以自定义在执行操作(`aiAction`)时允许的最大重新规划循环次数。

### 使用 LangSmith

LangSmith 是一个用于调试大语言模型的平台。想要集成 LangSmith，请按以下步骤操作：

启动 Midscene 后，你应该会看到类似如下的日志：

## 高级功能

### 使用图片作为提示词

你可以在提示词中使用图片作为补充，来描述无法通过自然语言表达的内容。

使用图片作为提示词时，提示词的参数格式如下：

- 示例一：使用图片描述点击位置

- 示例二：使用图片进行页面断言

**图片尺寸的注意事项**

在提示词中使用图片时，可能需要关注模型提供商对图片体积和尺寸的要求，过大（比如超过 10M）或过小（比如小于 10 像素）的图片都有可能导致模型调用时出现报错，具体的限制请以你所使用模型提供商的文档为准。

​

# Android 测试

## android mcp（了解）

- 配置，增加`"MIDSCENE_MCP_ANDROID_MODE": "true",`到配置中

### 安装依赖

- `npm install @midscene/android`

## android playground

- 启动 playground

## 与 Android adb 集成

### 安装依赖

### 编写脚本

编写下方代码，保存为 `./demo.ts`

### 运行

使用 `tsx` 来运行

### 查看运行报告

当上面的命令执行成功后，会在下图所示目录中生成报告

### `AndroidDevice` 的构造函数

AndroidDevice 的构造函数支持以下参数：

- `deviceId: string` - 设备 id
- `opts?: AndroidDeviceOpt` - 可选参数，用于初始化 AndroidDevice 的配置

- `autoDismissKeyboard?: boolean` - 可选参数，是否在输入文本后自动关闭键盘。默认值为 true。
- `keyboardDismissStrategy?: 'esc-first' | 'back-first'` - 可选参数，关闭键盘的策略。'esc-first' 优先尝试 ESC 键，如果键盘仍存在则尝试返回键。'back-first' 优先尝试返回键，如果键盘仍存在则尝试 ESC 键。默认值为 'esc-first'。
- `androidAdbPath?: string` - 可选参数，用于指定 adb 可执行文件的路径。
- `remoteAdbHost?: string` - 可选参数，用于指定远程 adb 主机。
- `remoteAdbPort?: number` - 可选参数，用于指定远程 adb 端口。
- `imeStrategy?: 'always-yadb' | 'yadb-for-non-ascii'` - 可选参数，控制 Midscene 何时调用 [yadb](https://github.com/ysbing/YADB) 来输入文本。默认值为 'always-yadb'。
- `displayId?: number` - 可选参数，用于指定要使用的显示器 ID。默认值为 undefined，表示使用当前显示器。

### Android Agent 上的更多接口

除了 [API 参考](https://midscenejs.com/zh/api.html) 中的通用 Agent 接口，AndroidAgent 还提供了一些其他接口：

#### [#](https://midscenejs.com/zh/integrate-with-android.html#agentlaunch)`agent.launch()`

启动一个网页或原生页面。

- 类型

- 参数：

- `uri: string` - 要打开的 uri，可以是网页 url 或原生 app 的 package name 或 activity name，如果存在 activity name，则以 / 分隔（例如：com.android.settings/.Settings）

- 返回值：

- `Promise<void>`

- 示例：

#### `agentFromAdbDevice()`

从已连接的 adb 设备中，创建一个 AndroidAgent。

- 类型

- 参数：

- `deviceId?: string` - 可选参数，要连接的 adb 设备 id，如果未传入，则使用第一个连接的设备
- `opts?: PageAgentOpt & AndroidDeviceOpt` - 可选参数，用于初始化 AndroidAgent 的配置，其中 PageAgentOpt 参考 [构造器](https://midscenejs.com/zh/api.html)，AndroidDeviceOpt 的配置值参考 [AndroidDevice 的构造函数](https://midscenejs.com/zh/integrate-with-android.html#androiddevice-的构造函数)

- 返回值：

- `Promise<AndroidAgent>` 返回一个 AndroidAgent 实例

- 示例：

#### `getConnectedDevices()`

获取所有连接的 Android 设备。

- 类型

- 返回值：

- `Promise<Device[]>` 返回一个 Device 数组

- 示例：

## 扩展自定义交互动作

使用 `customActions` 选项，结合 `defineAction` 定义的自定义交互动作，可以扩展 Agent 的动作空间。这些动作会追加在内置动作之后，方便 Agent 在规划阶段调用。

# IOS 测试

## iOS Playground（了解）

### 环境配置

- 启动 Playground

启动成功后，自动在浏览器中打开如下页面，如果没有打开，可以将图中的地址输入到浏览器中，`localhost:5800`

- 配置环境

### 示例

## IOS 集成

先看前面 2.8 节中的前置条件，有环境搭建部分。

### 安装依赖

成功日志如下

### 编写脚本

- 编写下方代码，保存为 `./demo.ts`

- `.env`

### 运行

使用 `tsx` 来运行

### 查看报告

按上面图片中的路径找到报告，并在浏览器中打开

## 构造函数与接口

### `IOSDevice` 的构造函数

IOSDevice 的构造函数支持以下参数：

- `opts?: IOSDeviceOpt` - 可选参数，用于初始化 IOSDevice 的配置

- `wdaPort?: number` - 可选参数，WebDriverAgent 端口。默认值为 8100。
- `wdaHost?: string` - 可选参数，WebDriverAgent 主机。默认值为 'localhost'。
- `autoDismissKeyboard?: boolean` - 可选参数，是否在输入文本后自动关闭键盘。默认值为 true。
- `customActions?: DeviceAction<any>[]` - 可选参数，自定义设备动作列表。

### iOS Agent 上的更多接口

#### `agent.launch()`

启动一个网页或原生 iOS 应用。

- 类型

- 参数：

- `uri: string` - 要打开的 uri，可以是网页 url、原生 app 的 bundle identifier 或自定义 URL scheme

- 返回值：

- `Promise<void>`

- 示例：

#### `agentFromWebDriverAgent()` (推荐)

通过连接 WebDriverAgent 服务创建 IOSAgent，这是最简便的方式。

- 类型

- 参数：

- `opts?: PageAgentOpt & IOSDeviceOpt` - 可选参数，用于初始化 IOSAgent 的配置，其中 PageAgentOpt 参考 构造器，IOSDeviceOpt 的配置值参考 IOSDevice 的构造函数

- 返回值：

- `Promise<IOSAgent>` 返回一个 IOSAgent 实例

- 示例：

## 扩展自定义交互动作

使用 `customActions` 选项，结合 `defineAction` 定义的自定义交互动作，可以扩展 Agent 的动作空间。这些动作会追加在内置动作之后，方便 Agent 在规划阶段调用。
