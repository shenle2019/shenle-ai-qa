---
title: "win10-VMWare安装与Centos7配置"
doc_id: 256207968
slug: vgd4wiydvrg45x05
book_id: 73651885
words: 352
updated_at: 2026-02-06T06:32:42.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/vgd4wiydvrg45x05
---
# 获取 Centos7 镜像

下载地址：<https://mirrors.aliyun.com/centos/7.9.2009/isos/x86_64/?spm=a2c6h.25603864.0.0.23d5f5ad7ZdRpw>

## 常用命令

# 下载与安装

官网下载太麻烦，可以联系班主任老师获取

本教程使用的是 15.5.7 版本

安装步骤都是下一步，注意安装位置，注册码在压缩包中有

，使用 rar 解压软件解压。<https://www.winrar.com.cn/>

# VMWare 虚拟机网络设置

记住网关，后面需要使用

# 创建虚拟机

> 点击浏览，找到下载的 iso 文件，并选择

> 如果需要配置鸿蒙就需要分配 60G

# 安装 Centos7.9

配置网络，下面也有命令的配置方式，这里是图形界面的配置

> 等待安装完成

# 网络配置

## 虚拟机网络设置

## 编辑虚拟机网络文件

在编辑之前先备份

## 重启网络服务

## 验证配置

在物理机的终端中 ping 一下设置的 ip 地址。如下图就是配置成功的效果，后面就可以使用 XShell 或者 FinalShell 等软件进行连接了
