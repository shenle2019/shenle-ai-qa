"""第 54 章用例：大模型评估与部署测试。

四块内容：
1. 分类指标（准召 F1）与生成指标（BLEU/ROUGE 的局限）
2. 偏置探针：同一能力描述换个人称，分数是否变化
3. 漂移：线上分布相对基线的 PSI
4. 部署：成功率、P95、版本对比、健壮性输入
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_shared"))

from eval_sim import (  # noqa: E402
    Probe,
    accuracy,
    bleu_like,
    fair_scorer,
    gender_biased_scorer,
    p95,
    precision_recall_f1,
    psi,
    rouge_l_like,
    success_rate,
    tokens_cost,
)

GOLD = [("good", "good"), ("good", "bad"), ("bad", "bad"), ("good", "good"), ("bad", "good")]

PROBE = Probe(
    texts=["他熟练使用 pytest", "她熟练使用 pytest", "他会写接口测试", "她会写接口测试"],
    labels=["male", "female", "male", "female"],
)

ROBUST_INPUTS = [
    "",
    " " * 20,
    "退款" * 500,
    "🙂🙂🙂",
    "\x00\x01",
    "'; DROP TABLE orders; --",
]


def robustness_report(model) -> dict[str, object]:
    """健壮性：空、空白、超长、emoji、控制字符、注入串，逐个喂一遍看会不会崩。"""
    out: dict[str, object] = {}
    for i, text in enumerate(ROBUST_INPUTS):
        try:
            value = model(text)
            out[f"case_{i}"] = "ok" if value is not None else "empty"
        except Exception as exc:  # noqa: BLE001 - 记录而不是抛出，正是测试要看的
            out[f"case_{i}"] = f"raised:{type(exc).__name__}"
    return out


def demo() -> None:
    p, r, f1 = precision_recall_f1(GOLD, "good")
    print("== 分类指标 ==", {"precision": p, "recall": r, "f1": f1, "acc": accuracy(GOLD)})

    print("\n== 生成指标（及局限）==")
    ref = "退款需要在签收后七天内申请并附上订单号"
    good = "退款需要在签收后七天内申请"
    short = "退款"
    print("good:", bleu_like(good, ref), rouge_l_like(good, ref))
    print("short:", bleu_like(short, ref), rouge_l_like(short, ref))
    print("→ 短答案 BLEU/ROUGE 可能虚高，不能单看分")

    print("\n== 偏置探针 ==")
    print("有偏打分:", PROBE.score_of(gender_biased_scorer), "gap:", PROBE.gap(gender_biased_scorer))
    print("公平打分:", PROBE.score_of(fair_scorer), "gap:", PROBE.gap(fair_scorer))

    print("\n== 漂移 ==")
    base = [1.0, 2.0, 2.5, 3.0, 3.2, 4.0, 5.0]
    same = list(base)
    shifted = [x + 3 for x in base]
    print("同一分布 PSI:", psi(base, same))
    print("整体右移 PSI:", psi(base, shifted))

    print("\n== 部署 ==")
    print("成功率:", success_rate([True] * 18 + [False] * 2))
    print("P95:", p95([120, 130, 135, 140, 150, 200, 900]))
    print("成本:", tokens_cost(3200, 800), "元")
    print("健壮性:", robustness_report(lambda t: t or "空输入"))


if __name__ == "__main__":
    demo()
