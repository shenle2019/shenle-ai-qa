---
title: "Git 安装 + Gitee 注册 + SSH 免密配置 + 私有仓库完整操作手册"
doc_id: 279547544
slug: giewgef92hnqc14m
book_id: 73651885
words: 1675
updated_at: 2026-07-30T07:11:19.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/giewgef92hnqc14m
---
# **Git 安装 + Gitee 注册 + SSH 免密配置 + 私有仓库完整操作手册**

适用系统：Windows / MacOS（分开说明），全程图文步骤化，新手可直接照着操作目标：本地 Git ↔ Gitee 私有仓库，实现**免密推送拉取、私有仓库访问、SSH 密钥安全配置**

## **一、Git 安装**

### **1.1 Windows 安装 Git**

1. 下载地址：[https://git-scm.com/download/win](https://link.wtturl.cn/?target=https%3A%2F%2Fgit-scm.com%2Fdownload%2Fwin&scene=im&aid=582478&lang=zh)

1. 运行安装包，**推荐默认一路下一步**，重点两处配置：

- Adjusting your PATH environment：选择【Git from the command line and also from 3rd-party software】

- Choosing the SSH executable：选择【Use OpenSSH】（必须，后续免密依赖）

1. 安装完成
2. 验证安装 打开 Git Bash（右键菜单 Git Bash Here）输入：

git --version

输出版本号即成功。

### **1.2 MacOS 安装 Git**

方式 1（推荐），终端执行：

xcode-select --install

弹出窗口点击安装；验证：

git --version

### 1.3 配置全局用户名邮箱（必须配置，代码提交身份）

打开 Git Bash / 终端执行，替换为你自己的信息：

## **二、Gitee 账号注册步骤**

1. 打开官网：[工作台 - Gitee.com](https://gitee.com/) <https://gitee.com>

1. 右上角【注册】

1. 参数填写：

- 仓库名称：英文名称（不能中文）

- 仓库介绍：随意填写

- 是否公开：选择【私有】（重点！私有仓库，陌生人看不到）

- 勾选：初始化 README（可选）

- 选择分支模型：默认 main

1. 点击【创建】

✅ 私有仓库特性：只有你、被邀请的成员能访问，外部人员无法搜索、克隆代码。

## **三、SSH 密钥生成（实现免密拉取 / 推送，核心步骤）**

原理：生成一对密钥：公钥（放到 Gitee）、私钥（留在本地电脑），配对成功无需账号密码

### **3.1 Git Bash / 终端执行生成密钥**

在任何一下目录下点右键，选择 git Bash,执行下面的指令：

#### **交互操作（全部直接回车，不要输入密码！免密需求）**

Enter file in which to save the key (/c/Users/xxx/.ssh/id\_ed25519): 【回车】

Enter passphrase (empty for no passphrase): 【回车】

Enter same passphrase again: 【回车】

执行完成，密钥生成成功。

### **3.2 找到公钥文件**

Windows 路径：C:\Users\你的用户名.ssh\id\_ed25519.pubMac 路径：~/.ssh/id\_ed25519.pub

用记事本打开 **.pub** **后缀文件**，**全选复制全部内容**（从ssh-ed25519一直到最后的邮箱，不要漏字符）

### **3.3 Gitee 添加公钥**

1. 登录 Gitee → 右上角头像 →【设置】

1. 左侧菜单【安全设置】→【SSH 公钥】

1. 标题：随便写（例如：家用 Windows 电脑）

1. 公钥文本框：粘贴刚刚复制的全部公钥内容

1. 点击【确定】，验证账号密码完成添加

### **3.4 测试 SSH 连通性**

Git Bash 执行：

ssh -T git@shturl.cc

首次连接输入 yes 回车出现类似提示即为成功：Hi xxx! You've successfully authenticated, but shturl.cc does not provide shell access.

❗ 失败排查：

公钥复制不全、有换行空格

选错公钥（不要复制没有.pub 的私钥）

防火墙拦截

## **四、本地项目** **↔** **Gitee 私有仓库 完整操作**

### **方式 A：本地已有代码，推送至新建私有仓库**

### **方式 B：克隆已存在的私有仓库到本地**

# 复制私有仓库的SSH地址，执行克隆 git clone git@shturl.cc:用户名/仓库名.git

✅ SSH 模式配置好密钥后，克隆私有仓库**不需要输入账号密码**

### **日常标准工作流**

⚠️ 重要提醒：如果使用 **HTTPS 地址** 克隆，就算配置 SSH 密钥依然需要账号密码！私有仓库免密**只能使用 SSH 地址**。

## **五、私有仓库权限管理（私人盾牌进阶操作）**

### **5.1 私有仓库如何添加合作者（多人协作）**

1. 进入私有仓库主页 →【管理】→【成员管理】

1. 【添加成员】输入对方 Gitee 用户名

1. 设置权限：

- 开发者：可以推送代码

- 观察者：只能拉取、查看代码，不能推送

1. 发送邀请，对方同意后即可访问私有仓库

### **5.2 撤销电脑 SSH 权限（设备丢失 / 换电脑）**

Gitee 设置 → 安全设置 → SSH 公钥，找到对应设备公钥，删除即可，该电脑立刻无法访问你的私有仓库。

### **5.3 多台电脑免密方案**

每一台电脑都单独生成 SSH 密钥，分别把公钥添加到 Gitee 账号 SSH 列表。

## **六、常见故障汇总**

1. Permission denied

- 公钥粘贴错误；使用了 HTTPS 地址；仓库地址写错

2.每次推送依然要求输入账号密码 → 检查 remote 地址：git remote -v，如果是 https 地址，切换为 ssh 地址

# 修改远程地址示例 git remote set-url origin git@shturl.cc:用户名/仓库名.git

3.新建仓库分支名为 master 和 main 冲突

git push -u origin main

## **七、极简操作清单（可保存快速查阅）**

1. 安装 Git → 配置 user.name/user.email

1. Gitee 注册，创建【私有仓库】

1. ssh-keygen 生成密钥，复制 pub 公钥

1. Gitee 安全设置添加 SSH 公钥，测试连通 ssh -T git@shturl.cc

1. 使用 SSH 地址 clone/push 私有仓库，实现免密访问
