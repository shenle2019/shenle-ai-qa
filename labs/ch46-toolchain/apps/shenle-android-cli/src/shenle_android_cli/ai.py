"""AI 视觉模型调用：读 ANDROID_AI_* 配置 + 多模态 chat/completions + bbox 解析。

与 shenle-web-cli/ai.py 的一致之处：
- 0-1000 归一化坐标（与图片实际像素无关），本地按图片真实尺寸换算成像素
- 用 urllib 直连，不拉 openai SDK
- 容错 JSON 解析（围栏 / 第一个 {} / 数字兜底）
- JSON 解析失败时自动重试一次

差异：
- 配置前缀：ANDROID_AI_API_KEY / ANDROID_AI_BASE_URL / ANDROID_AI_MODEL
  （跟 demo/shenle-android-cli/demo_2.py 对齐，不复用 WEB_AUTOMATION_AI_*）
- prompt 模板：要求 AI 返回 `{found: bool, bbox: [...]}`，
  `found=false` 时抛 ElementNotFound（屏幕上没看到）
- prompt 顺带把图片实际像素告诉 AI，便于它做绝对定位参考
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .errors import CliError, ElementNotFound


# 单元素定位 prompt（跟 demo_2.py 保持 1:1，除了占位变量命名）。
# 视觉模型对英文 prompt 响应更稳定，这里用英文；输入给 AI 的图片描述
# 仍然包含图片实际尺寸，方便它定位。
PROMPT_BBOX_TEMPLATE = """You are an AI assistant specialized in UI element localization on Android devices.

## Objective:
- ONLY identify if the target element exists in the screenshot.
- If found, provide the precise bounding box coordinates.
- Do NOT analyze page state or suggest actions.

## Output Format (strict JSON only)
{{
  "found": true | false,
  "bbox": [xmin, ymin, xmax, ymax] (only if found is true)
}}

## User Description
Find: {description}

## Screenshot Analysis
- Image size: {w}x{h} pixels (Android screen)
- Output bbox in 0-1000 normalized space.
"""


# 区域描述 prompt（4 节：layout / icons / text / intro）—— 跟 shenle-web-cli/ai.py
# 的 PROMPT_DESCRIBE_TEMPLATE 一致，确保两个工具的 get 行为对齐。
PROMPT_DESCRIBE_TEMPLATE = """你是 Android UI 描述助手。用户给出一张安卓屏幕截图，需要你详细描述其中某个区域的内容，给看不到这张图的"消费者"用。

区域描述：{area}

按下面四节输出，每节用一行 ## 标题 + 内容，不要其他多余文字：

## 布局
区域内元素的位置、大小、排列方式。

## 图标
区域内出现的图标的形状、颜色、含义。如无图标则写"无"。

## 文字
区域内所有可读的文字，按出现顺序逐行列出。如无文字则写"无"。

## 介绍
一两句话说明这个区域是什么、做什么的。"""


# 批量定位 prompt：一次 AI 调用返回 N 个 bbox（0-1000 归一化）
PROMPT_BATCH_BBOX_TEMPLATE = """You are an AI assistant specialized in UI element localization on Android devices.

## Output Format (strict JSON only)
{{
  "bboxes": [
    [xmin, ymin, xmax, ymax],
    [xmin, ymin, xmax, ymax],
    ...
  ]
}}

## User Descriptions
There are {n} elements to find, **in order**:
{indexed_list}

