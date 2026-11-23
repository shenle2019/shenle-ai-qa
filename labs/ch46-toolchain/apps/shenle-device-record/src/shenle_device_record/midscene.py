"""`npx @midscene/android` 封装。输出解析是纯函数，便于单测。

只用连接、截图、抓界面信息三项能力，不做任何自动化操作。
"""
from __future__ import annotations

import base64
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

from shenle_device_record import LOG_PREFIX

MIDSCENE_PKG = "@midscene/android"
# 首次运行 `npx --yes @midscene/android` 要从 npm 拉整个依赖树（几十 MB，
# 含 sharp 这种大包）。国内网络下经常超过 120s，给到 300s 只对首次下载有意义，
# 截图本身通常几秒就回来了。
MIDSCENE_TIMEOUT = 300.0

# 设备上落 uiautomator dump 的临时文件
_DUMP_REMOTE = "/sdcard/shenle_device_record_dump.xml"

# 网络 URL（http/https/ftp）整体剔除：这些不是本地文件路径，
# 但会被下面的路径正则啃出 'p://host/a.png'、'/host/a.png' 之类的碎片，
# 污染日志、误导排查。file:// 不在这里——它是 midscene 报告截图路径的常见形式，
# 需要还原成本地路径后再参与匹配（见 _FILE_URL_RE / _file_url_to_local）。
_NETWORK_URL_RE = re.compile(r"(?:https?|ftp)://\S*", re.IGNORECASE)
_FILE_URL_RE = re.compile(r"file:///[^\s\"'<>|]*", re.IGNORECASE)

# 必须以盘符、斜杠或 ./ ../ 开头，避免把普通单词误当路径；懒匹配到第一个图片后缀
_IMAGE_PATH_RE = re.compile(
    r'(?:[A-Za-z]:[\\/]|/|\.{1,2}[\\/])[^\r\n"\'<>|]*?\.(?:png|jpe?g)',
    re.IGNORECASE,
)
_DATA_URI_RE = re.compile(r"data:image/(?:png|jpe?g);base64,([A-Za-z0-9+/=\s]{200,})")
_BARE_B64_RE = re.compile(r"(?:^|[\s:'\"])([A-Za-z0-9+/]{1000,}={0,2})")
_XML_WITH_DECL_RE = re.compile(r"(<\?xml.*?</hierarchy>)", re.DOTALL)
_XML_NO_DECL_RE = re.compile(r"(<hierarchy\b.*?</hierarchy>)", re.DOTALL)

# 落盘前校验图片魔数。midscene 在 stderr 打的长 base64 日志（请求体 dump、
# 错误堆栈之类）会被 _BARE_B64_RE 误认成图片，必须再过一次魔数才能落盘。
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
_JPEG_MAGIC = b"\xff\xd8\xff"

# 子进程失败、输出里出现这些关键字时，怀疑是 midscene 缺 AI 模型配置。
# 大小写不敏感，匹配 `OPENAI_API_KEY`、`api_key`、`modelName` 等。
_AI_CONFIG_KEYWORDS = (
    "openai_api_key",
    "api key",
    "api_key",
    "midscene_model",
    "model name",
    "modelname",
)


class MidsceneError(RuntimeError):
    """midscene CLI 不可用或执行失败。"""


def _file_url_to_local(url: str) -> str | None:
    """把 `file://` URL 还原成本地路径字符串（不构造 Path）。

    支持：
      - `file:///tmp/shot.png`           → `/tmp/shot.png`
      - `file:///C:/Temp/shot.png`       → `C:/Temp/shot.png`（Windows 盘符）
      - `file:///tmp/my%20shot.png`      → `/tmp/my shot.png`（百分号解码）

    这里刻意不用 `urllib.request.url2pathname`：它在 Windows 上会把
    `C:/Temp` 转成 `C:\\Temp`，与现状 Windows 路径识别正则不兼容。
    """
    if not url or not url[:7].lower() == "file://":
        return None
    body = url[len("file://"):]
    # Windows 盘符形式：`/C:/...`，去掉前导斜杠
    if (
        len(body) >= 3
        and body[0] == "/"
        and body[1].isalpha()
        and body[2] == ":"
    ):
        body = body[1:]
    return unquote(body)


