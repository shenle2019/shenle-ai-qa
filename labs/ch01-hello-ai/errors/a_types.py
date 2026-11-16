# -*- coding: utf-8 -*-
# @Author: QX
# @File: A类型.py
# 创建变量

#ctrl+/ 注释
age = 18  # 整数

height = 1.75  # 浮点数

name = "小明"  # 字符串

is_passed = True  # 布尔值

#f _string
print(f"age = {age}, 类型: {type(age)}")

print(f"height = {height}, 类型: {type(height)}")

print(f"name = {name}, 类型: {type(name)}")

print(f"is_passed = {is_passed}, 类型: {type(is_passed)}")


name = input("请输入您的姓名：")
print("您好，" + name + "！")


a=input("请输入：")
a=float(a)
print(a,type(a))
