---
title: "课题九：AI界面UI自动化脚本执行"
doc_id: 256212039
slug: bdl19gdxm7dqdqut
book_id: 73651885
words: 17922
updated_at: 2026-02-06T06:59:24.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/bdl19gdxm7dqdqut
---
# 模块效果图

界面完成一样

提交后，就会打开浏览器执行，如果选择使用无头模式服务，就无法看到浏览，实际工作中以无头模式运行

到执行记录页面中查看结果

点击可以进入下面的预览界面

复制执行

# 数据库设计

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Column Name | Datatype | PK | NN | AI | Default/Expression | 字段注释 |
| id | INT | ✔ | ✔ | ✔ |  | 执行记录主键ID（自增） |
| project\_id | INT |  |  |  | NULL | 关联的项目ID |
| name | VARCHAR(255) |  |  |  | NULL | 执行批次名称 |
| exec\_type | VARCHAR(255) |  |  |  | NULL | 执行类型（如“web 网页”“安卓设备”“IOS 设备”） |
| case\_ids | LONGTEXT |  |  |  | NULL | 本次执行包含的用例ID集合（通常用逗号分隔存储） |
| details | LONGTEXT |  |  |  | NULL | 执行的用例详细信息 |
| desc | VARCHAR(1024) |  |  |  | NULL | 执行结果 |
| exec\_param | LONGTEXT |  |  |  | NULL | 执行参数（如环境配置、并发数、超时时间等） |
| exec\_status | VARCHAR(255) |  |  |  | NULL | 执行状态（如“执行中”“已结束”“异常结束”） |
| created\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP | 执行记录创建时间 |
| updated\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP ON UPDATE CURRENT\_TIMESTAMP | 执行记录更新时间（自动刷新） |

# 重点知识

## 基于 PlayWright MCP 运行 WebUI 测试用例

### PlayWright 基础

Playwright 是微软推出的一款**跨浏览器自动化测试 / 爬虫工具**，支持 Chrome、Firefox、Edge、Safari 等浏览器，核心优势是 API 简洁、跨平台、支持无头模式、能自动等待元素加载，兼顾稳定性和效率。下面演示的是 Python 环境使用

### MCP 基础

MCP 的全称是 Model Context Protocol（模型上下文协议），通过这个协议，让各种工具能够支持直接通过ai智能体进行调用

### PlayWright MCP 环境搭建

Playwright MCP 是基于 **Model Context Protocol（模型上下文协议）** 的浏览器自动化服务，主要面向 AI 场景：

1. **核心能力**：为大语言模型（LLM）提供结构化的网页交互能力，通过可访问性快照而非截图与网页交互，性能更优。
2. **典型场景**：AI 驱动的网页自动化、跨客户端的统一浏览器管控、低配置设备的浏览器能力调用。
3. **技术优势**：服务端集中管理浏览器实例，支持会话复用与上下文隔离，既保证了资源效率，又能确保不同客户端的操作安全隔离。
4. MCP服务与传统Playwright用法的区别

|  |  |  |
| --- | --- | --- |
| 对比维度 | 传统Playwright用法 | Playwright MCP用法 |
| 浏览器部署位置 | 客户端本地（需安装浏览器/驱动） | MCP服务端（客户端无需部署） |
| 调用方式 | 本地直接调用浏览器API | 客户通过网络远程调用MCP服务API |
| 资源占用 | 客户端占用浏览器资源 | 服务端集中占用浏览器资源 |
| 环境适配 | 需针对客户端环境适配驱动 | 仅需适配MCP服务端环境，客户端无依赖 |
| 共享性 | 无法共享，每个脚本独立启动浏览器 | 多客户端可共享MCP服务的浏览器资源 |

在前端项目中执行以下命令，本项目主要是在 Nodejs 中搭建`Playwright MCP`服务

下载成功后，在对应的位置中可以看下如下内容，注意版本号

- mac 上的 nvm 效果如下

- windows 上的 nvm 效果如下

- 启动`PlayWright MCP`服务

- `--port 8931`：指定服务监听 **8931 端口**
- `--viewport-size "1920,1080"`：固定所有新启动页面的**默认视口大小**
- `--output-dir /tmp/playwright_mcp`：指定服务**日志 / 截图 / 视频**的输出目录
- `--host 0.0.0.0`：支持所有 ip 格式访问，支持`localhost、127.0.0.1、局域网 ip`这三种方式
- `--headless`：无头模式
- 其它参数可以通过`mcp-server-playwright -h`命令获取学习

### 示例 Demo

## 基于 Mobile MCP 运行移动端用例

### Mobile MCP 环境搭建

- 全局下载，需要配置，`npm i -g @mobilenext/mobile-mcp`

- 启动服务，`mobole_mcp` 无法指定截图的目录，默认截图产生在命令执行的目录中

- 在项目中使用，简单易用，但每次会下载最新版本

下图中的警告无所谓，也可以使用警告中的版本

这个是没有警告的

> 注意，上面的命令的执行位置，因为后面产生的截图也在这个位置

### 安卓模拟器安装与启动

- 在`Mac`电脑上，可以安装`AndroidStudio`来安装原厂模拟器。可以直接使用安卓手机

- 下载地址：<https://developer.android.google.cn/studio?hl=zh-cn>
- 教程：<https://developer.android.google.cn/studio/run/managing-avds?hl=zh-cn>

- 在`Windows`上，可以安装雷电模拟器，<https://www.ldmnq.com/?n=6000>

- 在`Mac 电脑`上，打开模拟器即可，注意安卓和`IOS`模拟器只能打开一个，两个都打开只会在一个上执行。必须安装`Xcode`

### 示例 Demo

依然使用上面的示例，切换一个`MCP`服务就好了

- 提示词也要记得换一下

- 前端日志

- 后端日志，这个结果在实际请求中我们再写处理代码

- 执行中后的截图，这个保存位置由 mcp 服务启动命令所在的目录定的

## 封装提取函数

# 接口设计

## 数据库操作模块

## 路由模块

复制前面的路由模块

### 执行 UI 任务

## 加载路由模块

## Apifox 测试接口

# 前端页面

## 页面基本布局完成

- 添加`api`文件

- 先复制之前的内容代码

- 添加对应的路由代码

- 修改`AgentView`

## 实现用例查询功能

### 接口设计

接口测试

### 页面布局

## 查看用例

## 创建 AI 测试任务

- 选择好任务需要执行的测试用例，再指定任务的类型（WEB 网页、安卓、IOS）
- 点击创建 AI 测试任务，将用例 id 发送给后台接口，提取出相关参数并返回给前端，并在弹窗中显示
- 用户输入相关参数后，提交保存任务到数据库，并执行任务，执行任务过程中会对每个步骤进行截图
- 支持选中不同页面的测试用例

### 任务参数提取接口

删除了一个服务器参数，在 web 中不需要

### 任务参数处理界面

### 保存 AI 测试任务接口设计

接口测试

### 保存 AI 测试任务功能实现

# AI 测试执行记录

基本功能没什么变化，只是查看任务功能有些需要调整

## 查看测试任务

## 添加图片请求映射

每个步骤的截图默认是无法访问的，所以需要实现一个图片的请求服务。

# 完整代码

## 优化后的提示词
