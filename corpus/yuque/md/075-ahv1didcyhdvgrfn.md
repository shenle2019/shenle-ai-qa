---
title: "课题三：AI测试数据生成智能体功能实现"
doc_id: 256211990
slug: ahv1didcyhdvgrfn
book_id: 73651885
words: 9641
updated_at: 2026-02-06T06:59:01.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/ahv1didcyhdvgrfn
---
# 模块效果图

# 数据库设计

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Column Name | Datatype | PK | NN | AI | DefaultExpression | 字段注释 |
| id | INT(11) | ✔ | ✔ | ✔ |  | 主键ID（自增） |
| project\_id | INT(11) |  |  |  | NULL | 关联的项目ID |
| name | VARCHAR(255) |  |  |  | NULL | 模板名称 |
| description | TEXT |  |  |  | NULL | 模板描述 |
| created\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP | 创建时间（默认当前时间） |
| updated\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP ON UPDATE CURRENT\_TIMESTAMP | 更新时间（默认当前时间，更新时自动刷新） |
| fields | JSON |  |  |  | NULL | 字段配置（JSON格式） |
| hint | VARCHAR(1000) |  |  |  | NULL | 提示信息 |
| count | INT(11) |  |  |  | NULL | 生成的数量 |
| format | VARCHAR(45) |  |  |  | NULL | 数据格式 |
| lang | VARCHAR(45) |  |  |  | NULL | 语言 |

# ai 基础知识使用

## ai 基础 demo

上面的程序我们需要注意几点：

- 导入的是 openai 中的 OpenAI，这不搞错了
- 创建 OpenAI 对象时，需要指定 api\_key，从使用的大模型官网上去获取，不要直接用老师的，这个是会收费的，老师的在讲完课程后就注销了
- 还有 base\_url，使用的大模型地址，一定要和 api\_key 对应，不要搞乱了，比如出现，使用 deepseek 的 api\_key，但却用了阿里云的地址
- prompt 是提示词，让 ai 做什么就在提示词中指定
- 调用大模型时，需要通过 model 来指定使用的大模型名称，通过 messages 来指定提示词，基本就是图中的两用方式，system 就是上下文，user 就是用户的内容
- 最后就是要对结果进行处理，通过打印观察结果的数据结构

## ai 实战

实现生成测试数据的 ai 示例

执行结果如下

在这里执行时，我们会发现在结果生成的过程中，会一直没有任何反馈，用户体验不好，接下来我们来介绍另一种方式，使用流的方式来处理结果的显示

## 流式结果处理

### demo 演示

### 实战演示

## 提示词模板提取及渲染

现在 ai 基础已经完成，在这里我们完成提示词的模板提取。为什么要提取模板，不提取也可以的，但其实提示词内容占的篇幅很长，为了看程序方便就将提示词提取保存在一个文件中，也可以提高提示词的重用性

# 接口设计-增删改查

## 添加数据库模块

## 添加路由模块

复制 ProjectController.py 再粘贴，然后修改模块名为`TestDataTemplateController.py`，如下图。再修改下图中位置相应的代码。此时与项目管理类似的功能就完成了。这也是模板开发的好处。学员可以掌握这个技巧，但更建议学员自已动手写这些内容

这里我们也需要调整一下 queryAll 方法，查询的所有内容应该与项目关联，所以都需要传递对应的 project\_id。完整的代码如下，都是增删改查

## 加载路由模块

在 app.py 中添加，路由加载代码

## 测试接口

接口测试完成后。就可以准备前端页面了

# 接口设计-ai 数据生成

## ai 生成测试数据接口

在这个接口中主要的就是流式结果的处理，重点逻辑都在`generate`这个函数中

# 前端页面-ai 数据生成

## 添加 api 请求

复制 `project_api.js` 直接粘贴，然后按下图修改对应的内容

## 添加前端页面

## 添加 router 地址

## 修改链接地址

## ai 接口对接

添加接口请求及响应处理代码

执行打印如下，流式数据的 value 是在没有处理时就是收到数据 1 的位置的内容，无法看懂，所以需要使用TextDecoder 这个文本解码器来处理，处理后的内容就如收到数据 2 的位置内容

## 流式数据处理弹窗组件

因为这个弹窗会在多处地方被使用，所以我们封装了一个自定义组件

### 创建文件

自定义组件，一般习惯放在 components 目录中

这里使用了自定义组件，自定义组件，主要是为了提高代码的重复使用率，不用也可以

- defineProps：设置组件的属性，这些属性的数据可以在调用的地方进入传值
- computed：Vue 的计算属性，本质是一个函数，可以写复杂的逻辑来处理数据，与方法不同的地方在于，它是有缓存的，同时可以当成属性来使用
- watch：侦听器，可以监测一个属性的数值变化，从而执行对应的函数代码
- defineEmits：定义向外暴露的事件，从而实现组件向组件使用者传递数据

### 添加 AI 结果显示

## 提取 ai 请求 api 函数

### 解决 fetch 中的地址问题

使用 vite 提供的地址重写能力来解决

> 如果没有上面的地址重写，就会报错如下

### 提取 api 函数

因为 ai 请求处理在后续的功能中也会用到，所以这里需求将 ai 请求中可重用的代码提取到 api 文件中的函数

这里使用了封装思路是，将能通用的代码都提取到`test_data_template_api.js`中的

`processWithAIStream`函数中，但有部分业务代码的处理，不同的功能可能不一样，所以采用函数当成参数传进来的方式处理，这种方式的专业术语称为回调函数。如上面的`onMessage、onError、onComplete`三个函数都是当成参数。然后在`processWithAIStream`中将对应的函数参考取出来进行调用。好处就是`processWithAIStream`这个函数可以直接复制使用了，在其它模块中基本不需要修改，我们只需要关注`onMessage、onError、onComplete`这三个函数的修改了

# 前端页面-增删改查

## 前端页面

### 页面标题

### 基础配置

### **结果示例参考和字段配置**

### 保存模板

### 加载模板

这里需要使用到表格组件，<https://element-plus.org/zh-CN/component/table>。

### 运行生成及结果显示完整代码

- 完善结果界面

- 复制和下载
