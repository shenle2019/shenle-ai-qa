---
title: "bm工具"
doc_id: 256210717
slug: gdfzp9q8ar0als1n
book_id: 73651885
words: 8549
updated_at: 2026-02-06T06:51:40.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/gdfzp9q8ar0als1n
---
Bundle Manager（包管理工具，简称bm）是实现应用安装、卸载、更新、查询等功能的工具，bm为开发者提供基本的应用安装包的调试能力。

# bm工具命令列表

|  |  |
| --- | --- |
| 命令 | 描述 |
| help | 帮助命令，用于查询bm支持的命令信息。 |
| install | 安装命令，用于安装应用。 |
| uninstall | 卸载命令，用于卸载应用。 |
| dump | 查询命令，用于查询应用的相关信息。 |
| clean | 清理命令，用于清理应用的缓存和数据。此命令在root版本下可用，在user版本下打开开发者模式可用。其它情况不可用。 |
| get | 获取udid命令，用于获取设备的udid。 |
| quickfix | 快速修复相关命令，用于执行补丁相关操作，如补丁安装、补丁查询。 |
| compile | 应用执行编译AOT命令。 |
| copy-ap | 把应用的ap文件拷贝到/data/local/pgo目录下，供shell用户读取文件。 |
| dump-dependencies | 查询应用依赖的模块信息。 |
| dump-shared | 查询应用间HSP应用信息。 |
| dump-overlay | 打印overlay应用的overlayModuleInfo。 |
| dump-target-overlay | 打印目标应用的所有关联overlay应用的overlayModuleInfo。 |

# 帮助命令

# 安装命令

**安装命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -p | 必选参数，指定路径和多个HAP同时安装。 |
| -u | 可选参数，给指定用户安装一个HAP。默认安装到当前所有用户上。 |
| -r | 可选参数，覆盖安装一个HAP。默认值为覆盖安装。 |
| -s | 根据场景判断，安装应用间HSP时为必选参数，其他场景为可选参数。安装应用间共享库， 每个路径目录下只能存在一个同包名的HSP。 |
| -w | 可选参数，安装HAP时指定bm工具等待时间，最小的等待时长为5s，最大的等待时长为600s, 默认缺省为5s。 |

示例：

# 卸载命令

**卸载命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -n | 必选参数，指定Bundle名称卸载应用。 |
| -m | 可选参数，指定卸载应用的一个模块。默认卸载所有模块。 |
| -u | 可选参数，指定用户卸载应用。默认卸载当前所有用户下该应用。 |
| -k | 可选参数，卸载应用时保存应用数据。默认卸载应用时不保存应用数据。 |
| -s | 根据场景判断，安装应用间HSP时必选参数，其他场景为可选参数。卸载指定的共享库。 |
| -v | 可选参数，指定共享包的版本号。默认卸载同包名的所有共享包。 |

示例：

# 查询应用信息命令

**查询命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -a | 可选参数，查询系统已经安装的所有应用。 |
| -n | 可选参数，查询指定Bundle名称的详细信息。 |
| -s | 可选参数，查询指定Bundle名称下的快捷方式信息。 |
| -d | 可选参数，查询指定设备中的包信息。默认查询当前设备。 |
| -u | 可选参数，查询指定用户下指定Bundle名称的详细信息。默认查询当前设备上的所有用户。 |

示例：

# 清理命令

**清理命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -c -n | -n为必选参数，-c为可选参数。清除指定Bundle名称的缓存数据。 |
| -d -n | -n为必选参数，-d为可选参数。清除指定Bundle名称的数据目录。 |
| -i | 可选参数，清除分身应用的数据目录。默认为0。 |
| -u | 可选参数，清除指定用户下Bundle名称的缓存数据。默认为当时活跃用户。 |

示例：

# 获取udid命令

在 AGC 平台中添加测试时，需要获取设备的 uuid，就需要通过该命令来完成。

AGC：<https://developer.huawei.com/consumer/cn/service/josp/agc/index.html#/>

