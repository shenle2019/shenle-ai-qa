# 第 46 章 · AI 测试 Skills 与工具链落地

到第 45 章为止，平台是「自己写的」。这一章换一种做法：把一整套**现成的 AI 测试工具链**装到本机、接到项目里，并逐个验证它真的能跑——**能装、能注册、能跑出一条真实结果**，三件事缺一不可。

## 1. 一条工具链由四层组成

| 层 | 是什么 | 本次落地的东西 |
| --- | --- | --- |
| 技能层 | 给 AI 看的说明书（`SKILL.md`） | 10 个技能，覆盖录制、执行、报告、计划编排 |
| 命令层 | 能敲的命令（`console_scripts`） | 6 个已注册命令 |
| 脚本层 | 跟着技能走的辅助脚本 | 动态函数生成、HTML 报告渲染、测试计划生成 |
| 数据层 | 录制产物、用例编排、执行结果 | `snapshots/`、`plans/`、`result/*.json` |

技能层和执行层分开，是这套工具的关键设计：**技能只描述「怎么想」，命令负责「怎么做」**。换一个模型、换一个 Agent，技能文件照样能用。

## 2. 技能清单与注册位置

技能装到项目根的 `.claude/skills/`，一个技能一个目录，入口都是 `SKILL.md`：

| 技能 | 干什么 |
| --- | --- |
| `shenle-web-record` | 网页端录制：点 SNAP 抓视口 + 元素结构，落盘成快照批次 |
| `shenle-device-record` | 设备端采集：截当前屏幕 + 抓界面层级 |
| `shenle-api-record` | 接口录制：本地代理抓请求，装 CA 后可解 HTTPS |
| `shenle-web-cli` | Web 端视觉定位执行：截图 → 找元素 → 点击/输入/断言 |
| `shenle-android-cli` | 安卓端执行：adb 截图 + 视觉定位 + 点击输入滑动 |
| `shenle-api-cli` | 接口调用：send / extract / call / assert 四个子命令 |
| `shenle-test-flow-builder` | 把录制产物编排成可执行流程 |
| `shenle-test-plan-generator` | 生成测试计划（含环境选择、编排扫描） |
| `shenle-test-runner` | 按计划跑，产出执行结果 |
| `shenle-report-generate-html` | 把结果渲染成 HTML 报告 |
| `shenle-dynamic-function-generator` | 按需生成临时函数，补工具缺口 |
| `playwright-cli` | 通用浏览器操作（配套参考文档三篇） |

注册动作只有一步：把技能目录复制到项目的 `.claude/skills/`。**注册成功的判据不是「文件在」，而是每个目录都能被解析出 `SKILL.md` 且 frontmatter 有 `name`**——这一点写进了自检。

## 3. 六个命令的安装与验证

六个工具都是标准 Python 包（`pyproject.toml` + `src/` 布局），用可编辑安装注册成命令：

```bash
cd labs/ch46-toolchain/apps
for d in shenle-*/; do
  .venv/Scripts/python.exe -m pip install -e "$d" --no-deps
done
```

装完在 `.venv/Scripts/` 下多出六个 `.exe`。逐个验证：

| 命令 | 版本 | 跑出来的第一行 |
| --- | --- | --- |
| `shenle-android-cli` | 0.1.0 | `usage: shenle-android-cli [-h] [-s SERIAL] ...` |
| `shenle-api-cli` | 0.2.0 | `命令行驱动的接口调用工具（requests），替代 curl 给 AI 跑 API 任务` |
| `shenle-api-record` | 0.1.0 | `{record,install-ca,check,stop}` |
| `shenle-device-record` | 0.1.0 | `设备端界面采集：截当前屏幕 + 抓界面结构` |
| `shenle-web-cli` | 0.1.0 | `[-h] [--port PORT] [--headless] ...` |
| `shenle-web-record` | 0.1.0 | `Record a web page interactively: click the SNAP button ...` |

「能打印 usage」只是第一关。真正的验证是跑出一条业务结果：

```bash
# 起一个本地静态服务当被测站
python -m http.server 8732 --directory site/public

# 用 api-cli 发一次真实请求（请求描述走 stdin）
echo '{"method":"GET","url":"http://127.0.0.1:8732/logo.svg"}' | shenle-api-cli send
```

```
[OK] send: 200 GET http://127.0.0.1:8732/logo.svg elapsed=62ms
     result_file=C:\Users\...\Temp\shenle-api-results\20261123-101803-f46ce053.json
```

它把 `{request, response, meta}` 三段落成 JSON——这正是「录制 → 断言 → 报告」链条里的最小一环。

## 4. 本章实操

`labs/ch46-toolchain/`：

| 内容 | 说明 |
| --- | --- |
| `apps/` | 6 个可安装工具 + 3 个技能内置脚本，源码原样保留 |
| `.claude/skills/` | 10 个技能的原始定义 |
| `test_toolchain.py` | 7 条自检：技能齐全、每个 `SKILL.md` 有 frontmatter、命令已注册、`--version` 可用、源码在位、命名已净化 |
| `conftest.py` | 把 `apps/` 排除出测试收集 |

