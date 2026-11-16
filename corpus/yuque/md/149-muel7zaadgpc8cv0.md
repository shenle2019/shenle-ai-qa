---
title: "webui框架项目分析教程"
doc_id: 256211294
slug: muel7zaadgpc8cv0
book_id: 73651885
words: 1220
updated_at: 2026-02-06T06:55:01.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/muel7zaadgpc8cv0
---
# 概述

## 前提条件

- 阅读文件

## 项目获取

## 解压项目

## 导入项目

## 修改解释器

### 删除项目中自带的`.venv`目录

### 添加解释器

## 下载依赖

重新添加了虚拟环境后，就需要重装下载依赖到虚拟环境目录中

确认项目中存在依赖文件，没有的话，自己创建，然后从 1.5.1 这小节中去复制相关内容到创建的文件中保存

### requirements.txt

- `pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`：使用阿里云下载

成功下载后，可以在`.venv/lib`目录下看到如下内容，版本号有差异不用管

## 项目目录

## 配置环境

本教程中提供的浏览器及驱动，可以问老师要。太新的浏览器版本可能导致自动化运行时，会很慢

双击`chrome_76.0.3809.100.exe`进行安装，这个安装是全自动的，安装成功后就自动启动`Chrome`

chromedriver 驱动下载地址：<https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json>

### 配置环境变量

不建议有中文路径，文件中的路径只能参考不要照抄

### 检查配置

> 一定是重新打开的终端，如果在 pycharm 等工具中使用，一定要重启 pycharm。不然无法使用到最新的环境变量

- 检查`Chrome`配置

- 检查`chromedriver`配置

### 关闭浏览器自动升级

1. 点击搜索，输入服务

1. 在「名称」列表中分别找到并双击以下 2 项服务：

1. GoogleUpdater InternalService
2. GoogleUpdater Service

1. 点击「停止」按钮，并将「启动类型」设置为「禁用」。
2. 点击「应用」并关闭「服务」管理器。

只要是和更新有关的都要设置为禁用

# 项目启动阶段分析

## 项目入口 cli.py

### 启动过程

通过 cli.py 来启动程序，查看终端中的日志

## CasePlugin.py

自定义的一个插件，在 cli.py 指定，会自动调用处理

## 数据读取

### debug 分析

### yaml\_case\_parser 函数

### load\_yaml\_files 函数

### load\_context\_from\_yaml 函数

`context.yaml`用于保存一些公共数据

### debug 分析

灰色都是相关数据，可以在 debug 窗口中查看

数据读取完毕后，又会回到`yaml_case_parser`函数中，可根据下图的断点来了解程序的执行

## 测试用例模板

## 读取 conftest.py

`conftest.py`是 `pytest` 自动读取的文件，读取规则为先扫描和 `cli.py` 文件同级目录下的`conftest.py`再继续扫描读取子目录中的`conftest.py`

下面的了解即可

至此，下个数据加载的过程就介绍到这里

# 测试用例执行过程

## WebTestRunner.py

## 参数处理

- `test_case_execute`函数有两个参数

- `login_driver`是通过`@fixture`来处理的
- `caseinfo`是通过动态创建测试用例时处理的

### login\_driver

`login_driver`通过`fixture`进行传递，所以先会去 `conftest.py`中找到相应的函数。这是根据函数名来匹配的，此时会执行`login_driver()`函数中的代码，并将`yield driver`中这个`driver`变量传递给`test_case_execute`给`login_driver`变量

> 从`@pytest.fixture(scope='function')`中，可以了解到`login_driver` 的作用域是`function`，所以每个测试用例执行时，都会触发`login_driver`函数，如果只想启动一次浏览器，需要设置`scope='session'`

### caseinfo

在`CasePlugin.py`中

## KeyWords.py

封装了每个步骤的函数，在测试用例文件中通过关键字来指定步骤需要使用的函数，例如 yaml 文件中

## 执行步骤

### 1\_Alogin\_001.yaml

- 以`1_Alogin_001.yaml`来演示

> webui 调试如果停留太久，可能会与浏览器的连接断点，这个时候就需要重新开始 debug

#### 第一步

进行数据渲染之前。要理解数据渲染是什么意思，做了什么事。不是每个步骤都需要进行数据渲染

调用函数后，就会执行相应的函数代码

#### 错误演示

再点击执行下一步，查看图片中异常信息，要记住

#### 第二步

#### 第三步

> 后面步骤都差不多

### 2\_Aregistersuccess\_001.yaml

这里演示一下数据渲染，其它的与上面的登录示例差不多

如上，调试运行的时候，前面很多不关心的步骤就会快速执行

#### 渲染之前

渲染之前的模块

渲染之前的全局变量中的数据

#### 渲染之后

### 6\_login\_ddt.yaml

这里演示 ddts 的读取
