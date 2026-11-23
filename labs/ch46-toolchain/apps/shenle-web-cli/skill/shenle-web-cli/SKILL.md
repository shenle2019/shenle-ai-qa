---
name: shenle-web-cli
description: 通过 shenle-web-cli CLI 驱动 Chromium 跑网页自动化。点击 / 输入 / 截图 / 滚动 / 区域描述 / 坐标操作 / 批量，AI 视觉定位（0-1000 归一化坐标）。
---

# shenle-web-cli

## 触发词
- "用 shenle-web-cli 跑这个流程"
- "AI 点这个按钮 / AI 在这个输入框里输入"
- "截一下当前页面 / 自动截图取证"
- "点击 '提交' 按钮（按自然语言描述定位）"
- "滚动到列表底部"
- "断言当前 URL / 标题"
- "跑一轮回归"

## 前置
1. 项目装好：`pip install -e apps/shenle-web-cli`（或项目 venv 已含）
2. 当前 CWD 下有 `.env` 且包含：
   - `WEB_AUTOMATION_AI_API_KEY`
   - `WEB_AUTOMATION_AI_BASE_URL`
   - `WEB_AUTOMATION_AI_MODEL`（必须是视觉模型，例如 `qwen-vl-plus` / `qwen-vl-max` / `gpt-4o`）

## .env 加载行为（**关键**，避免踩坑）

**每次 `click` / `input` / `get` / `batch` / `scroll --region` 都自动从 CWD/.env 重新加载**（不需要重启浏览器 daemon）。
→ 改完 `.env` 直接再跑 click 即可生效，**不要**先 close+start。

**`start` 时强制把 CWD/.env 的变量同步到 daemon 子进程环境变量**（用 `dotenv_values` 读 + `subprocess.Popen(env=...)` 注入）。
→ 真实 shell 环境变量优先于 .env。
→ 这样 daemon 进程拿到的 env 是 start 时确定的那一份，后续切目录不影响 daemon。

**`click-at` / `input-at` / `swipe-to` / `navigate` / `screenshot` / `url` / `title` / `scroll`（无 `--region`）不需要 AI 配置**，不读 .env。

## 核心命令
```
shenle-web-cli start [--port 9222] [--headless]    # 启后台浏览器（per-port 独立 user_data/）
shenle-web-cli close [--port PORT]                  # 关闭浏览器；不带 --port 关所有
shenle-web-cli navigate <url>                       # 打开网页，viewport=1440x900
shenle-web-cli screenshot <path> [--format png|jpeg|auto]
shenle-web-cli click "<元素描述>" [--enhanced "补充描述"] [--screenshot out.png]
shenle-web-cli input "<输入框描述>" "<文本>" [--screenshot out.png]
shenle-web-cli scroll up|down|left|right [-c N] [--region "区域描述"] [--screenshot out.png]
shenle-web-cli get "<区域描述>"                       # AI 视觉描述，按 ## 布局 / ## 图标 / ## 文字 / ## 介绍 四节输出
shenle-web-cli url [--format json]
shenle-web-cli title [--format json]
shenle-web-cli batch click "登录" input "用户名::admin" click "提交" [--debug]
shenle-web-cli click-at <x> <y>                       # 无 AI，直接点击像素坐标
shenle-web-cli input-at <x> <y> "<文本>"              # 无 AI
shenle-web-cli swipe-to <x1> <y1> <x2> <y2>          # 无 AI，模拟拖拽
```

## 坐标系
- **AI 视觉命令返回 0-1000 归一化坐标**，工具自动换算到当前 viewport 像素
- 截图走 JPEG q=80（~3x 小于 PNG），加快 AI 推理
- `batch`：一次截图 + 一次 AI 识别 N 个元素，按顺序执行；比单条 click+input 快很多

## 输出格式
- 所有命令统一单行 `[OK] ...` 或 `[FAIL] ...`，exit 0/1
- `get` 的状态行打 stderr，内容打 stdout（方便脚本 capture）
- `--debug` 会保存带红框的标注图到 `shenle-debug-<cmd>-<ms>.png`

## 常见问题
| 报错 | 原因 | 修复 |
|------|------|------|
| `[FAIL] click: AI 服务不可达 (base_url)` | CWD/.env 的 BASE_URL 不可达 | 检查 `curl <BASE_URL>/v1/models` 通不通；改 .env 后直接再跑 click（无需重启） |
| `未连接到当前设备，请先运行 shenle-web-cli start` | daemon 没起 / 已关 | 跑 `start`；如已起，`close` 再 `start` |
| `[shenle] 浏览器已启动` 后 click 仍找不到元素 | 页面没加载完 / 描述不准 | 加 `navigate` 等页面加载；用 `--enhanced` 补充描述；`get` 先看页面长啥样 |
| `PortInUse` | 9222 被旧 daemon 占 | `shenle-web-cli close` 关掉再 `start`；或换 `--port` |
| `headless` 模式下 click 视觉错位 | 视口大小影响截图 | 工具强制 viewport=1440x900，通常无碍；如跑偏就 `--no-headless` 看真实页面 |

## 关联
- 视觉模型选型 + 坐标换算原理 → 参考 [ai.py](../../src/shenle_web_cli/ai.py)
- 浏览器生命周期 / state.json → [daemon.py](../../src/shenle_web_cli/daemon.py), [state.py](../../src/shenle_web_cli/state.py)
- 同类录制工具 → [shenle-web-record](../../../../apps/shenle-web-record)
