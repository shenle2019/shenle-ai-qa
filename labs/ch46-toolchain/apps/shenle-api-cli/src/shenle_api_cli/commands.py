"""send / extract / assert / call 四个子命令实现。

统一输出格式：
  [OK] send status=200 elapsed=234ms result_file=<path>
  [OK] extract name=<字段名> value=<值>
  [OK] assert passed=true reason=<一句话原因>
  [OK] call status=200 elapsed=234ms name=<字段名> value=<值>   ← 0.2 新增
失败一律 [FAIL] <cmd>: <msg>（cli.main 统一处理 CliError）。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .ai import (
    AIConfigError,
    PROMPT_ASSERT_NL,
    PROMPT_EXTRACT_NL,
    ask_text,
    load_config,
)
from .errors import (
    AssertFailed,
    CliError,
    RequestFileInvalid,
    RequestFileNotFound,
    ResultFileInvalid,
    ResultFileNotFound,
)
from .http_client import send_request
from .jsonpath import eval_path, is_jsonpath
from .request_builder import build_requests_args
from .result_store import default_result_dir, load_result, make_result_path, save_result


# ---------------------------------------------------------------------------
# 工具函数


def _read_request_input(args: argparse.Namespace) -> dict[str, Any]:
    """从 args 读取请求 dict（文件路径或 stdin）。

    优先级：
      1. --input <path> 显式指定（传 "-" 也走 stdin）
      2. <path> 位置参数（传 "-" 也走 stdin）
      3. stdin（当无位置参数且 stdin 非 TTY 时）

    Raises:
        RequestFileNotFound / RequestFileInvalid
    """
    # 优先用 --input
    path_str = getattr(args, "input", None)
    if path_str and path_str != "-":
        return _read_request_from_path(Path(path_str))

    # 位置参数
    req_path = getattr(args, "req_path", None)
    if req_path and req_path != "-":
        return _read_request_from_path(Path(req_path))

    # stdin（--input - / <path> - / 无参数但 stdin 非 TTY 都走这里）
    if not sys.stdin.isatty():
        try:
            raw = sys.stdin.read()
        except OSError as e:
            raise RequestFileInvalid(f"读 stdin 失败：{e}") from e
        return _parse_request_json(raw)

    raise RequestFileInvalid(
        "没指定请求文件：传 <req.json> 位置参数、--input <path>、或 stdin"
    )


def _read_request_from_path(path: Path) -> dict[str, Any]:
    """读 request.json 文件并解析。"""
    if not path.exists():
        raise RequestFileNotFound(str(path))
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        raise RequestFileInvalid(f"读文件失败：{e}") from e
    return _parse_request_json(raw)


def _parse_request_json(raw: str) -> dict[str, Any]:
    """把 JSON 字符串解析成 request dict。"""
    if not raw or not raw.strip():
        raise RequestFileInvalid("请求内容为空")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RequestFileInvalid(f"JSON 解析失败：{e}") from e
    if not isinstance(data, dict):
        raise RequestFileInvalid("请求 JSON 顶层必须是 dict")
    return data


def _truncate_value(value: Any, max_len: int = 200) -> str:
    """把任意值截断成短字符串（避免 stdout 单行过长）。"""
    if value is None:
        return "null"
    if isinstance(value, (dict, list)):
        s = json.dumps(value, ensure_ascii=False)
    else:
        s = str(value)
    if len(s) > max_len:
        return s[:max_len] + f"...(truncated, total {len(s)} chars)"
    return s


# ---------------------------------------------------------------------------
# send


def cmd_send(args: argparse.Namespace) -> int:
    """读 request.json → 发 HTTP → 落盘 result.json。

    输出单行：
      [OK] send: <METHOD> <url> → <status> elapsed=<N>ms result_file=<path>
      [FAIL] send: <msg>
    """
    request_dict = _read_request_input(args)
    req_args = build_requests_args(request_dict, default_timeout=args.timeout)

    # 默认从 cwd 启动请求（如果有 --verify-ssl 控制，这里接收）
    response = send_request(
        method=req_args["method"],
        url=req_args["url"],
        headers=req_args.get("headers") or {},
        data=req_args.get("data"),
        json_body=req_args.get("json_body"),
        timeout=req_args.get("timeout", 30.0),
        verify_ssl=not getattr(args, "no_verify_ssl", False),
        fail_on_status=not getattr(args, "no_fail_on_status", False),
    )

    # 决定输出目录
    out_dir = (
        Path(args.output_dir).expanduser().resolve()
        if getattr(args, "output_dir", None)
        else default_result_dir()
    )
    out_path = make_result_path(out_dir)

    cli_cmd = "shenle-api-cli send <req.json>"
    save_result(
        request_dict=request_dict,
        response=response,
        cli_cmd=cli_cmd,
        tool_version=__version__,
        out_path=out_path,
    )

    # stdout 单行
    short_url = response.url
    if len(short_url) > 80:
        short_url = short_url[:77] + "..."
    print(
        f"[OK] send: {response.status} {req_args['method']} {short_url} "
        f"elapsed={response.elapsed_ms}ms "
        f"result_file={out_path}"
    )
    return 0


# ---------------------------------------------------------------------------
# call (0.2 新增)：send + extract 一步到位
# ---------------------------------------------------------------------------


def _do_extract(
    result: dict[str, Any],
    field: str,
    extract_name: str,
) -> str:
    """从 result dict 里抽 field（支持 JSONPath 和 NL）。返格式化好的值字符串。"""
    response = result.get("response") or {}
    body_json = response.get("body_json")
    body_text = response.get("body_text") or ""
    content_type = (response.get("headers") or {}).get("content-type", "")

    if is_jsonpath(field):
        if body_json is None:
            raise CliError(
                "call: response body 不是合法 JSON，无法用 JSONPath 提取（"
                "body 头 200 字：" + (body_text or "")[:200] + "）"
            )
        value = _do_jsonpath_extract(body_json, field)
        if value is None:
            # JSONPath 未命中：返 null（不算错误，调用方能区分）
            return "null(JSONPath 未匹配)"
        return _truncate_value(value)

    # 自然语言模式
    extracted = _do_nl_extract(
        body_text,
        content_type,
        [(extract_name, field)],
    )
    val = extracted.get(extract_name, "")
    return _truncate_value(val)


def cmd_call(args: argparse.Namespace) -> int:
    """send + extract 一步到位（0.2 新增）。

    设计目的：避免 Windows cmd.exe / bash 跨平台的管道 / 变量赋值兼容问题。
    Agent 只需要发一次 bash 调用就能拿到值（不需要 $() / set / grep / |）。

    输出单行：
      [OK] call: status=200 method=POST elapsed=110ms name=<字段名> value=<值>

    用法：
      shenle-api-cli call req.json --field "$.data.token"                # JSONPath
      shenle-api-cli call req.json --field "返回的 token" --name 登录Token  # NL
      shenle-api-cli call req.json --field "$.code" --no-fail-on-status  # 测试 4xx 响应
    """
    request_dict = _read_request_input(args)
    req_args = build_requests_args(request_dict, default_timeout=args.timeout)

    response = send_request(
        method=req_args["method"],
        url=req_args["url"],
        headers=req_args.get("headers") or {},
        data=req_args.get("data"),
        json_body=req_args.get("json_body"),
        timeout=req_args.get("timeout", 30.0),
        verify_ssl=not getattr(args, "no_verify_ssl", False),
        fail_on_status=not getattr(args, "no_fail_on_status", False),
    )

    # 落盘（与 send 一致）
    out_dir = (
        Path(args.output_dir).expanduser().resolve()
        if getattr(args, "output_dir", None)
        else default_result_dir()
    )
    out_path = make_result_path(out_dir)

    save_result(
        request_dict=request_dict,
        response=response,
        cli_cmd=f"shenle-api-cli call <req.json> --field {args.field!r}",
        tool_version=__version__,
        out_path=out_path,
    )

    # 立刻抽字段
    extract_name = getattr(args, "name", None) or "value"
    result = load_result(out_path)
    value_str = _do_extract(result, args.field, extract_name)

    print(
        f"[OK] call: status={response.status} method={req_args['method']} "
        f"elapsed={response.elapsed_ms}ms "
        f"name={extract_name} value={value_str} "
        f"result_file={out_path}"
    )
    return 0


# ---------------------------------------------------------------------------
# extract


def _do_jsonpath_extract(body_json: Any, field: str) -> Any:
    """走 JSONPath 提取。匹配不到返 None。"""
    return eval_path(body_json, field)


def _do_nl_extract(
    response_body: str,
    content_type: str,
    extraction_specs: list[tuple[str, str]],
) -> dict[str, str]:
    """走 AI 自然语言提取，返回 {name: value}。

    Raises:
        AIConfigError / AIRuntimeError
    """
    cfg = load_config()
    specs_text = "\n".join(f'- 字段名 = "{desc}"' for _, desc in extraction_specs)
    sys_p = PROMPT_EXTRACT_NL.format(
        response_body=response_body[:8000],  # 截前 8KB 防止 prompt 爆
        content_type=content_type or "(unknown)",
        extraction_specs=specs_text,
    )
    usr_p = "请抽取上述字段。"
    parsed = ask_text(cfg, sys_p, usr_p, max_tokens=512)
    out: dict[str, str] = {}
    for name, _ in extraction_specs:
        v = parsed.get(name)
        if v is None:
            out[name] = ""
        else:
            out[name] = str(v)
    return out


def cmd_extract(args: argparse.Namespace) -> int:
    """从 result 文件提取变量（JSONPath 或 NL）。"""
    result_path = Path(args.result_path).expanduser()
    result = load_result(result_path)

    response = result.get("response") or {}
    body_json = response.get("body_json")
    body_text = response.get("body_text") or ""
    content_type = (response.get("headers") or {}).get("content-type", "")
    field = args.field

    # 自动判断
    if is_jsonpath(field):
        if body_json is None:
            raise CliError("extract: response body 不是合法 JSON，无法用 JSONPath 提取")
        value = _do_jsonpath_extract(body_json, field)
        if value is None:
            print(f"[OK] extract: name={field} value=null (JSONPath 未匹配)")
            return 0
        name = getattr(args, "name", None) or field
        print(f"[OK] extract: name={name} value={_truncate_value(value)}")
        return 0

    # 自然语言模式
    extract_name = getattr(args, "name", None) or "value"
    extracted = _do_nl_extract(
        body_text,
        content_type,
        [(extract_name, field)],
    )
    val = extracted.get(extract_name, "")
    print(f"[OK] extract: name={extract_name} value={_truncate_value(val)}")
    return 0


# ---------------------------------------------------------------------------
# assert


def cmd_assert(args: argparse.Namespace) -> int:
    """自然语言断言（必须 AI 配置）。"""
    result_path = Path(args.result_path).expanduser()
    result = load_result(result_path)

    response = result.get("response") or {}
    body_text = response.get("body_text") or ""
    content_type = (response.get("headers") or {}).get("content-type", "")
    status = response.get("status", 0)

    assertion = args.assertion
    cfg = load_config()
    sys_p = PROMPT_ASSERT_NL.format(
        response_body=body_text[:8000],
        content_type=content_type or "(unknown)",
        status_code=status,
        assertion=assertion,
    )
    parsed = ask_text(cfg, sys_p, "请判断断言是否通过。", max_tokens=256)
    passed = bool(parsed.get("passed"))
    reason = str(parsed.get("reason") or "").strip() or "(no reason)"

    if not passed:
        # 用 CliError 表达断言失败，让 main 打印 [FAIL]
        raise AssertFailed(reason)

    print(f"[OK] assert: passed=true reason={reason}")
    return 0
