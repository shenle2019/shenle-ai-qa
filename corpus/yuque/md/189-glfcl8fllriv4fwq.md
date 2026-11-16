---
title: "Git管理Python项目注意事项"
doc_id: 256210862
slug: glfcl8fllriv4fwq
book_id: 73651885
words: 219
updated_at: 2026-02-06T06:52:32.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/glfcl8fllriv4fwq
---
在使用 git 管理 Python 项目时，需要注意几点

# .gitignore

忽略文件，直接复制使用

有了这个依赖文件后，就可以无脑的使用 git -> add 这个菜单操作了

# 项目依赖文件

提交内容时，是不需要将.venv 目录提交的，所以需要先将项目使用的依赖导出到项目根目录下的`requirements.txt`文件中。

命令为 `pip freeze > requirements.txt`

注意，以后只要依赖发生变化都要重新导出项目依赖

在 git 服务器上的内容大概内容如下

# git 克隆的项目使用依赖

## 克隆项目

克隆后的项目目录如下

## 创建虚拟环境

## 激活虚拟环境

`.\.venv\Scripts\activate`

## 安装所有依赖

`pip install -r .\requirements.txt`
