"""把生成的数据落成文件：json / csv / 纯文本。"""

from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path


def _prepare(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def dump_json(path: str | Path, payload: object) -> Path:
    """写 JSON：中文不转义、缩进 2、日期用 isoformat。"""
    target = _prepare(Path(path))

    def default(obj: object) -> str:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return str(obj)

    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=default),
        encoding="utf-8",
    )
    return target


def load_json(path: str | Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_csv(path: str | Path, rows: list[dict]) -> Path:
    """utf-8-sig 让 Excel 直接打开不乱码。"""
    if not rows:
        raise ValueError("rows 不能为空")
    target = _prepare(Path(path))
    with target.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return target


def write_text(path: str | Path, lines: list[str]) -> Path:
    target = _prepare(Path(path))
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target
