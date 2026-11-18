"""可访问性静态检查：不引第三方库，直接在页面里跑一小段 JS 收问题。

查五类，都是「用户能感知」的硬伤：
1. 图片缺 alt；
2. 表单控件没有可访问名（label / aria-label / aria-labelledby / placeholder 都没有）；
3. 按钮或链接没有可读文本；
4. 标题层级跳跃（h1 -> h3）；
5. 同一页面出现重复 id。
"""

from __future__ import annotations

from playwright.sync_api import Page

AUDIT_JS = """
() => {
  const issues = [];
  const push = (rule, node, detail) => issues.push({
    rule,
    detail,
    html: node.outerHTML.slice(0, 160)
  });

  document.querySelectorAll('img').forEach(img => {
    if (!img.hasAttribute('alt')) push('img-alt', img, '图片缺少 alt');
  });

  document.querySelectorAll('input, select, textarea').forEach(el => {
    if (el.type === 'hidden') return;
    const id = el.id;
    const hasLabel = id && document.querySelector(`label[for="${id}"]`);
    const hasAria = el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby');
    const hasPlaceholder = el.hasAttribute('placeholder');
    if (!hasLabel && !hasAria && !hasPlaceholder) push('field-name', el, '表单控件没有可访问名');
  });

  document.querySelectorAll('button, a').forEach(el => {
    const text = (el.innerText || '').trim();
    const hasAria = el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby');
    if (!text && !hasAria) push('control-name', el, '按钮或链接没有可读文本');
  });

  let lastLevel = 0;
  document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
    const level = Number(h.tagName[1]);
    if (lastLevel && level - lastLevel > 1) push('heading-order', h, `标题从 h${lastLevel} 跳到 h${level}`);
    lastLevel = level;
  });

  const seen = new Set();
  document.querySelectorAll('[id]').forEach(el => {
    if (seen.has(el.id)) push('duplicate-id', el, `id 重复：${el.id}`);
    seen.add(el.id);
  });

  return issues;
}
"""


def audit(page: Page) -> list[dict[str, str]]:
    return page.evaluate(AUDIT_JS)


def assert_clean(page: Page) -> None:
    issues = audit(page)
    if issues:
        lines = [f"- [{item['rule']}] {item['detail']} :: {item['html']}" for item in issues]
        raise AssertionError("发现可访问性问题：\n" + "\n".join(lines))
