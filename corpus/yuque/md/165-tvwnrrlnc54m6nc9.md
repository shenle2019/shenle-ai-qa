---
title: "013-Git教程"
doc_id: 256211106
slug: tvwnrrlnc54m6nc9
book_id: 73651885
words: 479
updated_at: 2026-02-06T06:53:56.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/tvwnrrlnc54m6nc9
---
# 概述

主要用于团队中的代码管理。

git 工具官网：<https://git-scm.com/>

- 工具，git，管理工具，上传或拉取代码，工具的安装基本都是下一步，还要配置环境变量
- 远程仓库，保存代码

- 国内：gitee。<https://gitee.com/>
- 国外：github。<https://github.com/>

# 安装

<https://blog.csdn.net/weixin_64296810/article/details/139983964>

# Gitee 使用

必须要有账号

## 创建远程仓库

## 本地仓库配置

## 开启 Git

> 表示已经成功开启了 git 管理

## 将文件添加到暂存区

## 提交到本地仓库

> 如果已经关联了远程仓库，就可以直接 push

## 推送

> 输入成功，就会执行推送
>
> 密码错误

## 在远程仓库检查

# 仓库管理

## 添加开发者

# 修改提交及更新

## 修改代码

## 更新代码

## 冲突处理

当同一个文件被不同开发人员修改后，就会产生冲突。最终的效果，不是二选一，而整合在一起

- `Rebase`：还原
- `Merge`：合并，使用比较多

> 实际开发中，一般是先 pull 拉取最新代码到本地

### 解决冲突

#### 同一个文件，不同行

> 开发人员必须再自己检查一下代码

#### 同一个文件，同一行

> 减少冲突的方式，先 pull，再检查代码，再提交，再 push

# 分支

- 主线分支，不会在开发期间有代码修改等行为
- 实际开发中，一个版本对应一个分支，大家都该分支上开发，开发周期结束，将代码给测试人员测试，通过后，要上线了，再全并到主线分支中。

## 切换分支

## 合并分支

# 命令参考大全

- Git 大全：<https://gitee.com/all-about-git>
- Git 命令学习：<https://help.gitee.com/learn-Git-Branching/?locale=zh_CN>
