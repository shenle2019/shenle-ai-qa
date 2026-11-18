"""一个只用标准库写成的迷你网站，给 Web 自动化章节当被测试对象。

设计目标：
- 零依赖、零网络：测试跑在本机回环地址上，断网也能过；
- 覆盖真实页面里最常见的几类元素：表单、按钮、列表、动态插入的元素、需要登录才能看的页面；
- 每个元素都带 `data-testid`，方便演示「优先用测试 id 定位」这条实践。

用法::

    from labs._shared.mini_site import serve
    with serve() as base:
        print(base)   # http://127.0.0.1:51234
"""

from __future__ import annotations

import threading
import uuid
from contextlib import contextmanager
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

USERS = {"alice": "secret", "bob": "hunter2"}

LOGIN_PAGE = """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>登录 · 任务清单</title></head>
<body>
  <header><h1>任务清单</h1></header>
  <main>
    <form method="post" action="/login" data-testid="login-form">
      <label for="username">用户名</label>
      <input id="username" name="username" data-testid="username" autocomplete="off">

      <label for="password">密码</label>
      <input id="password" name="password" type="password" data-testid="password">

      <button type="submit" data-testid="login-submit">登录</button>
    </form>
    <p data-testid="error" class="error">__ERROR__</p>
  </main>
</body>
</html>"""

TODO_PAGE = """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>待办 · 任务清单</title></head>
<body>
  <header>
    <h1>待办清单</h1>
    <span data-testid="current-user">__USER__</span>
  </header>
  <main>
    <form method="post" action="/todos" data-testid="add-form">
      <label for="title">新任务</label>
      <input id="title" name="title" data-testid="new-title" autocomplete="off">
      <button type="submit" data-testid="add-submit">添加</button>
    </form>

    <ul data-testid="todo-list">
__ITEMS__
    </ul>

    <button type="button" data-testid="start" onclick="setTimeout(function(){
      var p = document.createElement('p');
      p.setAttribute('data-testid', 'done');
      p.textContent = '异步结果已返回';
      document.getElementById('slow-zone').appendChild(p);
    }, 600)">开始异步任务</button>
    <div id="slow-zone"></div>
  </main>
</body>
</html>"""

ITEM = '      <li data-testid="todo-item">__TITLE__</li>'

SEARCH_PAGE = """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>搜索 · 任务清单</title></head>
<body>
  <header><h1>搜索任务</h1></header>
  <main>
    <form method="get" action="/search" data-testid="search-form">
      <label for="q">关键词</label>
      <input id="q" name="q" value="__QUERY__" data-testid="q" autocomplete="off">
      <button type="submit" data-testid="search-submit">搜索</button>
    </form>
    <p data-testid="result-count">共 __COUNT__ 条</p>
    <ul data-testid="result-list">
__ROWS__
    </ul>
  </main>
</body>
</html>"""

PROFILE_PAGE = """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>个人资料 · 任务清单</title></head>
<body>
  <header>
    <h1>个人资料</h1>
    <span data-testid="current-user">__USER__</span>
  </header>
  <main>
    <img data-testid="avatar" src="/avatar.svg" alt="用户头像" width="64" height="64">
    <section data-testid="card" aria-label="账号信息">
      <h2>账号信息</h2>
      <dl>
        <dt>用户名</dt><dd data-testid="profile-name">__USER__</dd>
        <dt>角色</dt><dd data-testid="profile-role">测试工程师</dd>
      </dl>
    </section>
    <nav aria-label="主导航">
      <a href="/todos" data-testid="nav-todos">待办</a>
      <a href="/table" data-testid="nav-table">表格</a>
    </nav>
  </main>
</body>
</html>"""

TABLE_PAGE = """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>任务表格 · 任务清单</title></head>
<body>
  <header><h1>任务表格</h1></header>
  <main>
    <table data-testid="task-table">
      <caption>当前全部任务</caption>
      <thead><tr><th>序号</th><th>标题</th><th>选择</th></tr></thead>
      <tbody>
__ROWS__
      </tbody>
    </table>
  </main>
</body>
</html>"""


class _State:
    def __init__(self) -> None:
        self.sessions: dict[str, str] = {}
        self.todos: list[str] = ["写测试", "跑通构建"]
        self.lock = threading.Lock()

    def reset(self) -> None:
        with self.lock:
            self.sessions.clear()
            self.todos = ["写测试", "跑通构建"]


def _html(body: str, status: int = 200, headers: dict[str, str] | None = None) -> tuple:
    return status, {"Content-Type": "text/html; charset=utf-8", **(headers or {})}, body.encode("utf-8")


