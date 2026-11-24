from pathlib import Path

p = Path("CONTENT-RULES.md")
t = p.read_text(encoding="utf-8")
old = "**审查方式**：`python scripts/_audit_claims.py` 会把全部 `notes/ch*.md` 里「延伸知识 / 常见坑 / 自测答案 / 学生常问 / 面试题」抽出来，标出含方向词、绝对词、默认值词的句子，人工逐条过。每新增一章都要跑一遍。"
new = """**审查方式**：`python scripts/_audit_claims.py` 会把全部 `notes/ch*.md` 里「延伸知识 / 常见坑 / 自测答案 / 学生常问 / 面试题」抽出来，标出含方向词、绝对词、默认值词的句子，人工逐条过。每新增一章都要跑一遍。

**复核不靠自己一个人**（2026-11-24 补）。同一句话由同一个人写、同一个人审，等于没审——上面那句翻车话就是这么过去的。做法固定成三条：

1. **分批外包给审校 agent**：按 `ch01–15 / ch16–31 / ch32–46 / 站点与 kb` 切四批，每批给同一份输出格式（`行号 + 原句 + 问题 + 改法`，另附 `UNCERTAIN` 分区），要求「只报有把握的、不改文件、能用代码验的先跑一遍」。
2. **改的时候逐条断言**：修改脚本里每条替换都带 `assert old in text`，改不到就报错，避免「以为改了其实没改」。
3. **每条改动都要能指回证据**：语料原文、`labs/` 里的代码行、或实跑输出三选一。审校给出改法也要验——这一轮就有 2 条是误报（`shenle-device-record` 其实有 `SKILL.md`；`x += 1` 等价性只对数字/字符串成立），照抄会改错。

**台账**：每一轮排查都落一份 `docs/audit-YYYY-MM-DD.md`（起因、溯源、方法、按文件的修改清单、误报、根因），改了什么、为什么改，以后能查。2026-11-24 这一轮见 `docs/audit-2026-11-24.md`。"""
assert old in t
p.write_text(t.replace(old, new, 1), encoding="utf-8")
print("CONTENT-RULES updated")
