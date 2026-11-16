---
title: "pipenv使用教程"
doc_id: 256211361
slug: su7432lbtozb7qpf
book_id: 73651885
words: 905
updated_at: 2026-02-06T06:55:26.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/su7432lbtozb7qpf
---
`pipenv` 是 Python 项目的依赖管理工具，**结合了虚拟环境（Virtual Environment）和包管理（**`pip` **+** `requirements.txt`**）的功能**，提供更简洁高效的工作流。以下是 `pipenv` 的完整使用指南：

### **1. 核心功能**

- **自动创建和管理虚拟环境**：无需手动激活/退出环境。
- **依赖隔离**：每个项目独立依赖，避免版本冲突。
- **依赖锁定**：生成 `Pipfile.lock` 确保依赖版本精确复现。
- **开发/生产依赖分离**：区分必需依赖和开发工具（如测试框架）。
- **兼容** `requirements.txt`：支持导入和导出传统依赖文件。

### **2. 安装与配置**

#### **(1) 安装 pipenv**

#### **(2) 配置环境变量（可选）**

- **指定虚拟环境存储位置**（默认在项目目录）：

### **3. 基础使用**

#### **(1) 初始化项目**

#### **(2) 安装依赖**

#### **(3) 激活虚拟环境**

#### **(4) 运行脚本**

#### **(5) 依赖管理**

### **4. Pipfile 与 Pipfile.lock**

- `Pipfile`：TOML 格式的依赖描述文件（替代 `requirements.txt`）。

- `Pipfile.lock`：JSON 格式的精确依赖版本锁定文件（需提交到版本控制）。

### **5. 高级用法**

#### **(1) 从 requirements.txt 迁移**

#### **(2) 生成 requirements.txt**

#### **(3) 指定 Python 版本**

#### **(4) 多环境配置**

### **6. 常见问题与解决**

#### **问题 1：安装速度慢**

- **解决**：更换国内镜像源（如清华源）：

#### **问题 2：依赖冲突**

- **解决**：使用 `pipenv check` 检查安全漏洞和兼容性，手动调整版本。

#### **问题 3：虚拟环境位置混乱**

- **解决**：通过环境变量统一管理位置：

### **7. 命令速查表**

|  |  |
| --- | --- |
| **命令** | **作用** |
| `pipenv install` | 初始化虚拟环境并创建 Pipfile |
| `pipenv install <package>` | 安装包并更新 Pipfile |
| `pipenv uninstall <package>` | 卸载包并更新 Pipfile |
| `pipenv update` | 更新所有依赖到最新版本 |
| `pipenv lock` | 生成或更新 Pipfile.lock |
| `pipenv graph` | 显示依赖树 |
| `pipenv check` | 检查安全漏洞和兼容性问题 |
| `pipenv --rm` | 删除当前虚拟环境 |

### **8. 最佳实践**

1. **提交** `Pipfile.lock`：确保团队和部署环境依赖一致。
2. **分离开发依赖**：使用 `--dev` 标记测试工具、代码检查器等。
3. **定期更新依赖**：运行 `pipenv update` 保持依赖安全。
4. **结合 Docker**：在容器中通过 `pipenv install --system` 部署应用。

通过 `pipenv`，你可以告别手动管理 `requirements.txt` 和虚拟环境的繁琐，专注于代码开发！
