# apps/shenle-web-record/shenle_web_record/paths.py
"""Pure path, batch-id, and payload helpers. No Playwright."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

BATCH_ID_PATTERN = re.compile(r"^\d{8}-\d{6}$")


def generate_batch_id(now: datetime | None = None) -> str:
    """Return batch id `YYYYMMDD-HHmmss`. Uses `now` if provided, else `datetime.now()`."""
    moment = now if now is not None else datetime.now()
    return moment.strftime("%Y%m%d-%H%M%S")


BATCH_ROOT_NAME = "web"
BATCH_CATEGORY = "AI-信息采集"
IMG_SUBDIR = "img"
JSON_SUBDIR = "json"
SCREENSHOT_PREFIX = "screenshot_"


def make_batch_dir(root: str | Path, batch_id: str) -> Path:
    """Create `<root>/AI-信息采集/<batch_id>` and return it. Module/func subdirs
    (and img/json siblings under them) are created later by `_on_snap`, not here."""
    batch_dir = Path(root).expanduser().resolve() / BATCH_CATEGORY / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)
    return batch_dir


def next_seq(batch_dir: str | Path) -> int:
    """Return next sequence number (1-based). Scans `<batch_dir>/img/screenshot_*.png`."""
    img_dir = Path(batch_dir) / IMG_SUBDIR
    if not img_dir.is_dir():
        return 1
    max_n = 0
    for p in img_dir.glob(f"{SCREENSHOT_PREFIX}*.png"):
        stem = p.stem  # 'screenshot_007'
        suffix = stem[len(SCREENSHOT_PREFIX):]
        if suffix.isdigit():
            max_n = max(max_n, int(suffix))
    return max_n + 1


def build_dom_payload(html: str, img_relpath: str) -> dict[str, str]:
    """Build the `dom_NNN.json` payload. `img_relpath` is relative to the batch dir."""
    return {"content": html, "img": img_relpath}
