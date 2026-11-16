export const basics = `name = "李明"
scores = [85, 92, 78]
total = sum(scores)
print(f"{name} 的总分 {total}，平均 {total / len(scores):.1f}")
`

export const collections = `orders = [
    {"id": 1, "status": "paid", "qty": 2},
    {"id": 2, "status": "new", "qty": 5},
    {"id": 3, "status": "paid", "qty": 3},
]

paid = [o["id"] for o in orders if o["status"] == "paid"]
print("已支付订单:", paid)
print("已支付件数:", sum(o["qty"] for o in orders if o["status"] == "paid"))
`

export const decorator = `import time

def timing(fn):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} 用了 {time.perf_counter() - start:.4f}s")
    return wrapper

@timing
def slow_sum(n):
    return sum(range(n))

print("结果:", slow_sum(1_000_000))
`

export const exception = `def parse_int(raw):
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{raw!r} 不是整数") from exc

for value in ["42", "3.14"]:
    try:
        print(value, "->", parse_int(value))
    except ValueError as err:
        print("失败:", err, "| 原因:", repr(err.__cause__))
`
