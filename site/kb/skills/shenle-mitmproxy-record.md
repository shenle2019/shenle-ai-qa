---
title: shenle-mitmproxy-record
---

# shenle-mitmproxy-record

> 分组：**录制采集**　来源：`.claude/skills/shenle-mitmproxy-record`

## 它是什么

Use when recording HTTP/HTTPS traffic from clients that don't expose a CDP socket — desktop apps, mobile H5 with manual 

## 核心功能

- **桌面应用录制**：采集 Electron / Qt / .NET / Java Swing 等桌面软件的网络请求
- **手机 H5 / APP 录制**：手机 Wi-Fi 设置代理到电脑 IP，录制所有 HTTP/HTTPS 请求
- **任意 HTTP 客户端抓包**：CLI 工具、SDK、爬虫等
- **HTTPS 透明解密**：mitmproxy 用 CA 伪造证书实现解密，自动安装到系统根证书库

## 怎么用

```bash
shenle-mitmproxy-record record
shenle-mitmproxy-record record --no-browser
shenle-mitmproxy-record record --port 8888 --web-port 8889
shenle-mitmproxy-record record --no-browser --output ./output
```

## 产物与判读

接口采集统一命名 `AI-信息采集`，**不分模块**，按批次号(日期-序号)直接组织。

- **位置**：`{output}/<批次号>/`
- **格式**：`raw{NN}.json`（按录制顺序编号）
- **内容**：请求方法、URL、请求头、请求体、响应状态码、响应体
- **二进制 body**：`"base64:<...>"` 前缀 + base64 编码

完整目录示意（项目根下三个统一根目录并列）：

```text
<project-root>/
├── AI-信息采集/                    ← --output 默认值
│   └── 2026-07-28-153012/         ← 批次号(YYYYMMDD-HHMMSS)
│       ├── raw01.json
│       ├── raw02.json
│       └──

## 常见失败模式

输入缺字段、路径不存在时会直接报错；先按 SKILL.md 核对入参。

## 相关

- 全文与下载：[Skills 库](/skills/shenle-mitmproxy-record)
- 返回：[Skills 手册](/kb/skills/)

## 评分（skill-judge）

本轮新补入，尚未逐维打分；评分脚本 `scripts/_score_skills.py`，口径见 `docs/skill-scores.md`。
