from pathlib import Path

p = Path("site/kb/rules.md")
t = p.read_text(encoding="utf-8")
old = "## 质量红线"
new = """## 复核与台账

一句话写完、同一个人再读一遍，等于没审。2026-11-24 就是这么让一句方向反了的话活了一个月（`ch32` 的压测 timeout，见 `chapters/ch32`，排查全过程在仓库的 `docs/audit-2026-11-24.md`）。所以固定成三步：

1. **分批外包审校**：按 `ch01–15 / ch16–31 / ch32–46 / 站点与 kb` 切四批，每批只报「行号 + 原句 + 问题 + 改法」，另开一个「没把握」分区；能用代码验的先跑一遍再下结论。
2. **改的时候逐条断言**：改稿脚本里每条替换都带 `assert old in text`，改不到就报错，避免「以为改了」。
3. **每条改动都能指回证据**：语料原文、`labs/` 里的某一行代码、或一次真实运行输出，三选一。审校报的也要验——那一轮就有 2 条是误报。

事实性断言（大小、先后、默认值这类）在 `CONTENT-RULES.md` 第七节有完整规则：没有出处就标「经验判断，未验证」，并且「延伸知识」凑不满四条就写三条。

## 质量红线"""
assert old in t
p.write_text(t.replace(old, new, 1), encoding="utf-8")
print("rules page updated")
