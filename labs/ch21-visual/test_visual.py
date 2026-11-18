r"""第 21 章：视觉回归与可访问性检查。

跑法::

    .\.venv\Scripts\python.exe -m pytest labs/ch21-visual -q
"""

from __future__ import annotations

import pytest

from a11y import audit, assert_clean
from visual import assert_visual, diff_ratio, shot


def test_same_page_has_zero_diff(page, site):
    page.goto(f"{site}/todos")
    first = page.screenshot(full_page=True)
    page.reload()
    page.wait_for_load_state("load")
    second = page.screenshot(full_page=True)
    assert first == second, "同一页面两次截图应该完全一致"


def test_baseline_then_compare(logged, tmp_path):
    logged.goto(f"{logged.url.rsplit('/', 1)[0]}/profile")
    baseline = shot(logged, tmp_path / "profile-baseline.png")
    ratio = assert_visual(logged, baseline, tmp_path / "profile-now.png")
    assert ratio == 0.0


def test_visual_diff_detects_change(logged, site, tmp_path):
    logged.goto(f"{site}/profile")
    baseline = shot(logged, tmp_path / "before.png")
    # 只改一个元素的背景色，模拟「样式被人动了」
    logged.add_style_tag(content="[data-testid=card] { background: #ff0000 !important; }")
    current = shot(logged, tmp_path / "after.png")
    ratio, box = diff_ratio(baseline, current)
    assert ratio > 0.001, f"应该发现差异，实际 {ratio}"
    assert box is not None
    with pytest.raises(AssertionError):
        assert_visual(logged, baseline, tmp_path / "after2.png", tolerance=0.0005)


def test_size_mismatch_is_rejected(logged, site, tmp_path):
    logged.goto(f"{site}/profile")
    tall = shot(logged, tmp_path / "tall.png")
    logged.set_viewport_size({"width": 1024, "height": 320})
    short = shot(logged, tmp_path / "short.png")
    with pytest.raises(ValueError):
        diff_ratio(tall, short)


def test_profile_is_accessible(logged, site):
    logged.goto(f"{site}/profile")
    assert_clean(logged)


def test_login_page_is_accessible(page, site):
    page.goto(f"{site}/login")
    assert_clean(page)


def test_audit_catches_missing_field_name(page, site):
    page.goto(f"{site}/login")
    page.evaluate("""() => {
      const input = document.createElement('input');
      input.type = 'text';
      document.querySelector('main').appendChild(input);
    }""")
    rules = [item["rule"] for item in audit(page)]
    assert "field-name" in rules


def test_audit_catches_missing_alt(page, site):
    page.goto(f"{site}/login")
    page.evaluate("""() => {
      const img = document.createElement('img');
      img.src = '/avatar.svg';
      document.querySelector('main').appendChild(img);
    }""")
    assert "img-alt" in [item["rule"] for item in audit(page)]


def test_audit_catches_heading_jump(page, site):
    page.goto(f"{site}/login")
    page.evaluate("""() => {
      const h3 = document.createElement('h3');
      h3.textContent = '跳级标题';
      document.querySelector('main').appendChild(h3);
    }""")
    assert "heading-order" in [item["rule"] for item in audit(page)]