**获取udid命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -u | 必选参数，获取设备的udid。 |

示例：

# 快速修复命令

注：hqf文件制作方式可参考[HQF打包指令](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/packing-tool-V5#hqf打包指令)。

**快速修复命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -a -f | -a为可选参数，指定-a后，-f为必选参数。执行快速修复补丁安装命令，file-path对应hqf文件，支持传递1个或多个hqf文件，或传递hqf文件所在的目录。 |
| -q -b | -q为可选参数，指定-q后，-b为必选参数，未指定-q。根据包名查询补丁信息。 |
| -r -b | -r为可选参数，指定-r后，-b为必选参数。根据包名卸载未使能的补丁。 |
| -t | 可选参数，快速修复应用到指定目标路径。 |
| -d | 可选参数，应用快速修复调试模式。 |

示例：

# 共享库查询命令

**共享库查询命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -a | 可选参数，查询系统中已安装所有共享库。 |
| -n | 可选参数，查询指定共享库包名的详细信息。 |
| -m | 可选参数，查询指定共享库包名和模块名的详细信息。 |

示例：

# 共享库依赖关系查询命令

显示指定应用和指定模块依赖的共享库信息。

**共享库依赖关系查询命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -n | 必选参数，查询指定共享库包名的详细信息。 |
| -m | 可选参数，查询指定应用指定模块依赖的共享库信息。 |

示例：

# 应用执行编译AOT命令

应用执行编译AOT命令。

**compile命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -a | 可选参数，编译所有应用。 |
| -m | 可选参数，可选值为partial或者full。根据包名编译应用。 |
| -r | 可选参数，移除应用的结果。 |

示例：

# 拷贝ap文件命令

拷贝ap文件到指定应用的/data/local/pgo路径。

**copy-ap命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -a | 可选参数，默认所有包相关ap文件。拷贝所有包相关ap文件。 |
| -n | 可选参数，默认当前应用包名。根据包名拷贝对应包相关的ap文件。 |

示例：

# 查询overlay应用信息命令

打印overlay应用的overlayModuleInfo。

**dump-overlay命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -b | 必选参数，获取指定应用的所有OverlayModuleInfo信息。 |
| -m | 可选参数，默认当前应用主模块名。根据指定的包名和module名查询OverlayModuleInfo信息。 |
| -t | 可选参数，根据指定的包名和目标module名查询OverlayModuleInfo信息。 |
| -u | 可选参数，默认为当前活跃用户。根据指定的包名、目标module名和用户查询OverlayModuleInfo信息。 |

示例：

# 查询应用的overlay相关信息命令

查询目标应用的所有关联overlay应用的overlayModuleInfo信息。

**dump-target-overlay命令参数列表**

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -b | 必选参数，获取指定应用的所有OverlayBundleInfo信息。 |
| -m | 可选参数，默认当前应用主模块名。根据指定的包名和module名查询OverlayBundleInfo信息。 |
| -u | 可选参数，默认为当前活跃用户。根据指定的包名、目标module名和用户查询OverlayBundleInfo信息。 |

示例：

# bm工具错误码

## 9568320 签名文件不存在

**错误信息**

Failed to install bundle, no signature file.

**错误描述**

用户安装未签名的HAP包。

**可能原因**

HAP包未经签名认证。

**处理步骤**

1. 使用[自动签名](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5#section18815157237)。在连接设备后，重新为应用进行签名。
2. 使用手动签名，请参考[手动签名](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5#section297715173233)。

## 9568347 解析本地so文件失败

**错误信息**

Error: install parse native so failed.

**错误描述**

在启动调试或运行C++应用/服务时，安装HAP包出现错误，提示“error: install parse native so failed”错误信息。

**可能原因**

设备支持的Abi类型与C++工程中配置的Abi类型不匹配。

**处理步骤**

1. 将设备与DevEco Studio进行连接。
2. 打开命令行工具，并进入SDK安装目录下的toolchains{版本号}目录下。

1. 执行如下命令，查询设备支持的Abi列表，返回结果为default/armeabi-v7a/armeabi/arm64-v8a/x86/x86\_64中的一个或多个Abi类型。

1. 根据查询返回结果，检查[模块级build-profile.json5](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-hvigor-compilation-options-customizing-sample-V5#section4322212200)文件中的“abiFilters”参数中的配置，规则如下：

- 若返回结果为default，请执行如下命令，查询是否存在lib64文件夹。

- 存在lib64文件夹：则“abiFilters”参数中需要包含arm64-v8a类型。
- 不存在lib64文件夹：则“abiFilters”参数中需要至少包含armeabi/armeabi-v7a中的一个类型。

- 若返回结果为armeabi-v7a/armeabi/arm64-v8a/x86/x86\_64中的一个或多个，需要在“abiFilters”参数中至少包含返回结果中的一个Abi类型。

## 9568344 解析配置文件失败

**错误信息**

Error: install parse profile prop check error.

**错误描述**

在启动调试或运行应用/服务时，安装HAP出现错误，提示“error: install parse profile prop check error”错误信息。

**可能原因**

应用使用了应用特权，但应用的签名文件发生变化后未将新的签名指纹重新配置到设备的特权管控白名单文件install\_list\_capability.json中。

**处理步骤**

1. 获取新的签名指纹。

a. 在[项目级build-profile.json5](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-hvigor-compilation-options-customizing-sample-V5#section1448071082016)文件中，signingConfigs字段内的profile的值即为签名文件的存储路径。

b. 打开该签名文件（后缀为.p7b），打开后在文件内搜索“development-certificate”，将“-----BEGIN CERTIFICATE-----”和“-----END CERTIFICATE-----”以及中间的信息拷贝到新的文本中，注意换行并去掉换行符，保存为一个新的.cer文件，如命名为xxx.cer。

新的.cer文件格式如下图（仅作为格式示意，内容以实际为准）：

c. 使用keytool工具（在DevEco Studio安装目录下的jbr/bin文件夹内），执行如下命令通过.cer文件获取证书指纹的SHA256值。

d. 将证书指纹中SHA256的内容去掉冒号，即为最终要获得的签名指纹。

如SHA256值为下图（仅作为格式示意，内容以实际为准）：

去掉冒号后的签名指纹为：5753DDBC1A8EF88A62058A9FC4B6AFAFC1C5D8D1A1B86FB3532739B625F8F3DB

1. 获取设备的特权管控白名单文件install\_list\_capability.json。

a. 连接设备。

b. 执行如下命令查看设备的特权管控白名单文件install\_list\_capability.json。

设备上install\_list\_capability.json的位置通常为以下目录地址，通过bundleName找到对应的配置文件：

c. 执行如下命令拉取install\_list\_capability.json。

1. 将步骤1获取到的签名指纹配置到install\_list\_capability.json文件的app\_signature中，注意要配置到对应的bundleName下。

1. 将修改后的install\_list\_capability.json文件重新推到设备上，并重启设备。

1. 设备重启后，重新安装新的应用即可。

## 9568305 依赖的模块不存在

**错误信息**

Error: dependent module does not exist.

**错误描述**

在启动调试或运行应用/服务时，安装HAP出现错误，提示“error: dependent module does not exist”错误信息。

**可能原因**

运行/调试的应用依赖的动态共享包（SharedLibrary）模块未安装导致安装报错。

**处理步骤**

1. 先安装依赖的动态共享包（SharedLibrary）模块，再在应用运行配置页勾选Keep Application Data，点击OK保存配置，再运行/调试。

1. 在运行配置页，选择Deploy Multi Hap标签页，勾选Deploy Multi Hap Packages，选择依赖的模块，点击OK保存配置，再进行运行/调试。

## 9568259 安装解析配置文件缺少字段

**错误信息**

Error: install parse profile missing prop.

**错误描述**

在启动调试或运行应用/服务时，安装HAP出现错误，提示“error: install parse profile missing prop”错误信息。

**可能原因**

配置文件app.json5和module.json5中必填字段缺失。

**处理步骤**

- 方法1：请参考[app.json5配置文件](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/app-configuration-file-V5)和[module.json5配置文件](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/module-configuration-file-V5)查看并补充必填字段。
- 方法2：通过hilog日志判断缺失字段。

开启落盘命令：

落盘位置：/data/log/hilog

打开日志查看“profile prop %{public}s is mission”。如“profile prop icon is mission”表示“icon”字段缺失。

## 9568258 安装应用的releaseType与已安装应用的releaseType不相同

**错误信息**

Error: install releaseType target not same.

**错误描述**

在启动调试或运行应用/服务时，安装HAP出现错误，提示“error: install releaseType target not same”错误信息。

**可能原因**

设备上已安装的旧HAP和现在要安装的新HAP所使用的SDK中的releaseType值不一样。

**处理步骤**

1. 请先卸载设备上已安装的HAP，再安装新的HAP。

## 9568322 由于应用来源不可信，签名验证失败

**错误信息**

Error: signature verification failed due to not trusted app source.

**错误描述**

在启动调试或运行应用/服务时，安装HAP出现错误，提示“error: signature verification failed due to not trusted app source”错误信息。

**可能原因**

- 场景一：签名中未包含该调试设备的UDID。
- 场景二：签名时使用了[发布证书和发布profile文件](https://developer.huawei.com/consumer/cn/doc/app/agc-help-releaseharmony-0000001933963166)。发布证书签名的应用不能启动调试或运行。

**处理步骤**

- 场景一：

1. 使用[自动签名](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5#section18815157237)。在连接设备后，重新为应用进行签名。
2. 如果使用的是手动签名，对于HarmonyOS应用，请参考[手动签名](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5#section297715173233)，在UnsgnedDebugProfileTemplate.json文件中添加该调试设备的**UDID**。

- 场景二：使用[调试证书和调试profile文件](https://developer.huawei.com/consumer/cn/doc/app/agc-help-debug-app-0000001914423098)重新签名应用。

## 9568289 权限请求失败导致安装失败

**错误信息**

Error: install failed due to grant request permissions failed.

**错误描述**

在启动调试或运行应用/服务时，安装HAP出现错误，提示“error: install failed due to grant request permissions failed”错误信息。

**可能原因**

默认应用等级为normal，只能使用normal等级的权限，如果使用了system\_basic或system\_core等级的权限，将导致报错。

**处理步骤**

1. 在UnsgnedDebugProfileTemplate.json文件中修改APL等级，调整成system\_basic或system\_core等级，重新签名打包即可。

## 9568297 由于设备sdk版本较低导致安装失败

**错误信息**

Error: install failed due to older sdk version in the device.

**错误描述**

在启动调试或运行应用/服务时，安装HAP出现错误，提示“error: install failed due to older sdk version in the device”错误信息。

**可能原因**

该问题是由于编译打包所使用的SDK版本与设备镜像版本不匹配。

**处理步骤**

- 场景一：设备上的镜像版本低于编译打包的SDK版本，请更新设备镜像版本。查询设备镜像版本命令：

如果镜像提供的api版本为10，且应用编译所使用的SDK版本也为10，仍出现该报错，可能是由于镜像版本较低，未兼容新版本SDK校验规则，请将镜像版本更新为最新版本。

- 场景二：对于需要运行在HarmonyOS设备上的应用，请确认runtimeOS已改为HarmonyOS。

## 9568332 签名不一致导致安装失败

**错误信息**

Error: install sign info inconsistent.

**错误描述**

在启动调试或运行应用/服务时，安装HAP出现错误，提示“error: install sign info inconsistent”错误信息。

**可能原因**

设备上已安装的应用与新安装的应用中签名不一致或者多个包（HAP和HSP）之间的签名存在差异。如果在“Edit Configurations”中勾选了“Keep Application Data”（即不卸载应用，直接覆盖安装），并且重新进行了签名，将导致该报错。

**处理步骤**

1. 请卸载设备上已安装的应用，或取消勾选“Keep Application Data”后，重新安装新的应用。
2. 如果是因不同团队提供的HSP导致签名不一致问题，可以采用[集成态HSP](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/integrated-hsp-V5)的方式统一提供HSP；在多HAP包的情况下，必须确保所有HAP包的签名一致。

## 9568329 签名信息验证失败

**错误信息**

Error: verify signature failed.

**错误描述**

签名信息中的包名与应用的包名（bundleName）不一致。

**可能原因**

- 场景一：用户导入了三方提供的HSP模块，且该HSP既非[集成态HSP](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/integrated-hsp-V5)，又非同包名的HSP，造成包名不一致。
- 场景二：用户使用了错误的签名文件（后缀为.p7b）进行签名，造成包名不一致。

**处理步骤**

- 场景一：HSP只能给同包名的应用使用，只有集成态HSP可以给不同包名的应用使用。需要用户与三方开发者确认，三方开发者应提供集成态HSP、或同包名的HSP给用户使用。
- 场景二：检查签名流程和签名证书，参考[应用/服务签名](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5)。

## 9568266 安装权限拒绝

**错误信息**

Error: install permission denied.

**错误描述**

使用hdc install安装HAP时出现错误，提示“code:9568266 error: install permission denied”错误信息。

**可能原因**

hdc install不能安装release签名的企业应用。

**处理步骤**

1. 请使用hdc install指令安装调试debug签名的企业应用。

## 9568337 安装解析失败

**错误信息**

Error: install parse unexpected.

**错误描述**

应用推送到设备安装时，报错包管理打开hap文件失败。

**可能原因**

- 场景一：设备system分区存储空间已满，导致hdc file send文件后，因存储空间不足导致设备中文件损坏。
- 场景二：推送hap包到设备过程hap包损坏。

**处理步骤**

- 场景一：查看设备system分区存储空间，若已满，清理存储满足安装所需空间。

- 场景二：查看本地hap与推送到设备上hap的md5值，若不一致则表示推送过程hap损毁，请尝试重传。

## 9568316 数据代理中APL权限字段描述权限低

**错误信息**

Error: apl of required permission in proxy data is too low.

**错误描述**

proxyData标签requiredReadPermission和requiredWritePermission属性验证失败。

**可能原因**

用户工程module.json中，proxyData标签requiredReadPermission和requiredWritePermission属性验证失败，这两个属性要求system\_basic或system\_core权限等级。

**处理步骤**

1. 检查应用定义的proxyData内容是否符合要求，参考[proxyData标签](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/module-configuration-file-V5#proxydata标签)。

## 9568315 数据代理URI错误

**错误信息**

Error: uri in proxy data is wrong.

**错误描述**

proxyData标签uri属性验证失败。

**可能原因**

用户工程module.json中，proxyData标签uri属性验证失败，不满足uri格式要求。

**处理步骤**

1. 检查应用定义的proxyData内容是否符合要求，参考[proxyData标签](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/module-configuration-file-V5#proxydata标签)。

## 9568336 应用调试类型与已安装应用不一致

**错误信息**

Error: install debug type not same.

**错误描述**

应用调试类型（app.json的debug字段）与已安装应用不一致。

**可能原因**

开发者使用IDE的debug按钮安装了应用，后面打包之后又通过hdc install方式安装。

**处理步骤**

1. 卸载已安装的应用，重新安装新应用。

## 9568296 包类型错误

**错误信息**

Error: install failed due to error bundle type.

**错误描述**

bundleType错误导致应用安装失败。

**可能原因**

新安装应用的bundleType与已安装的有相同bundleName应用不一致。

**处理步骤**

- 方法一：卸载已安装的应用，重新安装新应用。
- 方法二：修改应用的bundleType，与已安装应用保持一致。

## 9568292 UserID为0的用户只能安装singleton应用

**错误信息**

Error: install failed due to zero user can only install singleton app.

**错误描述**

UserID 0用户只允许安装singleton权限应用，singleton权限应用只允许被UserID 0用户安装。

**可能原因**

singleton权限应用安装未指定UserID 0。

**处理步骤**

1. 应用是singleton权限，安装时指定UserID 0。

## 9568263 无法降级安装

**错误信息**

Error: install version downgrade.

**错误描述**

正在安装应用的VersionCode小于系统中已安装应用的VersionCode，安装失败。

**可能原因**

正在安装应用的VersionCode小于系统中已安装应用的VersionCode。

**处理步骤**

1. 卸载已安装的应用，重新安装新应用。

## 9568304 应用不支持当前设备类型

**错误信息**

Error: device type is not supported.

**错误描述**

正在安装的应用不支持当前设备类型，安装失败。

**可能原因**

正在安装的应用不支持当前设备类型。

**处理步骤**

1. 如需要适配当前设备，请在应用设备类型配置中增加当前设备类型。应用deviceTypes配置包含phone（手机）、tablet（平板）、2in1（2合1设备）、tv（智慧屏）、wearable（智能手表）和car（车机）。

## 9568317 应用的多进程配置与系统配置不匹配

**错误信息**

Error: isolationMode does not match the system.

**错误描述**

安装应用时，设置的isolationMode与系统配置项允许的系统配置不匹配。

**可能原因**

- 场景一：设备支持隔离模式，即persist.bms.supportIsolationMode为true时，HAP配置的isolationMode为nonisolationOnly。
- 场景二：设备不支持隔离模式，即persist.bms.supportIsolationMode为false时，HAP配置的isolationMode为isolationOnly。

**处理步骤**

1. 按照设备的隔离模式配置HAP配置文件isolationMode属性。

## 9568315 数据代理的uri属性错误

**错误信息**

Error: uri in proxy data is wrong.

**错误描述**

应用module.json文件中proxyData标签的uri属性验证失败。

**可能原因**

uri不满足格式规范。

**处理步骤**

1. 确认uri满足格式规范。

## 9568310 兼容策略不同

**错误信息**

Error: compatible policy not same.

**错误描述**

新包与已安装包兼容策略不同。

**可能原因**

设备中已安装相同包名的hap包。

**处理步骤**

1. 卸载已安装相同包名hap包，再安装新包。

## 9568391 包管理服务已停止

**错误信息**

Error: bundle manager service is died.

**错误描述**

包管理服务已停止。

**可能原因**

使用bm install -p \*\*\*.hap方式安装预置应用会杀掉正在运行的应用，导致异常（例如foundation进程重启）。

**处理步骤**

1. 预置应用请参考OTA升级。

## 9568393 验证代码签名失败

**错误信息**

Error: verify code signature failed.

**错误描述**

验证代码签名失败。

**可能原因**

- 场景一：包没有代码签名信息。
- 场景二：签名证书问题。

**处理步骤**

- 场景一：使用SDK签名工具验证包是否签名。

- 场景二：检查签名流程和签名证书，参考[应用/服务签名](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5)。

## 9568257 验证pkcs7文件失败

**错误信息**

Error: fail to verify pkcs7 file.

**错误描述**

验证pkcs7文件失败。

**可能原因**

应用当前使用的签名不符合HarmonyOS应用签名要求，通常是由于当前使用的是HarmonyOS应用的签名，应该替换为HarmonyOS应用的签名。

**处理步骤**

1. 在为应用/服务签名时勾选“Support HarmonyOS”,完成HarmonyOS应用签名后再次启动调试或运行应用。

## 9568401 调试包仅支持运行在开发者模式设备

**错误信息**

Error: debug bundle can only be installed in developer mode.

**错误描述**

调试包仅支持运行在开发者模式设备。

**可能原因**

终端设备未开启“开发者模式”。

**处理步骤**

1. 终端系统查看“设置 > 系统”中是否有“开发者选项”，如果不存在，可在“设置 > 关于本机”连续七次单击“版本号”，直到提示“开启开发者模式”，点击“确认开启”后输入PIN码（如果已设置），设备将自动重启。
2. USB数据线连接终端和PC，在“设置 > 系统 > 开发者选项”中，打开“USB调试”开关，弹出的“允许USB调试”的弹框，点击“允许”。
3. 启动调试或运行应用。

## 9568386 卸载找不到资源

**错误信息**

Error: uninstall missing installed bundle.

**错误描述**

卸载找不到资源。

**可能原因**

之前卸载不干净，有资源残留。

**处理步骤**

1. 手动清理el1/el2下所有未卸载的资源。
2. 重新安装。

## 9568284 安装版本不匹配

**错误信息**

Error: install version not compatible.

**错误描述**

安装版本不匹配。

**可能原因**

当前安装HSP的版本信息与已安装HAP的版本信息不匹配。

安装HSP时会做如下校验：

1. bundleName和HAP的一致。
2. version和HAP的一致。
3. 签名和HAP的一致。

**处理步骤**

1. 卸载版本信息不匹配的HAP，再安装HSP。
2. 修改HSP版本信息与HAP一致，再安装HSP。

## 9568287 安装包entry模块数量不合规

**错误信息**

Error: install invalid number of entry hap.

**错误描述**

安装包entry模块数量不合规。

**可能原因**

安装包中entry模块有多个。一个应用只能有一个entry模块，可以有多个feature模块。

**处理步骤**

1. 保留一个entry模块，其余entry模块修改为feature（修改module.json5中type字段）。

## 9568281 安装包vendor不一致

**错误信息**

Error: install vendor not same.

**错误描述**

安装包vendor不一致。

**可能原因**

app.json5文件中app的vendor字段配置不一致。

**处理步骤**

1. 若只有一个HAP，要求与已安装应用vendor字段一致，卸载重装即可。
2. 若包含集成态HSP，要求集成态HSP与使用方HAP的vendor字段保持一致。

## 9568279 安装版本名不一致

**错误信息**

Error: install version name not same.

**错误描述**

安装版本名不一致。

**可能原因**

- 场景一：只有一个hap，可能是保存数据的应用版本和新安装版本不一致导致。
- 场景二：HSP和HAP一起安装时，HSP和HAP的包名、版本号、sdk版本号、releaseType有不一致。

**处理步骤**

- 场景一：DevEco entry配置界面中取消勾选“Keep Application Data”。

- 场景二：对其HSP和HAP的包名、版本号、sdk版本号、releaseType使其一致。

## 9568274 安装服务错误

**错误信息**

Error: install installd service error.

**错误描述**

安装服务错误。

**可能原因**

安装服务异常。

**处理步骤**

1. 清除缓存，重启设备。

## 9568314 安装应用间共享库失败

**错误信息**

Error: Failed to install the HSP because installing a shared bundle specified by hapFilePaths is not allowed.

**错误描述**

安装应用间共享库失败。

**可能原因**

安装应用间共享HSP时使用“hdc app install \*\*\*”指令。

**处理步骤**

1. 安装应用间HSP时使用“hdc install -s \*\*\*”指令。

## 9568359 安装设置selinux失败

**错误信息**

Error: installd set selinux label failed.

**错误描述**

安装设置selinux失败。

**可能原因**

签名配置文件中APL字段错误。APL有“normal”、“system\_basic”和“system\_core”三种等级。

**处理步骤**

1. 确认签名文件p7b中apl字段是否有误。

1. 若apl字段有误，修改UnsgnedReleasedProfileTemplate.json文件中apl字段，并重新签名。

## 9568403 安装加密校验失败

**错误信息**

Error: check encryption failed.

**错误描述**

安装加密校验失败。

**可能原因**

可能是镜像版本较老；或者HAP包lib目录内非so文件导致。

**处理步骤**

1. 安装新版本镜像。
2. 删除HAP工程中lib目录内非so文件，重新签名打包。
