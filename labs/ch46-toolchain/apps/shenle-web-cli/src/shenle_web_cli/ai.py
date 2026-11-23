"""AI 视觉模型调用：读取配置 + 多模态 chat/completions + bbox 解析。

设计核心：AI 返回 0-1000 归一化坐标（与图片实际像素无关），由本地按
图片真实尺寸换算成像素坐标。比起让 AI 直接猜像素，跨尺寸/跨 DPI
稳定得多（参考 AI_UI_Demo/demo_02.py 的 convert_bbox_to_pixel 模式）。

只用标准库（urllib + json + base64），不再额外拉 HTTP 客户端。
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

from .errors import CliError


# 单元素 bbox：让 AI 给 0-1000 归一化坐标
PROMPT_BBOX_TEMPLATE = """你是网页 UI 元素定位助手。用户给出一张网页截图，需要你定位一个元素的 bounding box。

任务描述：{description}

【坐标系统，极其重要】
- 使用 **0-1000 归一化坐标**，无论图片实际多大都按 0-1000 输出
- (0, 0) = 图片左上角，(1000, 1000) = 图片右下角
- 所有 bbox 值必须是 0-1000 之间的整数
- xmin < xmax 且 ymin < ymax

【返回格式，严格 JSON，不要 markdown，不要任何解释文字】
{{"bbox": [xmin, ymin, xmax, ymax]}}

要求：
1. bbox 完全包住目标元素（视觉边界，不是它的 label 文字）
2. 元素如果是输入框，点输入框本身（不是 label）
3. 外边距尽量小，不要包含无关内容

返回示例：{{"bbox": [120, 340, 580, 380]}}"""


# 区域描述：四段结构化文本输出（用于 `get` 命令，不需坐标）
PROMPT_DESCRIBE_TEMPLATE = """你是网页 UI 描述助手。用户给出一张网页截图，需要你详细描述其中某个区域的内容，给看不到这张图的"消费者"用。

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


# 批量 bbox：一次 AI 调用识别多个元素
PROMPT_BATCH_BBOX_TEMPLATE = """你是网页 UI 元素定位助手。下面是一张网页截图，需要你按顺序定位 N 个元素的 bounding box。

元素列表（共 {n} 个，按顺序）：
{indexed_list}

【坐标系统，极其重要】
- 使用 0-1000 归一化坐标
- (0, 0) = 图片左上角，(1000, 1000) = 图片右下角
- 所有值必须是 0-1000 之间的整数

【返回格式，严格 JSON】
{{"bboxes": [[xmin,ymin,xmax,ymax], [xmin,ymin,xmax,ymax], ...]}}

要求：
1. 数组长度严格等于 {n}
2. 顺序与列表严格对应（不要重排）
3. 每个 bbox 完全包住对应元素

返回示例：{{"bboxes": [[100,200,500,800], [50,100,200,300]]}}"""


# ---------------------------------------------------------------------------
# 配置


@dataclass(frozen=True)
class AIConfig:
    api_key: str
    base_url: str
    model: str
    timeout_s: float = 30.0


class AIConfigError(CliError):
    """AI 配置缺失；属于 CliError 子类，由 cli.main 统一打印。"""


class AIRuntimeError(CliError):
    """调用 AI 过程中出错（网络、超时、响应结构异常）。"""


_REQUIRED_ENV = (
    "WEB_AUTOMATION_AI_API_KEY",
    "WEB_AUTOMATION_AI_BASE_URL",
    "WEB_AUTOMATION_AI_MODEL",
)


def load_config() -> AIConfig:
    """从 .env / 环境变量读 AI 配置。任一缺失即抛 AIConfigError。

    强制从 CWD/.env 读取：dotenv 的 load_dotenv() 默认从 ai.py 所在目录往上
    找 .env（找到 apps/shenle-web-cli/.env 会覆盖用户的意图），所以显式指定
    CWD/.env。找不到不报错（用户可能用真实环境变量配置）。
    """
    env_path = Path.cwd() / ".env"
    if env_path.is_file():
        # override=False 让真实环境变量优先；.env 只补缺失的
        load_dotenv(dotenv_path=env_path, override=False)
    missing = [n for n in _REQUIRED_ENV if not os.environ.get(n)]
    if missing:
        raise AIConfigError(
            "AI 配置缺失：" + "、".join(missing) +
            "。请在当前目录的 .env 文件或环境变量里配置。"
        )
    return AIConfig(
        api_key=os.environ["WEB_AUTOMATION_AI_API_KEY"],
        base_url=os.environ["WEB_AUTOMATION_AI_BASE_URL"].rstrip("/"),
        model=os.environ["WEB_AUTOMATION_AI_MODEL"],
    )


