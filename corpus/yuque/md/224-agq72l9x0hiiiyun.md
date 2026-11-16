---
title: "阶段八. 鸿蒙系统综合项目一"
doc_id: 256210631
slug: agq72l9x0hiiiyun
book_id: 73651885
words: 9060
updated_at: 2026-02-06T06:51:07.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/agq72l9x0hiiiyun
---
# 模块创建

一个鸿蒙可以由多个模块组成，Entry 是入口模块，只有有一个，Feature 是功能模块可以有多个，模块可以根据业务来划分。每个 Feature 模块可以单独编译成 hap，即安装包。hap 就相当于 Android 应用中的 apk

## 设置要运行模块

## 运行多个模块

模块和模块之间有关联，必须一起打包到手机上。

比如 Entry 模块会使用到 LoginAndReg 模块，则需要做以下设置

# 将图片复制到指定位置

图片在课堂派中有

# 登录界面

## 效果图

## 功能描述

- 完成指定的页面
- 文本按钮点击会切换颜色
- 短信验证码登录
- 记住密码，下一次打开软件时自动填充账号密码，用户再点击登录按钮，也可以实现自动登录直接跳转到主界面
- 输入框内容不能为空
- 登录成功跳转到主界面，登录失败则提示登录失败

### Day03

# 注册页面

## 效果图

## 功能描述

- 点击返回按钮，返回到登录页面
- 每个输入框都必需输入内容
- 密码和确认密码必须一致
- 手机号不能重复注册
- 清空按钮，清空所有输入的内容
- 用户类提取

## Day03

# 忘记密码页面

## 效果图

## 功能描述

- 根据手机号和昵称查询密码，并 Toast 显示
- 如果在登录页面用户已经输入了手机号，则直接将手机号自动填入到忘记密码页面

​

# 主界面

## 效果图

## 功能描述

- 实现标签页及切换功能
- 选中的标签图片和文字效果如上图所示

# 首页标签页面

## 效果图

## 功能描述

- 轮播图
- 网格菜单
- 产品列表

# 我的标签页面

## 效果图

## 功能描述

- 显示登录的用户信息
- 理解生命周期函数作用
- 返回到登录页面，了解 pushUrl 和 replaceUrl 的区别

​

# 全部实现代码

## 目录结构

## main\_pages.json

## EntryAbility

## LoginPage

## BorderTextInput

## MsgCodeBtn

## TitleBar

## RdbHelper

## UserTable

## RegPage

## ForgetPage

## MainPage

## HomeModel

## HomeView

## MineView

## MineModel

## UserInfoPage
