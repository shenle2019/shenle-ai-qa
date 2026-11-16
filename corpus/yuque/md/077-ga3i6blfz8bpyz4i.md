---
title: "【重点】Python代码调用AI"
doc_id: 256211830
slug: ga3i6blfz8bpyz4i
book_id: 73651885
words: 707
updated_at: 2026-02-06T06:58:02.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/ga3i6blfz8bpyz4i
---
# Python 调用 AI 大模型：从基础到实战的完整指南

用 Python 调用 AI 大模型其实很简单，不管是调用 OpenAI、通义千问这些大厂 API，还是本地部署的开源模型，核心都是「发送请求→获取响应」。下面按「易用性」从简单到进阶，整理了 3 种实用方法，新手也能直接抄代码跑起来。

## 一、最简单：调用大厂 API（推荐新手）

大厂的 AI 接口（如 OpenAI、通义千问）已经封装好，不用管复杂的模型部署，拿到 API 密钥就能直接用。以「通义千问」为例（免费额度够用）：

### 1. 准备工作

- 去「通义千问开放平台」注册账号，创建应用获取 `api_key`（类似密码，别泄露）

申请地址：<https://bailian.console.aliyun.com/?spm=5176.29597918.J_SEsSjsNv72yRuRFS2VknO.2.71d87b0835ITPT&tab=model#/api-key>

### 2. 核心代码（对话示例）

### 3. 运行效果

## 避坑指南：新手常犯的 3 个错误

1. **API 密钥泄露**：代码里别直接写密钥，建议用环境变量：

1. **网络问题**：国内调用 OpenAI 需配置代理，通义千问、文心一言等国内模型无此问题
2. **参数错误**：注意模型名称是否正确（如通义千问的 `qwen3-vl-plus`， 不能写错，其它模型也可以，自己尝试）
