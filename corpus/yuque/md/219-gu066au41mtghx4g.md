---
title: "阶段十二. DevEco Studio实操之黑盒覆盖率测试"
doc_id: 256210676
slug: gu066au41mtghx4g
book_id: 73651885
words: 1974
updated_at: 2026-02-06T06:51:24.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/gu066au41mtghx4g
---
DevEco Studio支持黑盒覆盖率测试，不需要开发测试用例，将编译插桩的HAP包推到设备上，然后对该应用模拟用户操作，退出应用后即可生成覆盖率报告，当前仅支持Stage模型。

# 操作步骤

1. 将设备与电脑进行连接，并对应用签名，具体请参考[应用/元服务运行](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-running-app-V5)和[应用/元服务签名](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5)。
2. 执行hvigor插桩编译命令，编译后在{projectPath}/{moduleName}/.test/default/intermediates/ohosTest路径下会生成init\_coverage.json文件，供后续生成覆盖率报告使用。

- moduleName：执行测试的模块。
- productName：当前生效的product，可以通过点击DevEco Studio右上方图标进行查看。

1. 如果设备上已存在待测试的应用，先卸载应用，不存在则跳过此步骤：

- bundleName：设备上已安装的应用包名。

1. 将插桩编译生成的HAP包安装到设备上：

- SignedHapPath：已签名的HAP包路径，默认在模块的build\default\outputs\default目录下。

1. 在设备上模拟用户操作，进行黑盒测试，测试完毕后，退出应用。
2. 从设备上取出覆盖率数据json文件存放到电脑本地：

- LocalPath：数据在电脑本地存放的路径，默认存放在当前执行命令的目录。

> 说明
>
> 在多模块相互跳转的场景下，只需要取最后退出的模块下生成的覆盖率数据json文件，但特殊场景下如多模块无跳转关系，则需要取每个独立模块下生成的覆盖率数据json文件。

1. 生成覆盖率报告：

- projectPath：工程路径。
- reportPath：指定的覆盖率报告文件生成路径。
- 黑盒覆盖率文件保存路径：可以任意指定，该路径用于拷贝上一个步骤取出的覆盖率数据，可以是目录或json文件。

说明

在多模块相互跳转的场景下，需要取各模块的init\_coverage.json文件路径，与黑盒覆盖率文件保存路径通过#拼接生成coverageFile参数。

1. 在本地找到报告文件路径并在浏览器中打开，查看代码覆盖率详情，关于覆盖率的计算方式请参考[查看覆盖率报告](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-ui-test-V5#section10394362109)。

# 查看覆盖率报告

测试覆盖率报告有四个测量维度，分别是：

- 语句覆盖率（Statements）：每个语句是否都已执行。
- 分支覆盖率（Branches）：每个流程控制的各个分支是否都已执行。
- 函数覆盖率（Functions）：每个函数是否都已调用。
- 行覆盖率（Lines）：每个可执行代码行是否都已执行。

以下是关于四个测量维度的细节说明：

- **流程控制**

常见的流程控制语句有if、while、do...while、switch、for等等，以及三目运算符（condition ? exprIfTrue : exprIfFalse），需要确保流程控制的每个边界情况（即分支）都被执行。

- **行（Lines of Source Code） vs 可执行代码行（Lines of Executable Code）**

- “行覆盖率”中的行是指可执行代码行（Lines of Executable Code），而不是源文件中所有的行（含空行）（Lines of Source Code）。一般来说，包含语句的每一行都应被视为可执行行，而复合语句（简称为语句块，用 {} 括起来）会被忽略，但其内容除外。如下所示非可执行行标记为+0：

- 对于DevEco Studio的覆盖率测试引擎来说：

- import、声明语句都被视为非可执行行（+0），赋值等语句视为可执行行（+1）。
- 如果某行存在可执行代码，则这一整行会被视为可执行代码行（+1）。
- 如果一个语句被拆分为多行，则该可执行代码块中，仅第一行被会视为可执行行。
- 如果某行只包含标点符号**}**、**});** 或 **;** ，会被视为非可执行行（+0）。
- 如果某行只定义方法名，会被视为非可执行行（+0）。
- 不管嵌套语句横跨多少行，可执行行的数目仅会 +1。

示例如下：

- **可执行代码行 vs 语句**

一般情况下，如果我们遵守良好的代码规范，可执行代码行和语句的表现是一致的。然而当我们将两个语句放一行时，就会得到不同的结果。如下所示，第一段代码是2 lines、2 statements，第二段代码是1 line、2 statements。

- **测试覆盖率报告的其他标识**

- E：'else path not taken'，表示 if/else 语句的 if（含 else if）分支已测试，而 else 分支未测试。
- I：'if path not taken'，与上面的 'E' 相反，即 if（含 else if） 分支未测试。
- Nx：表示当前可执行代码行被执行了N次。
- 粉色（背景色）：语句/函数未覆盖。
- 黄色（背景色）：分支未覆盖。

- **通过注释语法忽略指定代码**

代码中的某些分支可能很难、甚至无法测试，Deveco Studio提供了instrument ignore \* 语法来进行忽略，使得某些代码不计入覆盖率。

说明

使用时需先清除缓存，点击菜单栏**Build -> Clean Project**。

- **忽略文件：**在源文件中加入注释 // instrument ignore file或者 /\* instrument ignore file \*/，加入注释后，该文件不再插桩，覆盖率报告也不会有该文件。
- **忽略代码块、class、function等：**在代码块前加入/\* instrument ignore next \*/或者// instrument ignore next即可忽略。
- **忽略if/else分支：**在条件表达式前加上// instrument ignore if或者/\* instrument ignore if\*/（忽略if），// instrument ignore else或者/\* instrument ignore else\*/（忽略else）。
