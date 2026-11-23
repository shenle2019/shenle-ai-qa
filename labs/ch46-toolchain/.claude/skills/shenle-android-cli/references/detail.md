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