def _looks_like_ai_config_error(combined: str) -> bool:
    """子进程失败时，判断输出里是否暗示缺 AI 模型配置。"""
    lowered = (combined or "").lower()
    return any(kw in lowered for kw in _AI_CONFIG_KEYWORDS)


def _ai_config_hint() -> str:
    """给中文用户看的 AI 模型配置提示，原始输出仍由调用方负责保留。"""
    return (
        "提示：midscene 是 AI 驱动的截图工具，调用前需要配置大模型。"
        "常见需要设置的环境变量：OPENAI_API_KEY（OpenAI 兼容服务的 API key）、"
        "MIDSCENE_MODEL_NAME（模型名，例如 gpt-4o、qwen-vl-max 等）。"
        "具体字段名与可选模型请参考 midscene 官方文档："
        "https://midscenejs.com/model-provider"
    )


def extract_image_path(stdout: str) -> str | None:
    """从 midscene 输出里捞图片路径，取最后一个匹配（通常是最终结果行）。

    网络 URL（http/https/ftp）整段剔除；file:// 还原成本地路径后再参与匹配。
    """
    text = stdout or ""
    # 把 file:// 先就地替换成本地路径；不匹配 _IMAGE_PATH_RE 的形态（比如
    # 根本不带图片后缀）就替换成空格，避免后续正则啃出 `/var/foo` 之类的伪路径。
    def _replace_file_url(match: "re.Match[str]") -> str:
        local = _file_url_to_local(match.group(0))
        return local if local else " "

    expanded = _FILE_URL_RE.sub(_replace_file_url, text)
    cleaned = _NETWORK_URL_RE.sub(" ", expanded)
    matches = _IMAGE_PATH_RE.findall(cleaned)
    return matches[-1].strip() if matches else None


def extract_image_base64(stdout: str) -> str | None:
    """兜底：midscene 若直接输出图片 base64，把它抠出来。"""
    match = _DATA_URI_RE.search(stdout or "")
    if match:
        return re.sub(r"\s+", "", match.group(1))
    match = _BARE_B64_RE.search(stdout or "")
    return match.group(1) if match else None


def extract_hierarchy_xml(stdout: str) -> str:
    """抠出 uiautomator 的 XML 片段；找不到返回空串。

    已知限制：这里用非贪婪正则找第一个 `</hierarchy>` 收尾，依赖 uiautomator
    不会在属性值里出现 `</hierarchy>` 字面量（例如 `<node desc="</hierarchy>"/>`
    会导致截断）。实测 uiautomator dump 不会产生这种输出，故刻意不引入完整
    XML 解析，保持解析纯函数且对残缺输出健壮。
    """
    for pattern in (_XML_WITH_DECL_RE, _XML_NO_DECL_RE):
        match = pattern.search(stdout or "")
        if match:
            return match.group(1).strip()
    return ""


def _warn(message: str) -> None:
    """往 stderr 打一条中文警告；打印本身失败也不允许向上抛。"""
    try:
        print(f"{LOG_PREFIX} {message}", file=sys.stderr)
    except Exception:  # noqa: BLE001 - stderr 不可用时静默降级
        pass


def _looks_like_image_bytes(raw: bytes) -> bool:
    """粗校验落盘前的内容是不是真的图片（PNG / JPEG）。"""
    if raw.startswith(_PNG_MAGIC):
        return True
    if raw.startswith(_JPEG_MAGIC):
        return True
    return False


def _run(args: list[str], timeout: float) -> subprocess.CompletedProcess:
    """跑 `npx --yes @midscene/android <args>`。

    Windows 上 npx 实际是 npx.cmd，必须先用 shutil.which 解析，
    否则 subprocess 会抛 FileNotFoundError。
    """
    npx = shutil.which("npx")
    if npx is None:
        raise MidsceneError(
            "找不到 npx。请安装 Node.js（https://nodejs.org），并把它加入 PATH。"
        )
    cmd = [npx, "--yes", MIDSCENE_PKG, *args]
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise MidsceneError(
            f"midscene 命令超时（{timeout}s）：{' '.join(args)}。"
            "首次运行需要下载 npm 包（@midscene/android 依赖树较大），"
            "请确认网络可用后重试；国内网络可考虑设置 npm 镜像（如 npmmirror / 淘宝源）加速。"
        ) from exc
    except OSError as exc:
        # 权限不足、可执行文件损坏、命令行过长、句柄/内存耗尽等都走这里。
        # 统一转成 MidsceneError，让上层只需处理一种异常类型。
        raise MidsceneError(
            f"midscene 命令启动失败：{exc}。"
            f"请检查 npx（{npx}）是否可执行、磁盘与系统资源是否充足。"
        ) from exc


