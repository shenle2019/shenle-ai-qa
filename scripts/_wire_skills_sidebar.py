"""在侧栏「延伸阅读」加 Skills 手册入口，在 /labs/ 侧栏加单跑记录入口。"""

from pathlib import Path

CFG = Path(__file__).resolve().parents[1] / "site" / ".vitepress" / "config.mts"

OLD = """            { text: '接口自动化面试题（带答案）', link: '/kb/interview-api' },
            { text: '内容更新规则', link: '/kb/rules' }"""

NEW = """            { text: 'Skills 手册（13 个技能）', link: '/kb/skills/' },
            { text: 'Skills 单跑记录', link: '/labs/skills/' },
            { text: '接口自动化面试题（带答案）', link: '/kb/interview-api' },
            { text: '内容更新规则', link: '/kb/rules' }"""

LABS_ANCHOR = """          text: '实操记录',"""
LABS_INSERT = """          text: 'Skills 单跑记录',
          link: '/labs/skills/',
        },
        {
          text: '实操记录',"""


def main() -> None:
    text = CFG.read_text(encoding="utf-8")
    count = text.count(OLD)
    assert count == 2, f"延伸阅读 anchor 命中 {count} 次，应为 2"
    text = text.replace(OLD, NEW)

    labs = text.split("'/labs/': [")
    assert len(labs) == 2, "未找到 /labs/ 侧栏"
    head, tail = labs
    assert tail.count(LABS_ANCHOR) >= 1, "未找到 实操记录 锚点"
    tail = tail.replace(LABS_ANCHOR, LABS_INSERT, 1)
    CFG.write_text(head + "'/labs/': [" + tail, encoding="utf-8")
    print("wired: 延伸阅读 x2, labs x1")


if __name__ == "__main__":
    main()
