---
name: shenle-android-cli
description: 通过 shenle-android-cli CLI 驱动 adb 跑 Android 设备自动化。典型触发词：「用 shenle-android-cli 跑这个流程」「AI 点这个按钮」「自动点击登录按钮」「AI 在搜索框里输入」「截一下当前屏幕」「启动 App」「滑动列表」「长按」「冷启动测试」「force-stop」「自动化执行回归」「按自然语言描述定位元素」。本技能封装 `shenle-android-cli` CLI（adb shell input），核心命令分五类：①启动/状态 devices / launch / start / close / stop / current-app / appinfo；②截图 + AI 视觉 click / input / longpress / batch / get / swipe --region / screenshot（AI 返回 0-1000 归一化坐标，工具换算成像素 tap）；③纯坐标 click 改走 swipe-to / zoom / pinch / swipe（无 AI）；④系统按键 keyevent / recents / notifications / dump-ui / shell；⑤取证 get 输出四节描述。AI 命令依赖 3 个环境变量（`ANDROID_AI_API_KEY` / `ANDROID_AI_BASE_URL` / `ANDROID_AI_MODEL`），缺失立刻 `[FAIL]` 不重试。中文输入走 Android 剪贴板（`cmd clipboard set-primary-clip`），不支持的 ROM 报错让用户装 ADBKeyboard。统一输出单行 `[OK] ...` 或 `[FAIL] ...` + exit 0/1。
allowed-tools: Bash(shenle-android-cli:*) Bash(python:*)
---

# shenle-android-cli

命令行驱动的 Android UI 自动化工具（adb shell input）。AI 按自然语言调用底层 CLI，无需 selector / ref / xpath。

## Quick start

```bash
# 1) 看设备
shenle-android-cli devices
# → emulator-5554   device
# → 12345678        device

# 2) 启动一个 App（activity 可省，默认走 monkey 找 launcher）
shenle-android-cli launch com.android.settings
# → [OK] launch: com.android.settings/.Settings → Events injected: 1

# 3) 截图存证
shenle-android-cli screenshot ./shot.png
# → [OK] screenshot: ...\shot.png (1080x2400) [png]

# 4) AI 视觉定位 + 点击
shenle-android-cli click "搜索按钮" --screenshot ./after-click.png
# → [OK] click "搜索按钮": (720, 230); shot=...ms ai=...ms total=...ms; post=...\after-click.png

# 5) AI 视觉定位输入框 + 输入文本（中文 OK）
shenle-android-cli input "搜索框" "你好世界"
# → [OK] input "搜索框" "你好世界": (720, 230); shot=...ms ai=...ms type=...ms total=...ms

# 6) 回到桌面（Home 键，进程保留；冷启动测试用 `stop`）
shenle-android-cli close
```

## Lifecycle

```bash
shenle-android-cli --version
shenle-android-cli --help

shenle-android-cli start [-s SERIAL]
# 选定目标设备并打印选中信息；不持久化 session，下次还会重新跑 `adb devices -l`

shenle-android-cli close                       # Home 键回到桌面（App 进程保留）
shenle-android-cli stop <pkg>                  # am force-stop，杀进程（冷启动测试用）

shenle-android-cli <任何命令> [-s SERIAL] [--debug]
# -s / --serial：指定设备序列号（多设备场景下避免被自动选错）
# --debug：AI 类命令保存「红框标注图」到 cwd；内部异常打印完整堆栈
```

> **Phase 1 不持久化"当前选中的设备"**：多设备场景下要么每条命令都显式 `-s`，要么按 adb 列出顺序把目标设备排第一。

## 设备选择规则（Phase 1）

每条需要设备的命令独立跑 `adb devices -l`，按以下规则选定：

1. 用户显式传 `-s SERIAL`：精确匹配；状态非 `device` 时给出友好提示
2. 用户没传：取列表里第一台 `state == "device"` 的设备

后续会引入 session 持久化（类似 shenle-web-cli 的 state.json）。

## Commands

### 启动 / 状态

