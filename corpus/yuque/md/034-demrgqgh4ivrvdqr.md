---
title: "Dify搭建及使用教程"
doc_id: 256211765
slug: demrgqgh4ivrvdqr
book_id: 73651885
words: 886
updated_at: 2026-03-25T12:48:36.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/demrgqgh4ivrvdqr
---
# 概述

## 简介

官网地址：<https://dify.ai/zh>

官方文档：<https://docs.dify.ai/zh/use-dify/getting-started/introduction>

# Docker 安装 Dify

官方教程：<https://docs.dify.ai/zh/self-host/quick-start/docker-compose>

在本教程中通过 Docker 来安装这个 Dify，可以参考官方教程来完成

## 阿里云服务器安装 Docker

现在因为个人虚拟机安装使用 Docker 比较麻烦，需要翻墙，这里采用阿里云服务器来安装 Docker，会方便很多，本教程采用的就是 99 一年的服务器

### 安装 Docker

参考教程：<https://developer.aliyun.com/article/110806>

检查是否安装成功

### 添加镜像加速

地址：<https://cr.console.aliyun.com/cn-guangzhou/instances/mirrors>

## 安装 Dify

### 硬件

- CPU >= 2 Core
- RAM >= 4 GiB

### 软件

|  |  |  |
| --- | --- | --- |
| 操作系统 | 所需软件 | 说明 |
| macOS 10.14 或更高版本 | Docker Desktop | 将 Docker 虚拟机配置为至少 2 个虚拟 CPU 和 8 GiB 内存。  安装说明请参阅 [Mac 版 Docker Desktop 安装指南](https://docs.docker.com/desktop/mac/install/)  。 |
| Linux 平台 | Docker 19.03+  Docker Compose 1.28+ | 安装说明请参阅 [Docker 引擎安装指南](https://docs.docker.com/engine/install/)  和 [Docker Compose 安装指南](https://docs.docker.com/compose/install/)  。 |
| 启用了 WSL 2 的 Windows | Docker Desktop | 建议将源代码和绑定到 Linux 容器的数据存储在 Linux 文件系统中，而不是 Windows 文件系统中。  安装说明请参阅 [Windows 版 Docker Desktop 安装指南](https://docs.docker.com/desktop/windows/install/#wsl-2-backend)  。 |

### 离线安装

没有无法下载，就问老师要

也可以直接从网盘中下载

链接: <https://pan.baidu.com/s/1rQODKXmAHMDD_8JmjkJB5A?pwd=uigi> 提取码: uigi

下载完成后，记得先要将这个文件上传到 linux 服务器上。

解压成功后，如下

将`dify-1.11.4`重命名为`dify`

### 线上安装命令

比较慢，如果有 vpn 的话就会很快

### 启动 Dify

成功拉取如下图

> 下图就是拉取失败，基本就是前面 2.1.2 没有做对。如果正确的话，就能成功下载

有部分镜像无法拉取，则可以离线导入老师已经下载好的镜像。在上面的百度网般下载，然后上传到服务器中，注意文件位置。在导入之前先把之前下载的全部删除

再次进入到`dify/docker`目录下，执行`docker compose up -d`启动命令

创建完成后，输入`docker ps`查看效果如下

- 导出 dify 镜像命令如下，这个命令要了解，有可能今后会用到

> 在一台已经安装 dify 的电脑导出 dify 的 docker 镜像，命令如下
>
> ​

### 开放端口号

- 阿里云服务配置，docker 默认使用 80 端口，需要将 80 端口加入到安全组中

### 访问 Dify

- 打开管理员初始化页面以设置管理员账户：

- 完成管理员账户设置后，在以下地址登录 Dify：
