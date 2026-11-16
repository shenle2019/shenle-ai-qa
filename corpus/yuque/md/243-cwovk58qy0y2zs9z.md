---
title: "centos7-安装SonarQube"
doc_id: 256209235
slug: cwovk58qy0y2zs9z
book_id: 73651885
words: 1639
updated_at: 2026-02-06T06:41:55.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/cwovk58qy0y2zs9z
---
# 概述

## 简介

`Sonar`是一个用于代码质量管理的开源平台，用于管理源代码的质量，可以从七个维度检测代码质量，通过插件形式，可以支持包括`java,C#,C/C++,PL/SQL,Cobol,JavaScrip,Groovy`等等二十几种编程语言的代码质量管理与检测，在 2014 年后改名为`SonarQube`

官网：<https://www.sonarsource.com/>

## 下载

SonarQube 提供 **4 个版本**，覆盖不同规模团队需求1213：

1. **社区版（免费）**

- 基础功能：代码质量分析、安全热点检测、CI/CD 集成。
- 适用场景：个人开发者或小型团队（建议代码量 <10 万行）。

1. **开发者版（$160 / 年）**

- 新增功能：C/C++/Objective-C 语言支持、AutoConfig 自动配置、多项目聚合视图。
- 适用场景：中小型企业，需处理 10 万行以上代码。

1. **企业版（定制化收费）**

- 高级功能：COBOL、VB6 等遗留语言支持、SCIM 用户同步、无限集成 DevOps 平台。
- 适用场景：大型企业，需统一管理多项目组合。

1. **数据中心版（企业级部署）**

- 增强功能：高可用性（HA）、全球负载均衡、7×24 高级支持。
- 适用场景：跨国公司或对稳定性要求极高的场景。

可以自己下载，也可以在群里问老师要。

百度网盘 sonar 相关安装包和汉化包

链接：<https://pan.baidu.com/s/1aBdcGCCGSe6RkvxUTY4HTg> ，提取码：6818

下载后文件如下

官网下载地址：<https://www.sonarsource.com/products/sonarqube/downloads/>

下面页面中什么都不做，等待即可

# 安装

## 前提环境

### jdk

### zip 解压 安装解压工具

## 安装配置

- 本教程，`sonar`相关文件位置在`/root/software/sonar` 解压用unzip 包名

- 将解压的文件夹移动到`/opt/sonarqube`目录下，`mv sonarqube-9.7.0.61563 /opt/sonarqube`​

- 为了安全起见，不建议使用 `root` 用户运行 SonarQube，需要创建一个新用户。

- 编辑 `vi /etc/sysctl.conf` 文件，添加以下内容：

- 执行以下命令使配置生效：

- 编辑 `vi /etc/security/limits.conf` 文件，添加以下内容：

# 启动 SonarQube

使用 `sonarqube` 用户启动 SonarQube，建议开一个新的窗口来启动，以免来回切换用户

- 配置环境变量，只需要配置一次

- 运行

你可以使用以下命令检查 SonarQube 的运行状态：

如果没有权限，可以用root给权限

​

​

开放端口号，需要在一个使用 root 账号登录的窗口中执行

# 访问 SonarQube

打开浏览器，访问 `http://服务器IP地址:9000`，默认的用户名和密码都是 `admin`，首次登录后需要修改密码。默认账号`admin`和密码`admin`

第一登录成功后，会要求修改密码。自己修改即可

# Sonarqube 重启的问题

如果没有正确的关闭 sonarqube 服务，会导致 sonarqube 服务无法重启。需要删除临时文件夹`temp`

`rm -rf /opt/sonarqube/temp`

# 汉化 SonarQube

## 线上安装

## 离线安装

将`sonarqube 汉化包-9.7`在 windows 上解压，然后将`sonar-l10n-zh-plugin-9.7.jar`复制到`sonarqube`目录下`/extensions/plugins`。参考下图。`mv sonar-l10n-zh-plugin-9.7.jar /opt/sonarqube/extensions/plugins/`。然后重启`sonarqube`

重启：/opt/sonarqube/bin/linux-x86-64/sonar.sh restart

# 安装 SonarScanner

## 简介

SonarScanner 和 SonarQube 在代码质量管理流程中扮演着不同的角色，下面为你详细介绍它们的区别：

### 功能用途

- **SonarScanner**：主要用于收集代码数据。它会扫描项目源代码，依据特定规则分析代码中的各类问题，像代码漏洞、代码异味、缺乏测试覆盖等情况。扫描结束后，SonarScanner 会把分析结果发送到 SonarQube 服务器。简单来说，它的核心功能是对代码进行扫描并收集分析数据。
- **SonarQube**：是一个完整的代码质量管理平台。它接收来自 SonarScanner 的数据，将这些数据进行可视化展示，同时提供详细的代码分析报告。借助 SonarQube，团队能够清晰了解代码质量的整体状况，设置质量门来把控代码质量，还能追踪代码质量随时间的变化趋势。

### 工作方式

- **SonarScanner**：作为一个独立的命令行工具，可在本地开发环境或者持续集成（CI）服务器上运行。使用时，只需在项目根目录下执行相应的扫描命令，它就会按照配置对代码进行扫描。
- **SonarQube**：以服务器的形式存在，需要部署在服务器上并保持运行。它提供了 Web 界面，用户通过浏览器访问该界面，就能查看代码分析结果、管理项目和配置规则等。

### 应用场景

- **SonarScanner**：通常在开发人员的本地环境或者 CI/CD 流程中使用。开发人员在本地开发时可以随时运行 SonarScanner 来检查代码质量，及时发现并解决问题。在 CI/CD 流程中，SonarScanner 可以在代码提交或者构建时自动触发，确保每次代码变更都能进行质量检查。
- **SonarQube**：适用于团队协作和项目管理场景。团队成员可以通过 SonarQube 的 Web 界面查看整个项目的代码质量情况，进行问题跟踪和管理。项目管理人员可以利用 SonarQube 来制定质量标准、监控项目进度和质量趋势。

## 下载地址

<https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.7.0.2747-linux.zip>

<https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.7.0.2747-windows.zip>

<https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.7.0.2747-macosx.zip>

## 解压文件

将下载的文件解压，`unzip sonar-scanner-cli-4.7.0.2747-linux.zip -d /opt`

- 重命名文件夹，`mv /opt/sonar-scanner-4.7.0.2747-linux/ /opt/sonar-scanner`

## 配置环境变量

需要 root 账号，编辑 `/etc/profile` 文件，添加 SonarScanner 的环境变量：

验证配置是否生效，`sonar-scanner -v`

## 配置文件（了解）

非必须操作，`vi /opt/sonar-scanner/conf/sonar-scanner.properties`
