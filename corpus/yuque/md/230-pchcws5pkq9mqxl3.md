---
title: "阶段二. 开发工具DevEco Studio详解"
doc_id: 256210570
slug: pchcws5pkq9mqxl3
book_id: 73651885
words: 1858
updated_at: 2026-02-06T06:50:50.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/pchcws5pkq9mqxl3
---
# 鸿蒙中的应用与元服务详解

## 普通应用

鸿蒙 App 项目

安装使用，桌面会有图标

## 元服务

本质上就是小程序，但是是系统层面上的小程序，不需要安装，即用即开，用完就走

# 普通应用的创建与目录结构

## 创建普通应用

打开DevEco Studio，在欢迎页单击**Create Project**，创建一个新工程。

## 目录结构

- **AppScope > app.json5**：应用的全局配置信息。
- **entry：**应用/服务模块，编译构建生成一个HAP。

- **src > main > ets**：用于存放ArkTS源码。
- **src > main > ets > entryability**：应用/服务的入口，一个 HAP 可以有一个或多个 Ability 类，一个 Ability 类就是一个窗口，一个窗口可以有多个页面。
- **src > main > ets > pages**：应用/服务包含的页面。
- **src > main > resources：**用于存放应用/服务模块所用到的资源文件，如图形、多媒体、字符串、布局文件等。关于资源文件的详细说明请参考[资源分类与访问](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/resource-categories-and-access-V5)。

|  |  |
| --- | --- |
| 资源目录 | 资源文件说明 |
| base>element | 包括字符串、整型数、颜色、样式等资源的json文件。每个资源均由json格式进行定义，例如：   - boolean.json：布尔型 - color.json：颜色 - float.json：浮点型 - intarray.json：整型数组 - integer.json：整型 - pattern.json：样式 - plural.json：复数形式 - strarray.json：字符串数组 - string.json：字符串值 |
| base>media | 多媒体文件，如图形、视频、音频等文件，支持的文件格式包括：**.png**、**.gif**、**.mp3**、**.mp4**等。 |
| rawfile | 用于存储任意格式的原始资源文件。rawfile不会根据设备的状态去匹配不同的资源，需要指定文件路径和文件名进行引用。 |

- **src > main > module.json5**：Stage模型模块配置文件，主要包含HAP的配置信息、应用在具体设备上的配置信息以及应用的全局配置信息。具体请参考[module.json5配置文件](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/module-configuration-file-V5)。
- **build-profile.json5：**当前的模块信息、编译信息配置项，包括buildOption、targets配置等。
- **hvigorfile.ts**：模块级编译构建任务脚本。
- **oh-package.json5**：描述三方包的包名、版本、入口文件（类型声明文件）和依赖项等信息。

- **oh\_modules**：用于存放三方库依赖信息，包含应用/服务所依赖的第三方库文件。
- **build-profile.json5：**应用级配置信息，包括签名、产品配置等。
- **hvigorfile.ts：**应用级编译构建任务脚本。
- **oh-package.json5：**描述全局配置，如：依赖覆盖（overrides）、依赖关系重写（overrideDependencyMap）和参数化配置（parameterFile）等。

# ArkTS 在鸿蒙系统中的应用

## ArkTS 实操应用场景介绍

ArkTS是鸿蒙生态的应用开发语言。它在保持**TypeScript（简称TS）**基本语法风格的基础上，进一步通过规范强化静态检查和分析，使得在程序运行之前的开发期能检测更多错误，提升代码健壮性，并实现更好的运行性能。同时，提供了声明式UI范式、状态管理支持等相应的能力，让开发者可以以更简洁、更自然的方式开发高性能应用。 仓颉也鸿蒙开发的语言，不过是新出的，侧重点在于 AI 和大模型这一块

## **ArkTS相比TS特性差异**

## ArkUI 简介

ArkUI是一套构建分布式应用界面的声明式UI开发框架。它使用简洁的UI信息语法、丰富的UI组件、以及实时界面预览工具，帮助您提升HarmonyOS应用界面开发效率30%。您只需使用一套ArkTS API，就能在多个HarmonyOS设备上提供生动而流畅的用户界面体验。

## ArkUI 应用机制与操作方式介绍

### UI 更新机制

前端 Vue 和 React 类似

响应式

原理与现实生活中的订阅关注相似。以关注功能为例，当关注一个主播后，该主播发布了新的内容，则会通知关注它的粉丝。而 UI 更新机制也是差不多，通过装饰器来告诉编译器，哪些数据变化后需要更新 UI 界面。

### 逻辑和UI分离

# 预览器的应用实操机制

## 预览机制在工作中的基本应用

最常用，默认预览当前打开的文件，所以如果打开的不是 ets 文件且带有@Entry 或@Preview 装饰器，则无法预览

## 实时预览&双向预览&多设备预览

### 实时预览

部分属性的改动可以立马在预览器中看到效果

### 双向预览

双向预览可以在代码编辑区域定位到相应的代码，这个功能用起来非常方便

### 多设备预览

> 注意：不能与双向预览同时开启

## 多语言切换机制实操场景解析

文字显示时，在实际的 App 开发中可能需要适配多语言环境。这个时候需要通过字符串资源来实现

### 资源分类

官网参考资料：<https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/resource-categories-and-access-V5>

应用开发中使用的各类资源文件，需要放入特定子目录中存储管理。资源目录的示例如下所示，base目录、限定词目录、rawfile目录、resfile目录称为资源目录，element、media、profile称为资源组目录。**注意： stage模型多工程情况下，共有的资源文件放到AppScope下的resources目录。**

# 鸿蒙OS的日志窗口与日志分析机制

## Run

编译运行时，显示的日志信息

## 预览器编译日志

## 预览器日志

## 模拟器和真机日志

模拟器和真机日志使用是一样的，选择好对应的设备即可

​
