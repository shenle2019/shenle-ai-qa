# 拉拉货 真机手工验收清单

> 目标：用 shenle-android-cli 在真机/模拟器上跑「登录 + 添加订单」两条用例
> 截图证据统一存到 `D:\Code\AIQECourse\Phase2\`，每步的命名建议见下文

---

## 0. 前置检查（跑流程前必做）

| # | 命令 | 期望 |
|---|---|---|
| 0.1 | `shenle-android-cli devices` | 列出设备，看到目标设备 `state == device` |
| 0.2 | `shenle-android-cli --version` | 打印 `shenle-android-cli 0.1.0`（确认 CLI 在 PATH） |
| 0.3 | `shenle-android-cli current-app` | 看到 `com.kenny.logistics`（或本测试目标包名） |

环境变量在 `D:\Code\AIQECourse\Phase2\.env`（已配 `ANDROID_AI_*` 三件套）。

---

## 用例 1：登录

| # | 命令 | 人工核对 | 截图 |
|---|---|---|---|
| 1.0 | `shenle-android-cli screenshot ./01_login_before.png` | 当前停在登录页 | `01_login_before.png` |
| 1.1 | `shenle-android-cli batch input "手机号输入框::15096264001" input "密码输入框::123456" click "登录按钮" --screenshot ./02_login_after.png` | 一次 batch 完成 3 步；截图看到首页 | `02_login_after.png` |
| 1.2 | `shenle-android-cli current-app --format json` | `activity` = `.ui.MainActivity`（不是 `.ui.LoginActivity`） | — |

**用例 1 期望**：

- [ ] Activity 从 `.ui.LoginActivity` 跳到 `.ui.MainActivity`
- [ ] 首页顶部显示「欢迎使用拉拉货」

---

## 用例 2：添加订单

### 阶段 A：进入发货人信息页

| # | 命令 | 人工核对 | 截图 |
|---|---|---|---|
| 2.1 | `shenle-android-cli screenshot ./03_home.png` | 当前在首页，宫格区可见「一键下单」 | `03_home.png` |
| 2.2 | `shenle-android-cli click "一键下单" --screenshot ./04_after_onekey.png` | 进入下单页（标题"下单"，含"发货人 / 收货人"两栏） | `04_after_onekey.png` |

> **若 AI click 报错「找不到元素」**：用 dump-ui 取"一键下单"坐标后改用 `shenle-android-cli shell input tap <x> <y>`。

### 阶段 B：填发货人姓名 + 手机号

| # | 命令 | 人工核对 | 截图 |
|---|---|---|---|
| 2.3 | `shenle-android-cli shell "ime enable com.android.adbkeyboard/.AdbIME && ime set com.android.adbkeyboard/.AdbIME"` | 提示 "already enabled / selected"（剪贴板方案不可用，必须 ADBKeyboard） | — |
| 2.4 | `shenle-android-cli batch --input-method adbkeyboard input "姓名输入框::哈米" input "手机号输入框::15096268001" --screenshot ./05_after_fill.png` | 姓名=哈米、手机号=15096268001 都已填入；底部出现「ADB Keyboard {ON}」 | `05_after_fill.png` |

### 阶段 C：地址 picker 三列选择（核心难点）

| # | 命令 | 人工核对 | 截图 |
|---|---|---|---|
| 2.5 | `shenle-android-cli shell input tap 920 962` | 底部弹出三列 picker（省/市/区），中间高亮=安徽省 | `06_picker_open.png`（可选） |
| 2.6 | `shenle-android-cli dump-ui ./ui_picker.xml` | XML 中含 `id_province / id_city / id_district` 三列 bounds | — |
| 2.7 | `shenle-android-cli shell "cat /sdcard/window_dump.xml"` | 确认省列 bounds 中心 x ≈ 240（1440 屏宽三等分） | — |
| 2.8 | `shenle-android-cli swipe-to 240 1700 240 2420 --duration 1200` | 省列大幅上滑，停在 G/H 段附近（"过冲"） | `07_prov1.png` |
| 2.9 | `shenle-android-cli swipe-to 240 1700 240 1860 --duration 800` | 80px 微调，中间高亮到「湖南省」 | `07_prov2.png` |
| 2.10 | `shenle-android-cli screenshot ./07_prov_final.png` | 中间行 = **湖南省**（不是湖北/广东/广西） | `07_prov_final.png` |
| 2.11 | `shenle-android-cli shell input tap 1308 1505` | picker 顶部【确定】，picker 收起 | `08_after_addr_confirm.png` |

> **若 picker 没动 / 滑过头 / 卡住**：参考 SKILL.md `### ⚠️ WheelPicker / 省市区地址选择器（强制 — 必读）` 那一节排查。绝不能用 `swipe up -c 5` / `swipe-to --duration 50` / `tap listitem`。

