---
title: "Appium测试IOS环境搭建"
doc_id: 256209781
slug: zz1gqnzaleipyw73
book_id: 73651885
words: 737
updated_at: 2026-02-06T06:45:41.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/zz1gqnzaleipyw73
---
### **一、基础环境要求**

1. **操作系统**：macOS（建议最新稳定版，如Sonoma 14.x）。
2. **Xcode**：通过App Store安装最新版本（需与iOS版本兼容）。
3. **Xcode命令行工具**：

1. **Homebrew**（包管理工具）：

### **二、安装依赖工具**

1. **Node.js & Appium**

1. **iOS专用依赖库**

### **三、配置WebDriverAgent**

Appium通过WebDriverAgent驱动iOS设备，需手动配置：

1. **下载WebDriverAgent源码**

1. **安装依赖**

1. **Xcode项目配置**

- 打开`WebDriverAgent.xcodeproj`，选择目标设备（模拟器或真机）。
- **Signing & Capabilities**中设置开发者账号（需Apple ID或付费开发者账号）。
- 修改Bundle Identifier（避免冲突，如`com.yourcompany.WebDriverAgent`）。

### **四、启动Appium服务**

1. **启动Appium Server**

- 默认监听`0.0.0.0:4723`，可通过`--port`指定端口。

1. **验证环境**

### **五、连接设备**

#### **模拟器测试**

1. 启动Xcode模拟器：

1. **Appium Desired Capabilities配置示例**

#### **真机测试**

1. **设备准备**

- 设备开启**开发者模式**（设置 → 隐私与安全 → 开发者模式）。
- 信任电脑：连接设备后选择“信任此电脑”。
- 获取设备UDID：

1. **配置开发者证书**

- 在[Apple开发者账号](https://developer.apple.com/)中添加设备UDID。
- 创建并下载`Development Provisioning Profile`，双击安装。

1. **Appium Desired Capabilities配置**

### **六、运行测试示例**

1. **Python脚本示例**

1. **验证WebDriverAgent**

- 真机首次运行时，需在设备上手动信任开发者证书（设置 → 通用 → 设备管理）。

### **七、常见问题解决**

|  |  |
| --- | --- |
| **问题** | **解决方案** |
| `xcodebuild`权限错误 | 运行`sudo xcodebuild -license accept` |
| WebDriverAgent安装失败 | 检查Xcode签名配置，清理DerivedData |
| 真机无法连接 | 确保设备UDID已添加到开发者账号，重启usbmuxd |
| `Could not proxy command` | 检查Appium Server日志，确认端口未被占用 |

### **八、进阶优化**

1. **并行测试**：使用`appium -p 4723 -bp 5000`指定不同端口启动多实例。
2. **日志分析**：通过`idevicesyslog`实时查看设备日志。
3. **CI集成**：结合Jenkins/GitHub Actions实现自动化测试流水线。

​
