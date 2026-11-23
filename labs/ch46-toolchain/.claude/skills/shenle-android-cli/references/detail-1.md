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
