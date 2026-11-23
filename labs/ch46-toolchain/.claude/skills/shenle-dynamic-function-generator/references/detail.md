## 代码体规范

- 必须包含 `execute(**kwargs)` 函数作为入口
- `kwargs` 接收流程传入的所有参数
- 返回值应为 `dict`，包含 `outputs` 中定义的输出键
- 所有用到的模块（标准库 + 第三方库）都必须在函数体内**显式 import**，不得依赖外部已导入的命名空间（详见下方「包引入管理」）

### 包引入管理

动态函数运行在隔离的 Python 沙箱中，**函数体外没有任何自动注入的包**。所有用到的模块都必须显式 import，不能假设 `import xxx` 已经被别处执行，也不能依赖模块顶层已存在的变量。

#### 规范

1. **import 集中放在 `execute` 函数体顶部**：在函数最前面一次性引入全部依赖，不要散落在中间；**不要写到文件顶层**（`def execute` 之外），避免污染模块命名空间。
2. **每个用到的模块都要 import**：包括标准库（`json` / `re` / `os` / `sys` / `time` / `hashlib` / `base64` / `datetime` / `urllib.parse` 等）。例如代码里出现 `sys.argv`，就一定要 `import sys`；出现 `time.sleep` 就一定要 `import time`。
3. **第三方库用 `try/except ImportError` 保护**：运行环境未必预装了 `pymysql` / `requests` / `pandas` 等，捕获后给出合理的回退返回。
4. **禁止隐式依赖**：不要写 `from somewhere import something` 然后假设该包已在某处被加载过；不允许出现"动态函数 a 里 import 过了，所以动态函数 b 里不用再 import"这种隐式约定。
5. **import 顺序**：先标准库 → 再第三方库 → 再本地模块，每组之间空一行（可选但推荐）。

### 异常处理规范（重要）

动态函数的业务逻辑必须用 **`try / except / finally`** 整体包裹，且遵循以下原则：

1. **不要设置默认值**：当业务逻辑出现异常时，禁止返回 `""`、`0`、`None`、`False`、`{}`、`[]` 之类的占位默认值来"假装执行成功"。默认值会掩盖真实错误，导致上层流程拿到错误结果还继续往下走。
2. **必须抛出异常信息**：捕获到异常后应使用 `raise` 重新抛出（或抛出更具体的异常类型），让调用方清楚地知道"哪里、为什么失败"。
3. **`finally` 用于资源清理**：连接、文件句柄、临时对象等无论成功还是异常都要释放，统一放在 `finally` 中。
4. **ImportError 也属于异常**：第三方库缺失时同样要 `raise` 抛出，不要 `return {"error": ...}` 后继续往下走。
5. **校验失败也走异常**：参数缺失、类型不对、业务规则不满足等场景，使用 `raise ValueError(...)` / `raise TypeError(...)` 等显式抛出。

#### 推荐模板

