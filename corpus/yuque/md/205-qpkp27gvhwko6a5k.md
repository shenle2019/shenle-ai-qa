---
title: "hilog"
doc_id: 256210761
slug: qpkp27gvhwko6a5k
book_id: 73651885
words: 2815
updated_at: 2026-02-06T06:51:55.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/qpkp27gvhwko6a5k
---
HiLog日志系统，提供给系统框架、服务、以及应用，用于打印日志，记录用户操作、系统运行状态等。开发者可以通过hilog命令行查询相关日志信息。

# 环境要求

- 根据hdc命令行工具指导，完成[环境准备](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/hdc-V5#环境准备)。
- 正常连接设备。

# 命令行说明

|  |  |  |  |
| --- | --- | --- | --- |
| 短选项 | 长选项 | 参数 | 说明 |
| -h | --help |  | 帮助命令。 |
| 缺省 | 缺省 |  | 阻塞读日志，不退出。 |
| -x | --exit |  | 非阻塞读日志，读完退出。 |
| -g |  |  | 查询buffer的大小，配合-t指定某一类型使用，默认app和core。 |
| -G | --buffer-size | <size> | 设置指定<type>日志类型缓冲区的大小，配合-t指定某一类型使用，默认app和core， 可使用B/K/M为单位，范围为64K-16M。 |
| -r |  |  | 清除buffer日志，配合-t指定某一类型使用，默认app和core。 |
| -k |  | <on/off> | Kernel日志读取开关控制。 |
|  |  | on | 打开读取kernel日志。 |
|  |  | off | 关闭读取kernel日志。 |
| -s | --statistics |  | 查询统计信息，需配合-t或-D使用。 |
| -S |  |  | 清除统计信息，需配合-t或-D使用。 |
| -Q |  | <control-type> | 流控缺省配额开关控制。 |
|  |  | pidon | 进程流控开关打开。 |
|  |  | pidoff | 进程流控开关关闭。 |
|  |  | domainon | domain流控开关打开。 |
|  |  | domainoff | domain流控开关关闭。 |
| -L | --level | <level> | 指定级别的日志，示例：-L D/I/W/E/F。 |
| -t | --type | <type> | 指定类型的日志，示例：-t app/core/init/only\_prerelease。app为应用日志，core为系统日志，init为启动日志，only\_prerelease为仅在系统release版本前打印的日志，应用开发者无需关注。 |
| -D | --domain | <domain> | 指定domain。 |
| -T | --tag | <tag> | 指定tag。 |
| -a | --head | <n> | 只显示前<n>行日志。 |
| -z | --tail | <n> | 只显示后<n>行日志。 |
| -P | --pid | <pid> | 标识不同的pid。 |
| -e | --regex | <expr> | 只打印日志消息与<expr>匹配的行，其中<expr>是一个正则表达式。 |
| -f | --filename | <filename> | 设置落盘的文件名。 |
| -l | --length | <length> | 设置落盘的文件大小，需要大于等于64K。 |
| -n | --number | <number> | 设置落盘文件的个数。 |
| -j | --jobid | <jobid> | 设置落盘任务的ID。 |
| -w | --write | <control> | 落盘任务控制。 |
|  |  | query | 落盘任务查询。 |
|  |  | start | 落盘任务开始，命令行参数为文件名、单文件大小、落盘算法、rotate文件数目。 |
|  |  | stop | 落盘任务停止。 |
|  |  | refresh | 刷新缓冲区的日志到落盘文件。 |
|  |  | clear | 删除已经落盘的日志文件。 |
| -m | --stream | <algorithm> | 落盘方式控制。 |
|  |  | none | 无压缩方式落盘。 |
|  |  | zlib | zlib压缩算法落盘，落盘文件为.gz。 |
|  |  | zstd | zstd压缩算法落盘，落盘文件为.zst。 |
| -v | --format | <format> |  |
|  |  | time | 显示本地时间。 |
|  |  | color | 显示不同级别显示不同颜色，参数缺省级别颜色模式处理（按黑白方式）。 |
|  |  | epoch | 显示相对1970时间。 |
|  |  | monotonic | 显示相对启动时间。 |
|  |  | usec | 显示微秒精度时间。 |
|  |  | nsec | 显示纳秒精度时间。 |
|  |  | year | 显示将年份添加到显示的时间。 |
|  |  | zone | 显示将本地时区添加到显示的时间。 |
|  |  | wrap | 日志换行显示时，新行不增加时间戳等前缀。 |
| -b | --baselevel | <loglevel> | 设置可打印日志的最低等级：D(DEBUG)/I(INFO)/W(WARN)/E(ERROR)/F(FATAL)。 |

# 常用命令

## 查看帮助命令

**使用样例：**

## 非阻塞读日志

**使用样例：**

## 查看日志缓冲区大小

**使用样例：**

## 修改日志缓冲区大小

**使用样例：**

## 清除缓冲区日志

**使用样例：**

## 内核日志读取开关控制

**使用样例：**

## 查询统计信息

**使用样例：**

**统计信息说明**

## 清除统计信息

**使用样例：**

## 进程流控开关

**使用样例：**

## domain流控开关

**使用样例：**

## 查看指定级别日志

**使用样例：**

## 查看指定类型日志

**使用样例：**

## 查看指定domain日志

**使用样例：**

## 查看指定TAG日志

**使用样例：**

## 查看缓冲区前n行日志

**使用样例：**

## 查看缓冲区后n行日志

**使用样例：**

## 查看指定进程日志

**使用样例：**

## 查看符合正则匹配关键字的日志

**使用样例：**

## 查看、设置落盘任务

说明

查询当前任务： hilog -w query

开启hilog落盘任务，并且设置落盘文件数量为1000个： hilog -w start -n 1000

开启kmsglog落盘任务，并且设置落盘文件数量为100个： hilog -w start -n 100 -t kmsg

停止当前落盘任务： hilog -w stop

开启kmsglog落盘任务，并且设置落盘规则，其中压缩方式可以为zlib，zstd，none。以设置规则为例：文件名为kmsglog，大小为2M，数量为100个, 其压缩方式为zlib压缩，命令行为： hilog -w start -t kmsg -f kmsglog -l 2M -n 100 -m zlib

**使用样例：**

## 设置日志显示格式

**使用样例：**

## 设置可打印日志的最低等级

**使用样例：**
