---
title: "WebUI测试环境搭建"
doc_id: 256204495
slug: nyhfw6sns4yq265d
book_id: 73651885
words: 315
updated_at: 2026-02-06T06:08:09.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/nyhfw6sns4yq265d
---
## 配置环境

本教程中提供的浏览器及驱动，可以问老师要。太新的浏览器版本可能导致自动化运行时，会很慢

驱动下载地址：<https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json>

下面的浏览器版本较老，可以自己下载需要的版本，chrome 下载地址：<https://www.google.cn/intl/zh-CN_ALL/chrome/fallback/?e>

双击`chrome_76.0.3809.100.exe`进行安装，这个安装是全自动的，安装成功后就自动启动`Chrome`

chromedriver 驱动下载地址：<https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json>

### 配置环境变量

不建议有中文路径，文件中的路径只能参考不要照抄

### 检查配置

> 一定是重新打开的终端，如果在 pycharm 等工具中使用，一定要重启 pycharm。不然无法使用到最新的环境变量

- 检查`Chrome`配置

- 检查`chromedriver`配置

### 关闭浏览器自动升级

1. 点击搜索，输入服务

1. 在「名称」列表中分别找到并双击以下 2 项服务：

1. GoogleUpdater InternalService
2. GoogleUpdater Service

1. 点击「停止」按钮，并将「启动类型」设置为「禁用」。
2. 点击「应用」并关闭「服务」管理器。

只要是和更新有关的都要设置为禁用
