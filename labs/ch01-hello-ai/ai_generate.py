"""把「AI 协作四步法」第 2 步自动化：发提示词 → 拿回代码 → 存成文件。

没有 API key 时不会报错退出，而是用内置的 mock 代码走完整条链路，
方便先把流程跑通，再去申请 key。

用法：
  python ai_generate.py                使用 prompts/ch01.txt
  python ai_generate.py -p 自定义.txt
  python ai_generate.py --print-only   只打印，不写文件
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_PROMPT = ROOT / "prompts" / "ch01.txt"
OUTPUT = ROOT / "generated" / "hello_ai.py"

MOCK_CODE = '''"""离线 mock：没有配置 API key 时由 ai_generate.py 生成，用于跑通链路。"""


def build_greeting(name: str) -> str:
    return f"你好，{name}！这是第一章的第一个 AI 生成函数。"


if __name__ == "__main__":
    print(build_greeting("同学"))
'''


def load_prompt(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"提示词文件不存在：{path}")
    return path.read_text(encoding="utf-8").strip()


def call_llm(prompt: str, *, base_url: str, api_key: str, model: str, timeout: float = 60.0) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是 Python 老师，只输出可运行的代码，不要解释，不要 markdown 代码围栏。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        url=f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"].strip()


def strip_fence(text: str) -> str:
    """模型偶尔会加 ```python 围栏，这里去掉。"""
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="调用大模型生成一段 Python 代码")
    parser.add_argument("-p", "--prompt", default=str(DEFAULT_PROMPT), help="提示词文件")
    parser.add_argument("--print-only", action="store_true", help="只打印不落盘")
    args = parser.parse_args(argv)

    prompt = load_prompt(Path(args.prompt))
    api_key = os.getenv("AI_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or ""
    base_url = os.getenv("AI_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("AI_MODEL", "deepseek-chat")

    if api_key:
        print(f"→ 调用 {model} @ {base_url}")
        try:
            code = strip_fence(call_llm(prompt, base_url=base_url, api_key=api_key, model=model))
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as exc:
            print(f"✗ 调用失败：{exc}", file=sys.stderr)
            print("  提示：检查 AI_BASE_URL / AI_MODEL，或先用无 key 模式跑通流程。", file=sys.stderr)
            return 1
        source = "model"
    else:
        print("→ 未检测到 AI_API_KEY / DEEPSEEK_API_KEY，使用内置 mock 代码")
        code = MOCK_CODE
        source = "mock"

    print("\n----- 生成的代码 -----")
    print(code)
    print("----------------------")

    if not args.print_only:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(code, encoding="utf-8")
        print(f"\n已写入 {OUTPUT.relative_to(ROOT)}（来源：{source}）")
        print(f"下一步：python {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
