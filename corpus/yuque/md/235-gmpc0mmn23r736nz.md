---
title: "pikachu项目部署"
doc_id: 256209649
slug: gmpc0mmn23r736nz
book_id: 73651885
words: 345
updated_at: 2026-02-06T06:44:43.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/gmpc0mmn23r736nz
---
# 环境搭建

## mysql

## apache http 服务器安装

pikachu 是一个 php 项目。需要安装 apache http 服务器来运行

### 安装

`yum install -y httpd`

### 设置开机服务

`systemctl enable httpd.service`

### 开放端口号

防火墙开启时才需要。如果是云服务器，可以百度搜索相关开放端口号的方式

### 常用命令

- `systemctl start httpd`：

## 安装 php

### 选用remi的源来安装

- `yum install -y epel-release`

- `rpm -ivh http://rpms.famillecollet.com/enterprise/remi-release-7.rpm`，中间过程输入 y 即可

成功日志

### 安装 PHP

### 链接php文件

# 部署项目

## 创建库数据

- `mysql -uroot -pRoot_1234`：这里的密码替换成自己的，不要照抄
- `` CREATE SCHEMA `pikachu` DEFAULT CHARACTER SET utf8 ; ``：创建数据库，直接复制，不要需要修改

## 设置权限

`chmod -R 777 /var/www/html`

## 上传文件

- `cd /var/www/html`
- 将项目上传到`/var/www/html`目录下，并解压

## 修改Apache配置文件

注意细节不要写错

使用`:wq`保存

## 修改数据连接

- `vim /var/www/html/pikachu/inc/config.inc.php`

## 重启 http 服务

`systemctl restart httpd`

## 在浏览器中访问

`http://8.138.153.134/install.php`，`8.138.153.134`要替换成自己部署的服务器地址，不要照抄，点击`安装/初始化`按钮
