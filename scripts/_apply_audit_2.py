"""应用 ch16–ch31 审校报告的 8 条 ERROR 与 4 条 UNCERTAIN。"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FIXES = [
    (
        "notes/ch16-web-basics.md",
        'A：`<div><span>登录</span></div>` 里，`get_by_text("登录")` 可能同时命中 div 和 span。加 `exact=True` 只解决「部分匹配」，解决「祖先也含这段文字」要用 `page.get_by_text("登录", exact=True).locator("span")`，或者干脆换成 role/testid。',
        'A：Text 引擎默认只命中「包含这段文字的最小元素」：`<div><span>登录</span></div>` 只命中 span（实测 count=1），不会命中 div；只有当文字被拆到多个子节点（`<div><span>登</span><span>录</span></div>`）时才会命中父节点。要限定到某个后代，直接 `page.get_by_text("登录").locator("span")`，能换 role/testid 就别靠文本。',
    ),
    (
        "notes/ch17-po.md",
        "`expect_path` 里为什么要 `re.escape`：中文和 `?` 在正则里是元字符，不转义会匹配到别的路径。",
        "`expect_path` 里为什么要 `re.escape`：`?`、`.`、`+`、`(` 是正则元字符（中文不是），URL 的查询串最常带 `?`；不转义会把它当正则语法，匹配到别的路径。",
    ),
    (
        "notes/ch17-po.md",
        "- **别在页面类里缓存 locator 实例**：Playwright 的 locator 是惰性的，缓存本身没错，但元素被替换后旧 locator 仍指向旧节点——需要缓存就缓存「选择器字符串」。",
        "- **locator 实例可以缓存**：Locator 只保存选择器与过滤链，每次动作/断言都重新解析 DOM，元素被替换后仍命中新节点（实测）。会「指向旧节点」的是 ElementHandle——那个才该换成 locator 或缓存选择器字符串。",
    ),
    (
        "notes/ch18-locators.md",
        "- **YAML 里 `text: 登录` 会被当成布尔**：`on/off/yes/no` 在 YAML 1.1 里是布尔值，`登录` 不是，但 `true` 是。统一加引号最省事。",
        "- **YAML 里 `text: on` 会被当成布尔**：`on/off/yes/no` 在 YAML 1.1 里是布尔值，`text: 登录` 不会（实测 safe_load 返回字符串）。这类取值统一加引号最省事。",
    ),
    (
        "notes/ch18-locators.md",
        "2. 不该缓存 locator 对象，缓存「规格」即可。页面重渲染后旧 locator 仍指向旧节点，缓存对象会把「偶发失败」变成「稳定失败」。",
        "2. locator 对象可以直接缓存：Locator 每次动作都重新解析 DOM，重渲染后仍命中新节点；会「指向旧节点」的是 ElementHandle。把「定位规格」放配置里只是换一种写法，不是必须。",
    ),
    (
        "notes/ch18-locators.md",
        "- **`data-testid` 的约定**：Playwright 默认找 `data-testid`，也支持 `testIdAttribute: 'data-qa'` 改前缀；前后端约定一个前缀，比每次协商选择器省事。",
        '- **`data-testid` 的约定**：Playwright 默认找 `data-testid`，Python 里用 `test_id_attribute="data-qa"` 换属性名（JS 写 `testIdAttribute`，它指的是属性名不是前缀）；前后端约定一个属性名，比每次协商选择器省事。',
    ),
    (
        "notes/ch19-fixtures.md",
        "两块：**cookie** 和 **localStorage**。所以它既能恢复「服务端会话」，也能恢复「前端自己存的 token」。",
        "顶层两块：**cookies** 和 **origins**（`origins` 里带 `localStorage`，Playwright 1.51 起还包含 `indexedDB`）。所以它既能恢复「服务端会话」，也能恢复「前端自己存的 token」。",
    ),
    (
        "notes/ch23-framework.md",
        "A：四件事：固定浏览器版本（`playwright install --with-deps chromium` 锁版本）、固定测试数据（唯一前缀 + 清理）、给整批设超时、失败自动上传截图与 trace。缺一件就会开始出现「本地过 CI 不过」。",
        "A：四件事：固定浏览器版本——锁的是 `playwright` 包版本（如 `playwright==1.65.2`）并缓存 `PLAYWRIGHT_BROWSERS_PATH`，`playwright install chromium` 只装该包绑定的那版，包一升它就跟着换；固定测试数据（唯一前缀 + 清理）；给整批设超时；失败自动上传截图与 trace。缺一件就会开始出现「本地过 CI 不过」。",
    ),
    (
        "notes/ch24-adb.md",
        "`adb devices` 空列表的三种典型原因：线只供电不传数据、USB 调试没开、开了但没点「允许」。",
        "`adb devices` 空列表的典型原因：线只供电不传数据、USB 调试没开、驱动或 adb 服务没起来；没点「允许」的设备会以 `unauthorized` 出现在列表里，不会消失。",
    ),
    (
        "notes/ch24-adb.md",
        "4. **多设备时命令乱跑**：没带 `-s serial`，adb 会对第一台执行，结果和现象对不上。",
        "4. **多设备时命令直接失败**：没带 `-s serial`（或 `ANDROID_SERIAL`），adb 报 `more than one device/emulator` 并退出，一台都不会执行——是失败，不是误跑。",
    ),
    (
        "notes/ch29-stability.md",
        "- `ANR in`：主线程卡住超过 5 秒。",
        "- `ANR in`：主线程被阻塞到超时——输入事件 5 秒、前台 Broadcast 10 秒、前台 Service 20 秒，三类都会 ANR。",
    ),
    (
        "notes/ch29-stability.md",
        "- `--time` 参数让 logcat 带时间戳，和截图时间对得上。",
        "- `-v time`（或 `-v threadtime`）让每行带时间戳，和截图时间对得上。",
    ),
]


def main() -> None:
    for rel, old, new in FIXES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        assert old in text, f"{rel} 找不到：{old[:36]!r}"
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        print(f"ok {rel} <- {old[:30]!r}")


if __name__ == "__main__":
    main()
