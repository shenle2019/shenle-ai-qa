---
title: "centos7-NodeJS环境搭建"
doc_id: 256209427
slug: tu3sb1og7uauk4bx
book_id: 73651885
words: 1595
updated_at: 2026-03-28T07:46:57.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/tu3sb1og7uauk4bx
---
# 下载安装

NodeJS 的下载安装有两种方式

- 下载对应的 NodeJS 版本，然后安装配置。简单，但切换版本困难
- 通过 NVM 下载安装，然后配置。上手不是太难，需要学习相关命令，可以随意切换版本

## NVM

### 在线安装

- `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash`。但国内可能会下载不了，报错如下

### 离线安装

- 从`https://github.com/nvm-sh/nvm/releases/tag/v0.40.1`，在此处先下载。如果打不开，可以向老师要

这里提供一个下载地址

下载后，上传到 Linux，并解压，命令为：`tar -zxvf nvm-0.40.1.tar.gz`

安装 nvm。

### 配置环境变量

在环境变量中添加如下配置，`vim /etc/profile`

保存后，刷新环境变量`source /etc/profile`。然后通过`nvm -v`验证是否配置成功

### nvm 常用命令

部分命令在 Linux 上运行会不支持

- `nvm list available`：列出所有远程服务器的版本，下面截图是 windows 上的运行结果

- `nvm install v18`：下载 `v18`中的最新版本，也可以指定详细版本号。

- `nvm list`：查看下载的版本

- `nvm alias defalut v18.20.5`：修改默认版本，永久生效

- `nvm use v18`：如果有多个版本，可以通过`use`命令来指定使用的版本，不过只是一次性的。每次重新连接 Linux 服务器后都会使用默认指向的版本
- `nvm delete v18`：删除指定的版本

> CentOs7 使用 V16 以上版本会报错
>
> - 建议使用 v16 版本，因为解决上面的问题非常麻烦，至少需要 3 个小时

## 单独安装 nodejs

下载地址：<https://nodejs.org/zh-cn/download/prebuilt-binaries>

### 上传文件

本教程在 Mac 上通过 FinalShell 上传

### 解压文件

`tar -xvf node-v16.20.2-linux-x64`

将解压后的文件夹复制到`/usr/local/nodejs`目录，命令为：`cp -R node-v16.20.2-linux-x64 /usr/local/nodejs`

### 环境变量配置

本教程主要演示 CentOs7 上的配置方式

验证配置效果

# NodeJS 配置

## npm 国内下载源配置

`npm config set registry https://mirrors.cloud.tencent.com/npm/`

设置完成后，可以通过`npm config list`查看

## 全局下载配置

> 不管是 nvm 下载的，还是单独下载的 nodejs 都可以如下配置

- `cd /usr/local/nodejs`：进入到 nodejs 目录
- 创建两个文件夹`mkdir node_cache`和 `mkdir node_global`

- 将创建的目录配置到 npm 中

- `npm config set prefix "/usr/local/nodejs/node_global"`
- `npm config set cache "/usr/local/nodejs/node_cache"`
- 配置完成后，通过`npm config list`查看是否配置成功

将 node\_global 目录配置到环境变量中，nvm 下载的 nodejs 也可以如下配置，不需要修改什么

验证配置效果，通过`npm i -g nodemon`全局下载`nodemon`工具，然后通过`nodemon -v`验证，效果如下

可以在`node_global`目录下看下载的内容

# 后台运行 nodejs 项目

- 通过`nginx`运行，在这里不再多赘述
- 通过`pm2`命令来运行

## 全局下载 pm2

- `npm i -g pm2`
- 通过`cd`命令进入到项目根目录下

- 通过`pm2 start app.js`后台运行项目

- 如果上面的命令启动成功，但是无法访问，可以试下，`npm run prd`

在浏览器中查看效果如下

## pm2 其它命令

- `pm2 status`：查看运行状态

- `pm2 stop app.js`：停止指定的项目

# 安装 nodejs-v18 版本的问题

`tar -xvf node-v18.20.5-linux-x64.tar.xz`

具体问题如下图

> 如果安装的是 v18 或以上版本，会出现如下错误
>
> 具体原因，新版的node v18开始 都需要GLIBC\_2.27支持，可是目前系统内却没有那么高的版本

执行命令

## 升级 make

> make check 命令在执行完后，会有如下提示，不用处理

安装后，可通过`make -v`验证

## 升级 gcc

命令执行完后，结尾参照下图

> 报错如下

> 编译完成

安装完成

通过`gcc -v`检测

## 下载安装glibc-2.28

安装 bison 依赖，`yum install -y bison`，否则报错如下：

配置成功

> 如果前面的 make 和 gcc 升级没有做，就会报错如下

> 编译完成后，提示如下，虽然显示报错，但可以不用处理
>
> 没有错误的话，显示如下

## 更新libstdc++.so.6.0.26

在上面操作完成后，输入`node -v`报错如下，此时需要更新一下libstdc++.so.6.0.26

如果没有 unzip 命令，则下载`yum install unzip -y`

> 我在下载 unzip 时，经常卡死，且无法使用 Ctrl + C 命令终止，如下
>
> 此时需要重新连接到服务器，然后通过`kill -9`来杀进程解决
>
> 出现如上图情况，使用 Ctrl + Z 终止，然后通过`kill -9`来结束进程
>
> 重新执行时，出现如下问题
>
> 通过以下命令来解决
>
> - `mv /var/lib/rpm/__db* /tmp`
> - `rpm --rebuilddb`
> - `yum clean all`
>
> 再次执行`yum install -y unzip`就可以正常安装了

此时，所有问题都已经解决

​
