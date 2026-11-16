# 华测教育内部知识库 · 本地语料

2026-11-16 从语雀 `https://www.yuque.com/shiduo-gf6e9/tnhrl5`（book_id `73651885`）整库抓取，作为「华测 AI 测试全栈」学习流水线的第一手资料。

## 规模

| 项 | 数值 |
| --- | --- |
| 文档数 | 283 |
| 总字数（语雀统计） | 1,749,900 |
| Markdown 体积 | 4.8 MB |
| 原始 JSON | 50.3 MB（`raw/`，不入库） |
| 有正文的文档 | 283 / 283（无空文件） |

## 目录

```
corpus/yuque/
├─ md/            283 篇 Markdown，带 YAML 头（title/doc_id/slug/words/updated_at/原链接）
├─ raw/           语雀 API 原始 JSON，可重新转换（.gitignore 排除）
├─ catalog.json   机器索引：id / 标题 / slug / 字数 / md 相对路径 / H1
├─ INDEX.md       按学习阶段分组的人工索引
└─ _toc_raw.json  抓取时的文档清单快照
```

## 怎么抓的

1. 用户的 Chrome 开着远程调试（`chrome://inspect/#remote-debugging`），带着登录态；
2. `scripts/harvest.mjs` 通过 CDP 在页面内同源 `fetch('/api/docs/{id}?book_id=73651885')`，把 JSON 落到 `raw/`；
3. `scripts/convert.py` 把语雀的 lake HTML 转 Markdown（清掉 `<card>` 等专有标签，保留标题/列表/引用/代码块/表格/图片链接）；
4. `scripts/build_index.py` 按标题关键词把文档归入 12 个学习阶段，生成 `INDEX.md`。

> 语雀的目录（TOC）接口对「凭密码访问」的访客返回 401，所以**没有拿到原始分组与排序**；现在的分组是按标题关键词推断的，允许后续手工修正。

## 已知情况

- 有 5 组同名文档共 8 份冗余（`01-Python基础课` 有 v4/v5 两版 + 3 份同题；`Mysql练习题`、`性能测试`、`无标题文档`、`优化版本一` 各 2 份）。后续取用「优先取最新版本」。
- 若干标题是草稿态（`原始题目整理【暂且舍弃…】`、`无标题文档`、`优化版本一/二`），不当正文用。
- 单篇最大 `01-Python AI测试开发基础-v6`（86,454 字、137 个二级标题），是「Python 阶段」的主干教材；`01-Python基础课-v5`（53,982 字）是它的前身版本。
- 面试/笔试题占比不小（约 16.5 万字），单列为「08 面试与求职」，不混入课程主线。

## 复现

```powershell
# 需要 Chrome 已开远程调试，且有一个语雀标签页
cd E:\ailearning\shenle-ai-qa\scripts
node harvest.mjs --delay 300     # 抓 JSON（可断点续抓，已存在的跳过）
python convert.py                # JSON → Markdown + catalog.json
python build_index.py            # 生成 INDEX.md 与阶段统计
```
