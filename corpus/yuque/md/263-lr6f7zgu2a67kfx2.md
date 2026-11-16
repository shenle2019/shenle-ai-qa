---
title: "GOGS使用教程"
doc_id: 256205078
slug: lr6f7zgu2a67kfx2
book_id: 73651885
words: 1389
updated_at: 2026-02-06T06:12:36.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/lr6f7zgu2a67kfx2
---
# 概述

## 简介

官网地址：<https://gogs.io/>

文档地址：<https://gogs.io/docs>

- Gogs，全称为Go Git Service，是一个基于 Go 语言开发的Git服务。它提供了一个类似于GitHub的界面和功能，允许您在自己的服务器上搭建私有的Git仓库和代码托管平台（类似gitlab）。
- Gogs是一个轻量级的Git服务，其设计和性能优化使得它适合于小型团队和个人开发者。它具有Web界面，可以让您方便地管理和浏览仓库、处理问题、进行代码审查和管理团队成员。

以下是Gogs的一些主要特点：

1. 开源免费：Gogs以MIT许可证发布，可以免费自由地使用、修改和分发。
2. 轻量级：Gogs使用Go语言编写，易于部署和运行，在资源消耗方面占用较少的内存。
3. 快速和稳定：Gogs使用了一些性能优化措施来提升其响应速度和稳定性。
4. 易于使用：Gogs具有直观的用户界面，使得用户可以快速上手并进行版本控制和协作开发。
5. 集成功能：Gogs支持一些常见的功能，如问题跟踪、代码审查、Web钩子等。
6. 多种数据库支持：Gogs可以与多种常见的数据库进行集成，包括SQLite、MySQL和PostgreSQL等。
7. 支持扩展：Gogs有一个丰富的插件系统，允许用户根据自己的需求进行自定义扩展。

总之，Gogs是一个简单、易用且功能丰富的Git服务，适合小型团队和个人开发者在自己的服务器上构建私有的代码托管平台。

## 下载

下载地址：<https://gogs.io/docs/installation/install_from_binary.html>

### windows

直接解压即可

解压后，不同平台的内容都是差不多的

### Linux

这个版本只能在 Centos8 或以上使用，centos7 安装另一个版本，找老师要。

### mac（todo）

# 前置条件

启动 gogs 需要有安装 git 和 mysql

## git

## mysql

# 首次启动

启动命令

- `./gogs web`：使用默认的`3000`端口号来启动
- `./gogs web --port 8080`：指定端口号来启动

## windows

在终端中进入到 gogs 目录中，然后输入`gogs web`命令

在浏览器中输入访问地址，可看到如下图中的界面

## Linux

### 注意事项

> 这里 Linux 使用`0.13.0`版本。可以问老师要
>
> `0.13.2`这个版本在 centos7 安装有报错。在 CentOS8 或以上不会有这个问题

### 安装过程

上传到 Linux 中

通过命令来解压`tar -zxvf gogs_0.13.0_linux_amd64.tar.gz`

- `cd gogs`

- 开放端口号，如果是使用阿里云服务器，需要到安全组中去开放端口号

- `./gogs web`：运行项目

在物理机中使用浏览器访问

### 创建启动脚本（选做）

只是为了方便

在用户目录下，文件想放哪里自己定，创建`start_gogs.sh`，将下面试内容粘贴到文件中。也可以在 windows 创建好，然后上传到 Linux

添加执行权限

通过脚本运行

## Mac

操作与 Linux 一致

设置-》隐私-》仍然打开

# 配置 mysql 数据库

数据库根据自己的情况来使用，在本教程中只演示 mysql 数据。

配置前先关闭 gogs

## windows

### 创建 gogs 数据库

`` CREATE SCHEMA `gogs` DEFAULT CHARACTER SET utf8 ; ``

### 导入数据文件

## Linux 或 Mac

- 关闭 gogs 服务
- 找到 `gogs/scripts/mysql.sql` 文件，前面下载的包中有，记住这个路径，等下要用

- 进入 mysql 数据库，`mysql -uroot -p`。如果报如下错误，则表示没有安装 mysql，查看教程进行安装

### 创建 gogs 数据库

`` CREATE SCHEMA `gogs` DEFAULT CHARACTER SET utf8 ; ``

### 导入数据文件

`source /root/software/gogs/scripts/mysql.sql`

## gogs 配置 mysql 数据库

再次运行`gogs`服务

# 应用设置

## 服务器设置

## 管理员设置

点击立即安装

修改如下

## 配置完成效果

停止服务，也看可以看到生成一份配置文件`custom/conf/app.ini`。在这个配置文件中可以修改相关配置

# gogs 重启(重要)

## windows 的问题

在 windows 重新启动 gogs 时，使用的命令要注意

重启需要在终端使用正确的命令格式`.\gogs.exe web`，否则报错如下

注意`.\gogs.exe web`是反斜杠，回车键上面的那个

使用正确的命令则可以成功

# Gogs 基本使用

## 管理面板

## 用户管理

### 创建新的账户

## 组织管理

### 创建组织

## 创建仓库

### 添加组织仓库

在上图中

### 添加用户仓库

### 创建仓库

### 仓库设置

#### 基本设置

滚动到最下面

#### 添加协作者

# 结合 git 使用

## 示例

### 复制地址

### 在 Pycharm 中使用

创建`1.txt`

刷新页面就可以看到内容了

## 更多内容
