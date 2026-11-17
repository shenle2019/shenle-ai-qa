# 阶段启动卡（下次开工先读这一页）

用途：换一天、换一个会话、甚至换个模型，只要把这张卡喂回去，就能接着往下写，不用重新交代背景。

## 一句话现状

仓库 `shenle2019/shenle-ai-qa`，monorepo：`notes/`（知识库笔记）+ `labs/`（可运行的实操 + pytest）+ `site/`（VitePress 站点，GitHub Pages 发布）。

- 已完成：第 01–07 章（Python 与工程基础）、第 08–15 章（接口自动化），**184 条 pytest 全绿**。
- 线上：https://shenle2019.github.io/shenle-ai-qa/
- 内容规则：根目录 `CONTENT-RULES.md`（每条都要遵守，站点上也有 `/kb/rules`）。

## 下一阶段要做什么

Web 自动化，编号 **16 起**，预计 16–23 共 8 章。

素材位置：
- 视频（加密 `.sz`，只能本地播放器看）：`D:\huaceedu\4、AI + Web 自动化测试\*.sz`，标题就是章节大纲，例如「WEB自动化Pom框架设计」「基于 YAML 的自动化 WEB 测试框架」「元素定位集中管理」「用例前后置条件」「多用例管理」「浏览器复用机制」。
- 解压资料：`D:\huaceedu\4、AI + Web 自动化测试\资料_解压\资料` 目前**为空**（只有一个「资料获取方式.txt」），别在那里找代码。
- 语料（可机器读）：`E:\ailearning\_ref_corpus\yuque\md` 里有 9 篇与 Web 相关：`Web自动化面试题`、`Web自动化面试题_分类详细整理`、`微软PlaywrightMCP浏览器自动化`、`Web自动化测试 - 平台操作手册`、`webui框架项目分析教程`、`WebUI测试环境搭建`、`web自动化测试试卷含答案及解析`、`自动化平台-Web自动化测试操作手册`、`03-Flask-Web框架`。

## 建议的章节切法（可改，改前先说）

| 章 | 主题 | 实操落点 |
| --- | --- | --- |
| 16 | 浏览器自动化基础与选择器 | Playwright 起停、`get_by_role/get_by_test_id`、等待策略 |
| 17 | 页面对象（PO/POM） | 把页面封装成类，用例只写业务动作 |
| 18 | 元素定位集中管理 | 定位器抽到配置文件/常量，换 UI 不改用例 |
| 19 | 用例前后置与浏览器复用 | fixture 起浏览器、复用 context、登录态复用 |
| 20 | 数据驱动与多用例管理 | YAML 驱动用例、参数化、失败重试与截图 |
| 21 | 视觉与可访问性检查 | 截图对比、可访问性断言 |
| 22 | AI 生成 Web 用例 | 用页面快照喂模型生成步骤，人工审 |
| 23 | Web 框架收口 | CLI + 报告 + CI，能交给别人 |

红线：站点与仓库里**不出现任何课程/机构/来源字样**；每章必须有笔记 + 可跑实操 + pytest；文末四段（附：自测答案 / 学生常问 / 面试题 / 延伸知识）齐全。

## 每次交付的固定动作

```powershell
cd E:\ailearning\shenle-ai-qa
.\.venv\Scripts\python.exe -m pytest labs -q      # 必须全绿
cd site; npm run build; cd ..                      # 必须 build complete
python scripts\shot_site.py                        # 本地截图
git add -A; git commit -m "feat(web): ..."; git push origin HEAD
```

推送后等 GitHub Actions `success`，再打开线上页面确认标题与内容。

## 直接能用的开场 prompt（复制即用）

> 继续 shenle-ai-qa，做 Web 自动化阶段。先读仓库根的 `STAGE-BRIEF.md` 和 `CONTENT-RULES.md`，按里面的章节切法从第 16 章开始，一章一章往下做：每章笔记 + `labs/` 可跑实操 + pytest + 站点页，文末四段问答齐全，全程不出现来源字样。做完一章就跑 `pytest labs -q`、`npm run build`、截图、提交推送，并告诉我这一章的验收点。

更省事的版本（如果只想先看一章）：

> 读 `STAGE-BRIEF.md`，先做第 16 章（浏览器自动化基础与选择器），按 `CONTENT-RULES.md` 的标准交付，做完给我看截图和测试输出。

## 为什么不用做 skill

这份卡就是给「人」写的 skill：它放在仓库里、跟着代码走、改一次全端生效（本地 / GitHub / 线上站点都能看到），比做成插件技能更稳——插件技能换台机器就丢了，仓库不会。
