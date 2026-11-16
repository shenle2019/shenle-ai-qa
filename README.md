# shenle-ai-qa

AI 测试全栈的学习与实践仓库：**笔记**（notes）、**可运行的实验**（labs）、**对外站点**（site）。

每一章都按同一个闭环推进：读材料 → 提炼成笔记 → 写一个能跑的程序 → 截图 → 提交 → 部署 → 站点与进度更新。

## 结构

```
notes/     按章整理的学习笔记（提炼，不抄原文）
labs/      每章的实验代码，独立可跑，按章编号
site/      VitePress 站点，聚合笔记与实验入口
corpus/    本地语料（语雀知识库抓取结果，仅 md 与索引入库）
```

## 章节进度

| 章 | 主题 | 笔记 | 实验 |
| --- | --- | --- | --- |
| 01 | Python 入门与第一个 AI 生成程序 | [notes/ch01](notes/ch01-python-basics.md) | [labs/ch01-hello-ai](labs/ch01-hello-ai/README.md) |

## 本地开发

```powershell
# 站点
cd site
npm install
npm run dev        # http://localhost:5173

# 第一章实验
cd labs/ch01-hello-ai
python hello.py
python score.py
python ai_generate.py
```

## 约定

- 笔记只写自己消化过的内容，引用原文时标注来源章节。
- 实验一律可在干净环境跑起来：依赖写进 `requirements.txt`，密钥只从环境变量读，缺密钥时自动降级到本地 mock。
- 每章合并前必须有一张运行截图。

站点地址：https://shenle2019.github.io/shenle-ai-qa/
