from pathlib import Path

p = Path("labs/ch39-perf-platform/perf_platform.py")
lines = p.read_text(encoding="utf-8").splitlines()
i = 69  # 第 70 行
assert "default_env" in lines[i], lines[i]
assert lines[i].count("raw") >= 2, lines[i]
lines[i] = '    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}'
lines.insert(i + 1, '    if "default_env" not in raw:')
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("fixed; now:")
for j in range(i - 2, i + 4):
    print(j + 1, "|", lines[j])
