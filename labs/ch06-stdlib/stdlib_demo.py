"""第 6 章实验：文件、JSON、CSV、唯一文件名与异常。"""

from __future__ import annotations

import csv
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)


class DataFileError(Exception):
    """业务侧的统一异常：带文件路径与原因，方便定位。"""

    def __init__(self, path: Path | str, reason: str):
        super().__init__(f"{path} 处理失败：{reason}")
        self.path = Path(path)
        self.reason = reason


def write_lines(path: Path, lines: list[str]) -> int:
    """按 UTF-8 写文本，返回写入的行数。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(lines) + "\n"
    try:
        path.write_text(body, encoding="utf-8")
    except OSError as exc:
        raise DataFileError(path, f"写入失败：{exc}") from exc
    return len(lines)


def count_lines(path: Path) -> int:
    """逐行读取，避免把大文件整个读进内存。"""
    try:
        with path.open("r", encoding="utf-8") as fh:
            return sum(1 for _ in fh)
    except FileNotFoundError as exc:
        raise DataFileError(path, "文件不存在") from exc


def append_line(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip("\n") + "\n")


def dump_json(path: Path, payload: dict) -> str:
    """写 JSON：中文不转义、缩进 2、非基本类型用 str 兜底。"""
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def load_json(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DataFileError(path, "JSON 文件不存在") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DataFileError(path, f"JSON 解析失败：{exc.msg}") from exc


def write_csv(path: Path, rows: list[dict]) -> int:
    """utf-8-sig 让 Excel 打开不乱码；newline='' 防止多出空行。"""
    if not rows:
        raise ValueError("rows 不能为空")
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def unique_name(directory: Path, stem: str = "report", suffix: str = ".json") -> Path:
    """时间戳 + 短 uuid 生成不重复的文件名；撞了就重抽。"""
    directory.mkdir(parents=True, exist_ok=True)
    for _ in range(100):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        candidate = directory / f"{stem}-{stamp}-{uuid.uuid4().hex[:6]}{suffix}"
        if not candidate.exists():
            return candidate
    raise DataFileError(directory, "连续 100 次都没生成出唯一文件名")


def parse_int(raw: str) -> int:
    """把「转换失败」包装成业务异常，保留原始因果链。"""
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise DataFileError("<input>", f"{raw!r} 不是整数") from exc


def safe_divide(a: float, b: float) -> float:
    """演示 try/except/else/finally 的执行顺序。"""
    trace: list[str] = []
    try:
        result = a / b
    except ZeroDivisionError:
        trace.append("except")
        raise
    else:
        trace.append("else")
        return result
    finally:
        trace.append("finally")


def read_numbers(path: Path) -> list[int]:
    """跳过空行与注释行，坏数据直接抛业务异常。"""
    numbers: list[int] = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            try:
                numbers.append(int(text))
            except ValueError as exc:
                raise DataFileError(path, f"第 {lineno} 行不是整数：{text}") from exc
    return numbers


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    base = Path("labs/ch06-stdlib/_demo_out")
    base.mkdir(parents=True, exist_ok=True)

    txt = base / "notes.txt"
    print("写入行数:", write_lines(txt, ["第一行", "第二行"]))
    append_line(txt, "第三行")
    print("读取行数:", count_lines(txt))

    payload = {"id": 7, "name": "测试数据", "created": datetime(2026, 11, 16, 9, 0)}
    js = base / "payload.json"
    dump_json(js, payload)
    print("JSON 往返:", load_json(js))

    csv_path = base / "rows.csv"
    write_csv(csv_path, [{"id": 1, "name": "甲"}, {"id": 2, "name": "乙"}])
    print("CSV 读回:", read_csv(csv_path))

    print("唯一文件名:", unique_name(base).name)

    try:
        parse_int("abc")
    except DataFileError as exc:
        print("业务异常:", exc, "| 原因链:", repr(exc.__cause__))

    nums = base / "numbers.txt"
    write_lines(nums, ["1", "# 注释", "", "2"])
    print("数字文件:", read_numbers(nums))
