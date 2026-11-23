from pathlib import Path

from shenle_web_record.paths import make_batch_dir


def test_creates_batch_dir(tmp_path: Path):
    """make_batch_dir creates `<root>/AI-信息采集/<batch_id>`; module/func/img/json
    subdirs are created later by `_on_snap`."""
    bid = "20260102-030405"
    out = make_batch_dir(tmp_path, bid)
    assert out == tmp_path / "AI-信息采集" / bid
    assert out.is_dir()
    # No web/ intermediate layer.
    assert not (tmp_path / "web").exists()


def test_idempotent_when_called_twice(tmp_path: Path):
    bid = "20260102-030405"
    a = make_batch_dir(tmp_path, bid)
    b = make_batch_dir(tmp_path, bid)
    assert a == b
    assert a.is_dir()