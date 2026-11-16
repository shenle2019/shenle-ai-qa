---
title: "Linux练习题"
doc_id: 256211439
slug: wi4fh86rohyqachy
book_id: 73651885
words: 4729
updated_at: 2026-02-06T06:55:53.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/wi4fh86rohyqachy
---
## 题目

### 一、文件和目录操作类（30题）

1. 如何在当前目录下创建一个名为 `test_dir` 的目录？
2. 列出当前目录下的所有文件和目录，包括隐藏文件，使用什么命令？
3. 将文件 `file1.txt` 移动到 `test_dir` 目录中，命令是什么？
4. 复制 `test_dir` 目录下的 `file2.txt` 到当前目录，命令是？
5. 删除空目录 `test_dir` ，应使用什么命令？
6. 删除非空目录 `test_dir` 及其所有内容，命令是？
7. 查看文件 `file1.txt` 的内容，使用命令？
8. 分屏查看大文件 `big_file.txt` 的内容，用哪个命令？
9. 在文件 `file3.txt` 末尾追加一行文本 “This is a new line” ，命令是？
10. 创建一个空文件 `empty_file.txt` ，命令是？
11. 重命名文件 `old_name.txt` 为 `new_name.txt` ，如何操作？
12. 查找当前目录及其子目录下所有扩展名为 `.log` 的文件，命令是？
13. 查找系统中名为 `httpd.conf` 的文件，命令是？
14. 查看目录 `test_dir` 的详细信息（权限、所有者等），用什么命令？
15. 改变文件 `file4.txt` 的所有者为 `user1` ，命令是？
16. 改变目录 `test_dir` 的所属组为 `group1` ，命令是？
17. 给文件 `file5.txt` 设置权限，使所有者可读可写可执行，组用户可读可写，其他用户只读，命令是？
18. 递归地给目录 `test_dir` 及其子目录和文件设置权限为 755 ，命令是？
19. 查看当前所在目录的绝对路径，命令是？
20. 切换到用户 `user1` 的主目录，命令是？
21. 列出 `/var/log` 目录下最近修改时间最早的文件，命令是？
22. 比较文件 `file6.txt` 和 `file7.txt` 的内容是否相同，使用什么命令？
23. 将目录 `test_dir` 打包成 `test_dir.tar` ，命令是？
24. 将 `test_dir.tar` 解包到当前目录，命令是？
25. 压缩文件 `file8.txt` 为 `file8.txt.gz` ，使用什么命令？
26. 解压 `file8.txt.gz` ，命令是？
27. 在当前目录下创建多层目录 `dir1/dir2/dir3` ，命令是？
28. 查找当前目录下大小超过 10MB 的文件，命令是？
29. 把文件 `file9.txt` 的内容输出到新文件 `new_file.txt` 中，命令是？
30. 清空文件 `file10.txt` 的内容，命令是？

### 二、文本处理类（20题）

1. 统计文件 `text.txt` 中的行数，使用什么命令？
2. 在文件 `text.txt` 中查找包含 “error” 的行，命令是？
3. 使用正则表达式查找文件中所有以 “http” 开头的行，命令是？
4. 将文件 `text.txt` 中的所有 “apple” 替换为 “orange” ，并输出到新文件 `new_text.txt` ，命令是？
5. 提取文件 `data.csv` 的第 3 列，命令是？
6. 按第 2 列对文件 `data.csv` 进行升序排序，命令是？
7. 统计文件中每个单词的出现次数，命令是？
8. 显示文件 `text.txt` 的前 10 行，命令是？
9. 显示文件 `text.txt` 的后 5 行，命令是？
10. 从第 5 行开始显示文件 `text.txt` 的内容，命令是？
11. 删除文件 `text.txt` 中的空行，命令是？
12. 将文件 `file1.txt` 和 `file2.txt` 的内容合并为一个新文件 `merged.txt` ，命令是？
13. 在文件 `text.txt` 中查找 “warning” 并忽略大小写，命令是？
14. 查找并显示文件 `text.txt` 中第 15 行的内容，命令是？
15. 将文件 `text.txt` 中的所有小写字母转换为大写字母，命令是？
16. 统计文件 `text.txt` 中字符的数量，命令是？
17. 从文件 `data.txt` 中提取所有 IP 地址，命令是？
18. 使用 awk 计算文件 `numbers.txt` 中所有数字的总和，命令是？
19. 删除文件 `text.txt` 中所有以 “#” 开头的行，命令是？
20. 将文件 `text.txt` 按行逆序输出，命令是？

