"""提示词：把「页面快照 + 一句测试目标」变成一次可校验的生成请求。

四段结构：角色 → 输入 → 任务 → 输出契约。最后一段最容易被省，但省了就等着收一堆散文。
"""

from __future__ import annotations

from snapshot import render

SYSTEM = """你是一名 Web 自动化测试工程师，负责把一个页面上能做的操作写成可执行的步骤。

硬约束：
1. 只能使用下面「控件清单」里出现过的 data-testid，不要编造；
2. 步骤动作只允许：goto / fill / click / expect_text / expect_visible；
3. 每一步都要能落到具体元素或具体文本，不接受「验证功能正常」这类描述；
4. 只输出 JSON，不要解释、不要 Markdown 围栏以外的内容。
"""

OUTPUT_SCHEMA = """{
  "cases": [
    {
      "title": "一句话说清这条用例验证什么",
      "steps": [
        {"action": "goto", "path": "/login"},
        {"action": "fill", "testid": "username", "value": "alice"},
        {"action": "click", "testid": "login-submit"},
        {"action": "expect_text", "testid": "current-user", "value": "alice"}
      ],
      "expected": "跑完这些步骤后应该看到的结果"
    }
  ]
}"""


def build_prompt(snap: dict, goal: str) -> str:
    return "\n".join(
        [
            "【输入】",
            render(snap),
            "",
            "【任务】",
            f"针对上面的页面完成这个目标：{goal}",
            "给出 1–3 条用例，覆盖成功路径与至少一个失败或边界路径。",
            "",
            "【输出】",
            "严格按这个 JSON 结构返回，不要多余字段：",
            OUTPUT_SCHEMA,
        ]
    )


def build_messages(snap: dict, goal: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": build_prompt(snap, goal)},
    ]
