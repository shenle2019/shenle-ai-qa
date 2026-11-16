---
title: "SQL的考核-试卷"
doc_id: 254497691
slug: luqx0z20ak9xpd8y
book_id: 73651885
words: 591
updated_at: 2026-01-24T11:32:30.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/luqx0z20ak9xpd8y
---
以下是提取出的SQL题目（不含参考答案）：

### 【简单】根据给出的表结构，写出对应的SQL

1）创建用户表（user）  
字段类型长度：

- uid int 整型
- uname varchar(20)
- password varchar(20)
- birthday date 日期

2）向用户表中追加字段email，varchar类型，长度20

3）向用户表最前面添加字段status，int类型

4）向用户表password字段后面添加sage，int类型

5）修改sage的名称为age

6）修改password字段的长度为50

7）修改status到email之后的位置

8）删除字段status

9）修改表的名称为userinfo

10）清空数据库表

11）销毁数据库表user

### 【一般】根据给出的表结构，写出对应的SQL

表X有三个字段：Code、Name、Age，其中Code为主键；  
表Y有三个字段：Code、Class、Score，其中Code + Class为主键

表X：

|  |  |  |
| --- | --- | --- |
| Code | Name | Age |
| 97001 | 张三 | 22 |
| 97002 | 赵四 | 21 |
| 97003 | 张飞 | 20 |
| 97004 | 李五 | 22 |

表Y：

|  |  |  |
| --- | --- | --- |
| Code | Class | Score |
| 97001 | 数学 | 80 |
| 97002 | 计算机 | 59 |
| 97003 | 计算机 | 60 |
| 97004 | 数学 | 55 |

1）找出所有姓张的学生，并按年龄从小到大排列

2）取出计算机科考成绩不及格的学生

3）在TableX表中增加一条学生记录

4）根据主键进行更新李五的年龄记录

5）删除TableX中没有考试成绩的学生记录

6）取出每一个科目成绩最高的学生记录

### 【一般】针对车辆信息表和违法信息表，请写出SQL语句

现有车辆信息表CAR\_RECORD表示车辆的编号、车牌号码、车辆类型（1：大型汽车；2：小型汽车）、车辆颜色：

|  |  |  |  |
| --- | --- | --- | --- |
| CAR\_ID | Car\_Num | Car\_Type | Car\_Color |
| 1 | 浙BV7731 | 1 | red |
| 2 | 浙D065HG | 2 | blue |
| 3 | 浙A12A26 | 2 | black |

违法表CAR\_DPRECORD表示车辆的过车编号、车牌号码、过车速度、违法类型、抓拍时间：

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| ID | Car\_Num | Car\_Speed | Rec\_type | Cap\_Date |
| 20200001 | 浙BV7733 | 76 | 网红灯 | 2012-01-01 12:41:48 |
| 20200002 | 浙D065HG | 88 | 超速 | 2012-01-01 12:41:43 |
| 20200003 | 浙A12A26 | 65 | 逆行 | 2012-01-01 12:41:49 |

1）新车登记错误，修改浙A12A26的车辆颜色为黄色  
2）计算小型汽车的平均车速