### 三、系统信息和进程管理类（20题）

1. 查看当前系统的内核版本，命令是？
2. 查看系统当前的日期和时间，命令是？
3. 查看系统的 CPU 信息，命令是？
4. 查看系统的内存使用情况，命令是？
5. 查看当前登录的用户，命令是？
6. 查看当前系统运行了多长时间（uptime），命令是？
7. 查看系统磁盘空间使用情况，命令是？
8. 查看当前目录的磁盘使用情况（按文件大小排序），命令是？
9. 查看当前运行的进程，命令是？
10. 查找并终止名为 `httpd` 的进程，命令是？
11. 查看占用 CPU 资源最多的前 5 个进程，命令是？
12. 查看占用内存资源最多的前 3 个进程，命令是？
13. 以交互方式实时监控系统进程，使用什么命令？
14. 查看系统负载情况，命令是？
15. 查看网络连接状态，命令是？
16. 查看监听在 80 端口的进程，命令是？
17. 重启网络服务，命令是？
18. 查看系统日志文件 `/var/log/messages` 的最新内容，命令是？
19. 检查系统中已安装的软件包，命令是？
20. 更新系统中所有已安装的软件包，命令是？

### 四、网络操作类（15题）

1. 测试与目标主机 `www.example.com` 的连通性，使用什么命令？
2. 查看本机的 IP 地址，命令是？
3. 下载文件 `http://example.com/file.zip` ，命令是？
4. 使用 curl 发送 HTTP 请求并显示响应头，命令是？
5. 追踪数据包从本机到目标主机 `www.google.com` 的路由路径，命令是？
6. 查看 DNS 解析结果，命令是？
7. 设置网络接口 `eth0` 的 IP 地址为 `192.168.1.100` ，子网掩码为 `255.255.255.0` ，命令是？
8. 启动 SSH 服务，命令是？
9. 使用 SSH 连接到远程主机 `192.168.1.10` ，用户名为 `root` ，命令是？
10. 从远程主机 `192.168.1.10` 下载文件 `file.txt` 到本地，命令是？
11. 上传本地文件 `local_file.txt` 到远程主机 `192.168.1.10` 的 `/tmp/` 目录，命令是？
12. 检查防火墙状态，命令是？
13. 开放防火墙的 8080 端口，命令是？
14. 查看当前已建立的网络连接，命令是？
15. 使用 nc（netcat）命令测试远程主机的 22 端口是否开放，命令是？

### 五、用户和权限管理类（15题）

1. 创建新用户 `testuser` ，命令是？
2. 为用户 `testuser` 设置密码，命令是？
3. 删除用户 `testuser` 及其主目录，命令是？
4. 将用户 `testuser` 添加到组 `developers` ，命令是？
5. 创建新组 `admins` ，命令是？
6. 查看当前用户所属的组，命令是？
7. 切换到用户 `testuser` ，命令是？
8. 查看用户 `root` 的 UID 和 GID ，命令是？
9. 临时以超级用户权限执行命令 `ls /root` ，命令是？
10. 修改 `/etc/sudoers` 文件，允许用户 `testuser` 执行所有命令，命令是？
11. 查看当前登录用户的详细信息，命令是？
12. 锁定用户 `testuser` ，使其无法登录，命令是？
13. 解锁用户 `testuser` ，命令是？
14. 显示用户 `testuser` 的密码过期信息，命令是？
15. 修改文件 `important.txt` 的权限，使其他用户无法访问，命令是？

## 答案

### 一、文件和目录操作类（30 题）

1. **问题**：如何在当前目录下创建一个名为 `test_dir` 的目录？  
   **答案**：`mkdir test_dir`
2. **问题**：列出当前目录下的所有文件和目录，包括隐藏文件，使用什么命令？  
   **答案**：`ls -a`
3. **问题**：将文件 `file1.txt` 移动到 `test_dir` 目录中，命令是什么？  
   **答案**：`mv file1.txt test_dir/`
4. **问题**：复制 `test_dir` 目录下的 `file2.txt` 到当前目录，命令是？  
   **答案**：`cp test_dir/file2.txt .`
5. **问题**：删除空目录 `test_dir` ，应使用什么命令？  
   **答案**：`rmdir test_dir`
6. **问题**：删除非空目录 `test_dir` 及其所有内容，命令是？  
   **答案**：`rm -r test_dir`
7. **问题**：查看文件 `file1.txt` 的内容，使用命令？  
   **答案**：`cat file1.txt`
