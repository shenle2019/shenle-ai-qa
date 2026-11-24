"""给 api-cli 的报错表补一条 BOM 坑（真实踩到的那条）。"""

from __future__ import annotations

from pathlib import Path

path = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "shenle-api-cli" / "SKILL.md"
text = path.read_text(encoding="utf-8")
if "Unexpected UTF-8 BOM" in text:
    print("已存在，跳过")
    raise SystemExit(0)

row = (
    "| `[FAIL] send: 请求文件格式错误：JSON 解析失败：Unexpected UTF-8 BOM` "
    "| req.json 被 PowerShell 写成带 BOM 的 UTF-8 | 用 `Set-Content -Encoding utf8NoBOM`，"
    "或让 Python 用 `open(..., encoding='utf-8')` 写 |\n"
)
anchor = "| `[FAIL] send: 网络请求失败：...` |"
idx = text.find(anchor)
if idx < 0:
    print("没找到锚点，未修改")
    raise SystemExit(1)
text = text[:idx] + row + text[idx:]
path.write_text(text, encoding="utf-8")
print("已补 BOM 一行，正文", len(text.splitlines()), "行")