## Screenshot Analysis
- Image size: {w}x{h} pixels (Android screen)
- Output each bbox in 0-1000 normalized space.
- Length of `bboxes` array MUST be exactly {n}.
- Order MUST match the descriptions above.
"""


_REQUIRED_ENV = (
    "ANDROID_AI_API_KEY",
    "ANDROID_AI_BASE_URL",
    "ANDROID_AI_MODEL",
)


@dataclass(frozen=True)
class AIConfig:
    api_key: str
    base_url: str
    model: str
    timeout_s: float = 30.0


class AIConfigError(CliError):
    """ANDROID_AI_* 配置缺失。"""


class AIRuntimeError(CliError):
    """调 AI 出错（网络、超时、响应结构异常）。"""


def load_config() -> AIConfig:
    """从 CWD/.env + 环境变量读 AI 配置。任一缺失即抛 AIConfigError。

    override=False 让真实环境变量优先；.env 只补缺失的。
    """
    env_path = Path.cwd() / ".env"
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path, override=False)
    missing = [n for n in _REQUIRED_ENV if not os.environ.get(n)]
    if missing:
        raise AIConfigError(
            "AI 配置缺失：" + "、".join(missing) + "。"
            "请在当前目录的 .env 文件或环境变量里配置，例如：\n"
            "  ANDROID_AI_API_KEY=sk-xxx\n"
            "  ANDROID_AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1\n"
            "  ANDROID_AI_MODEL=qwen-vl-plus"
        )
    return AIConfig(
        api_key=os.environ["ANDROID_AI_API_KEY"],
        base_url=os.environ["ANDROID_AI_BASE_URL"].rstrip("/"),
        model=os.environ["ANDROID_AI_MODEL"],
    )


# ---------------------------------------------------------------------------
# 调用


def ask_vision_for_bbox_norm(
    cfg: AIConfig,
    screenshot_path: Path,
    description: str,
    img_w: int,
    img_h: int,
) -> list[int]:
    """让 AI 返回 bbox，**0-1000 归一化坐标**。

    返回 [xmin, ymin, xmax, ymax]，每个值 0-1000 的整数。
    调用方需要按图片真实尺寸换算成像素：
        scale_x = img_w / 1000
        scale_y = img_h / 1000
        bbox_px = [xmin*scale_x, ymin*scale_y, xmax*scale_x, ymax*scale_y]

    AI 返回 `found=false` 时抛 ElementNotFound（让上层报"屏幕上没看到"）。
    """
    text = _call_vision_with_retry(
        cfg, screenshot_path,
        PROMPT_BBOX_TEMPLATE.format(description=description, w=img_w, h=img_h),
        max_tokens=512,
    )
    obj = _try_parse_json_loose(text)
    if obj is None:
        raise AIRuntimeError(f"AI 响应里找不到 JSON：{text[:200]!r}")

    # 兼容两种返回：
    #   {"found": false}                       → 屏幕上没看到
    #   {"found": true, "bbox": [...]}         → 标准
    #   {"bbox": [...]}（没 found 字段）        → 视为 found=true
    if isinstance(obj, dict):
        if obj.get("found") is False:
            raise ElementNotFound(description)
        bbox = obj.get("bbox")
        if bbox is None and obj.get("found") is True:
            raise AIRuntimeError(f"AI 找到元素但没给 bbox：{text[:200]!r}")
    elif isinstance(obj, list) and len(obj) == 4:
        bbox = obj
    else:
        bbox = None

    parsed = _bbox_from_obj({"bbox": bbox} if bbox else obj)
    if parsed is None:
        raise AIRuntimeError(f"AI 响应里找不到 0-1000 bbox：{text[:200]!r}")
    return parsed


async def ask_vision_for_bbox_norm_async(
    cfg: AIConfig,
    screenshot_path: Path,
    description: str,
    img_w: int,
    img_h: int,
) -> list[int]:
    return await asyncio.to_thread(
        ask_vision_for_bbox_norm, cfg, screenshot_path, description, img_w, img_h,
    )


def ask_vision_describe(
    cfg: AIConfig, screenshot_path: Path, area: str,
) -> str:
    """给 AI 一张截图 + 区域描述，返回该区域的结构化文本描述（**不**解析）。

    4 节输出（layout / icons / text / intro），用于 `get` 命令。
    """
    return _call_vision_with_retry(
        cfg, screenshot_path,
        PROMPT_DESCRIBE_TEMPLATE.format(area=area),
        max_tokens=1024,
    )


def ask_vision_for_bbox_batch_norm(
    cfg: AIConfig,
    screenshot_path: Path,
    descriptions: list[str],
    img_w: int,
    img_h: int,
) -> list[list[int]]:
    """一次 AI 调用返回 N 个 bbox（0-1000 归一化坐标），按 descriptions 顺序。

    N=1 时自动走单元素路径（避免 prompt 啰嗦）。
    """
    if not descriptions:
        return []
    if len(descriptions) == 1:
        return [ask_vision_for_bbox_norm(
            cfg, screenshot_path, descriptions[0], img_w, img_h,
        )]
    indexed = "\n".join(f"{i+1}. {d}" for i, d in enumerate(descriptions))
    prompt = PROMPT_BATCH_BBOX_TEMPLATE.format(
        n=len(descriptions),
        indexed_list=indexed,
        w=img_w, h=img_h,
    )
    text = _call_vision_with_retry(
        cfg, screenshot_path, prompt, max_tokens=2048,
    )
    return _parse_bbox_batch(text, len(descriptions))


def _call_vision(
    cfg: AIConfig,
    screenshot_path: Path,
    prompt_text: str,
    max_tokens: int = 512,
    image_format: str = "jpeg",
) -> str:
    """统一的视觉调用入口：截图 + prompt → 返回 AI 文本回复。"""
    img_b64 = base64.b64encode(Path(screenshot_path).read_bytes()).decode("ascii")

    body = {
        "model": cfg.model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_format};base64,{img_b64}",
                        },
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }

    req = urllib.request.Request(
        url=f"{cfg.base_url}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {cfg.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=cfg.timeout_s) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:300]
        raise AIRuntimeError(
            f"AI 服务返回 HTTP {e.code}：{detail}"
        ) from e
    except urllib.error.URLError as e:
        raise AIRuntimeError(
            f"AI 服务不可达（{cfg.base_url}）：{e.reason}"
        ) from e
    except TimeoutError as e:
        raise AIRuntimeError(
            f"AI 服务超时（>{cfg.timeout_s:.0f}s）"
        ) from e
    except json.JSONDecodeError as e:
        raise AIRuntimeError(f"AI 响应不是合法 JSON：{e}") from e

    try:
        msg = payload["choices"][0]["message"]
        content = msg.get("content")
        # 兼容 reasoning 模型：把推理/思考字段当 fallback
        if not content:
            content = msg.get("reasoning_content") or msg.get("reasoning")
        if not isinstance(content, str):
            content = None
    except (KeyError, IndexError, TypeError) as e:
        raise AIRuntimeError(
            f"AI 响应结构异常：{str(payload)[:300]}"
        ) from e
    if not content:
        finish = payload.get("choices", [{}])[0].get("finish_reason", "?")
        raise AIRuntimeError(
            f"AI 返回空内容（finish_reason={finish}; "
            f"model 可能是 reasoning 模型但 prompt 没要求它输出到 content 字段；"
            f"或 max_tokens 不够）"
        )
    return content


def _call_vision_with_retry(
    cfg: AIConfig,
    screenshot_path: Path,
    prompt_text: str,
    max_tokens: int = 512,
    image_format: str = "jpeg",
) -> str:
    """_call_vision + JSON 解析失败时自动重试一次。"""
    for attempt in range(2):
        try:
            text = _call_vision(cfg, screenshot_path, prompt_text, max_tokens, image_format)
            # 顺手验证一次 JSON 能不能解出来——不能就在这里重试
            if _try_parse_json_loose(text) is None:
                if attempt == 0:
                    continue
                raise AIRuntimeError(f"AI 响应里找不到 JSON：{text[:200]!r}")
            return text
        except AIRuntimeError as e:
            if attempt == 1 or "JSON" not in str(e):
                raise
            continue
    raise AIRuntimeError("AI 调用重试耗尽")  # 不会到这里


# ---------------------------------------------------------------------------
# 容错 JSON 解析（跟 web-cli/ai.py 一致）


def _try_parse_json_loose(text: str):
    """尽量宽松地从 AI 响应里抠 JSON object 或 array。"""
    if not text:
        return None
    s = text.strip()
    s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*```$", "", s)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    for pat in [r"\{[\s\S]*?\}", r"\[[\s\S]*?\]"]:
        m = re.search(pat, s)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                continue
    return None


def _bbox_from_obj(obj) -> list[int] | None:
    """从 dict / list 中抠出 [xmin, ymin, xmax, ymax]（0-1000）。"""
    if isinstance(obj, dict):
        bbox = obj.get("bbox")
    elif isinstance(obj, list) and len(obj) == 4:
        bbox = obj
    else:
        return None
    if not isinstance(bbox, list) or len(bbox) != 4:
        return None
    try:
        vals = [int(round(float(v))) for v in bbox]
    except (ValueError, TypeError):
        return None
    if not all(0 <= v <= 1000 for v in vals):
        return None
    if not (vals[0] < vals[2] and vals[1] < vals[3]):
        return None
    return vals


def _parse_bbox_batch(text: str, n: int) -> list[list[int]]:
    """解析 AI 返回的 N 个 bbox（0-1000）。"""
    obj = _try_parse_json_loose(text)
    bboxes_raw: object | None = None
    if isinstance(obj, dict):
        bboxes_raw = obj.get("bboxes")
    elif isinstance(obj, list):
        bboxes_raw = obj

    results: list[list[int]] = []
    if isinstance(bboxes_raw, list):
        for i, item in enumerate(bboxes_raw[:n]):
            bbox = _bbox_from_obj({"bbox": item} if not isinstance(item, dict) else item)
            if bbox is None:
                # 容错：抓 4 个数字
                nums = re.findall(r"\b\d{1,4}\b", str(item))
                if len(nums) >= 4:
                    vals = [int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3])]
                    if (all(0 <= v <= 1000 for v in vals)
                            and vals[0] < vals[2] and vals[1] < vals[3]):
                        bbox = vals
            if bbox is None:
                raise AIRuntimeError(
                    f"第 {i+1}/{n} 个 bbox 格式错误：{item!r}"
                )
            results.append(bbox)
        if len(results) == n:
            return results

    # 兜底：整文本按出现顺序抓 4*N 个数字
    nums = re.findall(r"\b\d{1,4}\b", text)
    if len(nums) >= n * 4:
        results = []
        for i in range(n):
            v = [int(nums[i*4+j]) for j in range(4)]
            if not (all(0 <= x <= 1000 for x in v) and v[0] < v[2] and v[1] < v[3]):
                raise AIRuntimeError(f"第 {i+1}/{n} 个 bbox 范围无效：{v}")
            results.append(v)
        return results

    raise AIRuntimeError(f"AI 响应里找不到 {n} 个 bbox：{text[:200]!r}")
