---
title: "接口自动化课程"
doc_id: 256211633
slug: vttuaedrt7a2pfmk
book_id: 73651885
words: 4583
updated_at: 2026-02-06T06:56:51.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/vttuaedrt7a2pfmk
---
# 概述

## 接口定义

API（Application Programming Interface，应用程序编程接口）是一组定义、协议和工具，用于实现不同软件应用之间的通信和数据交互，允许开发者通过预先定义的接口来访问软件功能或数据，而无需了解其底层实现细节。

- **本质作用**：作为不同软件系统之间的 “桥梁”，允许应用程序通过标准化接口获取数据或执行操作，例如天气应用获取气象数据、电商 APP 调用支付接口等。

## 接口测试核心要素

### 接口组成

接口都是由开发人员设计并开发完成的。测试人员需要了解接口的组成，一般公司会有接口说明文档

- URL：就是接口的访问地址，由协议+服务器 IP+端口号/资源地址?Params组成。

- 示例：`http://localhost:8080/login.html`或`http://localhost:8080/api/login`
- 协议：`http://`或`https://`
- 服务器 IP：用来找电脑的，本机访问可以使用`localhost`和`127.0.0.1`，局域网访问，需要使用局域网 IP，外网访问需要使用外网 IP 或域名
- 端口号：用来找电脑上的程序的，默认是 80，可以不写，其它端口号都需要指定，格式为`:端口`。同一个端口只能被一个程序使用，否则就会出现端口已被使用的提醒
- 资源地址：`/资源路径`，例如登录页面，`/login.html`或者登录接口，`/api/login`等

- Method：接口的请求方式，主要分为`get`和`post`，在`restful`接口中还会细分为`put`和`delete` 等，但本质上这些都是`post`。
- Headers：请求头信息
- Params：地址参数信息，也是 get 请求的参数，不要放需要保密的数据，且长度有限制。

- 格式：`?参数名=值&参数名=值`，多个之间使用`&`连接，中间不能有空格

- Body：请求体，post 请求的参数
- 接口返回状态码（200/404/500等）

- 200：接口响应成功
- 404：接口地址不存在，基本就是写错了
- 500：服务端报错

- 响应格式（JSON/XML）：接口响应的数据一般是 json 或 xml 格式，也有可能是一段文本

- json：大部分接口都是
- xml：部分接口，现在已经不多了，缺点标签太多，占用流量比数据本身都要大

### 接口访问范围

- 本机访问：接口的服务器 IP 部分`localhost`和`127.0.0.1`，则说明这个接口只能在这一台电脑上访问，其它电脑不可以访问
- 局域网访问：接口的服务器 IP 部分是局域网 IP，则支持同在一个局域网内的电脑访问，

- 格式：`192.168.xxx.xxx`

- 外网访问：<http://novel.hctestedu.com/user/register.html>。这个地址支持任何一台能上网的电脑访问。novel.hctestedu.com 是服务器域名，域名会被解析为外网 IP 地址。

域名比 IP 地址好记忆，所以一般外网的服务都会使用域名，内网服务一般都是 IP 地址

## 接口拦截

在部分公司可能没有接口说明文档，这个时候测试人员需要通过一些工具来拦截接口，从而了解接口的组成与使用，常用的方法有浏览器的开发者工具(F12)或使用 Fiddler 工具。在有些场景还是需要 Fiddler 工具才能拦截到接口信息，比如登录接口，在浏览器工具经常会因为页面跳转了，导致无法拦截到需要的接口。因为页面跳转了导致浏览器开发者工具也会刷新

### 开发者工具使用

以 Chrome 浏览器开发者工具为演示

- get 请求

- post 请求，一般登录和注册接口都是 post，地址是<http://novel.hctestedu.com/user/register.html>

- 需要认证的接口，一般需要带上 token 信息。在这里以我的书架接口来演示

要注意到这个 token 是怎么传递的，然后在 Postman、Jmeter、Python 来访问这个请求的时候，要保持一致

### Fiddler 使用

Fiddler 安装全部下一步即可。

## 请求接口

请求接口，可以用浏览器，也可以用一些工具：

- Postman
- Jmeter
- Python 的接口请求库，requests，这是一个第三方库，需要通过 pip 命令来下载，才能使用

### postman 测试接口

从上面拦截的接口中，可以观察到以下几个信息

此时已经可以成功访问了。实际工作中基本这几个要清楚，后面可能还需要 token 信息等。基本都是在请求头或请求参数中处理，还有 cookie 信息

# pip 命令详解