```bash
shenle-android-cli devices
# 按状态分组列出 adb 看得到的所有设备

shenle-android-cli start [-s SERIAL]
# 选定目标设备并校验；打印选中信息

shenle-android-cli launch <pkg> [activity]
# 启动 App；activity 可省，省略则用 monkey 找 launcher

shenle-android-cli close
# 按 Home 键回到桌面（进程保留）

shenle-android-cli stop <pkg>
# am force-stop —— 杀进程（**冷启动测试用**）

shenle-android-cli current-app [--format json]
# 当前前台 App；默认 text 输出 pkg/activity
# --format json 输出 {"package": ..., "activity": ...}

shenle-android-cli appinfo <pkg>
# dumpsys package —— dumpsys 输出走 stdout，[OK] 走 stderr 方便 pipe
```

### 截图 + AI 视觉定位（自然语言描述，无需 selector / ref / xpath）

> **必须配 3 个环境变量**（缺一立刻 `[FAIL]`，不重试）：
>
> ```bash
> ANDROID_AI_API_KEY=sk-xxx
> ANDROID_AI_BASE_URL=https://your-llm-gateway/v1
> ANDROID_AI_MODEL=your-vision-model-name
> ```
>
> 三个从当前目录 `.env` 自动加载；真实环境变量优先。

```bash
shenle-android-cli screenshot <path.png> [--format png|jpeg|auto] [--quality 85]
# 截当前屏幕到文件
# --format auto 时按扩展名推断；JPEG 质量 1-100
# → [OK] screenshot: <path> (<w>x<h>) [<format>]

shenle-android-cli click "<元素描述>" [--screenshot out.png]
shenle-android-cli click "登录按钮"
shenle-android-cli click "登录按钮" --screenshot ./after.png     # 操作后追加一张截图取证
# → [OK] click "登录按钮": (720, 230); shot=...ms ai=...ms total=...ms
# → [OK] click "登录按钮": (720, 230); shot=...ms ai=...ms total=...ms; post=...\after.png

shenle-android-cli input "<输入框描述>" "<文本>" [--screenshot out.png]
shenle-android-cli input "搜索框" "你好世界"                       # 中文 OK（走剪贴板）
shenle-android-cli input "用户名" "admin"
# → [OK] input "搜索框" "你好世界": (720, 230); shot=...ms ai=...ms type=...ms total=...ms

shenle-android-cli longpress "<元素描述>" [--duration 1500]
# AI 视觉定位 + 在中心点长按 duration ms（默认 1500）

shenle-android-cli batch <op> <args> [<op> <args> ...] [--debug] [--screenshot out.png]
# 一次截图 + 一次 AI 批量识别多个元素 + 按顺序执行。比串行 click/input 快很多
# 支持：click / input / click-at / input-at / longpress
# input 格式：input "<描述>::<文本>"（描述和文本用 :: 分隔）
# → [OK] batch: 3/3 ops total=...ms shot=...ms ai=...ms ops=...ms

shenle-android-cli swipe <dir> [-c N] [--region "区域描述"] [--distance 0.5] [--screenshot out.png]
# 按方向滑动（整屏 / 区域内）
# dir: up | down | left | right
# -c N：连续 N 次
# --region：AI 视觉定位区域，只在区域内滑（需要 AI 配置）
# --distance：滑动距离占屏幕宽/高的比例，默认 0.5

shenle-android-cli get "<区域描述>" [--screenshot out.png]
# AI 视觉描述页面区域，**按 ## 布局 / ## 图标 / ## 文字 / ## 介绍 四节输出**
# 状态行 ([OK] / [FAIL]) 打 stderr，正文打 stdout —— 脚本可直接 capture 正文
```

### 纯坐标（无 AI）

> 用不到，必须知道精确像素位置时用。一般优先用 AI 命令。

```bash
shenle-android-cli swipe-to <x1> <y1> <x2> <y2> [--duration 300]
# 显式坐标滑动（精确定位场景）
# → [OK] swipe-to: (x1,y1)→(x2,y2); duration=300ms; swipe=...ms

shenle-android-cli zoom <x> <y> --scale 2.0 [--duration 300]
# 双指放大（两个 adb input swipe 并行模拟；部分机型可能识别为两次单指）

shenle-android-cli pinch <x> <y> --scale 0.5 [--duration 300]
# 双指缩小（同 zoom 实现）

shenle-android-cli click-at <x> <y>            # 通过 batch click-at 使用
shenle-android-cli input-at <x> <y> "<文本>"   # 通过 batch input-at 使用
# 注：当前 CLI 顶层没有 click-at / input-at，但 batch 支持这两个 op（见下）
```

