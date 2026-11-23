---
name: shenle-device-record
description: Use when the user wants to record UI from a real Android device connected over USB-debugging — drives the local `shenle-device-record` CLI to capture screenshot + uiautomator dump into a timestamped batch under `AI-信息采集/<batch>/<module>/<func>/{img,json}`, optionally with a multimodal LLM writing interface/layout/elements descriptions into the JSON. Trigger phrases include "录一下手机", "设备录制", "截一下 APP", "抓一下安卓", "Android 真机采集", "device record", "capture phone screen", "record app UI".
version: 0.1.0
---

# shenle-device-record

驱动本机 `shenle-device-record` CLI，在**接在电脑上、已开 USB 调试**的真机 Android 上做界面采集。默认走 `serve` 子命令：本地起 HTTP + WebSocket 服务 + 自动用 `npx playwright` 打开 Chromium 录制面板，左侧实时画面，右侧填模块/功能/描述后一键落盘。`record` 子命令是 CLI 一次一截，适合脚本化场景。

**这是有副作用、会弹浏览器、长时间运行的工具**——按下面的 4 步流程走，遇到要用户决策的地方**停下来问**，不要自己猜。

> **不要做的事（任何时候都生效）**
>
> - 不要自己装任何东西（node / adb / chromium / npm 包）——告诉用户怎么装，让用户自己装
> - 不要替用户改 `.env`——给指引让用户写
> - 不要擅自 `kill-server` / `taskkill` 别人的进程——可能影响其他工具
> - 不要假设端口 `8765` 没被占——撞了让用户决定是换端口还是先杀掉现有进程（用户自己杀）
> - 多台设备时不要自己挑——必须停下来问用户
> - 采集期间不要阻塞用户——服务跑起来就挂起，等用户反馈

## 整体流程

```
Step 1: 环境预检（node / adb / npx playwright）
         ↓
Step 2: 确认设备（adb devices -l） + 多设备时让用户选
         ↓
Step 3: 启动 serve（后台 + 浏览器自动弹出）
         ↓
Step 4: 等用户结束 → 报告产物位置 + 下游怎么读
```

---

## Step 1: 环境预检

**目标**：确认 `node` / `adb` / `npx playwright` 都可用。任何一项没有，停下来告诉用户怎么装，**不要自己装**。

### 必跑检查

```bash
node --version         # 应输出 v18+ 的版本号
adb version            # 应有 Android Debug Bridge 字样
npx playwright --version   # 应输出 1.x 或 2.x 版本号
```

> **注意**：这里用的是 Node.js 的 Playwright（`npx playwright`），**不是** Python 的 `python -m playwright`。两者独立下载浏览器到不同目录，互不影响。本机 chromium-1200 是 Python Playwright 的，跟本工具无关，不要套那个 1.57 的版本约束。

### 判定

| 结果 | 怎么办 |
|---|---|
| 三个都有 | 进 Step 2 |
| `node` 找不到 | 提示用户装 Node.js（≥18）：`https://nodejs.org/zh-cn/download`。**不要自动装** |
| `adb` 找不到 | 提示用户装 Android SDK platform-tools，把 `adb.exe` 加到 PATH。**不要自动装** |
| `npx playwright --version` 报错 | 提示用户先跑一次 `npx playwright install chromium`（首次下载约 30s–2min）。不要替用户跑——下载过程可能弹交互 |
| `npx playwright --version` 报浏览器没下 | 提示用户跑 `npx playwright install chromium`（同上） |

### AI 配置（启动前先看一眼 `.env`）

`s serve` 网页里有「AI 分析」复选框，**采集时勾选就启用、不勾就不启用**，不需要 CLI 启动前问。

AI 字段（`interface_desc` / `layout_desc` / `elements_desc`）能不能真写到 JSON，取决于 CLI 的当前目录有没有 `.env`：

