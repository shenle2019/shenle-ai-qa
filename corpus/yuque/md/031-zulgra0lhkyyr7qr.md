---
title: "Openclaw使用教程"
doc_id: 261565632
slug: zulgra0lhkyyr7qr
book_id: 73651885
words: 27471
updated_at: 2026-03-28T08:45:55.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/zulgra0lhkyyr7qr
---
# 概述

## 简介

官网：<https://docs.openclaw.ai/zh-CN>

OpenClaw 是一款**开源的本地优先 AI 智能体执行框架**（曾用名 **Clawdbot、Moltbot**），由奥地利开发者 Peter Steinberger 于 2025 年 11 月启动，核心定位是 “给大语言模型装上‘手’和‘脚’”，让 AI 不仅能对话，更能直接操控设备完成具体任务，官方口号为 “The AI that actually does things”（真正能做事的 AI）。

其核心特点的通俗解读的如下：

1. 开源免费：源码公开，可自由修改、二次开发，无官方收费项目，支持本地私有化部署，数据存储在用户自身设备，隐私保护更强；
2. 低门槛易上手：无需编程基础，支持无代码 / 低代码操作，可通过自然语言下达指令，自动拆解复杂任务并执行，普通人也能快速使用；
3. 功能实用：核心是自动化执行，可实现文件整理、数据处理、截图录屏、场景演示等多种操作，还能对接多种通讯工具和 AI 模型，适配个人办公、日常辅助等多场景；
4. 区别于传统 AI：与 ChatGPT 等纯对话 AI 不同，OpenClaw 侧重 “执行” 而非 “问答”，能替代人工完成重复性流程化工作，真正解放双手。

## 安装

### Nodejs 中安装

> nodejs 最低版本要求是 24。本教程中使用的是 24 版本
>
> 如果本地没有安装 Nodejs，通过此教程进行安装，

> 配置了国内下载源，安装时间差不多用了 10 分钟，这个耐心等待就好了

### 验证安装

安装完成后，在 cmd 中执行`openclaw -h`，可以看到如下效果

# 基本使用

## 配置 Openclaw

第一次启动前，需要先通过`Openclaw onboard`命令来进行配置，界面如下

### 大模型配置

这里演示使用 MiniMax 大模型，按下面的图片中选择操作

> 有想安装的就通过 space 键来选中，按 enter 来提交，上下键进行切换

> 暂时不用，按一下 space，再按 enter 即可

### 配置完成后日志

> 之前会自动打开浏览器。记住浏览器要比较新才可以，否则打不开。

如果忘记了 token 就可以在概览界面中查看，比如第一次在 chrome 中打开了上面的地址，后面忘记了，在 firefox 中浏览器打开时，如果忘记了 token 就无法访问。此时就可以在概览中查看 token，也可以去配置文件中查找，后面讲解

如下在 firefox 中打开浏览器后，因为没有传入 token，界面就会如下

### Openclaw 配置文件

在第一次配置完 Openclaw 后，会在用户目录下产生一个配置文件。本教程的位置如下图

> 如果不知道配置文件在哪里，可以使用命令查找`openclaw config file`

可以直接在配置文件中修改一些内容，再重启 Openclaw 就能生效。这也是为什么在前面配置时，随便填写一些内容的原因。下一节就学习如何配置大模型。

下面是就是 token 在`openclaw.json`配置文件中的位置

## 大模型配置

要教程中通过阿里云大模型演示

### 登录阿里云百炼平台

1. 打开浏览器，访问阿里云百炼官网：<https://bailian.aliyun.com/>
2. 点击右上角【登录】按钮，输入阿里云账号及密码完成登录

### 获取 API-Key

