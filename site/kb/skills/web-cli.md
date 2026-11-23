---
title: shenle-web-cli
---

# shenle-web-cli

> 分组：**执行与定位**　来源：`.claude/skills/web-cli`

## 它是什么

给网页截图，让视觉模型找元素，直接点击、输入、断言。

技能自带的触发描述：

> 通过自然语言驱动 Chromium 跑 WEB 测试用例。典型触发词：「用 shenle-web-cli 跑这个用例」「AI 执行登录流程」「自动化点这个按钮」「在搜索框里输入」「自动截图取证」「截一下当前页面」「点击「提交」按钮」「滚动到列表底部」「断言当前 URL」「跑一轮回归」「回放这个测试」。本技能封装 `sh

## 核心功能

- `--port` 复用已开浏览器会话，`--headless` 适合流水线
- 元素不依赖固定选择器，靠视觉 + 语义定位
- 内置截图、滚动、页面描述、断言等常用动作

## 怎么用

```bash
shenle-web-cli open https://example.com
shenle-web-cli click --text "登录"
shenle-web-cli screenshot -o out.png
```

## 产物与判读

操作日志 + 截图；断言失败时给出视觉差异说明

## 常见失败模式

需要视觉模型 key；页面渲染慢时首次定位会超时

## 相关

- 单跑记录：[shenle-web-cli 单跑记录](/labs/skills/web-cli)
- 返回：[Skills 手册](/kb/skills/)
