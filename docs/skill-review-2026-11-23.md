# Skills 手册语义复核（2026-11-23）

复核对象：site/kb/skills/ 13 篇技能说明页。目标不是补规则条数，而是找**说错的地方**。

## 方法

1. 六个 CLI 技能页（web-cli / android-cli / api-cli / api-record / device-record / web-record）逐个跑真实的 <cli> --help，把页面里提到的子命令与真实子命令集合做差集。
2. 两个没有 CLI 的技能（test-runner / report-generate-html）核实入口是否真的存在。
3. 其余技能页检查「怎么用」里的命令能否照抄执行。

## 结果

| 页面 | 页面提到的子命令数 | 实际子命令数 | 不存在的子命令 |
| --- | --- | --- | --- |
| web-cli | 6 | 14 | 0 |
| android-cli | 1 | 24 | 0 |
| api-cli | 2 | 4 | 0 |
| api-record | 3 | 4 | 0 |
| device-record | 2 | 2 | 0 |
| web-record | 1 | 1 | 0 |

**没有说错的子命令**；问题集中在「说得太少」：

- ndroid-cli：原来只写了 3 条命令（devices / screenshot / click），实际有 24 个子命令。已补全分组清单（设备 / 应用 / 看 / 动 / 系统 / batch）和 8 条可照抄的示例。
- web-cli：核心功能里漏了 atch，已补上并注明语义。

## 两个「没有控制台脚本」的技能

- shenle-test-runner：定位是**编排技能**（读 plan、串起其它 CLI、汇总结果），本身不是 CLI。pps/shenle-test-runner/ 下只有示例数据，没有可执行入口 —— 页面写的是「按 SKILL.md 指定计划路径执行」，与实际一致，**不需要**补 console_scripts。
- shenle-report-generate-html：是一个脚本（scripts/generate_html.py），不是打包命令；--help 实测可用（需要 --project-dir 与 --plan-id）。页面写的是按路径调用脚本，与实际一致，**不需要**补 console_scripts。

结论：13 页无需改写的语义错误为 0；补齐了 2 页的命令覆盖，其余保持原样。
