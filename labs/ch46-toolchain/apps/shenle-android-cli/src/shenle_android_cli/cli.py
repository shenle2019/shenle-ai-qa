"""CLI 入口：argparse 分发 + 统一异常处理。

子命令（Phase 4）：
- devices               列出 adb 看得到的所有设备
- start                 选定一台目标设备（-s 指定或第一台可用）
- launch <pkg>          启动 App（Activity 可选）
- close                 按 Home 键回到桌面（保留进程）
- stop <pkg>            am force-stop（杀进程，冷启动测试）
- screenshot <path>     截屏到文件
- click <desc>          AI 视觉定位 + tap
- input <desc> <text>   AI 视觉定位 + tap + 输入文本
- batch <ops...>        一次截图 + 一次 AI + 顺序执行多个 op
- longpress <desc>      AI 定位 + 长按
- swipe <dir>           滑动（整屏 / 区域内）
- swipe-to x1 y1 x2 y2  显式坐标滑动
- zoom x y --scale 2.0  双指放大（线程并行）
- pinch x y --scale 0.5 双指缩小
- keyevent <code|alias> 按键
- recents               最近任务
- notifications         下拉通知栏
- current-app           当前前台 App
- get <区域描述>        AI 视觉描述页面区域（4 节）
- shell <cmd...>        adb shell 透传
- dump-ui <file>        uiautomator dump → pull
- appinfo <pkg>         dumpsys package
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from . import __version__
from .adb import run_adb, run_adb_relaxed, summarize_output
from .commands import (
    cmd_appinfo,
    cmd_batch,
    cmd_click,
    cmd_current_app,
    cmd_dump_ui,
    cmd_get,
    cmd_input,
    cmd_keyevent,
    cmd_longpress,
    cmd_notifications,
    cmd_pinch,
    cmd_recents,
    cmd_screenshot,
    cmd_shell,
    cmd_stop,
    cmd_swipe,
    cmd_swipe_to,
    cmd_zoom,
)
from .devices import list_devices, pick_device
from .errors import AdbCommandFailed, CliError, PackageNotFound

# Windows 默认控制台是 GBK，argparse 拿到中文 description 会乱码。
# 在打印任何东西之前，把 stdout/stderr 强切到 UTF-8。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass


# ---------------------------------------------------------------------------
# parser


def build_parser() -> argparse.ArgumentParser:
    # 全局参数：可以出现在 <command> 之前（顶层）或之后（子命令）。
    # 用 argparse.SUPPRESS 当默认值：顶层解析了 --serial 之后，
    # 子解析器没看到 --serial 也不会用 None 把顶层的值覆盖掉。
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "-s", "--serial", default=argparse.SUPPRESS,
        help="目标设备序列号；不传则用 adb 列表里的第一台可用设备",
    )
    shared.add_argument(
        "--debug", action="store_true", default=argparse.SUPPRESS,
        help="调试模式：内部异常打印完整堆栈（默认仅一行提示）",
    )
    shared.add_argument(
        "--input-method", choices=["clipboard", "adbkeyboard"], default=argparse.SUPPRESS,
        help=(
            "中文输入方式：clipboard（默认，Android 10+ cmd clipboard）"
            "或 adbkeyboard（ADBKeyboard 第三方 IME）。"
            "不传则读 INPUT_METHOD 环境变量；都没有默认 clipboard。"
            "顶层 / input / batch 子命令位置都能用。"
        ),
    )

    parser = argparse.ArgumentParser(
        prog="shenle-android-cli",
        description=(
            "命令行驱动的安卓 UI 自动化工具（adb shell input）。"
            "后续供 AI 按自然语言调用。"
        ),
        parents=[shared],
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # ---- devices ----
    sub.add_parser(
        "devices",
        help="列出当前 adb 看得到的所有设备",
        description=(
            "调用 `adb devices -l`，按状态分组输出（✓ 可用 / ✗ 异常）。"
            "如果 adb 看不到任何设备，会给一份排查清单。"
        ),
        parents=[shared],
    )

    # ---- start ----
    sub.add_parser(
        "start",
        help="选定目标设备（后续 launch / close 等命令会复用同一条规则）",
        description=(
            "按 `-s/--serial` 选定一台设备；不传则选 adb 列表里第一台"
            "状态为 device 的设备。Phase 1 不持久化选择——每条命令会重新解析"
            "adb devices（用同样的规则），所以多设备时记得显式 -s。"
        ),
        parents=[shared],
    )

    # ---- launch ----
    launch_p = sub.add_parser(
        "launch",
        help="启动一个 App",
        description=(
            "调用 `adb shell am start -W -n <pkg>/<activity>` 启动指定包名 + Activity；"
            "如果不传 Activity，则退化为 `monkey -p <pkg> -c LAUNCHER 1`，"
            "由系统自行挑 launcher activity。"
            "Activity 简写 `.MainActivity` 会被自动补全为 `<pkg>/.MainActivity`。"
        ),
        parents=[shared],
    )
    launch_p.add_argument("pkg", help="包名（如 com.android.settings）")
    launch_p.add_argument(
        "activity", nargs="?", default=None,
        help="Activity 名（可选）。可写简写 .MainActivity 或完整类名",
    )

    # ---- close ----
    sub.add_parser(
        "close",
        help="按 Home 键回到桌面（App 进程保留）",
        description="调用 `adb shell input keyevent 3`（KEYCODE_HOME）。",
        parents=[shared],
    )

    # ---- screenshot ----
    screenshot_p = sub.add_parser(
        "screenshot",
        help="截当前屏幕到文件",
        description=(
            "用 `adb exec-out screencap -p` 截当前屏幕。"
            "扩展名为 .png/.jpg/.jpeg 自动选格式；也可显式 --format。"
        ),
        parents=[shared],
    )
    screenshot_p.add_argument("path", help="输出图片路径（.png / .jpg）")
    screenshot_p.add_argument(
        "--format", choices=["auto", "png", "jpeg"], default="auto",
        help="输出格式；auto 按扩展名推断（默认）",
    )
    screenshot_p.add_argument(
        "--quality", type=int, default=85,
        help="JPEG 质量 1-100（仅 jpeg 格式生效，默认 85）",
    )

    # ---- click ----
    click_p = sub.add_parser(
        "click",
        help="AI 视觉定位并点击一个元素",
        description=(
            "截当前屏幕 → 视觉模型按自然语言描述定位元素（0-1000 归一化坐标）→"
            "换算成屏幕像素 → `adb shell input tap`。"
            "需要 ANDROID_AI_API_KEY / BASE_URL / MODEL 配置（详见 ai.py）。"
        ),
        parents=[shared],
    )
    click_p.add_argument("description", help="元素的自然语言描述（如「登录按钮」）")
    click_p.add_argument(
        "--screenshot", dest="post_shot", default=None,
        help="操作完成后额外保存一张截图到指定路径",
    )

    # ---- input ----
    input_p = sub.add_parser(
        "input",
        help="AI 视觉定位输入框并填入文本（中文 / emoji OK）",
        description=(
            "AI 视觉定位 → tap → 输入文本。"
            "非 ASCII（中文 / emoji）强制走「剪贴板 + 粘贴」方案："
            "cmd clipboard set-primary-clip + 读回校验 + keyevent 279；"
            "剪贴板方案不可用时会明确报错（提示用 ADBKeyboard），"
            "不会回退到 `adb shell input text`（中文必然乱码）。"
        ),
        parents=[shared],
    )
    input_p.add_argument("description", help="输入框的自然语言描述（如「用户名」）")
    input_p.add_argument("text", help="要输入的文本")
    input_p.add_argument(
        "--screenshot", dest="post_shot", default=None,
        help="操作完成后额外保存一张截图到指定路径",
    )

    # ---- swipe ----
    swipe_p = sub.add_parser(
        "swipe",
        help="按方向滑动（整屏 / 区域内）",
        description=(
            "无 --region：整屏滑动，按屏幕比例算起点终点（默认移动 50%）。"
            "有 --region：AI 视觉定位区域 bbox，在区域内部按方向滑动。"
            "用 `adb shell input swipe ... 300` 执行，300ms = 自然滑动速度。"
        ),
        parents=[shared],
    )
    swipe_p.add_argument("direction", choices=["up", "down", "left", "right"],
                         help="滑动方向（手指移动方向）")
    swipe_p.add_argument("-c", "--count", type=int, default=1,
                         help="滑动次数（连续滑动实现滚动更多内容），默认 1")
    swipe_p.add_argument("--region", default=None,
                         help="区域描述（如「左侧菜单」）；指定后只在区域内滑动")
    swipe_p.add_argument("--distance", type=float, default=0.5,
                         help="移动距离占屏幕/区域的比例 0.1~1.0，默认 0.5")
    swipe_p.add_argument("--screenshot", dest="post_shot", default=None,
                         help="操作完成后额外保存一张截图到指定路径")

    # ---- swipe-to ----
    swipe_to_p = sub.add_parser(
        "swipe-to",
        help="显式坐标滑动（精确定位场景）",
        description=(
            "用绝对像素坐标滑动。`adb shell input swipe x1 y1 x2 y2 duration`。"
            "无 AI，纯粹坐标。"
        ),
        parents=[shared],
    )
    swipe_to_p.add_argument("x1", type=int, help="起点像素 X")
    swipe_to_p.add_argument("y1", type=int, help="起点像素 Y")
    swipe_to_p.add_argument("x2", type=int, help="终点像素 X")
    swipe_to_p.add_argument("y2", type=int, help="终点像素 Y")
    swipe_to_p.add_argument("--duration", type=int, default=300,
                           help="滑动持续时间（ms），默认 300")
    swipe_to_p.add_argument("--screenshot", dest="post_shot", default=None,
                           help="操作完成后额外保存一张截图到指定路径")

    # ---- keyevent ----
    keyevent_p = sub.add_parser(
        "keyevent",
        help="按键（支持 30+ 别名 + 数字键码）",
        description=(
            "调 `adb shell input keyevent <code>`。"
            "常用别名：back / home / recents / menu / enter / delete / "
            "volume_up / volume_down / power / up / down / left / right / "
            "f1~f12 等；也支持直接传数字键码（如 4 = back、187 = recents）。"
            "完整别名见 src/shenle_android_cli/keyevent.py 的 KEYCODE_ALIASES。"
        ),
        parents=[shared],
    )
    keyevent_p.add_argument("code", help="数字键码或别名（back / home / recents / ...）")

    # ---- recents / notifications ----
    sub.add_parser(
        "recents",
        help="打开最近任务（KEYCODE_APP_SWITCH）",
        description="`adb shell input keyevent 187`。",
        parents=[shared],
    )
    sub.add_parser(
        "notifications",
        help="下拉通知栏",
        description="`adb shell cmd statusbar expand-notifications`（Android 8+）。",
        parents=[shared],
    )

    # ---- current-app ----
    current_app_p = sub.add_parser(
        "current-app",
        help="输出当前前台应用（package/activity）",
        description=(
            "解析 `dumpsys activity activities` 拿 mResumedActivity；"
            "拿不到回退 `dumpsys window` 的 mCurrentFocus。"
            "默认 text 输出 `<package>/<activity>` 单行；"
            "--format json 输出 `{\"package\": \"...\", \"activity\": \"...\"}`。"
        ),
        parents=[shared],
    )
    current_app_p.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="输出格式（默认 text）",
    )

    # ---- get ----
    get_p = sub.add_parser(
        "get",
        help="AI 视觉描述页面某个区域的内容（4 段：布局/图标/文字/介绍）",
        description=(
            "截当前屏幕发给视觉模型，按 ## 布局 / ## 图标 / ## 文字 / ## 介绍 四节输出。"
            "状态行打 stderr，内容打 stdout，方便脚本直接 capture stdout。"
            "跟 shenle-web-cli 的 get 命令行为一致。"
        ),
        parents=[shared],
    )
    get_p.add_argument("description", help="区域描述（如「顶部导航栏」「搜索结果列表」）")
    get_p.add_argument(
        "--screenshot", dest="post_shot", default=None,
        help="操作完成后额外保存一张截图到指定路径",
    )

    # ---- batch ----
    batch_p = sub.add_parser(
        "batch",
        help="一次截图 + 一次 AI 批量识别 + 顺序执行多个操作",
        description=(
            "适合「同一页面连续点多个元素 + 填几个文本框」的场景。\n"
            "同一页面只截一次图；click / longpress / input 描述一次发给 AI 批量识别；\n"
            "按输入顺序逐个执行（每个 op tap AI 框的中心）。\n\n"
            "语法（空格分隔；click/input 的描述可含空格）：\n"
            "  click <描述>\n"
            '  input <描述>::<文本>      （描述与文本用 :: 分隔；走 AI 定位输入框）\n'
            "  click-at <x> <y>\n"
            '  input-at <x> <y> <文本>\n'
            "  longpress <描述> [--duration 1500]\n\n"
            "注意：\n"
            "  - click / longpress / input 都走 AI 定位（与 demo_2.py 思路一致）\n"
            "  - 中文 / emoji 走 --input-method 指定的方式（默认 clipboard）\n\n"
            "示例：\n"
            "  shenle-android-cli batch click \"登录\" input \"用户名::admin\" \\\n"
            "      input \"密码::123456\" click \"登录按钮\""
        ),
        parents=[shared],
    )
    batch_p.add_argument(
        "ops", nargs="+",
        help="操作序列（按上面语法拼接）",
    )
    batch_p.add_argument(
        "--screenshot", dest="post_shot", default=None,
        help="执行完成后额外保存一张截图到指定路径",
    )

    # ---- longpress ----
    longpress_p = sub.add_parser(
        "longpress",
        help="AI 视觉定位 + 长按（默认 1500ms）",
        description=(
            "AI 定位元素中心 → 在中心点按住不放 duration 毫秒。"
            "实现：`adb shell input swipe x y x y duration`（同起点终点 = 长按）。"
        ),
        parents=[shared],
    )
    longpress_p.add_argument("description", help="元素的自然语言描述")
    longpress_p.add_argument(
        "--duration", type=int, default=1500,
        help="长按时长（ms），默认 1500",
    )
    longpress_p.add_argument(
        "--screenshot", dest="post_shot", default=None,
        help="操作完成后额外保存一张截图",
    )

    # ---- zoom / pinch ----
    zoom_p = sub.add_parser(
        "zoom",
        help="双指放大（scale > 1 = 张开 = 内容放大；scale < 1 = 合拢 = 内容缩小）",
        description=(
            "近似实现：用两个线程并行跑 `adb shell input swipe` 模拟双指。"
            "初始偏移 200px，终止偏移 = 200 * scale。"
            "部分机型可能被识别为两次连续单指滑动 —— 这是已知限制。"
        ),
        parents=[shared],
    )
    zoom_p.add_argument("x", type=int, help="双指中心 X")
    zoom_p.add_argument("y", type=int, help="双指中心 Y")
    zoom_p.add_argument(
        "--scale", type=float, required=True,
        help="终止偏移 / 初始偏移（>1 张开，<1 合拢）",
    )
    zoom_p.add_argument(
        "--duration", type=int, default=300,
        help="单指滑动持续时间（ms），默认 300",
    )

    pinch_p = sub.add_parser(
        "pinch",
        help="双指缩小（同 zoom，只是 --scale 命名习惯不同）",
        description="实现同 zoom；参数含义一致。",
        parents=[shared],
    )
    pinch_p.add_argument("x", type=int, help="双指中心 X")
    pinch_p.add_argument("y", type=int, help="双指中心 Y")
    pinch_p.add_argument(
        "--scale", type=float, required=True,
        help="终止偏移 / 初始偏移",
    )
    pinch_p.add_argument(
        "--duration", type=int, default=300,
        help="单指滑动持续时间（ms）",
    )

    # ---- shell / dump-ui / appinfo / stop ----
    shell_p = sub.add_parser(
        "shell",
        help="adb shell 透传（剩余所有参数原样传给 adb shell）",
        description=(
            "原始 adb shell 输出原样打 stdout/stderr；"
            "退出码原样返回（不像其它命令固定 0/1）。\n\n"
            "--filter PATTERN：行级包含过滤（避免 Windows 没 grep 的问题，"
            "在 cmd / PowerShell / Git Bash 上都能用）。\n"
            "例：shenle-android-cli shell dumpsys window --filter mCurrentFocus"
        ),
        parents=[shared],
    )
    shell_p.add_argument(
        "--filter", "-f", default=None,
        help="行级包含过滤（只打印包含该字符串的行，跨平台）",
    )
    shell_p.add_argument(
        "cmd", nargs="+",
        help="adb shell 命令（剩余所有参数，至少一个）",
    )

    dump_ui_p = sub.add_parser(
        "dump-ui",
        help="uiautomator dump → pull 到本地 XML",
        description=(
            "在设备上跑 `uiautomator dump /sdcard/window_dump.xml`，"
            "再 `adb pull` 到本地。XML 含完整控件树（class / text / resource-id / bounds）。"
        ),
        parents=[shared],
    )
    dump_ui_p.add_argument("path", help="输出 XML 路径（.xml）")

    appinfo_p = sub.add_parser(
        "appinfo",
        help="dumpsys package —— 输出走 stdout，[OK] 走 stderr 方便 pipe",
        description=(
            "调 `adb shell dumpsys package <pkg>`，原样输出。"
            "用 `shenle-android-cli appinfo com.x | grep versionName` 提取版本号。"
        ),
        parents=[shared],
    )
    appinfo_p.add_argument("pkg", help="包名")

    stop_p = sub.add_parser(
        "stop",
        help="am force-stop —— 杀进程（冷启动测试用）",
        description=(
            "调 `adb shell am force-stop <pkg>`。"
            "和 `close`（Home 键保留进程）不同——stop 会把进程完全杀掉，"
            "下次 launch 就是冷启动。"
        ),
        parents=[shared],
    )
    stop_p.add_argument("pkg", help="包名")

    return parser


# ---------------------------------------------------------------------------
# 子命令实现


def _resolve_device(args) -> str:
    """根据 args.serial 选定并校验一台设备，返回 serial。"""
    devices = list_devices()
    serial = getattr(args, "serial", None)
    return pick_device(devices, serial).serial


def _cmd_devices(args) -> int:
    """列设备：即使列表为空也不抛 NoDevice，由这里给出友好提示。"""
    devs = list_devices()
    if not devs:
        print("当前 adb 没有看到任何安卓设备。")
        print("（如果手机已连接，请确认 USB 调试已打开，")
        print("  并执行 adb kill-server && adb start-server 后重试）")
        return 0

    ready = [d for d in devs if d.state == "device"]
    others = [d for d in devs if d.state != "device"]
    print(f"已连接 {len(devs)} 台设备（{len(ready)} 可用）：")
    for d in devs:
        marker = "✓" if d.state == "device" else "✗"
        print(f"  {marker} {d.describe()}")
    if others:
        print()
        print("状态异常：")
        for d in others:
            print(f"  - {d.describe()}")
    return 0


def _cmd_start(args) -> int:
    """选定设备。Phase 1 不持久化，只打印。"""
    serial = _resolve_device(args)
    print(f"[shenle] 已选定设备 {serial}")
    print("[shenle] 提示：后续 launch / close 等命令若不传 -s，会用同样的规则重新选设备。")
    return 0


def _cmd_launch(args) -> int:
    """启动 App：activity 给定走 am start，没给走 monkey。"""
    serial = _resolve_device(args)
    pkg = args.pkg
    activity = args.activity

    if activity:
        # 简写 `.MainActivity` → `<pkg>/.MainActivity`；完整类名保持原样
        if not activity.startswith(".") and "." not in activity:
            activity = "." + activity
        component = f"{pkg}/{activity}"
        proc = run_adb(
            ["shell", "am", "start", "-W", "-n", component],
            serial=serial,
        )
        verb = f"am start -W -n {component}"
    else:
        # monkey 找不到 launcher activity 时 exit != 0 + stderr 是 Java 堆栈
        # （"No activities found" 或 status=-4）。从用户视角看，"包未安装"
        # 和 "包没 LAUNCHER activity" 是同一回事：PackageNotFound。
        proc = run_adb_relaxed(
            ["shell", "monkey", "-p", pkg, "-c",
             "android.intent.category.LAUNCHER", "1"],
            serial=serial,
        )
        if proc.returncode != 0:
            raise PackageNotFound(pkg)
        verb = f"monkey -p {pkg} -c LAUNCHER 1"

    summary = summarize_output(proc)
    if summary:
        print(f"[OK] launch: {pkg} (device={serial}) → {summary}")
    else:
        print(f"[OK] launch: {pkg} (device={serial}) ({verb})")
    return 0


def _cmd_close(args) -> int:
    """按 Home 键。input keyevent 3 = KEYCODE_HOME，App 进程不会被杀。"""
    serial = _resolve_device(args)
    run_adb(["shell", "input", "keyevent", "3"], serial=serial)
    print(f"[shenle] 已回到桌面（device={serial}）")
    return 0


# ---------------------------------------------------------------------------
# main


# 哪些是"基础设施类"命令（用 [shenle] 前缀），哪些是"原子操作"（用 [FAIL] 前缀）。
# 后续阶段加入 click/input/screenshot 等时会全部归到"原子操作"。
_INFRA_COMMANDS = {"devices", "start", "close"}


_HANDLERS = {
    "devices": _cmd_devices,
    "start": _cmd_start,
    "launch": _cmd_launch,
    "close": _cmd_close,
    "stop": cmd_stop,
    "screenshot": cmd_screenshot,
    "click": cmd_click,
    "input": cmd_input,
    "batch": cmd_batch,
    "longpress": cmd_longpress,
    "swipe": cmd_swipe,
    "swipe-to": cmd_swipe_to,
    "zoom": cmd_zoom,
    "pinch": cmd_pinch,
    "keyevent": cmd_keyevent,
    "recents": cmd_recents,
    "notifications": cmd_notifications,
    "current-app": cmd_current_app,
    "get": cmd_get,
    "shell": cmd_shell,
    "dump-ui": cmd_dump_ui,
    "appinfo": cmd_appinfo,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    handler = _HANDLERS[args.command]
    try:
        return handler(args)
    except CliError as e:
        if args.command in _INFRA_COMMANDS:
            print(f"[shenle] {e.message}", file=sys.stderr)
        else:
            print(f"[FAIL] {args.command}: {e.message}")
        return 1
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        if getattr(args, "debug", False):
            raise
        if args.command in _INFRA_COMMANDS:
            print(f"[shenle] 内部错误：{e}", file=sys.stderr)
            print("[shenle] 提示：用 --debug 重试可看到完整堆栈。", file=sys.stderr)
        else:
            print(f"[FAIL] {args.command}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