```ini
DEVICE_VISION_AI_API_KEY=sk-...
DEVICE_VISION_AI_MODEL=gpt-4o
DEVICE_VISION_AI_BASE_URL=https://api.openai.com/v1   # 可选，默认 OpenAI 官方
```

国内可用火山豆包 / 智谱 / 月之暗面 / 本地 ollama 等兼容端点。

命名约定：用 `DEVICE_VISION_AI_*` 前缀（跟 shenle-web-cli 的 `WEB_AUTOMATION_AI_*` 同构），多工具共用一份 `.env` 时不撞名。

> **⚠️ 注意：这是两层 AI 配置，不要漏配**
>
> `shenle-device-record` 内部截图走的是 midscene（一个独立的第三方 CLI）。**midscene 自己也要 AI 配置**，否则连截图都拿不到，更轮不到 AI 描述界面。常见两个 env 名：
>
> | env 名 | 谁读 | 不配的后果 |
> |---|---|---|
> | `OPENAI_API_KEY` + `MIDSCENE_MODEL_NAME` | midscene | 启动就报 `OPENAI_API_KEY is not set`，整条采集链路挂 |
> | `DEVICE_VISION_AI_API_KEY` + `DEVICE_VISION_AI_MODEL` + `DEVICE_VISION_AI_BASE_URL` | shenle-device-record | 采集照常，JSON 里 `interface_desc` 等三个字段写 `null` |
>
> 两套都要配才能用上 AI 描述功能。midscene 的 env 直接设到 shell 环境变量或写到同份 `.env` 里都行（`shenle-device-record` 不消费这两个名字，不冲突）。

**启动前顺手 ls 一下**（不阻塞流程，只用于决定告诉用户什么）：

```bash
SHENLE_BIN="$(which shenle-device-record)"
ls -la "$(dirname "$SHENLE_BIN")/../.env" 2>/dev/null \
  || ls -la "$(dirname "$SHENLE_BIN")/.env" 2>/dev/null
```

| `.env` 状态 | 启动后告诉用户 |
|---|---|
| 存在 | "AI 分析可用，网页里勾上「AI 分析」复选框即可启用。" |
| 不存在 | "AI 分析未配置（网页里复选框无效）。如需启用请在 shenle-device-record 同级目录写 `.env`（`DEVICE_VISION_AI_API_KEY` + `DEVICE_VISION_AI_MODEL` 必填）。" |

**AI 失败也只是 JSON 三个字段写 null，不影响主流程。**

---

## Step 2: 确认设备

### 跑

```bash
adb devices -l
```

### 输出格式

```
List of devices attached
emulator-5554          device product:sdk_gphone64_x86_64 model:sdk_gphone64_x86_64 device:emu64xa transport_id:1
ABC123XYZ              unauthorized usb:1-2
```

- `device` = 可用
- `unauthorized` = 手机没点「允许 USB 调试」或点了取消
- `offline` = adb 与手机断了

### 按状态分支

#### 没列出任何设备

告诉用户：

> 没检测到安卓设备。请：
> 1. 用 USB 线连手机（模拟器请确保已启动）；
> 2. 手机进入 **设置 → 关于本机**，连点 7 次「版本号」打开「开发者选项」；
> 3. 进入「开发者选项」，**开启 USB 调试**；
> 4. 重插 USB 线，手机弹出「是否允许 USB 调试」对话框 → 点「允许」；
> 5. 让用户自己跑一次 `adb kill-server && adb start-server` 再回来。

让用户做完这几步后重跑 `adb devices -l`。**不要**替用户 kill-server（可能影响别的进程）。

#### 只有一台 `device`

直接用。告诉用户用哪台：

> 检测到 1 台设备：`emulator-5554 (device, sdk_gphone64_x86_64)`。

继续 Step 3，但**把设备序列号记下来**，后面启动命令要传 `--device-id`（空串会被 midscene CLI 解析成 boolean 报错）。

#### 有多台 `device` —— **必须问用户**

**不要自己选**。停下来问：