# ---------------------------------------------------------------------------
# 调用


# 容忍 AI 在 JSON 外面包 markdown / 解释文本
def ask_vision_for_bbox_norm(
    cfg: AIConfig,
    screenshot_path: Path,
    description: str,
) -> list[int]:
    """让 AI 返回 bbox，**0-1000 归一化坐标**。

    返回 [xmin, ymin, xmax, ymax]，每个值 0-1000 的整数。
    调用方需要按图片真实尺寸换算成像素：
        scale_x = img_w / 1000
        scale_y = img_h / 1000
        bbox_px = [xmin*scale_x, ymin*scale_y, xmax*scale_x, ymax*scale_y]
    """
    text = _call_vision_with_retry(
        cfg, screenshot_path,
        PROMPT_BBOX_TEMPLATE.format(description=description),
        max_tokens=2048,
    )
    return _parse_single_bbox(text)


def ask_vision_for_bbox_batch_norm(
    cfg: AIConfig,
    screenshot_path: Path,
    descriptions: list[str],
) -> list[list[int]]:
    """一次 AI 调用返回 N 个 bbox（0-1000 归一化坐标）。"""
    if not descriptions:
        return []
    if len(descriptions) == 1:
        return [ask_vision_for_bbox_norm(cfg, screenshot_path, descriptions[0])]
    indexed = "\n".join(f"{i+1}. {d}" for i, d in enumerate(descriptions))
    prompt = PROMPT_BATCH_BBOX_TEMPLATE.format(
        n=len(descriptions), indexed_list=indexed
    )
    text = _call_vision_with_retry(
        cfg, screenshot_path, prompt, max_tokens=4096
    )
    return _parse_bbox_batch(text, len(descriptions))


def ask_vision_describe(
    cfg: AIConfig,
    screenshot_path: Path,
    area: str,
) -> str:
    """给 AI 一张截图 + 区域描述，返回该区域的结构化文本描述（不解析）。"""
    return _call_vision(
        cfg, screenshot_path,
        PROMPT_DESCRIBE_TEMPLATE.format(area=area),
        max_tokens=1024,
    )


def _call_vision(
    cfg: AIConfig,
    screenshot_path: Path,
    prompt_text: str,
    max_tokens: int = 1024,
    image_format: str = "jpeg",
) -> str:
    """统一的视觉调用入口：截图 + prompt → 返回 AI 文本回复。

    image_format: "jpeg" 或 "png"。Phase 4 起 AI 截图默认走 JPEG q=80（小 ~3x）。
    """
    img_b64 = base64.b64encode(
        Path(screenshot_path).read_bytes()
    ).decode("ascii")

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
        # 兼容 reasoning 模型（DeepSeek/Qwen-Thinking 等）：把推理/思考字段当
        # fallback；通常模型会把最终 JSON 输出放在 reasoning_content / reasoning。
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


# ---------------------------------------------------------------------------
# 重试 + 解析


def _call_vision_with_retry(
    cfg: AIConfig,
    screenshot_path: Path,
    prompt_text: str,
    max_tokens: int = 512,
    image_format: str = "jpeg",
) -> str:
    """_call_vision + JSON 解析失败时自动重试一次（AI 偶发坏响应）。"""
    for attempt in range(2):
        try:
            text = _call_vision(
                cfg, screenshot_path, prompt_text, max_tokens, image_format
            )
            return text
        except AIRuntimeError as e:
            # 只对 "JSON 解析失败" 这类重试；网络/HTTP 错误直接抛出
            if attempt == 1 or "JSON" not in str(e):
                raise
            continue
    raise AIRuntimeError("AI 调用重试耗尽")  # 不会到这里


