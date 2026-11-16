---
title: "课题五：AI接口文档分析功能实现"
doc_id: 256212009
slug: mbhgq8vggrkdtay9
book_id: 73651885
words: 3644
updated_at: 2026-02-06T06:59:08.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/mbhgq8vggrkdtay9
---
# 模块效果图

AI接口文档分析功能的界面与课题四 AI 需求评审助手功能界面基本一致

- ai 的提示词不同

导入的示例

# 数据库设计

表结构也是一样的，表名`api_documents`

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Column | Datatype | PK | NN | AI | Default / Expression | 注释 |
| id | INT | ✔️ | ✔️ | ✔️ |  |  |
| project\_id | INT |  |  |  | NULL | 项目 id |
| name | VARCHAR(255) |  |  |  | NULL | 需求标题 |
| parent\_id | INT |  |  |  | NULL | 父 id |
| title | VARCHAR(255) |  |  |  | NULL | 暂未使用 |
| content | LONGTEXT |  |  |  | NULL | 需求内容，markdown 格式内容 |
| created\_by | VARCHAR(100) |  |  |  | NULL | 创建人 id，暂未使用 |
| is\_directory | TINYINT(1) |  |  |  | '0' | 是否是目录，暂未使用 |
| created\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP | 创建时间 |
| updated\_at | TIMESTAMP |  |  |  | CURRENT\_TIMESTAMP ON UPDATE CURRENT\_TIMESTAMP | 更新时间 |
| ai\_suggest | LONGTEXT |  |  |  | NULL | ai 评审内容 |

# 接口设计

## 数据库操作模块

- 这个和前面的都差不多，主要是和数据库表结构一一对应

## 路由模块

复制`DocumentController.py`再粘贴，然后修改模块名为`ApiDocumentController.py`，如下图。再修改下图中位置相应的代码。此时与项目管理类似的功能就完成了。这也是模板开发的好处。学员可以掌握这个技巧，但更建议学员自已动手写这些内容

> 如果有问题接口的业务需要，调整，再修改对应的代码即可。先复制了

## 加载路由模块

## apifox 测试接口

# 前端页面

## 复制 api 文件

## 复制 DocumentView.vue

复制`DocumentView.vue`文件，粘贴到`api_document`目录，被重命名为`ApiDocumentView.vue`

## 添加路由配置

修改 AgentView.vue 中对应的访问地址

## 调整部分代码

- 修改 api

- 将采纳改成历史记录