```python
def execute(**kwargs):
    """函数说明"""
    # 标准库
    import json
    import sys
    import re
    import time
    import hashlib
    import traceback
    from datetime import datetime

    # 第三方库（必须 try/except ImportError 保护）
    try:
        import pymysql
    except ImportError as e:
        raise ImportError(f"pymysql 未安装，请先 pip install pymysql: {e}") from e

    try:
        import requests
    except ImportError as e:
        raise ImportError(f"requests 未安装，请先 pip install requests: {e}") from e

    # 业务逻辑（try/except/finally 整体结构）
    conn = None
    try:
        # --- 参数校验（失败就 raise） ---
        if not kwargs.get("required_param"):
            raise ValueError("required_param 不能为空")

        # --- 业务执行 ---
        conn = pymysql.connect(...)
        result = do_something(conn)
        return {"result": result}
    except Exception:
        # 出现异常不要设置默认值，直接把异常信息抛给调用方
        raise
    finally:
        # 无论成功还是异常，都要释放资源
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


# === CLI 入口（必加，不能省）===========================================
# runner 的 `run_dynamic_function` 工具会用参数数组启动当前 Python 解释器,
# 并把 UTF-8 JSON 通过 stdin 传给 `<脚本路径> --_context-stdin`,
# 所以每个动态函数文件**必须**自带 `if __name__ == "__main__":` 块,
# 否则 `python` 跑这个文件不会有任何输出(只 import 了 execute 然后退出)。
# 下面这段是固定模板,直接复制到文件末尾即可,不要修改。
#
# **为什么用 `--_context-stdin` 而不是 `--_context "<json>"`?**
# stdin 能原样传输 JSON 字节,同时规避 shell 引号和系统默认编码差异。
if __name__ == "__main__":
    import argparse
    import json
    import sys
    import traceback

    parser = argparse.ArgumentParser(description="AIQE 动态函数执行入口")
    parser.add_argument(
        "--_context",
        default="",
        help="运行时上下文 JSON 字符串(命令行直接传,简单场景用)",
    )
    parser.add_argument(
        "--_context-stdin",
        action="store_true",
        help="从 stdin 读取运行时上下文 JSON(推荐,避免 shell 引号嵌套问题)",
    )
    # parse_known_args:除已注册选项外,允许透传任意 --key value 给 execute(**kwargs)
    _parsed, _extras = parser.parse_known_args()

    if _parsed._context_stdin:
        try:
            _context_str = sys.stdin.read()
        except Exception as _e:
            raise RuntimeError(f"从 stdin 读取 _context 失败:{_e}") from _e
    else:
        _context_str = _parsed._context

    _kwargs: dict = {"_context": _context_str}
    _i = 0
    while _i < len(_extras):
        _arg = _extras[_i]
        if not _arg.startswith("--"):
            raise ValueError(
                f"不支持的位置参数 {_arg!r},请使用 --key value 形式"
            )
        _key = _arg[2:]
        if not _key:
            raise ValueError(f"参数名不能为空:{_arg!r}")
        if _i + 1 < len(_extras) and not _extras[_i + 1].startswith("--"):
            _kwargs[_key] = _extras[_i + 1]
            _i += 2
        else:
            # 布尔型标记:只传 --flag,不接 value
            _kwargs[_key] = ""
            _i += 1

    try:
        _result = execute(**_kwargs)
        print(json.dumps(_result, ensure_ascii=False))
    except SystemExit:
        raise
    except Exception as _e:
        # 诊断信息走 stderr,stdout 仍保持干净,调用方用 returncode 区分成功/失败
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"error": str(_e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
# === CLI 入口结束 =====================================================
```

> **为什么必须有 `__main__` 块？** `run_dynamic_function` 会直接启动这个 .py 文件,通过 stdin 注入上下文,再从 stdout 解析 JSON。如果文件里只有 `def execute(**kwargs)`,`python` 解释器执行完文件不会产生结果。`__main__` 块负责把 stdin JSON 喂给 `execute`,并把返回 dict JSON 化后输出。

#### 异常处理反例（不要这样写）

```python
# ❌ 反例 1：异常被吞掉，返回默认值
try:
    data = json.loads(json_str)
except json.JSONDecodeError:
    data = {}        # 错误！默认值掩盖了解析失败
    return {"data": data}

# ❌ 反例 2：捕获后只 return error 字段，继续走成功分支
try:
    result = api.call()
except Exception as e:
    return {"error": str(e)}   # 错误！调用方可能只读 result 字段

# ❌ 反例 3：缺包也不抛，只置 None 继续运行
try:
    import pandas
except ImportError:
    pandas = None    # 错误！后面用到 pandas 时会报 NoneType 错误，信息更模糊
```

#### AI 生成完函数后的自检清单

**写完代码必须逐项核对，否则不予提交：**

