---
title: shenle-device-record
---

# shenle-device-record

> Use when the user wants to record UI from a real Android device connected over USB-debugging — drives the local `shenle-device-record` CLI to capture screenshot + uiautomator dump into a timestamped …

正文 125 行，随包 references 2 个。

读完想直接用：[下载 zip（SKILL.md+references）](/skills/shenle-device-record.zip)　·　看说明与评分：[Skills 手册 · shenle-device-record](/kb/skills/shenle-device-record)

---

# shenle-device-record

驱动本机 `shenle-device-record` CLI，在**接在电脑上、已开 USB 调试**的真机 Android 上做界面采集。默认走 `serve` 子命令：本地起 HTTP + WebSocket 服务 + 自动用 `npx playwright` 打开 Chromium 录制面板，左侧实时画面，右侧填模块/功能/描述后一键落盘。`record` 子命令是 CLI 一次一截，适合脚本化场景。

**这是有副作用、会弹浏览器、长时间运行的工具**——按下面的 4 步流程走，遇到要用户决策的地方**停下来问**，不要自己猜。

&gt; **不要做的事（任何时候都生效）**
&gt;
&gt; - 不要自己装任何东西（node / adb / chromium / npm 包）——告诉用户怎么装，让用户自己装
&gt; - 不要替用户改 `.env`——给指引让用户写
&gt; - 不要擅自 `kill-server` / `taskkill` 别人的进程——可能影响其他工具
&gt; - 不要假设端口 `8765` 没被占——撞了让用户决定是换端口还是先杀掉现有进程（用户自己杀）
&gt; - 多台设备时不要自己挑——必须停下来问用户
&gt; - 采集期间不要阻塞用户——服务跑起来就挂起，等用户反馈

## 四个 Step 的判定标准

每一步的完整命令、参数、输出样例都在 `references/steps.md`，正文只留「怎么判断这步算过」。

| 步骤 | 过关标准 | 不过就停 |
| --- | --- | --- |
| 1 环境预检 | 依赖 `adb` 与 `shenle-device-record` 都能跑，版本打印正常 | 缺依赖先装，不往下走 |
| 2 确认设备 | `adb devices` 里目标设备是 `device` | `unauthorized` / `offline` 就修，别硬采 |
| 3 启动录制 | 产物目录出现新的时间戳批次，里面有截图与 JSON | 只有一半就当失败 |
| 4 收尾 | JSON 的 `elements` 与截图对得上，进程已退出 | 层级为空要重采 |

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

## 常见错误速查

| 现象 | 怎么查 |
|---|---|
| 服务启动但浏览器没出来 | 看 Playwright 日志（路径在启动日志里有）；多半是 Chromium 没下载完（首次跑要等 1–2 分钟） |
| 浏览器出来了但页面是空白 / WebSocket 连不上 | 检查端口是否被占（换 `--port`） |
| 左侧画面是黑色 / 不刷新 | 看服务端 stderr 有没有 `take_screenshot 失败`——多半是 midscene 配置问题（AI 模型环境变量、AI key 错等）；把报错原始输出贴给用户 |
| JSON 里 `content` 是空串 | `uiautomator dump` 在某些 Android 版本会竞态失败（特别是旧 MIUI / ColorOS）；不影响截图，告诉用户这是已知问题 |
| 实时模式下画面不刷新 / 提示"连续失败 N 次" | 服务端 stderr 会有 `midscene 截图失败`，查真因；工具会自动切到按需模式，不阻塞 |
| 用户关浏览器后服务不退 | `Ctrl+C` 强退（让用户自己按，不要替他按） |
| 端口 `8765` 被占 | 加 `--port &lt;其它&gt;`，或问用户要不要先杀掉现有进程（**不替你杀**） |
| 终端中文乱码 | 让用户在当前 `cmd.exe` 跑一次 `chcp 65001` 再跑命令；或者换 Git Bash / Windows Terminal。**只影响终端显示，不影响落盘文件** |
| `npx --yes @midscene/android` 首次跑超慢 | 首次会拉几十 MB 依赖（`sharp` 等），1–2 分钟起步，**不要中途 Ctrl-C**。国内网络可临时走 `npm config set registry https://registry.npmmirror.com` |

