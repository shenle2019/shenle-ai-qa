---
title: "阶段一. 鸿蒙OS vs 安卓&IOS"
doc_id: 256210560
slug: uhear4ww88u41ue0
book_id: 73651885
words: 2791
updated_at: 2026-02-06T06:50:46.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/uhear4ww88u41ue0
---
# 鸿蒙 OS 的特点，长处与注意事项

## 鸿蒙系统概述

HarmonyOS 是一款面向万物互联时代的、全新的分布式操作系统。 在传统的单设备系统能力基础上，HarmonyOS 提出了基于同一套系统能力、适配多种终端形态的分布式理念，能够支持手机、平板、智能穿戴、智慧屏、车机、PC、智能音箱、耳机、 AR/VR 眼镜等多种终端设备，提供全场景（移动办公、运动健康、社交通信、媒体娱乐等） 业务能力。

官网地址：<https://developer.huawei.com/consumer/cn/>

## 1+8+N 概念

## 鸿蒙系统的分类

- 商业鸿蒙系统：华为公司自己产品或者授权给其它公司使用产品
- 开源鸿蒙系统：OpenHarmony，开源原子基金会去维护，商业鸿蒙是完全支持OpenHarmony。相当于 Android 的 AOSP

## 核心技术理念

### 一次开发，多端部署

### 自由流转

## 鸿蒙 2030 愿景及关键特征

# 开发者账号生态注册流程及细节

## 注册账号

地址：<https://id1.cloud.huawei.com/CAS/portal/userRegister/regbyphone.html?>

使用邮件还是手机号注册都可以

注册完成，即可登录

## 实名认证

主要跟着官网步骤操作即可。没有什么难度，个人账号就以个人开发者认证即可

参考资料：<https://developer.huawei.com/consumer/cn/doc/start/rna-0000001062530373>

# 环境搭建与安装细节

## DevEcoStudio 下载安装

下载地址：<https://developer.huawei.com/consumer/cn/download/>。目前需要登录才可下载

DevEco Studio支持Windows和macOS系统，下面将针对两种操作系统的软件安装方式分别进行介绍。

### Windows环境

#### 运行环境要求

为保证DevEco Studio正常运行，建议电脑配置满足如下要求：

- 操作系统：Windows10 64位、Windows11 64位
- 内存：16GB及以上
- 硬盘：100GB及以上
- 分辨率：1280\*800像素及以上

#### 安装DevEco Studio

1. 下载完成后，双击下载的“deveco-studio-xxxx.exe”，进入DevEco Studio安装向导。在如下界面选择安装路径，默认安装于C:\Program Files路径下，也可以单击**浏览（B）...**指定其他安装路径，然后单击**Next**。

1. 在如下安装选项界面勾选**DevEco Studio**后，单击**Next**，直至安装完成。

1. 安装完成后，单击**Finish**完成安装。

1. 说明

- DevEco Studio提供开箱即用的开发体验，将HarmonyOS SDK、Node.js、Hvigor、OHPM、模拟器平台等进行合一打包，简化DevEco Studio安装配置流程。
- HarmonyOS SDK已嵌入DevEco Studio中，无需额外下载配置。HarmonyOS SDK可以在DevEco Studio安装位置下DevEco Studio\sdk目录中查看。如需进行OpenHarmony应用开发，可通过Settings > OpenHarmony SDK页签下载OpenHarmony SDK。

### macOS环境

#### 运行环境要求

为保证DevEco Studio正常运行，建议电脑配置满足如下要求：

- 操作系统：macOS(X86) 11/12/13/14 macOS(ARM) 12/13/14
- 内存：8GB及以上
- 硬盘：100GB及以上
- 分辨率：1280\*800像素及以上

#### 安装DevEco Studio

1. 在安装界面中，将“**DevEco-Studio.app**”拖拽到“**Applications**”中，等待安装完成。

1. 安装完成后，接下来请根据[配置代理](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-environment-config-V5)，检查和配置开发环境。说明

- DevEco Studio提供开箱即用的开发体验，将HarmonyOS SDK、Node.js、Hvigor、OHPM、模拟器平台等进行合一打包，简化DevEco Studio安装配置流程。
- HarmonyOS SDK已嵌入DevEco Studio中，无需额外下载配置。HarmonyOS SDK可以在DevEco Studio安装位置下DevEco Studio\sdk目录中查看。如需进行OpenHarmony应用开发，可通过DevEco Studio > Preferences **>** OpenHarmony SDK页签下载OpenHarmony SDK。

### 诊断开发环境

为了您开发应用/服务的良好体验，DevEco Studio提供了开发环境诊断的功能，帮助您识别开发环境是否完备。您可以在欢迎页面单击**Diagnose**进行诊断。如果您已经打开了工程开发界面，也可以在菜单栏单击**Help > Diagnostic Tools > Diagnose Development Environment**进行诊断。

DevEco Studio开发环境诊断项包括电脑的配置、网络的连通情况、依赖的工具是否安装等。如果检测结果为未通过，请根据检查项的描述和修复建议进行处理。

### 启用中文化插件

1. 单击**File > Settings**（macOS为**DevEco Studio > Preferences** ） **> Plugins**，选择**Installed**页签，在搜索框输入“Chinese”，搜索结果里将出现**Chinese(Simplified)**，在右侧单击**Enable**，单击**OK**。

