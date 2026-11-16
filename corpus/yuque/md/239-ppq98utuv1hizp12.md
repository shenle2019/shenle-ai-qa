---
title: "centos7-VirtualBox 安装使用"
doc_id: 256209456
slug: ppq98utuv1hizp12
book_id: 73651885
words: 250
updated_at: 2026-02-06T06:43:24.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/ppq98utuv1hizp12
---
### 下载

官网地址：<https://www.virtualbox.org/wiki/Downloads>

### 历史版本下载

下载地址：<https://www.virtualbox.org/wiki/Download_Old_Builds>

本教程使用的版本为

### 安装

双击安装

> 文档中没有截图的步骤都是下一步或者默认处理

安装后启动界面如下

### 创建虚拟机

### 安装 Centos7.9

> 等待安装完成

### 网络配置

登录到虚拟机中，使用 root 账号就可以了

virtualbox 设置静态 ip 需要设置两个网卡

- `cd /etc/sysconfig/network-scripts/`
- `cp ifcfg-enp0s3 ifcfg-enp0s8`

- `ifcfg-enp0s3`：负责上网
- `ifcfg-enp0s8`：设置静态 ip，与物理连接

#### 网卡设置

关闭虚拟机

#### 修改网络配置文件

开始虚拟机

##### ifcfg-enp0s3

主要负现上外网

- `vi cd /etc/sysconfig/network-scripts/ifcfg-enp0s3`

`:wq`保存

##### ifcfg-enp0s8

设置静态 ip，负责与物理机通信

- 查看静态网关地址

此处是 192.168.56.1，所以下面的 GATEWAY=192.168.56.1，IPADDR=192.168.56.110。这个IPADDR 最后一段 110，可以自定义，范围在 10 到 250 之内就好了

- `vi cd /etc/sysconfig/network-scripts/ifcfg-enp0s8`
