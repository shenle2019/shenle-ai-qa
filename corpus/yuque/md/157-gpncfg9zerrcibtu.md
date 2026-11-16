---
title: "Python 的 LEGB 规则详解"
doc_id: 256211192
slug: gpncfg9zerrcibtu
book_id: 73651885
words: 605
updated_at: 2026-02-06T06:54:24.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/gpncfg9zerrcibtu
---
LEGB 规则是 Python 中变量查找的顺序规则，它定义了当访问一个变量时，Python 解释器查找该变量的顺序。LEGB 是四个作用域的首字母缩写：

## 1. LEGB 的含义

- **L (Local)** - 局部作用域
- **E (Enclosing)** - 嵌套函数的非全局作用域
- **G (Global)** - 全局作用域
- **B (Built-in)** - 内置作用域

Python 会按照 L → E → G → B 的顺序查找变量。

## 2. 各作用域详解

### Local (局部作用域)

当前函数内部定义的变量。

### Enclosing (嵌套作用域)

外层非全局作用域（闭包函数中的变量）。

### Global (全局作用域)

模块级别定义的变量。

### Built-in (内置作用域)

Python 内置的变量和函数（如 `len`, `open`, `range` 等）。

## 3. 变量查找顺序示例

## 4. 修改作用域变量

### global 关键字

修改全局作用域的变量：

### nonlocal 关键字

修改嵌套作用域的变量（Python 3+）：

## 5. 特殊注意事项

1. **变量遮蔽问题**：局部变量会遮蔽同名全局变量

1. **lambda 表达式**也遵循 LEGB 规则：

1. **类定义**中的变量查找略有不同，类有自己的命名空间

理解 LEGB 规则对于掌握 Python 的作用域和闭包概念至关重要，特别是在编写嵌套函数和装饰器时。
