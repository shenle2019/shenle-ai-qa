"""第 25 章：定位策略的落点。

同一个控件往往有好几种找法，这里把它们收成几个函数，顺带演示「找不到时怎么办」。
"""

from __future__ import annotations

from labs._shared.app import App, AppError
from labs._shared.ui_tree import Node


def by_id(app: App, id_short: str) -> Node:
    """首选：resource-id。开发改布局时最容易保持稳定的一类。"""
    return app.find(id_short=id_short)


def by_text(app: App, text: str, *, exact: bool = True) -> Node:
    """兜底：可见文字。文案一改就失效，所以只当兜底。"""
    if exact:
        return app.find(text=text)
    return app.find(text_contains=text)


def by_desc(app: App, desc: str) -> Node:
    """无障碍描述。图标按钮通常只有 content-desc。"""
    return app.find(content_desc=desc)


def by_type(app: App, class_name: str, *, index: int = 0) -> Node:
    """按控件类型取第 N 个，最不稳，最后才用。"""
    nodes = [n for n in app.tree().walk() if n.class_name == class_name]
    if index >= len(nodes):
        raise AppError(f"{class_name} 只找到 {len(nodes)} 个，取不到第 {index} 个")
    return nodes[index]


def first_tappable(app: App) -> Node:
    """第一个可点且可见的节点，用来兜底「随便点一下」的场景。"""
    for node in app.tree().walk():
        if node.clickable and node.bounds.width > 0 and node.bounds.height > 0:
            return node
    raise AppError("界面上没有可点的节点")


def describe(node: Node) -> str:
    """把节点压成一行，写日志用。"""
    return (
        f"{node.class_name.split('.')[-1]}(id={node.id_short or '-'}, "
        f"text={node.text or '-'}, desc={node.content_desc or '-'}, "
        f"center={node.center})"
    )


def tap_all_texts(app: App, texts: list[str]) -> list[str]:
    """依次点一串文字，返回实际点到的顺序，用来验证页面栈。"""
    tapped: list[str] = []
    for text in texts:
        app.tap_text(text)
        tapped.append(text)
    return tapped
