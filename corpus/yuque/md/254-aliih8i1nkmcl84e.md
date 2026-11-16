---
title: "win10-Android自动化测试环境搭建"
doc_id: 256207745
slug: aliih8i1nkmcl84e
book_id: 73651885
words: 430
updated_at: 2026-02-06T06:31:01.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/aliih8i1nkmcl84e
---
# 概述

本教程主要演示基于 Appium 搭建 Android 的 App 自动化测试环境

# 环境搭建

## 获取资料

下载后，解压如下

## 安装模拟器

本教程使用的是雷电模拟器

官网地址：<https://www.ldmnq.com/>

安装步骤全部下一步

启动

### 设置

### 安装应用

获取应用

将上面的`apk`文件拖拽到雷电模拟器中

## JDK

## NodeJS

建议使用`nvm`安装，可以方便的切换版本，因为下面的 appium 工具可能会随着时间的更新而要求更高的 nodejs 版本。nodejs 不要安装在 C 盘

## SDK 配置

路径中不要有中文，也不要有空格。获老师获取 sdk 压缩包

下面是本教程中位置

配置环境变量

修改`path`变量

验证是否配置成功

查看连接的设备，`adb devices`，图片中的内容只是参考，不用一模一样

## 安装 appium

使用 node 的 v16 或 v18 版本，cmd 必须使用管理员权限打开

- `npm i -g appium@2.1.3`

下载成功后，可以到 npm 配置的全局下载的位置查看

### 配置 appium 的环境

- `appium driver install uiautomator2@2.29.8`

### 启动 appium

- 通过`where appium`命令确保 appium 只有类似如下两个位置

- `appium`运行

## 安装 appium inspector

在菜单或桌面可以找到安装好的程序

### 连接 appium 服务

`platformVersion`要根据模块器的版本来调整，不要照抄

- `adb shell getprop ro.build.version.release`：获取 Android 设备的`platformVersion`
