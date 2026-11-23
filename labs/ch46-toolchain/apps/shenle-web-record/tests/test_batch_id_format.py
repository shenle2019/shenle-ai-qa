# apps/shenle-web-record/tests/test_batch_id_format.py
import re
from datetime import datetime

import pytest

from shenle_web_record.paths import generate_batch_id


def test_format_matches_yyyymmdd_hhmmss():
    bid = generate_batch_id(datetime(2026, 8, 28, 14, 30, 0))
    assert re.fullmatch(r"\d{8}-\d{6}", bid)


def test_pads_single_digits():
    bid = generate_batch_id(datetime(2026, 1, 2, 3, 4, 5))
    assert bid == "20260102-030405"


def test_default_uses_now(monkeypatch):
    from shenle_web_record import paths as paths_mod

    fake = datetime(2030, 12, 31, 23, 59, 59)

    class FakeDatetime:
        @classmethod
        def now(cls):
            return fake

    # Replace the entire `datetime` symbol inside paths.py with our stub.
    monkeypatch.setattr(paths_mod, "datetime", FakeDatetime)
    assert paths_mod.generate_batch_id() == "20301231-235959"