"""解析 uiautomator dump 出来的窗口树。

一个 dump 长这样（节选）：

    <hierarchy rotation="0">
      <node index="0" text="" resource-id="com.demo:id/toolbar" class="android.widget.FrameLayout"
            clickable="false" enabled="true" bounds="[0,0][1080,180]">
        <node index="0" text="登录" resource-id="" class="android.widget.TextView"
              clickable="false" enabled="true" bounds="[48,84][240,144]" />
      </node>
    </hierarchy>

这一层只做三件事：把 XML 变成树、按条件找节点、算坐标。不碰 adb。
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

BOUNDS_RE = re.compile(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]")


@dataclass(frozen=True)
class Bounds:
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def center(self) -> tuple[int, int]:
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def contains(self, x: int, y: int) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    @classmethod
    def parse(cls, raw: str) -> "Bounds":
        match = BOUNDS_RE.search(raw or "")
        if not match:
            return cls(0, 0, 0, 0)
        return cls(*(int(g) for g in match.groups()))


@dataclass
class Node:
    text: str = ""
    resource_id: str = ""
    class_name: str = ""
    content_desc: str = ""
    package: str = ""
    clickable: bool = False
    enabled: bool = True
    checkable: bool = False
    checked: bool = False
    focused: bool = False
    selected: bool = False
    scrollable: bool = False
    bounds: Bounds = field(default_factory=lambda: Bounds(0, 0, 0, 0))
    children: list["Node"] = field(default_factory=list)
    parent: "Node | None" = field(default=None, repr=False, compare=False)

    # ---------- 派生属性 ----------

    @property
    def id_short(self) -> str:
        """com.demo:id/login_btn -> login_btn；没有 resource-id 就是空串。"""
        return self.resource_id.split("/", 1)[-1] if self.resource_id else ""

    @property
    def center(self) -> tuple[int, int]:
        return self.bounds.center

    @property
    def label(self) -> str:
        """用于日志/报错的短名字：text > content-desc > id_short > class。"""
        return self.text or self.content_desc or self.id_short or self.class_name.split(".")[-1]

    # ---------- 查找 ----------

    def walk(self) -> list["Node"]:
        """先序展开整棵树。"""
        nodes = [self]
        for child in self.children:
            nodes.extend(child.walk())
        return nodes

    def find_all(self, **criteria) -> list["Node"]:
        """按属性等值过滤；text 支持 None 表示忽略。"""
        return [n for n in self.walk() if n.matches(**criteria)]

    def find(self, **criteria) -> "Node":
        found = self.find_all(**criteria)
        if not found:
            raise LookupError(f"找不到节点：{criteria}")
        if len(found) > 1:
            names = ", ".join(f"<{n.label}@{n.bounds}>" for n in found[:5])
            raise LookupError(f"匹配到 {len(found)} 个节点，请加条件：{names}")
        return found[0]

    def matches(
        self,
        *,
        text: str | None = None,
        id_short: str | None = None,
        resource_id: str | None = None,
        content_desc: str | None = None,
        class_name: str | None = None,
        clickable: bool | None = None,
        enabled: bool | None = None,
        text_contains: str | None = None,
    ) -> bool:
        if text is not None and self.text != text:
            return False
        if text_contains is not None and text_contains not in self.text:
            return False
        if id_short is not None and self.id_short != id_short:
            return False
        if resource_id is not None and self.resource_id != resource_id:
            return False
        if content_desc is not None and self.content_desc != content_desc:
            return False
        if class_name is not None and self.class_name != class_name:
            return False
        if clickable is not None and self.clickable is not clickable:
            return False
        if enabled is not None and self.enabled is not enabled:
            return False
        return True

    def clickable_ancestor(self) -> "Node | None":
        """点文字点不到时，往上找最近的可点父节点。"""
        node = self.parent
        while node is not None:
            if node.clickable:
                return node
            node = node.parent
        return None

    # ---------- 输出 ----------

    def dumps(self, indent: int = 0) -> str:
        pad = "  " * indent
        flags = "".join(
            [
                "C" if self.clickable else "-",
                "E" if self.enabled else "d",
                "S" if self.scrollable else "-",
            ]
        )
        line = f"{pad}{flags} <{self.label}> {self.bounds.width}x{self.bounds.height} @{self.bounds.x1},{self.bounds.y1}"
        return "\n".join([line] + [child.dumps(indent + 1) for child in self.children])


def _bool(raw: str | None) -> bool:
    return (raw or "").strip().lower() == "true"


def _node(element: ET.Element) -> Node:
    node = Node(
        text=element.get("text", ""),
        resource_id=element.get("resource-id", ""),
        class_name=element.get("class", ""),
        content_desc=element.get("content-desc", ""),
        package=element.get("package", ""),
        clickable=_bool(element.get("clickable")),
        enabled=_bool(element.get("enabled", "true")),
        checkable=_bool(element.get("checkable")),
        checked=_bool(element.get("checked")),
        focused=_bool(element.get("focused")),
        selected=_bool(element.get("selected")),
        scrollable=_bool(element.get("scrollable")),
        bounds=Bounds.parse(element.get("bounds", "")),
    )
    node.children = [_node(child) for child in element if child.tag == "node"]
    for child in node.children:
        child.parent = node
    return node


def parse_dump(xml_text: str) -> Node:
    """把 dump 文本解析成根节点。空文本/坏 XML 抛 ValueError。"""
    if not xml_text or "<hierarchy" not in xml_text:
        raise ValueError("不是有效的 uiautomator dump")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"dump XML 解析失败：{exc}") from exc
    first = root.find("node")
    if first is None:
        raise ValueError("dump 里没有节点")
    return _node(first)


def require(node: Node, **criteria) -> Node:
    """找不到就抛 LookupError，语义比 find 更明确一点（用于断言）。"""
    return node.find(**criteria)
