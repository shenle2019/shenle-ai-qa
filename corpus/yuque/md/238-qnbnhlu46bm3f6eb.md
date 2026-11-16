---
title: "centos7-Java环境搭建"
doc_id: 256209499
slug: qnbnhlu46bm3f6eb
book_id: 73651885
words: 171
updated_at: 2026-02-06T06:43:43.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/qnbnhlu46bm3f6eb
---
## 下载

下载地址：

- `jdk17`：<https://www.oracle.com/java/technologies/downloads/?er=221886#java17>

- `jdk11`：<https://www.oracle.com/java/technologies/downloads/?er=221886#java11>

- `jdk8`：<https://www.oracle.com/java/technologies/downloads/?er=221886#java8>

下载的时候需要登录，如果没有账号就自己注册一个，再登录就可以了

上传文件到 Linux 上，然后解压

- `tar -zxvf jdk-17.0.13_linux-x64_bin.tar.gz`
- `tar -zxvf jdk-11.0.25_linux-x64_bin.tar.gz`
- `tar -zxvf jdk-8u431-linux-x64.tar.gz`

- `mkdir /usr/local/jdk`

将解压的文件夹复制到`/usr/local/jdk`目录下，命令为：

- `cp -rf jdk-17.0.13 jdk-11.0.25 jdk1.8.0_431/ /usr/local/jdk`

通过`ls /usr/local/jdk`命令查看目录，必须和下图一样。

## 配置环境变量

将 java 的环境变量写入到系统环境变量`/etc/profile`文件中

通过`cat /etc/profile`查看

- 检查是否配置成功，`java -version`
