# 实验

每个实验都是一个能直接运行的 `.py`，配一份 pytest。不依赖第三方库，克隆下来就能跑。

> 想不装环境先看效果？打开 [在线运行 playground](/labs/playground)，代码直接在浏览器里跑。

## 七个实验

| 章 | 实验目录 | 源文件 | 覆盖的知识点 | 测试 |
| --- | --- | --- | --- | --- |
| 01 | `labs/ch01-basics` | `basics.py` | 类型转换、`is` vs `==`、f-string、运算符优先级 | 10 |
| 02 | `labs/ch02-control-flow` | `flow.py` | 条件边界、循环、`for...else`、双层跳出、retry | 10 |
| 03 | `labs/ch03-collections` | `collections_demo.py` | 去重保序、词频、字典反转、嵌套聚合、切片浅拷贝 | 12 |
| 04 | `labs/ch04-functions` | `functions_demo.py` | 可变默认参数、`*args/**kwargs`、闭包、递归、深浅拷贝 | 13 |
| 05 | `labs/ch05-oop` | `oop_demo.py` | 类/实例属性、三种方法、`@property`、魔术方法、装饰器 | 12 |
| 06 | `labs/ch06-stdlib` | `stdlib_demo.py` | UTF-8 读写、JSON、CSV、唯一文件名、异常链 | 14 |
| 07 | `labs/ch07-testkit` | `testkit/`（3 个模块） | 校验器、数据生成（可复现 seed）、落盘夹具 | 20 |

合计 **91 条测试**。

## 怎么跑

```powershell
# 全部
.venv\Scripts\python.exe -m pytest labs -q

# 单章
.venv\Scripts\python.exe -m pytest labs\ch05-oop -q

# 单章直接看输出
.venv\Scripts\python.exe labs\ch05-oop\oop_demo.py
```

## 每个实验长什么样

以第 5 章为例，`oop_demo.py` 里是「一个知识点一个小函数 + 一段 `__main__` 演示」：

```python
class Counter:
    total = 0                 # 类属性：所有实例共享

    def __init__(self, name="c"):
        self.name = name
        self.count = 0        # 实例属性：每个实例独立
        Counter.total += 1
```

`test_oop_demo.py` 里每个行为一条断言，失败信息能直接定位到「哪个知识点没掌握」。

## 约定

- 一个 lab 只依赖标准库；需要密钥的实验从环境变量读，缺省走 mock。
- 输出目录（`_out/`、`data/`）不入库。
- 每个 `def` 都能单独被测试调用，不在模块顶层做副作用。
