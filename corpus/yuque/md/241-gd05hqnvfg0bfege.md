---
title: "centos7-常用命令"
doc_id: 256209317
slug: gd05hqnvfg0bfege
book_id: 73651885
words: 464
updated_at: 2026-02-06T06:42:26.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/gd05hqnvfg0bfege
---
- 查看 Centos 系统版本：`cat /etc/redhat-release`
- 进入到目录：`cd 目录名称`
- 命令补全：按`tab`
- 上级目录：`cd ..`
- 回到用户目录：`cd ~`
- 去到根目录：`cd /`
- 编辑文件：`vi 文件名称`
- 创建目录：`mkdir 目录名称`
- 删除文件或目录：`rm -rf 目录或文件路径`
- 复制文件或目录

- 复制文件：`cp 文件路径 目标文件路径`
- 复制目录：`cp -R 文件路径 目标文件路径`

- 服务启动：`systemctl start 服务名称`
- 服务停止：`systemctl stop 服务名称`
- 服务状态查看：`systemctl status 服务名称`
- 关闭防火墙：在本地虚拟机直接关闭防火墙可以省很多事，公司服务器不要这样操作

- `sudo systemctl stop firewalld`：停止防火墙服务
- `sudo systemctl disable firewalld`：禁止防火墙开机自启

- 如果不想关闭防火墙，需要了解开放端口号命令

- 文件上传命令，可以使用第 3 节中的软件上传，更方便：`scp 文件路径 服务器账号@服务器地址:/服务保存路径`

- 示例：`scp grafana-enterprise-10.4.1-1.x86_64.rpm root@192.168.109.100/~`

- 后台永久运行命令：`nohup 命令 > file.log 2>&1 &`

- `nohup` ： 不挂断的运行，注意并没有后台运行的功能
- `&`：是指在后台运行
- `> file.log 2>&1`：将错误日志或标准日志输出到 file.log 文件中
