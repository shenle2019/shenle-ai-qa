from pathlib import Path

from shenle_web_record.paths import next_seq


def test_returns_one_when_dir_missing(tmp_path: Path):
    assert next_seq(tmp_path / "nope") == 1


def test_returns_one_when_img_dir_empty(tmp_path: Path):
    (tmp_path / "img").mkdir()
    assert next_seq(tmp_path) == 1


def test_returns_max_plus_one(tmp_path: Path):
    img = tmp_path / "img"
    img.mkdir()
    for name in ("screenshot_001.png", "screenshot_003.png", "screenshot_007.png"):
        (img / name).touch()
    assert next_seq(tmp_path) == 8


def test_ignores_non_matching_files(tmp_path: Path):
    img = tmp_path / "img"
    img.mkdir()
    (img / "screenshot_002.png").touch()
    (img / "screenshot_abc.png").touch()  # should be ignored
    (img / "notes.txt").touch()
    assert next_seq(tmp_path) == 3