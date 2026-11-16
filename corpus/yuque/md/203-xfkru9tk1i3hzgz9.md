---
title: "hitrace"
doc_id: 256210775
slug: xfkru9tk1i3hzgz9
book_id: 73651885
words: 1606
updated_at: 2026-02-06T06:51:59.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/xfkru9tk1i3hzgz9
---
HiTrace为开发者提供业务流程调用链跟踪的维测接口。通过使用该接口所提供的功能，帮助开发者迅速获取指定业务流程调用链的运行日志，定位跨设备、跨进程、跨线程的故障问题。

# 环境要求

- 根据hdc命令行工具指导，完成[环境准备](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/hdc-V5#环境准备)。
- 正常连接设备。

# 命令行说明

|  |  |
| --- | --- |
| 命令 | 含义说明 |
| -h | 帮助命令。 |
| -l | 查看tag列表。 |
| --trace\_begin | 开始捕获trace。 |
| --trace\_finish | 结束捕获trace。 |
| --trace\_dump | 导出trace信息。 |
| -b N | 设置用于存储和读取trace的缓冲区大小(buffer size KB)。默认的缓冲区大小为2048 KB。 |
| -t N | 设置hitrace运行时长，单位为秒（默认为5秒），取决于分析所需的时间。 |
| -o | 文件名指定目标文件的名称（默认为stdout）。 |
| -z | 压缩捕获的跟踪。 |
| --trace\_clock | 设置向trace添加时间戳的时钟类型，可以是引导（默认）、全局、单声道、正常运行时间或性能。 |
| --trace\_finish\_nodump | 停止捕获trace时不打印trace信息。 |
| --start\_bgsrv | 开启快照模式trace采集服务。 |
| --dump\_bgsrv | 触发快照模式trace输出到文件。 |
| --stop\_bgsrv | 关闭快照模式trace采集服务。 |

说明

快照模式定义为固定trace标签的trace采集服务，默认情况不落盘，开发者可通过 --dump\_bgsrv 命令触发当前时刻的trace转储，trace为二进制格式，文件默认生成在 /data/log/hitrace 目录下，文件命名格式为trace-YYMMDDHHmmSS@[BOOT\_TIME].sys。可通过[smpartperf在线工具](https://www.smartperf.host)进行查看。

# 常用命令

在hdc shell执行如下命令：

1. 查看hitrace包含的tag。

**使用样例：**

1. 开始抓指定tag的trace。

**使用样例：**

1. 结束抓trace。

**使用样例1：**

**使用样例2：**

1. 设置抓trace的一些信息：hitrace -b 10240 -t 10 -o /data/local/tmp/test2.ftrace app ability。

**使用样例：**

- 设置缓冲区大小为10240KB；
- 设置抓trace时间为10s；
- 设置抓完trace后文件存储在/data/local/tmp/test1.htrace中；
- 抓取app/ability两个tag的trace；

1. 导出trace信息。

**使用样例1：**

**使用样例2：**

1. 开启快照模式trace采集服务。

**使用样例：**

1. 快照模式导出trace。

默认将trace信息保存至/data/log/hitrace/文件夹下，文件命名格式为trace-YYMMDDHHmmSS@[BOOT\_TIME].sys，抓到的是二进制trace。可通过[smpartperf在线工具](https://www.smartperf.host)进行查看。

**使用样例：**

1. 关闭快照模式trace采集服务。

**使用样例：**

1. 抓取trace后进行压缩。

**使用样例：**

1. 设置trace的输出时钟为boot(设备系统时间)。

**使用样例：**

1. 结束抓trace，取消trace信息打印在命令行窗口。

**使用样例：**
