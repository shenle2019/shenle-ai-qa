"""应用 ch32–ch46 审校报告里的 ERROR 与 UNCERTAIN（含 ch46 目录结构事实纠正）。"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FIXES = [
    (
        "notes/ch32-perf-basics.md",
        "| 错误率 | 非 2xx 的比例 | 把 4xx 业务拒绝也算成「服务挂了」 |",
        "| 错误率 | 5xx 与超时的比例（4xx 单列，不算故障） | 把 4xx 业务拒绝也算成「服务挂了」 |",
    ),
    (
        "notes/ch32-perf-basics.md",
        "平均值是 19.5ms，看上去很健康；但 P99 是 200ms——**每 20 个用户里就有 1 个在等 0.2 秒**。平均值把尾部抹平了，而用户体验恰恰由尾部决定。",
        "平均值是 19.5ms，看上去很健康；但 5% 的请求要等 200ms——**每 20 个用户里就有 1 个在等 0.2 秒**。这个比例该看 P95；P99 只描述最慢的 1%（每 100 个有 1 个），别混着说。平均值把尾部抹平了，而用户体验恰恰由尾部决定。",
    ),
    (
        "notes/ch33-scenarios.md",
        "- `target_factory(level)` 每档新建一个 target，避免上一档的连接被复用——否则第一档建立的连接会一直吃满池子，后面几档的数字全是假的。",
        "- `target_factory(level)` 每档新建 target 只重置统计口径；连接是否复用取决于 Session——demo 五档共用一个 Session，要换连接得每档新建 Session。",
    ),
    (
        "notes/ch33-scenarios.md",
        "3. **每档时长太短**：小于 5 秒时，GC、连接建立、预热都还没走完，噪声比信号大。",
        "3. **每档时长太短**：小于 5 秒时 GC、连接建立、预热都没走完，噪声比信号大；本章 demo 为提速只跑 1.5 秒，结论只看趋势，别当容量。",
    ),
    (
        "notes/ch33-scenarios.md",
        "1. 连接是池化资源，前档建立的连接会占住池子，后档的排队时间会被算进 RT，数字失真；新建 target 才能让每档从同一初始状态开始。",
        "1. 连接复用会让后档从「热连接」起步，与前档不可比；要每档从同一初始状态开始，得每档新建 Session（demo 没这么做，所以只看趋势）。",
    ),
    (
        "notes/ch34-scripts.md",
        "次数分布符合 1:3:1 的权重（6 次请求里 1 次登录、3 次查列表、2 次下单，因为随机取整）。",
        "次数分布大致符合 1:3:1 的权重（6 次抽样得到 1 次登录、3 次查列表、2 次下单）；样本小、每次跑都不一样。",
    ),
    (
        "notes/ch34-scripts.md",
        "3. **思考时间用 `time.sleep` 放在请求之后**：看起来对，但会让「最后一次请求」的停顿不计入，压测总时长偏短；对吞吐影响可以忽略，对长尾统计有影响。",
        "3. **思考时间放在请求之后**：每次都会睡（含最后一次），总时长多出一段尾部空转、TPS 被压低；要贴近真实节奏，停顿应放在两次请求之间。",
    ),
    (
        "notes/ch35-analyze.md",
        "2. 所有并发线程都在服务端「处理中」，客户端没有排队等待，说明瓶颈已经在服务端内部（CPU/锁/IO），而不是连接层。",
        "2. 所有并发都在服务端「处理中」、且 `pool_wait` 为 0，才说明瓶颈在服务端内部（CPU/锁/IO）；`pool_wait > 0` 说明卡在连接池，先扩池或减持有时间。",
    ),
    (
        "notes/ch35-analyze.md",
        "- 施压端与被测端同机时，先把施压端 CPU 限制在 1 核以内，避免它自己成为瓶颈。",
        "- 施压端与被测端同机时，让两端绑到不相交的 CPU 核（或干脆分机）；把施压端限到 1 核只会让它更早成为瓶颈。",
    ),
    (
        "notes/ch37-chain.md",
        "- 全链路压测的「容量」应按最慢一跳算，而不是平均值。",
        "- 全链路压测的「容量」取各跳容量的最小值（瓶颈跳），不能按延迟最慢的那一跳或平均值算。",
    ),
    ("notes/ch39-perf-platform.md", "- 失败：3", "- 失败：2"),
    (
        "notes/ch41-config.md",
        "- 变量支持默认值写法 ${VAR:-dev} 能减少本地配置成本。",
        "- 默认值写法 `${VAR:-dev}` 能省本地配置，但本章的 `expand` 只认 `${VAR}`，还没实现默认值语法，会原样保留字面量；要用得先改正则。",
    ),
    (
        "notes/ch42-assets.md",
        "3. 路径参数用正则拒绝 /，导致 /a/{id}/b 匹配失败。",
        "3. 路径参数用贪婪的 `.+`，会把 `/b` 一起吃进参数，`/a/{id}/b` 就匹配错；应当用 `[^/]+`。",
    ),
    (
        "notes/ch42-assets.md",
        "A：定期用资产跑一次「探活」：对每个接口发最小合法请求，把 404/405 这类「路径都不存在」的结果标出来。",
        "A：定期用资产跑一次「探活」：对每个接口发最小合法请求，404 说明路径不存在、405 说明方法没实现，两类分别标出来——405 恰恰说明路径是存在的。",
    ),
    (
        "notes/ch44-plans.md",
        "三个状态对外暴露：提交后前端轮询的是 `summary()`，不是逐条结果。",
        "对外只暴露 queued / passed / failed 三个状态（running 是内部瞬态）：提交后前端轮询 `summary()` 拿计数，不是逐条结果。",
    ),
    (
        "notes/ch44-plans.md",
        "2. 同一计划里不同用例的稳定性不同，记在计划上会让「坏用例的重试」挤占「好用例的次数」。",
        "2. 每个任务各自记 attempts；上限放在计划层没问题，但绝不能共用一个计数器，否则坏用例会把额度用光。",
    ),
    (
        "notes/ch46-toolchain.md",
        "| `shenle-report-generate-html` | 把结果渲染成 HTML 报告 |",
        "| `shenle-report-generate-html` | 把结果渲染成 HTML 报告（`SKILL.md` 在包内 `skill/` 子目录，注册时拷内层目录） |",
    ),
    (
        "notes/ch46-toolchain.md",
        "for d in shenle-*/; do",
        "for d in shenle-android-cli shenle-api-cli shenle-api-record \\\n"
        "         shenle-device-record shenle-web-cli shenle-web-record; do",
    ),
]


def main() -> None:
    for rel, old, new in FIXES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        assert old in text, f"{rel} 找不到：{old[:40]!r}"
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        print(f"ok {rel} <- {old[:32]!r}")


if __name__ == "__main__":
    main()