> 检测到 N 台设备可用：
> 1. `emulator-5554 (device, sdk_gphone64_x86_64)` —— 模拟器
> 2. `ABC123XYZ (device, Pixel_6_Pro)` —— 真机
> 3. `DEF456GHI (device, Pixel_5)` —— 真机
>
> 用哪台？告诉我 serial（`emulator-5554` 这种）或描述（"模拟器"/"Pixel 6"）。

等用户回。记下用户选的序列号。

#### 设备状态是 `unauthorized` 或 `offline`

如果用户**指定的**设备是这个状态：

> 你选的 `ABC123XYZ` 当前是 `unauthorized`：手机没弹出「允许 USB 调试」对话框或点了取消。请：
> - 重插 USB 线，手机会重新弹对话框 → 点「允许」；
> - 或者执行 `adb kill-server && adb start-server` 后重试（让你自己跑，我不替你跑）。

不要自动 kill-server——可能影响别的进程。

---

## Step 3: 启动录制

### 命令

不管用户在 Step 2 选了什么，命令长这样：

```bash
shenle-device-record serve --platform android [-o <输出根目录>] [--device-id <serial>] [--port 8765]
```

- `--platform android`：当前唯一支持的平台
- `--device-id`：**强烈建议传**——空串会让 midscene CLI 解析失败。如果你 Step 2 拿到了 serial，**一定传**
- `-o`：输出根目录。**默认值是当前目录**——问用户要不要改：
  - 默认会落到**当前目录**下的 `AI-信息采集/<时间戳>/`。要换路径吗（比如 `~/Desktop/录制结果`）？
  - 如果用户不改，直接用 `.`
- `--port`：默认 `8765`。除非用户说改，否则不动
- `--no-browser`：跳过自动开 Chromium。**默认不要加**——自动开浏览器是产品核心体验

### 启动方式

服务不会自己退出，要等用户关浏览器。用 **Bash 工具的后台进程能力**（`run_in_background: true`），把命令和启动路径都传好。

```bash
# Windows（Git Bash）：
cd apps/shenle-device-record
shenle-device-record serve --platform android --device-id <serial> > "$TEMP/shenle-serve.log" 2>&1
```

### 验证启动成功

**等几秒**后看服务输出，确认以下三行都打出来了：

```
[shenle-device-record] WebSocket 监听 ws://127.0.0.1:8765/ws
[shenle-device-record] 服务已就绪：http://127.0.0.1:8765/
[shenle-device-record] 已启动 Playwright 浏览器（pid XXXXX）
```

**只要有任何一行没出现**，就是启动失败——看 Playwright 日志（路径会在日志里打出来）：

```
[shenle-device-record] Playwright 输出写到：C:\...\shenle-playwright-<pid>.log
```

把那个路径告诉用户，让用户自己 `cat` 那个日志看具体错误。

### 告诉用户

启动成功后告诉用户：

> 服务起来了，浏览器已打开 `http://127.0.0.1:8765/`。你可以：
> - 左侧看手机实时画面（默认 1 fps，需要时按右侧 `+`/`-` 调）；
> - 切「实时」/「按需」模式（按需模式停推流，需要时点采集才截）；
> - 填右侧「模块」「功能点」「描述」（不填也行，会落到 `未分类/未分类`），点「截图采集」；
> - 勾上「AI 分析」复选框会调用多模态模型把界面描述写到 JSON（依赖 `.env` 配置）；
> - **采集完关浏览器窗口**，服务会自动退出。
>
> 我现在挂起等你。要我期间帮你看什么日志 / 排查什么就喊我。

**然后进入等待状态**——等用户说"采完了 / 关浏览器了 / 出错了"。

#### 备选：`record` 子命令

如果用户**只要 CLI 一次一截**（不开浏览器、不要实时画面），用 `record`：

```bash
shenle-device-record record --platform android --device-id <serial> -o <目录>
```

