---
title: "基于WIN 搭建VUE-API测试平台部署"
doc_id: 251194048
slug: ownu20cdhpf55ke1
book_id: 73651885
words: 366
updated_at: 2025-12-31T08:11:56.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/ownu20cdhpf55ke1
---
# 第一步：安装Python环境

参考：

# 第二步：安装数据库，并且导入SQL

当前框架的数据库为：MySQL 5.7.41 版本

参考：

# 第三步：启动后端

打开后端项目，比如：

通过编译工具打开项目，并且安装依赖

然后再修改你自己的数据库的配置，请进入到：platform-flask-server —config— dev\_settings.py

然后到app.py 文件当中启动即可，只要不报错就可以。

​

# 第四步：安装VUE

前提条件：安装node js

## NodeJS 环境搭建

## 运行 Vue 项目

cd 到前面 vue 项目中，在终端中执行

​

# 第五步：需要用到核心执行器

> 执行用例需要用到核心执行器，对应的核心执行器放在：`platform_api_5.0\核心执行器\api-engine`中。

**​**

**|操作步骤：**

1. 打开后端项目，比如：`platform-flask-server`
2. 切换到终端到你核心执行器，比如：`..\核心执行器\api-engine`，如下图

1. 在终端执行如下两个命令

​

3. 执行用例查看运行结果

在终端输入如下命令：

如图：

​
