"""把 send 命令的 request/response 落盘到系统 temp 目录。

默认位置：`<tempdir>/shenle-api-results/<YYYYMMDD-HHmmss>-<uuid4[:8]>.json`

文件结构与 shenle-api-record rawNN.json 类似，便于复用其 inspect 脚本。
"""

from __future__ import annotations

import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from .errors import ResultFileInvalid, ResultFileNotFound
from .http_client import ResponseData


# 默认结果目录：<tempdir>/shenle-api-results
def default_result_dir() -> Path:
    """返回默认结果目录（系统 tempdir / shenle-api-results）。"""
    return Path(tempfile.gettempdir()) / "shenle-api-results"


def ensure_result_dir(dir_path: Path) -> Path:
    """确保结果目录存在（不存在则创建）。"""
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def make_result_path(dir_path: Path) -> Path:
    """生成一个唯一的 result 文件路径。

    命名：<YYYYMMDD-HHmmss>-<uuid4 前 8 位>.json
    """
    ensure_result_dir(dir_path)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return dir_path / f"{ts}-{short_uuid}.json"


def save_result(
    request_dict: dict[str, Any],
    response: ResponseData,
    cli_cmd: str,
    tool_version: str,
    out_path: Path,
) -> Path:
    """把 {request, response, meta} 写到 out_path，返回写入的路径。

    Args:
        request_dict: 原始请求 dict（send 命令收到的原样）
        response: ResponseData
        cli_cmd: 调用本工具的命令行字符串（如 "shenle-api-cli send req.json"）
        tool_version: 工具版本号
        out_path: 目标路径

    Returns:
        实际写入的路径。
    """
    ensure_result_dir(out_path.parent)
    payload = {
        "request": request_dict,
        "response": {
            "url": response.url,
            "status": response.status,
            "status_text": response.status_text,
            "headers": response.headers,
            "body_text": response.body_text,
            "body_json": response.body_json,
            "elapsed_ms": response.elapsed_ms,
            "called_at": response.called_at,
        },
        "meta": {
            "tool_version": tool_version,
            "cli_cmd": cli_cmd,
            "size_bytes": response.size_bytes,
            "body_truncated": response.body_truncated,
        },
    }
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_path


def load_result(path: Path) -> dict[str, Any]:
    """读 result 文件，返回完整 dict（{request, response, meta}）。

    Raises:
        ResultFileNotFound: 文件不存在
        ResultFileInvalid: JSON 解析失败 / 缺 response
    """
    if not path.exists():
        raise ResultFileNotFound(str(path))
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        raise ResultFileInvalid(f"读文件失败：{e}") from e
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ResultFileInvalid(f"JSON 解析失败：{e}") from e
    if not isinstance(data, dict):
        raise ResultFileInvalid("顶层不是 dict")
    if "response" not in data:
        raise ResultFileInvalid("缺 response 段（可能不是 shenle-api-cli 生成的文件）")
    return data
