---
title: "BeanShell 断言JDBC"
doc_id: 256211382
slug: wgk9igi2p1ddz74t
book_id: 73651885
words: 326
updated_at: 2026-02-06T06:55:33.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/wgk9igi2p1ddz74t
---
### 使用 BeanShell 断言

BeanShell 断言允许你使用 Java 代码编写自定义的断言逻辑，适用于更复杂的验证场景。

#### 步骤

1. **添加 JDBC Request 采样器**：配置好数据库连接信息和 SQL 查询语句。
2. **添加 BeanShell 断言**：在 JDBC Request 采样器上右键选择“添加” -> “断言” -> “BeanShell 断言”。
3. **编写 BeanShell 代码**：  
   以下是一个示例代码，假设 SQL 查询返回结果包含 `name` 和 `age` 两个字段，你想验证 `name` 字段的值为 “John”，`age` 字段的值为 25。
