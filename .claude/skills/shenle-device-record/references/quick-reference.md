# shenle-device-record 一页速查

shenle-device-record 的高频命令与对照表，动手前先扫一眼。

| 想干什么 | 命令 |
| --- | --- |
| 看有没有设备 | `adb devices` |
| 单次采集 | `shenle-device-record record` |
| 连续采集 | `shenle-device-record serve` |
| 指定设备 | `shenle-device-record record -s <serial>` |
| 看版本 | `shenle-device-record --version` |
| 手动抓一屏 | `adb -s <serial> exec-out screencap -p > screen.png` |