8. **问题**：分屏查看大文件 `big_file.txt` 的内容，用哪个命令？  
   **答案**：`less big_file.txt`
9. **问题**：在文件 `file3.txt` 末尾追加一行文本 “This is a new line” ，命令是？  
   **答案**：`echo "This is a new line" >> file3.txt`
10. **问题**：创建一个空文件 `empty_file.txt` ，命令是？  
    **答案**：`touch empty_file.txt`
11. **问题**：重命名文件 `old_name.txt` 为 `new_name.txt` ，如何操作？  
    **答案**：`mv old_name.txt new_name.txt`
12. **问题**：查找当前目录及其子目录下所有扩展名为 `.log` 的文件，命令是？  
    **答案**：`find . -name "*.log"`
13. **问题**：查找系统中名为 `httpd.conf` 的文件，命令是？  
    **答案**：`find / -name httpd.conf 2>/dev/null`（忽略错误输出）
14. **问题**：查看目录 `test_dir` 的详细信息（权限、所有者等），用什么命令？  
    **答案**：`ls -l test_dir`
15. **问题**：改变文件 `file4.txt` 的所有者为 `user1` ，命令是？  
    **答案**：`chown user1 file4.txt`
16. **问题**：改变目录 `test_dir` 的所属组为 `group1` ，命令是？  
    **答案**：`chgrp group1 test_dir`
17. **问题**：给文件 `file5.txt` 设置权限，使所有者可读可写可执行，组用户可读可写，其他用户只读，命令是？  
    **答案**：`chmod 764 file5.txt`
18. **问题**：递归地给目录 `test_dir` 及其子目录和文件设置权限为 755 ，命令是？  
    **答案**：`chmod -R 755 test_dir`
19. **问题**：查看当前所在目录的绝对路径，命令是？  
    **答案**：`pwd`
20. **问题**：切换到用户 `user1` 的主目录，命令是？  
    **答案**：`cd ~user1`
21. **问题**：列出 `/var/log` 目录下最近修改时间最早的文件，命令是？  
    **答案**：`ls -t /var/log | tail -1`
22. **问题**：比较文件 `file6.txt` 和 `file7.txt` 的内容是否相同，使用什么命令？  
    **答案**：`diff file6.txt file7.txt`
23. **问题**：将目录 `test_dir` 打包成 `test_dir.tar` ，命令是？  
    **答案**：`tar -cvf test_dir.tar test_dir`
24. **问题**：将 `test_dir.tar` 解包到当前目录，命令是？  
    **答案**：`tar -xvf test_dir.tar`
25. **问题**：压缩文件 `file8.txt` 为 `file8.txt.gz` ，使用什么命令？  
    **答案**：`gzip file8.txt`
26. **问题**：解压 `file8.txt.gz` ，命令是？  
    **答案**：`gunzip file8.txt.gz` 或 `gzip -d file8.txt.gz`
27. **问题**：在当前目录下创建多层目录 `dir1/dir2/dir3` ，命令是？  
    **答案**：`mkdir -p dir1/dir2/dir3`
28. **问题**：查找当前目录下大小超过 10MB 的文件，命令是？  
    **答案**：`find . -size +10M`
29. **问题**：把文件 `file9.txt` 的内容输出到新文件 `new_file.txt` 中，命令是？  
    **答案**：`cat file9.txt > new_file.txt`
30. **问题**：清空文件 `file10.txt` 的内容，命令是？  
    **答案**：`> file10.txt`

### 二、文本处理类（20 题）

1. **问题**：统计文件 `text.txt` 中的行数，使用什么命令？  
   **答案**：`wc -l text.txt`
2. **问题**：在文件 `text.txt` 中查找包含 “error” 的行，命令是？  
   **答案**：`grep "error" text.txt`
3. **问题**：使用正则表达式查找文件中所有以 “http” 开头的行，命令是？  
   **答案**：`grep '^http' text.txt`
4. **问题**：将文件 `text.txt` 中的所有 “apple” 替换为 “orange” ，并输出到新文件 `new_text.txt` ，命令是？  
   **答案**：`sed 's/apple/orange/g' text.txt > new_text.txt`
5. **问题**：提取文件 `data.csv` 的第 3 列，命令是？  
   **答案**：`cut -d',' -f3 data.csv`
6. **问题**：按第 2 列对文件 `data.csv` 进行升序排序，命令是？  
   **答案**：`sort -t',' -k2 data.csv`
7. **问题**：统计文件中每个单词的出现次数，命令是？  
   **答案**：`cat text.txt | tr ' ' '\n' | sort | uniq -c`
