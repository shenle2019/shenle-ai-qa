---
title: "MySQL考试试题(题目+答案篇)"
doc_id: 256211240
slug: dya9ib13g84nawd5
book_id: 73651885
words: 5678
updated_at: 2026-02-06T06:54:40.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/dya9ib13g84nawd5
---
### 一、选择题

1. **题目**：数据库系统的核心是（ ）  
   A. 数据库客户端  
   B. 数据库管理系统  
   C. 数据模型  
   D. 软件工具  
   **答案**：B  
   **分析**：数据库系统的核心是数据库管理系统（DBMS），它负责数据库的建立、使用和维护。数据库客户端用于与数据库交互；数据模型是对现实世界数据特征的抽象；软件工具是辅助开发和管理数据库的手段。所以选B。
2. **题目**：在 SQL 中，下面哪个函数在计算时不会忽略 NULL 值（ ）  
   A. SUM(列)  
   B. AVG(列)  
   C. MAX(列)  
   D. COUNT(列)  
   **答案**：D  
   **分析**：`SUM(列)`、`AVG(列)`、`MAX(列)`在计算时会忽略空值`NULL`，而`COUNT(列)`会统计列中的所有值，包括空值（但`COUNT(*)`统计的是行数，不受空值影响）。因此选D。
3. **题目**：在 SQL 中，以下操作不正确的是（ ）  
   A. SELECT \* FROM table WHERE AGE IS NULL  
   B. SELECT \* FROM table WHERE AGE IS NOT NULL  
   C. SELECT \* FROM table WHERE AGE = NULL  
   D. SELECT \* FROM table WHERE NOT (AGE is null)  
   **答案**：C  
   **分析**：在SQL中，判断一个值是否为空用`IS NULL`，判断不为空用`IS NOT NULL`，`NOT (AGE is null)`等价于`AGE IS NOT NULL`。不能使用`AGE = NULL`来判断空值，所以C选项操作不正确。
4. **题目**：在 SQL 中，获取表中若干行数据使用（ ）子句。  
   A. INTO  
   B. UNIQUE  
   C. ORDER BY  
   D. WHERE  
   **答案**：D  
   **分析**：`WHERE`子句用于筛选满足特定条件的行数据；`INTO`用于将查询结果插入到指定的表或变量中；`UNIQUE`用于确保列中的值唯一；`ORDER BY`用于对查询结果进行排序 。所以获取表中若干行数据应使用`WHERE`子句，选D。
5. **题目**：下列实体集之间的联系属于多对多联系的是（ ）  
   A. 学校与教师  
   B. 商品条形码与商品  
   C. 班级与班长  
   D. 学生与课程  
   **答案**：D  
   **分析**：一个学生可以选修多门课程，一门课程也可以被多个学生选修，学生与课程之间是多对多联系。一个学校有多个教师，但一个教师只能属于一个学校，是一对多联系；一个商品条形码唯一对应一个商品，是一对一联系；一个班级只有一个班长，是一对一联系。所以选D。
6. **题目**：一个 SELECT 语句最少应该包括的子句是（ ）  
   A. SELECT，GROUP BY  
   B. SELECT，FROM  
   C. SELECT，WHERE  
   D. SELECT，ORDER BY  
   **答案**：B  
   **分析**：`SELECT`语句中，`SELECT`关键字用于指定要查询的列，`FROM`关键字用于指定数据来源表，这两个关键字是`SELECT`语句最少应该包含的。`GROUP BY`用于分组查询；`WHERE`用于筛选条件，它们不是必需的。所以选B。
7. **题目**：数据库是（ ）  
   A. 一些数据的集合  
   B. 以一定的组织结构保存在计算机存储设备中的数据的集合  
   C. 辅助存储器上的一个文件  
   D. 磁盘上的一个数据文件  
   **答案**：C  
   **分析**：数据库是一个结构化的数据集合，它可以包含多种类型的数据和对象。`DBF`文件是一种特定类型的数据库文件格式，但数据库不仅仅是`DBF`文件；关系是数据库中数据的一种组织形式；数据库也不是简单的一组文件。所以选C。
8. **题目**：在 SQL 中，删除表的命令是（ ）  
   A. DELETE TABLE  
   B. DELETE FROM TABLE  
   C. DROP FROM TABLE  
   D. DROP TABLE  
   **答案**：D  
   **分析**：在SQL中，删除表的正确语法是`DROP TABLE 表名`。`DELETE TABLE`和`DELETE FROM TABLE`语法错误；`DROP 表`语法不完整。所以选D。
