---
title: "Python环境搭建"
doc_id: 251193575
slug: evqn9bpmteqhctz4
book_id: 73651885
words: 1230
updated_at: 2025-12-31T07:51:43.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/evqn9bpmteqhctz4
---
# 下载

随堂资料中 包含对应的安装包，如果同学出现因操作系统出现的兼容性问题，需要升级或者降级版本，可以自行通过文档下载对应的安装包。

tips: 如果没有出现兼容性问题，建议直接使用自带软件安装包安装。能最大限度的规避兼容问题。

官网：<http://python.p2hp.com/downloads/>

<http://python.p2hp.com/downloads/windows/index.html>

公司课程推荐使用`3.9`或`3.10`版本

# 安装

# 检查环境变量

通过 CMD 来验证环境变量配置是否成功。打开一个新的 CMD 窗口

输入`python -V`

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

此总方式下载的内容会影响所有项目，不过当内置虚拟环境中下载了相同的库后就会优先使用内置虚拟环境中的

### 使用内置虚拟环境

内置虚拟环境中下载的内容只会影响当前项目

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
