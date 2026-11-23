// apps/shenle-web-record/shenle_web_record/assets/snap_button.js
// v3: draggable floating panel with 3 inputs (module/func/desc) + SNAP button.
(function () {
  var PANEL_ID = "__shenle_panel__";
  var BTN_ID = "__shenle_snap_btn__";
  var INPUT_MODULE = "__shenle_inp_module__";
  var INPUT_FUNC = "__shenle_inp_func__";
  var INPUT_DESC = "__shenle_inp_desc__";
  var HANDLE_ID = "__shenle_handle__";

  function build() {
    if (document.getElementById(PANEL_ID)) {
      return; // already present
    }
    if (!document.documentElement) {
      return false; // not ready yet; retry on DOMContentLoaded
    }

    var style = document.createElement("style");
    style.textContent =
      "#" + PANEL_ID + "{" +
        "position:fixed;right:18px;bottom:18px;z-index:2147483647;" +
        "background:#1f1f1f;color:#fff;border-radius:10px;" +
        "box-shadow:0 8px 24px rgba(0,0,0,.35);padding:0;" +
        "font:13px/1.4 -apple-system,Segoe UI,sans-serif;" +
        "min-width:280px;user-select:none;" +
      "}" +
      "#" + HANDLE_ID + "{" +
        "cursor:move;background:#2a2a2a;padding:6px 10px;" +
        "border-top-left-radius:10px;border-top-right-radius:10px;" +
        "font-size:11px;letter-spacing:.5px;color:#aaa;" +
        "display:flex;align-items:center;justify-content:space-between;" +
      "}" +
      "#" + PANEL_ID + " .shenle-row{" +
        "display:flex;align-items:center;gap:6px;padding:6px 10px;" +
      "}" +
      "#" + PANEL_ID + " label{" +
        "width:36px;color:#aaa;font-size:11px;" +
      "}" +
      "#" + PANEL_ID + " input{" +
        "flex:1;background:#2a2a2a;color:#fff;border:1px solid #3a3a3a;" +
        "border-radius:4px;padding:4px 6px;font:inherit;" +
        "outline:none;" +
      "}" +
      "#" + PANEL_ID + " input:focus{" +
        "border-color:#ff4d4f;" +
      "}" +
      "#" + BTN_ID + "{" +
        "margin:6px 10px 10px;width:calc(100% - 20px);" +
        "padding:8px 12px;border:none;border-radius:6px;cursor:pointer;" +
        "background:#ff4d4f;color:#fff;font:600 14px/1 inherit;" +
        "display:block;text-align:center;" +
      "}" +
      "#" + BTN_ID + ":disabled{" +
        "background:#555;cursor:not-allowed;" +
      "}" +
      "#" + BTN_ID + "[data-state=\"done\"]" +
        "{background:#52c41a;}" +
      "#" + BTN_ID + "[data-state=\"err\"]" +
        "{background:#faad14;}" +
      "#" + PANEL_ID + ".shenle-hidden{display:none !important;}";

    document.documentElement.appendChild(style);

    var panel = document.createElement("div");
    panel.id = PANEL_ID;

    var handle = document.createElement("div");
    handle.id = HANDLE_ID;
    handle.innerHTML = '<span>● ● ●</span><span>SNAP</span>';
    panel.appendChild(handle);

    function row(labelText, inputId) {
      var row = document.createElement("div");
      row.className = "shenle-row";
      var label = document.createElement("label");
      label.textContent = labelText;
      var input = document.createElement("input");
      input.id = inputId;
      input.type = "text";
      input.autocomplete = "off";
      row.appendChild(label);
      row.appendChild(input);
      return { row: row, input: input };
    }

    var r1 = row("模块", INPUT_MODULE);
    var r2 = row("功能", INPUT_FUNC);
    var r3 = row("描述", INPUT_DESC);
    panel.appendChild(r1.row);
    panel.appendChild(r2.row);
    panel.appendChild(r3.row);

    var btn = document.createElement("button");
    btn.id = BTN_ID;
    btn.type = "button";
    btn.textContent = "SNAP";
    panel.appendChild(btn);

    document.documentElement.appendChild(panel);

    // ---- Drag logic ----
    var dragging = false;
    var dragOffsetX = 0;
    var dragOffsetY = 0;
    handle.addEventListener("mousedown", function (e) {
      dragging = true;
      var rect = panel.getBoundingClientRect();
      dragOffsetX = e.clientX - rect.left;
      dragOffsetY = e.clientY - rect.top;
      // Switch to absolute positioning anchored at current spot.
      panel.style.left = rect.left + "px";
      panel.style.top = rect.top + "px";
      panel.style.right = "auto";
      panel.style.bottom = "auto";
      e.preventDefault();
    });
    document.addEventListener("mousemove", function (e) {
      if (!dragging) return;
      var x = Math.max(0, Math.min(window.innerWidth - panel.offsetWidth, e.clientX - dragOffsetX));
      var y = Math.max(0, Math.min(window.innerHeight - panel.offsetHeight, e.clientY - dragOffsetY));
      panel.style.left = x + "px";
      panel.style.top = y + "px";
    });
    document.addEventListener("mouseup", function () {
      dragging = false;
    });

    // ---- Validation / button state ----
    function refreshBtn() {
      var m = document.getElementById(INPUT_MODULE).value.trim();
      var f = document.getElementById(INPUT_FUNC).value.trim();
      btn.disabled = !(m && f);
    }
    r1.input.addEventListener("input", refreshBtn);
    r2.input.addEventListener("input", refreshBtn);
    r3.input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !btn.disabled) {
        btn.click();
      }
    });
    refreshBtn();

    // ---- Click handler ----
    btn.addEventListener("click", function () {
      var payload = {
        module: document.getElementById(INPUT_MODULE).value.trim(),
        func: document.getElementById(INPUT_FUNC).value.trim(),
        desc: document.getElementById(INPUT_DESC).value.trim(),
      };
      if (!payload.module || !payload.func) {
        setState("err", "⚠ 模块+功能必填", 1500);
        return;
      }
      if (!window.__shenle_snap__) {
        setState("err", "NOT READY", 1500);
        return;
      }
      Promise.resolve(window.__shenle_snap__(payload))
        .then(function (r) {
          if (r && r.ok) {
            setState("done", "✓ " + r.seq, 1500);
          } else {
            setState("err", "⚠ " + (r && r.error ? r.error : "ERR"), 2000);
          }
        })
        .catch(function (e) {
          setState("err", "⚠ ERR", 2000);
        });
    });

    function setState(state, text, ms) {
      btn.setAttribute("data-state", state);
      btn.textContent = text;
      if (ms) {
        setTimeout(function () {
          btn.removeAttribute("data-state");
          btn.textContent = "SNAP";
          refreshBtn();
        }, ms);
      }
    }

    return true;
  }

  if (!build()) {
    document.addEventListener("DOMContentLoaded", build, { once: true });
  }
})();