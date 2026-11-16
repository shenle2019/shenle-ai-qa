---
title: "03-Flask-Web框架"
doc_id: 256210848
slug: upum3g83txnpggr5
book_id: 73651885
words: 1371
updated_at: 2026-02-06T06:52:25.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/upum3g83txnpggr5
---
# 概述

## 简介

Flask 是一个轻量级的 WSGI Web 应用程序框架。 它旨在使入门变得快速而简单，并能够扩展到 复杂的应用程序。

官网地址：<https://flask.palletsprojects.com/en/stable/>

本教程基于 Python3.10.11 和 Flask2.3.2

## 下载 Flask

### 项目虚拟环境

在创建项目时，使用虚拟环境时，需要先激活荐虚拟环境，再执行下载命令

### 使用环境变量中的虚拟环境

> pip 下载的内容会保存在 python 安装目录下的 site-packages 目录中

也可以将项目改造成项目内置的虚拟环境

- 创建虚拟环境，`python3 -m venv .venv`
- 激活虚拟环境，`.\.venv\Scripts\activate`

# 基本使用

## 创建服务器

### 处理 get 请求

### 启动服务

#### 命令启动

命令格式：`flask --app python 文件路径 run`

#### main 方法启动

### 在 Postman 测试接口

### 处理 post 请求

> 添加完后，记得重启服务器

### 支持多种请求方式

# 请求参数处理

## 路径参数

|  |  |
| --- | --- |
| `string` | （缺省值） 接受任何不包含斜杠的文本 |
| `int` | 接受正整数 |
| `float` | 接受正浮点数 |
| `path` | 类似 `string` ，但可以包含斜杠 |
| `uuid` | 接受 UUID 字符串 |

## get 请求参数

## post 请求参数

### 表单参数

### 表单文件上传参数

### json 参数

​

# 响应处理

视图函数的返回值会自动转换为一个响应对象。如果返回值是一个字符串，那 么会被转换为一个包含作为响应体的字符串、一个 `200 OK` 出错代码 和一 个 *text/html* 类型的响应对象。如果返回值是一个字典或者列表， 那么会调用 `jsonify()` 来产生一个响应。以下是转换的规则：

1. 如果视图返回的是一个响应对象，那么就直接返回它。
2. 如果返回的是一个字符串，那么根据这个字符串和缺省参数生成一个用于 返回的响应对象。
3. 如果返回的是一个迭代器或者生成器，那么返回字符串或者字节，作为流 响应对待。
4. 如果返回的是一个字典或者列表，那么使用 [jsonify()](https://dormousehole.readthedocs.io/en/2.3.2/api.html#flask.json.jsonify) 创建一个响应对象。
5. 如果返回的是一个元组，那么元组中的项目可以提供额外的信息。元组中 必须至少包含一个项目，且项目应当由 `(response, status)` 、 `(response, headers)` 或者 `(response, status, headers)` 组 成。 `status` 的值会重载状态代码， `headers` 是一个由额外头部 值组成的列表或字典。
6. 如果以上都不是，那么 Flask 会假定返回值是一个有效的 WSGI 应用并把 它转换为一个响应对象。

## 响应 json 数据

# 路由使用

创建包

# 配置文件

# 数据库框架-SQLAlchemy