## 执行顺序

1. `adb devices` 确认设备是 `device` 而不是 `unauthorized` / `offline`。
2. 需要分流时显式带 `-s &lt;serial&gt;`；只有一台设备才省。
3. 解锁屏幕并停在一个确定的页面，避免层级抓到锁屏或半透明弹窗。
4. 跑 `record`（单次）或 `serve`（连续采集），产物进时间戳批次目录。
5. 打开 JSON 核对 `elements` 数量与截图是否对得上，再交给下游做用例。

## 判断与选择

| 场景 | 用哪个 | 为什么 |
| --- | --- | --- |
| 抓一屏就够 | `record` | 单次命令，起停成本最低 |
| 连续点着采 | `serve` | 本地服务常驻，省掉每轮重建连接 |
| 多台设备 | `-s &lt;serial&gt;` | 不带会被 `adb` 直接拒绝，不会替你挑一台 |
| 页面有 WebView / 自定义绘制 | 截图 + AI 描述 | `uiautomator` 只给得到能反映到无障碍树的控件 |
| 层级里有 `com.android.systemui` | 先关弹窗再采 | 系统弹窗会把业务层级挡掉 |

## 反模式

- **NEVER** 在多设备机器上省略 `-s` —— 因为 `adb` 会报 `more than one device/emulator` 直接退出。
- **NEVER** 把 `unauthorized` 当成"等一下就好" —— 因为要在手机上点「允许调试」，不点永远不会变。
- **NEVER** 只存截图不存层级 —— 因为图片给人看，定位要坐标与 resource-id，缺一样都没法回到用例里。
- **NEVER** 在锁屏状态下采集 —— 因为层级只有锁屏那几层，元素全错。
- **NEVER** 用同一目录覆盖上一批 —— 因为前后两次对比时丢基线，按时间戳分批是唯一可追溯的做法。

## 失败兜底

- `device unauthorized`：手机上点允许；仍不行就 `adb kill-server` 后重插。
- `device offline`：换线或换 USB 口，再 `adb devices` 复核。
- 层级抓不全：先关系统弹窗、锁屏，再重抓；WebView 内容改用截图 + 视觉模型。
- `record` 报目录不存在：确认工作目录可写，或用参数指定输出根目录。
- 全都不行：退回 `labs/_shared/adb.py` 里的 `screenshot` / `dump_ui` 两个原语手搓一次，判断是设备还是封装的问题。

## 示例

最小一次采集（单台设备，采完就能在产物目录看到时间戳批次）：

```bash
adb devices                                  # 确认状态是 device
shenle-device-record record                  # 抓当前屏幕 + 层级，写入时间戳批次
ls &lt;产物目录&gt;/&lt;最新批次&gt;                      # 应看到截图 PNG 与 JSON 各一份
```

多台设备时换成：

```bash
shenle-device-record record -s FA7B11A03073
```

## 报错对照

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `device unauthorized` | 手机上没点允许调试 | 点允许；还不行进 `adb kill-server` 重插 |
| `device offline` | 线材或 USB 口不稳 | 换线换口，再 `adb devices` 复核 |
| `more than one device/emulator` | 多设备没带 `-s` | 加 `-s &lt;serial&gt;` |
| 层级里只有 `com.android.systemui` | 锁屏或系统弹窗盖住 | 解锁、关弹窗再采 |
| JSON 里 `elements` 为空 | 页面是自绘或 WebView | 改走截图 + 视觉描述 |
| 找不到产物目录 | 工作目录不可写 | 换可写目录或显式指定输出根 |
| `record` 秒退无输出 | 依赖缺失或版本不匹配 | 先 `--version` 与 `--help` 各跑一次定位 |

## 速查表在 references 里

MANDATORY：动手前先读 `references/quick-reference.md`，那里是高频命令与对照表；正文只讲判断与避坑，不重复贴命令清单。

