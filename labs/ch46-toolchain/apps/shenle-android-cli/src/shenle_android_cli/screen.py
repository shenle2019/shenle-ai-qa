"""截图 + 屏幕尺寸。

- screencap_to_image: `adb exec-out screencap -p` → PIL.Image（RGB）
  走 exec-out 是因为直接 `adb shell screencap -p` 会写到设备文件，
  exec-out 把 PNG 字节直接吐到 stdout，避免中间文件 + 编码问题。
- screencap_to_file: 上面 + 落盘（PNG/JPEG 二选一）
"""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

from .adb import run_adb_bytes


def screencap_to_image(serial: str) -> Image.Image:
    """`adb exec-out screencap -p` → PIL.Image（确保 RGB）。"""
    proc = run_adb_bytes(["exec-out", "screencap", "-p"], serial=serial)
    if proc.returncode != 0:
        stderr_text = proc.stderr.decode(errors="replace").strip()
        raise RuntimeError(
            f"screencap 失败（rc={proc.returncode}）：{stderr_text or '无 stderr'}"
        )
    if not proc.stdout:
        raise RuntimeError("screencap 返回空字节（设备没响应？）")
    try:
        img = Image.open(io.BytesIO(proc.stdout))
        img.load()  # 立即把流读完，防止 BytesIO 被回收
    except Exception as e:
        raise RuntimeError(f"screencap 输出解析失败：{e}") from e
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def screencap_to_file(
    serial: str,
    path: Path,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> tuple[int, int]:
    """截图 → 写到 path。返回 (w, h)。fmt ∈ {"png", "jpeg"}。"""
    img = screencap_to_image(serial)
    path.parent.mkdir(parents=True, exist_ok=True)
    fmt = fmt.lower()
    if fmt == "jpeg":
        img.save(path, format="JPEG", quality=quality, optimize=True)
    elif fmt == "png":
        img.save(path, format="PNG")
    else:
        raise ValueError(f"不支持的截图格式：{fmt!r}（仅 png / jpeg）")
    return img.size


def image_to_jpeg_tempfile(img: Image.Image) -> Path:
    """把 PIL.Image 写成临时 JPEG，返回路径。**调用方负责 unlink**。

    AI 视觉识别走 JPEG q=85，比 PNG 小约 3x，省 token。
    """
    import os
    import tempfile

    fd, path_str = tempfile.mkstemp(suffix=".jpg", prefix="shenle-android-vision-")
    os.close(fd)
    p = Path(path_str)
    img.save(p, format="JPEG", quality=85, optimize=True)
    return p
