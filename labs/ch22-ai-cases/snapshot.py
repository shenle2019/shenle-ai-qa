"""把页面压成一份「模型能读懂、人也能核对」的快照。

不把整页 HTML 丢给模型：太长、噪声太多、还容易让它编造不存在的 id。
只给：地址、标题、标题层级、可交互控件清单（带 data-testid）、正文摘要。
"""

from __future__ import annotations

from playwright.sync_api import Page

SNAPSHOT_JS = """
() => {
  const controls = [];
  document.querySelectorAll('input, select, textarea, button, a').forEach(el => {
    const text = (el.innerText || '').trim();
    const testid = el.getAttribute('data-testid');
    if (!testid && !text) return;
    controls.push({
      tag: el.tagName.toLowerCase(),
      role: el.getAttribute('role') || (el.tagName === 'BUTTON' ? 'button' : el.tagName === 'A' ? 'link' : 'input'),
      name: text || el.getAttribute('aria-label') || el.getAttribute('placeholder') || '',
      testid: testid || '',
      type: el.getAttribute('type') || '',
      placeholder: el.getAttribute('placeholder') || ''
    });
  });

  return {
    title: document.title,
    headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(h => h.innerText.trim()).filter(Boolean),
    controls,
    text: (document.body.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 1200)
  };
}
"""


def snapshot(page: Page) -> dict:
    data = page.evaluate(SNAPSHOT_JS)
    data["url"] = page.url
    return data


def render(snap: dict) -> str:
    """把快照转成几行紧凑文本，直接拼进提示词。"""
    lines = [f"地址：{snap['url']}", f"标题：{snap['title']}"]
    if snap["headings"]:
        lines.append("标题层级：" + " / ".join(snap["headings"][:6]))
    lines.append("可交互控件：")
    for item in snap["controls"][:20]:
        bits = [f"- {item['tag']}"]
        if item["testid"]:
            bits.append(f"testid={item['testid']}")
        if item["name"]:
            bits.append(f"名称={item['name']}")
        if item["type"]:
            bits.append(f"type={item['type']}")
        if item["placeholder"]:
            bits.append(f"placeholder={item['placeholder']}")
        lines.append(" ".join(bits))
    lines.append(f"正文摘要：{snap['text'][:400]}")
    return "\n".join(lines)
