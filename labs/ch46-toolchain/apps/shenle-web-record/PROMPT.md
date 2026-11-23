# shenle-web-record 交互式录制器 — 扩展提示词

> 本文档是从实际训练过程中提炼出的"成品级"提示词，可直接用于 SKILL 工具调用或交给他人/未来的 Claude 执行。它在原始需求之上补充了 12 个隐藏约束，避免重蹈训练时踩过的坑。

---

## 任务：优化 shenle_web_record 工具为交互式 headed-browser 录制器

## 核心目标

通过 `record <URL>` 命令打开 headed Chromium 浏览器，页面右下角注入一个浮动 SNAP 按钮。每次点击按钮执行一次采集：

1. 截图保存到 `<ROOT>/web/AI-信息采集/<批次号>/img/screenshot_<NNN>.png`
2. 采集 DOM 数据保存到 `json/dom_<NNN>.json`，结构为：

   ```json
   {"content": "<ARIA a11y 快照字符串>", "img": "img/screenshot_NNN.png"}
   ```

3. 序号 3 位补零（`001`, `002`, …），从 `1` 递增，多次点击同批次内递增。
4. 批次号 `YYYYMMDD-HHmmss`，**会话启动时生成一次**，关闭浏览器即结束会话。
5. 同秒重新启动 → 复用目录 + 从 `max+1` 续号（**绝不覆盖历史**）。

---

## 关键技术约束（踩坑后必须遵守）

### 1. 环境层 — 禁止 `pip install -e .`

若项目路径含中文字符，Python 3.11 的 `site.py` 用 `gbk` 解码 `.pth` 文件会失败，并写入一个 UTF-8 编码的 `.pth`，导致**所有 Python 调用崩溃**。

**对策**：
- 禁止 `pip install -e .`，改用 `PYTHONPATH=.` 注入
- README / 安装文档需明确此警告
- 单元测试用 `conftest.py` 把项目根加入 `sys.path`，无需安装

### 2. Playwright API 层（最大坑）

#### 2.1 必须用 `async_api`，**禁止 sync API**

`expose_function` 回调里若再调 `page.evaluate` / `page.screenshot`，**sync API 会死锁**（事件循环互锁等待）。即使最简单的 `page.evaluate('document.title')` 也死锁。

**对策**：`RecorderSession.run()` 和 `_on_snap()` 都用 `async def`。

#### 2.2 Browser 没有 `wait_for_event`

无论 sync 还是 async API，`Browser` 对象都没有 `wait_for_event` 方法。

**正确做法**：

```python
import asyncio
disconnected = asyncio.Event()
browser.on("disconnected", lambda _b: disconnected.set())
await disconnected.wait()
```

#### 2.3 a11y 入口是 `page.aria_snapshot()`

- Python async API 的 a11y 方法**只有** `page.aria_snapshot()`（不是 `page.accessibility.snapshot()`，那是 Node.js 的）
- 返回**字符串**（playwright-cli `snapshot` 子命令那种 YAML 格式），不是 dict

### 3. snap_button.js 层 — DOMContentLoaded 兜底

**`add_init_script` 在 chromium 进程刚启动时执行，早于 `document.documentElement` 创建**。此时 `documentElement` 是 `null`，任何 `appendChild` 会静默失败。

**正确写法**：

```js
(function () {
  var BTN_ID = "__shenle_snap_btn__";

  function build() {
    if (document.getElementById(BTN_ID)) return;  // 已存在
    if (!document.documentElement) return false;  // 还没准备好
    // ... 创建 style + button ...
    return true;
  }

  if (!build()) {
    document.addEventListener("DOMContentLoaded", build, { once: true });
  }
})();
```

**按钮 id 必须固定为 `__shenle_snap_btn__`**（Python 端 `evaluate` 隐藏/恢复按钮时依赖）。

**点击事件调 `window.__shenle_snap__()`**（对应 Python 端 `expose_function("__shenle_snap__", ...)`）。

### 4. 序号与状态机层（off-by-one 高发区）

- `next_seq(batch_dir)` 返回"下一个可用序号"（空目录 → `1`，有 max → `max+1`）
- `_on_snap` 推进规则：

  ```python
  new_seq = self._seq                                # 用现值
  seq_str = f"{new_seq:03d}"
  img_path = batch_dir / f"screenshot_{seq_str}.png"
  json_path = batch_dir / f"dom_{seq_str}.json"
  try:
      await page.evaluate(...hide button...)
      await page.screenshot(path=str(img_path), full_page=False)
      tree = await page.aria_snapshot()
      await page.evaluate(...restore button...)
  except Exception as exc:
      return {"ok": False, "error": str(exc)}        # 失败：self._seq 不动

  json_path.write_text(json.dumps(
      build_dom_payload(tree, f"img/screenshot_{seq_str}.png"),
      ensure_ascii=False, indent=2,
  ), encoding="utf-8")
  self._seq = new_seq + 1                             # 成功：才推进
  return {"ok": True, "seq": seq_str}
  ```

**关键不变量**：
- 失败时 `self._seq` 不变
- 推进 `self._seq` **必须在 try 块外、且仅在写文件成功后**

### 5. 错误处理层