8. **问题**：显示文件 `text.txt` 的前 10 行，命令是？  
   **答案**：`head -10 text.txt`
9. **问题**：显示文件 `text.txt` 的后 5 行，命令是？  
   **答案**：`tail -5 text.txt`
10. **问题**：从第 5 行开始显示文件 `text.txt` 的内容，命令是？  
    **答案**：`tail -n +5 text.txt`
11. **问题**：删除文件 `text.txt` 中的空行，命令是？  
    **答案**：`grep -v '^$' text.txt`
12. **问题**：将文件 `file1.txt` 和 `file2.txt` 的内容合并为一个新文件 `merged.txt` ，命令是？  
    **答案**：`cat file1.txt file2.txt > merged.txt`
13. **问题**：在文件 `text.txt` 中查找 “warning” 并忽略大小写，命令是？  
    **答案**：`grep -i "warning" text.txt`
14. **问题**：查找并显示文件 `text.txt` 中第 15 行的内容，命令是？  
    **答案**：`sed -n '15p' text.txt`
15. **问题**：将文件 `text.txt` 中的所有小写字母转换为大写字母，命令是？  
    **答案**：`tr '[:lower:]' '[:upper:]' < text.txt`
16. **问题**：统计文件 `text.txt` 中字符的数量，命令是？  
    **答案**：`wc -m text.txt`
17. **问题**：从文件 `data.txt` 中提取所有 IP 地址，命令是？  
    **答案**：`grep -oE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' data.txt`
18. **问题**：使用 awk 计算文件 `numbers.txt` 中所有数字的总和，命令是？  
    **答案**：`awk '{sum+=$1} END {print sum}' numbers.txt`
19. **问题**：删除文件 `text.txt` 中所有以 “#” 开头的行，命令是？  
    **答案**：`sed '/^#/d' text.txt`
20. **问题**：将文件 `text.txt` 按行逆序输出，命令是？  
    **答案**：`tac text.txt`

### 三、系统信息和进程管理类（20 题）

1. **问题**：查看当前系统的内核版本，命令是？  
   **答案**：`uname -r`
2. **问题**：查看系统当前的日期和时间，命令是？  
   **答案**：`date`
3. **问题**：查看系统的 CPU 信息，命令是？  
   **答案**：`cat /proc/cpuinfo`
4. **问题**：查看系统的内存使用情况，命令是？  
   **答案**：`free -h`
5. **问题**：查看当前登录的用户，命令是？  
   **答案**：`who`
6. **问题**：查看当前系统运行了多长时间（uptime），命令是？  
   **答案**：`uptime`
7. **问题**：查看系统磁盘空间使用情况，命令是？  
   **答案**：`df -h`
8. **问题**：查看当前目录的磁盘使用情况（按文件大小排序），命令是？  
   **答案**：`du -sh * | sort -h`
9. **问题**：查看当前运行的进程，命令是？  
   **答案**：`ps aux`
10. **问题**：查找并终止名为 `httpd` 的进程，命令是？  
    **答案**：`pkill httpd` 或 `killall httpd`
11. **问题**：查看占用 CPU 资源最多的前 5 个进程，命令是？  
    **答案**：`ps aux --sort=-%cpu | head -5`
12. **问题**：查看占用内存资源最多的前 3 个进程，命令是？  
    **答案**：`ps aux --sort=-%mem | head -3`
13. **问题**：以交互方式实时监控系统进程，使用什么命令？  
    **答案**：`top` 或 `htop`
14. **问题**：查看系统负载情况，命令是？  
    **答案**：`w` 或 `uptime`
15. **问题**：查看网络连接状态，命令是？  
    **答案**：`netstat -tulpn`
16. **问题**：查看监听在 80 端口的进程，命令是？  
    **答案**：`netstat -tulpn | grep :80`
17. **问题**：重启网络服务，命令是？  
    **答案**：`service network restart`（CentOS/RHEL）或 `systemctl restart network`（Ubuntu/Debian）
18. **问题**：查看系统日志文件 `/var/log/messages` 的最新内容，命令是？  
    **答案**：`tail -f /var/log/messages`
19. **问题**：检查系统中已安装的软件包，命令是？  
    **答案**：`dpkg -l`（Debian/Ubuntu）或 `rpm -qa`（CentOS/RHEL）
20. **问题**：更新系统中所有已安装的软件包，命令是？  
    **答案**：`apt update && apt upgrade`（Debian/Ubuntu）或 `yum update`（CentOS/RHEL）

