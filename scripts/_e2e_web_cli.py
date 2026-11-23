"""用 qwen3-vl-plus 验 bbox 输出，再跑一遍 shenle-web-cli 的真实点击链路。"""

from __future__ import annotations

import base64
import io
import json
import os
import subprocess
import sys
import threading
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / ".venv" / "Scripts"
BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen3-vl-plus"


def load_key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("WEB_AUTOMATION_AI_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no key")


def png() -> str:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (320, 200), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([40, 70, 200, 130], fill="#A3E635", outline="black", width=2)
    d.text((90, 96), "LOGIN", fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def bbox_probe(key: str) -> None:
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": '只回 JSON：{"bbox":[x1,y1,x2,y2]}，绿色按钮在原图 320x200 中的位置。'},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{png()}"}},
                ],
            }
        ],
    }
    req = urllib.request.Request(
        f"{BASE}/chat/completions",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = json.loads(resp.read().decode())
    print("bbox:", body["choices"][0]["message"]["content"][:200].replace("\n", " "))


HTML = """<!doctype html><meta charset=utf-8><title>cli 冒烟</title>
<body style="font-family:sans-serif;padding:40px">
<h1 id=t>AI 测试全栈 · CLI 冒烟页</h1>
<button id=go style="padding:12px 24px;font-size:16px" onclick="document.getElementById('out').textContent='已点击 ' + new Date().toISOString()">登录</button>
<p id=out>未点击</p></body>"""


def serve(dirpath: Path, port: int) -> ThreadingHTTPServer:
    handler = lambda *a, **kw: SimpleHTTPRequestHandler(*a, directory=str(dirpath), **kw)  # noqa: E731
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def run(args: list[str], env: dict[str, str]) -> str:
    exe = BIN / f"{args[0]}.exe"
    proc = subprocess.run([str(exe)] + args[1:], cwd=ROOT, capture_output=True, text=True, timeout=180, encoding="utf-8", errors="replace", env=env)
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return f"$ {' '.join(args)}\n{out}\n(exit {proc.returncode})"


def main() -> None:
    key = load_key()
    bbox_probe(key)

    tmp = ROOT / "labs" / "ch46-toolchain" / ".smoke"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "index.html").write_text(HTML, encoding="utf-8")
    httpd = serve(tmp, 8733)
    env = dict(os.environ)
    env.update(
        {
            "WEB_AUTOMATION_AI_API_KEY": key,
            "WEB_AUTOMATION_AI_BASE_URL": BASE,
            "WEB_AUTOMATION_AI_MODEL": MODEL,
            "PYTHONIOENCODING": "utf-8",
            "PLAYWRIGHT_BROWSERS_PATH": str(ROOT / ".pw-browsers"),
        }
    )
    logs = []
    try:
        logs.append(run(["shenle-web-cli", "start", "--headless", "--port", "9223"], env))
        logs.append(run(["shenle-web-cli", "navigate", "http://127.0.0.1:8733/index.html"], env))
        logs.append(run(["shenle-web-cli", "screenshot", str(tmp / "shot.png")], env))
        logs.append(run(["shenle-web-cli", "click", "页面上的登录按钮"], env))
        logs.append(run(["shenle-web-cli", "get", "页面底部那行状态文字"], env))
        logs.append(run(["shenle-web-cli", "title", "--format", "json"], env))
        logs.append(run(["shenle-web-cli", "close"], env))
    finally:
        httpd.shutdown()
    print("\n\n".join(logs))
    (ROOT / "labs" / "ch46-toolchain" / ".smoke" / "cli.log").write_text("\n\n".join(logs), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
