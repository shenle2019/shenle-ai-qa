"""框架用例：换环境只改 --env，改接口只动 api.py。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
sys.path.insert(0, str(HERE))

from fw_api import Batch, Files, Users  # noqa: E402
from fw_client import ApiError, HttpClient  # noqa: E402
from mini_api import serve  # noqa: E402


@pytest.fixture(scope="session")
def base():
    with serve() as url:
        yield url


@pytest.fixture(scope="session")
def client(base):
    return HttpClient(base, timeout=5, retries=1)


@pytest.fixture
def users(client):
    api = Users(client)
    api.login()
    yield api
    client.headers.pop("Authorization", None)


def test_list_users(users):
    data = users.list(size=2)
    assert data["total"] >= 3
    assert len(data["items"]) <= 2


def test_create_and_delete(users):
    created = users.create("framework-user")
    users.delete(created["id"])
    with pytest.raises(ApiError) as exc:
        users.c.get(f"/api/users/{created['id']}")
    assert exc.value.status == 404


def test_upload_then_download(client, users):
    files = Files(client)
    payload = b"hello framework"
    meta = files.upload("note.txt", payload)
    assert meta["size"] == len(payload)
    assert files.download(meta["name"]) == payload


def test_upload_rejects_non_multipart(client, users):
    with pytest.raises(ApiError) as exc:
        client.post("/api/upload", json={"file": "not-multipart"})
    assert exc.value.status == 415


def test_batch_import_counts(users):
    batch = Batch(users)
    result = batch.import_csv(HERE / "data" / "users.csv")
    assert result["ok"] == 3, result
    assert result["failed"] == []


def test_batch_import_reports_partial_failure(users, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("name,role\nqa_ok,tester\n,tester\n", encoding="utf-8")
    result = Batch(users).import_csv(bad)
    assert result["ok"] == 1
    assert len(result["failed"]) == 1


def test_export_csv_has_header(users):
    rows = [{"name": "a", "role": "tester"}, {"name": "b", "role": "dev"}]
    text = Batch(users).export_csv(rows)
    assert text.splitlines()[0] == "name,role"
    assert "a,tester" in text