def take_screenshot(device_id: str, timeout: float = MIDSCENE_TIMEOUT) -> Path:
    """截当前屏幕，返回图片文件路径（临时文件，调用方用完自行删除）。

    device_id 为空字符串时不传 --device-id，让 midscene CLI 自己 auto-detect
    第一台设备。直接传 `--device-id ""` 会被 midscene 的 yargs/zod 解析成
    boolean false（"Expected string, received boolean"）。
    """
    args = ["take_screenshot"]
    if device_id:
        args.extend(["--device-id", device_id])
    proc = _run(args, timeout)
    combined = f"{proc.stdout or ''}\n{proc.stderr or ''}"
    if proc.returncode != 0:
        message = (
            f"midscene 截图失败（退出码 {proc.returncode}）。原始输出：\n{combined.strip()}"
        )
        if _looks_like_ai_config_error(combined):
            message = f"{message}\n{_ai_config_hint()}"
        raise MidsceneError(message)

    path_str = extract_image_path(combined)
    if path_str:
        candidate = Path(path_str)
        if candidate.is_file():
            return candidate

    encoded = extract_image_base64(combined)
    if encoded:
        padded = encoded + "=" * (-len(encoded) % 4)
        decoded = base64.b64decode(padded)
        # 兜底分支解出来的字节必须看着像图片。stderr 里夹带的 base64 日志
        # （请求体 dump、堆栈等）会被 _BARE_B64_RE 误匹配，过这一关再落盘。
        if _looks_like_image_bytes(decoded):
            handle, tmp_name = tempfile.mkstemp(prefix="shenle_shot_", suffix=".png")
            with os.fdopen(handle, "wb") as fh:
                fh.write(decoded)
            return Path(tmp_name)

    raise MidsceneError(
        "midscene 截图命令执行成功，但输出里没找到图片路径或图片数据。"
        f"请把下面这段原始输出发给开发者以便修正解析：\n{combined.strip()}"
    )


def dump_hierarchy(device_id: str, timeout: float = MIDSCENE_TIMEOUT) -> str:
    """抓当前界面 UI 层级 XML。任何失败都只警告并返回空串，不中断采集。

    硬性契约：本函数永不抛异常。除了已知的 MidsceneError，这里还兜底捕获所有
    Exception（例如 _run 内部漏出的 OSError、解析期的意外错误），使契约不依赖
    上游实现细节。BaseException（KeyboardInterrupt / SystemExit）仍然放行，
    让用户的 Ctrl-C 不会被静默吞掉。
    """
    try:
        return _dump_hierarchy_impl(device_id, timeout)
    except Exception as exc:  # noqa: BLE001 - 契约要求：永不向上抛
        _warn(f"警告：抓取界面层级时发生未预期错误（{type(exc).__name__}）：{exc}")
        return ""


def _dump_hierarchy_impl(device_id: str, timeout: float) -> str:
    command = (
        f"uiautomator dump {_DUMP_REMOTE} >/dev/null 2>&1; "
        f"cat {_DUMP_REMOTE}; rm -f {_DUMP_REMOTE}"
    )
    # device_id 为空时不传 --device-id（同 take_screenshot 注释里的原因）
    args = ["runadbshell", "--command", command]
    if device_id:
        args.insert(0, "--device-id")
        args.insert(1, device_id)
    try:
        proc = _run(args, timeout)
    except MidsceneError as exc:
        _warn(f"警告：抓取界面层级失败：{exc}")
        return ""

    combined = f"{proc.stdout or ''}\n{proc.stderr or ''}"
    if proc.returncode != 0:
        _warn(
            f"警告：抓取界面层级失败（退出码 {proc.returncode}）："
            f"{combined.strip()[:500]}"
        )
        return ""

    xml = extract_hierarchy_xml(combined)
    if not xml:
        _warn("警告：输出里没找到 uiautomator XML，content 将留空。")
    return xml
