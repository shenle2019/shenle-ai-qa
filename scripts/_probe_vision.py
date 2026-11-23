"""用百炼 key 探一次视觉能力：模型列表 + 看图问答 + bbox 输出。"""

from __future__ import annotations

import base64
import io
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
CANDIDATES = ["qwen-vl-max", "qwen-vl-plus", "qwen2.5-vl-72b-instruct", "qwen3-vl-plus"]


def key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("WEB_AUTOMATION_AI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no key in .env")


def http(url: str, payload: dict | None, token: str) -> tuple[int, dict]:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:  # type: ignore[attr-defined]
        return exc.code, json.loads(exc.read().decode() or "{}")


def make_png() -> str:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (320, 200), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([40, 70, 200, 130], fill="#A3E635", outline="black", width=2)
    d.text((60, 92), "LOGIN", fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def ask(model: str, token: str, image_b64: str, prompt: str) -> tuple[int, dict]:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                ],
            }
        ],
    }
    return http(f"{BASE}/chat/completions", payload, token)


def main() -> None:
    token = key()
    status, models = http(f"{BASE}/models", None, token)
    ids = [m.get("id", "") for m in models.get("data", [])] if status == 200 else []
    vision = [i for i in ids if "vl" in i.lower() or "vision" in i.lower()]
    print(f"models: {status} total={len(ids)} vision={len(vision)}")
    print("vision ids:", ", ".join(sorted(vision)[:12]) or "(none)")

    image = make_png()
    for model in CANDIDATES:
        st, body = ask(model, token, image, "图里有一个按钮，告诉我按钮上的英文单词，只回单词。")
        if st != 200:
            print(f"[{model}] HTTP {st} -> {str(body)[:160]}")
            continue
        text = body["choices"][0]["message"]["content"]
        print(f"[{model}] OK -> {str(text)[:60]}")

    st, body = ask(
        "qwen-vl-max",
        token,
        image,
        '返回 JSON：{"bbox":[x1,y1,x2,y2]}，表示绿色按钮的位置，坐标按 320x200 的原图。',
    )
    print("bbox probe:", st, str(body)[:220])


if __name__ == "__main__":
    main()
