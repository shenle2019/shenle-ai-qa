from pathlib import Path


def test_index_html_exists():
    p = Path(__file__).resolve().parent.parent / "src" / "shenle_device_record" / "static" / "index.html"
    assert p.is_file(), f"应存在 {p}"


def test_index_html_has_required_hooks():
    p = Path(__file__).resolve().parent.parent / "src" / "shenle_device_record" / "static" / "index.html"
    html = p.read_text(encoding="utf-8")
    for hook in ["id=\"live-img\"", "id=\"module-input\"", "id=\"func-input\"",
                 "id=\"desc-input\"", "id=\"ai-checkbox\"", "id=\"capture-btn\"",
                 "id=\"mode-realtime\"", "id=\"mode-ondemand\"", "id=\"fps-dec\"",
                 "id=\"fps-inc\"", "id=\"fps-display\"", "id=\"capture-count\"",
                 "id=\"status-bar\"", "id=\"capture-overlay\"", "id=\"last-path\""]:
        assert hook in html, f"index.html 必须含 {hook}"


def test_index_html_connects_to_ws():
    p = Path(__file__).resolve().parent.parent / "src" / "shenle_device_record" / "static" / "index.html"
    html = p.read_text(encoding="utf-8")
    assert "/ws" in html, "前端应连到 /ws 路径"
    assert "WebSocket" in html or "new WebSocket" in html


def test_index_html_handles_capture_result():
    p = Path(__file__).resolve().parent.parent / "src" / "shenle_device_record" / "static" / "index.html"
    html = p.read_text(encoding="utf-8")
    # 至少要有处理 captured / mode_changed / frame 三种消息的痕迹
    assert "captured" in html and "mode_changed" in html and "frame" in html