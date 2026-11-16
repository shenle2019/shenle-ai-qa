---
title: "02-Pytest框架"
doc_id: 256210844
slug: zvbvno5pnhu3a59q
book_id: 73651885
words: 841
updated_at: 2026-02-06T06:52:23.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/zvbvno5pnhu3a59q
---
# 概述

## 简介

`pytest` 是一个使构建简单和可伸缩的测试变得容易的框架。测试具有表达性和可读性，不需要样板代码。几分钟后就可以开始对应用程序或库进行小的单元测试或复杂的功能测试。

官网：<https://docs.pytest.org/en/stable/>

## 安装

在项目根目录下，执行`pip install pytest==8.0.2`

### 查看安装的版本

- `pytest --version`

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

## 升级 pip 版本

有时候在执行 pip 命令时，会有如下提示，这个直接复制下面提示中的命令，粘贴到终端中运行即可。

- `python.exe -m pip install --upgrade pip`

等待下载完成后即可

## install

- `pip install 库名`：安装指定的库
- `pip install 库名==版本号`：安装指定的版本的库
- `pip install -U 库`：升级指定的库
- `pip install -i https://mirrors.aliyun.com/pypi/simple/ 库名`：从指定源安装，示例就是从`https://mirrors.aliyun.com/pypi/simple/`下载库

## uninstall

- `pip uninstall 库名`：卸载指定库，会询问是否删除
- `pip uninstall 库名 -y`：不会询问，直接删除

## show

- `pip show 库名`：查看已安装库详细信息

## list

- `pip list`：查看已经安装的库

## freeze

- `pip freeze`：查看项目下载的库及版本

在项目开发中，为了方便团队成员统一环境，我们可以创建一个包含所有依赖的requirements文件

- `pip freeze > requirements.txt`：将项目中的库保存到`requirements.txt`文件中，文件名可自定义
- `pip install -r requirements.txt`：批量安装`requirements.txt`文件中的库

# 基本使用

## 创建测试用例

### pytest 用例运行规则

1. pytest将在当前目录及其子目录中运行所有格式为 `test_**.py` 或者 `**_test.py` 文件
2. 测试方法/测试函数 默认必须是 test开头
3. 测试类必须是 Test开头
4. 测试类不能有构造方法\_\_init\_\_

### 函数写法

### 类写法

## 运行测试用例

## 断言
