## Commands

### Core — 浏览控制 + 截图

```bash
shenle-web-cli navigate <url>
# 自动补 https:// 前缀；把 viewport 拉到 1440x900（每次都拉，固定不变）
# → [OK] navigate: <url> → title="<title>"

shenle-web-cli screenshot <path.png>
# 截当前 viewport（非整页）
# → [OK] screenshot: <path> (<w>x<h>) [<format>]
shenle-web-cli screenshot ./shot.jpg                        # 按扩展名推断 jpeg
shenle-web-cli screenshot ./shot.jpg --quality 70           # JPEG 质量 1-100
shenle-web-cli screenshot ./shot.png --format png           # 显式指定
shenle-web-cli screenshot ./shot.jpg --format jpeg --quality 90
```

### Core — AI 视觉定位（自然语言描述，无需 selector）

> **必须配 3 个环境变量**（缺一立刻 `[FAIL]`，不重试）：
>
> ```bash
> WEB_AUTOMATION_AI_API_KEY=sk-xxx
> WEB_AUTOMATION_AI_BASE_URL=http://your-llm-gateway/v1
> WEB_AUTOMATION_AI_MODEL=your-vision-model-name
> ```
>
> 三个从当前目录 `.env` 自动加载；真实环境变量优先。

```bash
shenle-web-cli click <description>
shenle-web-cli click "登录按钮"
shenle-web-cli click "登录按钮" --enhanced "右上角、蓝色"
shenle-web-cli click "登录" --screenshot ./after.png     # 操作后追加一张截图取证
# → [OK] click "登录": (820, 360)
# → [OK] click "登录": (820, 360); 截图 → ...\after.png

shenle-web-cli input <description> <text>
shenle-web-cli input "用户名" "admin"
shenle-web-cli input "搜索框" "你好，世界"                # 中文 OK
shenle-web-cli input "搜索框" "a very long string..."     # 长字符串 OK
shenle-web-cli input "密码" "secret" --screenshot ./filled.png
# 输入前自动 Ctrl+A + Delete 清空，再 insert_text 整串填入
# → [OK] input "用户名" "admin": (720, 240)

shenle-web-cli scroll <direction> [-c N] [--region <描述>] [--screenshot <path>]
shenle-web-cli scroll down                                # 滚整页 1 次
shenle-web-cli scroll down -c 5                           # 滚整页 5 次
shenle-web-cli scroll down --region "左侧菜单"            # AI 视觉定位区域，只滚该区域
shenle-web-cli scroll down --region "结果列表" -c 3 --screenshot ./scrolled.png
# direction: up | down | left | right
# → [OK] scroll: down ↓ × 1
# → [OK] scroll: down ↓ × 3 in "结果列表" bbox_1000=[...] bbox_px=[...] center=(...)
```

### Core — AI 视觉读取（自然语言描述 + 结构化文本）

```bash
shenle-web-cli get <description>
shenle-web-cli get "顶部导航栏"
shenle-web-cli get "搜索结果列表"
shenle-web-cli get "购物车侧边栏" --screenshot ./cart.png
# 把当前 viewport 发给视觉模型，按下面 4 段输出：
# ## 布局
# ## 图标
# ## 文字
# ## 介绍
# 状态行打 stderr（[OK] / [FAIL]），结构化文本打 stdout —— 脚本可直接 capture stdout
```

### Core — 读页面状态（断言 / 取证）

```bash
shenle-web-cli url
shenle-web-cli url --format json
# → https://example.com/
# → {"url": "https://example.com/", "title": "Example Domain"}

shenle-web-cli title
shenle-web-cli title --format json
# → Example Domain
# → {"url": "https://example.com/", "title": "Example Domain"}
```

### Raw coordinates — 无 AI，纯像素坐标

> 用不到，必须知道精确像素位置时用。一般优先用 AI 命令。

```bash
shenle-web-cli click-at <x> <y>
shenle-web-cli click-at 820 360

shenle-web-cli input-at <x> <y> <text>
shenle-web-cli input-at 720 240 "admin"
# 不会清空已有内容，直接点击 + insert_text

shenle-web-cli swipe-to <x1> <y1> <x2> <y2>
shenle-web-cli swipe-to 500 800 500 200       # 向上滑动
# 起点 (x1,y1) → 终点 (x2,y2)，中间 10 步平滑拖动
```

### Batch — 一次截图 + 一次 AI 识别多个元素

> **多步操作优先用 batch**：只截一次图、只调一次 AI，按顺序执行。比串行 click/input 快 ~2 倍、AI 准确率也更高（一次看到所有目标）。

```bash
shenle-web-cli batch <op> <args> [<op> <args> ...]
```

支持 4 种操作（空格分隔；描述可含空格；input 用 `::` 把描述和文本分开）：

| 操作 | 语法 | 说明 |
| --- | --- | --- |
| `click` | `click <描述>` | AI 视觉定位并点击 |
| `input` | `input <描述>::<文本>` | AI 视觉定位输入框并填入 |
| `click-at` | `click-at <x> <y>` | 无 AI，点击原始坐标 |
| `input-at` | `input-at <x> <y> <文本>` | 无 AI，点击原始坐标后输入 |

**示例**：

```bash
# 登录表单：填用户名 + 密码 + 点登录（3 步，1 次 AI）
shenle-web-cli batch input "用户名::admin" input "密码::123456" click "登录"

# 混合 AI 和坐标（先点搜索框坐标 → AI 识别搜索按钮 → 点提交）
shenle-web-cli batch click-at 100 200 click "搜索按钮"

# 调试：加 --debug 看每步 AI 返回的 bbox + 标注图
shenle-web-cli batch input "用户名::admin" input "密码::123" click "登录" --debug
# → [OK] batch: 3/3 ops total=2.1s shot=180ms ai=620ms ops=900ms
# → [DEBUG] #1 '用户名' → bbox_1000=[...] bbox_px=[...] center=(...)
# → [DEBUG] 标注图: <cwd>\shenle-debug-batch-<ts>.png
```
