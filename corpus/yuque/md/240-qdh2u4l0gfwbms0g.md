---
title: "centos7-Nginx教程"
doc_id: 256209387
slug: qdh2u4l0gfwbms0g
book_id: 73651885
words: 1699
updated_at: 2026-02-06T06:42:59.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/qdh2u4l0gfwbms0g
---
# Nginx 概述

## Nginx 简介

Nginx是一款高性能的http 服务器/反向代理服务器及电子邮件（IMAP/POP3）代理服务器。由俄罗斯的程序设计师Igor Sysoev所开发，官方测试nginx能够支支撑5万并发链接，并且cpu、内存等资源消耗却非常低，运行非常稳定。

## Nginx 的应用场景

1、http服务器。Nginx是一个http服务可以独立提供http服务。可以做网页静态服务器。

2、[虚拟主机](https://cloud.tencent.com/product/lighthouse?from_column=20065&from=20065)。可以实现在一台服务器虚拟出多个网站。例如个人网站使用的虚拟主机。

3、反向代理，[负载均衡](https://cloud.tencent.com/product/clb?from_column=20065&from=20065)。当网站的访问量达到一定程度后，单台服务器不能满足用户的请求时，需要用多台服务器集群可以使用nginx做反向代理。并且多台服务器可以平均分担负载，不会因为某台服务器负载高宕机而某台服务器闲置的情况。

## 安装步骤

### 添加 Nginx 的 Yum 仓库

- `vim /etc/yum.repos.d/nginx.repo`，创建文件，并写入以下内容，使用`:wq`保存退出

### 安装 Nginx

`sudo yum install nginx -y`

### 启动 Nginx 服务

`sudo systemctl start nginx`

### 设置 Nginx 开机自启

`sudo systemctl enable nginx`

### 检查Nginx服务状态

`sudo systemctl status nginx`

### 停止服务

`sudo systemctl stop nginx`

### 防火墙设置

### 在浏览器验证

在浏览器中输入`http://服务器ip地址`即可，例如：`http://192.168.109.100/`。

## 配置文件

Nginx的默认配置文件位于`/etc/nginx/nginx.conf`。

- 编辑配置文件：`sudo vi /etc/nginx/nginx.conf`
- 修改配置后，重新加载Nginx配置 ：`sudo nginx -s reload`或`sudo systemctl restart nginx`

# 虚拟主机配置

## 什么是虚拟主机

虚拟主机是一种特殊的软硬件技术，它可以将网络上的每一台计算机分成多个虚拟主机，每个虚拟主机可以独立对外提供www服务，这样就可以实现一台主机对外提供多个web服务，每个虚拟主机之间是独立的，互不影响的。

## 虚拟主机配置方式

通过nginx可以实现虚拟主机的配置，nginx支持三种类型的虚拟主机配置：

1. 基于ip的虚拟主机
2. 基于域名的虚拟主机
3. 基于端口的虚拟主机

实际使用的过程中，我们一般常用的是用域名或是端口来区分web服务。

### Nginx配置文件的结构

介绍了什么是虚拟主机，下面介绍下nginx的配置文件结构，虚拟主机配置的位置，具体如下：

每个server就是一个虚拟主机。

## 基于端口号的虚拟主机配置

- `cd /etc/nginx/conf.d/`
- `cp default.conf server8080.conf`
- `vi server8080.conf`

- 指定端口号

- `systemctl restart nginx`：重启服务
- 开放端口号 8080，如果防火墙已经关闭则不用

### 修改响应的页面

- 创建目录，`mkdir /usr/share/nginx/test`
- 创建 html 文件，`vi /usr/share/nginx/test/index.html`，添加如下代码

- 修改配置文件，`vi /etc/nginx/conf.d/server8080.conf`

- `systemctl restart nginx`

## 基于ip的虚拟主机配置

通过 IP 地址设置虚拟主机， 而且 Linux 操作系统允许添加 IP 别名，就是在一块物理网卡上绑定多个lP地址。这样就能够在使用单一网卡的同一个服务器上运行多个基于IP的虚拟主机。

### 给虚拟机绑定多个 IP 地址

如果只需要一个 IP 地址，就不这本个操作

`vi /etc/sysconfig/network-scripts/ifcfg-ens33`

重启网络服务：`systemctl restart network`

查看 IP 地址：`ip addr`

​

### 配置步骤

- `cd /etc/nginx/conf.d/`
- `cp default.conf mutil_ip.conf`
- `vi mutil_ip.conf`

重启 nginx 服务，`systemctl restart nginx`，发现失败，如果没有遇到就不用管

解决方案， 权限拒绝，经检查发现是开启selinux 导致的

- `setenforce 0`： 临时关闭selinux
- 永久关闭`selinux` ，`vi /etc/selinux/config` ， 将SELINUX=enforcing改为SELINUX=disabled

- 开放端口号，9527

验证配置是否成功

# Nginx 反向代理

## 概述

反向代理正好与正向代理相反，对于客户端而言代理服务器就像是原始服务器，并且客户端不需要进行任何特别的设置。客户端向反向代理的命名空间(name-space)中的内容发送普通请求，接着反向代理将判断向何处(原始服务器)转交请求，并将获得的内容返回给客户端。

使用反向代理服务器的作用如下：

- 保护和隐藏原始资源服务器
- 负载均衡

## 配置

本教程以反向代理 prometheus 服务为例，

- `cd /etc/nginx/conf.d/`
- `cp default.conf proxy_pass.conf`
- `vi proxy_pass.conf`

重启 nginx 服务，`systemctl restart nginx`

- 开放端口号，8100 和 8101

## 验证效果
