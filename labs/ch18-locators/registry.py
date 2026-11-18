"""把 YAML 里的定位描述翻译成 Playwright 的 Locator。

好处很直接：定位器只有一份，页面类只写 `self.at("todos.item")`，
换 id、换文案、换语言，改 yaml 就行，不用碰用例。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from playwright.sync_api import Locator, Page

HERE = Path(__file__).resolve().parent
DEFAULT_FILE = HERE / "locators.yaml"

ALLOWED = {"testid", "role", "label", "text", "placeholder", "css"}


class LocatorError(KeyError):
    """定位器找不到时抛自己的异常，比裸 KeyError 好排查。"""


def load(path: Path | str = DEFAULT_FILE) -> dict[str, dict[str, dict[str, Any]]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("定位器文件的最外层必须是「页面名 -> 定位器名 -> 描述」")
    return data


class Registry:
    def __init__(self, page: Page, path: Path | str = DEFAULT_FILE) -> None:
        self.page = page
        self.data = load(path)

    def spec(self, key: str) -> dict[str, Any]:
        page_name, _, locator_name = key.partition(".")
        if not locator_name:
            raise LocatorError(f"定位器 key 要写成「页面.名称」，收到 {key!r}")
        try:
            return self.data[page_name][locator_name]
        except KeyError as exc:
            raise LocatorError(f"定位器 {key!r} 不存在，检查 locators.yaml") from exc

    def at(self, key: str) -> Locator:
        return self.resolve(self.spec(key))

    def resolve(self, spec: dict[str, Any]) -> Locator:
        by = spec.get("by")
        if by not in ALLOWED:
            raise ValueError(f"不支持的定位方式 {by!r}，可选：{sorted(ALLOWED)}")

        if by == "testid":
            return self.page.get_by_test_id(spec["value"])
        if by == "role":
            return self.page.get_by_role(spec["role"], name=spec.get("name"), exact=spec.get("exact", False))
        if by == "label":
            return self.page.get_by_label(spec["value"], exact=spec.get("exact", False))
        if by == "text":
            return self.page.get_by_text(spec["value"], exact=spec.get("exact", False))
        if by == "placeholder":
            return self.page.get_by_placeholder(spec["value"])
        return self.page.locator(spec["value"])