### 四、网络操作类（15 题）

1. **问题**：测试与目标主机 `www.example.com` 的连通性，使用什么命令？  
   **答案**：`ping www.example.com`
2. **问题**：查看本机的 IP 地址，命令是？  
   **答案**：`ip addr show` 或 `ifconfig`
3. **问题**：下载文件 `http://example.com/file.zip` ，命令是？  
   **答案**：`wget http://example.com/file.zip`
4. **问题**：使用 curl 发送 HTTP 请求并显示响应头，命令是？  
   **答案**：`curl -I http://example.com`
5. **问题**：追踪数据包从本机到目标主机 `www.google.com` 的路由路径，命令是？  
   **答案**：`traceroute www.google.com`（Linux）或 `tracert www.google.com`（Windows）
6. **问题**：查看 DNS 解析结果，命令是？  
   **答案**：`nslookup www.example.com`
7. **问题**：设置网络接口 `eth0` 的 IP 地址为 `192.168.1.100` ，子网掩码为 `255.255.255.0` ，命令是？  
   **答案**：`ifconfig eth0 192.168.1.100 netmask 255.255.255.0`
8. **问题**：启动 SSH 服务，命令是？  
   **答案**：`service ssh start`（Ubuntu/Debian）或 `systemctl start sshd`（CentOS/RHEL）
9. **问题**：使用 SSH 连接到远程主机 `192.168.1.10` ，用户名为 `root` ，命令是？  
   **答案**：`ssh root@192.168.1.10`
10. **问题**：从远程主机 `192.168.1.10` 下载文件 `file.txt` 到本地，命令是？  
    **答案**：`scp root@192.168.1.10:/path/to/file.txt .`
11. **问题**：上传本地文件 `local_file.txt` 到远程主机 `192.168.1.10` 的 `/tmp/` 目录，命令是？  
    **答案**：`scp local_file.txt root@192.168.1.10:/tmp/`
12. **问题**：检查防火墙状态，命令是？  
    **答案**：`systemctl status firewalld`（CentOS/RHEL）或 `ufw status`（Ubuntu/Debian）
13. **问题**：开放防火墙的 8080 端口，命令是？  
    **答案**：`firewall-cmd --zone=public --add-port=8080/tcp --permanent && firewall-cmd --reload`（CentOS/RHEL）或 `ufw allow 8080`（Ubuntu/Debian）
14. **问题**：查看当前已建立的网络连接，命令是？  
    **答案**：`netstat -anp | grep ESTABLISHED`
15. **问题**：使用 nc（netcat）命令测试远程主机的 22 端口是否开放，命令是？  
    **答案**：`nc -zv 192.168.1.10 22`

### 五、用户和权限管理类（15 题）

1. **问题**：创建新用户 `testuser` ，命令是？  
   **答案**：`useradd testuser`
2. **问题**：为用户 `testuser` 设置密码，命令是？  
   **答案**：`passwd testuser`
3. **问题**：删除用户 `testuser` 及其主目录，命令是？  
   **答案**：`userdel -r testuser`
4. **问题**：将用户 `testuser` 添加到组 `developers` ，命令是？  
   **答案**：`usermod -aG developers testuser`
5. **问题**：创建新组 `admins` ，命令是？  
   **答案**：`groupadd admins`
6. **问题**：查看当前用户所属的组，命令是？  
   **答案**：`groups`
7. **问题**：切换到用户 `testuser` ，命令是？  
   **答案**：`su - testuser`
8. **问题**：查看用户 `root` 的 UID 和 GID ，命令是？  
   **答案**：`id root`
9. **问题**：临时以超级用户权限执行命令 `ls /root` ，命令是？  
   **答案**：`sudo ls /root`
10. **问题**：修改 `/etc/sudoers` 文件，允许用户 `testuser` 执行所有命令，命令是？  
    **答案**：`visudo` 然后添加 `testuser ALL=(ALL) ALL`
11. **问题**：查看当前登录用户的详细信息，命令是？  
    **答案**：`id`
12. **问题**：锁定用户 `testuser` ，使其无法登录，命令是？  
    **答案**：`usermod -L testuser`
13. **问题**：解锁用户 `testuser` ，命令是？  
    **答案**：`usermod -U testuser`
14. **问题**：显示用户 `testuser` 的密码过期信息，命令是？  
    **答案**：`chage -l testuser`
15. **问题**：修改文件 `important.txt` 的权限，使其他用户无法访问，命令是？  
    **答案**：`chmod o-rwx important.txt`
