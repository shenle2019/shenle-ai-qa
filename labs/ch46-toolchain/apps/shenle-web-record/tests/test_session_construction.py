from pathlib import Path

from shenle_web_record.paths import generate_batch_id
from shenle_web_record.session import RecorderSession


def test_init_assigns_paths_and_seq(monkeypatch, tmp_path: Path):
    # Freeze batch id for determinism
    fixed = "20260102-030405"
    monkeypatch.setattr(
        "shenle_web_record.session.generate_batch_id", lambda *a, **k: fixed
    )

    s = RecorderSession(url="https://example.com", output_root=str(tmp_path))

    assert s.url == "https://example.com"
    assert s._batch_id == fixed
    assert s._batch_dir == tmp_path / "AI-信息采集" / fixed
    assert s._batch_dir.is_dir()
    # v3: img/json subdirs are no longer created in __init__ — _on_snap creates
    # them under the module/func target directory on first click.
    assert not (s._batch_dir / "img").exists()
    assert s._seq == 1  # fresh dir → seq starts at 1
