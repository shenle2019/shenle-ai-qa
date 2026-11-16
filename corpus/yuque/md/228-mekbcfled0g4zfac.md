---
title: "阶段四. 实操-鸿蒙OS系统下的调试与运行机制"
doc_id: 256210580
slug: mekbcfled0g4zfac
book_id: 73651885
words: 1640
updated_at: 2026-02-06T06:50:54.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/mekbcfled0g4zfac
---
# 调试功能

使用调试方式来运行项目，可以由程序员自己来控制程序的运行，同时可以很方便的查看变量等数据内容。是一种非常有效的排错手段

## 打断点

## 调试工具介绍

# 预览器机制下的调试

在新的版本中预览器也支持调试。

# 模拟器运行与调试

模拟器常见问题：<https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-emulator-faqs-V5#section172728114485>

其它操作与预览器一样，点击运行或调试按钮即可

​

# 真机运行与调试

真机运行必须要签名

## 前提条件

在**Phone或Tablet**上查看**设置 > 系统**中开发者选项是否存在，如果不存在，可在**设置 > 设备名称**中，连续七次单击“版本号”，直到提示“开启开发者选项”，点击**确认开启**后输入PIN码（如果已设置），设备将自动重启，请等待设备完成重启。

## 使用USB连接方式

1. 使用USB方式，将Phone或Tablet与PC端进行连接。
2. 在**设置 > 系统 > 开发者选项**中，打开“**USB调试**”开关（确保设备已连接USB）。
3. 在Phone或Tablet中会弹出“允许USB调试”的弹框，单击**允许**。

1. 在菜单栏中，单击**Run>Run'模块名称'**或，或使用默认快捷键**Shift+F10**（macOS为**Control+R**）运行应用/服务。

1. DevEco Studio启动HAP的编译构建和安装。安装成功后，设备会自动运行安装的HarmonyOS应用/服务。

> 说明
>
> 设备连接后，如果DevEco Studio无法识别到设备，显示“No device”，请参考[设备连接后，无法识别设备的处理指导](https://developer.huawei.com/consumer/cn/doc/harmonyos-faqs-V5/faqs-app-debugging-3-V5)。

## 鸿蒙系统的自动签名机制与调试方式

官网指南：<https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5>

## 设备UUID机制实操应用

- 添加鸿蒙设备

<https://developer.huawei.com/consumer/cn/doc/app/agc-help-add-device-0000001946142249#section67331926102911>

为了使用方便，将 hdc 命令配置到环境变量

- 添加 Android 设备

<https://developer.huawei.com/consumer/cn/forum/topic/0201452734347330728?fid=0101587866109860105>

## 鸿蒙系统中的手动签名场景与调试

指南：<https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5#section297715173233>

### 生成 key 和 CSR

注意：后缀名为`.p12`，然设置密码

### 申请调试证书

### 调试Profile文件

### 手动签名

#### 添加证书指纹

#### 添加公钥指纹

完成，就可以运行到真机了

### 添加新的签名方式

# ArkUI Inspector实操使用

开发者可以使用ArkUI Inspector，在DevEco Studio上查看应用在真机上的UI显示效果，并通过查看多次操作后的界面状态，快速分析定位UI界面存在的问题。

ArkUI Inspector支持的功能包括：

- 查看设备上应用的UI显示效果。
- 导出及导入应用UI界面快照，脱离设备查看UI显示效果。
- 在组件树上选择组件，UI界面自动框选对应组件，属性列表显示当前组件的属性信息。
- 在UI界面点击选择组件，组件树对应组件变化为选中状态，属性列表显示当前组件的属性信息。
- UI组件源码跳转，选中UI组件后点击源码跳转按钮即可跳转至源码位置。
- 在UI界面上选择Show Component Border，可查看当前页面上所有组件显示区域。
- 在组件树上选择自定义组件，属性列表显示当前组件配置的状态变量信息以及影响组件。

## 使用场景

针对界面较复杂的应用：

- 通过组件树查看组件的父子关系，检查是否存在冗余组件。
- 针对应用在真机或模拟器上运行出现UI界面显示异常，尤其经过多次界面复杂操作后产生的界面错误以及后台逻辑错误，进行问题分析定位。

## 使用约束

- 仅运行在前台的应用支持Inspector查看。
- 已通过USB或WLAN连接设备。
- 仅支持Stage工程。
- 仅支持全屏应用或者焦点在前台的窗口。
- 不支持应用市场上架的商用签名应用。

## 操作步骤

1. 在DevEco Studio下方点击**ArkUI Inspector**，打开ArkUI Inspector。

如果没有可以在菜单栏中打开

1. 点击RUN或者DEBUG按钮，将应用推包到设备上，在设备应用列表选择当前显示在设备前端的UI进程。

1. ArkUI Inspector左侧为当前的组件树结构，中间栏显示当前设备的UI显示界面，右侧在选中组件的情况下为当前组件的属性信息。当设备上UI发生变化时，可点击中间栏右上角按钮同步设备上的UI效果。可以在左侧组件树上选择或直接在UI界面点击选择组件。

点击，勾选组件树信息的配置项**Show Tree Statistics**，可显示组件树节点信息。

1. 在设备框，点击设备列表的最后一项**Stop inspector**，可断开与设备的连接。

## UI界面快照

ArkUI Inspector支持导出及导入应用UI界面快照，脱离设备查看应用UI界面显示效果。

- 在中间栏点击可以将应用UI界面快照导出到本地。导出成功后将默认在DevEco Studio中打开该快照。
- 在中间栏点击可以导入本地的应用UI界面快照。导入成功后将在DevEco Studio中打开该快照。

## UI组件源码跳转

1. 单击**Run > Edit Configurations**，勾选“**Enable DebugLine**”，点击**OK**保存后，重新运行工程，表示开启源码跳转功能。

1. 在ArkUI Inspector中，选中要进行源码跳转的UI组件。

1. 点击右侧的源码跳转按钮，即可跳转到UI组件源码位置。

## 显示布局边框

在UI显示设置上，勾选“**Show Component Border**”，可显示当前页面所有组件的布局信息。

## 查看UI组件的状态变量

点击自定义组件，可以查看自定义组件定义状态变量，以及状态变量影响的下一层组件。
