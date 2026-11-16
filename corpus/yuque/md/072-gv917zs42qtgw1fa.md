---
title: "课题七：AI接口用例设计助手功能实现"
doc_id: 256212017
slug: gv917zs42qtgw1fa
book_id: 73651885
words: 10804
updated_at: 2026-02-06T06:59:15.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/gv917zs42qtgw1fa
---
# 模块效果图

右侧菜单数据与 AI 需求评审一致，只是这里只有查看功能

# 数据库设计

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

### 解决数据复杂数据的保存问题

在本章功能中需要考虑一个复杂数据的情况，如下数据结构中的`steps`是一个字典。这个时候无法直接插入插入到数据库中会报错

报错信息如下

解决方案，将`steps`数据转换成 json 字符串即可，以下的函数都会做对应的修改

### AI 生成测试用例接口

## 加载路由模块

## Apifox 测试接口

# 前端页面

## 复制 api 文件

## 复制 TestCaseView.vue

## 添加路由链接

## 调整添加和编辑弹窗

将下面内容替换图片中的内容

### 添加功能调整

在 Vue 中有两种响应式写法，在早期的版本中`reactive`是针对复杂数据类型，`ref`无法针对多层复杂数据类型使用，但现在新版本中不会了。<https://cn.vuejs.org/guide/essentials/reactivity-fundamentals.html>

- `ref`
- `reactive`

> 在使用上 ref 的响应式数据需要通过`变量名.value`来操作数据，但`reactive`不用，
>
> 所以需要将代码中的`addOrEditForm.value`替换成`addOrEditForm`。一定要做哈

调整如下两处内容

### 编辑功能调整

解决方法，将`addOrEditForm.steps`所有属性进行判断，如果是`object`类型就是转换成字符串即可

## 调整查看用例弹窗

替换前

替换后如下

调整下面的代码，因为 steps 是一个字符串，所以需要转换成 json 对象

## 调整 AI 测试用例生成

因为 `steps`是一个对象，所以也需要转换成`json`格式的字符串才可以显示

# 完整代码
