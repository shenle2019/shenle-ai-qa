---
title: "课题六：AI测试用例智能体功能实现"
doc_id: 256212014
slug: di0vy8ekh0cml6ky
book_id: 73651885
words: 14461
updated_at: 2026-02-06T06:59:12.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/di0vy8ekh0cml6ky
---
# 模块效果图

右侧菜单数据与 AI 需求评审一致，只是这里只有查看功能

# 数据库设计

​

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Column Name | Datatype | PK | NN | AI | DefaultExpression | 字段注释 |
| id | INT(11) | ✔ | ✔ | ✔ |  | 主键ID（自增） |
| project\_id | INT(11) |  |  |  | NULL | 关联的项目ID |
| module\_id | INT(11) |  |  |  | NULL | 关联的需求 ID |
| name | VARCHAR(255) |  |  |  | NULL | 测试用例名称 |
| priority | VARCHAR(10) |  |  |  | 'p2' | 用例优先级（如p0/p1/p2） |
| precondition | VARCHAR(1024) |  |  |  | NULL | 用例前置条件 |
| expected | VARCHAR(1024) |  |  |  | NULL | 预期结果 |
| created\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP | 创建时间（默认当前时间） |
| updated\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP ON UPDATE CURRENT\_TIMESTAMP | 更新时间（自动刷新） |
| steps | LONGTEXT |  |  |  | NULL | 测试步骤（长文本） |

# 接口设计

## 数据库操作模块

## 路由模块

复制前面的路由模块

### 查询所有用例

每个用例需要有指定项目及模块 id。如果不指定就是查询全部

### 分页查询

代码然后较多，主要就是条件参数需要处理

- limit和offset就是分页查询相关的设置
- 分页查询还需要做一次总数的查询，就是当前条件一共有多少数据

### 批量删除

完整代码如下

删除不需要的内容

### AI 生成测试用例接口

## 加载路由模块

## Apifox 测试接口

# 前端页面

## 页面基本布局完成

创建`TestCaseView.vue`文件

### 添加路由配置

修改 `AgentView.vue` 中对应的访问地址

在浏览器中的效果如下，因为是复制之前的代码，所以效果如下。后面再一点点地去修改

### 添加 api 文件

## 修改左侧菜单的功能

- 添加查看功能

- 查询菜单数据

- 点击查看按钮实现一个弹窗，显示富文本框，显示需求内容，这里有几个问题要解决

1. 每次点击都会通过`open`事件去调用`initEditor`函数，从而创建一个 Vditor 对象，会造成内存浪费，要保存只用一个 Vditor 对象
2. 如何保证？确保 Vditor 对象只会创建一次，而后面点击查看时候重用并改成内容即可

- 实现 `handleNodeClick` 功能，和之前一样

## 添加表格显示

### 基本使用

官网地址：<https://element-plus.org/zh-CN/component/table>，主要分为两个组件

- `el-table`：表格组件，通过 `data` 属性指定数据源
- `el-table-column`：表格列组件，通过`prop`来指定显示的数据的属性值，通过`label`来显示列名

- 自定义列模板，`scope`是代码行数据对象，保存每一行对应的数据，`$index`是索引值，`row`为当前数据对象，按上图中的示例数据来说的话，就是`{ date: '2016-05-03', name: 'Tom', address: 'No. 189, Grove St, Los Angeles', }`

### 测试用例表格完成

使用对应的示例数据完成页面布局效果

- 加载表格数据

### 添加分页组件

官网资料：<https://element-plus.org/zh-CN/component/pagination>

### 查询指定模块的用例

## 添加和编辑测试用例及保存功能

- 添加时必须指定模块 id，通过左侧菜单点击获取
- 点击手动添加按钮，出现添加弹窗，如果没有模块 id 则提示

## 删除及批量删除

批量删除，通过 sql 中的 in 语法来实现。

### 添加后台接口

### 添加 api 接口

### 前端页面

## 查看测试用例

官网资料：<https://element-plus.org/zh-CN/component/descriptions>

<https://element-plus.org/zh-CN/component/tag>

## AI 测试用例生成

### 添加流式窗口

### 添加额外需求处理

### 添加主需求处理

不用改动

### 添加 ai 请求处理

### 添加 ai 结果处理

- ai 结果弹窗

- ai 结果处理，ai 生成的测试用例保存进`tmp_testcaseList`容器中，并显示在表格上

- 应用功能实现，在后台添加批量插入接口，然后在前端将选中的测试用例数据发送给批量插入接口

# 测试用例导出 Excel 功能

## excel 生成 demo

在 python 通过 pandas 来生成 Excel 文件

Pycharm 查看 Excel 表格的插件

## 接口设计

## 前端页面

### 添加 api 函数

# 完整代码
