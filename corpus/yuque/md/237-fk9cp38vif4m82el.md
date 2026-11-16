---
title: "读书屋环境搭建"
doc_id: 256209548
slug: fk9cp38vif4m82el
book_id: 73651885
words: 1391
updated_at: 2026-02-06T06:44:05.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/fk9cp38vif4m82el
---
# 领取资料

找班主任领取资料

# 搭建环境

JDK 要求版本是 JDK8

## windows

## linux

## macos

# 部署项目

## Linux

解压项目资料，全部上传到 Linux 服务器上的 novel 目录中，如果没有 novel 就创建

1. 将 novel-templates.zip解压后的templates文件夹放在与 novel-front-3.5.4.jar 同级目录下

1. `unzip novel-templates.zip`
2. `unzip`命令没有，则使用`yum install -y unzip`下载

1. 将 novel-temp.zip 解压后的 temp 文件夹放在根目录下（linux 就 / 目录）（windows的话，你放到对应的 盘符 根目录，比如你的 novel-front-3.5.4.jar 在D盘，就把解压后的temp放在 D 盘目录下 ）

1. `unzip novel-temp.zip`，解压
2. `mv temp /`，剪切到根目录

1. 必须要有 JDK环境，必须要有Mysql服务器

1. 要在mysql服务器上面创建对应的数据库， 以及账户。然后运行 novel-plus.sql 内的语句，生成对应的表和数据

1. 通过命令`mysql -uroot -p`连接 mysql 服务器，可以使用图形软件，更方便
2. 创建数据库名称不能修改， `` CREATE DATABASE `novel-plus` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; ``
3. 指定数据库，`use novel-plus;`，注意使用分号结尾，
4. 导入 sql 文件，输入命令`source ~/novel/novel-plus.sql;`，这里的路径不要照抄，在 mac 或 windows 平台，可以直接拖拽文件到终端中
5. 导入日志，如图
6. 导入完成后，退出。

1. 在`novel-front-3.5.4.jar`包所在的目录下运行命令，如下图，优先使用本地连接

注意： 上面的jdbc url 你要修改对应的 IP 端口 和 数据库名称，以及用户名和密码。

- 开放端口号，在 linux 作为服务器时，需要将服务绑定的端口对外开放，这样其它电脑才可以通过该端口号访问服务

在浏览器中访问

如果测试服务器需要多个 JDK 版本，这个时间可以使用临时环境变量来解决。在些提供脚本，按实际情况替换脚本中的路径即可

## Mac

1. 解压资料

1. 将 temp 目录复制到根目录，在 mac 中比较麻烦，参考链接：<https://blog.csdn.net/cq20110310/article/details/114929072>

1. `sudo vi /etc/synthetic.conf`，将 temp 目录映射到根目录
3. 使用`:wq`保存后，再通过`sudo reboot`命令重启电脑，之前在终端输入`ls /`，就可以看到如下图效果

1. 导入数据，命令导入的方式与 Linux 中的操作一样

后面的步骤与 Linux 中一样

1. 启动服务

## Windows

步骤基本与上面的差不多，直接看上面的操作步骤

1. 解压资料到 D 盘中的某个目录

1. 将 temp 放到盘符根目录，比如`d:/temp`

1. 导入数据库

1. 创建数据库名称不能修改，`` CREATE DATABASE `novel-plus` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */ /*!80016 DEFAULT ENCRYPTION='N' */; ``

1. 指定数据库，`use novel-plus;`，注意使用分号结尾，按回车键执行
2. 导入 sql 文件，`source ~/novel/novel-plus.sql`，这里的路径不要照抄，在 mac 或 windows 平台，可以直接拖拽文件到终端中

1. 在终端通过命令启动项目

通过 bat 脚本来启动，更加方便简单。创建一个`start_novel.bat`，复制如下内容

然后就可以双击`start_novel.bat`来启动项目了

# 常见错误

## JDK 版本不对

必须是 JDK8 才可以，否则报错如下

## 端口号被占用

解决办法，找到端口被占用的进程，然后杀掉。完成后再次启动项目即可

### linux 和 mac

`netstat -tulnp | grep 18001`

### windows

- `netstat -aon|findstr "18001"`

- `taskkill /PID 进程号 -T -F`：进程通过上面的命令查出来

- 命令示例：`taskkill /PID 18576 -T -F`

​
