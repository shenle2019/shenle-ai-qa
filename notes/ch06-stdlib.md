# 第 6 章 · 标准库、文件、JSON 与异常

> 本章目标：能读写文件、处理 JSON 与 CSV、生成不重复的文件名，并用「异常 + 日志 + 测试」把失败管住。

## 1. 模块与导入

```python
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
```

- 一个 `.py` 文件就是一个模块，一个带 `__init__.py` 的目录就是包；
- `if __name__ == "__main__":` 里的代码只在「直接运行」时执行，被 import 时不执行；
- 标准库优先：路径用 `pathlib`，JSON 用 `json`，时间用 `datetime`，别自己造轮子。

## 2. 路径：pathlib 优于字符串拼接

```python
from pathlib import Path

root = Path(__file__).resolve().parent          # 当前文件所在目录
data_dir = root / "data"                        # 用 / 拼路径，跨平台
data_dir.mkdir(parents=True, exist_ok=True)     # 已存在也不报错

for p in data_dir.glob("*.json"):               # 只找一层
    print(p.name, p.suffix, p.stat().st_size)

for p in root.rglob("*.py"):                    # 递归
    print(p.relative_to(root))
```

常用：`.name` / `.stem` / `.suffix` / `.parent` / `.exists()` / `.is_file()` / `.read_text()` / `.write_text()`。

## 3. 文件读写

```python
path = Path("notes.txt")

path.write_text("第一行\n第二行\n", encoding="utf-8")     # 一次写
text = path.read_text(encoding="utf-8")                    # 一次读

with path.open("a", encoding="utf-8") as f:                # 追加
    f.write("第三行\n")

with path.open("r", encoding="utf-8") as f:
    for line in f:                                          # 逐行读，省内存
        print(line.rstrip())
```

要点：

- **永远显式写 `encoding="utf-8"`**，Windows 默认是 gbk，中文会炸；
- 用 `with`，离开代码块自动关闭文件（异常也会关）；
- 大文件不要 `read()` 全读进来，逐行迭代；
- 二进制用 `"rb"` / `"wb"`，拿到的是 `bytes`。

## 4. JSON

```python
import json

data = {"id": 1, "tags": ["a", "b"], "ok": True}

text = json.dumps(data, ensure_ascii=False, indent=2)   # Python -> 字符串
back = json.loads(text)                                  # 字符串 -> Python

Path("x.json").write_text(text, encoding="utf-8")
loaded = json.loads(Path("x.json").read_text(encoding="utf-8"))
```

- `ensure_ascii=False` 才能输出中文而不是 `\u4e2d`；
- 只支持基本类型：dict / list / str / int / float / bool / None；
- 遇到 `datetime`、`Decimal`、自定义对象要传 `default=`：`json.dumps(obj, default=str)`；
- `json.load(f)` / `json.dump(obj, f)` 是文件版。

## 5. CSV

```python
import csv

with open("rows.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name"])
    writer.writeheader()
    writer.writerows([{"id": 1, "name": "a"}])

with open("rows.csv", newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        print(row["id"], row["name"])
```

`utf-8-sig` 让 Excel 打开不乱码；`newline=""` 防止 Windows 写出多余空行。

## 6. 时间、随机与唯一文件名

```python
from datetime import datetime, timedelta
import uuid, random, hashlib

now = datetime.now()
stamp = now.strftime("%Y%m%d-%H%M%S")
later = now + timedelta(days=7)

unique = uuid.uuid4().hex[:8]
digest = hashlib.md5(b"abc").hexdigest()

def unique_name(directory: Path, stem: str = "report", suffix: str = ".json") -> Path:
    """时间戳 + 短 uuid；若已存在就再抽一次。"""
    while True:
        candidate = directory / f"{stem}-{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}{suffix}"
        if not candidate.exists():
            return candidate
```

要点：时间戳会撞（同一秒），uuid 才真正唯一；`random` 是伪随机，不要用于安全场景。

## 7. 异常

```python
try:
    value = int("abc")
except ValueError as exc:
    print("转换失败:", exc)
else:
    print("没出错才走这里")
finally:
    print("无论如何都走这里")
```

- 只捕获**你预期**的异常类型，别裸 `except:`；
- `raise` 重新抛出当前异常，`raise X from exc` 保留因果链；
- 自定义异常继承 `Exception`，带上下文信息：

```python
class ConfigError(Exception):
    def __init__(self, path: Path, reason: str):
        super().__init__(f"{path} 配置有问题：{reason}")
        self.path = path
        self.reason = reason
```

`EAFP`（先做再兜）在 Python 里比 `LBYL`（先检查再做）更常见，但**检查一次就能避免的**（如 `path.exists()`）还是先检查。

## 8. 日志

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)
log.info("开始处理 %s", path)
```

用 `%s` 占位而不是 f-string：级别不够时不会白算字符串。

## 9. 单元测试

```python
import pytest

def test_add():
    assert 1 + 1 == 2

@pytest.mark.parametrize("raw,expected", [("1", 1), (" 2 ", 2)])
def test_to_int(raw, expected):
    assert int(raw) == expected

with pytest.raises(ValueError):
    int("x")
```

- 一个测试只测一件事，名字写清「什么条件下发生什么」；
- 用 `tmp_path` fixture 造临时目录，别往真实目录写；
- 断言失败信息要能定位问题。

## 10. 本章实验

`labs/ch06-stdlib/`：

```powershell
python labs/ch06-stdlib/stdlib_demo.py
python -m pytest labs/ch06-stdlib -q
```

包含：UTF-8 文件读写与逐行统计、JSON 往返（含中文与 `default=str`）、CSV 读写、唯一文件名生成、自定义异常与 `from` 链、`tmp_path` 下的完整文件用例。

## 11. 自测

1. `open(..., encoding="utf-8")` 不写会怎样？
2. `json.dumps` 输出 `\u4e2d` 是缺了哪个参数？
3. `except Exception` 为什么不该滥用？
4. 同一秒生成两个文件名，只用时间戳会出什么问题？
