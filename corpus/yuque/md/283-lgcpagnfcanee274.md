---
title: "NodeJS 环境的安装"
doc_id: 251192347
slug: lgcpagnfcanee274
book_id: 73651885
words: 1156
updated_at: 2025-12-31T07:45:21.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/lgcpagnfcanee274
---
# window10 安装 NodeJS

提供两种安装方式，二选一

## 单独安装

### 下载

目前主流的版本是 v16 和 v18。更高版本没有特殊要求不推荐安装。可以先单独安装，然后再安装 nvm，nvm 会自动管理已经安装的 nodejs

下载地址：<https://nodejs.org/zh-cn/download>

- 下载 v18 版本

- 下载 v16 版本

### 安装

注意：不建议将 nodejs 安装在 C 盘中。可能在后面的使用过程中会出现权限问题，如下图

### 配置环境变量

找到安装位置，如下图，不要照抄图片中的路径

打开环境变量界面

windows10 的版本不同，打开方式会有差异

创建 NODE\_HOME 变量，变量值为当前安装的 nodejs 目录。后面可以在 path 中使用这个变量，这样做可以方便的修改切换 nodejs 的版本。

添加到 path 中

注意：环境变量修改了，相关使用的软件都需要重启，因为这些软件对环境变量只是一次性读取，修改后不会重新读取。例如 pycharm、cmd 终端等软件，想要使用最新的环境变量都需要重启

### 验证环境变量

终端一定要使用**管理员权限**打开

### 国内下载源配置

nodejs 默认是从国外地址下载内容，速度很慢，所以需要配置国内下载源

- `npm config set registry https://mirrors.cloud.tencent.com/npm/`
- `npm config list`：查看设置内容

### 全局下载配置

在 nodejs 安装目录下，创建两个目录`node_cache`和`node_global`

配置命令，下面标红的路径不要照抄，要替换成你的实际路径

- `npm config set prefix "C:\Program Files\nodejs\node_global"`
- `npm config set cache "C:\Program Files\nodejs\node_cache"`

验证配置是否成功，`npm i -g nodemon`。全局一下载`nodemon`来演示

因为前面将 nodejs 安装在 C 盘中。所以会出现权限问题

解决方案

- 重装 nodejs 到非 C 盘，在这里就不演示了
- 修改权限

过程大概一分钟，看网速

下载成功

在配置的全局下载目录中查看

输入 `nodemon -v`发现此时还无法使用全局下载的命令，需要配置环境变量

修改 path 变量，添加`%NODE_HOME%\node_global`

然后确定保存后，重启 cmd。输入`nodemon -v`

## NVM 安装(推荐)

安装文件，如果下面连接无法下载，可以向班主任老师要

[nvm-setup.rar](https://www.yuque.com/attachments/yuque/0/2025/rar/1364680/1736760454107-eaf1f77b-99d5-4977-aa5e-8567e368a129.rar)

### 安装

`C:\Users\Duan\AppData\Roaming\nvm` 这个是隐藏路径，不建议使用，更换路径不要有中文，不要有空格。

如果电脑上没有安装 nodejs，就不会有下图中的提示。

安装完成后，环境变量会自动加上

### 环境变量

在 CMD 验证安装情况，`nvm -v`

### 设置 nvm 国内镜像

只支持 Windows 系统

### 离线安装 nodejs

当有时候无法线上下载时，如下图，就可以采用离线安装折方式

去官网下载指定的版本，<https://nodejs.org/zh-cn/download>

### nvm 常用命令

以下所有命令要使用管理员权限打开 cmd

- `nvm list available`：列出所有远程服务器的版本，下面截图是 windows 上的运行结果

- `nvm install v18`：下载 `v18`中的最新版本，也可以指定详细版本号，`nvm install 20.18.1`

- `nvm list`：查看下载的版本

- `nvm use v18`：如果有多个版本，可以通过`use`命令来指定使用的版本。使用 use 命令时 cmd 必须是通过管理员权限打开的，否则报错如下

参考链接：<https://blog.csdn.net/weixin_45682449/article/details/120948835>

- `nvm uninstall 版本号`：删除指定的版本

### 全局下载配置

这里推荐在 nvm 安装目录下，创建两个目录`node_cache`和`node_global`。

配置命令，**下面命令中红色部分不要照抄，换成自己你的路径**

- `npm config set prefix "C:\Users\Duan\AppData\Roaming\nvm\node_global"`
- `npm config set cache "C:\Users\Duan\AppData\Roaming\nvm\node_cache"`

配置好后，就算切换了 nodejs 版本，也不会影响

验证配置是否成功，`npm i -g nodemon`。全局一下载`nodemon`来演示

配置环境变量，添加`%NVM_HOME%\node_global`

然后确定保存后，重启 cmd。输入`nodemon -v`

### 国内下载源配置

nodejs 默认是从国外地址下载内容，速度很慢，所以需要配置国内下载源

- `npm config set registry https://mirrors.cloud.tencent.com/npm/`
- `npm config list`：查看设置内容
