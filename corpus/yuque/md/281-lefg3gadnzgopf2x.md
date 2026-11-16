---
title: "win-安装Mysql数据库"
doc_id: 251194477
slug: lefg3gadnzgopf2x
book_id: 73651885
words: 1011
updated_at: 2025-12-31T08:04:49.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/lefg3gadnzgopf2x
---
# 5.7.31

## 下载MySQL

**Mysql****官网下载地址**[https://downloads.mysql.com/archives/installer/](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fdownloads.mysql.com%2Farchives%2Finstaller%2F&objectId=2093568&objectType=1&contentType=undefined)

#### 选择想要安装的版本，点击Download下载

**本篇文章选择的是5.7.31版本**

## 安装MySQL

#### 选择设置类型

**双击运行mysql-installer-community-5.7.31.0.msi，这里选择是自定义安装，所以直接选择“Custom”，点击“Next”**

“Developer Default”是开发者默认

“Server only”仅作为服务器安装

“Client only”仅作为客户端安装

“Full”是完整安装

“Custom”是自定义安装

#### 选择安装的产品和功能

**依次点开“My**[SQL Server](https://cloud.tencent.com/product/sqlserver?from_column=20065&from=20065)**s”、“MySQL Servers”、“MySQL Servers 5.7”、“MySQL Servers 5.7.31 -64”，然后点击绿色箭头将选中的版本移植到右边选中框中**

注：这里选择的是64位系统

#### 先选中“MySQL Server 5.7.31” ，之后点击下方的蓝色“Advanced Options”

#### 自定义安装路径和数据存放路径，更改完成之后点击“OK”

注：虽说安装在C盘也没毛病，但是个人建议不要安装到C盘，我安装到了D盘

#### 直接点击“OK”

注：这里因为选择了我自己创建的路径，故程序提示路径已存在，是否要继续

#### 更改完成之后点击“Next”

#### 确认一下安装路径和数据存放路径对不对，没有问题的话就直接点击Next

#### 直接点击“Yes”

#### 先选中“MySQL Server5.7.31”，若电脑中没有这个环境，会提示安装“Microsoft Visual C++ 2013”环境，点击“Execute”

#### 勾选中之后点击“Install”

#### 安装完成，点击“Close”

#### 看到这个对勾就说明这个环境安装上了，直接点击“Next”

#### 直接点击“Execute”

#### 出现这个图标就说明安装成功了，直接点击“Next”

#### 直接点击“Next”

#### 直接点击“Next”

#### 选择安装类型

**个人学习研究的话选择“Development Computer”则可以，我这里选择是“Development Computer”**

Development Computer 适合个人开发学习使用的

Server Computer 是像主要用于像FTP，email，web服务器等等

Dedicated Computer 只用作MySQL服务器

#### MySQL的默认端口是3306，不需要作修改，直接点击“Next”

#### 这里需要设置MySQL的密码，不需要太复杂，设置完了直接点击“Next”

#### 直接点击“Next”

#### 直接点击“Execute”，开始安装，点击安装之后需要等待片刻

#### 点击“Finish”

#### 点击“Next”

#### 点击“Finish”，此时MySQL安装完成

#### 在开始界面搜索mysql，点击第一个MySQL 5.7 Command Line Client

#### **输入刚才设置的MySQL的密码，按Enter键（回车键）**

#### 出现下面界面就说明已经安装成功了

**至此，**MySQL数据库**安装成功**

## 配置环境变量

#### 找到MySQL的安装路径

#### 右击此电脑选择“属性”

#### 先点击“高级系统设置”，再点击“环境变量”

#### 在“系统变量”中选择“Path”，点击“编辑”

#### 点击“新建”，将MySQL的安装路径添加上去，之后点击“确定”

#### 直接点击“确定”

#### 验证环境变量是否配置好，按下“window+R”键 弹出运行框，输入“cmd”进入window命令行

#### 输入“mysql -u root -p”按下回车

#### 输入密码，按下“Enter键（回车键）”，出现下面界面则是已经配置成功

# 数据库管理软件

## workbench

### 下载

下载地址：<https://dev.mysql.com/downloads/workbench/>

### 创建连接

### 数据库管理

### 表管理

### sql 脚本执行
