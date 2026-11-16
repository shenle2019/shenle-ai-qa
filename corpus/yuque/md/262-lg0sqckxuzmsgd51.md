---
title: "使用临时环境变量"
doc_id: 256205204
slug: lg0sqckxuzmsgd51
book_id: 73651885
words: 173
updated_at: 2026-02-06T06:13:00.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/lg0sqckxuzmsgd51
---
当电脑上有多个 JDK 安装版本和 Jmeter 版本时，修改环境变量比较麻烦。可以设置临时的环境变量来解决。临时变量设置，只能一个终端有效

# windows

## JDK

JDK 安装位置

在终端中输入以下命令：

- `set JAVA_HOME=C:\Program Files\Java\jdk-1.8`
- `set PATH=%JAVA_HOME%\bin;%PATH%`

## Jmeter

Jmeter 位置

配置命令：

- `set PATH=C:\apache-jmeter-5.4.1\bin;%PATH%`：简化写法

# linux/macos

设置临时变量

- 设置`java`临时变量，注意下面的`JAVA_HOME`路径不要照抄

- `export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_361.jdk/Contents/Home`
- `export PATH=$JAVA_HOME/bin:$PATH:`

- 设置`jmeter`临时变量，注意下面的`JMETER_HOME`路径不要照抄

- `export JMETER_HOME=/Users/duan/Documents/apache-jmeter-5.4.1`
- `export PATH=$JMETER_HOME/bin:$PATH:`

- 启动`jmeter`：在终端输入`jmeter`命令即可
