---
title: "atm工具"
doc_id: 256210753
slug: izgk0vkrk7gge8af
book_id: 73651885
words: 648
updated_at: 2026-02-06T06:51:53.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/izgk0vkrk7gge8af
---
Access Token Manager (程序访问控制管理工具，简称atm工具)，是用于查询应用进程的权限、使用类型等信息的工具，为开发者提供了根据tokenid、包名、进程名等信息进行访问控制管理的能力。

# 环境说明

在使用本工具前，开发者需要先获取[hdc工具](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/hdc-V5)，执行hdc shell。

# atm工具命令列表

|  |  |
| --- | --- |
| 命令 | 描述 |
| help | 帮助命令，显示atm支持的命令信息。 |
| dump | 查询命令，用于查询访问控制相关数据信息。 |

# 帮助命令

# 查询命令

下表所列命令中，-t、-v为必选参数，-i、-b、-n、-p为可选参数。对atm dump -v命令，-i和-p参数可以组合使用；对atm dump -t命令，-i、-b、-n参数只能单独使用。

|  |  |
| --- | --- |
| 参数 | 参数说明 |
| -h | 帮助信息。 |
| -t | 必选参数，查询系统中所有应用进程信息。 |
| -t -i <token-id> | 可选参数，通过应用进程的tokenid，查询该应用的基本信息以及对应的权限信息。 |
| -t -b <bundle-name> | 可选参数，通过应用进程的包名bundle-name，查询该应用的基本信息以及对应的权限信息。 |
| -t -n <process-name> | 可选参数，通过应用进程的进程名process-name，查询该应用的基本信息以及对应的权限信息。 |
| -v | 必选参数，查询系统中所有应用进程的权限使用类型。 |
| -v -i <token-id> | 可选参数，通过应用进程的tokenid，查询该应用的权限使用类型。 |
| -v -p <permission-name> | 可选参数，通过权限名，查询该权限的使用类型。 |

示例：
