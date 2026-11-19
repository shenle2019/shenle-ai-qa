# 第 24 章 · ADB 与设备连接

真机自动化的第一道坎不是写用例，而是「确认这台设备到底在不在、是什么、能不能被我碰」。这一章把这件事做成可重复的探测。

## 1. 三条命令先摸清底细

| 命令 | 回答什么 | 常见输出解读 |
| --- | --- | --- |
| `adb devices -l` | 有哪些设备、状态如何 | `device` 可用；`offline` 掉线；`unauthorized` 没点手机上的允许 |
| `adb shell getprop ro.product.model` | 型号 | `Pixel 2` 这类硬件名 |
| `adb shell wm size` / `wm density` | 分辨率、像素密度 | 有 `Override` 时以 Override 为准 |

`adb devices` 空列表的三种典型原因：线只供电不传数据、USB 调试没开、开了但没点「允许」。无线调试在 Android 11 之后要先 `adb pair`，直接扫 5555 端口是连不上的。

## 2. 把 adb 包成对象

裸写 `subprocess.run(["adb", "shell", ...])` 会让用例到处都是字符串拼接。封装后有四个好处：

- 路径只解析一次（显式传入 > PATH > 常见安装目录）；
- 会话隔离：每个 `Device` 绑定一个 serial，多设备时不会串；
- 统一超时与报错：所有失败都变成 `AdbError`，并且带 stderr，不再靠猜；
- 二进制安全：`screencap` 走 `exec-out`，不经过换行转换。

```python
from labs._shared.adb import Device

device = Device.first_online(timeout=5)
print(device.model(), device.android_version(), device.size())
```

## 3. 设备画像：一次采集，多处复用

`collect()` 把型号、系统版本、分辨率、密度、前台界面、截图结果收进一个字典；某一项失败只写进 `errors`，不影响其他项。这一点很重要：真机常常「大部分能用、个别命令抽风」，一次全崩会让人误判。

`report()` 再把它排成几行文字，失败时直接贴进报告或工单。

## 4. 端口反代：让手机访问你本机的服务

```bash
adb reverse tcp:8080 tcp:8080
```

手机里访问 `127.0.0.1:8080` 就打到电脑的 8080。这件事的意义是：被测 App 不需要改代码去连局域网 IP，联调环境随身携带。

## 5. 本章实操

`labs/ch24-adb/`：

- `probe.py`：`collect()` / `report()` / `quick_check()`
- `demo_probe.py`：接上手机打印真实画像，没接就打印排查顺序
- `test_probe.py`：6 条，其中 1 条标 `device`，只有真机在才会跑

```bash
.\.venv\Scripts\python.exe labs/ch24-adb/demo_probe.py
.\.venv\Scripts\python.exe -m pytest labs/ch24-adb -q
```

## 常见坑

1. **看到 `unauthorized` 就以为设备坏了**：手机此时正弹着授权框，点允许即可；勾「一律允许」后不会再问。
2. **截图拿到的字节不是 PNG**：用了 `adb shell screencap -p` 而非 `exec-out`，换行被改写导致文件损坏。封装里判断了 PNG 魔数，坏的就报错。
3. **`wm size` 读到物理分辨率**：开发者选项里改过分辨率时会有 `Override size`，要优先用它，否则坐标全偏。
4. **多设备时命令乱跑**：没带 `-s serial`，adb 会对第一台执行，结果和现象对不上。

## 自测

1. `adb devices` 显示 `offline` 与 `unauthorized` 分别该做什么？
2. 为什么取截图要用 `exec-out screencap` 而不是 `shell screencap -p`？
3. `wm size` 同时有 `Physical` 与 `Override` 时为什么用后者？
4. 多设备环境下，封装里哪一行保证了命令只打到目标设备？

## 附：自测答案

1. `offline` 是连接断了，重插线或 `adb kill-server && adb start-server`；`unauthorized` 是手机没授权，点亮屏幕点「允许 USB 调试」。
2. `shell` 会经过 PTY，`\n` 被改写成 `\r\n`，PNG 二进制被破坏；`exec-out` 是原始字节流。
3. App 渲染用的是 Override 后的逻辑分辨率，坐标换算必须跟它一致，否则点击位置偏移。
4. `Device._base()` 里带上 `-s <serial>`，所有子命令都基于它拼装。

## 学生常问

**Q：为什么不用 Appium？**

A：这一阶段的目标是理解「设备是怎么被驱动的」。adb 是底座，Appium 在它上面又叠了一层服务与协议；先把 dump、input、screencap 用熟，换任何框架都能对上号。等需要跨平台控件查找（XCUITest、Windows）时再上 Appium 更划算。

**Q：真机忽然连不上，怎么快速判断是环境还是用例的问题？**

A：先跑 `demo_probe.py`。它能出型号就是环境好的，问题在用例；它报 `adb devices` 为空就是环境问题。这个脚本就是给自己留的「第一层排除法」。

**Q：无线调试为什么扫不到 5555？**

A：Android 11 起无线调试要先 `adb pair <ip>:<port> <code>` 配对，配对用的端口每次随机，不是 5555。5555 是老的 `adb tcpip 5555` 方式，需要先插线开一次。

## 面试题

**Q：怎么保证设备自动化的稳定性？**

A：三层：连接层（在线检测 + 掉线重连）、操作层（等待代替 sleep、定位带兜底）、证据层（失败截图 + logcat）。缺任何一层，失败都会变成「不知道发生了什么」。

**Q：多设备并发时要注意什么？**

A：serial 必须显式绑定；端口反代每个设备各做一次；截图与日志目录按 serial 分；不要共用同一个后端端口，除非你能接受互相干扰。

**Q：为什么要把「设备画像」单独做一层？**

A：它把不稳定因素（连接、分辨率、系统版本）从用例里剥离出来。用例失败时先看画像是否正常，能快速区分「环境不对」和「断言不对」。

## 延伸知识

- `adb shell settings get global device_provisioned`：判断设备是否已过开机向导。
- `adb shell dumpsys window | grep mCurrentFocus`：不用 dump 也能知道前台是哪个界面。
- `adb exec-out screencap -p > shot.png`：命令行直接存图，排查问题时最快。
- `adb shell getprop ro.build.version.sdk`：按 API 号而不是版本号写兼容分支更稳。
