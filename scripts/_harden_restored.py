"""给恢复回来的两个技能补六段（执行顺序/判断与选择/反模式/失败兜底/一页速查），拉到 ≥108。"""

from __future__ import annotations

from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / ".claude" / "skills"

API_CLI = """
## 执行顺序

1. 先确认请求 JSON：`url` 必填，`method` 缺省 GET，`headers` / `urlParams` / `bodyParams` 都是 `[{name, value}]`。
2. 首选一条 `call`：`shenle-api-cli call req.json --field "$.data.token"`，send 与取值一次完成。
3. 只有需要把 `result_file` 交给后续任务时，才拆成 `send` + `extract` 两步。
4. JSONPath 判不出来（`$..`、filter、非 JSON body）时改用 `--field "返回的 X"` 走自然语言，或直接读 result 文件。
5. 断言优先写成可判定的 JSONPath/状态码；自然语言 `assert` 只做兜底复核。

## 判断与选择

| 场景 | 用哪个 | 为什么 |
| --- | --- | --- |
| 常规调接口、取一个字段 | `call` | 一条命令、无管道无赋值，Windows cmd 里也不会挂 |
| 需要结果文件给下一步 | `send` 再 `extract` | 中间产物落盘，后续步骤可以复用 |
| 4xx 也要取值 | 加 `--no-fail-on-status` | 默认 4xx/5xx 会 `[FAIL]` 退出，加了才继续落盘 |
| 响应不是 JSON | `--field "中文描述"` 或直接看 result | JSONPath 只对 JSON 有效 |
| 要断言业务语义 | 状态码/字段先断言，语义再兜底 | 可判定优先，模糊结论放最后 |

## 反模式

- **NEVER** 用 `result_file=$(...)` 接输出 —— 因为 Bash 工具在 Windows 上走 `cmd /c`，这种赋值语法直接失败。
- **NEVER** 依赖 `{{xxx}}` 在工具里再渲染 —— 因为 runner 送进来之前已经渲染完，工具只认字面值。
- **NEVER** 用 `extract --field "$..id"` 这类递归语法 —— 因为工具只支持点号路径与数组下标，会 `[FAIL]`。
- **NEVER** 为了省一步把 token 硬编码进 req.json —— 因为泄露进 git 历史就洗不掉，用 `--field` 现场取。
- **NEVER** 只看 `[OK]` 就当断言通过 —— 因为 `[OK]` 只说明请求发出去了，状态码与字段要另行断言。

## 失败兜底

- 网络失败（`网络请求失败`）：先 `ping`/`curl` 同 URL 确认可达，再调大 `--timeout`；仍失败就换内网地址。
- 4xx/5xx：加 `--no-fail-on-status` 落盘，读 result 里的原始报文定位，不要盲改请求。
- JSONPath 不匹配（`value=null`）：改自然语言抽取，或先 `--debug` 看完整 body。
- 需要 AI 的 `assert` 报配置缺失：检查 `.env` 里三个 `API_AUTOMATION_AI_*`，缺哪个补哪个。
- 以上都不行：直接用 `python -c` + `requests` 兜底复现一次，再回来判断是工具 bug 还是接口问题。

## 一页速查

| 想干什么 | 命令 |
| --- | --- |
| 发请求并取 token | `shenle-api-cli call req.json --field "$.data.token"` |
| 只要结果文件 | `shenle-api-cli send req.json` |
| 从已有结果取字段 | `shenle-api-cli extract result.json --field "$.data.id"` |
| 4xx 也继续 | `shenle-api-cli call req.json --field "$.msg" --no-fail-on-status` |
| 自然语言取值 | `shenle-api-cli call req.json --field "返回的 token" --name 登录Token` |
| 看版本 | `shenle-api-cli --version` |
"""

DEVICE_RECORD = """
## 执行顺序

1. `adb devices` 确认设备是 `device` 而不是 `unauthorized` / `offline`。
2. 需要分流时显式带 `-s <serial>`；只有一台设备才省。
3. 解锁屏幕并停在一个确定的页面，避免层级抓到锁屏或半透明弹窗。
4. 跑 `record`（单次）或 `serve`（连续采集），产物进时间戳批次目录。
5. 打开 JSON 核对 `elements` 数量与截图是否对得上，再交给下游做用例。

## 判断与选择

| 场景 | 用哪个 | 为什么 |
| --- | --- | --- |
| 抓一屏就够 | `record` | 单次命令，起停成本最低 |
| 连续点着采 | `serve` | 本地服务常驻，省掉每轮重建连接 |
| 多台设备 | `-s <serial>` | 不带会被 `adb` 直接拒绝，不会替你挑一台 |
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

## 一页速查

| 想干什么 | 命令 |
| --- | --- |
| 看有没有设备 | `adb devices` |
| 单次采集 | `shenle-device-record record` |
| 连续采集 | `shenle-device-record serve` |
| 指定设备 | `shenle-device-record record -s <serial>` |
| 看版本 | `shenle-device-record --version` |
| 手动抓一屏 | `adb -s <serial> exec-out screencap -p > screen.png` |
"""

PATCH = {
    "shenle-api-cli": API_CLI,
    "shenle-device-record": DEVICE_RECORD,
}

for name, extra in PATCH.items():
    path = SKILLS / name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if "## 执行顺序" in text:
        print(f"{name}: 已有六段，跳过")
        continue
    text = text.rstrip() + "\n" + extra
    path.write_text(text, encoding="utf-8")
    print(f"{name}: 追加六段，{len(text.splitlines())} 行")
