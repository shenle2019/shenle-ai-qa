"""第 40 章测试：路由匹配、CRUD 语义、错误码、仓储唯一约束。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from projects import ProjectRepo, build_app  # noqa: E402


@pytest.fixture()
def app():
    return build_app(ProjectRepo(":memory:"))


def test_health_reports_counts(app) -> None:
    assert app.handle("GET", "/health").body == {"status": "ok", "projects": 0}


def test_create_returns_201_and_id(app) -> None:
    resp = app.handle("POST", "/projects", body={"name": "电商后台", "owner": "shenle"})
    assert resp.status == 201
    assert resp.body["id"] == 1
    assert resp.body["name"] == "电商后台"


def test_create_rejects_blank_name(app) -> None:
    assert app.handle("POST", "/projects", body={"name": "   "}).status == 400


def test_create_duplicate_is_409(app) -> None:
    app.handle("POST", "/projects", body={"name": "同名"})
    resp = app.handle("POST", "/projects", body={"name": "同名"})
    assert resp.status == 409
    assert "已存在" in resp.body["error"]


def test_list_orders_by_id(app) -> None:
    for name in ("a", "b", "c"):
        app.handle("POST", "/projects", body={"name": name})
    names = [item["name"] for item in app.handle("GET", "/projects").body["items"]]
    assert names == ["a", "b", "c"]


def test_get_missing_is_404(app) -> None:
    assert app.handle("GET", "/projects/99").status == 404


def test_rename_updates_row(app) -> None:
    created = app.handle("POST", "/projects", body={"name": "旧名"}).body
    resp = app.handle("PATCH", f"/projects/{created['id']}", body={"name": "新名"})
    assert resp.status == 200
    assert resp.body["name"] == "新名"
    assert resp.body["id"] == created["id"]


def test_rename_to_existing_is_409(app) -> None:
    first = app.handle("POST", "/projects", body={"name": "a"}).body
    app.handle("POST", "/projects", body={"name": "b"})
    assert app.handle("PATCH", f"/projects/{first['id']}", body={"name": "b"}).status == 409


def test_delete_then_get_is_404(app) -> None:
    created = app.handle("POST", "/projects", body={"name": "待删"}).body
    assert app.handle("DELETE", f"/projects/{created['id']}").status == 204
    assert app.handle("GET", f"/projects/{created['id']}").status == 404


def test_unknown_route_is_404(app) -> None:
    resp = app.handle("GET", "/nope")
    assert resp.status == 404
    assert "没有这个路由" in resp.body["error"]


def test_repo_is_framework_agnostic(tmp_path) -> None:
    """仓储层不依赖 HTTP：直接调用也能工作，且能落盘。"""
    repo = ProjectRepo(tmp_path / "p.db")
    item = repo.create("落盘项目")
    repo2 = ProjectRepo(tmp_path / "p.db")
    assert repo2.get(item["id"])["name"] == "落盘项目"


def test_query_params_merge_into_request(app) -> None:
    """路径参数与查询参数并存时不互相覆盖（查询参数优先）。"""
    created = app.handle("POST", "/projects", body={"name": "q"}).body
    resp = app.handle("GET", f"/projects/{created['id']}", query={"project_id": str(created["id"])})
    assert resp.status == 200