| 场景 | 行为 |
|---|---|
| `goto` 失败 / 超时 | **不退出**，打印 stderr 后继续 `wait_for_event`，浏览器保持开，已采集的不丢 |
| `browser.launch` 失败 | 检测异常信息含 `"Executable doesn't exist"` / `"browser was not found"` / `"chromium"`，附加 `\n  → run: playwright install chromium` 提示 |
| 截图 / DOM 写入失败 | 序号不递增；按钮变 `⚠ ERR`；用户可再点重试 |
| 浏览器被关闭 | 自然结束；CLI 打印批次目录与采集数 |
| 同秒重启 | 复用目录 + 从 max+1 续号 |

---

## CLI 接口

```
shenle-web-record record <URL> [-o ROOT]
```

- `URL` 必填
- `-o / --output ROOT`：批次根目录；最终路径 `<ROOT>/web/AI-信息采集/<批次号>/`，默认 `cwd`
- `--help` / `--version` 正常
- 入口：`asyncio.run(run_session(url, output))`

---

## 文件结构

```
shenle_web_record/
├── __init__.py
├── __main__.py
├── cli.py                  # argparse + asyncio.run dispatch
├── session.py              # RecorderSession (async)
├── paths.py                # generate_batch_id / make_batch_dir / next_seq / build_dom_payload
└── assets/
    └── snap_button.js      # 注入脚本（含 DOMContentLoaded 兜底）
tests/
├── conftest.py             # sys.path 注入
├── test_batch_id_format.py
├── test_paths.py
├── test_next_seq.py
├── test_dom_payload.py
├── test_cli_parser.py
├── test_session_construction.py
└── test_on_snap.py         # 用 AsyncMock + asyncio.run(s._on_snap())
```

---

## 测试陷阱

### 6.1 `monkeypatch.setattr("module.datetime", datetime)` 是 no-op

`datetime` 是类，把同一个类赋给自己没有任何效果。**正确做法**：

```python
class FakeDatetime:
    @classmethod
    def now(cls):
        return fake_datetime

monkeypatch.setattr(module_obj, "datetime", FakeDatetime)
```

### 6.2 MagicMock 不会真写文件

若测试断言 `png.exists()`，Mock 默认不创建任何文件。**必须让 mock 写出真实空文件**：

```python
s._page.screenshot.side_effect = lambda path, **kw: Path(path).write_bytes(b"")
```

### 6.3 AsyncMock + `asyncio.run` 包同步测试

由于 `_on_snap` 是 `async`，同步测试需要：

```python
import asyncio
from unittest.mock import AsyncMock

def test_happy_path(tmp_path):
    s._page = AsyncMock()  # 不是 MagicMock
    result = asyncio.run(s._on_snap())
    ...
```

### 6.4 RED 阶段可能"假 RED"

新测试的断言可能被现有代码意外满足（例如 parser 默认值测试）。这**不是 implementer 的错**，是 brief 的瑕疵。继续推进即可。

---

## 12 个扩展点速查

| # | 来源 | 扩展点 |
|---|---|---|
| 1 | 需求歧义 | 批次号时机（启动一次 vs 每次点击） |
| 2 | 需求歧义 | DOM 采集内容（outerHTML vs 结构化 a11y 快照） |
| 3 | 需求歧义 | `web/AI-信息采集/` 相对路径（cwd vs 项目根） |
| 4 | 需求歧义 | 截图范围（视口 vs 整页） |
| 5 | 环境陷阱 | 中文路径 + Python 3.11 + `pip install -e .` 灾难 |
| 6 | API 陷阱 | **Playwright sync API 在 expose_function 回调里死锁**（最大坑） |
| 7 | API 陷阱 | Browser 没有 `wait_for_event`，需 `Event` + `on("disconnected")` |
| 8 | API 陷阱 | a11y 入口是 `aria_snapshot()`，返回字符串 |
| 9 | 时序陷阱 | `add_init_script` 时 `documentElement` 是 `null`，需 DCL 兜底 |
| 10 | 状态机 | off-by-one：失败不递增、成功后才推进 `_seq` |
| 11 | 规格 | goto 失败不退出；launch 失败给 install 提示 |
| 12 | 测试 | `monkeypatch` no-op、`AsyncMock` + `asyncio.run`、`side_effect` 真写文件 |

---

## 使用方式

把本文档作为 SKILL 提示词交给 Claude（或团队成员），要求实现：

> "请按 [PROMPT.md](../../PROMPT.md) 的完整约束实现 apps/shenle-web-record 工具，
> 涵盖核心目标、所有关键技术约束、CLI 接口、文件结构、测试陷阱。"

执行流程推荐：
1. **Brainstorm** — 让 Claude 与你逐项澄清需求歧义点（条目 1-4）
2. **Plan** — 用 writing-plans 输出实施计划（含每个 Task 的测试代码）
3. **Execute** — 用 subagent-driven-development 逐 Task 派发 + 两阶段 review
4. **Verify** — 完整测试套件 + 端到端真实跑（headless 启动 + 程序触发 click + 验证文件）

执行环境前提：项目根路径**不含中文字符**（否则需先移动项目或升级 Python 3.12+）。