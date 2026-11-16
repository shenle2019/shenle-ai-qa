---
title: "阶段三. 鸿蒙OS环境变量配置机制"
doc_id: 256210573
slug: bb6f0czgwp5aqqg2
book_id: 73651885
words: 1521
updated_at: 2026-02-06T06:50:52.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/bb6f0czgwp5aqqg2
---
# Command Line Tools for HarmonyOS Next

Command Line Tools集合了HarmonyOS应用开发所用到的系列工具，包括代码检查codelinter、三方库包管理ohpm、命令行解析hstack、编译构建hvigorw。

## HDC

hdc（HarmonyOS Device Connector）是为开发人员提供的用于调试的命令行工具，通过该工具可以在windows/linux/mac系统上与设备进行交互。

### 配置环境变量HDC\_SERVER\_PORT

在**此电脑 > 属性 > 高级系统设置 > 高级 > 环境变量**中，添加HDC端口变量名为：HDC\_SERVER\_PORT，变量值可设置为任意未被占用的端口，如7035。

环境变量配置完成后，关闭并重启DevEco Studio。

## 相关命令环境变量配置

> 注意：注意路径，不要照抄。根据自己的解压路径来

### Windows

#### 验证命令

> 验证命令，在DevEco Studio创建的项目目录下，所有命令都可以通过
>
> 注意：部分命令必须在鸿蒙项目目录下才可以运行
>
> `hdc`一定要配置成功，否则会影响后面的配置

### MacOS

1. 打开终端工具，执行以下命令，根据输出结果分别执行不同命令。

- 如输出结果为/bin/bash，则执行以下命令，打开.bash\_profile文件。

- 如输出结果为/bin/zsh，则执行以下命令，打开.zshrc文件。

1. 单击字母“i”，进入**Insert**模式。
2. 输入以下内容，在PATH路径下添加HDC\_SERVER\_PORT端口信息。

> 参考效果图片

1. 编辑完成后，单击**Esc**键，退出编辑模式，然后输入“:wq”，单击**Enter**键保存。
2. 执行以下命令，使配置的环境变量生效。

- 如果步骤1时打开的是.bash\_profile文件，请执行如下命令：

- 如果步骤1时打开的是.zshrc文件，请执行如下命令：

1. 环境变量配置完成后，关闭并重启DevEco Studio。

# Python

下载：<http://python.p2hp.com/downloads/index.html>

本教程版本为 **3.10.11**

## 安装

### MacOS

> 安装步骤基本都是默认配置，不需要

> 在`MacOS`中，`Python`命令会自动配置到环境变量中，检查`Pyhton`命令是否可用
>
> - `python3 -V`
>
> - `pip3 -V`
>
> 在`MacOS`中命令默认名称为`python3和pip3`，使用不方便，创建相应的软连接
>
> 找命令的安装位置
>
> - `which python3`
> - `which pip3`
>
> 创建软连接
>
> - `ln -s /Library/Frameworks/Python.framework/Versions/3.10/bin/python3 /Library/Frameworks/Python.framework/Versions/3.10/bin/python`
> - `ln -s /Library/Frameworks/Python.framework/Versions/3.10/bin/pip3 /Library/Frameworks/Python.framework/Versions/3.10/bin/pip`
>
> 验证软件连接

### Windows

## 配置环境变量

> 如果完全按本教程的操作，上面的环境变量是会自动配置好的，不用手动操作。
>
> 验证环境变量配置是否成功，**不能使用之前打开过的终端命令窗口**

# PyCharm

常用的Python开发工具，测试人员使用免费的社区版本即可，专业版本可自行破解

下载地址：<https://www.jetbrains.com.cn/pycharm/download/?section=windows>

> 安装步骤基本都是下一步。

# DevEco Testing Hypium

DevEco Testing Hypium(以下简称Hypium)是HarmonyOS平台的UI自动化测试框架，支持开发者使用python语言为应用编写UI自动化测试脚本，主要包含以下特性：

1. Hypium提供了原生控件/图像/比例坐标等**多种控件定位能力**，支持多窗口操作以及触摸屏/鼠标/键盘等**多种模拟输入功能**，支持**多设备**并行操作，能够覆盖各类场景和多种形态设备上的自动化用例编写需求。
2. Hypium包含配套**用例编写辅助插件**, 支持控件查看/投屏操作等多种用例开发辅助功能，提升用例开发体验和效率。
3. Hypium能够为执行的用例生成详细的**用例执行报告**，并且自动记录设备日志以及执行步骤截图，为开发者和测试人员提供高效和专业的测试用例执行和结果分析体验。

## Hypium

解压下载的`devecotesting-hypium-5.0.7.200.zip`

- `DevecoTesting-Hypium-5.0.7.200.zip`：是`Pycharm`的一个插件
- `hypium-5.0.7.200.zip`：自动化测试框架
- `hypium_perf-5.0.7.200.zip​`：hypium\_perf是基于hypium框架的性能测试能力扩展包，支持通过UI自动化操作检测应用特定使用场景的性能指标。通过hypium\_perf编写的脚本需结合DevEco Testing的场景化性能测试服务使用，以输出可视化的性能测试报告。

## 安装`Pycharm`插件

## 安装Hypium

在终端中执行以下命令

## 安装 Hypium\_perf

需要先安装 Hypium，解压压缩包`hypium_perf-5.0.7.200.zip`​

然后在终端中打开，输入`install.bat`

确认安装，输入`y`

回车确认执行安装

也可以手动安装

安装完成后，可以在 PyCharm 中查看

# 创建 Hypium 项目

# UIViewer插件使用

> 在Windows系统中，插件有bug，**模拟器无法连接**。只能连接真机设备。报错如下
>
> 在MacOS-arm cpu 的设备上，可以使用
>
> 不过可以`DevEco Testing`工具也有`UIViewer`使用

# DevEco Testing

DevEco Testing是一站式的应用测试服务平台。为开发者提供自动化测试框架，及稳定性、性能等专项测试服务，覆盖应用测试全周期，助力打造高品质应用。

**安装过程基本就是下一步，不要有中文路径即可**
