# 第 3 章 · 列表、元组、字典与推导式

> 本章目标：掌握四种常用容器，知道什么场景该用哪种，并能用推导式把「遍历 + 过滤 + 转换」写成一行。

## 1. 列表：有序、可变

```python
nums = [3, 1, 4, 1, 5]
nums.append(9)          # 尾部追加
nums.insert(1, 7)       # 指定位置插入
nums.remove(1)          # 删掉第一个值为 1 的元素
last = nums.pop()       # 弹出尾部（也可 pop(0)）
nums.sort()             # 原地排序
sorted_copy = sorted(nums, reverse=True)   # 返回新列表
```

常用操作：

| 操作 | 写法 | 复杂度 |
| --- | --- | --- |
| 取长度 | `len(nums)` | O(1) |
| 索引 | `nums[0]`、`nums[-1]` | O(1) |
| 切片 | `nums[1:3]`、`nums[::-1]` | O(k) |
| 查找值 | `nums.index(4)` | O(n) |
| 判断存在 | `4 in nums` | O(n) |

切片是**浅拷贝**：`nums[:]` 得到新列表，但里面的可变元素还是共享的。

## 2. 遍历的四种写法

```python
for x in nums:                 # 只要值
for i, x in enumerate(nums):   # 同时要下标
for x in reversed(nums):       # 反向
for a, b in zip(xs, ys):       # 并行遍历两个列表
```

`zip` 以最短的为准；需要等长补齐用 `itertools.zip_longest`。

## 3. 列表推导式

```python
squares = [x * x for x in range(10)]              # 映射
evens = [x for x in range(10) if x % 2 == 0]      # 过滤
pairs = [(a, b) for a in "ab" for b in [1, 2]]    # 双层
```

等价于「建空列表 + for + if + append」，但更快也更短。超过两层嵌套或条件太复杂就不该硬写推导式，可读性优先。

## 4. 元组：有序、不可变

```python
point = (3, 4)
x, y = point              # 解包
single = (5,)             # 单元素必须带逗号
```

不可变带来两个好处：可以作为字典的键、可以安全地当「只读记录」传参。`namedtuple` / `dataclass(frozen=True)` 是可读性更好的替代。

## 5. 字典：键值映射

```python
user = {"name": "李明", "age": 18}
user["age"] = 19                  # 改
user["city"] = "杭州"             # 增
del user["city"]                  # 删
age = user.get("age", 0)          # 取，缺省给默认值（不会 KeyError）
```

遍历：

```python
for k in user: ...                    # 键
for k, v in user.items(): ...         # 键值
for v in user.values(): ...           # 值
```

**坑**：`user["not_exist"]` 抛 `KeyError`；`user.get("not_exist")` 返回 `None`。计数场景用 `collections.Counter` 或 `dict.setdefault`。

## 6. 字典推导式

```python
squares = {x: x * x for x in range(5)}
index = {name: i for i, name in enumerate(["a", "b"])}
# 反转：值 -> 键（值必须唯一，否则后者覆盖前者）
flipped = {v: k for k, v in index.items()}
```

## 7. 嵌套结构：真实数据长什么样

接口返回、JSON、配置，基本都是「字典套列表套字典」：

```python
orders = [
    {"id": 1, "items": [{"sku": "A", "qty": 2}], "status": "paid"},
    {"id": 2, "items": [], "status": "cancelled"},
]

paid_ids = [o["id"] for o in orders if o["status"] == "paid"]
total_qty = sum(item["qty"] for o in orders for item in o["items"])
```

读这种数据的心法：**先确定外层是什么（列表还是字典），再一层层往里取**，取值一律用 `.get()` 兜底。

## 8. 该用哪个

| 容器 | 有序 | 可变 | 能当键 | 典型场景 |
| --- | --- | --- | --- | --- |
| `list` | 是 | 是 | 否 | 有序集合、队列、结果集 |
| `tuple` | 是 | 否 | 是 | 固定结构、多返回值 |
| `dict` | 是（3.7+） | 是 | 否 | 带名字的字段、索引、计数 |
| `set` | 否 | 是 | 否 | 去重、集合运算 |

## 9. 本章实操

`labs/ch03-collections/`：

```powershell
python labs/ch03-collections/collections_demo.py
python -m pytest labs/ch03-collections -q
```

包含：列表去重保序、`Counter` 词频、字典反转、嵌套订单聚合、切片浅拷贝的验证。

## 10. 自测

1. `nums[:]` 和 `nums` 是同一个对象吗？
2. `(5)` 和 `(5,)` 有什么区别？
3. `dict.get(k)` 与 `dict[k]` 在键不存在时分别怎样？
4. 用一行推导式取出下面数据里所有已支付订单的商品名：
   `[{"status":"paid","items":[{"name":"A"}]}, {"status":"new","items":[{"name":"B"}]}]`

## 附：自测答案

1. 不是同一个对象（`nums[:]` 是新列表），但里面装的是同一批元素引用——浅拷贝。元素是可变对象时，改元素两边都变。
2. `(5)` 只是加了括号的整数 5，类型是 `int`；`(5,)` 才是单元素元组。定义元组靠逗号，不靠括号。
3. `d[k]` 键不存在抛 `KeyError`；`d.get(k)` 返回 `None`（可给默认值 `d.get(k, 0)`）。要「必须存在」用 `d[k]`，要「可缺省」用 `get`。
4. `[item["name"] for order in orders if order["status"] == "paid" for item in order["items"]]`。

## 学生常问

**Q：列表推导式和 `for` 循环该选哪个？**

A：只是为了生成一个新列表就用推导式，一行能看懂；循环体里有 `print`、`try`、多个分支、或者要改外部状态，就用普通循环。

**Q：字典能排序吗？**

A：字典本身按插入顺序遍历，不能「排序」。要按值看排行，就 `sorted(d.items(), key=lambda kv: kv[1], reverse=True)`，结果是一个列表。

**Q：`set` 能去重，为什么不能直接当接口返回？**

A：`set` 无序且不能 JSON 序列化。要返回就转 `list`，但转换后顺序不保证，需要稳定顺序就 `sorted(set(...))`。

## 面试题

**Q：列表、元组、集合、字典的底层差别，各自适合什么场景？**

A：列表是动态数组，按下标访问快、中间插入慢；元组是不可变序列，可作为字典键、可哈希；集合是哈希表，去重和成员判断 O(1)；字典是哈希表存键值对，按 key 查 O(1)。选型看访问方式：按位置用列表/元组，按 key 用字典，去重和集合运算用 set。

**Q：`dict` 的 key 为什么必须可哈希？**

A：哈希表靠 key 的哈希值定位槽位，key 一旦可变、哈希值就会变，之前存的位置再也找不到。所以 `list`、`dict`、`set` 不能当 key，`tuple` 里只要含可变元素也不能。

**Q：`copy.copy` 和 `copy.deepcopy` 的区别？**

A：浅拷贝只复制最外层容器，内层还是共享引用；深拷贝递归复制所有层级。接口测试里造数据，嵌套结构一律深拷贝，否则用例之间会互相污染。

## 延伸知识

- 推导式可以带条件：`[x for x in xs if x > 0]`；也能嵌套，但超过两层就该拆函数。
- `dict` 合并：Python 3.9+ 用 `a | b`，3.8 及以前用 `{**a, **b}`。
- `collections` 里三个常用件：`defaultdict`（免去 get 默认值）、`Counter`（计数）、`deque`（两端进出）。
- 切片是浅拷贝，`[::-1]` 反转、`[::2]` 隔一个取一个；切片越界不会报错，这点和下标不同。
