from pathlib import Path

import pytest
from stdlib_demo import (
    DataFileError,
    append_line,
    count_lines,
    dump_json,
    load_json,
    parse_int,
    read_csv,
    read_numbers,
    safe_divide,
    unique_name,
    write_csv,
    write_lines,
)


def test_write_and_count_lines(tmp_path):
    path = tmp_path / "a" / "notes.txt"
    assert write_lines(path, ["一", "二"]) == 2
    append_line(path, "三")
    assert count_lines(path) == 3
    assert path.read_text(encoding="utf-8").splitlines() == ["一", "二", "三"]


def test_count_lines_missing_file(tmp_path):
    with pytest.raises(DataFileError) as info:
        count_lines(tmp_path / "nope.txt")
    assert "文件不存在" in str(info.value)


def test_json_roundtrip_keeps_chinese(tmp_path):
    path = tmp_path / "payload.json"
    text = dump_json(path, {"name": "测试数据", "n": 1})
    assert "测试数据" in text  # ensure_ascii=False
    assert load_json(path) == {"name": "测试数据", "n": 1}


def test_json_uses_default_str_for_objects(tmp_path):
    from datetime import datetime

    path = tmp_path / "payload.json"
    dump_json(path, {"created": datetime(2026, 11, 16, 9, 0)})
    assert load_json(path)["created"].startswith("2026-11-16")


def test_json_broken_file_raises(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(DataFileError) as info:
        load_json(path)
    assert "JSON 解析失败" in str(info.value)


def test_csv_roundtrip(tmp_path):
    path = tmp_path / "rows.csv"
    assert write_csv(path, [{"id": 1, "name": "甲"}, {"id": 2, "name": "乙"}]) == 2
    assert read_csv(path) == [{"id": "1", "name": "甲"}, {"id": "2", "name": "乙"}]


def test_csv_rejects_empty_rows(tmp_path):
    with pytest.raises(ValueError):
        write_csv(tmp_path / "x.csv", [])


def test_unique_name_is_really_unique(tmp_path):
    names = {unique_name(tmp_path).name for _ in range(30)}
    assert len(names) == 30
    assert all(n.startswith("report-") and n.endswith(".json") for n in names)


def test_parse_int_wraps_error():
    assert parse_int("42") == 42
    with pytest.raises(DataFileError) as info:
        parse_int("abc")
    assert info.value.__cause__ is not None


def test_safe_divide_success():
    assert safe_divide(6, 3) == 2


def test_safe_divide_zero_raises():
    with pytest.raises(ZeroDivisionError):
        safe_divide(1, 0)


def test_read_numbers_skips_comments_and_blanks(tmp_path):
    path = tmp_path / "numbers.txt"
    write_lines(path, ["1", "# 注释", "", "2", "3"])
    assert read_numbers(path) == [1, 2, 3]


def test_read_numbers_reports_bad_line(tmp_path):
    path = tmp_path / "numbers.txt"
    write_lines(path, ["1", "oops"])
    with pytest.raises(DataFileError) as info:
        read_numbers(path)
    assert "第 2 行" in str(info.value)


def test_path_helpers(tmp_path):
    nested = tmp_path / "x" / "y"
    nested.mkdir(parents=True)
    target = nested / "file.txt"
    target.write_text("hi", encoding="utf-8")
    assert target.name == "file.txt"
    assert target.stem == "file"
    assert target.suffix == ".txt"
    assert target.parent == nested
    assert list(nested.glob("*.txt")) == [target]
    assert Path(target.read_text(encoding="utf-8")) == Path("hi")