9. **题目**：在 SQL 中，向数据表中插入一条记录使用（ ）语句。  
   A. CREATE  
   B. INSERT  
   C. SAVE  
   D. UPDATE  
   **答案**：B  
   **分析**：`INSERT`用于向数据表中插入新记录；`CREATE`用于创建数据库对象（如表、视图等）；`SAVE`不是SQL标准语句；`UPDATE`用于更新表中已存在的数据。所以选B。
10. **题目**：子查询是（ ）  
    A. 选取单表中字段子集的查询语句  
    B. 选取多表中字段子集的查询语句  
    C. 返回单表中数据子集的查询语句  
    D. 嵌入到另一个查询语句之中的查询语句  
    **答案**：D  
    **分析**：子查询是嵌入到另一个查询语句之中的查询语句，它可以用于辅助主查询获取更精确的结果。A、B、C选项对其定义不准确。所以选D。
11. **题目**：子模式 DDL 用来描述（ ）  
    A. 数据库的总体逻辑结构  
    B. 数据库的局部逻辑结构  
    C. 数据库的物理存储结构  
    D. 数据库的概念结构  
    **答案**：B  
    **分析**：子模式DDL（数据定义语言）用来描述数据库的局部逻辑结构，它定义了用户能够看到和使用的那部分数据结构。数据库的总体逻辑结构由模式DDL描述；物理存储结构涉及存储设备等底层细节；概念结构是对现实世界的抽象描述。所以选B。
12. **题目**：SQL 语言中，使用最频繁的语句是（ ）  
    A. UPDATE  
    B. DELETE  
    C. SELECT  
    D. INSERT  
    **答案**：C  
    **分析**：`SELECT`语句用于查询数据，是使用最频繁的语句，在数据库操作中，查询数据的需求最为常见。`UPDATE`用于更新数据；`DELETE`用于删除数据；`INSERT`用于插入数据，它们的使用频率相对较低。所以选C。
13. **题目**：在 SQL 中，撤销用户权限的命令是（ ）  
    A. GRANT  
    B. CREATE  
    C. REVOKE  
    D. INSERT  
    **答案**：C  
    **分析**：`GRANT`语句用于将权限授予用户；`CREATE`用于创建数据库对象；`REVOKE`用于撤销用户权限；`INSERT`用于插入数据。所以选C。
14. **题目**：在 SQL 中，删除表的正确命令是（ ）  
    A. DELETE TABLE  
    B. DELETE FROM TABLE  
    C. DROP TABLE  
    D. DROP FROM TABLE  
    **答案**：C  
    **分析**：删除表的正确语法是`DROP TABLE 表名`。`DELETE TABLE`和`DELETE FROM TABLE`语法错误；`DROP FROM TABLE`语法不完整。所以选C。
15. **题目**：在 MySQL 中，更改表名的语句是（ ）  
    A. ALTER TABLE 表名 RENAME 新表名  
    B. ALTER TABLE 表名 MODIFY 新表名  
    C. ALTER TABLE 表名 ALTER 新表名  
    D. ALTER TABLE 表名 CHANGE 新表名  
    **答案**：A  
    **分析**：在MySQL中，`ALTER TABLE 表名 RENAME 新表名`用于更改表名；`MODIFY`用于修改表字段的定义（如数据类型等）；`ALTER`用于更改表字段（如添加列等）；`CHANGE`用于修改列的定义（包括列名和数据类型等）。所以选A。
16. **题目**：`GRANT`和`REVOKE`语句属于（ ）  
    A. 数据定义语言  
    B. 数据操作语言  
    C. 数据控制语言  
    D. 数据库事务  
    **答案**：C  
    **分析**：`GRANT`和`REVOKE`用于权限管理，属于数据控制语言（DCL）。数据定义语言（DDL）包括`CREATE`、`DROP`、`ALTER`等语句；数据操作语言（DML）包括`SELECT`、`INSERT`、`UPDATE`、`DELETE`等语句；数据库事务包括`COMMIT`和`ROLLBACK`等操作。所以选C。
17. **题目**：以下表结构设计中，设计不合理的字段是（ ）

