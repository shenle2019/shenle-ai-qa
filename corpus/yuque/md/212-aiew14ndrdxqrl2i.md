---
title: "aa工具"
doc_id: 256210721
slug: aiew14ndrdxqrl2i
book_id: 73651885
words: 2660
updated_at: 2026-02-06T06:51:42.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/aiew14ndrdxqrl2i
---
Ability assistant（Ability助手，简称为aa），是用于启动应用和启动测试用例的工具，为开发者提供基本的应用调试和测试能力，例如启动应用组件、强制停止进程、打印应用组件相关信息等。

# aa工具命令列表

|  |  |
| --- | --- |
| 命令 | 描述 |
| -h/help | 帮助命令。用于查询aa支持的命令信息。 |
| start | 启动命令。用于启动一个应用组件，目标组件可以是FA模型的PageAbility和ServiceAbility组件，也可以是Stage模型的UIAbility和ServiceExtensionAbility组件，且目标组件相应配置文件中的exported标签不能配置为false。 |
| stop-service | 停止命令。用于停止ServiceAbility。 |
| force-stop | 强制停止进程命令。通过bundleName强制停止一个进程。 |
| test | 启动测试框架命令。根据所携带的参数启动测试框架。 |
| attach | 进入调试模式命令。通过bundleName使指定应用进入调试模式。 |
| detach | 退出调试模式命令。通过bundleName使指定应用退出调试模式。 |
| appdebug | 等待调试命令。用于设置、取消设置应用等待调试状态，以及获取处于等待调试状态的应用包名和持久化信息。等待调试状态只对debug类型应用生效。appdebug的设置命令只对单个应用生效，当重复设置时，应用包名与持久化状态会替换成最新设置内容。 |
| process | 应用调试/调优命令。对应用进行调试或调优，IDE用该命令集成调试和调优工具。 |

# 帮助命令（help）

# 启动命令（start）

启动一个应用组件，目标组件可以是FA模型的PageAbility和ServiceAbility组件，也可以是Stage模型的UIAbility和ServiceExtensionAbility组件，且目标组件相应配置文件中的exported标签不能配置为false。

**启动命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h/--help | 帮助信息。 |
| -d | 可选参数，deviceId。 |
| -a | 可选参数，abilityName。 |
| -b | 可选参数，bundleName。 |
| -m | 可选参数，moduleName。 |
| -U | 可选参数，URI。 |
| -A | 可选参数，action。 |
| -e | 可选参数，entity。 |
| -t | 可选参数，type。 |
| -S | 可选参数，调试时是否进入应用沙箱。携带该参数代表进入，不携带代表不进入。 |
| --pi | 可选参数，整型类型键值对。 |
| --pb | 可选参数，布尔类型键值对。 |
| --ps | 可选参数，字符串类型键值对。 |
| --psn | 可选参数，空字符串关键字。 |
| --wl | 可选参数，windowLeft，窗口左边距，单位px。  **约束：**  仅当2in1设备处于开发者模式下，且被启动应用采用调试签名时，该字段生效。 |
| --wt | 可选参数，windowTop，窗口上边距，单位px。  **约束：**  仅当2in1设备处于开发者模式下，且被启动应用采用调试签名时，该字段生效。 |
| --wh | 可选参数，windowHeight，窗口高度，单位px。  **约束：**  仅当2in1设备处于开发者模式下，且被启动应用采用调试签名时，该字段生效。 |
| --ww | 可选参数，windowWidth，窗口宽度，单位px。  **约束：**  仅当2in1设备处于开发者模式下，且被启动应用采用调试签名时，该字段生效。 |
| -D | 可选参数，调试模式。 |
| -p | 可选参数，调优命令。命令由调用方自定义。 |

**返回值**：

当启动成功时，返回"start ability successfully."；当启动失败时，返回"error: failed to start ability."，同时会包含相应的失败信息。

**示例**：

以隐式启动Ability为例。

说明

本例中仅介绍了部分字段的使用。关于Ability匹配的详细规则参考[显式Want与隐式Want匹配规则](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/explicit-implicit-want-mappings-V5)。

