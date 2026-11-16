---
title: "CentOS7.9测试环境搭建教程"
doc_id: 256208272
slug: ekbhnbz33q3xlbnr
book_id: 73651885
words: 4744
updated_at: 2026-02-06T06:34:54.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/ekbhnbz33q3xlbnr
---
# 获取 Centos7 镜像

下载地址：<https://mirrors.aliyun.com/centos/7.9.2009/isos/x86_64/?spm=a2c6h.25603864.0.0.23d5f5ad7ZdRpw>

## 常用命令

# 虚拟机软件

## VirtualBox 安装使用

### 下载

官网地址：<https://www.virtualbox.org/wiki/Downloads>，本教程使用的是 7.1.4

直接下载地址：<https://download.virtualbox.org/virtualbox/7.1.4/VirtualBox-7.1.4-165100-Win.exe>

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

- `vi /etc/sysconfig/network-scripts/ifcfg-enp0s3`

`:wq`保存

##### ifcfg-enp0s8

设置静态 ip，负责与物理机通信

- 查看静态网关地址

此处是 192.168.56.1，所以下面的 GATEWAY=192.168.56.1，IPADDR=192.168.56.110。这个IPADDR 最后一段 110，可以自定义，范围在 10 到 250 之内就好了

- `vi /etc/sysconfig/network-scripts/ifcfg-enp0s8`

重启系统，在终端输入`reboot`命令，重启后，登录账号在终端中输入`ip addr`，查看网络配置是否生效

## VMWare

# 常用工具

## XShell7

下载地址：<https://www.xshell.com/zh/free-for-home-school/>

常用的连接 Linux 的工具

## Xftp7

主要用于上传文件，下载地址：<https://www.xshell.com/zh/free-for-home-school/>

## FinalShell

下载地址：<https://www.hostbuf.com/t/988.html>

支持 Windows、MacOS、Linux 三个平台。相当于 XShell 和 XFtp 两个软件的集合体。主要功能都是免费的

第一次安装时可能会有如下提示

参考图

点击确定后可能需要再输入一次密码，但提示做即可

### 上传文件

### 下载文件

# 设置国内源(必做)

> 如果 yum 无法下载内容，报错如上图时，可以更新国内下载源来解决

## wget 下载工具

保证本地包含`wget`工具，执行如下指令表示已经安装 `wget`工具。

- `wget --version`：查看`wget`命令是否可用，没有可通过命令`yum -y install wget`安装

也可以离线安装，安装包如果下面的地址不能下载，可以问班主任要

在物理机上解压上传到虚拟机

安装命令`rpm -ivh wget-1.14-18.el7_6.1.x86_64.rpm`

安装完成后，使用`wget --version`检查

## 备份历史配置

- `cd /etc/yum.repos.d`
- `mv CentOS-Base.repo CentOS-Base.repo.bak`或者`mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.bak`

## 配置国内源

### 阿里云

> 阿里云最近总是报 403，可以换其它源

`wget -O /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-7.repo`，等待即可，全自动

### 华为云

下面的命令直接复制粘贴按回车即可

## 清空并生成缓存

# 端口查看工具

- `sudo yum install net-tools -y`

- `netstat -tulnp`：查看向外提供服务的端口号
- `netstat -tulnp | grep "端口"`：查看指定的端口号

- 例如：`netstat -tulnp | grep 18001`

# Git 安装

`yum install git -y`

验证安装是否成功

通过`yum remove git -y`命令，可以卸载在线安装的 git

# Java

## 下载

下载地址：

- `jdk17`：<https://www.oracle.com/java/technologies/downloads/?er=221886#java17>

- `jdk11`：<https://www.oracle.com/java/technologies/downloads/?er=221886#java11>

- `jdk8`：<https://www.oracle.com/java/technologies/downloads/?er=221886#java8>

下载的时候需要登录，如果没有账号就自己注册一个，再登录就可以了

上传文件到 Linux 上，然后解压

以上三个`JDK`都有可能使用到，所以三个都解压，本教程会讲如何同时使用多个 jdk 版本

将三个`JDK`文件夹复制到`/usr/local/jdk`目录下

- `mkdir /usr/local/jdk`
- `cp -R jdk-17.0.13 /usr/local/jdk/`
- `cp -R jdk-11.0.25 /usr/local/jdk/`
- `cp -R jdk1.8.0_431/ /usr/local/jdk/`

## 配置环境变量