def _make_handler(state: _State, port_holder: dict):
    class Handler(BaseHTTPRequestHandler):
        server_version = "MiniSite/1.0"

        def log_message(self, *args) -> None:  # 静音，避免污染测试输出
            return

        # --- 工具 ---
        def _send(self, status: int, headers: dict[str, str], body: bytes) -> None:
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _redirect(self, location: str, headers: dict[str, str] | None = None) -> None:
            self._send(302, {"Location": location, **(headers or {})}, b"")

        def _user(self) -> str | None:
            raw = self.headers.get("Cookie", "")
            if not raw:
                return None
            jar = SimpleCookie()
            jar.load(raw)
            sid = jar.get("sid")
            if not sid:
                return None
            return state.sessions.get(sid.value)

        def _read_form(self) -> dict[str, str]:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length).decode("utf-8")
            return {k: v[0] for k, v in parse_qs(raw).items()}

        # --- 路由 ---
        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?")[0]
            if path == "/":
                self._redirect("/login")
                return
            if path == "/login":
                self._send(*_html(LOGIN_PAGE.replace("__ERROR__", "")))
                return
            if path == "/todos":
                user = self._user()
                if not user:
                    self._redirect("/login")
                    return
                items = "\n".join(ITEM.replace("__TITLE__", t) for t in state.todos)
                self._send(*_html(TODO_PAGE.replace("__USER__", user).replace("__ITEMS__", items)))
                return
            if path == "/search":
                query = parse_qs(self.path.split("?", 1)[1]).get("q", [""])[0] if "?" in self.path else ""
                hits = [t for t in state.todos if query.lower() in t.lower()] if query else []
                rows = "\n".join(
                    f'      <li data-testid="result-item">{t}</li>' for t in hits
                ) or '      <li data-testid="empty">没有匹配结果</li>'
                body = SEARCH_PAGE.replace("__QUERY__", query).replace("__ROWS__", rows).replace("__COUNT__", str(len(hits)))
                self._send(*_html(body))
                return
            if path == "/profile":
                user = self._user()
                if not user:
                    self._redirect("/login")
                    return
                self._send(*_html(PROFILE_PAGE.replace("__USER__", user)))
                return
            if path == "/table":
                user = self._user()
                if not user:
                    self._redirect("/login")
                    return
                rows = "\n".join(
                    f'      <tr data-testid="row"><td>{i}</td><td data-testid="cell-title">{t}</td>'
                    f'<td><input type="checkbox" data-testid="pick" aria-label="选择 {t}"></td></tr>'
                    for i, t in enumerate(state.todos, start=1)
                )
                self._send(*_html(TABLE_PAGE.replace("__ROWS__", rows)))
                return
            if path == "/avatar.svg":
                svg = (
                    '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">'
                    '<rect width="64" height="64" fill="#a3e635"/>'
                    '<circle cx="32" cy="24" r="12" fill="#3f6212"/>'
                    '<rect x="12" y="40" width="40" height="18" rx="9" fill="#3f6212"/></svg>'
                )
                self._send(200, {"Content-Type": "image/svg+xml; charset=utf-8"}, svg.encode("utf-8"))
                return
            if path == "/health":
                self._send(*_html("ok"))
                return
            self._send(*_html("<h1>404</h1>", status=404))

        def do_POST(self) -> None:  # noqa: N802
            path = self.path.split("?")[0]
            form = self._read_form()
            if path == "/login":
                user = form.get("username", "")
                password = form.get("password", "")
                if USERS.get(user) != password:
                    self._send(*_html(LOGIN_PAGE.replace("__ERROR__", "用户名或密码错误"), status=401))
                    return
                sid = uuid.uuid4().hex
                state.sessions[sid] = user
                self._redirect("/todos", {"Set-Cookie": f"sid={sid}; Path=/; HttpOnly"})
                return
            if path == "/todos":
                user = self._user()
                if not user:
                    self._redirect("/login")
                    return
                title = (form.get("title") or "").strip()
                if title:
                    with state.lock:
                        state.todos.append(title)
                self._redirect("/todos")
                return
            self._send(*_html("<h1>404</h1>", status=404))

    return Handler


@contextmanager
def serve(port: int = 0):
    """起一个后台线程跑迷你站，退出上下文时自动关掉。"""
    state = _State()
    holder: dict = {}
    handler = _make_handler(state, holder)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    holder["port"] = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{holder['port']}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)
