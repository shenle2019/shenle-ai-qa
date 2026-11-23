---
title: shenle-web-cli 单跑记录
---

# shenle-web-cli 单跑记录

> 分组：**执行与定位**　手册：[shenle-web-cli](/kb/skills/web-cli)

## 环境

- 仓库：`shenle-ai-qa`，虚拟环境 `.venv`（Python 3.11.9）
- 技能：`.claude/skills/` 下已注册；可安装的命令用 `pip install -e --no-deps` 注册为控制台脚本

## 本次调用

```bash
shenle-web-cli start --headless --port 9223
```

## 真实输出

```text
$ shenle-web-cli start --headless --port 9223
[shenle] 浏览器已启动 （无头模式）：CDP 端口 9223，pid 9220
[shenle] 数据目录：E:\ailearning\shenle-ai-qa\user_data\9223
(exit 0)

$ shenle-web-cli navigate http://127.0.0.1:8733/index.html
[OK] navigate: http://127.0.0.1:8733/index.html → title="cli 冒烟"
(exit 0)

$ shenle-web-cli screenshot E:\ailearning\shenle-ai-qa\labs\ch46-toolchain\.smoke\shot.png
[OK] screenshot: E:\ailearning\shenle-ai-qa\labs\ch46-toolchain\.smoke\shot.png (1280x720) [png]
(exit 0)

$ shenle-web-cli click 页面上的登录按钮
[OK] click "页面上的登录按钮": (87, 160)
(exit 0)

$ shenle-web-cli get 页面底部那行状态文字
## 布局
位于页面左下角，单行文本，靠左对齐，字体较小，与上方“登录”按钮垂直间距适中。

## 图标
无

## 文字
已点击 2026-11-23T03:10:53.831Z

## 介绍
该区域为操作时间戳状态提示，用于记录并显示用户最近一次点击事件的具体UTC时间，辅助调试或审计。
[OK] get "页面底部那行状态文字"
(exit 0)

$ shenle-web-cli title --format json
{"url": "http://127.0.0.1:8733/index.html", "title": "cli 冒烟"}
(exit 0)

$ shenle-web-cli close
[shenle] 浏览器已关闭（端口 9223）
(exit 0)
```

## 判读

- 退出正常、能看到命令自身的用法/版本，说明**注册与依赖这一层通了**。
- 产物形态：命令回显（点击返回坐标、截图返回尺寸、`get` 按布局/图标/文字/介绍四节输出）+ 截图文件
- 需要人工或外部条件（点 SNAP、真机、视觉模型 key）的步骤，标注为「未能自动验证」，不写成功。

## 复现

```bash
.venv/Scripts/python.exe -m pytest labs/ch46-toolchain -q
```