# ---------------------------------------------------------------------------
# 解析（容错：直接 JSON / 围栏 JSON / 正则抠块 / 数字兜底）


def _try_parse_json_loose(text: str):
    """尽量宽松地从 AI 响应里抠 JSON object 或 array。"""
    if not text:
        return None
    s = text.strip()
    # 去掉 ```json ... ``` 围栏
    s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*```$", "", s)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    # 找第一个 {...} 或 [...]
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


def _parse_single_bbox(text: str) -> list[int]:
    """解析 AI 返回的单元素 bbox（0-1000）。"""
    obj = _try_parse_json_loose(text)
    if obj is not None:
        bbox = _bbox_from_obj(obj)
        if bbox is not None:
            return bbox
    # 数字兜底：抓前 4 个数字
    nums = re.findall(r"\b\d{1,4}\b", text)
    if len(nums) >= 4:
        try:
            vals = [int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3])]
            if all(0 <= v <= 1000 for v in vals) and vals[0] < vals[2] and vals[1] < vals[3]:
                return vals
        except ValueError:
            pass
    raise AIRuntimeError(
        f"AI 响应里找不到 0-1000 bbox JSON：{text[:200]!r}"
    )


def _parse_bbox_batch(text: str, n: int) -> list[list[int]]:
    """解析 AI 返回的 N 个 bbox（0-1000）。"""
    obj = _try_parse_json_loose(text)
    bboxes: list | None = None
    if isinstance(obj, dict):
        bboxes = obj.get("bboxes")
    elif isinstance(obj, list):
        bboxes = obj
    if isinstance(bboxes, list) and len(bboxes) >= n:
        results: list[list[int]] = []
        for i, item in enumerate(bboxes[:n]):
            bbox = _bbox_from_obj(item)
            if bbox is None:
                # 单个 item 解析失败 —— 容错：抓 4 个数字
                nums = re.findall(r"\b\d{1,4}\b", str(item))
                if len(nums) >= 4:
                    try:
                        bbox = [int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3])]
                        if not (all(0 <= v <= 1000 for v in bbox)
                                and bbox[0] < bbox[2] and bbox[1] < bbox[3]):
                            bbox = None
                    except ValueError:
                        bbox = None
                if bbox is None:
                    raise AIRuntimeError(
                        f"第 {i+1}/{n} 个 bbox 格式错误：{item!r}"
                    )
            results.append(bbox)
        return results

    # 整文本兜底：按出现顺序抓 4*N 个数字
    nums = re.findall(r"\b\d{1,4}\b", text)
    if len(nums) >= n * 4:
        results = []
        for i in range(n):
            v = [int(nums[i*4+j]) for j in range(4)]
            if all(0 <= x <= 1000 for x in v) and v[0] < v[2] and v[1] < v[3]:
                results.append(v)
            else:
                raise AIRuntimeError(
                    f"第 {i+1}/{n} 个 bbox 范围无效：{v}"
                )
        return results

    raise AIRuntimeError(
        f"AI 响应里找不到 {n} 个 bbox：{text[:200]!r}"
    )


# ---------------------------------------------------------------------------
# async 包装：在 Playwright async 上下文里调用时不会阻塞事件循环


async def ask_vision_for_bbox_norm_async(
    cfg: AIConfig,
    screenshot_path: Path,
    description: str,
) -> list[int]:
    return await asyncio.to_thread(
        ask_vision_for_bbox_norm, cfg, screenshot_path, description
    )


async def ask_vision_for_bbox_batch_norm_async(
    cfg: AIConfig,
    screenshot_path: Path,
    descriptions: list[str],
) -> list[list[int]]:
    return await asyncio.to_thread(
        ask_vision_for_bbox_batch_norm, cfg, screenshot_path, descriptions
    )


async def ask_vision_describe_async(
    cfg: AIConfig,
    screenshot_path: Path,
    area: str,
) -> str:
    return await asyncio.to_thread(
        ask_vision_describe, cfg, screenshot_path, area
    )