|  |  |  |
| --- | --- | --- |
| 字段名 | 数据类型 | 说明 |
| 部门号 | INT | 部门编号 |
| 部门名 | VARCHAR(20) | 部门名称 |
| 部门经理 | VARCHAR(20) | 部门负责人姓名 |
| 部门成员 | VARCHAR(200) | 部门所有成员姓名，用逗号分隔 |
| A. 部门号 |  |  |
| B. 部门名 |  |  |
| C. 部门经理 |  |  |
| D. 部门成员 |  |  |
| **答案**：D |  |  |
| **分析**：“部门成员”字段存储了多个值，不符合数据库设计的范式，应拆分成关联表来存储。部门号、部门名、部门经理字段设计相对合理。所以选D。 |  |  |
| 18. **题目**：已知商品表（商品id，商品名称，销量），查询销量最大的商品id，正确的 SQL 语句是（ ） |  |  |
| A. SELECT 商品id FROM 商品表 WHERE 销量 = MAX(销量) |  |  |
| B. SELECT 商品id FROM 商品表 GROUP BY 销量 HAVING 销量 = MAX(销量) |  |  |
| C. SELECT 商品id,MAX(销量) FROM 商品表 GROUP BY 商品id |  |  |
| D. SELECT 商品id FROM 商品表 WHERE 销量 = (SELECT MAX(销量) FROM 商品表) |  |  |
| **答案**：D |  |  |
| **分析**：A选项中`MAX(销量)`不能直接在`WHERE`子句中使用；B选项`GROUP BY 销量`会导致结果不符合需求；C选项`SELECT 商品id,MAX(销量)`中`商品id`与`MAX(销量)`不匹配。D选项先通过子查询获取最大销量，再在主查询中筛选出销量等于最大销量的记录，符合要求。所以选D。 |  |  |
| 19. **题目**：关于`HAVING`子句，以下说法正确的是（ ） |  |  |
| A. `HAVING`子句可以包含任意的列名 |  |  |
| B. 不可以同时使用`WHERE`子句和`HAVING`子句 |  |  |
| C. `HAVING`子句的作用是限定分组的条件 |  |  |
| D. 如果`SELECT`语句中没有聚合函数，就不能使用`HAVING`子句 |  |  |
| **答案**：D |  |  |
| **分析**：`HAVING`子句用于对分组后的结果进行筛选，只能用于包含聚合函数的查询中，且只能包含聚合函数作用的字段，不能包含普通标量字段，A错误；使用`HAVING`子句的同时可以使用`WHERE`子句，`WHERE`用于对表中数据进行筛选，`HAVING`用于对分组结果筛选，B错误；`HAVING`子句作用是对分组结果进行筛选，而不是限定分组条件，分组条件用`GROUP BY`，C错误；如果`SELECT`语句中没有聚合函数，就不能使用`HAVING`子句，D正确。所以选D。 |  |  |

### 二、多选题

1. **题目**：已知`emp`表（员工编号，员工姓名，部门编号）和`dept`表（部门编号，部门名称），要查询所有员工姓名和对应部门名称，可使用的连接方式有（ ）  
   A. LEFT JOIN  
   B. RIGHT JOIN  
   C. JOIN emp e,dept d ON e.部门编号 = d.部门编号  
   D. JOIN emp e,dept d WHERE e.部门编号 = d.部门编号  
   **答案**：AB  
   **分析**：`LEFT JOIN`是以左表（`emp`表）为基础，展示左表所有记录及匹配的右表记录；`RIGHT JOIN`是以右表（`dept`表）为基础，展示右表所有记录及匹配的左表记录，这两种方式都能实现查询所有员工姓名和对应部门名称的需求。C、D选项中未使用表别名限定字段所属表，在多表连接查询时，若字段在多个表中存在，会导致SQL语法错误。所以选AB。
