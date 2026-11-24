"""给 /kb/ 与 /skills/ 补左侧栏（这两个路径原来没有 sidebar key，页面自己不显示侧栏）。

做法：在 sidebar 对象结尾（`      ]` + `    },` 处）插入两个新 key，
内容复用「延伸阅读」那组链接 + 一个「知识库」组，避免再改已有的 /chapters/、/labs/ 块。
"""
from pathlib import Path

CFG = Path(__file__).resolve().parents[1] / "site" / ".vitepress" / "config.mts"

BLOCK = """      ],
      '/kb/': [
        {
          text: '知识库',
          items: [
            { text: '知识库索引', link: '/kb/' },
            { text: 'Skills 手册（全部技能）', link: '/kb/skills/' },
            { text: '接口自动化面试题（带答案）', link: '/kb/interview-api' },
            { text: '内容更新规则', link: '/kb/rules' }
          ]
        },
        {
          text: '延伸阅读',
          items: [
            { text: '测试全栈知识库', link: '/chapters/' },
            { text: '实操记录', link: '/labs/' },
            { text: '在线运行 playground', link: '/labs/playground' },
            { text: 'Skills 库（可预览下载）', link: '/skills/' },
            { text: 'Skills 单跑记录', link: '/labs/skills/' }
          ]
        }
      ],
      '/skills/': [
        {
          text: 'Skills',
          items: [
            { text: 'Skills 库（可预览下载）', link: '/skills/' },
            { text: 'Skills 手册（全部技能）', link: '/kb/skills/' },
            { text: 'Skills 单跑记录', link: '/labs/skills/' }
          ]
        },
        {
          text: '延伸阅读',
          items: [
            { text: '知识库索引', link: '/kb/' },
            { text: '测试全栈知识库', link: '/chapters/' },
            { text: '实操记录', link: '/labs/' },
            { text: '内容更新规则', link: '/kb/rules' }
          ]
        }
      ]
    },"""

src = CFG.read_text(encoding="utf-8")
if "'/kb/': [" in src or "'/skills/': [" in src:
    print("already patched")
else:
    marker = "      ]\n    },\n"
    idx = src.rindex(marker)
    out = src[:idx] + BLOCK + src[idx + len(marker):]
    CFG.write_text(out, encoding="utf-8")
    print("patched", len(src), "->", len(out))
