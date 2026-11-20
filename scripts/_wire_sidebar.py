"""补侧栏：把「第五阶段」的 32 项后面接上 33–39（两处）。"""

from pathlib import Path

CH = [
    ("ch33", "33 场景设计：基准与负载"),
    ("ch34", "34 压测脚本与参数化"),
    ("ch35", "35 结果分析与瓶颈定位"),
    ("ch36", "36 中间件性能要点"),
    ("ch37", "37 全链路压测与隔离"),
    ("ch38", "38 AI 辅助性能分析"),
    ("ch39", "39 性能平台收口"),
]

config = Path("site/.vitepress/config.mts")
text = config.read_text(encoding="utf-8")
anchor = "            { text: '32 性能测试基础与指标', link: '/chapters/ch32' }\n"
extra = "".join(f"            {{ text: '{label}', link: '/chapters/{slug}' }},\n" for slug, label in CH)
assert text.count(anchor) == 2, f"anchor count = {text.count(anchor)}"
text = text.replace(anchor, anchor.rstrip("\n") + ",\n" + extra)
config.write_text(text, encoding="utf-8")
print("sidebar wired, occurrences:", text.count("ch39"))