- [ ] 函数体内实际用到的每一个模块（包括 `sys` / `os` / `re` / `time` / `hashlib` / `base64` / `datetime` / `urllib` 等标准库）都写了对应 `import`？
- [ ] 第三方库（`pymysql` / `requests` / `pandas` / `openpyxl` 等）都包了 `try/except ImportError`，且**直接 `raise` 抛出**，没有 `return {"error": ...}` 或置 `None` 后继续？
- [ ] 所有 import 都集中在 `execute` 函数体顶部，**没有**写到 `def execute` 之外？
- [ ] 没有出现"假设别处已经 import 过"的隐式依赖？
- [ ] 没有任何用到的名字（变量/函数/常量）找不到 import 来源？
- [ ] 业务逻辑是否被 `try / except / finally` 整体包裹？
- [ ] `except` 中是否使用 `raise` 把异常信息抛出，**没有**用 `return {}` / `return ""` / `return False` 等默认值代替？
- [ ] 资源（连接、文件、临时文件等）是否在 `finally` 中释放？
- [ ] **文件末尾是否包含 `if __name__ == "__main__":` CLI 入口块**（否则 agent `python` 调用无输出,task 直接 FAIL）？

### 运行时上下文信息

函数代码中获取运行时上下文信息的方式为 `kwargs.get("_context", "")`，这是一个 JSON 字符串，解析后得到 `context` 字典，包含当前流程执行的上下文信息（如租户、用户、流程参数、节点输出等）。

**基础示例：**

```python
def execute(**kwargs):
    """使用运行时上下文信息的示例函数"""
    import json

    try:
        _context_str = kwargs.get("_context", "")
        if not _context_str:
            raise ValueError("_context 缺失，无法获取运行时上下文")

        context = json.loads(_context_str)
        if not isinstance(context, dict):
            raise TypeError(f"_context 解析后必须是 dict，实际为 {type(context).__name__}")

        user_id = context.get("user_id", "")
        tenant_id = context.get("tenant_id", "")
        flow_params = context.get("flow_params", {})

        if not user_id:
            raise ValueError("context 中缺少 user_id")

        # 使用上下文信息进行操作
        ...
    except Exception:
        # 直接把异常信息抛出，不要设置默认值
        raise
    finally:
        pass
```

> 注意：`kwargs` 中的 `_context` 是函数运行时的上下文信息，不是操作系统的环境变量。

### 环境变量读取方式

`AI-环境变量/<name>/env_var.yaml` 中定义的每个变量，在运行时会被**平铺注入到 `context` 顶层**（不是嵌套在 `env_vars` 子对象里），与 yaml 键一一对应。例如 yaml 中有：

```yaml
DB_HOST: localhost
DB_NAME: novel_plus
api_project_url: http://novel.hctestedu.com
```

则 `context["DB_HOST"] == "localhost"`，`context["DB_NAME"] == "novel_plus"`，`context["api_project_url"] == "http://novel.hctestedu.com"`，**直接用 `context.get("DB_HOST", "localhost")` 即可**，不要再额外做嵌套查找。

**读取环境变量示例：**

```python
def execute(**kwargs):
    """读取环境变量中的数据库配置，查询用户信息"""
    import json

    conn = None
    try:
        _context_str = kwargs.get("_context", "")
        if not _context_str:
            raise ValueError("_context 缺失，无法获取环境变量")

        context = json.loads(_context_str)

        # 缺少必填环境变量时直接 raise，不要用默认值掩盖
        db_host = context.get("DB_HOST")
        if not db_host:
            raise ValueError("环境变量 DB_HOST 未配置")

        db_name = context.get("DB_NAME")
        if not db_name:
            raise ValueError("环境变量 DB_NAME 未配置")

        db_user = context.get("DB_USER")
        if not db_user:
            raise ValueError("环境变量 DB_USER 未配置")

        # 可选变量有合理兜底，没有也不致命
        db_port_str = context.get("DB_PORT", "3306")
        try:
            db_port = int(db_port_str)
        except (TypeError, ValueError):
            raise ValueError(f"环境变量 DB_PORT 必须是整数，实际为 {db_port_str!r}") from None

        db_password = context.get("DB_PASSWORD", "")

        # 接下来用 db_host / db_port / db_name / db_user / db_password 连接数据库即可
        ...
    except Exception:
        # 直接把异常信息抛出，不设置默认值
        raise
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
```

> 写代码前可以先读 `AI-环境变量/<name>/env_var.yaml` 了解有哪些变量可用，但取值时**必须直接 `context.get(...)`，不要走任何嵌套结构**。