```bash
python -m pytest labs/ch46-toolchain -q
# 7 passed
```

自检里有一条专门查命名：整个工具链（文件名 + 文件内容）不允许残留旧厂牌字样。这条测试是**先失败后通过**——第一次跑出 131 个文件、37 个路径要改，改完才绿。

## 5. 常见坑

1. **直接 `python src/xxx/cli.py` 会报 `ModuleNotFoundError`**。这类包用 `src/` 布局，不安装就没有包路径，必须 `pip install -e`。
2 **vendor 源码里的 `tests/` 会被本仓库 pytest 收走**，撞模块名后直接中断收集。用 `collect_ignore_glob` 隔离，别去改别人的测试。
3. **`__pycache__` 会拖住改名**：改了源码名，旧 `.pyc` 里还是老名字，扫描会误报。先删缓存再校验。
4. **交互式录制不能进 CI**：`web-record record` 要人点 SNAP，`device-record` 要真机。自动化只能覆盖 `send`、`check`、`plan` 这类非交互子命令。

## 6. 自测

1. 为什么技能层和命令层要分开？合成一个文件行不行？
2. 六个工具为什么用 `--no-deps` 安装？
3. 只验证「命令能打印 usage」够不够？还要验什么？
4. 为什么 vendor 目录必须排除出测试收集？

## 附：自测答案

1. 分开是因为**技能是给模型的，命令是给 shell 的**。技能要随模型/Agent 切换，命令要随依赖和环境切换；合成一个文件后，改一段提示词就得动可执行代码，两边都难维护。
2. 因为宿主项目已经有 `requests`/`playwright`/`mitmproxy` 等依赖，`--no-deps` 避免 pip 再去解析一遍可能冲突的版本；依赖统一由项目 `.venv` 管。
3. 不够。usage 只证明「入口能进」。要再验三件事：`--version` 一致、关键子命令能完成一次真实动作（如 send 返回 200）、产物落盘可读。
4. 因为 vendor 测试自带同名模块与外部依赖，混进主测试集会造成收集冲突和误报；排除后主仓库的测试仍然只覆盖自己写的代码，vendor 保持原样可追溯。

## 学生常问

**Q：这些工具和前面 40–45 章自己写的平台冲突吗？**

A：不冲突，是两种路径。前面是自己实现（可控、可测、能改），这一章是接现成工具链（省时间、覆盖广）。真实项目里常见组合是：**录制用现成工具，执行和报告接自己的平台**。

**Q：为什么只装了 6 个，另外 3 个不装？**

A：另外三个不是独立命令：`shenle-ai-test-runner` / `shenle-test-runner` 是跟着技能走的编排脚本，`shenle-report-generate-html` 是技能里的渲染脚本。它们靠 `SKILL.md` 调用，不需要注册成全局命令。

**Q：工具都装了，但没真机、没有视觉模型，还能验什么？**

A：验不依赖外部条件的部分：命令注册、版本、参数解析、`api-cli send` 这种纯 HTTP 动作、报告渲染。设备类与视觉类留 `pytest.mark.device` / 需要 key 的跳过，和前面章节的做法保持一致。

## 面试题

**Q：让你把一套第三方测试工具接进团队平台，你怎么评估？**

A：四个维度。① **接口**：是命令还是库，能不能非交互调用；② **产物**：落盘格式是否结构化（JSON 优于日志）；③ **依赖**：是否引入重组件（浏览器、代理、设备）；④ **可替代性**：技能与执行是否解耦，换模型要不要改代码。

**Q：为什么强调「注册」这一步，而不是把工具目录加到 PATH？**

A：注册（`pip install -e`）会生成入口脚本、写入元数据，`pip list` 和 `importlib.metadata` 都能查到，可复现、可卸载；加 PATH 只是碰巧能跑，换机器就散架。

**Q：工具链落地失败的典型原因是什么？**

A：不是「工具不好用」，而是**验证停在第一步**：装完看到 usage 就宣布成功，没有跑出一条真实业务结果。所以验收标准要写成「一条命令 + 一个真实响应 + 一份落盘产物」。

## 延伸知识

- 可编辑安装的本质：`site-packages` 里放一个 `.pth` 指向源码目录，改代码立即生效，不用重装。
- `console_scripts` 是 `entry_points` 的一种，`importlib.metadata.entry_points(group="console_scripts")` 可以编程式列出全部命令，适合做环境自检。
- 录制类工具的通病是**产物不稳定**（元素 id 变化、截图分辨率不同）。落地时要先定产物 schema，再谈回放。
- 想让 AI 稳定调用这些命令，最好给每个命令配一份「输入 schema + 成功判据」，比让它读 `--help` 靠谱得多。
