# shenle-web-record

交互式网页录制命令行工具：基于 Playwright 打开 headed Chromium 浏览器，在页面上注入一个悬浮 **SNAP** 按钮。每次点击按钮采集一对文件（视口截图 + 原始 `outerHTML`）到独立的批次目录，序号递增。不同启动会话的批次目录互不覆盖。

## 安装

```bash
cd apps/shenle-web-record
# 推荐：用 PYTHONPATH 注入而非 editable install
# （在含中文路径的项目上，pip install -e . 会污染全局 site-packages）
pip install playwright
playwright install chromium
```

要求：Python 3.11+。

## 用法

```bash
# 默认：批次根目录为当前目录，最终落盘 web/AI-信息采集/<YYYYMMDD-HHmmss>/
shenle-web-record record https://example.com

# 指定批次根目录
shenle-web-record record https://example.com -o /path/to/root

# 帮助
shenle-web-record --help

# 版本
shenle-web-record --version
```

执行后浏览器窗口弹出，页面右上角出现一个红色 **SNAP** 按钮。点击按钮采集一次；按钮短暂变绿显示 ✓ N。**关闭浏览器窗口即结束本次会话**。

## 输出文件

每次启动生成一个批次目录：

```
<ROOT>/web/AI-信息采集/<YYYYMMDD-HHmmss>/
├── img/
│   ├── screenshot_001.png
│   ├── screenshot_002.png
│   └── ...
└── json/
    ├── dom_001.json
    ├── dom_002.json
    └── ...
```

`dom_NNN.json` 结构：

```json
{
  "content": "<原始 document.documentElement.outerHTML>",
  "img": "img/screenshot_NNN.png"
}
```

- `content`：原始 outerHTML，**不转义、不结构化**
- `img`：相对于批次目录的路径

**绝不覆盖**：同一秒内重新启动会复用目录并从最大序号 +1 续号；不同批次始终是不同目录。

## 验证（手工 E2E 冒烟）

```bash
shenle-web-record record https://example.com
# 浏览器弹出 → 点击 SNAP 按钮 → 按钮短暂变绿显示 ✓ 001
# 关闭浏览器 → 命令行打印批次目录与采集数
ls web/AI-信息采集/<批次号>/img/         # 至少 1 张 png
cat web/AI-信息采集/<批次号>/json/dom_001.json
```

## 作为模块运行

```bash
python -m shenle_web_record record https://example.com
```

## 测试

```bash
pip install pytest
PYTHONPATH=. pytest
```
