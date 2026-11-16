---
title: "通过 SSH 隧道在 Python 中连接 MySQL"
doc_id: 256211349
slug: buz63nvzgty3px80
book_id: 73651885
words: 736
updated_at: 2026-02-06T06:55:22.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/buz63nvzgty3px80
---
要通过 SSH 隧道在 Python 中连接 MySQL 数据库，可以使用 `paramiko` 和 `sshtunnel` 库建立 SSH 通道，再结合 `mysql-connector-python` 或 `PyMySQL` 连接数据库。以下是具体步骤：

### **步骤 1：安装依赖库**

### **步骤 2：Python 代码实现**

### **关键参数说明**

|  |  |
| --- | --- |
| **参数** | **说明** |
| `remote_bind_address` | 目标 MySQL 在 SSH 服务器后方的地址（通常为 `('127.0.0.1', 3306)`） |
| `local_bind_address` | 本地映射端口（默认自动分配，也可手动指定如 `('127.0.0.1', 63306)`） |

### **认证方式选择**

#### **1. 使用 SSH 密钥认证（推荐）**

- 生成密钥对（如果尚未生成）：

- 将公钥 `id_rsa.pub` 内容添加到 SSH 服务器的 `~/.ssh/authorized_keys` 文件中。
- 代码中设置 `ssh_pkey='/path/to/private_key'`，无需 `ssh_password`。

#### **2. 使用密码认证**

- 直接设置 `ssh_password='your_ssh_password'`，但安全性较低。

### **常见问题处理**

#### **1. 连接超时或拒绝**

- 检查 SSH 服务器是否允许端口转发（`sshd_config` 中 `AllowTcpForwarding yes`）。
- 确认目标 MySQL 是否在 SSH 服务器本地监听（`netstat -tuln | grep 3306`）。

#### **2. 密钥权限问题**

- 确保私钥文件权限为 `600`：

#### **3. 数据库连接错误**

- 验证 MySQL 用户是否允许从 `localhost` 连接（检查 `mysql.user` 表权限）。

### **使用 PyMySQL 的替代方案**

若使用 `PyMySQL`，只需修改连接部分代码：

### **完整流程总结**

1. **建立 SSH 隧道**：通过 `sshtunnel` 将远程 MySQL 端口映射到本地。
2. **连接本地映射端口**：使用常规 MySQL 连接库访问 `127.0.0.1:local_port`。
3. **执行数据库操作**：与直接连接 MySQL 无异。

通过这种方式，可以安全地访问位于内网或受限环境的 MySQL 数据库。
