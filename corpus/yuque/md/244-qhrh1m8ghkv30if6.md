---
title: "centos7-安装配置Maven"
doc_id: 256209136
slug: qhrh1m8ghkv30if6
book_id: 73651885
words: 515
updated_at: 2026-02-06T06:41:24.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/qhrh1m8ghkv30if6
---
# 概述

## 简介

Maven 是一款`基于Java平台`的项目管理和整合工具，它将项目的开发和管理过程抽象成一个`项目对象模型（Project Object Model 简称 POM）`。开发人员只需要做一些简单的配置，Maven 就可以自动完成项目的编译、测试、打包、发布以及部署等工作。

官网：<https://maven.apache.org/index.html>

## 下载

其它版本下载地址：<https://archive.apache.org/dist/maven/maven-3/>。不管哪个平台都可以直接使用

## 配置环境变量

### 前提条件

### 解压文件

不需要安装，直接解压，然后配置环境变量就好了

- `unzip apache-maven-3.6.2.zip`

### 配置环境变量

## Maven 配置

配置文件在`conf`目录中，名称为`settings.xml`

### linux

编辑`vi settings.xml`，建议在 windows 上操作，然后上传到 Linux 中

### windows

# 常用命令

- `mvn clean`

- 作用：删除 target 目录（清理编译/打包生成的文件）。
- 场景：确保从头开始构建，避免残留文件干扰。

- `mvn compile`

- 作用：编译项目源代码。
- 场景：快速检查代码是否能编译通过，无需打包。

- `mvn package`

- 作用：编译 + 运行测试 + 打包（生成 JAR/WAR 等）。
- 场景：本地验证完整构建流程，生成可部署的包。

- `mvn install`

- 作用：编译 + 测试 + 打包，并将构建结果安装到本地仓库。
- 场景：本地多模块项目中，将子模块的构建结果提供给其他模块使用。

- `mvn deploy`

- 作用：将构建结果发布到远程仓库（如 Nexus、Artifactory）。
- 场景：将稳定版本的依赖共享给团队或持续集成环境。
