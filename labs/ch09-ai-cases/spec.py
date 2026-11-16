"""第 9 章用的接口契约（OpenAPI 的一个很小的子集）。

真实项目里这份东西来自 ``/openapi.json``，这里手写一份，好让实验不依赖外部服务。
"""

from __future__ import annotations

SPEC: dict = {
    "title": "MiniSUT",
    "base_url": "http://127.0.0.1:8010",
    "auth": {"type": "bearer", "header": "Authorization", "expires_in": 3600},
    "endpoints": [
        {
            "method": "POST",
            "path": "/api/login",
            "summary": "登录换 token",
            "auth": False,
            "params": [
                {"name": "username", "in": "body", "type": "string", "required": True, "max_length": 32},
                {"name": "password", "in": "body", "type": "string", "required": True, "max_length": 64},
            ],
            "responses": {200: ["token", "expires_in"], 401: ["error"], 422: ["error", "message"]},
            "rules": ["口令错误返回 401，不区分「用户不存在」与「密码错误」"],
        },
        {
            "method": "GET",
            "path": "/api/users",
            "summary": "用户列表（分页）",
            "auth": True,
            "params": [
                {"name": "page", "in": "query", "type": "int", "required": False, "min": 1, "default": 1},
                {"name": "size", "in": "query", "type": "int", "required": False, "min": 1, "max": 100, "default": 10},
            ],
            "responses": {200: ["total", "page", "size", "items"], 401: ["error"], 422: ["error", "message"]},
            "rules": ["size 上限 100", "items 里每个元素含 id/name/role"],
        },
        {
            "method": "POST",
            "path": "/api/users",
            "summary": "创建用户",
            "auth": False,
            "params": [
                {"name": "name", "in": "body", "type": "string", "required": True, "max_length": 32},
                {"name": "role", "in": "body", "type": "enum", "values": ["admin", "tester", "viewer"], "default": "tester"},
                {"name": "email", "in": "body", "type": "string", "required": False, "format": "email"},
            ],
            "responses": {201: ["id", "name", "role"], 409: ["error"], 422: ["error", "message"]},
            "rules": ["name 唯一，重名返回 409", "成功要带 Location 头"],
        },
    ],
}

DIMENSIONS = ["参数", "位置", "鉴权", "状态", "幂等", "数据量", "兼容"]
