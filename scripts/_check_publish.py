"""发布后自检：索引行数、zip 数量、两页是否存在。"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
idx = (ROOT / "site" / "skills" / "index.md").read_text(encoding="utf-8")
rows = [ln for ln in idx.splitlines() if ln.startswith("| `")]
zips = sorted(p.name for p in (ROOT / "site" / "public" / "skills").glob("*.zip"))
print("index rows:", len(rows))
print("zips:", len(zips))
print("api/dev:", [z for z in zips if "api-cli" in z or "device-record" in z])
for name in ("shenle-api-cli", "shenle-device-record"):
    page = ROOT / "site" / "skills" / f"{name}.md"
    print(name, "page?", page.is_file(), page.stat().st_size if page.is_file() else "-")
