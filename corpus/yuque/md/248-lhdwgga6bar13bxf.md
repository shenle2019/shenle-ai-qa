---
title: "win10-Mysql安装教程"
doc_id: 256208176
slug: lhdwgga6bar13bxf
book_id: 73651885
words: 1389
updated_at: 2026-02-06T06:34:06.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/lhdwgga6bar13bxf
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

# 8.0.40

## 下载

下载地址：<https://dev.mysql.com/downloads/windows/installer/8.0.html>

## 安装

择自定义安装，可以自己选择安装地址

3.选择需要的产品，添加到右侧。单击右侧已经添加的产品，更改下载地址。每一个产品都需要更改，如下图：

4.提示目录已存在，不用管，直接yes关闭，下一步就可以

5.安装下载刚刚添加的产品

6.一路向下就可以了

7.设置端口，默认3306，一般不用更改，直接下一步，如果该[端口被占用](https://so.csdn.net/so/search?q=%E7%AB%AF%E5%8F%A3%E8%A2%AB%E5%8D%A0%E7%94%A8&spm=1001.2101.3001.7020)，可以更改为其他端口 ，比如3307

8.推荐勾选第二个，这个是密码校验，第一个是强密码校验，MySQL8.x更换了加密插件。如果选择第一种强加密校验，可能无法与Navicat等图形化客户端连接

9.设置管理员用户root密码，Weak提示密码等级弱，直接忽略就行

10.继续一路向下

此步为安装完成

11.检验是否安装成功

安装成功！

12.MySQL Workbench 也是一个数据库图形化设计软件，在上面第三部，选择的四个产品中的其中一个

## 配置环境变量

按`win`,搜索输入`环境变量`。

若你按照上述的方法配置的MySQL,绝对路径与下面一样， 否则复制粘贴自己设置的MySQL服务的bin的绝对路径。  
`C:\Program Files\MySQL\MySQL Server 8.0\bin`

这样可以通过启动终端， 输入命令的方式启动MySQL了。