1. 在弹窗中单击**Restart**，重启DevEco Studio后即可生效。

## Command Line Tools for HarmonyOS Next

Command Line Tools集合了HarmonyOS应用开发所用到的系列工具，包括代码检查codelinter、三方库包管理ohpm、命令行解析hstack、编译构建hvigorw。

## Python

下载：<http://python.p2hp.com/downloads/index.html>

本教程版本为 **3.10.11**

## PyCharm

常用的Python开发工具，测试人员使用免费的社区版本即可，专业版本可自行破解

下载地址：<https://www.jetbrains.com.cn/pycharm/download/?section=windows>

> 安装步骤基本都是下一步。

## DevEco Testing Hypium

DevEco Testing Hypium(以下简称Hypium)是HarmonyOS平台的**UI自动化测试框架**，支持开发者使用`python`语言为应用编写UI自动化测试脚本，主要包含以下特性：

1. Hypium提供了原生控件/图像/比例坐标等**多种控件定位能力**，支持多窗口操作以及触摸屏/鼠标/键盘等**多种模拟输入功能**，支持**多设备**并行操作，能够覆盖各类场景和多种形态设备上的自动化用例编写需求。
2. Hypium包含配套**用例编写辅助插件**, 支持控件查看/投屏操作等多种用例开发辅助功能，提升用例开发体验和效率。
3. Hypium能够为执行的用例生成详细的**用例执行报告**，并且自动记录设备日志以及执行步骤截图，为开发者和测试人员提供高效和专业的测试用例执行和结果分析体验。

## DevEco Testing

DevEco Testing是一站式的应用测试服务平台。为开发者提供自动化测试框架，及稳定性、性能等专项测试服务，覆盖应用测试全周期，助力打造高品质应用。

**安装过程基本就是下一步，不要有中文路径即可**

# 测试流程中的注意事项与选项

鸿蒙操作系统（HarmonyOS）的测试流程涉及多个方面，确保应用程序在鸿蒙系统上能够稳定运行并提供良好的用户体验。以下是一些在鸿蒙测试流程中需要注意的事项和选项：

## 测试注意事项

- 手动对应用进行必要的预置操作，包括权限授予、用户协议确认、账号登录等等，以保障自动化遍历可顺利进行
- 确保手机性能状态正常，包括网络连接通畅、非高温、非低电量（推荐>80%），以及其他可能对性能表现产生影响的变量
- 不要设置各类锁屏密码，确保自动化能完成上滑解锁
- 应用图标在桌面可见，不要藏起来（自动化会翻页查找，但不会打开文件夹）进入服务卡片后，选择要测试的应用，点击创建任务即可开始，任务过程无需人工干预

## 兼容性测试

- **UI适配**：检查应用程序在不同屏幕尺寸和分辨率下的显示效果。
- **API兼容性**：确保应用程序使用的API在鸿蒙系统中可用并且行为正确。
- **第三方库**：如果使用了第三方库，确保这些库在鸿蒙系统中兼容。

## 功能测试

- **核心功能**：验证应用程序的核心功能是否正常工作，如登录、支付、数据同步等。
- **边缘情况**：测试各种边缘情况，如网络不稳定、存储空间不足等。
- **多任务处理**：检查应用程序在多任务环境下的表现，确保不会出现崩溃或性能下降。

## 性能测试

- **启动时间**：测量应用程序的启动时间，确保启动速度符合预期。
- **响应时间**：测试用户操作的响应时间，确保用户体验良好。
- **资源占用**：监控CPU、内存、电池等资源的使用情况，确保应用程序不会过度消耗资源。

## 安全测试

- **数据保护**：确保敏感数据（如密码、支付信息）在传输和存储过程中加密。
- **权限管理**：检查应用程序请求的权限是否合理，确保不会滥用权限。
- **漏洞扫描**：使用安全工具扫描应用程序，查找潜在的安全漏洞。

## 用户体验测试

- **界面设计**：确保界面设计符合鸿蒙系统的UI规范，提供一致的用户体验。
- **交互流畅性**：检查用户交互的流畅性，确保没有卡顿或延迟。
- **多语言支持**：如果应用程序支持多语言，确保所有语言版本都经过测试。

## 分布式测试

- **设备协同**：测试应用程序在多设备协同场景下的表现，如手机与手表、平板之间的互动。
- **服务连续性**：确保应用程序在设备切换时能够无缝衔接，保持服务的连续性。

## 自动化测试

- **脚本编写**：编写自动化测试脚本，提高测试效率和覆盖率。
- **持续集成**：将自动化测试集成到持续集成（CI/CD）流程中，确保每次代码提交都能自动进行测试。

## 反馈与修复

- **用户反馈**：收集用户的反馈意见，及时发现和解决问题。
- **缺陷管理**：使用缺陷管理系统记录和跟踪发现的问题，确保每个问题都能得到妥善处理。

## 文档与培训

- **测试文档**：编写详细的测试计划和测试用例，确保测试过程有据可依。
- **团队培训**：对测试团队进行培训，确保他们熟悉鸿蒙系统的特性和测试工具。
