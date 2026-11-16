---
title: "读书屋接口文档"
doc_id: 256209608
slug: rzq5c78q0yqulin0
book_id: 73651885
words: 3472
updated_at: 2026-02-06T06:44:27.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/rzq5c78q0yqulin0
---
### 接口：注册接口

- 地址：/user/register
- 类型：POST
- 状态码：200
- 简介：注册接口
- 请求接口格式：

- 返回接口格式：

### 接口：登录

- 地址：/user/login
- 类型：POST
- 状态码：200
- 简介：使用注册的账号进行登录
- 请求接口格式：

- 返回接口格式：

### 接口：点击榜单

- 地址：/book/listClickRank
- 类型：GET
- 状态码：200
- 简介：显示当前的点击榜单列表
- 请求接口格式：

- 返回接口格式：

### 接口：新书榜单

- 地址：/book/listNewRank
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：最新更新

- 地址：/book/listUpdateRank
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：全部作品-列表

- 地址：/book/listBookCategory
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：书籍详情页

- 地址：/book/queryBookDetail/id
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

├─ id: Number (必选) (书籍id)

- 返回接口格式：

- 地址：/book/listRank
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：排行榜

- 地址：/book/listRank
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：我的书架-我的书架

- 地址：/user/listBookShelfByPage
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：我的书架-最近阅读

- 地址：/user/listReadHistoryByPage
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：用户信息

- 地址：/user/userInfo
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：个人中心-我的书评列表

- 地址：/user/listCommentByPage
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：个人中心-我的书评列表

- 地址：/book/addBookComment
- 类型：POST
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：个人中心-我的反馈列表

- 地址：/user/listUserFeedBackByPage
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：个人中心-我的反馈提交

- 地址：/user/addFeedBack
- 类型：POST
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：账号设置-用户名

- 地址：/user/updateUserInfo
- 类型：POST
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：账号设置-修改密码

- 地址：/user/updatePassword
- 类型：POST
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：这家专区-注册

- 地址：
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：作家专区-小说列表

- 地址：/author/listBookByPage
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：作家专区- 稿费收入-订阅明细

- 地址：/author/listIncomeDailyByPage
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：作家专区- 稿费收入-稿费汇总

- 地址：/author/listIncomeMonthByPage
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：作家专区- 小说管理-新增书籍

- 地址：/author/addBook
- 类型：POST
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：作家专区- 章节管理列表

- 地址：/book/queryIndexList
- 类型：GET
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：作家专区- 章节管理-新增章节

- 地址：/author/addBookContent
- 类型：POST
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：

### 接口：作家专区- 章节管理-删除章节

- 地址：/author/deleteIndex/{{id}}
- 类型：DELETE
- 状态码：200
- 简介：无
- 请求接口格式：

- 返回接口格式：