2. **题目**：已知`emp`表（员工编号，员工姓名，部门编号，工资），查询部门员工工资平均值大于 2000 的部门编号及部门平均工资，正确的 SQL 语句是（ ）  
   A. SELECT 部门编号,AVG(工资) FROM emp GROUP BY 部门编号 HAVING AVG(工资)>2000  
   B. SELECT 部门编号,AVG(工资) FROM emp HAVING AVG(工资)>2000 GROUP BY 部门编号  
   C. SELECT 部门编号,AVG(工资) FROM emp WHERE AVG(工资)>2000 GROUP BY 部门编号  
   D. SELECT 部门编号,AVG(工资) FROM emp GROUP BY 部门编号 HAVING AVG(工资)>2000  
   **答案**：AD  
   **分析**：查询部门员工工资平均值大于2000的部门编号及部门平均工资，需要先使用`GROUP BY deptno`对部门进行分组，再使用`AVG(sal)`计算平均工资，最后用`HAVING`子句筛选平均工资大于2000的分组。B选项`HAVING`子句位置错误；C选项应使用`HAVING`而不是`WHERE`来筛选分组结果。所以选AD。
3. **题目**：已知`student`表（学生姓名，数学成绩），查询数学成绩最高的学生姓名，正确的 SQL 语句是（ ）  
   A. SELECT 学生姓名 FROM student WHERE 数学成绩 IS (SELECT MAX(数学成绩) FROM student)  
   B. SELECT 学生姓名 FROM student WHERE 数学成绩 = (SELECT 数学成绩 FROM student ORDER BY 数学成绩 DESC LIMIT 1)  
   C. SELECT 学生姓名 FROM student WHERE 数学成绩 = (SELECT MAX(数学成绩) FROM student)  
   D. SELECT 学生姓名 FROM student WHERE 数学成绩 IN (SELECT MAX(数学成绩) FROM student)  
   **答案**：C  
   **分析**：A选项中`IS`仅用于`NULL`判断，不能用于比较值；B选项语法错误；D选项`IN`操作符用于判断某个值是否在指定的集合中，而`SELECT MAX(math) FROM student`返回的是一个单一的最大值，不是集合，所以不能用`IN`。C选项正确，通过子查询获取数学成绩的最大值，再在主查询中筛选出成绩等于该最大值的学生姓名。所以选C。
4. **题目**：已知`goods`表（商品id，商品名称，单价），要按单价升序排序，每页显示 3 条数据，显示第三页的数据，正确的 SQL 语句是（ ）  
   A. SELECT \* FROM goods ORDER BY 单价 DESC LIMIT 6,3  
   B. SELECT \* FROM goods ORDER BY 单价 LIMIT 2,3  
   C. SELECT \* FROM goods ORDER BY 单价 LIMIT 3,3  
   D. SELECT \* FROM goods ORDER BY 单价 ASC LIMIT 6,3  
   **答案**：D  
   **分析**：按单价升序排序用`ORDER BY price asc`，`LIMIT`后面跟两个参数，第一个是偏移量，第二个是返回的行数。每页显示3条数据，显示第三页的数据，偏移量应为6（前两页共6条数据），返回行数为3，所以`LIMIT 6,3`。A选项`ORDER BY price desc`是降序排序；B选项未指定排序方向且偏移量和行数设置错误；C选项未指定排序方向。所以选D。
5. **题目**：关于数据库约束，以下说法正确的是（ ）  
   A. 每个表中可以有多个`UNIQUE`约束  
   B. `UNIQUE`约束和`PRIMARY KEY`约束的值都不能为 null  
   C. `NOT NULL`约束表示字段的值不能为 null  
   D. `DEFAULT`约束可以为字段设置默认值  
   **答案**：ACD  
   **分析**：每个表中可以有多个`UNIQUE`约束，用于确保列值的唯一性，但只能有一个`PRIMARY KEY`约束，A正确；`UNIQUE`约束值可以为空，但只能有一个空值，`PRIMARY KEY`约束值不能为null且不能重复，B错误；`NOT NULL`用于给字段添加非空约束，值不能为null，C正确；`DEFAULT`给字段设置默认值，当字段不赋值时，默认值生效，D正确 。所以选ACD。

### 三、简答题

1. **题目**：简述`delete`，`drop`，`truncate`区别。  
   **答案**：

- `DELETE`：用于删除表中的数据，可以根据条件删除部分数据。它是DML（数据操作语言）语句，逐行删除数据，会产生大量日志记录，执行速度相对较慢。例如`DELETE FROM student WHERE age < 18;`，可以删除`student`表中年龄小于18岁的学生记录。
- `DROP`：用于删除表结构及表中的所有数据，同时释放相关的存储空间。它是DDL（数据定义语言）语句，执行后无法回滚（除非在事务中且未提交事务）。例如`DROP TABLE student;`，会删除整个`student`表。
- `TRUNCATE`：用于删除表中的所有数据，并重置表的自增长列（如果有），使其重新从初始值开始计数。它也是DDL语句，执行速度通常比`DELETE`快，因为它直接释放表空间，产生的日志记录较少。例如`TRUNCATE TABLE student;`，会删除`student`表中的所有数据。