### ⚠️ WheelPicker / 省市区地址选择器（强制 — 必读）

> **物流 / 货运 / 收货地址类 App 大量用 iOS-style 三列 WheelPicker（省/市/区）。这种 picker 是必踩坑，必须按下面规则操作：**

#### 错误做法（**全部无效**，会卡住测试）

```bash
# ❌ 1. 用 swipe up/down 整屏滑——picker 不会滚
shenle-android-cli swipe up -c 5
shenle-android-cli swipe down -c 5

# ❌ 2. duration 太小（< 500ms）—— picker 当成 fling 直接吞掉事件，页面纹丝不动
shenle-android-cli swipe-to 240 2200 240 1500 --duration 50

# ❌ 3. 起点在 picker 区域外（如 y < picker_top）——事件落在标题栏上
shenle-android-cli swipe-to 240 1500 240 2400   # y=1500 可能已在 picker 上方

# ❌ 4. 想用 click / input 选中某项 —— picker 不能 tap，要靠滚
shenle-android-cli shell input tap 240 1900      # 不触发选中也不滚
shenle-android-cli click "湖南省"
```

#### 正确做法（**唯一有效**）

```bash
# ✅ 慢速拖动（duration 800~1500ms，distance 700~1000px，起点终点都在 picker 内）
shenle-android-cli swipe-to <picker_center_x> <picker_top+100> <picker_center_x> <picker_bottom-100> --duration 1000

# ✅ 先 dump-ui 拿三列 bounds（picker 把屏宽三等分）
shenle-android-cli dump-ui ./ui.xml
# 找 id_province / id_city / id_district —— center_x = (left+right)/2
# 纵向范围一般在 y=1595~2484，center_y ≈ 2040

# ✅ 大幅慢滑过冲 → 再小步回滚精确到位（80px ≈ 滚 1 项）
shenle-android-cli swipe-to 240 1700 240 2420 --duration 1200   # 大幅过冲
shenle-android-cli screenshot ./check.png
shenle-android-cli swipe-to 240 1700 240 1780 --duration 800    # 80px 小步回滚
shenle-android-cli screenshot ./check.png

# ✅ 高亮 = 中间那行。选中后点 picker 顶部的【确定】按钮（不是底部页面那个！）
# 顶部【确定】center 大约 (1308, 1505)（按 1440x2560 屏）
shenle-android-cli shell input tap 1308 1505
```

#### 特征速记

- **不是 fling**：duration ≤ 100ms 或 distance ≤ 500px 完全无效。
- **不是 tap**：点 listitem 不会触发选中。
- **循环列表**：滚到底自动回卷到头，找中间段（H/K 之类）需要先过冲再回滚。
- **三列独立滚动**：省/市/区各滑各的，第一列确认后第二/三列才会联动更新数据。

#### 自检流程（卡住时按这个顺序）

1. `dump-ui` 拿 picker 三列 bounds（`id_province / id_city / id_district`）。
2. 检查起点/终点是否**都在 picker 纵向范围内**（一般在 y=1500~2400）。
3. 检查 `swipe-to` 的 distance ≥ 700、duration ≥ 800。
4. 截一张图看是否动了。如果纹丝不动 → 距离/起点有问题；如果动了但定位不准 → 用 80px 小步回滚精确。

### 系统按键 / 系统面板

```bash
shenle-android-cli keyevent <code|alias>
# 支持 30+ 别名：back / home / recents / volume_up / volume_down / power / enter / tab / ...
# 也支持数字键码（4 / 3 / 187）或 0x 前缀的十六进制（0x20）
# → [OK] keyevent: back (code=4)

shenle-android-cli recents
# 最近任务（KEYCODE_APP_SWITCH = 187）

shenle-android-cli notifications
# 下拉通知栏（cmd statusbar expand-notifications）

shenle-android-cli dump-ui <file>
# uiautomator dump → pull 到本地 XML（AI 之外的元素结构取证）

shenle-android-cli shell <cmd...> [--filter PATTERN]
# adb shell 透传；原始 stdout/stderr 原样，退出码原样返回
# --filter PATTERN：行级包含过滤（避免 Windows 没 grep 的问题）
```

