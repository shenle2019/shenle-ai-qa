"""应用 kb / 首页审校报告里的 7 条 ERROR 与 3 条较硬的 UNCERTAIN。"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPLACEMENTS = [
    # ---- kb/interview-api.md ----
    (
        "site/kb/interview-api.md",
        "有键：同一个键连发两次，断言第二次返回 200（不是 201）、body 里的 id 与第一次相同、库里只有一条。",
        "有键：同一个键连发两次，按文档断言第二次**重放首次结果**（首次 201，重放通常还是 201；并发没跑完时也可能 409），body 里的 id 与第一次相同、库里只有一条。",
    ),
    (
        "site/kb/interview-api.md",
        "因为它影响客户端缓存和幂等设计。判断标准永远是文档，不是个人习惯。",
        "因为它影响客户端缓存（201 默认不被缓存）和消费方的分支处理；幂等由请求方法和幂等键决定，跟状态码无关。判断标准永远是文档，不是个人习惯。",
    ),
    (
        "site/kb/interview-api.md",
        "另外只对 5xx 和连接错误重试——4xx 是请求本身有问题，重试一百次结果一样。",
        "另外只对 5xx、连接错误和 408/429 重试——408 是请求超时、429 是限流，退避之后有意义；其余 4xx 才是请求本身的问题，重试一百次结果一样。",
    ),
    (
        "site/kb/interview-api.md",
        "分别用等待策略、数据隔离、重试解决；给不稳定的用例打 `flaky` 标记并限期修，不要长期靠重试掩盖。",
        "分别用就绪等待、数据隔离、轮询等结果、修 bug 解决；重试只兜环境抖动，治不了时序问题，更不能掩盖真 bug。给不稳定的用例打 `flaky` 标记并限期修。",
    ),
    (
        "site/kb/interview-api.md",
        "401 是「没认证」：没带 token、token 过期、签名不对，客户端应该去登录。",
        "401 是「没认证」：没带 token、token 过期，客户端应该去登录；请求签名校验不通过（HMAC / AWS 那类）常按文档给 403，别一律当 401。",
    ),
    (
        "site/kb/interview-api.md",
        "两个都要测非法字段、类型错误、不存在资源（404）。",
        "两个都要测非法字段、类型错误；「资源不存在」按文档判——PATCH 通常 404，PUT 允许「不存在就创建」（201/204），别写死成 404。",
    ),
    (
        "site/kb/interview-api.md",
        "审完通常删三分之一、改三分之一。",
        "审完删改多少取决于文档质量（经验值：改动量常在 30%–60%），别当固定比例。",
    ),
    # ---- site/index.md ----
    (
        "site/index.md",
        "| 32 | 性能测试基础与指标 | ch32 | labs/ch32-perf-basics |",
        "| 32 | 性能测试基础与指标 | ch32 | labs/ch32-perf-basics |\n"
        "| 33 | 压测场景与拐点 | ch33 | labs/ch33-scenarios |\n"
        "| 34 | 压测脚本与权重 | ch34 | labs/ch34-scripts |\n"
        "| 35 | 性能归因 | ch35 | labs/ch35-analyze |\n"
        "| 36 | 中间件与链路指标 | ch36 | labs/ch36-middleware |\n"
        "| 37 | 全链路与影子隔离 | ch37 | labs/ch37-chain |\n"
        "| 38 | AI 辅助性能分析 | ch38 | labs/ch38-ai |\n"
        "| 39 | 性能平台收口 | ch39 | labs/ch39-perf-platform |",
    ),
    (
        "site/index.md",
        "| 40 | 平台架构与最小可用 | `labs/ch40-*` |\n"
        "| 41 | 项目配置与环境上下文 | `labs/ch41-*` |\n"
        "| 42 | 接口资产与一致性校验 | `labs/ch42-*` |\n"
        "| 43 | 用例与关键字执行器 | `labs/ch43-*` |\n"
        "| 44 | 测试计划与异步执行 | `labs/ch44-*` |\n"
        "| 45 | 平台收口 | `labs/ch45-*` |",
        "| 40 | 平台架构与最小可用 | `labs/ch40-*` |\n"
        "| 41 | 项目配置与环境上下文 | `labs/ch41-*` |\n"
        "| 42 | 接口资产与一致性校验 | `labs/ch42-*` |\n"
        "| 43 | 用例与关键字执行器 | `labs/ch43-executor` |\n"
        "| 44 | 测试计划与异步执行 | `labs/ch44-plans` |\n"
        "| 45 | 平台收口：报告、门槛与部署 | `labs/ch45-report` |\n"
        "| 46 | 工具链：skills 与 CLI | `labs/ch46-toolchain` |",
    ),
    (
        "site/index.md",
        "第四阶段：APP 终端 UI 自动化。把 Appium 与设备农场接进来，把「接口通 → 界面对」扩到移动端，再回到测试平台做统一编排。\n"
        "| ch43 | 用例与关键字执行器 | `labs/ch43-executor` |\n"
        "| ch44 | 测试计划与异步执行 | `labs/ch44-plans` |\n"
        "| ch45 | 平台收口：报告、门槛与部署 | `labs/ch45-report` |",
        "前六个阶段都写完了：Python 基础、接口、Web、APP（ch24–31，只用 adb，不引 Appium）、性能、平台与工具链。"
        "下一步是把六个阶段收口成一条流水线——一条命令从接口跑到界面、从压测跑到平台报告；再往后才是真机农场与多环境并行。",
    ),
    # ---- site/kb/skills/index.md ----
    (
        "site/kb/skills/index.md",
        "全部 18 个技能 ≥108 分（最低 109）；",
        "有评分的 18 个技能全部 ≥108 分（最低 109；手册页共 21 个，device-record / api-cli / report-generate-html 只写用法未打分）；",
    ),
]


def main() -> None:
    for rel, old, new in REPLACEMENTS:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        assert old in text, f"{rel} 找不到：{old[:40]!r}"
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        print(f"ok {rel} <- {old[:28]!r}")

    # skills 索引表：去掉 8 行末尾多余的 **109**
    idx = ROOT / "site/kb/skills/index.md"
    lines = idx.read_text(encoding="utf-8").splitlines()
    fixed = 0
    for i, line in enumerate(lines):
        if line.startswith("| `shenle-") and line.rstrip().endswith("**109** |"):
            lines[i] = line.rstrip()[: -len("**109** |")].rstrip() + " |"
            fixed += 1
    idx.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ok skills/index.md 去掉多余评分列 x{fixed}")


if __name__ == "__main__":
    main()