### 阶段 D：详细地址 + 提交

| # | 命令 | 人工核对 | 截图 |
|---|---|---|---|
| 2.12 | `shenle-android-cli shell input tap 920 1283` | 详细地址输入框获得焦点 | — |
| 2.13 | `shenle-android-cli shell "am broadcast -a ADB_INPUT_TEXT --es msg '长沙'"` | 详细地址输入「长沙」 | `09_after_detail.png` |
| 2.14 | `shenle-android-cli shell input tap 720 2440` | 点击底部【确定】按钮 | `10_final.png` |
| 2.15 | `shenle-android-cli shell "ime set com.android.inputmethod.pinyin/.InputService"` | 还原系统输入法（清理测试副作用） | — |

---

## 用例 2 期望（人工核对清单）

### 期望 1：返回到下单页

- [ ] Activity = `com.kenny.logistics`（不再是 `.ui.SendActivity` 或 `.ui.PickerActivity`）
- [ ] 顶部标题文字 = `下单`
- [ ] 页面仍能看到「发货人 / 收货人 / 配送方式 / 预计发货时间 / 限时到达时间 / 货物明细」六栏

### 期望 2：发货人显示添加的数据信息

- [ ] 发货人行第一行：`哈米(15096268001)`
- [ ] 发货人行第二行：`湖南省/长沙市/长沙县 长沙`

**两者都满足**才视为用例通过；任一不满足 → 用例失败，需截图取证。

---

## 通用排查（卡住时按这个顺序）

| 现象 | 排查命令 |
|---|---|
| AI click 找不到元素 | `shenle-android-cli --debug click "..."` 看 `shenle-debug-click-*.png` 红框图 |
| 中文输入乱码 | 确认已切到 ADBKeyboard：`shenle-android-cli shell "ime list -s"` 看 `com.android.adbkeyboard/.AdbIME` |
| 多设备乱选 | 每条命令加 `-s <SERIAL>`，或让目标设备排在 `adb devices` 第一 |
| picker 滑不动 | 起点 y 必须在 picker 范围内（≈ 1700~2400）；distance ≥ 700；duration ≥ 800 |
| 坐标不准 | `shenle-android-cli dump-ui ./ui.xml` + `shenle-android-cli shell "cat /sdcard/window_dump.xml"` 查真实 bounds |

---

## 一键复跑（所有命令串起来）

```bash
# 前置
shenle-android-cli devices
shenle-android-cli screenshot ./01_login_before.png

# 用例 1
shenle-android-cli batch input "手机号输入框::15096264001" input "密码输入框::123456" click "登录按钮" --screenshot ./02_login_after.png
shenle-android-cli current-app --format json

# 用例 2
shenle-android-cli screenshot ./03_home.png
shenle-android-cli click "一键下单" --screenshot ./04_after_onekey.png
shenle-android-cli shell "ime enable com.android.adbkeyboard/.AdbIME && ime set com.android.adbkeyboard/.AdbIME"
shenle-android-cli batch --input-method adbkeyboard input "姓名输入框::哈米" input "手机号输入框::15096268001" --screenshot ./05_after_fill.png
shenle-android-cli shell input tap 920 962
shenle-android-cli dump-ui ./ui_picker.xml
shenle-android-cli swipe-to 240 1700 240 2420 --duration 1200
shenle-android-cli swipe-to 240 1700 240 1860 --duration 800
shenle-android-cli screenshot ./07_prov_final.png
shenle-android-cli shell input tap 1308 1505
shenle-android-cli shell input tap 920 1283
shenle-android-cli shell "am broadcast -a ADB_INPUT_TEXT --es msg '长沙'"
shenle-android-cli shell input tap 720 2440
shenle-android-cli screenshot ./10_final.png
shenle-android-cli shell "ime set com.android.inputmethod.pinyin/.InputService"
```
