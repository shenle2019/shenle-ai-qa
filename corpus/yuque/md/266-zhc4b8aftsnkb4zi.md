---
title: "安装Allure环境"
doc_id: 256204838
slug: zhc4b8aftsnkb4zi
book_id: 73651885
words: 305
updated_at: 2026-02-06T06:10:46.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/zhc4b8aftsnkb4zi
---
# 简介

Allure是一款java语言开发的[轻量级](https://so.csdn.net/so/search?q=%E8%BD%BB%E9%87%8F%E7%BA%A7&spm=1001.2101.3001.7020)开源自动化测试报告生成框架。它支持绝大部分测试框架，比如TestNG、Junit、pytest 等。

下载地址：<https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/>

> 随堂资料中 包含对应的安装包，如果同学出现因操作系统出现的兼容性问题，需要升级或者降级版本，可以自行通过文档下载对应的安装包。
>
> tips: 如果没有出现兼容性问题，建议直接使用自带软件安装包安装。能最大限度的规避兼容问题。

# 配置环境变量

## 前提环境

需要配置 jdk 环境变量

## 配置环境变量

### Linux 或 Mac

- 上传解压文件，`unzip allure-commandline-2.18.1.zip`

配置环境变量步骤如下，不要照抄路径。将环境变量写入到`/etc/profile`

刷新环境变量：`source /etc/profile`，再执行`allure --version`，查看配置是否成功

### windows

点击新建，将上面的路径复制进来即可

打开一个新的 cmd 终端，输入`allure --version`
