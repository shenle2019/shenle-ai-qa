# shenle-web-cli

命令行驱动的浏览器自动化工具（Playwright + CDP）。

- **Phase 1**：`start` / `close` —— 启停一个长生命周期后台浏览器
- **Phase 2**：`navigate` / `screenshot` / `click` / `input` —— 原子操作；
  `click` 与 `input` 走 AI 视觉定位

## 跟 `shenle-web-record` 的关系

`shenle-web-record` 是**录制**（人工在浏览器里点 SNAP，截图 + a11y 落盘）。
`shenle-web-cli` 是**回放**（脚本 / AI 让浏览器自己跑）。两者共用同套
Playwright + chromium 二进制，互不干扰。

## 安装

工程根目录的 `.venv` 已经装了 Playwright 1.57.0（chromium-1200 是本机唯一
能用的二进制）。新工具以可编辑模式装进同一个 venv：

```bash
.venv/Scripts/python.exe -m pip install -e apps/shenle-web-cli
```

激活 venv 后就能全局敲 `shenle-web-cli`：

```bash
shenle-web-cli --version
shenle-web-cli --help
```

## 用法

### 启停浏览器

```bash
shenle-web-cli start [--port 9222] [--headless]
shenle-web-cli close
shenle-web-cli --version
shenle-web-cli --help
shenle-web-cli --debug <command> [...]   # 任意命令加 --debug 看完整堆栈
```

`start` 拉起的是**脱离父进程**的 daemon，父 CLI 命令退出后浏览器
依然常驻；Cookie / 登录态保存在固定的 user-data-dir，下次 `start` 自动复用。

### 原子操作（依赖后台浏览器）

```bash
shenle-web-cli navigate <url>
shenle-web-cli screenshot <path.png>
shenle-web-cli click <description>           [--enhanced "..."] [--screenshot out.png]
shenle-web-cli input <description> <text>    [--enhanced "..."] [--screenshot out.png]
```

输出统一为单行 `[OK] ...` 或 `[FAIL] ...`，exit code 0/1，方便 AI parse。

- `navigate` 自动补 `https://` 前缀；把 viewport 拉到 1440x900。
- `screenshot` 截**当前 viewport**（非整页）。
- `click` / `input` 走 AI 视觉：
  1. 用 Playwright 截当前 viewport → 临时 PNG
  2. base64 → `data:image/png;base64,...` → POST `/v1/chat/completions`
  3. 解析返回的 `{"x":..,"y":..}`（容错掉 markdown / 前缀解释文字）
  4. `page.mouse.click(x, y)`；`input` 再用 `keyboard.insert_text(text)`
     整串填入（中文 / 长字符串都 OK）

### AI 配置

`click` / `input` 需要三个环境变量（从当前目录的 `.env` 自动加载，
真实环境变量优先）：

```bash
WEB_AUTOMATION_AI_API_KEY=sk-xxx
WEB_AUTOMATION_AI_BASE_URL=http://your-llm-gateway/v1
WEB_AUTOMATION_AI_MODEL=your-vision-model-name
```

任意一个缺失会立刻 `[FAIL]`，不会反复重试。

## 端到端验证

```bash
# 1) 拉起后台浏览器（窗口会弹出来）
shenle-web-cli start

# 2) 打开一个网站
shenle-web-cli navigate https://example.com
# → [OK] navigate: https://example.com → title="Example Domain"

# 3) 截图存证
shenle-web-cli screenshot ./shot.png
# → [OK] screenshot: ...\shot.png (1440x900)

# 4) 视觉点击（AI 看到 "IANA" 链接，返回坐标，点它）
shenle-web-cli click "More information..." --screenshot ./after-click.png

# 5) 视觉输入（去一个有搜索框的页面）
shenle-web-cli navigate https://www.baidu.com
shenle-web-cli input "搜索框" "你好，世界"
# → [OK] input "搜索框" "你好，世界": (xxx, yyy)

# 6) 关掉
shenle-web-cli close
```

### 全局状态位置

- Windows : `%LOCALAPPDATA%\shenle-web-cli\`
  - `state.json` — 当前后台浏览器状态
  - `profile\`    — Chromium 持久化 user-data-dir
  - `daemon.log`  — 后台进程日志

## Project layout

```
apps/shenle-web-cli/
├── pyproject.toml
├── README.md
├── .gitignore
└── src/
    └── shenle_web_cli/
        ├── __init__.py       # 版本号
        ├── cli.py            # argparse 入口
        ├── daemon.py         # 后台长驻进程
        ├── state.py          # state.json 读写 + 健康检查 + 杀进程
        ├── errors.py         # CliError 基类 + 子类
        ├── ai.py             # AI 配置 + 多模态 chat/completions
        ├── browser_session.py  # connect_over_cdp 临时连接
        └── commands.py       # navigate / screenshot / click / input 实现
```
