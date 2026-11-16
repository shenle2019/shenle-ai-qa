---
title: "api-engine项目分析教程"
doc_id: 256211110
slug: lbiogm9uzwcl1an7
book_id: 73651885
words: 4364
updated_at: 2026-02-06T06:53:57.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/lbiogm9uzwcl1an7
---
# 概述

## 项目获取

加课码 `YKWHYD`

点击开始学习，然后下载

## 解压项目

## 导入项目

## 添加解释器

### 删除项目中自带的`.venv`目录

### 添加解释器

在 pycharm 的右下角

## 下载依赖

找到项目根目录下依赖文件

### requirements.txt

这是最新的，原来的可能会导致部分内容下载失败，可以将下面的内容复制替换到项目中的 `requirements.txt`文件中。然后通过命令

- `pip install -r requirements.txt`：安装依赖
- `pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`：使用阿里云下载

成功下载后，可以在`.venv/lib`目录下看到如下内容，版本号有差异不用管

## 项目目录

目录简介

- `cli.py`：为项目的启动入口
- `examples/examples-ds`：使用`yaml`保存测试用例
- `examples/examples-dsw`：使用`excel`保存测试用例

# 项目启动阶段分析-Excel 格式

## cli.py

这是项目的启动文件

### run 函数

下面的 run 函数是通过 setup.py 打包时，才会执行，在本教程中不做讨论

### 项目入口

1. 测试用例所在目录拼接
2. 告诉 pytest 核心执行类的路径，在 pytest 执行后，扫描到了以`test_`开头的函数，并将函数中参数 caseinfo 标记 fixture 传入的参数

1. case\_path 保存了测试用例所在的目录
2. pytest.main 函数来启动执行。并指定插件

### debug 分析执行时的数据

## CasesPlugin.py

### debug 分析数据

### debug 按钮说明

：多用该按钮，直接执行在下一个断点处，可以快速调试

## CaseParser.py

读取测试用例数据

## 用例数据读取

主要支持两种用例数据格式，使用哪种方式可以在`cli.py`的启动参数中指定。然后在`CaseParser.py`中具体执行

- `excel`：具体查看`excel_case_parser`函数，定义在`ExcelCaseParser.py`
- `yaml`：具体查看`yaml_case_parser`函数，定义在`YamlCaseParser.py`

### excel 格式模板

#### context.xlsx

相关读取代码，会将相关数据保存到一个`g_context()`对象中的字典里面，`g_context`是一个单例类，只能创建一个对象，如何即可以实现数据的共享

#### 1\_测试用例\_读书屋.xlsx

模板中的使用`{{}}`包裹的都是动态数据，在后面程序中会动态渲染。具体的处理过程后面再说明

### excel 文件数据读取

- `keywords.yaml`：文件定义了接口请求的参数、请求结果处理的方式参数，在后面再分析。

这里就是整个 excel 文件的处理过程。yaml 文件格式处理，后面再分析

​

# 测试用例执行过程

测试用例的执行主要是通过 `ApiTestRunner.py`中的`test_case_execute`函数来处理的，该函数的参数`caseinfo`可接收每条测试用例的数据

## allure 报告标题的处理

## KeyWords.py

`KeyWords.py`文件封装了常用的操作函数，具体使用后面再分析，代码有兴趣的可以提前了解一下

## globalContext.py

定义了一个单例类`g_context`，不管在哪里实例化都创建的都是同一个对象，该类中有一个私有属性`_dic`是一个字典

## 数据准备

## 数据渲染

将`context`中的数据渲染到模板中，通过`key`在`context`中找到`value`，然后将这个`value`的值替换掉模板中的`{{key}}`的数据

如上图，渲染之前模板中的数据为`{{password}}`，此时就会以`password`作为`key`，从`context`中去寻找是否有`password`这个`key`对应的`value`数据，如下图，找到的`value`是`123456`，然后替换模板中的`{{password}}`。如果没有`{{}}`这种格式的数据，就不会做任何处理

