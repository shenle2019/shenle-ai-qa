"""把语雀 raw/*.json 转成 Markdown，并生成 catalog.json。

用法: python convert.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE = Path(__file__).resolve().parents[1] / "corpus" / "yuque"
RAW = BASE / "raw"
MD = BASE / "md"

CARD_RE = re.compile(r"<card\b[^>]*/?>", re.I)
NUMBER_PREFIX = re.compile(r"^(\d{1,2})[\s.、_-]+")


def clean_html(html: str) -> str:
    """去掉 lake 专有标签，保留可读结构。"""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all("card"):
        # 图片卡片保留链接，其余直接丢弃
        if tag.get("name") in {"yuqueimage", "image"}:
            src = tag.get("src") or tag.get("data-src")
            if src:
                tag.replace_with(soup.new_tag("img", src=src))
                continue
        tag.decompose()

    for tag in soup.find_all(["meta", "style", "script"]):
        tag.decompose()

    # lake 的 ol/li 带 list= / fid= 等属性，清掉避免脏输出
    for tag in soup.find_all(True):
        tag.attrs = {k: v for k, v in tag.attrs.items() if k in {"href", "src", "alt", "title", "colspan", "rowspan"}}

    return str(soup)


def to_markdown(html: str) -> str:
    text = md(clean_html(html), heading_style="ATX", bullets="-", strip=["span"])
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def first_heading(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def safe_slug(value: str, fallback: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9\-]+", "-", value).strip("-")
    return value or fallback


def main() -> None:
    MD.mkdir(parents=True, exist_ok=True)
    wrapper = json.loads((BASE / "_toc_raw.json").read_text(encoding="utf-8"))
    inner = json.loads(wrapper["value"]) if isinstance(wrapper.get("value"), str) else wrapper
    rows = inner["rows"]

    catalog = []
    converted = 0
    for index, row in enumerate(rows, start=1):
        doc_id = row["id"]
        raw_path = RAW / f"{doc_id}.json"
        if not raw_path.exists():
            catalog.append({**row, "md": None, "status": "missing"})
            continue

        payload = json.loads(raw_path.read_text(encoding="utf-8"))
        data = payload.get("data") or {}
        content_html = data.get("content") or ""
        title = data.get("title") or row["t"]
        content_md = to_markdown(content_html) if content_html else ""

        stem = f"{index:03d}-{safe_slug(data.get('slug') or str(doc_id), str(doc_id))}"
        out = MD / f"{stem}.md"
        front = [
            "---",
            f"title: {json.dumps(title, ensure_ascii=False)}",
            f"doc_id: {doc_id}",
            f"slug: {data.get('slug', '')}",
            f"book_id: {data.get('book_id', 73651885)}",
            f"words: {data.get('word_count', 0)}",
            f"updated_at: {data.get('content_updated_at', '')}",
            f"yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/{data.get('slug', '')}",
            "---",
            "",
        ]
        out.write_text("\n".join(front) + content_md + "\n", encoding="utf-8")
        converted += 1

        catalog.append(
            {
                **row,
                "slug": data.get("slug") or row.get("s", ""),
                "words": data.get("word_count", row.get("w", 0)),
                "md": str(out.relative_to(BASE)).replace("\\", "/"),
                "h1": first_heading(content_md, title),
                "status": "ok",
            }
        )

    (BASE / "catalog.json").write_text(
        json.dumps({"book_id": 73651885, "count": len(catalog), "docs": catalog}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"converted={converted} total={len(catalog)} -> {BASE / 'catalog.json'}")


if __name__ == "__main__":
    main()