1. 登录成功后，进入大模型服务平台百炼控制台 (<https://bailian.console.aliyun.com/#/home>)

1. 在控制台顶部导航栏选择【模型】，左侧导航栏依次选择【密钥管理】->【API-Key 管理】

1. 若密钥管理中无 API Key 记录，执行创建操作

1. 生成成功后，可在列表中查看已创建的 API-Key

1. 应用 API-KEY 时，点击如图所示的复制按钮

### 获取语言模型和视觉语言模型信息

1. 在控制台首页，点击顶部导航栏【模型】->【语音模型】

1. 模型名称获取：在模型列表中，点击【查看详情】进入模型详情页

- 滚动到页面底部，可以看到模型的地址

### 修改配置文件

修改`openclaw.json`中的配置，下图红框中的内容自己添加上去，图片后面有对应的内容，可以直接复制，记得修改 apiKey

### 检查配置文件

修改完配置文件后，建议通过`openclaw doctor`命令来检查配置文件是否有错误

### 重启 Openclaw

先通过`Ctrl+C`命令关闭之前启动的 Openclaw，然后通过`openclaw gateway start`启动 Openclaw 即可。命令日志如下

启动完成后，可以在浏览器打开对应的网页，然后就可以直接进行聊天了

## Openclaw.json 配置文件简介

下面是`Openclaw.json`完整说明，不要复制下面的内容。也可以不看

### 老师的 openclaw.json

至此 openclaw.json 的配置文件内容如下，学员可以直接复制替换自己的 openclaw.json 中的内容。

## 基础设置

在聊天使用之前，可以给 Openclaw 设置一些基本信息，直接通过对话设置即可。

设置的内容对应着 USER.md 这个文档

IDENTITY.md 对应着智能体的身份信息

在 `agents.defaults.workspace` 内，OpenClaw 期望以下用户可编辑的文件：

- `AGENTS.md` — 操作指令 + “记忆”
- `SOUL.md` — 人设、边界、语气
- `TOOLS.md` — 用户维护的工具说明（例如 `imsg`、`sag`、约定）
- `BOOTSTRAP.md` — 一次性首次运行仪式（完成后删除）
- `IDENTITY.md` — 智能体名称/风格/表情
- `USER.md` — 用户档案 + 偏好称呼

在新会话的第一轮，OpenClaw 将这些文件的内容直接注入智能体上下文。空文件会被跳过。大文件会被修剪和截断并添加标记，以保持提示词精简（阅读文件获取完整内容）。如果文件缺失，OpenClaw 会注入一行”文件缺失”标记（`openclaw setup` 将创建安全的默认模板）。`BOOTSTRAP.md` 仅在**全新工作区**（没有其他引导文件存在）时创建。如果你在完成仪式后删除它，后续重启不应重新创建。

## 概览

## 频道

这里查看配置的聊天频道(channels)。

## 实例

实例查看。一个网关启动成功后即为一个实例。

1. **连接其他设备作为节点**

- 在其他电脑/服务器上安装 OpenClaw
- 配置连接到你的网关
- 它们会自动出现在实例列表中

在另一个浏览器打开就会发现实例增多了

## 会话

### 会话（Sessions）

- **含义**：这是 OpenClaw 的**对话上下文管理页面**。
- **作用**：所有跟 AI 的聊天、工具调用、任务规划，都会形成一个 “会话”。你可以在这里管理所有会话，**新建、删除、修改配置**。

### Active (minutes) / Limit

- **Active (minutes)**：筛选最近多少分钟内活跃的会话。
- **Limit**：限制显示会话数量上限（图中是 120）。

### Include global / Include unknown

- **Include global**：包含全局会话（已勾选）。
- **Include unknown**：包含未知来源的会话（未勾选）。

## 使用情况

点击 Refresh 按钮下面才会有数据出现

## 定时任务

- 查看定时任务
- 创建定时任务

### 添加定时任务

可以通过界面编辑，也可以直接在聊天那里，通过对话来设置。`帮我添加一个定时任务，收集每天的ai相关新闻，然后在早上8点发给我`

## 代理（Agents）

这是 OpenClaw 管理**独立 AI 工作环境**的核心页面，每个代理都是一个隔离的 “AI 分身”。

### 创建代理

创建代理只能通过命令来创建，命令格式为：`openclaw agents add<新代理名>`

> 添加完成后，要重启 openclaw

## 日志

openclaw 的运行日志，在这里可以查看

## 文档

点击之后跳转到官方文档

# 技能管理

## 什么是 Skill

`Skill = 教给 AI 助手一套"标准化工作流程"`

## 技能分类

### WORKSPACE SKILLS（工作区技能）

- **含义**：**当前代理工作区专属的自定义技能**
- **来源**：你在代理工作区（如 `workspace`）里手动编写 / 放置的 `.py` 或 `.claw` 脚本
- **作用**：实现**项目级、场景化**的自动化逻辑，比如针对某个项目的专属工具、业务脚本
- **特点**：仅对当前代理生效，不会影响其他代理，高度灵活、可定制
- **位置**：托管/本地：`~/.openclaw/<workspace>/skills`

### BUILT-IN SKILLS（内置技能）

- **含义**：**OpenClaw 自带的核心基础技能**
- **来源**：随 OpenClaw 安装包一起发布的官方内置能力
- **典型技能**：文件读写、目录操作、浏览器控制、系统命令执行、文本处理、代码补全等
- **作用**：提供 AI 最基础的 “动手能力”，是完成日常任务的核心依赖
- **特点**：默认启用、稳定可靠，无需额外配置即可使用

### 全局 Skills（所有项目通用）

|  |  |
| --- | --- |
| **操作系统** | **路径** |
| **macOS/Linux** | `~/.openclaw/skills/` |
| **Windows** | `C:\Users\<用户名>\.openclaw\skills\` |

### 配置额外 Skills 目录

如果想添加额外的 Skills 目录，可以编辑 `~/.openclaw/openclaw.json`​

### 优先级顺序

从高到低：

|  |  |  |
| --- | --- | --- |
| **优先级** | **位置** | **说明** |
| 1（最高） | `workspace/skills/` | 项目内 Skills |
| 2 | `~/.openclaw/skills/` | 全局 Skills |
| 3 | `skills.load.extraDirs` | 配置的额外目录 |
| 4（最低） | 内置 Bundled Skills | OpenClaw 内置 |

## 添加技能

clawhub 市场：<https://clawhub.ai/skills?sort=downloads>

### 添加第三方 skill

#### 在线安装（了解）

由于官方的原因，国内基本无法使用命令直接下载，可以通过离线下载的方式添加

#### 离线安装

在 clawhub 上下载 skill 文件，解压到 workspace 中的 skills 目录中，例如打开下面的地址

<https://clawhub.ai/Shuai-DaiDai/feishu-doc-manager>。点击 Download zip

将下载的内容解压到指定的位置

然后在终端可以通过执行`openclaw skills`命令来检查是否添加成功

这里只讲 skill 的添加，skill 的具体触发 ai 会自动根据场景使用

### skill 说明

每个 skill 都有固定的格式，从上面的 skill 中我们先讲解一下两个文件的作用

#### SKILL.md

这是 Skill 的**入口定义文件**，OpenClaw 会优先读取它来理解技能的功能、触发条件和执行逻辑。

- **作用**：

- 告诉 AI 这个技能是什么、什么时候该被调用、如何执行。
- 包含 YAML 格式的元数据头（技能名称、描述、权限等）和 Markdown 格式的执行流程说明。

- **关键内容**：markdown

- **注意**：文件名必须是 `SKILL.md`（大写 S），否则 OpenClaw 无法识别。

#### `_meta.json`（辅助元数据文件 ​）

这是 Skill 的**结构化元数据文件**，用于更精细地管理技能信息，通常由工具或框架自动生成。

- **作用**：

- 存储结构化的技能元数据（版本、作者、依赖、配置等），方便 OpenClaw 框架解析和管理。
- 补充 `SKILL.md` 中不便用 Markdown 表达的机器可读信息，比如版本号、依赖列表、配置 schema 等。

- **典型内容**：json

- **注意**：如果没有这个文件，OpenClaw 会从 `SKILL.md` 的 YAML 头中提取元数据，所以它是**可选的**，没有就手动创建即可。

## 创建技能

在 skills 目录中创建对应的目录

创建对应的文件，然后将下面的内容复制到对应的文件中。这里给大家演示一个 skill，根据用户提供的系统地址，爬取所以的接口，并产出对接的接口文档

使用技能，在聊天中输入提示词，`http://novel.hctestedu.com/，帮我提取这个系统中的所有的接口，并产出一个md文档给我`

中间，通过几次对话来纠结它的结果。

生成的文件，保存在下面的位置

天气 skill

# 常用命令

## 基础入门命令

- openclaw onboard：交互式初始化向导，首次安装时配置AI模型、联网搜索、权限、网关、工作区等核心内容
- openclaw setup：初始化本地配置和代理工作区，创建基础运行环境

- openclaw doctor：健康检查工具，自动检测配置错误、API Key有效性、模型连通性并提供修复建议
- openclaw status：显示网关运行状态、频道健康状况、当前模型与会话信息

- openclaw health：从运行中的网关获取健康状态，快速确认服务可用性

- openclaw logs：查看网关运行日志，支持实时跟踪，用于定位报错原因

- openclaw dashboard：使用当前令牌打开Web图形控制面板，可视化管理配置与任务

- openclaw help：显示命令帮助信息，格式为openclaw help <命令名>
- openclaw reset：重置本地配置和状态（保留CLI工具），解决疑难配置问题

## 网关管理命令

- openclaw gateway start：启动网关服务（后台运行，推荐教学使用），在 mac 上是后台运行，在 windows 上和后面的 run 命令一样

- openclaw gateway stop：停止网关服务

- openclaw gateway restart：重启网关服务，修改配置后常用，在 windows 上可能会卡死，建议使用 Ctrl+C 停止再使用 start 命令启动
- openclaw gateway status：查看网关服务运行状态、端口与连接信息

- openclaw gateway run：前台运行网关，适合调试时查看实时输出

## 配置管理命令

- openclaw config file：打印当前生效的配置文件路径，快速定位openclaw.json

- openclaw config get <配置项>：读取指定配置项的值，示例：openclaw config get agents.defaults.model

- openclaw config set <配置项> <值>：修改指定配置项，示例：openclaw config set agents.defaults.model dashscope/qwen3.5-plus
- openclaw config unset <配置项>：移除指定配置项，恢复为默认值
- openclaw config validate：验证配置文件语法是否合法，课前检查必备

## 模型管理命令

- openclaw models list：列出所有已配置的可用AI模型

- openclaw models status：查看模型的连通状态、能力与认证信息

- openclaw models set <模型ID>：设置默认使用的AI模型，示例：openclaw models set dashscope/qwen3.5-plus

## 代理与技能命令

- openclaw agents list：查看所有已创建的隔离代理

- openclaw agent：执行单次AI任务，触发一轮代理推理与执行。`openclaw agent --agent main -m "1+1=几"`

- openclaw skills list：查看 OpenClaw 支持的所有自动化技能（文件、浏览器、截图等）

- openclaw skills check：检查技能依赖是否完整，确认技能可用

## 浏览器自动化命令

- openclaw browser start：启动AI可控制的专用浏览器（Chrome/Chromium）

- openclaw browser open 地址：打开指定的地址，示例：`openclaw browser open http://www.baidu.com`

- openclaw browser status：查看浏览器运行状态

- openclaw browser screenshot：捕获当前页面截图，演示AI视觉能力

# 频道管理

Openclaw 支持集成各种聊天工具，在这里演示国内的飞书集成，微信和 QQ 暂时没有官方直接集成的方式，可以在网上找插件

## 飞书机器人集成

### 创建飞书应用

打开飞书应用中心，<https://open.feishu.cn/app?lang=zh-CN>

### 添加飞书机器人

### 在 Openclaw 中配置

- 通过命令启用 feishu 插件

如果提示没有找到就使用下面的命令下载，如果效果如上图，就不用执行下面的命令了

- 先获取飞书应用信息

- 配置飞书应用信息

### openclaw.json 的变化

后面如果需要对飞书配置做修改，可以直接在配置文件中修改，再重启即可

### 添加权限

搜索并开通下面 3 个：

1. `im:message`
2. `im:message:send_as_bot`

> `im:message.p2p_msg:readonly`记得要加上这个权限

### 事件与回调

- 修改`openclaw.json`中的配置

然后重启 openclaw。

- 添加事件`im.message.receive_v1`

### 发布版本

### 在飞书上测试

> `openclaw pairing approve feishu 2Q2YU3CK`。注意`2Q2YU3CK`在上面的错误提示是复制的。不会的话就在群里提问
>
> 或者通过`openclaw config set channels.feishu.allowAll true`命令设置默认允许所有飞书用户

最后，飞书应用已经可以成功和 Openclaw 对话了

# 通信

## channels

### 核心身份验证

|  |  |  |
| --- | --- | --- |
| **配置项** | **当前值** | **说明** |
| **App Id** | `cli_a93144cf79f8dbc0` | 飞书应用唯一标识 ✅ |
| **App Secret** | `[已隐藏]` | 应用密钥 ✅ |
| **Verification Token** | 空 | 飞书回调校验令牌 |
| **Encrypt Key** | 空 | 消息加密密钥 |

### ​连接模式

|  |  |  |
| --- | --- | --- |
| **配置项** | **选项** | **说明** |
| **Connection Mode** | `websocket`  ✅ / `webhook` | 消息接收方式 |
| **Webhook Host/Path/Port** | 空 | webhook模式才需要填写 |

**WebSocket vs Webhook：**

- `websocket` - 长连接，实时性好，推荐 ✅
- `webhook` - 需要公网地址，飞书主动推送

### ​消息处理

|  |  |  |
| --- | --- | --- |
| **配置项** | **当前值** | **说明** |
| **Chunk Mode** | `length` | 按字符数分块 |
| **Text Chunk Limit** | 空 | 单条消息最大字符 |
| **Render Mode** | `auto` | 消息渲染方式 |
| **Reply In Thread** | `disabled` | 是否嵌套回复 |
| **Require Mention** | `关闭` | 群聊是否需要@ |

### ​权限策略

|  |  |  |
| --- | --- | --- |
| **配置项** | **当前值** | **说明** |
| **Dm Policy** | `open` | 私聊策略（任何人可私聊） |
| **Dm History Limit** | 空 | 私聊历史条数 |
| **Group Policy** | `open` | 群聊策略 |
| **Group Session Scope** | `group` | 群组会话隔离方式 |

**Dm Policy 选项：**

- `open` - 任何人都可以私聊
- `pairing` - 需要审批配对
- `allowlist` - 只有白名单用户可以私聊

## Messages（消息）

### Ack Reaction（确认反馈）

|  |  |  |
| --- | --- | --- |
| **配置项** | **选项** | **说明** |
| **Ack Reaction Emoji** | 👍 👍 等 | 收到消息时显示的表情 |
| **Ack Reaction Scope** | `group-mentions`  / `group-all`  / `direct`  / `all`  / `off` | 反馈显示范围 |

**Scope 选项说明：**

- `group-mentions` - 仅群聊中被@时
- `group-all` - 群聊所有消息
- `direct` - 仅私聊
- `all` - 所有消息
- `off` - 关闭

### ​Group Chat Rules（群聊规则）

|  |  |  |
| --- | --- | --- |
| **配置项** | **说明** | **建议值** |
| **Group History Limit** | 加载的群聊历史消息数量 | 10-50 |
| **Group Mention Patterns** | @机器人的匹配规则 | 留空使用默认 |

### ​Suppress Tool-error Warnings（抑制工具错误）

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **关闭** (推荐) | 显示工具错误给用户 |
| **开启** | 隐藏错误，仅Agent知道 |

### ​Message Text to Speech（消息转语音）

|  |  |  |
| --- | --- | --- |
| **配置项** | **选项** | **说明** |
| **Auto** | `off`  / `always`  / `inbound`  / `tagged` | 自动朗读模式 |
| **Max Text Length** | 数字 | 最大朗读字符数 |
| **Mode** | `final`  / `all` | 朗读模式 |
| **Provider** | `elevenlabs`  / `openai`  / `edge` | TTS提供商 |
| **Model Override** | - | 自定义模型 |
| **Timeout Ms** | 数字 | 超时时间 |

### ​建议配置

|  |  |
| --- | --- |
| **配置项** | **建议值** |
| **Ack Reaction Emoji** | 👍 或 👍 |
| **Ack Reaction Scope** | `direct` |
| **Group History Limit** | `20` |
| **Suppress Warnings** | 保持关闭 |
| **TTS Auto** | `off`  （不需要语音时） |

## Broadcast（广播）

> 目前只支持 WhatsApp 这个 app

### ​Broadcast Strategy（广播策略）

|  |  |
| --- | --- |
| **选项** | **说明** |
| **parallel** ✅ | 并行发送，所有目标同时接收，速度快 |
| **sequential** | 顺序发送，逐个发送，可控制顺序 |

**推荐：** 使用 `parallel`（速度优先）

### ​Custom entries（自定义条目）

**当前状态：** 无自定义条目

**作用：** 用于配置哪些来源的消息被广播到哪些Agent

## Talk（语音）

这个页面用于配置**实时语音交互**功能。

> ### ⚠️ 重要说明
>
> **这些设置仅在使用语音对话功能时才需要配置！**
>
> 如果你主要用**文字聊天**，不需要配置这个页面的任何内容，保持默认值即可。

### ​核心认证

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Talk API Key** | ElevenLabs API密钥（仅迁移用） |
| **Talk Active Provider** | 活跃的语音提供商（如 `elevenlabs`  ） |

### ​语音参数

|  |  |  |
| --- | --- | --- |
| **配置项** | **说明** | **建议值** |
| **Talk Model ID** | 语音模型ID（默认 `eleven_v3`  ） | 留空使用默认 |
| **Talk Voice ID** | 默认声音ID | 留空使用默认 |
| **Talk Output Format** | 输出格式（如 `mp3_44100_128`  ） | 留空使用默认 |

### ​对话控制

|  |  |  |
| --- | --- | --- |
| **配置项** | **说明** | **当前值** |
| **Talk Interrupt on Speech** | 用户说话时自动停止AI | 关闭 |

**Interrupt 说明：**

- 开启 - 用户说话时AI停止，用户说完AI继续
- 关闭 - 对话式轮流发言

### ​高级设置

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Talk Silence Timeout (ms)** | 用户沉默多久后发送（默认700-900ms） |
| **Talk Provider Settings** | 各提供商的特定设置 |
| **Talk Voice Aliases** | 声音名称映射 |

## Audio（音频）

**用途：** 当用户发送语音消息时，自动转录成文字供AI处理

### 配置项

|  |  |  |
| --- | --- | --- |
| **配置项** | **说明** | **建议值** |
| **Audio Transcription Command** | 转录命令（Whisper等） | 需要安装Whisper |
| **Audio Transcription Timeout (sec)** | 转录超时时间 | 60-300秒 |

### Audio Transcription Command 示例

如果你安装了 Whisper CLI，可以配置：

或

# 配置

## Environment Variables（环境变量）

### 用途

配置Shell环境导入和自定义环境变量。

### 主要配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Shell Environment Import Enabled** | 是否启用Shell环境导入 |
| **Shell Environment Import Timeout (ms)** | Shell环境导入超时时间 |
| **Custom entries** | 自定义环境变量（键值对） |

## Updates（更新）

### 用途

配置OpenClaw自动更新策略。

### 主要配置项

|  |  |  |
| --- | --- | --- |
| **配置项** | **说明** | **默认值** |
| **Auto Update Enabled** | 启用自动更新 | 开启 |
| **Auto Update Beta Check Interval (hours)** | Beta版检查间隔 | 1小时 |
| **Auto Update Stable Delay (hours)** | 稳定版延迟发布 | 6小时 |
| **Auto Update Stable Jitter (hours)** | 稳定版随机延迟 | 12小时 |
| **Update Channel** | 更新频道 | stable |
| **Update Check on Start** | 启动时检查更新 | 开启 |

## Metadata（元数据）

### 用途

显示配置文件的元信息。

### 配置项

|  |  |  |
| --- | --- | --- |
| **配置项** | **说明** | **当前值** |
| **Config Last Touched At** | 最后修改时间 | 自动记录 |
| **Config Last Touched Version** | 最后修改时的版本 | 2026.3.13 |

## Logging（日志）

### 用途

配置日志记录级别和输出方式。

### 主要配置项

|  |  |  |
| --- | --- | --- |
| **配置项** | **选项** | **说明** |
| **Console Log Level** | `silent`  /`fatal`  /`error`  /`warn`  /`info`  /`debug`  /`trace` | 控制台日志级别 |
| **Log Level** | 同上 | 文件日志级别 |
| **Console Log Style** | `pretty`  /`compact`  /`json` | 控制台日志样式 |
| **Log File Path** | 日志文件路径 | 空 |
| **Max File Bytes** | 日志文件最大大小 | 空 |
| **Sensitive Data Redaction Mode** | `off`  /`tools` | 敏感数据脱敏模式 |
| **Custom Redaction Patterns** | 自定义脱敏正则表达式 | 无 |

## Diagnostics（诊断）

### 用途

配置调试和诊断功能。

### 主要配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Diagnostics Enabled** | 启用诊断功能 |
| **Diagnostics Flags** | 诊断标志 |
| **Cache Trace Enabled** | 启用缓存追踪 |
| **Cache Trace File Path** | 缓存追踪文件路径 |
| **Cache Trace Include Messages** | 追踪是否包含消息 |
| **OpenTelemetry** | 分布式追踪配置（折叠） |

## Cli（命令行）

### 用途

配置命令行界面显示。

### 配置项

|  |  |  |
| --- | --- | --- |
| **配置项** | **选项** | **说明** |
| **CLI Banner** | CLI横幅总开关 | - |
| **CLI Banner Tagline Mode** | `random`  /`sequential`  /`off` | 横幅标语模式 |

## Secrets（密钥）

### 用途

配置API密钥和敏感信息的存储方式。

### 配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Env** | 环境变量方式 |
| **Exec** | 可执行脚本方式 |
| **File** | 文件方式 |
| **Providers** | 各提供商的密钥配置 |

## Acp（Agent Control Protocol）

### 用途

配置ACP协议用于多Agent通信。

### 主要配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **ACP Enabled** | 启用ACP（默认关闭） |
| **ACP Backend** | ACP后端地址 |
| **ACP Default Agent** | 默认Agent |
| **ACP Allowed Agents** | 允许的Agent列表 |
| **ACP Max Concurrent Sessions** | 最大并发会话数 |
| **ACP Dispatch Enabled** | 启用ACP调度 |
| **ACP Runtime Install Command** | 运行时安装命令 |
| **ACP Runtime TTL (minutes)** | 运行时生存时间 |

> ⚠️ ACP是高级功能，普通用户无需配置

# 外观与设置

## Appearance（外观）

### 主要配置项

|  |  |  |  |
| --- | --- | --- | --- |
| **配置项** | **说明** | **当前值** | **选项** |
| **Theme** | 选择主题系列 | Claw | Claw / Knot / Dash |
| **Mode** | 浅色或深色模式 | System（跟随系统） | System / Light（浅色）/ Dark（深色） |

### Connection（连接状态）

|  |  |  |
| --- | --- | --- |
| **配置项** | **说明** | **当前值** |
| **GATEWAY** | 后端网关WebSocket地址 | ws://127.0.0.1:18789 |
| **STATUS** | 与后端的连接状态 | Connected（已连接，绿色） |
| **ASSISTANT** | 助手服务标识 | Assistant |

## UI

### 配置项

|  |  |
| --- | --- |
| **配置项** | **详细说明** |
| **Assistant Avatar** | 用于UI界面中的助手头像。建议使用受信任的资源和高清晰度的图片。 |
| **Assistant Name** | 在聊天窗口和状态上下文中显示的名称。请保持名称稳定，以便识别。 |
| **Accent Color** | 主要强调色，应在高对比度下在亮/暗主题中都可读。 |

## Setup Wizard（设置向导）

### 用途

显示设置向导的执行历史和状态信息。

### 配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Wizard Last Run Timestamp** | 最近一次完成向导的ISO时间戳 |
| **Wizard Last Run Command** | 最近一次向导运行的命令 |
| **Wizard Last Run Commit** | 开发版本中的源代码提交ID（用于调试） |
| **Wizard Last Run Mode** | 向导执行模式：local（本地）或 remote（远程） |
| **Wizard Last Run Version** | 最近一次向导运行时的OpenClaw版本 |

# 自动化

## Commands（命令）

### 用途

配置自定义斜杠命令和系统级命令的执行权限。

### 配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Command Elevated Access Rules** | 定义提权命令访问规则，确保特权命令不会暴露给普通用户 |
| **Allow Bash Chat Command** | 允许使用 `!`  或 `/bash`  命令运行主机Shell命令（需开启tools.elevated权限） |
| **Bash Foreground Window (ms)** | Bash转入后台前等待时长（默认2000ms，设为0则立即转入后台） |
| **Allow /config** | 允许通过 `/config`  命令读写磁盘配置文件 |
| **Allow /debug** | 允许使用 `/debug`  命令进行运行时设置覆盖 |
| **Native Commands** | 在支持的渠道注册原生斜杠/菜单命令，提高命令可发现性 |

## Hooks（钩子）

### 用途

配置Webhooks和事件钩子，用于接收外部系统的回调和自动化事件。

### 通用钩子设置

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Hooks Allowed Agent IDs** | 允许的Agent ID白名单，用于将自动化限制在专用服务Agent中 |
| **Hooks Allowed Session Key Prefixes** | 允许的会话密钥前缀白名单，防止任意会话密钥注入 |
| **Hooks Allow Request Session Key** | 允许调用者提供会话密钥，实现调用者控制的路由 |
| **Hooks Default Session Key** | 未提供密钥时的默认会话密钥 |

### Gmail钩子设置

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Gmail Hook Label** | Gmail标签过滤器，限制触发钩子的邮件范围 |
| **Gmail Hook Max Body Bytes** | 每个事件处理的最大Gmail负载字节数 |
| **Gmail Hook Model Override** | Gmail触发运行时的可选模型覆盖 |
| **Gmail Hook Push Token** | Gmail推送回调的共享密钥令牌 |
| **Gmail Hook Renew Interval (min)** | Gmail watch订阅续订频率 |
| **Gmail Hook Subscription** | Pub/Sub订阅名称 |
| **Gmail Hook Thinking Override** | 思考努力程度覆盖：off/minimal/low/medium/high |
| **Gmail Hook Pub/Sub Topic** | Google Pub/Sub主题名称 |

### 内部钩子

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Internal Hooks Enabled** | 是否启用内部钩子运行时 |
| **Internal Hook Handlers** | 内部事件处理程序列表，将事件映射到模块 |

### 映射与路径设置

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Hook Mappings** | 匹配入站钩子请求并选择操作的映射规则 |
| **Hooks Max Body Bytes** | Webhooks接受的最大负载大小 |
| **Hooks Endpoint Path** | 钩子端点HTTP路径（建议使用不可猜测的路径） |
| **Hooks Presets** | 命名钩子预设包 |
| **Hooks Auth Token** | 钩子入口检查的共享令牌 |
| **Hooks Transforms Directory** | 映射转换模块基目录 |

## Bindings（绑定）

### 用途

定义路由规则和持久性ACP会话所有权。

### 配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **type=route** | 执行普通路由，将任务或消息分配给特定路径或处理程序 |
| **type=acp** | 持久性ACP治理绑定，将会话固定分配给特定坐席环境 |

## Cron（定时任务）

### 用途

配置计划任务与自动化执行。

### 配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Cron Enabled** | 启用由网关管理的计划Cron作业执行 |
| **Failure Alert** | 任务失败时的警报通知 |
| **Cron Max Concurrent Runs** | 同时执行的最大Cron作业数量 |
| **Cron Retry Policy** | 瞬态错误时的重试策略覆盖 |
| **Cron Retry Backoff (ms)** | 重试间隔时间（默认[30000, 60000, 300000]毫秒） |
| **Cron Retry Max Attempts** | 最大重试次数（默认3次） |
| **Cron Retry Error Types** | 触发重试的错误类型 |

## Approvals（审批）

### 用途

配置执行审批转发，将审批请求路由到运营频道。

### 配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Approval Agent Filter** | 符合转发条件的Agent ID白名单 |
| **Forward Exec Approvals** | 启用将审批请求转发到指定交付目的地 |
| **Approval Forwarding Mode** | 审批提示发送位置：session（原始聊天）/targets（指定目标）/both（两者） |
| **Approval Session Filter** | 会话密钥过滤器（子字符串或正则表达式） |
| **Approval Forwarding Targets** | 明确的交付目标列表（包含频道和目的地详情） |

## Plugins（插件）

### 用途

管理和配置插件扩展。

### 配置项

|  |  |
| --- | --- |
| **配置项** | **说明** |
| **Plugin Allowlist** | 允许加载的插件ID白名单 |
| **Plugin Denylist** | 禁止加载的插件ID黑名单（用于紧急回滚和高风险插件阻止） |
| **Enable Plugins** | 全局启用或禁用插件加载（默认true） |
| **Plugin Entries** | 各插件的详细设置，包括启用状态和运行时配置 |

### 内置插件

|  |  |
| --- | --- |
| **插件** | **说明** |
| **ACPX Runtime** | ACP扩展运行时 |
| **@openclaw/bluebubbles** | BlueBubbles集成 |
| **Device Pairing** | 设备配对功能 |
| **@openclaw/diagnostics-otel** | 可观测性诊断 |
| **Diffs** | 差异对比 |
| **@openclaw/discord** | Discord集成 |

# 基础设施

网关、Web、浏览器和媒体设置。

## Gateway

### Gateway

​

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Allow x-real-ip Fallback | 允许使用 X-Real-IP 确定客户端真实IP（当连接来自受信任代理时） | 在反向代理环境下获取真实客户端IP |

### Gateway Auth

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Auth Allow Trusted Identity | 允许受信任的身份验证方式 | 使用受信任代理或Tailscale身份验证的场景 |
| Gateway Auth Mode | 身份验证模式：token（令牌）、password（密码）或 trusted-proxy（受信任代理） | 选择合适的认证方式保护Gateway访问 |
| Gateway Password | 密码认证模式的密码（推荐通过环境变量 OPENCLAW\_GATEWAY\_PASSWORD 设置） | 密码认证时使用 |

### Gateway Auth Rate Limit

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Control Loopback | 是否对回环连接启用速率限制 | 生产环境建议关闭本地测试 |
| Lockout Duration | 锁定持续时间（秒），配置频率限制控制以降低暴力破解风险 | 设置暴力破解锁定时长 |
| Max Attempts | 最大尝试次数 | 防止暴力破解的尝试次数限制 |
| Window (s) | 速率限制时间窗口（秒） | 统计频率限制的时间范围 |

### Gateway Token

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Token | 令牌认证模式的共享令牌（使用 'token' 模式时的机密令牌） | 用于token模式下的身份验证 |

### Gateway Trusted Proxy Auth

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Allow Users | 受信任代理模式下允许的用户列表 | 限制可访问的代理用户 |
| Required Headers | 必需的身份请求头列表 | 指定代理必须传递的头信息 |
| User Header | 用户身份请求头名称 | 定义传递用户身份的头字段名 |

### Gateway Bind Mode

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Bind Mode | 网关监听器的网络接口绑定模式：loopback（仅本地）、auto、all、custom、linked | 控制Gateway的网络可访问范围 |

### Gateway Channel Health Check Interval (min)

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Channel Health Check Interval (min) | 自动通道健康探测和状态更新的间隔（分钟） | 调整连接可靠性检测频率 |

### Control UI

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Control UI Allowed Origins | CORS允许的源列表，用于跨域访问控制 | 配置跨域访问控制 |
| Insecure Control UI Auth Toggle | 绕过回环流量的正常验证要求（不安全选项） | 仅用于紧急救援，默认关闭 |
| Control UI Base Path | 控制界面的URL路径前缀，默认 /dashboard | 自定义Dashboard访问路径 |
| Dangerous Allow Insecure Header Origin Fallback | 允许不安全源回退（危险选项） | 仅用于调试，默认关闭 |
| Dangerous Disable Control UI Device Auth | 禁用控制界面设备身份检查（危险选项） | 仅用于紧急救援，默认关闭 |
| Control UI Enabled | 启用或禁用控制界面 | 开启或关闭Web管理界面 |
| Control UI Asset Root | 控制界面资源文件根目录 | 自定义UI资源路径 |

### Gateway Custom Bind Host

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Custom Bind Host | 自定义绑定主机地址（使用custom绑定模式时指定） | 指定具体IP |

### Gateway HTTP API

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway HTTP Endpoints | HTTP API端点配置 | 控制API暴露面，减少攻击面 |
| Gateway HTTP Security Headers | HTTP安全响应头配置 | 自定义安全Headers |

### Gateway Mode

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Mode | Gateway运行模式：local（本地）或 remote（远程连接远程Gateway） | local为本地Gateway，remote为连接远程Gateway |

### Nodes

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Node Allowlist (Extra Commands) | 允许执行的节点额外命令白名单 | 仅允许特定命令执行 |
| Gateway Node Denylist | 屏蔽的命令名称列表（即使节点声明中存在也要屏蔽），默认包含 \*、system.run、vfs.file.contents、vfs.file.read、vfs.file.write、vm.memory.add、vm.cpu.add | 禁用高危命令 |

### Gateway Port

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Port | Gateway监听API、控制界面和连接的TCP端口，默认18789 | 自定义Gateway端口 |

### Gateway Push Delivery

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway APNs Relay | APNS中继地址配置 | iOS设备推送消息中转 |

### Config Reload

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Config Reload Debounce (ms) | 配置变更防抖时间（毫秒），默认1000ms | 避免频繁重载 |
| Config Reload Mode | 配置重载模式：hybrid（热应用安全更改，关键更改需重启）、soft、hard | hybrid为默认推荐模式 |

### Remote Gateway

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Remote Gateway Password | 远程Gateway连接的密码（仅在网关模式设为remote时生效） | remote模式下的身份验证 |
| Remote Gateway SSH Identity | SSH身份文件路径 | SSH传输方式的密钥认证 |
| Remote Gateway SSH Target | SSH目标地址，格式：user@host | 指定远程Gateway的SSH目标 |
| Remote Gateway TLS Fingerprint | TLS证书指纹验证 | 固定TLS指纹验证连接安全 |
| Remote Gateway Token | 远程Gateway连接的令牌 | remote模式下的令牌认证 |
| Remote Gateway Transport | 远程传输方式：ssh（通过SSH隧道）或 direct（直接WebSocket） | 选择远程连接方式 |
| Remote Gateway URL | 远程Gateway WebSocket地址，格式：wss://localhost:30740 | 指定远程Gateway地址 |

### Gateway Tailscale

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Tailscale Mode | Tailscale集成模式：off（关闭）、direct（仅tailnet可访问）、tunnel（公开暴露） | off关闭，direct推荐，tunnel公开暴露需认证 |
| Gateway Tailscale Restart on Exit | 退出时重置Tailscale配置 | 退出时自动清理Tailscale配置 |

### Gateway TLS

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway TLS Auto-Generate Cert | 无证书时自动生成自签名证书 | 简化TLS配置 |
| Gateway TLS CA Path | CA证书包路径（PEM格式） | TLS双向认证的CA证书 |
| Gateway TLS Certificate Path | TLS证书PEM文件路径 | HTTPS服务器证书 |
| Gateway TLS Enabled | 启用TLS加密连接 | 保护通信安全 |
| Gateway TLS Key Path | TLS私钥PEM文件路径 | HTTPS私钥 |

### Gateway Tool Exposure Policy

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Tool Allowlist | 允许使用的工具白名单（独立于代理配置文件的工具可用性管理） | 细粒度控制可用工具 |
| Gateway Tool Denylist | 禁止使用的工具黑名单 | 禁用高风险工具 |

### Gateway Trusted Proxy CIDRs

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| Gateway Trusted Proxy CIDRs | 受信任代理的IP范围列表（CIDR格式），用于 'trusted-proxy' 验证模式下的受信任上游代理 | 配置受信任的反向代理IP范围 |

## Web

|  |  |
| --- | --- |
| **配置项** | **描述** |
| Web Channel Enabled | 启用Web频道运行时及WebSocket生命周期行为 |
| Web Channel Heartbeat Interval | Web频道心跳间隔（秒） |
| Web Channel Reconnect Policy | 传输失败后重连的退避策略 |
| Web Reconnect Backoff Factor | 重连指数退避倍数（大于1） |
| Web Reconnect Initial Delay | 第一次重试前初始延迟（毫秒） |
| Web Reconnect Jitter | 重连延迟随机化因子（0-1） |
| Web Reconnect Max Attempts | 最大重连尝试次数 |

## Browser

|  |  |
| --- | --- |
| **配置项** | **描述** |
| Browser Attach-only Mode | 限制为仅附加模式，不启动本地浏览器 |
| Browser CDP Port Range Start | 起始CDP端口（冲突时调高） |
| Browser CDP URL | 远程CDP websocket URL |
| Browser Enabled | 启用浏览器功能 |
| Browser Evaluate Enabled | 启用浏览器端脚本评估 |
| Browser No-Sandbox Mode | 禁用Chromium沙箱隔离（危险） |
| Browser Profiles | 浏览器配置文件连接映射 |

## NodeHost

|  |  |
| --- | --- |
| **配置项** | **描述** |
| Node Browser Proxy Allowed Profiles | 浏览器配置文件白名单 |
| Node Browser Proxy Enabled | 通过节点代理暴露浏览器控制服务器 |

## Canvas Host

|  |  |
| --- | --- |
| **配置项** | **描述** |
| Canvas Host Enabled | 启用画布主机服务器进程 |
| Canvas Host Live Reload | 开发时启用画布资产自动重载 |
| Canvas Host Port | 画布主机HTTP服务器端口 |
| Canvas Host Root Directory | 画布内容和静态资产根目录 |

## Discovery

|  |  |
| --- | --- |
| **配置项** | **描述** |
| mDNS Discovery Mode | mDNS广播模式（minimal/full/off） |
| Wide-area Discovery Domain | 广域发现DNS-SD域名 |
| Wide-area Discovery Enabled | 启用广域发现信号 |

## Media

|  |  |
| --- | --- |
| **配置项** | **描述** |
| Preserve Media Filenames | 保留上传媒体的原始文件名 |
| Media Retention TTL | 媒体文件自动清理保留时长（小时） |

# AI 与代理

代理、模型、技能、工具、记忆和会话设置。

## Agents（代理）

### Agent Defaults（代理默认值）

这些是**所有代理共享的默认设置**，除非在 `agents.list` 中单独覆盖。

|  |  |  |
| --- | --- | --- |
| **配置项** | **标签** | **说明** |
| **Block Streaming Break** | - | AI输出时分块传输的结束标记，设为 `text_end`  和 `message_end` |
| **Block Streaming Default** | - | 块流传输开关，默认 **开启** |
| **Thinking Default** | - | AI思考模式默认值 |
| **Timeout Seconds** | - | 代理任务超时时间（秒） |
| **Verbose Default** | - | 详细模式输出级别：`off`  / `on`  / `full` |

### 工作区与文件相关

|  |  |  |
| --- | --- | --- |
| **配置项** | **标签** | **说明** |
| **Bootstrap Max Chars** | performance | 单个引导文件最大字符数，默认 **20,000** |
| **Bootstrap Total Max Chars** | performance | 所有引导文件总字符数上限，默认 **150,000** |
| **Bootstrap Prompt Truncation Warning** | advanced | 引导文件被截断时是否警告：`off`  / `once`  （默认） / `always` |
| **Workspace** | advanced | 代理工作区路径 |

### 交互体验相关

|  |  |  |
| --- | --- | --- |
| **配置项** | **标签** | **说明** |
| **Typing Mode** | - | AI回复显示方式：`never`  / `instant`  （即时） / `thinking`  / `message` |
| **Typing Interval Seconds** | - | 打字动画间隔（秒） |
| **Human Delay** | - | 人为延迟设置 |

### 其他设置

|  |  |  |
| --- | --- | --- |
| **配置项** | **标签** | **说明** |
| **Time Format** | - | 时间格式：`auto`  / 12小时制 / 24小时制 |
| **User Timezone** | - | 用户时区 |
| **Image Max Dimension (px)** | - | 图片最大尺寸（像素） |
| **Media Max Mb** | - | 媒体文件最大大小（MB） |
| **Pdf Model** | - | PDF处理模型配置 |

## Models（模型配置）

### Bedrock Model Discovery（Bedrock模型发现）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Bedrock Default Context Window** | 当提供商元数据缺少显式限制时，应用于发现模型的备用上下文窗口值 | 使用现实的默认值避免超出真实提供商限制的过大提示 |
| **Bedrock Default Max Tokens** | 应用于没有显式输出Token限制的发现模型的备用最大Token值 | 使用保守默认值减少截断意外和非预期Token支出 |
| **Bedrock Discovery Enabled** | 为支持Bedrock的提供商启用定期Bedrock模型发现和目录刷新 | 正在使用Bedrock且正确配置IAM权限时启用 |
| **Bedrock Discovery Provider Filter** | 可选的Bedrock发现提供商允许列表过滤器，仅刷新选定提供商 | 多提供商环境中限制发现范围 |
| **Bedrock Discovery Refresh Interval** | Bedrock发现轮询的刷新频率（秒） | 生产环境使用较长间隔降低API成本和控制平面干扰 |
| **Bedrock Discovery Region** | 用于Bedrock发现调用的AWS区域 | 使用配置了Bedrock模型的区域避免发现结果为空 |

### Model Catalog Mode（模型目录模式）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Model Catalog Mode** | 控制提供商目录行为："merge"保留内置内容并覆盖自定义提供商，"replace"仅使用配置的提供商 | 使用merge保留默认模型同时添加自定义；使用replace完全自定义模型列表 |

### Model Providers（模型提供商）

**通用提供商配置：**

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **API Adapter** | 选择用于控制模型调用的请求/响应兼容性处理的适配器 | 确保与不同API格式的兼容性 |
| **API Key** | 用于API密钥认证的凭据 | 配置提供商访问凭证 |
| **Auth Mode** | 选择认证风格（api-key/aws-sdk/oauth/token） | 根据提供商要求选择合适的认证方式 |
| **Authorization Header** | 为真时，即使有其他认证方式，凭据也通过HTTP Authorization请求头发送 | 需要显式传递认证令牌时启用 |
| **Base URL** | 用于模型请求的服务端点基础URL | 配置API端点地址 |
| **Headers** | 额外的HTTP请求头 | 添加自定义头如API版本标识 |
| **Inject num\_ctx (OpenAI Compat)** | 控制是否为OpenAI兼容的Ollama提供商注入options.num\_ctx | Ollama本地部署时启用 |

**模型条目配置：**

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Api** | 选择API类型 | 根据模型支持的API格式选择 |
| **Context Window** | 模型的上下文窗口大小 | 确保不超过模型的实际处理能力 |
| **Max Tokens** | 最大输出Token数 | 限制单次响应的最大长度，控制成本 |
| **Id** | 模型标识符 | 用于API调用的模型ID |
| **Name** | 模型显示名称 | 便于识别的友好名称 |
| **Input** | 输入类型（text/image） | 选择模型支持的输入模式 |
| **Reasoning** | 是否启用推理功能 | 启用推理模型的高级思考能力 |
| **Cost** | 成本配置 | 设置token费用用于成本控制 |

## Skills（技能配置）

### Allow Bundled（允许捆绑）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Allow Bundled** | 添加允许捆绑的项目列表 | 限制只能使用特定技能包，增强安全性 |

### Entries（条目）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Custom entries** | 自定义条目配置 | 添加特定项目的技能配置 |

### Install（安装设置）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Node Manager** | 选择首选的包管理器（npm/pnpm/yarn/bun） | 根据团队偏好或项目要求选择合适的包管理器 |
| **Prefer Brew** | 是否首选Brew安装 | macOS环境偏好使用Homebrew安装依赖 |

### Limits（限制设置）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Max Candidates Per Root** | 每个根目录下允许的最大候选技能数量 | 限制技能搜索范围，防止性能问题 |
| **Max Skill File Bytes** | 单个技能文件的最大大小限制 | 防止加载过大的技能文件影响性能 |
| **Max Skills In Prompt** | 提示词中允许包含的最大技能数量 | 控制提示词长度，优化token使用 |
| **Max Skills Loaded Per Source** | 从单个来源加载的最大技能数量 | 限制从单一来源加载过多技能 |
| **Max Skills Prompt Chars** | 技能相关提示词的最大字符长度 | 控制技能描述长度，避免提示词膨胀 |

### Load（加载设置）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Extra Dirs** | 添加加载技能时需要扫描的额外目录 | 索引默认路径之外的自定义技能位置 |
| **Watch Skills** | 启用文件系统监控以检测技能定义变化，无需重启即可应用更新 | 开发工作流中启用；不可变的生产镜像中禁用 |
| **Skills Watch Debounce** | 合并快速发生的技能文件更改的防抖窗口时间（毫秒） | 频繁写入时增加此值减少重新加载频率；需要更快编辑反馈时降低 |

## Tools（工具配置）

### Agents/Agent Tool Access（代理工具访问）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Agents/Agent Target Checklist** | 允许目标代理列表，用于限制代理或组之间的访问 | 在多代理架构中，家庭助手代理可能需要调用主代理的服务，但不应访问工作代理 |
| **Restricting Agent Tool Use** | 限制代理的工具使用权限（白名单/黑名单） | 公开群聊中限制代理只能使用聊天工具，禁止执行命令或修改文件 |
| **Tool Allow list** | 代理只能使用列表中的工具 | 仅允许代理使用文件读取功能，实现只读助手模式 |
| **Tool Deny list** | 代理禁止使用列表中的工具 | 禁止家庭成员使用的代理执行危险命令(如exec)，防止误操作 |
| **Tool Policy by Provider** | 按提供商/权限限制工具访问 | 对不同AI模型供应商应用不同安全级别，商业模型可以访问更多工具 |
| **Tool Deny list** | 明确拒绝代理访问的工具 | 安全加固场景，明确禁止某些高风险工具 |

### Minimal Tool Privileges（最小工具权限）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Minimal Tool Privileges** | 设置代理的基本工具访问权限 | 为新用户或测试代理启用基础功能，确保基本工具可用 |
| **Disable Trusted Tool Access** | 禁用可信工具自动访问 | 高安全环境需要显式授权每个工具，不依赖隐式信任 |
| **Deny Tool** | 明确拒绝的工具黑名单 | 临时禁用某个问题工具（如web\_search出故障时） |

### Apply Policy（应用策略）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Data Ads** | 控制代理中数据广告的使用 | 商业代理需要展示定向广告以实现盈利 |
| **Background Ads** | 背景广告数量配置 | 调整广告展示频率，平衡用户体验与收益 |
| **Dialogue Ads** | 对话中广告数量 | 控制对话流中插入广告的频率 |
| **Disc Ads** | 磁盘广告显示类型 | 区分标准/主要/更多广告展示层级 |
| **Pure News Ranking** | 纯净新闻排名策略 | 新闻类代理需要去除赞助内容，提供真实排名 |
| **Pure Media Search** | 纯净媒体搜索策略 | 媒体搜索代理过滤成人/不当内容 |
| **Invisibility Policy (Static)** | 隐身策略控制可见性 | 内部管理代理不希望在用户界面显示 |
| **Deep Link Request** | 深度链接域名白名单 | 限制代理只能跳转到已认证的合作伙伴网站 |
| **User Safe On Profiles** | 用户配置文件白名单 | 仅允许经过安全审核的用户配置文件 |
| **Safe Domain Trusted Sites** | 可信域名白名单 | 企业代理只能访问内部网站，防止钓鱼攻击 |
| **Pure Priority** | 纯净新闻优先级设置 | 调整算法优先级，高值确保纯净内容优先 |
| **Disable Ads** | 完全禁用广告 | 付费用户享受无广告体验 |
| **Multi-query Policy** | 多查询策略控制 | 研究代理需要同时查询多个信息源 |

### Links（链接）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Restricted Link Understanding** | 限制链接理解功能 | 防止代理访问外部链接，保护企业数据安全 |
| **Link Understanding Max Count** | 单次请求最大链接数 | 防止恶意代理短时间内请求大量URL造成资源耗尽 |
| **Link Understanding Models** | 链接理解模型白名单 | 指定使用便宜的embedding模型处理链接，降低成本 |
| **Link Understanding Scope** | 链接理解范围 | 限制代理只分析特定域名下的链接 |
| **Link Understanding Timeout** | 链接理解超时时间 | 网络慢时延长等待时间，或快速失败释放资源 |

### Loss Detection（丢包检测）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Loss Loop Count Threshold** | 检测循环次数阈值 | 调试时快速发现问题(值=1)，生产环境适当提高避免误报 |

### Datastore（数据存储）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Tool Ops Description** | 包含工具操作描述 | 开发调试需要详细日志，正式环境关闭节省空间 |
| **Non-Agent Match Name Threshold** | 名称匹配阈值 | 模糊匹配(0.8)适合用户可能有拼写错误；精确匹配(0.95)适合结构化查询 |
| **Non-Agent Match Score Threshold** | 得分匹配阈值 | 高阈值(0.7)确保返回结果高度相关，低阈值(0.3)返回更多候选 |
| **Non-Agent Match Max Count** | 最大返回数 | 移动端限制返回数(5)节省带宽，桌面端可以返回更多(20) |

### Media（媒体）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Allow Short Reading Summary** | 音频简短摘要 | 播客代理为长音频生成快速摘要，方便用户决定是否完整收听 |
| **Media Understanding Shared Models** | 共享媒体模型 | 企业统一使用特定vision模型，确保分析结果一致性 |

### Message（消息）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Allow Cross Chat Messaging** | 跨聊天消息传递 | 多设备代理需要同步消息，或群组代理转发重要通知 |
| **Disable Message Translation** | 禁用消息翻译 | 内部团队使用统一语言，不需要自动翻译功能 |

**Cross Control（跨控制）：**

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Allow Cross-Context Device Control** | 跨设备控制 | 家庭自动化场景，通过聊天控制智能家居设备 |
| **Allow Cross-Context Home Control** | 跨上下文家庭控制 | 远程控制家中灯光、空调等设备 |
| **Device Control Status** | 设备状态显示 | 用户需要实时了解设备开关状态 |
| **Device Control Status Prefix** | 状态消息前缀 | "🔌 " 等emoji前缀便于识别设备消息 |
| **Cross-Context Status Suffix** | 状态消息后缀 | 添加时间戳后缀便于追溯 |

### Tool Policy（工具策略）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Sandbox Tool Policy** | 沙盒工具策略 | 公开群组代理在隔离环境运行，防止系统被破坏 |
| **Independent Tool Sandbox Policy** | 独立沙盒策略 | 每个代理有独立安全边界，互不影响 |

**Sandbox Allow/Deny 列表：**

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Allow** | 沙盒内允许的工具 | 只读沙盒只允许read工具 |
| **Also Allow** | 额外允许的工具 | 在拒绝某些工具后，例外允许特定安全工具 |
| **Deny** | 沙盒内拒绝的工具 | 禁止exec、write等写操作，保护沙盒内数据 |

### Revision（修订）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Revision Tool Policy** | 修订工具策略 | 文件修改代理需要版本控制能力 |
| **Independent Tool Revision Policy** | 独立修订策略 | 为每个代理维护独立的修改历史 |

### Web Tools（Web工具）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Web Search Max Result** | 搜索结果最大数 | 快速概览(5条)，深度研究(20条) |
| **Enable Web Search Tool** | 启用网页搜索 | 问答代理需要实时网络信息 |
| **Precision Advisor** | 精准顾问 | 需要高质量搜索结果的学术研究 |
| **Precision Score** | 精准得分阈值 | 过滤低质量结果，确保返回内容相关性 |
| **Search Result Max Length** | 结果最大长度 | 移动端简短摘要(500)，桌面端完整摘要(2000) |
| **Show Search Raw Result** | 显示原始结果 | 开发调试需要查看原始API响应 |
| **Search Result Filter** | 结果过滤阈值 | 去除垃圾信息和广告 |
| **Web Search Result Count** | 返回结果数 | 控制API调用成本 |
| **Web Search Result Snippet** | 摘要数量 | 快速浏览(1条)，详细研究(3条) |
| **Web Search Multiple Queries** | 多重查询 | 同时搜索多个关键词，适合研究代理 |
| **Web Search Timeout** | 搜索超时 | 慢速网络延长到5000ms，快速网络可缩短到1000ms |
| **Web Search User Agent** | 用户代理 | 模拟特定浏览器访问，或设置企业标识 |

**各搜索引擎提供商设置：**

|  |  |
| --- | --- |
| **提供商** | **使用场景** |
| **Brave** | 重视隐私的用户，使用Brave搜索保护隐私 |
| **Gemini** | Google生态用户，获得更好的搜索集成 |
| **Gecit** | 特定地区搜索引擎，支持本地化搜索 |
| **Kind** | 自定义搜索引擎，企业内网搜索 |
| **Proximity** | 根据用户位置选择最优搜索源 |

### 工具组使用场景速查

|  |  |
| --- | --- |
| **工具组** | **适用场景** |
| `group:fs` | 只读文件代理 |
| `group:runtime` | 自动化脚本代理（需执行命令） |
| `group:sessions` | 会话管理代理（跨会话消息） |
| `group:memory` | 记忆检索代理 |
| `group:web` | 网络搜索代理 |
| `group:ui` | 浏览器自动化代理 |
| `group:automation` | 系统管理代理（定时任务） |
| `group:messaging` | 消息推送代理 |
| `group:nodes` | 设备控制代理（IoT） |
| `group:openclaw` | OpenClaw内部工具访问 |

## Memory（记忆配置）

AI 的记忆系统，管理上下文信息和知识检索。

### Memory Backend（记忆后端）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Memory Backend** | 选择全局记忆引擎："builtin"使用OpenClaw内部记忆，"qmd"使用QMD边车流水线。除非打算操作QMD，否则保留"builtin" | 普通用户使用内置记忆即可满足需求；有高级检索需求的用户切换到QMD |

### Memory Citations Mode（记忆引用模式）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Memory Citations Mode** | 控制回复中引用的可见性："auto"在有用时显示引用，"on"始终显示，"off"则隐藏。保留"auto"作为平衡信噪比的默认设置 | 学术场景需要显示引用；普通用户使用auto避免干扰 |

### Qmd（QMD配置）

**QMD Binary（二进制文件）：**

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **QMD Binary** | 设置QMD后端使用的qmd二进制文件的可执行路径（默认从PATH环境变量解析） | 多个qmd安装或PATH不同时，使用绝对路径确保正确调用 |
| **QMD Include Default Memory** | 自动将默认记忆文件（MEMORY.md和memory/\*\*/\*.md）索引到QMD集合中 | 希望仅通过显式自定义路径控制索引时关闭 |

**Limits（限制）：**

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **QMD Max Injected Chars** | 限制一次对话轮次中跨所有命中结果注入的QMD文本总量 | 控制提示词膨胀和延迟；上下文持续被截断时调高 |
| **QMD Max Results** | 限制每个召回请求返回的QMD命中数量（默认8） | 调高获得更广泛召回上下文；调低保持提示词精简和快速 |
| **QMD Max Snippet Chars** | 限制从QMD命中中提取的每个结果片段长度（默认700字符） | 提示词膨胀过快时调低；回答遗漏关键细节时调低 |
| **QMD Search Timeout** | 设置每个查询的QMD搜索超时时间（默认4000ms） | 大索引或慢环境调高；保持请求延迟在有限范围时调低 |

**QMD MCPorter（QMD MCPorter配置）：**

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **QMD MCPorter Enabled** | 通过mcporter守护进程而不是每个请求生成qmd来路由QMD | 大型模型冷启动昂贵时启用；简单本地设置保留直接进程模式 |
| **QMD MCPorter Server Name** | 命名用于QMD调用的mcporter服务器目标（默认qmd） | mcporter设置使用自定义服务器名称时更改 |
| **QMD MCPorter Start Daemon** | 启用时自动启动mcporter守护进程（默认true） | 进程生命周期由服务管理器外部管理时关闭 |

**QMD Extra Paths（额外路径）：**

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **QMD Extra Paths** | 添加要包含在QMD索引中的自定义目录或文件，每个都有可选名称和glob模式 | 索引默认记忆路径之外的项目特定知识位置 |

**QMD Surface Scope（表面范围）：**

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **QMD Search Mode** | 选择QMD检索路径："query"标准查询流，"search"面向搜索的检索，"vsearch"强调向量检索 | 除非正在调整相关性质量，否则保留默认值 |

### Sessions（会话配置）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **QMD Session Indexing** | 将会话转录内容索引到QMD中以便召回包含先前对话（实验性，默认false） | 需要转录内存且接受较大索引变动时启用 |
| **QMD Session Export Directory** | 覆盖QMD索引前写入清理后会话导出的位置 | 默认状态存储受限或导出必须落在托管卷上时使用 |
| **QMD Session Retention** | 导出的会话文件在自动清理前保留天数（默认无限） | 设置存储卫生或合规保留政策时配置有限值 |

### Update（更新配置）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **QMD Command Timeout** | 设置QMD维护命令（如集合列表/添加）的超时时间（默认30000ms） | 慢速磁盘或远程文件系统运行时调高 |
| **QMD Update Debounce** | 设置连续QMD刷新尝试之间的最小延迟（默认15000ms） | 频繁文件更改导致抖动或后台负载时调高 |
| **QMD Embed Interval** | 设置QMD重新计算嵌入的频率（持续时间字符串，默认60m；设为0禁用） | 较短间隔提高新鲜度但增加嵌入工作量和成本 |
| **QMD Embed Timeout** | 设置每个qmd embed循环的最大运行时间（默认120000ms） | 较重嵌入工作负载或慢硬件调高；轻量级SLA下调低快速失败 |
| **QMD Update Interval** | 设置QMD从源内容刷新索引的频率（默认5m） | 较短间隔提高新鲜度但增加后台CPU和I/O |
| **QMD Update on Startup** | 在网关启动期间运行一次初始QMD更新（默认true） | 启动速度比即时新鲜度重要时禁用 |
| **QMD Update Timeout** | 设置每个qmd update循环的最大运行时间（默认120000ms） | 较大集合调高；希望更快检测故障时调低 |
| **QMD Wait for Boot Sync** | 阻塞启动完成直到初始QMD同步完成（默认false） | 需要在提供流量前获得完全最新召回时启用 |

## Session（会话配置）

会话管理与持久化，控制 AI 对话的状态存储、生命周期和维护策略。

### Session Agent-to-Agent（会话代理间交互）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Agent-to-Agent Ping-Pong Turns** | 代理间交换中请求者和目标代理之间的最大回复轮次。使用较低值来硬限制聊天循环并确保可预测的运行完成 | 高级代理到代理自动化系统需要限制轮次防止无限循环 |
| **DM Session Scope** | DM（私聊）会话范围。"main"保持连续性，"per-peer"、"per-channel-peer"、"per-account-channel-peer"增加隔离度 | 共享收件箱或多账户部署使用隔离模式 |

### Session Identity Links（会话身份链接）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Identity Links** | 将规范身份映射到提供商定义的对端ID，以便在多个通道或账户中识别同一人类用户 | 多渠道统一用户身份管理场景 |

### Session Idle Minutes（会话空闲分钟数）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Idle Minutes** | 旧版空闲重置的分钟数，用于跨非活动间隙的会话重用行为。仅为了兼容性而使用 | 与旧配置保持兼容；推荐使用sessionResetByType |

### Session Main Key（会话主键）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Main Key** | 覆盖当dmScope或路由逻辑指向"main"时用于连续性的规范主会话密钥 | 手动固定会话时配置；否则使用稳定默认值 |

### Session Maintenance（会话维护）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Disk High-water Target** | 磁盘预算清理高水位线时的目标大小，默认为磁盘预算的80% | 受限磁盘上设置更低值实现更积极的回收 |
| **Session Max Disk Budget** | 每个代理会话存储磁盘预算（如"500mb"）。警告模式报告压力，强制执行模式删除旧条目 | 限制每个代理的存储空间，防止无限制增长 |
| **Session Max Entries** | 限制存储中保留的总会话条目数 | 受限环境使用较低限制；需要更长历史时使用较高限制 |
| **Session Maintenance Mode** | 确定维护操作是仅报告（warn）还是主动应用（enforce） | 在线期间保持warn，验证安全阈值后切换到enforce |
| **Session Prune After** | 删除早于此持续时间的条目（如"30d"或"12h"） | 用作主要保留控制，与数据保留策略保持一致 |
| **Session Rotate Size** | 当文件大小超过阈值时轮换会话存储（如"10mb"或"1gb"） | 防止单文件增长，使备份/恢复操作可控 |
| **Session Parent Fork Max Tokens** | 允许线程/会话继承分支的最大父会话令牌数 | 父会话超过此值时启动新线程会话以保护性能 |

### Session Reset Policy（会话重置策略）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Daily Reset Hour** | 设置每日小时边界（0-23），仅在日常模式下有效 | 与操作员时区对齐以满足人类可读的行为 |
| **Session Reset Idle Minutes** | 空闲模式下重置前的不活动窗口，或作为日常模式下的辅助防护 | 使用较大值保留连续性，较小值处理高频线程 |
| **Session Reset Mode** | 重置策略："daily"在配置小时重置，"idle"在不活动窗口后重置 | 保持每种策略一种清晰模式，避免意外切断 |

### Session Reset by Channel（按频道重置会话）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Reset by Channel** | 按提供商/频道ID键控的特定频道重置覆盖 | 某个频道需要超出类型级别策略的重置行为时使用 |

### Session Reset by Chat Type（按聊天类型重置会话）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Reset (Direct)** | 定义直接聊天的重置策略，取代类型级别的基本会话重置配置 | 作为规范的直接消息覆盖 |
| **Session Reset (Group)** | 定义群组聊天的重置策略，连续性和噪音模式与DM不同 | 繁忙群组使用较短的空闲窗口避免上下文漂移 |
| **Session Reset (Thread)** | 定义线程范围会话的重置策略，包括重点频道线程工作流 | 线程会话需要比其他聊天类型更快或更慢过期时使用 |

### Session Reset Triggers（会话重置触发器）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Reset Triggers** | 列出在入站内容中匹配时强制重置会话的消息触发器 | 谨慎使用显式重置短语，避免意外切断上下文 |

### Session Scope（会话范围）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Scope** | 设置基本会话分组策略。"per-sender"按发送者，"global"在每个频道上下文存储一个会话 | 为了更安全的多用户行为保持"per-sender" |

### Session Send Policy（会话发送策略）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Send Policy Default Action** | 没有规则匹配时的回退操作："allow"用于简单设置，"deny"需要针对每个目的地的显式允许规则 | 需要严格控制会话工具发送目的地时使用deny |
| **Session Send Policy Rules** | 在默认操作之前评估的有序允许/拒绝规则 | 首先放置最具体的规则，避免遮蔽异常 |

### Session Store Path（会话存储路径）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Session Store Path** | 设置用于持久化会话记录的会话存储文件路径 | 需要自定义磁盘布局、备份路由或挂载卷存储时使用 |

### Session Thread Bindings（会话线程绑定）

|  |  |  |
| --- | --- | --- |
| **设置项** | **说明** | **使用场景** |
| **Thread Binding Enabled** | 线程绑定会话路由功能和重点线程传递行为的全局主开关 | 现代线程工作流保持开启；需要全局禁用时关闭 |
| **Thread Binding Idle Timeout** | 线程绑定会话的默认空闲窗口（小时），0表示禁用 | 默认24小时 |
| **Thread Binding Max Age** | 线程绑定会话的可选最大时长（小时），0表示禁用硬上限 | 需要强制会话过期时设置 |
| **Session Typing Interval** | 定期输入指示器间隔 | 增加减少话痨更新，减少获得更积极的输入反馈 |
| **Session Typing Mode** | 控制输入行为计时："instant"即时、"thinking"思考中、"message"消息 | 低容量频道保持保守模式避免不必要的输入噪音 |

# 调试

大部分都是关于程序健康状态的信息，常用的就是这个手动调试功能

# 节点

代理能操作的设备节点。了解一下，后面讲演示如何添加配置节点

### Exec Approvals（执行审批）

**核心作用**：控制 Agent 能否在远程设备/节点上执行命令

|  |  |  |
| --- | --- | --- |
| **选项** | **作用** | **使用场景** |
| **Target** | 指定谁来编辑审批规则 | Gateway=中央管理；节点=各设备自己管理 |
| **Scope** | 作用域隔离 | "Defaults"是默认规则；"main"是主配置 |
| **Security** | 默认安全模式 | **Deny**=默认拒绝所有执行，需手动审批 |
| **Ask** | 询问策略 | "On miss"=规则未命中时询问用户 |
| **Ask fallback** | UI不可用时的策略 | 防止无法弹出确认框时执行危险操作 |
| **Auto-allow skill CLIs** | 自动放行技能工具 | 开启后信任的技能脚本可直接运行 |

**典型使用场景**：

- 🔒 **高安全模式**：Security设为Deny，所有执行都需审批
- 🚀 **开发模式**：Security设为Allow，快速迭代测试
- 👥 **团队协作**：为不同团队/设备设置不同Scope规则

### ​Exec Node Binding（节点绑定）

**核心作用**：控制 Agent 执行命令时连接到哪个设备

|  |  |  |
| --- | --- | --- |
| **选项** | **作用** | **使用场景** |
| **Default binding** | 默认执行的节点 | 多个节点时指定主力执行机 |
| **per-agent binding** | 单个Agent绑定 | 指定某个AI助手只能操作特定设备 |

**典型使用场景**：

- 🖥️ **固定执行机**：开发环境只在"dev-server"执行
- 🔀 **负载均衡**：多个节点轮流执行任务
- 🛡️ **权限隔离**：财务Agent只能操作内网机器

### ​Devices（设备管理）

**核心作用**：配对和认证客户端设备

|  |  |  |
| --- | --- | --- |
| **操作** | **作用** | **使用场景** |
| **Pair** | 添加新设备 | 手机/平板/其他电脑连接控制 |
| **Rotate** | 更新令牌 | 定期轮换增强安全性 |
| **Revoke** | 撤销设备 | 设备丢失或转让时立即禁用 |

**角色权限说明**：

|  |  |
| --- | --- |
| **角色** | **权限范围** |
| `operator.admin` | 完全管理权限 |
| `operator.approvals` | 审批执行请求 |
| `operator.pairing` | 配对新设备 |
| `operator.read` | 仅查看权限 |

**典型使用场景**：

- 📱 **手机控制**：配对手机作为移动控制端
- 👥 **团队共享**：多人共用一个Gateway，每个人的设备单独配对
- 🔐 **设备回收**：员工离职后Revoke其所有设备

### ​Nodes（节点管理）

**核心作用**：显示已连接的节点设备状态

**典型使用场景**：

- 📊 **监控状态**：查看哪些设备在线
- 🔧 **远程维护**：通过Gateway管理远程节点
- 🌐 **分布式执行**：将任务分发到多个节点并行处理

### 一句话总结

|  |  |
| --- | --- |
| **模块** | **解决的核心问题** |
| **Exec Approvals** | "谁能执行什么命令？" |
| **Exec Node Binding** | "命令在哪个设备上执行？" |
| **Devices** | "谁可以连接进来？" |
| **Nodes** | "有哪些设备可以被控制？" |

### 常见配置组合

|  |  |
| --- | --- |
| **场景** | **配置建议** |
| **个人本地使用** | Security=Deny, Auto-allow开, Default binding=Any |
| **团队协作** | 按团队划分Scope, 分配不同角色的设备 |
| **安全企业环境** | Security=Deny, Ask=Always, 每次执行都审批 |
| **自动化脚本** | Auto-allow skill CLIs开, 预批准常用工具 |

### 网关、节点、代理、会话关系
