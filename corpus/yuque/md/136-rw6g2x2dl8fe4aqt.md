---
title: "Python包管理器-UV"
doc_id: 256211376
slug: rw6g2x2dl8fe4aqt
book_id: 73651885
words: 1424
updated_at: 2026-02-06T06:55:31.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/rw6g2x2dl8fe4aqt
---
# 简介

- `Python` 包管理生态中存在多种工具，如 `pip`、`pip-tools`、`poetry`、`conda` 等，各自具备一定功能。
- 而今天介绍的`uv` 是 `Astral` 公司推出的一款基于 `Rust` 编写的 `Python` 包管理工具，旨在成为 “**Python 的 Cargo**”。
- 它提供了快速、可靠且易用的包管理体验，在性能、兼容性和功能上都有出色表现，为 `Python` 项目的开发和管理带来了新的选择。

官网教程：<https://docs.astral.sh/uv/>

# 安装

## Windows

## Linux 和 Macos

## 通过 pip 安装

在终端查看安装效果

# 配置国内下载源

在 Windows 系统上，可以通过以下几种方式修改 UV 的下载源，选择其中一种即可

## 通过环境变量修改

UV 提供了 `UV_DEFAULT_INDEX` 环境变量来设置默认的包索引源。

1. 打开 “此电脑” 或 “我的电脑”，右键点击选择 “属性”。
2. 在弹出的窗口中选择 “高级系统设置”。
3. 在 “系统属性” 窗口中，点击 “环境变量” 按钮。
4. 在 “系统变量” 或 “用户变量” 中点击 “新建”：

- **变量名**：`UV_DEFAULT_INDEX`
- **变量值**：设置为你想要的镜像源地址，例如 `https://mirrors.aliyun.com/pypi/simple`。

1. 点击 “确定” 保存设置。必须重新终端或相关软件

## 通过配置文件修改

UV 支持在项目级别、用户级别和系统级别使用配置文件。

### 用户级别配置文件：

- **文件路径**：`%APPDATA%\uv\uv.toml`，不清楚`%APPDATA%`所代表的路径，可在终端输入命令查看，每个人都不一样，不要照抄

- 如果文件不存在，则自己创建

再用记事本软件或其它软件打开

- 在该文件中添加以下内容：

### 项目级别配置文件：

- **文件路径**：项目目录下的 `pyproject.toml` 或 `uv.toml`。
- 在 `pyproject.toml` 中添加：

- 或在 `uv.toml` 中添加：

## 通过命令行临时指定

在命令行中运行 UV 命令时，可以直接指定镜像源：

## 注意事项

- 如果同时设置了环境变量和配置文件，环境变量的优先级更高。

|  |  |
| --- | --- |
| **镜像源** | **URL** |
| 清华大学 | <https://pypi.tuna.tsinghua.edu.cn/simple> |
| 阿里云 | <https://mirrors.aliyun.com/pypi/simple> |
| 腾讯云 | <https://mirrors.cloud.tencent.com/pypi/simple> |
| 华为云 | <https://repo.huaweicloud.com/repository/pypi/simple> |

# 常用命令

## 创建项目

使用`uv`之前，创建一个`Python`项目，就是创建一个文件夹而已。但使用`uv`来创建项目就会多一些项目配置方面的文件。这些文件可以帮我更好的进行团队管理

- 在终端中进入到指定的目录，使用`uv init`命令，使用当前的 python 版本来创建项目，自动将项目添加了 git 管理

- `uv init 项目名称 --python=版本号`：例如`uv init demo01 --python=3.9`。使用该命令，先查看 4.5.2 小节

### pyproject.toml

`pyproject.toml`中是一些项目信息

## 运行脚本

- `uv run 脚本路径`

## 依赖管理

### 添加第三方库(依赖)

- `uv add 库名`

- `uv add 库名==版本号`，下载指定版本的库，这里演示了替换的效果，因为前面已经下载过了最新版本

下载第三方库后，会在 `pyproject.toml`文件中的`dependencies`节点查看到第三方库信息

同时也会产生一个新的文件`uv.lock`，这个文件保存了其它依赖信息

### 删除依赖

- `uv remove 库名`

### 查看依赖

- `uv tree`

### 下载所有依赖

当其它人通过 git 或其它方式获取到项目后，需要重新下载依赖

- `uv sync`：下载项目中配置的依赖

## 执行 pip 命令（待完善）

- `uv pip`：执行`pip`命令
- `uv pip install`：下载依赖
- `uv pip install -r .\requirements.txt`：下载`requirements.txt`中的所有依赖
- `uv pip freeze > requirements.txt`：兼容传统格式
- `uv pip sync requirements.txt`：批量安装

​

## uv python 命令

### 常用命令

### 配置国内下载源

通过环境变量来设置

​

### 下载 Python 版本​

- `uv python install 版本号`：下载指定的版本

- `uv python install 版本号 版本号 版本号`：下载指定的多个版本

### 查看 python 的版本

- `uv python list`：查看可被使用的版本，绿色文字为已下载的版本

### 删除 Python 版本

### 切换 Python 版本

- `uv venv .venv`：使用默认版本创建虚拟环境
- `uv venv -p 版本号`：切换虚拟环境中的 python 版本

## 工具下载

### uv tool

有一些库可以当成工具来使用，比如`pytest、pycowsay、ruff`等，有些工具不需要在代码中使用，只是用来在命令行执行。

这个时候就需要使用`uv tool install 库名`来下载了

- `uv tool install ruff`：下载`ruff`工具，用来检查代码规范
- `ruff --version`：查看工具版本，验证是否下载成功

重启终端

### 临时运行

通过`uv tool`下载的命令比较麻烦，如果只想临时使用，可以使用`uvx`来代替

- `uvx 库名`不想下载依赖，但又想使用依赖，这里以`pycowsay`依赖为例

​
