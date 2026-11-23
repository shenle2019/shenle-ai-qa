## 示例

### 创建文件：数据处理/parse_json_response.py

```python
# AIQE_DYNAMIC_FUNCTION_META {"function_code": "parse_json_response", "function_type": "数据处理", "function_name": "JSON响应解析", "description": "解析JSON格式的API响应，提取指定字段", "enabled": true, "params": [{"key": "json_str", "name": "JSON字符串", "value_type": "string", "required": true, "default_value": "", "description": "待解析的JSON字符串", "test_value": "{\"code\": 200, \"data\": {\"name\": \"test\"}}"}, {"key": "field_path", "name": "字段路径", "value_type": "string", "required": false, "default_value": "data", "description": "要提取的字段路径，支持点号分隔", "test_value": "data.name"}], "outputs": [{"key": "extracted_value", "name": "提取值", "value_type": "string", "description": "从JSON中提取的值"}, {"key": "parse_success", "name": "解析状态", "value_type": "boolean", "description": "是否解析成功"}]}

def execute(**kwargs):
    """解析JSON响应，提取指定字段。"""
    import json

    # 业务逻辑用 try/except/finally 整体包裹
    try:
        # --- 参数校验（失败直接 raise，不设置默认值） ---
        json_str = kwargs.get("json_str", "")
        if not json_str:
            raise ValueError("json_str 不能为空")

        field_path = kwargs.get("field_path", "data")
        if not field_path:
            raise ValueError("field_path 不能为空")

        # --- 业务执行 ---
        data = json.loads(json_str)
        if not isinstance(data, dict):
            raise TypeError(f"JSON 顶层必须是对象，实际为 {type(data).__name__}")

        value = data
        for key in field_path.split("."):
            if not isinstance(value, dict):
                raise TypeError(f"无法在 {type(value).__name__} 类型上访问字段 '{key}'")
            if key not in value:
                raise KeyError(f"字段路径 '{field_path}' 在 JSON 中不存在")
            value = value[key]

        return {"extracted_value": str(value), "parse_success": True}
    except Exception:
        # 出现异常不要设置默认值（如 {"extracted_value": "", "parse_success": False}），
        # 直接把异常信息抛给调用方
        raise
    finally:
        # 资源清理（无外部资源时留空即可，但结构保留）
        pass


# === CLI 入口(必加,直接复用上文「推荐模板」里的固定代码) ===
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
            raise ValueError(f"不支持的位置参数 {_arg!r},请使用 --key value 形式")
        _key = _arg[2:]
        if not _key:
            raise ValueError(f"参数名不能为空:{_arg!r}")
        if _i + 1 < len(_extras) and not _extras[_i + 1].startswith("--"):
            _kwargs[_key] = _extras[_i + 1]
            _i += 2
        else:
            _kwargs[_key] = ""
            _i += 1

    try:
        _result = execute(**_kwargs)
        print(json.dumps(_result, ensure_ascii=False))
    except SystemExit:
        raise
    except Exception as _e:
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({"error": str(_e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
```
