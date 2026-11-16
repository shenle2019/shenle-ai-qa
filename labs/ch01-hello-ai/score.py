"""课程项目：问姓名 + 三门成绩，算总分和平均分。

两种用法：
  python score.py                        交互模式，逐项输入
  python score.py --name 李明 --scores 85 92 78   非交互，便于自测与自动化
"""

from __future__ import annotations

import argparse
import sys

SUBJECTS = ("语文", "数学", "英语")
MIN_SCORE = 0
MAX_SCORE = 100


def parse_score(raw: str, subject: str) -> float:
    """把输入转成分数，非法时抛 ValueError 并带上科目名。"""
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{subject}成绩必须是数字，收到 {raw!r}") from exc
    if not MIN_SCORE <= value <= MAX_SCORE:
        raise ValueError(f"{subject}成绩必须在 {MIN_SCORE}-{MAX_SCORE} 之间，收到 {value:g}")
    return value


def ask_score(subject: str) -> float:
    """交互模式：一直问到合法为止。"""
    while True:
        try:
            return parse_score(input(f"请输入{subject}成绩："), subject)
        except ValueError as exc:
            print(f"  ✗ {exc}，请重新输入")


def summarise(name: str, scores: dict[str, float]) -> dict[str, object]:
    total = sum(scores.values())
    average = total / len(scores)
    return {
        "name": name,
        "total": total,
        "average": average,
        "passed": average >= 60,
        "weakest": min(scores, key=scores.get),
    }


def report(result: dict[str, object]) -> str:
    mark = "及格" if result["passed"] else "不及格"
    return "\n".join(
        [
            f"姓名：{result['name']}",
            f"总分：{result['total']:.1f}",
            f"平均分：{result['average']:.2f}",
            f"结论：{mark}（平均分 {'≥' if result['passed'] else '<'} 60）",
            f"最弱科目：{result['weakest']}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="三门成绩统计")
    parser.add_argument("--name", help="学生姓名；不传则交互输入")
    parser.add_argument("--scores", nargs=3, metavar=("语文", "数学", "英语"), help="三门成绩")
    args = parser.parse_args(argv)

    name = args.name or input("请输入姓名：").strip()
    if not name:
        print("姓名不能为空", file=sys.stderr)
        return 2

    if args.scores:
        try:
            scores = {s: parse_score(v, s) for s, v in zip(SUBJECTS, args.scores)}
        except ValueError as exc:
            print(f"✗ {exc}", file=sys.stderr)
            return 2
    else:
        scores = {s: ask_score(s) for s in SUBJECTS}

    print()
    print(report(summarise(name, scores)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
