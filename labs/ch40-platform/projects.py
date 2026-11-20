"""第 40 章：分层示例——路由层（miniweb）+ 仓储层（sqlite3）+ 服务层（projects.py）。

分层的判据只有一条：换掉存储或换掉框架时，业务代码不用改。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from miniweb import App, Request, Response, error, json_response

__all__ = ["ProjectRepo", "build_app", "SCHEMA"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    owner TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class ProjectRepo:
    """仓储层：只管 SQL，不关心 HTTP。"""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def create(self, name: str, owner: str = "") -> dict:
        try:
            cur = self.conn.execute("INSERT INTO projects (name, owner) VALUES (?, ?)", (name, owner))
        except sqlite3.IntegrityError as exc:
            raise ValueError("项目名已存在") from exc
        self.conn.commit()
        return self.get(cur.lastrowid)  # type: ignore[arg-type]

    def get(self, project_id: int) -> dict:
        row = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            raise KeyError(f"项目 {project_id} 不存在")
        return dict(row)

    def list(self) -> list[dict]:
        return [dict(row) for row in self.conn.execute("SELECT * FROM projects ORDER BY id")]

    def rename(self, project_id: int, name: str) -> dict:
        try:
            cur = self.conn.execute("UPDATE projects SET name = ? WHERE id = ?", (name, project_id))
        except sqlite3.IntegrityError as exc:
            raise ValueError("项目名已存在") from exc
        if cur.rowcount == 0:
            raise KeyError(f"项目 {project_id} 不存在")
        self.conn.commit()
        return self.get(project_id)

    def delete(self, project_id: int) -> None:
        cur = self.conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        if cur.rowcount == 0:
            raise KeyError(f"项目 {project_id} 不存在")
        self.conn.commit()


def _name(body: dict | None) -> str:
    name = (body or {}).get("name", "")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name 不能为空")
    return name.strip()


def build_app(repo: ProjectRepo) -> App:
    """服务层：校验参数、把仓储异常翻译成状态码。"""
    app = App()

    @app.get("/health")
    def health(req: Request) -> Response:
        return json_response({"status": "ok", "projects": len(repo.list())})

    @app.get("/projects")
    def list_projects(req: Request) -> Response:
        return json_response({"items": repo.list()})

    @app.post("/projects")
    def create_project(req: Request) -> Response:
        try:
            name = _name(req.body)
        except ValueError as exc:
            return error(400, str(exc))
        try:
            item = repo.create(name, (req.body or {}).get("owner", ""))
        except ValueError as exc:
            return error(409, str(exc))
        return json_response(item, 201)

    @app.get("/projects/{project_id}")
    def get_project(req: Request) -> Response:
        try:
            return json_response(repo.get(int(req.query["project_id"])))
        except (KeyError, ValueError):
            return error(404, "项目不存在")

    @app.patch("/projects/{project_id}")
    def patch_project(req: Request) -> Response:
        try:
            return json_response(repo.rename(int(req.query["project_id"]), _name(req.body)))
        except ValueError as exc:
            return error(409 if "已存在" in str(exc) else 400, str(exc))
        except KeyError:
            return error(404, "项目不存在")

    @app.delete("/projects/{project_id}")
    def delete_project(req: Request) -> Response:
        try:
            repo.delete(int(req.query["project_id"]))
        except KeyError:
            return error(404, "项目不存在")
        return Response(status=204, body=None)

    return app
