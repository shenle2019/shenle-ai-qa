---
title: "Python打包exe"
doc_id: 256211458
slug: ro9hew8qtip7xnvc
book_id: 73651885
words: 792
updated_at: 2026-02-06T06:56:01.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/ro9hew8qtip7xnvc
---
将多模块 Python 项目打包成 EXE 时，需要确保所有模块、依赖项和资源文件都被正确识别和包含。以下是详细的分步指南，以 **PyInstaller** 为例（推荐用于复杂项目）：

### **一、项目结构准备**

假设你的项目目录结构如下：

### **二、安装 PyInstaller**

### **三、核心打包步骤**

#### **1. 生成.spec 文件（推荐用于复杂项目）**

- `--name`：指定 EXE 名称（可选）。
- `--onedir`：生成包含依赖的文件夹（默认，体积较小）；`--onefile`：生成单个 EXE 文件（体积大，但部署方便）。

执行后会在项目根目录生成 `my_app.spec` 文件，后续通过修改此文件配置打包规则。

#### **2. 配置.spec 文件**

打开生成的 `.spec` 文件（以 `my_app.spec` 为例），重点修改以下部分：

##### **(1) 包含自定义模块（解决模块缺失问题）**

PyInstaller 可能无法自动识别深层模块，需手动添加到 `hiddenimports` 或 `pathex`：

##### **(2) 包含资源文件（如图标、配置文件）**

使用 `datas` 参数将非代码文件复制到输出目录：

#### **3. 执行打包命令**

- 打包完成后，EXE 文件位于 `dist/` 目录下。
- 若使用 `--onefile`，直接运行 `dist/my_app.exe`；若使用 `--onedir`，运行 `dist/my_app/my_app.exe`。
