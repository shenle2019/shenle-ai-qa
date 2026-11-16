"""业务语义层：用例只跟这里打交道。"""

from __future__ import annotations

import csv
import io
from pathlib import Path

from fw_client import HttpClient


class Users:
    def __init__(self, client: HttpClient):
        self.c = client

    def login(self, username: str = "alice", password: str = "secret") -> str:
        token = self.c.post("/api/login", json={"username": username, "password": password}).json()["token"]
        self.c.headers["Authorization"] = f"Bearer {token}"
        return token

    def list(self, page: int = 1, size: int = 10) -> dict:
        return self.c.get("/api/users", params={"page": page, "size": size}).json()

    def create(self, name: str, role: str = "tester") -> dict:
        return self.c.post("/api/users", json={"name": name, "role": role}).json()

    def delete(self, uid: int) -> None:
        self.c.delete(f"/api/users/{uid}")


class Files:
    def __init__(self, client: HttpClient):
        self.c = client

    def upload(self, name: str, payload: bytes, content_type: str = "text/plain") -> dict:
        return self.c.post("/api/upload", files={"file": (name, payload, content_type)}).json()

    def download(self, name: str) -> bytes:
        return self.c.get(f"/api/files/{name}").content


class Batch:
    """CSV 批量导入：逐条创建，统计成功/失败。"""

    def __init__(self, users: Users):
        self.users = users

    def import_csv(self, path: Path) -> dict:
        ok, failed = 0, []
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                try:
                    self.users.create(row["name"], row.get("role") or "tester")
                    ok += 1
                except Exception as exc:  # noqa: BLE001 - 批量导入要吞掉单条失败
                    failed.append({"name": row.get("name"), "error": str(exc)[:80]})
        return {"ok": ok, "failed": failed}

    def export_csv(self, rows: list[dict]) -> str:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()) if rows else ["name"])
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue()