## 通用 flag

下面这些 flag 加在大多数命令后面都行：

```bash
shenle-android-cli <command> [args] -s <SERIAL>
shenle-android-cli <command> [args] --serial <SERIAL>
# 指定连哪台设备（多设备场景；默认取 adb 列表第一个 state==device）

shenle-android-cli <command> [args] --debug
# 调试模式：
#   - click / input / longpress / swipe --region / batch 会保存「AI 红框标注图」
#     到 cwd/shenle-debug-<cmd>-<ts>.png（默认行为；不污染 cwd）
#   - 打印 bbox 换算过程 + 各阶段耗时（毫秒）
#   - 内部异常时打印完整堆栈

shenle-android-cli click/input/swipe-to <args> --screenshot POST_PATH
# 操作完成后额外保存一张操作后截图（不带框），方便回归取证
```

## 元素定位（AI 视觉）

`click` / `input` / `longpress` / `batch click|longpress` / `swipe --region` / `get` 的 AI 元素定位遵循这套约定：

- **坐标系**：0-1000 **归一化坐标**，与图片实际像素无关。本地按真实截图尺寸换算成像素中心。
  - AI 返回 `[xmin, ymin, xmax, ymax]`（0-1000 整数）
  - 像素中心 = `((xmin+xmax)/2 * img_w/1000, (ymin+ymax)/2 * img_h/1000)`
- **描述**：自然语言，写「登录按钮」「用户名输入框」「左侧菜单」即可。
- **输入框**：点输入框本身（不是 label 文字）。
- **bbox 容差**：太小（<5x5 像素）会报 `[FAIL]` 重试。

## Batch — 一次截图 + 一次 AI 识别多个元素

> **多步操作优先用 batch**：只截一次图、只调一次 AI，按顺序执行。比串行 click/input 快很多、AI 准确率也更高（一次看到所有目标）。

支持的 5 种操作（空格分隔；描述可含空格；input 用 `::` 把描述和文本分开）：

| 操作 | 语法 | 说明 |
| --- | --- | --- |
| `click` | `click <描述>` | AI 视觉定位并点击 |
| `input` | `input <描述>::<文本>` | AI 视觉定位输入框并填入（**batch input 固定走屏幕中心**，不走 AI） |
| `click-at` | `click-at <x> <y>` | 无 AI，点击原始坐标 |
| `input-at` | `input-at <x> <y> <文本>` | 无 AI，点击坐标后输入 |
| `longpress` | `longpress <描述> [--duration N]` | AI 视觉定位 + 长按（默认 1500ms） |

**示例**：

```bash
# 登录表单：填用户名 + 密码 + 点登录（3 步，1 次 AI）
shenle-android-cli batch input "用户名::admin" input "密码::123456" click "登录"

# 混合 AI 和坐标（先点搜索框坐标 → AI 识别搜索按钮 → 点提交）
shenle-android-cli batch click-at 100 200 click "搜索按钮"

# 长按元素
shenle-android-cli batch longpress "我的头像" --duration 2000

# 调试：加 --debug 看每步 AI 返回的 bbox + 标注图
shenle-android-cli --debug batch input "用户名::admin" input "密码::123" click "登录"
# → [OK] batch: 3/3 ops total=...ms shot=...ms ai=...ms ops=...ms
# → ai框=shenle-debug-batch-<ts>.png
```

**性能对比**（300ms AI 延迟 + 真实 screencap，3 次 click 操作）：

```
串行（3 条独立 click）：4.33s
batch（1 条 batch click×3）：2.42s
batch 比 serial 快 1.91s（44%）
```

## 中文输入（关键，避免乱码）

`adb shell input text` 对非 ASCII（中文 / emoji）会丢字符或乱码。
本工具对 **非 ASCII 文本** 强制走 Android 10+ 的标准剪贴板方案：

```
adb shell cmd clipboard set-primary-clip --user 0 <文本>   # 写入
adb shell cmd clipboard get-primary-clip --user 0          # 读回校验
adb shell input keyevent 279                              # 触发粘贴
```

