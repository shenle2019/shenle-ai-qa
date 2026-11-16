---
title: "centos7-Mysql安装"
doc_id: 256209359
slug: up7yiyu1n6gb4oew
book_id: 73651885
words: 872
updated_at: 2026-03-10T11:01:16.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/up7yiyu1n6gb4oew
---
## 卸载旧版本

通过以下命令确认 Linux 没有安装 Mysql。参考下图

- `yum list installed | grep mysql`
- `rpm -qa | grep mysql`

### 卸载`mariadb`

`yum remove mariadb-libs -y`，不然可能会影响安装

### 卸载已安装的 Mysql

根据情况来做

## 5.7.44 版本安装

下载地址：<https://downloads.mysql.com/archives/community/>

### 上传并解压

- 上传位置没有要求
- 在`mysql-5.7.44-1.el7.x86_64.rpm-bundle.tar`这个文件所在的路径下创建目录：`mkdir mysql57`，注意命令所在的目录

- 解压到`mysql57`目录中，命令：`tar -xvf mysql-5.7.44-1.el7.x86_64.rpm-bundle.tar -C mysql57`

### 安装

安装`rpm`文件

- `cd mysql57 && yum localinstall -y mysql-community-{server,client,common,libs}-*`

安装后检查`rpm -qa | grep mysql`

### 启动 mysql 服务

- `systemctl start mysqld`
- `systemctl status mysqld`

### 查看初始密码

`cat /var/log/mysqld.log | grep password`

登录的时候手动输入，不要输入错误。这个密码每个人都不一样

### 测试登录

`mysql -uroot -p密码`：-p和密码之间不能有空格

> 第二种方式，`mysql -uroot -p`。回车后，直接复制粘贴初始密码，粘贴后不会有任何提示，按回车就好了

如果密码写错了，就会报错如下

### 修改初始密码

`ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Root_1234';`

## 8.0.39 版本安装

### 下载

### 上传到 Linux 指定目录

创建目录，`mkdir mysql`，将文件上传到 Linux，本教程中在保存在桌面上的 `mysql` 目录，然后通过`ls`命令查看

### 解压文件

使用`cd`命令进入到 `mysql` 目录，然后通过`tar -xvf mysql-8.0.39-1.el7.x86_64.rpm-bundle.tar`命令解压文件，

### 安装 rpm 文件

安装`rpm`文件，注意，保持顺序安装，复制下面所有命令，粘贴运行，更方便

- `rpm -ivh mysql-community-common-8.0.39-1.el7.x86_64.rpm`

- `rpm -ivh mysql-community-client-plugins-8.0.39-1.el7.x86_64.rpm`

- `rpm -ivh mysql-community-libs-8.0.39-1.el7.x86_64.rpm`

- `rpm -ivh mysql-community-client-8.0.39-1.el7.x86_64.rpm`

- `rpm -ivh mysql-community-icu-data-files-8.0.39-1.el7.x86_64.rpm`

- `rpm -ivh mysql-community-libs-compat-8.0.39-1.el7.x86_64.rpm`

- `rpm -ivh mysql-community-server-8.0.39-1.el7.x86_64.rpm`

### 启动服务

- `systemctl start mysqld`：启动服务
- `systemctl status mysqld`：查看服务启动状态

### 查看初始密码

`cat /var/log/mysqld.log | grep password`

### 登录 mysql

- `mysql -uroot -p`：按回车，然后输入初始密码，输入正确就会进入如下界面

### 修改初始密码

- `ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Root_1234';`

## 远程连接配置

Linux 一般作为服务器使用，所以在上面安装的数据库经常会被远程连接，一般常用两种方式

- 配置 root 用户连接：个人电脑常用，简单直接
- 创建新用户连接：公司常用方式

### 配置 root 账户连接

### 创建数据库新用户连接

### 开放 3306 端口号

### 退出 mysql 终端

输入`quit;`命令注意要带上分号

### 远程连接

#### workbench

下载地址：<https://dev.mysql.com/downloads/workbench/>

#### 终端
