---
title: "Docker使用教程"
doc_id: 256204943
slug: yrf46slf2yfvytur
book_id: 73651885
words: 2175
updated_at: 2026-02-06T06:11:16.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/yrf46slf2yfvytur
---
# 概述

## 简介

docker官网： www.docker.com

dockerhub官网： hub.docker.com

docker文档官网：docs.docker.com

Docker是基于Go语言实现的云开源项目。

Docker的主要目标是：`Build, Ship and Run Any App, Anywhere(构建，装载任何应用在任何地方)`，也就是通过对应用组件的封装、分发、部署、运行等生命周期的管理，使用户的APP及其运行环境能做到**一次镜像,处处运行**。

> 现在 Docker 在国内使用受限。

## docker的基本组成

docker。docker本身是一个容器运行载体、管理引擎。其组成包括如下三要素：

1. **镜像(image)。**是一个只读的模板。镜像可以用来创建Docker容器，一个镜像可以创建很多容器。相当于容器的模板，类比到C++中镜像就是类模板。
2. **容器(container)。**通过镜像创建出来的运行实例。容器为镜像提供了一个标准且隔离的运行环境，他可以被创建、开始、停止、删除，每个容器都是相互隔离的，就像鲸鱼身上的一个个集装箱那样。类比到C++中容器就相当于类模板new出来的一个个实例。 可以把容器看做是一个**简易版的Linux环境**(进程空间、用户空间、网络空间)和运行在其上的应用程序。
3. **仓库(repository)。**集中存放镜像文件的场所。类似于存放各种git项目的github、类似于存放各种jar包的Maven。Docker公司提供的官方的registry被称为Docker Hub。仓库分为公开(Public)仓库和私有(Private)仓库两种形式。目前最大的公开仓库就是 hub.docker.com ，国内的公开仓库包括阿里云、网易云等 都存放了大量的镜像供用户下载；私有仓库则是个人或者企业自己搭建的仓库。

# Centos7 安装 Docker

以下是在 **阿里云 CentOS 7 服务器** 上安装 Docker 的详细步骤，使用国内镜像加速，解决网络延迟问题：

## 卸载旧版本 Docker（如有）

## 安装依赖工具包

成功的日志，类似就行，下载失败就多试几次

## 添加阿里云 Docker 镜像源

## 安装 Docker 最新版本

## 启动 Docker 并设置开机自启

## 验证安装是否成功

## 配置阿里云容器镜像加速（可选但推荐）

配置不配置都没关系，国家下载源基本被禁用了

- **获取专属加速地址**：  
  登录 [阿里云容器镜像服务控制台](https://cr.console.aliyun.com/) → 左侧菜单“镜像加速器” → 复制你的专属加速器地址。

## 允许普通用户运行 Docker（可选）

重新 SSH 登录后，无需 `sudo` 即可运行 `docker` 命令。

# Mac 安装 Docker

## 下载 docker

<https://docs.docker.com/desktop/setup/install/mac-install/>。地址需要翻墙才能访问，需要的可以问老师要

剩下的就是安装后启动了比较简单

# 常用 docker 命令

以下是 **Docker 常用命令手册**，涵盖容器管理、镜像操作、网络与数据卷等场景，方便快速查阅：

先了解一下，也可以直接跳到下面的实战内容中

## 容器生命周期管理

|  |  |  |
| --- | --- | --- |
| 命令 | 说明 | 示例 |
| **运行容器** | 创建并启动容器 | `docker run -d --name mynginx -p 80:80 nginx` |
| `docker run` | `-d` 后台运行，`-p` 端口映射，`-v` 挂载卷 | `docker run -it ubuntu /bin/bash`（交互式终端） |
| **启动/停止容器** |  |  |
| `docker start <容器>` | 启动已停止的容器 | `docker start mynginx` |
| `docker stop <容器>` | 停止运行中的容器 | `docker stop mynginx` |
| `docker restart <容器>` | 重启容器 | `docker restart mynginx` |
| **删除容器** |  |  |
| `docker rm <容器>` | 删除已停止的容器 | `docker rm mynginx` |
| `docker rm -f <容器>` | 强制删除运行中的容器 | `docker rm -f mynginx` |

## 容器状态查看与操作

|  |  |  |
| --- | --- | --- |
| 命令 | 说明 | 示例 |
| **查看容器列表** |  |  |
| `docker ps` | 查看运行中的容器 |  |
| `docker ps -a` | 查看所有容器（含已停止的） |  |
| `docker ps -q` | 仅显示容器 ID | `docker stop $(docker ps -q)`（停止所有容器） |
| **进入容器终端** |  |  |
| `docker exec -it <容器> /bin/bash` | 进入运行中的容器 | `docker exec -it mynginx bash` |
| **查看容器日志** |  |  |
| `docker logs <容器>` | 查看容器日志 | `docker logs -f mynginx`（实时跟踪日志） |

## 镜像管理

|  |  |  |
| --- | --- | --- |
| 命令 | 说明 | 示例 |
| **拉取/查看镜像** |  |  |
| `docker pull <镜像名>` | 从仓库拉取镜像 | `docker pull ubuntu:20.04` |
| `docker images` | 列出本地镜像 | `docker images -q`（仅显示镜像 ID） |
| **删除镜像** |  |  |
| `docker rmi <镜像>` | 删除指定镜像 | `docker rmi ubuntu:20.04` |
| `docker rmi $(docker images -q)` | 删除所有镜像（慎用！） |  |
| **构建镜像** |  |  |
| `docker build -t <镜像名> .` | 根据 Dockerfile 构建镜像 | `docker build -t myapp:v1 .` |

## 网络与数据卷

|  |  |  |
| --- | --- | --- |
| 命令 | 说明 | 示例 |
| **网络管理** |  |  |
| `docker network ls` | 列出所有网络 |  |
| `docker network create <网络名>` | 创建自定义网络 | `docker network create mynet` |
| `docker network connect <网络> <容器>` | 将容器连接到网络 | `docker network connect mynet mynginx` |
| **数据卷管理** |  |  |
| `docker volume create <卷名>` | 创建数据卷 | `docker volume create myvol` |
| `docker volume ls` | 列出所有数据卷 |  |
| `docker volume inspect <卷名>` | 查看卷详细信息 |  |

## 系统清理与维护

|  |  |  |
| --- | --- | --- |
| 命令 | 说明 | 示例 |
| **清理资源** |  |  |
| `docker system prune` | 清理未使用的容器、网络、镜像 | `docker system prune -a`（清理所有未使用资源） |
| `docker container prune` | 删除所有已停止的容器 |  |
| **查看系统信息** |  |  |
| `docker info` | 显示 Docker 系统信息 |  |
| `docker version` | 查看 Docker 版本 |  |

# 实战示例

## Gogs

### **创建 Gogs 数据目录**

### 导出镜像

因为 docker 现在的国内镜像都无法使用了，要解决这个问题，要么使用阿里云等云服务器，要么就使用老师导出的镜像文件，然后导入到自己的 docker 中。

### 导入镜像

- 查看没有任何 gogs 镜像

- 进入到镜像保存的位置

- 导入镜像：`docker load -i gogs.0.13.2.tar`

### **运行 Gogs 容器**

### **配置示例（关键参数说明）**

### **验证安装**

### **访问 Gogs**

打开浏览器访问：`http://服务器IP:3000`

具体 Gogs 的使用，请看教程

## Mysql

#### **1. 运行 MySQL 容器（带持久化数据卷）**

#### **2. 复制文件到容器内**

#### **3. 保存容器为镜像**
