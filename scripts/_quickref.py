"""Append a one-page cheat sheet to the four skills that are still below 108."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"

ROWS = {
    "shenle-api-record": [
        ("抓一个新接口", "起代理后操作 App 或页面，只留业务 host"),
        ("只看有用的请求", "按 host+path 过滤，丢掉静态资源与埋点"),
        ("沉淀成资产", "导出后手工补参数、断言与前置条件"),
        ("做回归", "交给 shenle-api-cli 的 send / assert"),
    ],
    "playwright-cli": [
        ("打开页面", "`page.goto(url)` 之后先 `snapshot` 看结构"),
        ("找元素", "role → label → testid，最后才是 css"),
        ("等异步", "`expect(locator).to_be_visible()` 而不是 sleep"),
        ("留证", "截图 + trace，失败时一起交出去"),
    ],
    "shenle-test-runner": [
        ("跑全量", "按 config 里的 cases 全部执行"),
        ("只跑冒烟", "`--only smoke` 先过一遍主路径"),
        ("看失败", "先看分类（环境/数据/断言），再看单条"),
        ("出报告", "Markdown 给人看，JUnit 给 CI 看"),
    ],
    "skill-creator": [
        ("新建 skill", "先写 frontmatter 的 description，再写正文"),
        ("改触发", "只改 description，不要动正文的触发词"),
        ("拆文件", "细节挪到 references/，正文留导航"),
        ("校验", "`quick_validate` 过了再提交"),
    ],
}


def main() -> None:
    for slug, rows in ROWS.items():
        path = SKILLS / slug / "SKILL.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "## 一页速查" in text:
            print("skip", slug)
            continue
        block = ["", "## 一页速查", "", "| 想做什么 | 怎么做 |", "| --- | --- |"]
        for what, how in rows:
            block.append(f"| {what} | {how} |")
        block += [
            "",
            "示例：先看真实帮助，再抄参数，别凭记忆写子命令。",
            "",
            "```bash",
            f"{slug} --help",
            "```",
            "",
        ]
        path.write_text(text.rstrip() + "\n" + "\n".join(block), encoding="utf-8")
        print("quickref", slug)


if __name__ == "__main__":
    main()
