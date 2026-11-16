"""第 9 章演示：契约 -> 矩阵 -> 用例 -> 提示词 -> 审。

跑法：``.venv\\Scripts\\python.exe labs\\ch09-ai-cases\\run_demo.py``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matrix import coverage, gaps, generate  # noqa: E402
from prompt import BAD_SAMPLE, build_prompt, estimate_coverage, review  # noqa: E402
from spec import DIMENSIONS, SPEC  # noqa: E402


def main() -> None:
    all_cases = []
    for endpoint in SPEC["endpoints"]:
        cases = generate(endpoint)
        all_cases.extend(cases)
        print(f"\n## {endpoint['method']} {endpoint['path']}  ->  {len(cases)} 条")

    table = coverage(all_cases, DIMENSIONS)
    print("\n## 覆盖矩阵")
    header = f"{'接口':<22}" + "".join(f"{d:<6}" for d in DIMENSIONS)
    print(header)
    for endpoint, row in table.items():
        line = f"{endpoint:<22}" + "".join(f"{row[d]:<6}" for d in DIMENSIONS)
        print(line)

    holes = gaps(table, DIMENSIONS)
    print(f"\n空格子：{len(holes)} 个")
    for endpoint, dim in holes:
        print(f"  - {endpoint} / {dim}")

    prompt = build_prompt(SPEC, table, all_cases)
    out = Path(__file__).resolve().parent / "_prompt.txt"
    out.write_text(prompt, encoding="utf-8")
    print(f"\n提示词已写入 {out}（{len(prompt)} 字符，可直接贴给任意 LLM）")

    print("\n## 审一份『模型产出』的样例")
    verdict = review(BAD_SAMPLE)
    for bucket in ("pass", "revise", "drop"):
        print(f"  {bucket}: {len(verdict[bucket])}")
        for case in verdict[bucket]:
            issues = ", ".join(case.get("problems", [])) or "无"
            print(f"    - {case['id']} {case['title']} :: {issues}")

    print("\n## 审完的维度分布")
    print(json.dumps(estimate_coverage(verdict["pass"]), ensure_ascii=False))


if __name__ == "__main__":
    main()