## 执行步骤操作

以第一个测试用例来说明，分为六个步骤，每个步骤分为：

- 步骤描述：用于描述步骤说明
- 关键字：对应`keywords.py`中定义的函数，每个函数的操作方式会在`keywords.yaml`中定义

- 参数\_1：操作对应的链接、操作符、或参数

### 第一步

发起请求，并将请求结果保存到`g_context()`对象中共享。

- 参数 \_1：表示请求的 url 地址，对应 URL
- 参数 \_2：请求地址参数，对应 params，一般是 get 请求的参数
- 参数 \_3：请求头参数，对应 headers
- 参数 \_4：请求体参数，对应 body，即 post 请求的参数

### 第二步

处理响应结果中的 msg 字段，要求响应结果必须包含该字段

- 步骤描述
- 关键字：对应`keywords.py`对应的`ex_jsonData`函数
- 参数 \_1：`jsonpath`的提取操作符，`$..msg`获取响应结果中所有的 `msg` 属性，并以列表的形式返回
- 参数 \_2：提取操作符提取的结果列表的索引位置
- 参数 \_3：`msg_success`，作为将结果保存在`g_context()`对象中的`key`

### 第三步

处理响应结果中的 code 字段，要求响应结果必须包含该字段

- 步骤描述
- 关键字：对应`keywords.py`对应的`ex_jsonData`函数
- 参数 \_1：`jsonpath`的提取操作符，`$..code`获取响应结果中的所有的`code`属性，并以列表的形式返回
- 参数 \_2：提取操作符提取的结果列表的索引位置
- 参数 \_3：`msg_code`，作为将结果保存在`g_context()`对象中的`key`

### 第四步

处理响应结果中的 token 字段，要求响应结果必须包含该字段

- 步骤描述
- 关键字：对应`keywords.py`对应的`ex_jsonData`函数
- 参数 \_1：`jsonpath`的提取操作符，`$..token`获取响应结果中的所有的 `token` 属性，并以列表的形式返回
- 参数 \_2：提取操作符提取的结果列表的索引位置
- 参数 \_3：`token`，作为将结果保存在`g_context()`对象中的`key`

### 第五步

对响应结果中的 `msg_success` 字段做断言处理，

- 步骤描述
- 关键字：对应`keywords.py`对应的 `assert_text_comparators` 函数
- 参数 \_1：`{{msg_success}}`，从`g_context()`取出`msg_success`这个`key`对应的`value`
- 参数 \_2：断言预期值
- 参数 \_3：比较运算符，将`{{msg_success}}`对应的值与参数 \_2 对应的预期值进行相应的断言

### 第六步

对响应结果中的 `msg_code` 字段做断言处理，

- 步骤描述
- 关键字：对应`keywords.py`对应的 `assert_text_comparators` 函数
- 参数 \_1：`{{msg_code}}`，从`g_context()`取出`msg_code`这个`key`对应的`value`
- 参数 \_2：断言预期值
- 参数 \_3：比较运算符，将`{{msg_code}}`对应的值与参数 \_2 对应的预期值进行相应的断言

## 总结

到此基于 Excel 用例模板的执行过程就全部整理完成。其它测试用例的执行过程基本类似，通过本教程了解整个框架的运行过程，测试用例的执行过程可以打断点+debug 来分析，教程中的断点位置都可以参考使用

# 项目启动阶段分析-Yaml 格式

## 测试用例目录

## cli.py

## yaml 文件读取过程

### 与 Excel 数据的不同之处

yaml 格式通过 ddts 来指定测试数据，该数据会被保存在字典中，以 context 为 key，在执行测试用例时会获取 context 中的数据

### ddts 单条数据处理

### ddts 多条数据处理

## 测试用例的执行

测试用例的执行基本与 Excel 一致，这里再赘述。参考 3.6 节

# 测试报告生成

处理测试报行，每个测试用例执行完成后，都会触发该函数

# 常用错误

逐步收集补充

# 其它文章
