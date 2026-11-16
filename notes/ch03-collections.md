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

## 9. 本章实验

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