pip是Python的官方包管理工具，其名称源自“Pip Installs Packages”。它最初由Julien Phalip在2008年创建，目的是为了简化Python包的安装过程。随着时间的推移，pip逐渐成为了Python社区的标配工具。

- 通过`pip -V`查看其版本信息

## Python 两种虚拟环境区别

在创建 Python 项目时，有两种常见的虚拟环境，

- 一种是使用系统环境变量配置中的
- 一种是使用保存在项目中的虚拟环境，称为内置虚拟环境

### 使用环境变量中虚拟环境

创建项目如下图

创建后，就一个项目目录

这种方式创建的项目，在使用 pip 下载内容时，默认会将下载的内容保存到用户目录下，类似如下图中的提示目录。要使用下载的内容，需要配置环境变量

> 此总方式下载的内容会影响所有项目，不过当内置虚拟环境中下载了相同的库后就会优先使用内置虚拟环境中的

### 使用内置虚拟环境

> 内置虚拟环境中下载的内容只会影响当前项目

## 升级 pip 版本（了解）

有时候在执行 pip 命令时，会有如下提示，这个直接复制下面提示中的命令，粘贴到终端中运行即可。

- `python.exe -m pip install --upgrade pip`

等待下载完成后即可

## install（掌握）

- `pip install 库名`：安装指定的库
- `pip install 库名==版本号`：安装指定的版本的库
- `pip install -U 库`：升级指定的库
- `pip install 库名 -i https://mirrors.aliyun.com/pypi/simple/`：从指定源安装，示例就是从`https://mirrors.aliyun.com/pypi/simple/`下载库，这是临时配置

示例下载`requests`模块：

- `pip install requests`
- `pip install requests -i https://mirrors.aliyun.com/pypi/simple/`

### 永久配置（推荐）

- Mac/Linux

- windows

## uninstall

- `pip uninstall 库名`：卸载指定库，会询问是否删除
- `pip uninstall 库名 -y`：不会询问，直接删除

## show

- `pip show 库名`：查看已安装库详细信息

## list

- `pip list`：查看已经安装的库

## freeze（掌握）

- `pip freeze`：查看项目下载的库及版本

在项目开发中，为了方便团队成员统一环境，我们可以创建一个包含所有依赖的requirements文件

- `pip freeze > requirements.txt`：将项目中的库保存到`requirements.txt`文件中，文件名可自定义

- `pip install -r requirements.txt`：批量安装`requirements.txt`文件中的库

## 离线安装依赖

### download

在测试中经常会遇到不能上网的内网电脑或服务器，此时就可以使用 download 命令，将需要的库下载后，再发送到离线电脑上进行安装

download 命令会将需要的库下载打包成 whl 文件，如果没有 whl 文件，就会下载成源码，这个时候可以使用 wheel 这个库来将源码打包成 whl 文件

- `pip download requests`：下载到当前命令所在的目录
- `pip download requests -d whl_packages`：下载到指定的目录

部分依赖库下载的时候没有 whl 文件，是一个源码包，例如

`pip download jsonpath -d whl_packages`。此时可以使用 wheel 这个库来处理。

​

### wheel 依赖库

下载：`pip install wheel`