如果设备 / ROM 不支持 `cmd clipboard`（vivo / ColorOS / HyperOS 等定制 ROM 常见、部分模拟器镜像也没有），**不会**回退到 `input text`——会直接报错并提示装 [ADBKeyboard](https://github.com/senzhk/ADBKeyBoard) 兜底：

```
[FAIL] input: 剪贴板方案不可用（set-primary-clip 失败：No shell command implementation.）。
        常见于 vivo/ColorOS/HyperOS 等定制 ROM。请改用 ADBKeyboard：装好 APK →
        切到 ADBKeyboard 输入法 → 用 `adb shell am broadcast -a ADB_INPUT_TEXT
        --es msg '...'` 输入。
```

> "看似成功但内容乱码" 比 "明确失败" 更危险（用例静默通过），所以宁可报错也不兜底。

通过 `--input-method adbkeyboard` 或环境变量 `INPUT_METHOD=adbkeyboard` 切换到 ADBKeyboard 路径。

## 冷启动 vs 热启动

```bash
shenle-android-cli stop com.android.settings       # am force-stop，杀进程
# → [OK] stop: com.android.settings 已强制停止（am force-stop）

shenle-android-cli launch com.android.settings    # 冷启动
# → [OK] launch: com.android.settings ... → Events injected: 1

shenle-android-cli close                           # Home 键，保留进程
# → [shenle] 已回到桌面（device=emulator-5554）

shenle-android-cli shell dumpsys activity processes | grep com.android.settings
# → *APP* UID 1000 ProcessRecord{... com.android.settings/1000}    # 进程还在
```

- `stop` = 杀进程（**冷启动测试**）
- `close` = Home 键（**热切换**，进程保留）

## AI 红框标注图（`--debug`）

`--debug` 时启用，AI 类命令把用过的那张截图画红框 + 标签，保存到 `cwd/shenle-debug-<cmd>-<timestamp>.png`，路径打在 `[OK]` 行末尾：

```
# 不带 --debug：干干净净一行
$ shenle-android-cli click "搜索按钮"
[OK] click "搜索按钮": (720, 230); shot=469ms ai=812ms total=1281ms

# 带 --debug：多一张标注图 + 路径
$ shenle-android-cli --debug click "搜索按钮"
[OK] click "搜索按钮": (720, 230); shot=469ms ai=812ms total=1281ms; ai框=shenle-debug-click-1700000000000.png
```

点开 `ai框` 那张图能看到 AI 把元素框在了哪个位置——调试 AI 误识别时直接看图就行。
**默认不开 `--debug` 不生成**，避免每次跑都污染 cwd。

## Output format

每个命令统一走 **单行** + exit code，方便 AI / 脚本 parse：

| 场景 | 形态 | exit code |
| --- | --- | --- |
| 成功 | `[OK] <cmd> <args>: <result>` | 0 |
| 业务失败（参数 / 设备 / 包名 / 剪贴板 / AI 配置） | `[FAIL] <cmd> <args>: <msg>` | 1 |
| 内部未捕获异常（`--debug` 看堆栈） | `[FAIL] <cmd> <args>: <msg>` | 2 |
| 基础设施类失败（`devices` / `start` / `close`） | `[shenle] <msg>`（stderr） | 1 |
| AI debug（仅 `--debug`） | `[DEBUG] ...`（stderr） | — |
| 透传命令（`shell` / `appinfo`）的 [OK] | `[OK] ...`（stderr），原始输出 stdout | — |

**stdout / stderr 约定**：

- `[OK]` / `[FAIL]` 打 **stdout**（`start` / `close` / 透传命令的 [OK] 打 stderr）。
- `[DEBUG]` 打 **stderr**。
- `get` 命令的状态行 `[OK] get "..."` 打 **stderr**，4 节描述内容打 **stdout**——脚本可以直接 `capture` 正文。
- `shell` / `appinfo` 走透传：原始 stdout 原样 + 退出码原样返回。

## Environment variables

| 变量 | 用途 | 必需 |
| --- | --- | --- |
| `ANDROID_AI_API_KEY` | AI 网关 key | `click` / `input` / `longpress` / `batch click\|longpress` / `swipe --region` / `get` 必需 |
| `ANDROID_AI_BASE_URL` | AI 网关 base URL（不带 `/chat/completions` 后缀） | 同上 |
| `ANDROID_AI_MODEL` | 视觉模型名 | 同上 |
| `INPUT_METHOD` | 输入法方案（`clipboard` 默认 / `adbkeyboard`） | 可选 |

也支持从当前目录的 `.env` 自动加载（`python-dotenv`）。

> **环境变量前缀是 `ANDROID_AI_*`**（跟 web-cli's `WEB_AUTOMATION_AI_*` 区分），跟 `apps/shenle-android-cli/demo/demo_2.py` 一致。

`devices` / `start` / `launch` / `close` / `stop` / `current-app` / `screenshot` / `swipe`（无 `--region`）/ `swipe-to` / `zoom` / `pinch` / `keyevent` / `recents` / `notifications` / `dump-ui` / `shell` / `appinfo` 不需要 AI 配置。

## 常见问题

| 报错 | 原因 | 修复 |
| --- | --- | --- |
| `[FAIL] click: AI 配置缺失：ANDROID_AI_API_KEY、ANDROID_AI_BASE_URL、ANDROID_AI_MODEL。...` | CWD/.env 没配或缺变量 | 在当前目录写 `.env` 含这 3 个变量；改完直接再跑 click（无需重启） |
| `[FAIL] click: AI 服务不可达（http://...）：...` | CWD/.env 的 BASE_URL 不可达 | `curl <BASE_URL>/v1/models` 看通不通 |
| `adb: no devices/emulators found` | 没接设备 / USB 调试没开 / 没授权 | `adb devices` 看列表；插线 / 开 USB 调试 / 同意弹窗 |
| `am force-stop: ... package does not exist` | 包名错 | 用 `shenle-android-cli appinfo <pkg>` 先查 |
| `剪贴板方案不可用（set-primary-clip 失败：...）` | vivo / ColorOS / HyperOS 等定制 ROM 不支持 `cmd clipboard` | 装 [ADBKeyboard](https://github.com/senzhk/ADBKeyBoard) → 切到 ADBKeyboard 输入法 → `--input-method adbkeyboard` |
| `[FAIL] swipe: ... 设备存在 ...（`device=emulator-5554`）` | 多设备 + 没传 `-s` | 每条命令都加 `-s SERIAL`，或让目标设备在 `adb devices` 里排第一 |
| 截图上 AI 框的位置和实际元素差很远 | 描述不消歧 | 用 `--debug` 看 `shenle-debug-click-<ts>.png` 确认 AI 框在哪；改描述（加位置 / 颜色 / 文字） |
| `input` 中文看上去成功了但内容是乱码 | 不应该出现——本工具直接报错而不是兜底 | 走"中文输入"那段排查 |
| WheelPicker（省/市/区）滑动没反应 | `swipe up -c N` / `swipe-to --duration 50` / tap listitem —— 全部无效 | 必读 **WheelPicker / 省市区地址选择器** 那节：慢速拖动（duration 800~1500ms，距离 ≥ 700px），先 dump-ui 拿 picker bounds |

## Examples

### 登录流程（最常见）

```bash
shenle-android-cli launch com.example.app
shenle-android-cli screenshot ./before.png

shenle-android-cli --debug batch \
    input "用户名输入框::admin" \
    input "密码输入框::secret123" \
    click "登录按钮"
# → [OK] batch: 3/3 ops total=...ms shot=...ms ai=...ms ops=...ms

shenle-android-cli screenshot ./after.png
shenle-android-cli current-app                          # 断言：是不是 com.example.app
```

### 跑一轮回归（多用例串行）

```bash
# 用例 1：搜索
shenle-android-cli launch com.example.app
shenle-android-cli batch input "搜索框::手机" click "搜索按钮"
shenle-android-cli swipe down -c 5
shenle-android-cli screenshot ./case1.png
shenle-android-cli get "搜索结果列表" > case1-desc.txt   # capture stdout 正文

# 用例 2：冷启动测试
shenle-android-cli stop com.example.app
shenle-android-cli launch com.example.app
shenle-android-cli screenshot ./case2.png
```

### 滚动 / 长按 / 取证

```bash
shenle-android-cli launch com.example.app

shenle-android-cli swipe up -c 5                         # 整屏上滑 5 次
shenle-android-cli --debug swipe down --region "商品列表" --screenshot ./scrolled.png
shenle-android-cli longpress "我的头像" --duration 2000  # 长按头像

shenle-android-cli dump-ui ./ui.xml                      # 元素结构取证
shenle-android-cli get "底部导航栏"                      # AI 视觉描述（4 节）

shenle-android-cli close
```

### ⚠️ 地址选择器（WheelPicker，物流 / 货运类 App 必踩）

```bash
# 场景：发货人信息页 → 点地址 → 弹省/市/区三列 picker → 选湖南省/长沙市 → 确定

# 1. 点地址文本框（中心点先用 dump-ui 拿，或者 AI click "地址输入框"）
shenle-android-cli shell input tap 920 962

# 2. dump-ui 拿 picker 三列 bounds
shenle-android-cli dump-ui ./ui_picker.xml
# 期望看到 id_province / id_city / id_district（如 [0,1595][480,2484] / [480,1595][960,2484] / [960,1595][1440,2484]）

# 3. 慢速大幅上滑省列（从初始位置往要找的字母段过冲）
shenle-android-cli swipe-to 240 1700 240 2420 --duration 1200   # 过冲到 G/H 段
shenle-android-cli screenshot ./prov1.png                        # 检查位置

# 4. 小步回滚精确到目标（80px ≈ 1 项）
shenle-android-cli swipe-to 240 1700 240 1860 --duration 800    # 80px 微调
shenle-android-cli screenshot ./prov2.png

# 5. 中间那行高亮就是要选中的，点 picker 顶部【确定】完成
shenle-android-cli shell input tap 1308 1505                    # 顶部确定 center (1308, 1505)
shenle-android-cli screenshot ./after_pick.png                  # picker 收起，地址已写入
```

**绝不要这样写**（会让 picker 完全没反应、卡死测试）：

```bash
# ❌ 整屏快滑
shenle-android-cli swipe up -c 5

# ❌ 短促 fling（duration < 500ms）
shenle-android-cli swipe-to 240 2200 240 1500 --duration 50

# ❌ tap listitem 想选中
shenle-android-cli shell input tap 240 1900

# ❌ 用 click 想让 AI 找"湖南省"
shenle-android-cli click "湖南省"
```

详见 **WheelPicker / 省市区地址选择器（强制 — 必读）** 那一节。

### Debug 单条 AI 命令

```bash
shenle-android-cli launch com.android.settings
shenle-android-cli --debug click "搜索按钮" --screenshot ./after.png
# → [DEBUG] bbox_1000=[...] scale=(...,...) bbox_px=[...] center=(...)
# → [DEBUG] screencap=...ms ai=...ms total=...ms
# → [OK] click "搜索按钮": (720, 230); shot=...ms ai=...ms total=...ms;
#        ai框=shenle-debug-click-1700000000000.png; post=...\after.png
# 点开 ai框 那张图能直接看到 AI 框选的位置
```

## Specific tasks

* **批量操作 + 取证**：`batch` 一次截图 + 一次 AI 识别多个元素，按顺序执行 —— 性能 / 准确率都优于串行 click/input。
* **⚠️ WheelPicker（省/市/区地址选择器，物流类 App 必踩）**：fling / tap / 整屏 swipe 全都无效；只能 `swipe-to` 慢拖（duration 800~1500ms，distance ≥ 700px）。详见 **WheelPicker / 省市区地址选择器（强制 — 必读）**。
* **AI bbox 选偏了**：用 `--debug` 看 `shenle-debug-<cmd>-<ts>.png`；改描述（加位置 / 颜色 / 文字）。
* **中文输入乱码**：本工具直接 `[FAIL]` 不兜底，走"中文输入"那段排查：优先装 ADBKeyboard。
* **冷启动 vs 热启动**：测冷启动用 `stop <pkg>` 再 `launch`；测热切换用 `launch` + `close`（Home 键）。
* **多设备**：每条命令加 `-s SERIAL`；或让目标设备在 `adb devices -l` 里排第一。
* **跨会话保状态**：Android 自动化不像 web 自动化有持久 user-data-dir；登录态 / 数据都依赖 App 自己的持久化，不在本工具能力范围。