环境变量中只能配置一个版本，这个没有固定，以自己最常用的那个为主，本教程配置的是`jdk-11.0.25`

`vi /etc/profile`

- 刷新环境变量：`source /etc/profile`

## 使用临时变量

在测试环境搭建过程中，经常会遇到不同的软件会有使用不同的环境，比如有些软件要求使用 jdk8 ，有些可能需要 jdk11。此时就需要使用临时环境变量来完成任务了，这个时候需要开启多个连接窗口

- 设置`java`临时变量，注意下面的`JAVA_HOME`路径不要照抄

> 不只是 jdk 可以这样操作，很多软件都可以

# Mysql Server 离线安装

# 安装 Python

# Redis 离线安装

下载地址：<http://download.redis.io/releases/>

## 上传文件并解压

上传文件到桌面，通过`tar -xvf redis-7.2.6.tar.gz`命令解压

解压成功后，内容如下，使用`cd redis-7.2.6`命令进入到目录

## 执行安装命令

- `make MALLOC=libc`

- `cd src && make install`​

检查`/usr/local/bin`目录是否有`redis`相关命令

如果没有，则再`redis`目录执行`make install`

## 尝试启动 redis 服务

- `./redis-server`：如下图表示启动成功

启动成功后可以通过`Ctrl + C`来停止服务

## 设置开机启动

依次执行

复制`redis.conf`文件到`/etc/redis`目录下

`cp redis.conf /etc/redis/6379.conf`

通过`vim /etc/redis/6379.conf`或`vi /etc/redis/6379.conf`命令修改配置文件，如果`vim`没有安装就使用`vi`命令

vi 搜索命令，进入到文件后，输入`/daemonize no`即可以定位到相应的文本

### 后台启动

将`no`改成`yes`

### 修改 bind 绑定的 ip

修改`0.0.0.0`映射所有地址

### 将启动文件复制到 init.d 中

通过命令`vi /etc/init.d/redisd`，编辑文件

- `chmod +x /etc/init.d/redisd`：增加脚本执行权限
- 增加系统服务

- `chkconfig --add redisd`
- `chkconfig --list redisd`

## 启动 redis-server

通过命令`service redisd start`启动`redis`服务端，如果报如下错误

需要修改`sudo vi /etc/sysctl.conf`

## 查看 redis 启动状态

- `ps -aux | grep redis`

## 使用客户端测试

- `redis-cli`或`./redis-cli`，进入客户端
- `set test "Hello"`：添加一条数据
- `get test`：查看添加的数据
- `exit`：退出客户端

# InfluxDB

