from ch54_cases import GOLD, PROBE, robustness_report  # noqa: F401

from eval_sim import (
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


def test_confusion_metrics_match_hand_count():
    # GOLD 里 good：tp=2（1、4 条）、fp=1（第 5 条把 bad 判成 good）、fn=1（第 2 条）
    p, r, f1 = precision_recall_f1(GOLD, "good")
    assert p == 0.6667
    assert r == 0.6667
    assert f1 == 0.6667


def test_accuracy_is_share_of_correct():
    assert accuracy(GOLD) == 0.6


def test_bleu_rewards_short_answers_unfairly():
    ref = "退款需要在签收后七天内申请并附上订单号"
    short = "退款"
    good = "退款需要在签收后七天内申请"
    # 短答案 1-gram 全中，精确率虚高；这正是「BLEU 不能单独用」的证据
    assert bleu_like(short, ref) >= bleu_like(good, ref) - 0.1


def test_rouge_l_drops_for_short_answer():
    ref = "退款需要在签收后七天内申请并附上订单号"
    assert rouge_l_like("退款", ref) < rouge_l_like("退款需要在签收后七天内申请", ref)


def test_biased_scorer_has_gap():
    assert PROBE.gap(gender_biased_scorer) > 0


def test_fair_scorer_has_no_gap():
    assert PROBE.gap(fair_scorer) == 0


def test_psi_zero_for_identical_distribution():
    base = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert psi(base, list(base)) == 0.0


def test_psi_large_for_shifted_distribution():
    base = [1.0, 2.0, 3.0, 4.0, 5.0]
    shifted = [x + 5 for x in base]
    assert psi(base, shifted) > 0.25


def test_success_rate_counts_failures():
    assert success_rate([True] * 9 + [False]) == 0.9


def test_p95_uses_nearest_rank():
    assert p95([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 10


def test_cost_increases_with_completion_tokens():
    assert tokens_cost(1000, 2000) > tokens_cost(1000, 200)


def test_robustness_report_covers_all_inputs():
    report = robustness_report(lambda t: t or "空输入")
    assert len(report) == 6
    assert all(isinstance(v, str) for v in report.values())
