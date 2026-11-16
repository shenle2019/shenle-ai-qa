---
title: "linux怎么设置定时开关机"
doc_id: 256210993
slug: ub5mpms40z28tg4l
book_id: 73651885
words: 726
updated_at: 2026-02-06T06:53:16.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/ub5mpms40z28tg4l
---
Linux系统设置定时开关机主要有以下几种方法：

### 使用shutdown命令

这是最常用的方法，基本格式为“shutdown [选项] 时间 [警告信息]”。例如：

- **定时关机**：“sudo shutdown -h +30”表示系统将在30分钟后自动关闭；“sudo shutdown -h 22:00”表示系统将在当天的22:00关闭。
- **定时重启**：“sudo shutdown -r +1”表示系统将在1分钟后重新启动；“sudo shutdown -r 08:00”表示在早上8点重启系统。
- **取消定时关机或重启**：如果在设置了关机或重启后改变了主意，可以使用“sudo shutdown -c”命令取消。

### 使用at命令

首先需要确保系统安装了at工具，然后可以通过以下步骤设置定时任务：

1. **安装at命令**：在Ubuntu或Debian系统上，使用“sudo apt install at”命令安装；在CentOS或RHEL系统上，使用“sudo yum install at”命令安装。
2. **启用atd服务**：使用“sudo systemctl start atd && sudo systemctl enable atd”命令确保atd服务正在运行。
3. **设置定时关机或重启**：例如，若要在晚上11点关机，可以使用“echo "shutdown now" | at 23:00”；若要设置定时重启，可以使用“echo "reboot" | at 23:00”。

### 使用crontab命令

crontab是一个基于时间的作业调度工具，允许用户设置定期的任务。具体步骤如下：

1. **编辑crontab文件**：在终端中输入“sudo crontab -e”命令编辑当前用户的crontab文件。如果是第一次运行这个命令，可能会提示选择一个文本编辑器。
2. **设置定时任务**：在打开的编辑器中，按照“分 时 日 月 周 命令”的格式添加自己的定时任务。例如，如果想要每天晚上7点20分定时关机，可以添加“20 19 \* \* \* /sbin/shutdown -h now”。
3. **保存并退出编辑器**：保存更改并退出编辑器。在nano编辑器中，可以按“Ctrl+X”，然后按“Y”确认保存更改，最后按“Enter”键退出。
4. **检查crontab文件**：使用“sudo crontab -l”命令查看当前用户的crontab文件，以确认定时任务已经设置。

### 使用图形界面工具

许多Linux发行版提供了图形界面工具来设置定时关机或重启。例如，在Ubuntu系统中的GNOME桌面环境下，只需点击“系统”菜单中的“关机”选项，然后在弹出的对话框中选择“定时关机”，设置好时间即可。