- `cd .\whl_packages\`：先进入到源码文件所在的目录中
- `pip wheel .\jsonpath-0.82.2.tar.gz`：执行打包命令

### 离线安装

- 安装单个`whl`文件，注意所在的目录

### 安装多个`whl`文件

- 一次性下载`requirements.txt`文件中所有的依赖，`pip download -d 指定的目录 -r requirements.txt`，要注意当前所在的命令目录，应该是`requirements.txt`所在的目录

- `pip download -d .\whl_packages\ -r requirements.txt`，一定要注意命令所在的目录

- 删除虚拟环境文件夹`.venv`，然后再重新添加

`pip install --no-index --find-links=./whl_packages -r requirements.txt`，注意命令执行时所在的目录

# Requests 请求模块

Requests 模块是 Python 中用于发送 HTTP 请求的强大工具，它简化了与 Web 服务器交互的过程，让开发者可以轻松地发送各种类型的 HTTP 请求并处理响应。

Requests 模块并非 Python 内置，需要通过 pip 安装

**核心特点包括**：

- **简洁易用**：提供简单直观的 API，无需手动处理复杂的 HTTP 细节（如连接管理、Cookie 处理等）。
- **功能全面**：支持所有 HTTP 方法（GET、POST、PUT、DELETE 等）、文件上传、认证、会话管理等。
- **兼容性强**：支持 HTTP、HTTPS 协议，以及连接池、代理设置等高级功能。

## 基本使用

，可以先看下接口文档，测一下其它接口。也可以自己拦截

右键运行脚本，打印内容如下，这个结果，只知道请求是成功了，但具体的数据无法查看。此时可以通过 debug 来处理

这是访问首页的响应结果内容

这是注册的响应结果内容

再去获取最近的验证码，然后换一个新的账号看下效果

## Json 格式的请求参数

在 post 请求中，上面演示了表单数据。还有一种是 json 数据。这里需要通过另一项目来演示

## 请求头处理

通过读书屋我的书架接口来演示，先拦截读书屋登录接口。可以通过下面的操作来快速获取接口地址

因为登录成功后会发生页面跳转，在浏览器中不方便拦截，所以在这里通过 Fiddler 来拦截

根据上面的数据结构来写对就的代码获取 token 数据

## 常用认证机制

### JWT 机制（记住）

一般是开发去做，但测试需要知道原理

##### **基本概念**

- **无状态认证**：用户信息通过加密的 Token 存储在客户端，不依赖服务器存储。
- **Token 结构**：**Header.Payload.Signature**

- **Header**：包含 Token 类型和签名算法（如 `HS256`）。
- **Payload**：包含声明（Claims），如用户 ID、权限、过期时间等。
- **Signature**：使用密钥对 Header 和 Payload 签名，防止篡改。

##### **工作流程**

1. 用户登录时，服务器生成 JWT 并返回给客户端。
2. 客户端存储 JWT（通常在 `localStorage` 或 `Cookie` 中）。
3. 后续请求中，客户端在请求头中携带 JWT（如 `Authorization: Bearer <token>`）。
4. 服务器验证签名，解析 Payload 获取用户信息。

##### **优缺点**

- **优点**：

- 无状态：适合微服务和分布式系统。
- 跨域支持：可通过 HTTP Header 传递，支持 CORS。
- 扩展性强：可自定义 Payload 包含丰富信息。

- **缺点**：

- Token 体积大：Base64 编码后数据较长。
- 安全性风险：若存储在 `localStorage` 中，易受 XSS 攻击。
- 注销困难：Token 一旦发放，无法主动失效（需配合黑名单机制）。

### Session 机制（了解）

##### **基本概念**

- **会话跟踪**：服务器通过 Session ID 识别用户，保存在服务器端的内存或数据库中。
- **工作流程**：

1. 用户登录时，服务器创建 Session 对象并生成唯一 Session ID。
2. Session ID 通过 Cookie 发送给客户端。
3. 后续请求中，客户端携带 Session ID，服务器验证并获取用户信息。

##### **优缺点**

- **优点**：

- 数据存储在服务器端，安全性较高。
- 实现简单，依赖成熟的 Web 框架。

- **缺点**：

- 扩展性差：分布式系统中需要 Session 共享机制。
- 服务器压力大：存储大量 Session 数据。
- 跨域支持困难：依赖 Cookie，受同源策略限制。

### 两者对比

|  |  |  |
| --- | --- | --- |
| **特性** | **Session** | **JWT** |
| **存储位置** | 服务器端（内存 / 数据库） | 客户端（Cookie/LocalStorage） |
| **状态性** | 有状态 | 无状态 |
| **扩展性** | 差（需 Session 共享） | 好（不依赖服务器存储） |
| **跨域支持** | 差（依赖 Cookie） | 好（通过 Header 传递） |
| **安全性** | 较高（数据在服务器） | 中等（需防止 XSS 和 CSRF） |
| **性能** | 高（验证仅需比对 ID） | 低（每次需解密和验证签名） |
| **适用场景** | 单服务器应用、对安全性要求高 | 分布式系统、跨域服务、移动端 |

## 文件上传

在读书屋中涉及到两个接口，一个是文件上传，然后将上传后的路径更新到路径的头像路径中

页面地址：<http://novel.hctestedu.com/user/setup.html>

# Pytest

## 概述

### 简介

`pytest` 是一个使构建简单和可伸缩的测试变得容易的框架。测试具有表达性和可读性，不需要样板代码。几分钟后就可以开始对应用程序或库进行小的单元测试或复杂的功能测试。

官网：<https://docs.pytest.org/en/stable/>

### 下载

在项目根目录下，执行`pip install pytest==8.0.2`​

### 查看安装的版本

- `pytest --version`

## 基本使用

### 创建用例

### 运行

### 用例自动发现的规则

### 常用插件

### 用例顺序

### 夹具

### 参数化

### 用例标记

### 重新运行失败的测试用例

### pytest.ini 配置文件

# CICD