1. **题目**：列举你用过的数据库的数据类型，并说明使用场景。  
   **答案**：

- **整数类型（如**`INT`**）**：适用于存储整数数据，如年龄、数量、ID等。例如存储学生的年龄字段`age INT`，因为年龄通常是整数。
- **字符串类型（如**`VARCHAR`**）**：用于存储可变长度的字符串，如姓名、地址、描述等。例如存储学生姓名`name VARCHAR(20)` ，因为姓名长度不固定且一般不会太长。
- **日期和时间类型（如**`DATE`**、**`DATETIME`**）**：`DATE`用于存储日期，格式为`YYYY - MM - DD`，如订单日期、出生日期等；`DATETIME`用于存储日期和时间，格式为`YYYY - MM - DD HH:MM:SS`，如记录操作发生的具体时间。例如`order_date DATE`存储订单日期，`operation_time DATETIME`存储操作时间。
- **浮点类型（如**`FLOAT`**、**`DOUBLE`**）**：用于存储小数数据，如价格、体重、成绩等。例如商品价格`price DOUBLE`，因为价格可能包含小数部分。
- **文本类型（如**`TEXT`**）**：用于存储较长的文本内容，如文章内容、产品描述等。例如存储一篇新闻文章的内容`content TEXT`。

1. **题目**：作为测试人员，在哪些场景下需要用到数据库？  
   **答案**：

- **数据存储和读取测试**：验证应用程序是否能正确地将数据存储到数据库中，并能准确读取出来。例如测试用户注册功能时，检查用户信息是否正确存入数据库，登录时能否从数据库获取正确的用户信息。
- **数据一致性测试**：确保数据库中的数据在各种操作（如插入、更新、删除）后保持一致性。例如在转账操作中，检查转账前后账户余额的变化是否符合预期，数据是否完整准确。
- **性能测试**：模拟大量数据和并发操作，测试数据库在高负载情况下的性能表现。如测试电商网站在促销活动期间，大量订单数据写入数据库时的响应时间和吞吐量。
- **数据关联测试**：检查不同表之间数据的关联关系是否正确。例如在多表连接查询时，验证查询结果是否符合业务逻辑，确保外键约束等关系正常。
- **安全测试**：测试数据库的权限管理，验证不同用户角色是否只能访问和操作其被授权的数据。如检查普通用户是否无法访问管理员的敏感数据。

### 四、设计题

1. **题目**：有`student`表（id，姓名，性别，出生年份，院系，住址）和`score`表（学号，课程名，分数）。

- 1.1 为`student`表和`score`表增加多行记录。
- 1.2 查询`student`表的第 2 条到 4 条记录。
- 1.3 从`student`表中查询每个院系有多少人。  
  **答案**：
- 1.1

1. **题目**：有部门表`dept`（`DEPTNO`部门编号，`DNAME`部门名称）、雇员表`emp`（`Empno`雇员编号，`Emname`雇员姓名，`Mgr`部门经理，`Hiredate`雇佣日期，`Sal`工资，`Deptno`部门编号）。

- 2.1 找出部门名称为`ACCOUNTING`的部门下的所有员工名称。
- 2.2 找出部门名称为`SALES`的部门的部门经理。
- 2.3 找出部门名称为`RESEARCH`的部门下雇佣日期为 1995 - 12 - 17 到 1997 - 10 - 20 的员工。
- 2.4 找出每个部门下每月需要发出的薪水总额及部门名称。  
  **答案**：
- 2.1

1. **题目**：有学生表（`T_Student`）（`Sid`学号，`Sname`学生姓名）、成绩表（`T_Score`）（`Sid`学号，`Cid`课程编号，`score`成绩）、课程表（`T_Course`）（`Cid`课程编号，`Cname`课程名称）。

- 3.1 查询各个科目的平均成绩。
- 3.2 查询学生的信息及课程分数（要求显示学生信息即科目名称及对应的成绩，使用连接查询实现）。
- 3.3 检索“01”课程分数小于 60，按分数降序排列的学生信息。  
  **答案**：
- 3.1