InfluxDB是一个由InfluxData开发的开源时序型[数据库](https://so.csdn.net/so/search?q=%E6%95%B0%E6%8D%AE%E5%BA%93&spm=1001.2101.3001.7020)，专注于海量时序数据的高性能读、高性能写、高效存储与实时分析等

InfluxDB广泛应用于DevOps监控、IoT监控、实时分析等场景。除了具有成本优势的高性能读、高性能写、高存储率，InfluxDB还具有如下特点：

1. 无系统环境依赖，部署方便。
2. 无结构化（SchemaLess）的数据模型，灵活强大。
3. 原生HTTP管理接口，免插件配置和免第三方依赖。
4. 强大的类SQL查询语句的操作接口，学习成本低，上手快。
5. 丰富的权限管理功能，精细到“表”级别。
6. 丰富的时效管理功能，自动删除过期数据，自定义删除指标数据。
7. 低成本存储，采样时序数据，压缩存储。
8. 丰富的聚合函数，支持AVG、SUM、MAX、MIN等聚合函数。

下载地址：<https://dl.influxdata.com/influxdb/releases/influxdb-1.8.4.x86_64.rpm>

也可以跟班主任要。把下面的图发给班主任即可

## 安装

- 上传到虚拟机中

- 执行安装命令：`sudo yum install -y influxdb-1.8.4.x86_64.rpm`

## 启动

- `systemctl start influxdb`：`启动命令`
- `systemctl status influxdb`：查看启动状态

- `sudo systemctl enable influxdb.service`：设置开机启动，

## 验证服务启动情况

- `influx`

输入`exit`退出

# Prometheus

## 下载

官网地址：<https://prometheus.io/download/>

本教程使用版本下载地址：<https://github.com/prometheus/prometheus/releases/download/v2.51.1/prometheus-2.51.1.linux-amd64.tar.gz>

历史版本可以在这里找，<https://github.com/prometheus/prometheus/releases>

也可以跟班主任要。把下面的图发给班主任即可

## 上传并解压

`tar -zxvf prometheus-2.51.1.linux-amd64.tar.gz`

复制到`/usr/local/prometheus`目录下，这个只是习惯，想放哪里都可以。但不要太随

`cp -R prometheus-2.51.1.linux-amd64 /usr/local/prometheus`

## 配置环境变量

`vi /etc/profile`，在文件最后添加。`/usr/local/prometheus`这是我配置的路径，不要照抄，除非完成跟文档一致

​

输入`source /etc/profile`，刷新环境变量

​

## 开放端口号

如果防火墙没有关闭，需要开放端口号 9090

## 启动

- 指定配置文件启动：`prometheus --config.file=/usr/local/prometheus/prometheus.yml`，可以在任何目录复制该命令执行

浏览器访问，直接输入`http://192.168.109.100:9090/`。这个地址不要照抄

- 进入到目录再启动：`cd /usr/local/prometheus/ && prometheus`。必须注意当前所在的目录

## **prometheus.yml 配置文件**

## **数据采集工具 --node exporter**

在Prometheus的架构设计中，Prometheus Server并不直接服务监控特定的目标，其主要任务负责数据的收集，存储并且对外提供数据查询支持。因此为了能够能够监控到某些东西，如主机的CPU使用率，我们需要使用到Exporter。Prometheus周期性的从Exporter暴露的HTTP服务地址（通常是/metrics）拉取监控样本数据。、

### 上传解压

### 复制到/usr/local 目录下

### 启动

- 启动：`cd /usr/local/node_exporter && ./node_exporter`

- 后台启动：`nohup ./node_exporter > node_export.log 2>&1 &`

node\_exporter 占用端口为 9100

### 配置 Prometheus 获取 node\_exporter 数据

通过 vi 来编辑配置文件，`vi /usr/local/prometheus/prometheus.yml`

### 重新启动 prometheus

关闭原来的后台启动的`prometheus`

- `netstat -tunpl | grep 9090`
- `kill -9 11862`

cd 到 prometheus 目录

后台启动：`nohup prometheus > prometheus.log 2>&1 &`

​

### 查看配置效果

在浏览器中访问 prometheus

## 配置 mysql\_exporter

> 将上面的文件下载，然后上传到 linux 中。如果下载不了找老师要

### 解压

解压文件不想要中文，也可以在物理机上解决后，再上传

如果报如下错误就下载解决命令`yum install -y zip unzip`

解压后的文件如下

- 解压`tar -zxvf mysqld_exporter-0.14.0.linux-amd64.tar.gz`
- 复制到`/usr/local`目录下，`cp -rf mysqld_exporter-0.14.0.linux-amd64 /usr/local/mysqld_exporter`

### 添加环境变量

`vi /etc/profile`

命令说明

- `root`：数据库的用户名
- `Root_1234`：`root`账号的密码
- `192.168.1.106`：要连接的`mysql`的在的服务器

刷新环境变量：`source /etc/profile`

### 启动服务

- `cd /usr/local/mysqld_exporter && ./mysqld_exporter` 前台运行，停止使用`Ctrl + C`命令

- `nohup ./mysqld_exporter > mysqld_exporter.log 2>&1 &` 后台运行
- 默认为 9104 网络端口用语数据库采集信息 给prometheus去调用

### 修改 prometheus.yml 配置文件

重启prometheus

### 查看效果

# Grafana

## 概述

‌[**Grafana**](https://www.baidu.com/s?wd=Grafana&rsv_idx=2&tn=baiduhome_pg&usm=2&ie=utf-8&rsv_pq=a67e15f70003dca2&oq=grafana%E6%98%AF%E4%B8%80%E6%AC%BE%E4%BB%80%E4%B9%88%E6%A0%B7%E7%9A%84%E5%B7%A5%E5%85%B7&rsv_t=bd350ypwtKbEUHGLMthSg2zWIRXc0FiCvlOnXxyscmbxIMUizRoY1BX%2F2vu0Y35lIDGG&rsv_dl=re_dqa_generate&sa=re_dqa_generate)**是一款开源的数据可视化和监控工具，主要用于展示和分析时间序列数据。**‌它支持多种数据源，如[Prometheus](https://www.baidu.com/s?wd=Prometheus&rsv_idx=2&tn=baiduhome_pg&usm=2&ie=utf-8&rsv_pq=a67e15f70003dca2&oq=grafana%E6%98%AF%E4%B8%80%E6%AC%BE%E4%BB%80%E4%B9%88%E6%A0%B7%E7%9A%84%E5%B7%A5%E5%85%B7&rsv_t=5857EWgZqHqJcfItCW0qzOApCIy%2BiQqoAryfn9DPmdEitaMBA8gZnaeZnDuZQdjc1A5f&rsv_dl=re_dqa_generate&sa=re_dqa_generate)、[InfluxDB](https://www.baidu.com/s?wd=InfluxDB&rsv_idx=2&tn=baiduhome_pg&usm=2&ie=utf-8&rsv_pq=a67e15f70003dca2&oq=grafana%E6%98%AF%E4%B8%80%E6%AC%BE%E4%BB%80%E4%B9%88%E6%A0%B7%E7%9A%84%E5%B7%A5%E5%85%B7&rsv_t=1a1dIukBux5Uy7Z9t%2FTfOA3FQTRAPJIFydVvDcTurLHsJiiYHjsnDM53sLEcUo2qphrP&rsv_dl=re_dqa_generate&sa=re_dqa_generate)、[Graphite](https://www.baidu.com/s?wd=Graphite&rsv_idx=2&tn=baiduhome_pg&usm=2&ie=utf-8&rsv_pq=a67e15f70003dca2&oq=grafana%E6%98%AF%E4%B8%80%E6%AC%BE%E4%BB%80%E4%B9%88%E6%A0%B7%E7%9A%84%E5%B7%A5%E5%85%B7&rsv_t=0f51uhzxCL4VBYVqq2HXgkfEQvfuo7AgWdeKhxBDP%2BH9Ir759ySyi0mm9lPNxpP1zQd5&rsv_dl=re_dqa_generate&sa=re_dqa_generate)、[Elasticsearch](https://www.baidu.com/s?wd=Elasticsearch&rsv_idx=2&tn=baiduhome_pg&usm=2&ie=utf-8&rsv_pq=a67e15f70003dca2&oq=grafana%E6%98%AF%E4%B8%80%E6%AC%BE%E4%BB%80%E4%B9%88%E6%A0%B7%E7%9A%84%E5%B7%A5%E5%85%B7&rsv_t=6ce8IRefsJQlNaOCPm7EIeNlFHFYZvU6p%2FvU0rdEContAjhnR1xh5jODLPV5Pn9BrFOp&rsv_dl=re_dqa_generate&sa=re_dqa_generate)、[MySQL](https://www.baidu.com/s?wd=MySQL&rsv_idx=2&tn=baiduhome_pg&usm=2&ie=utf-8&rsv_pq=a67e15f70003dca2&oq=grafana%E6%98%AF%E4%B8%80%E6%AC%BE%E4%BB%80%E4%B9%88%E6%A0%B7%E7%9A%84%E5%B7%A5%E5%85%B7&rsv_t=6ce8IRefsJQlNaOCPm7EIeNlFHFYZvU6p%2FvU0rdEContAjhnR1xh5jODLPV5Pn9BrFOp&rsv_dl=re_dqa_generate&sa=re_dqa_generate)和[PostgreSQL](https://www.baidu.com/s?wd=PostgreSQL&rsv_idx=2&tn=baiduhome_pg&usm=2&ie=utf-8&rsv_pq=a67e15f70003dca2&oq=grafana%E6%98%AF%E4%B8%80%E6%AC%BE%E4%BB%80%E4%B9%88%E6%A0%B7%E7%9A%84%E5%B7%A5%E5%85%B7&rsv_t=edf7nDTb5qIXrxAO6PGktlps5M9CEDRK8Fm97lk%2Fhn1CfamnYfSMo9C%2BCtg4vVW8po5C&rsv_dl=re_dqa_generate&sa=re_dqa_generate)等，用户可以在一个仪表盘上显示来自不同数据源的数据，并进行跨数据源的查询和分析。‌

官网：<https://grafana.com/>

## 下载

下载地址：<https://dl.grafana.com/enterprise/release/grafana-enterprise-10.4.1-1.x86_64.rpm>

安装文件也可以跟班主任要。把下面的图发给班主任即可

## 上传并安装

安装命令：`sudo yum install -y grafanaenterprise10.4.11.x86_64.rpm`

## 启动

- `sudo systemctl daemon-reload`：这个命令的作⽤是重新加载 Systemd 系统管理守护程序的配置⽂件
- `sudo systemctl start grafana-server`：启动服务
- `sudo systemctl status grafana-server`：查看服务启动状态
- `sudo systemctl restart grafana-server`：重新启动服务，非必要
- `sudo systemctl enable grafana-server.service`：设置开机启动

## 浏览器访问服务

grafana 默认端口是 3000，如果开启了防火墙需要开放端口号。

在浏览器输入:<http://192.168.109.100:3000/login>。IP 地址不要照抄。初始⽤户名和密码为 admin

第一次登录会要求修改密码。也可以点击 Skip，继续保持默认密码

## 添加 InfluxDB

## 添加 Prometheus

导入看板文件

# 安装 NodeJs

下载地址：<https://nodejs.org/zh-cn/download/prebuilt-binaries>

## 上传文件

本教程在 Mac 上通过 FinalShell 上传

## 解压文件

`tar -xvf node-v16.20.2-linux-x64`

将解压后的文件夹复制到`/usr/local/nodejs`目录，命令为：`cp -R node-v16.20.2-linux-x64 /usr/local/nodejs`

## 配置环境变量

本教程主要演示 CentOs7 上的配置方式。

- `vim /etc/profile`：编辑环境变量
- `source /etc/profile`：使用环境变量生效

验证配置效果

## 国内源下载配置

`npm config set registry https://mirrors.cloud.tencent.com/npm/`

设置完成后，可以通过`npm config list`查看

## 全局下载配置

- `cd /usr/local/nodejs`：进入到 nodejs 目录
- 创建两个文件夹`mkdir node_cache`和 `mkdir node_global`

- 将创建的目录配置到 npm 中

- `npm config set prefix "/usr/local/nodejs/node_global"`
- `npm config set cache "/usr/local/nodejs/node_cache"`
- 配置完成后，通过`npm config list`查看是否配置成功

验证配置效果，通过`npm i -g nodemon`全局下载`nodemon`工具，然后通过`nodemon -v`验证，效果如下

可以在`node_global`目录下看下载的内容

> 到此 nodejs 就已经安装配置完成了，后面的是关于

## 后台运行 nodejs 项目

- 通过`nginx`运行，在这里不再多赘述
- 通过`pm2`命令来运行

### 全局下载 pm2

这里需要有 nodejs 项目才可以

- `npm i -g pm2`
- 通过`cd`命令进入到项目根目录下

- 通过`pm2 start app.js`后台运行项目

- 如果上面的命令启动成功，但是无法访问，可以试下，`npm run prd`

在浏览器中查看效果如下

### pm2 其它命令

- `pm2 status`：查看运行状态

- `pm2 stop app.js`：停止指定的项目

## 安装 nodejs-v18 版本的问题

`tar -xvf node-v18.20.5-linux-x64.tar.xz`

具体问题如下图

> 如果安装的是 v18 或以上版本，会出现如下错误
>
> 具体原因，新版的node v18开始 都需要GLIBC\_2.27支持，可是目前系统内却没有那么高的版本

执行命令

### 升级 make

> make check 命令在执行完后，会有如下提示，不用处理

安装后，可通过`make -v`验证

### 升级 gcc

命令执行完后，结尾参照下图

> 报错如下

> 编译完成

安装完成

通过`gcc -v`检测

### 下载安装glibc-2.28

安装 bison 依赖，`yum install -y bison`，否则报错如下：

配置成功

> 如果前面的 make 和 gcc 升级没有做，就会报错如下

> 编译完成后，提示如下，虽然显示报错，但可以不用处理
>
> 没有错误的话，显示如下

### 更新libstdc++.so.6.0.26

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

# 配置鸿蒙 Next 测试环境

## 下载 Linux 版本

官网下载地址：<https://developer.huawei.com/consumer/cn/download/command-line-tools-for-hmos>

本教程使用的版本如下

下载完成后，上传到 Linux 上并解压，解压命令为`unzip commandline-tools-linux-x64-5.0.3.906.zip`

## 配置环境变量

`vim /etc/profile`

保存后，通过`source /etc/profile`使用环境变量生效

> 如上图，`ohpm -v`命令验证通过，但是在执行`hdc -v`命令时，却报错了，通过执行`sudo yum install libatomic -y`命令来解决。
>
> 如下图错，参考升级 make 和 gcc 那一节内容来解决

# Ngnix

# 读书屋环境搭建