适合自动化脚本场景，没有页面交互。**不**走本 skill 主流程的 4 步——这是另一个用法。

---

## Step 4: 收尾

### 用户说"采完了 / 关浏览器了"之后

1. 确认服务已退（看刚才的日志最后几行有没有服务退出信息，或进程列表里没有 `node.exe` / `playwright` 进程）。**不要**自己 `taskkill`，让用户确认。
2. 列出产物位置：

```bash
ls -la <输出根目录>/AI-信息采集/<批次号>/
```

3. 给用户一段总结：

> 采集完成。产物在：
> `<输出根目录>/AI-信息采集/<批次号>/未分类/未分类/`
> ├── `img/screenshot_001.png`（截图）
> ├── `img/screenshot_002.png`
> ├── ...
> ├── `json/android_001.json`（界面结构 + 元数据）
> ├── `json/android_002.json`
> └── ...
>
> 同一批次号目录下的所有截图共享一个采集会话（多次采集都落这里）。
> 序号自动递增，不覆盖旧文件。

4. **解释 JSON 结构**——如果用户要让大模型分析：

> 每个 JSON 有 5 个固定字段 + 最多 3 个 AI 字段：
> - `content`（字符串）：uiautomator dump 出来的界面结构 XML（如果工具没抓到是空串——是工具问题不是设备问题）
> - `img`（字符串）：相对路径 `img/screenshot_NNN.png`
> - `module` / `func` / `desc`（字符串）：用户在网页里填的模块、功能点、描述
> - `interface_desc` / `layout_desc` / `elements_desc`（可选）：AI 分析结果。如果工具没启用 AI 这三个字段是 `null`；启用了的话可能是字符串也可能是 `null`（AI 失败）。

5. **告诉用户怎么交给下游**：

> 把这整个 `AI-信息采集/<批次号>/` 目录交给分析程序即可。下游会：
> - 遍历批次下每个 `json/android_NNN.json`；
> - 从 `img` 字段读 PNG 路径，把 PNG 字节流喂给多模态大模型（如果分析需要）；
> - 读 `content` 字段（XML）拿 UI 结构；
> - 读 `module` / `func` / `desc` 字段拿业务说明；
> - 读 AI 三字段（如果有）作为额外上下文。

---

## 常见错误速查

| 现象 | 怎么查 |
|---|---|
| 服务启动但浏览器没出来 | 看 Playwright 日志（路径在启动日志里有）；多半是 Chromium 没下载完（首次跑要等 1–2 分钟） |
| 浏览器出来了但页面是空白 / WebSocket 连不上 | 检查端口是否被占（换 `--port`） |
| 左侧画面是黑色 / 不刷新 | 看服务端 stderr 有没有 `take_screenshot 失败`——多半是 midscene 配置问题（AI 模型环境变量、AI key 错等）；把报错原始输出贴给用户 |
| JSON 里 `content` 是空串 | `uiautomator dump` 在某些 Android 版本会竞态失败（特别是旧 MIUI / ColorOS）；不影响截图，告诉用户这是已知问题 |
| 实时模式下画面不刷新 / 提示"连续失败 N 次" | 服务端 stderr 会有 `midscene 截图失败`，查真因；工具会自动切到按需模式，不阻塞 |
| 用户关浏览器后服务不退 | `Ctrl+C` 强退（让用户自己按，不要替他按） |
| 端口 `8765` 被占 | 加 `--port <其它>`，或问用户要不要先杀掉现有进程（**不替你杀**） |
| 终端中文乱码 | 让用户在当前 `cmd.exe` 跑一次 `chcp 65001` 再跑命令；或者换 Git Bash / Windows Terminal。**只影响终端显示，不影响落盘文件** |
| `npx --yes @midscene/android` 首次跑超慢 | 首次会拉几十 MB 依赖（`sharp` 等），1–2 分钟起步，**不要中途 Ctrl-C**。国内网络可临时走 `npm config set registry https://registry.npmmirror.com` |