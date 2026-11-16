---
title: "课题十：AI性能数据分析助手"
doc_id: 256212053
slug: gikt9npc1xstc4pf
book_id: 73651885
words: 9251
updated_at: 2026-02-06T06:59:30.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/gikt9npc1xstc4pf
---
# 模块效果图

# 数据库设计

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Column | Datatype | PK | NN | AI | Default / Expression | 注释 |
| id | INT | ✅ | ✅ | ✅ |  |  |
| created\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP | 创建时间 |
| updated\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP | 更新时间 |
| project\_id | INT |  |  |  | NULL | 项目 id |
| configs | JSON |  |  |  | NULL | 数据配置 |

# 重点知识

## AI 性能分析的流程

1. 填写数据源，数据源是一个 url 地址
2. 使用`Playwright`在打浏览器中打开地址并访问，页面加载成功后，进行截图
3. 将截图内容发给 ai 转换成文字描述，然后结合性能分析提示词一起发给 ai 行性能分析

## 示例

- 示例图片，复制到豆包中

- 性能数据提取提示词，将图片的内容转换成文字，将提示词也复制到豆包中

- 性能分析提示词，将豆包中生成的内容复制到提示词模板中，替换掉下面的性能压测数据集内容，然后再一起发给豆包

## 浏览器截图

实现思路：

- 先截图，高度无法预测，所以直接设置为 5000，后面再做裁剪
- 截图成功后，会有大量纯色部分，这些部分需要裁剪
- 裁剪完成后，返回图片的二进制内容，发给 ai 进行数据提取

## 性能数据分析

​

# 接口设计

## 数据库操作模块

## 路由模块

## 加载路由模块

## Apifox 测试接口

# 前端页面

## 页面基本布局完成

### 添加 api 文件

### 创建布局文件

### 添加路由代码

### 修改`AgentView`

在浏览器中访问效果如下

## 数据源加载与配置

- `el-date-picker`：<https://element-plus.org/zh-CN/component/date-picker>

## ai 性能分析

## 结果处理

### 结果显示

### 导出结果

# 完整代码
