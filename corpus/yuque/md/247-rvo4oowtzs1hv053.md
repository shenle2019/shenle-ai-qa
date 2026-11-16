---
title: "win10-Java环境搭建"
doc_id: 256208211
slug: rvo4oowtzs1hv053
book_id: 73651885
words: 534
updated_at: 2026-02-06T06:34:20.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/rvo4oowtzs1hv053
---
# 下载

> 随堂资料中 包含对应的安装包，如果同学出现因操作系统出现的兼容性问题，需要升级或者降级版本，可以自行通过文档下载对应的安装包。
>
> tips: 如果没有出现兼容性问题，建议直接使用自带软件安装包安装。能最大限度的规避兼容问题。

主要使用JDK8这个版本

下载地址：<https://www.oracle.com/java/technologies/downloads/#java8>

JDK11下载地址：<https://www.oracle.com/java/technologies/downloads/#java11-windows>

本课程主要使用JDK8，也可以使用JDK11，其它版本尽量不要用。

下载时会要求先登录Oracle账号，如果没有就注册一个，按注册步骤输入即可。

## 安装JDK

找到下载的JDK软件，双击运行。基本都是下一步

下一步，等待安装完成，即可。

## 目录介绍

> jre-1.8目录不需要关心，了解即可。因为在JDK目录中也有一个JRE目录，其和jre-1.8目录是一样，即开发环境是包含了运行环境。

# 配置环境变量

需要将JDK中的bin目录配置到系统的环境变量中，这样可以方便程序员或者第三方软件(Idea、Eclipse)快速的找到Java的相关命令。

> 上面的用户变量或系统变量，二选一，优先使用系统变量，如果没有，再去用户变量中找，所以同一个配置，只需要在一个地方配置即可。
>
> 简单一点可以直接把jdk/bin目录路径直接复制到path中即可。
>
> 标准方式，是先创建一个JAVA\_HOME系统变量来保存JDK的目录，推荐，因为可能会有一些软件会用到JAVA\_HOME这个变量

在`path`中添加红框中的内容

> 完成后，点击确定关闭所有窗口。然后重新打开一个新的终端，通过输入`java -version`命令来查看是否配置成功。
