"""第 1 章实验：类型、运算符与输出格式化。"""

from __future__ import annotations


def to_int(text: str) -> int:
    """把用户输入转成整数。

    int('3.5') 会抛 ValueError，所以先尝试 float 再截断，
    这样 '3.5' 和 '3' 都能被接受。
    """
    try:
        return int(text)
    except ValueError:
        return int(float(text))


def format_duration(seconds: int) -> str:
    """把秒数格式化成 1h02m03s；不足一小时省略小时。"""
    if seconds < 0:
        raise ValueError("秒数不能为负")
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    return f"{minutes}m{secs:02d}s"


def same_object(a: object, b: object) -> bool:
    """演示 is / == 的分工：这里只回答「是不是同一个对象」。"""
    return a is b


def summary(name: str, age: int) -> str:
    """一行 f-string 拼出摘要。"""
    return f"姓名: {name} | 年龄: {age}"


def precedence_demo() -> list[int]:
    """同一表达式加括号与不加括号的对比。"""
    return [2 + 3 * 4, (2 + 3) * 4]


if __name__ == "__main__":
    print("to_int('3.5') =", to_int("3.5"))
    print("format_duration(3723) =", format_duration(3723))
    print("format_duration(83) =", format_duration(83))
    print(summary("李明", 18))
    print("2+3*4 / (2+3)*4 =", precedence_demo())

    a = [1, 2, 3]
    b = a
    c = [1, 2, 3]
    print("a is b:", same_object(a, b), "| a == c:", a == c, "| a is c:", same_object(a, c))
    print("bool('False') =", bool("False"), "| bool('') =", bool(""))