- **目标应用**：修改module.json5配置，为目标Ability配置uris。

- **拉起方应用**: 隐式启动Ability。

- 如果需要拉起应用的页面，可以使用-U命令，示例如下：

- 在上述基础上，如果需要携带参数，可以使用如下命令：

UIAbility获取传入参数示例如下：

- 如果需要拉起浏览器并跳转指定页面，可以使用-A -U命令，示例如下：

本例中以https://www.example.com为例，请根据实际情况替换为真实的网址。

# 停止命令（stop-service）

用于停止ServiceAbility。

**停止命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h/--help | 帮助信息。 |
| -d | 可选参数，deviceId。 |
| -a | 必选参数，abilityName。 |
| -b | 必选参数，bundleName。 |
| -m | 可选参数，moduleName。 |

**返回值**：

当成功停止ServiceAbility时，返回"stop service ability successfully."；当停止失败时，返回"error: failed to stop service ability."。

**示例**：

# 强制停止进程命令（force-stop）

通过bundleName强制停止一个进程。

**返回值**：

当成功强制停止该进程时，返回"force stop process successfully."；当强制停止失败时，返回"error: failed to force stop process."。

**示例**：

# 进入调试模式命令（attach）

通过bundleName使指定应用进入调试模式。

**进入调试模式命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h/--help | 帮助信息。 |
| -b | 必选参数，bundleName。 |

**返回值**：

当应用成功进入调试模式时，返回"attach app debug successfully."；当给定参数不合法时，返回"fail: unknown option."并打印帮助信息。

**示例**：

# 退出调试模式命令（detach）

通过bundleName使指定应用退出调试模式。

**退出调试模式命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h/--help | 帮助信息。 |
| -b | 必选参数，bundleName。 |

**返回值**：

当应用成功退出调试模式时，返回"detach app debug successfully."；当给定参数不合法时，返回"fail: unknown option."并打印帮助信息。

**示例**：

# 等待调试命令（appdebug）

用于设置、取消设置应用等待调试状态，以及获取处于等待调试状态的应用包名和持久化信息。等待调试状态只对debug类型应用生效。appdebug的设置命令只对单个应用生效，当重复设置时，应用包名与持久化状态会替换成最新设置内容。

**等待调试命令参数列表**

|  |  |  |
| --- | --- | --- |
| 参数 | 二级参数 | 参数说明 |
| -h/--help | - | 帮助信息。 |
| -b/--bundlename | bundleName | 为指定应用设置等待调试状态。设置时，不会进行包名合法化的校验。 |
| -p/--persist | - | 可选参数；持久化标志位，加入该参数，代表持续设置应用为等待调试状态，无论重启设备、重装应用都可以持续生效；不加入该参数，代表等待调试状态仅可以在重启设备前生效一次。需要和-b参数组合使用，例如：aa appdebug -b <bundleName> -p。 |
| -c/--cancel | - | 取消等待调试状态。 |
| -g/--get | - | 获取等待调试状态的应用包名和持久化信息。 |

**返回值**：

当执行成功时，返回"app debug successfully."；当执行失败时，返回"error: failed to app debug."；当失败原因为非开发者模式时，返回"error: not developer mode."。

**示例**：

# 应用调试/调优命令（process）

对应用进行调试或调优，IDE用该命令集成调试和调优工具。

**应用调试/调优命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h/--help | 帮助信息。 |
| -b | 必选参数，bundleName。 |
| -a | 必选参数，abilityName。 |
| -m | 可选参数，moduleName。 |
| -p | 可选参数，调优命令，与-D必须二选一。命令由调用方自定义。 |
| -D | 可选参数，调试命令，与-p必须二选一。命令由调用方自定义。 |
| -S | 可选参数，进入应用沙箱。 |

**返回值**：

当执行成功时，返回"start native process successfully."；当执行失败时，返回"error: failed to start native process."；当给定参数不合法时，返回"error: option requires a value."并打印帮助信息。

**示例**：
