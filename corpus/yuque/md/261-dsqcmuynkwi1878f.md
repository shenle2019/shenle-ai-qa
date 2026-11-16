---
title: "Jenkins使用教程"
doc_id: 256205291
slug: dsqcmuynkwi1878f
book_id: 73651885
words: 3616
updated_at: 2026-02-06T06:13:39.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/dsqcmuynkwi1878f
---
**前置条件**：具备基础编程经验（如Python/pytest）

# Jenkins简介与核心概念

## 简介

官网地址：<https://www.jenkins.io/zh/>

Jenkins是开源CI&CD软件领导者， 提供超过1000个插件来支持构建、部署、自动化， 满足任何项目的需要。

## 什么是持续集成/持续交付（CI/CD）？

- **核心目标**：通过自动化流程快速、可靠地交付高质量软件。
- **典型流程**：

- **价值体现**：减少手动操作、提高协作效率、快速发现代码缺陷。

## Jenkins的核心功能与优势

- **开源免费**：社区活跃，插件生态丰富（超过1500个插件）。
- **分布式构建**：支持多节点并行执行任务，提升效率。
- **对比其他工具**：

|  |  |  |
| --- | --- | --- |
| 工具 | 优势 | 适用场景 |
| Jenkins | 高度灵活、插件丰富 | 复杂定制化流程 |
| GitLab CI | 与GitLab深度集成 | GitLab项目轻量级CI/CD |
| GitHub Actions | 原生GitHub支持 | 开源项目快速集成 |

## 版本分界线

# Jenkins安装与基础配置

## 下载

所有版本地址：<https://mirrors.jenkins.io/war-stable/>

本教程下载的版本为`2.414.3`

下载后，得到一个`jenkins.war`文件，这是一个 jar 的打包文件，可以在 Windows、Linux、MacOS 系统中使用

## 安装 Jenkins

### 前提条件

本教程使用 jdk11

如果电脑上存在多个 jdk 版本，且不同的 jdk 版本都需要被使用，此时可以使用临时环境变量来启动 jenkins

，查看教程中的 JDK 切换，非常重要，必须掌握的技能

### 启动 Jenkins

#### linux

- 需要使用无头模式启动：`java -Djava.awt.headless=true -jar jenkins.war`
- 通过`--httpPort=9090`指定启动端口号：`java -Djava.awt.headless=true -jar jenkins.war --httpPort=9090`

开放端口号

在浏览器中通过 IP 地址访问

创建启动脚本`vi jenkins.sh`

添加如下内容

添加执行权限：

- **快速使用命令**

|  |  |  |
| --- | --- | --- |
| **场景** | **命令** | **说明** |
| **默认启动** | `sudo ./jenkins.sh start` | 使用默认JDK和端口8080 |
| **指定端口启动** | `sudo ./jenkins.sh start -p 9090` | 在9090端口运行 |
| **指定JDK路径启动** | `sudo ./jenkins.sh start -j /opt/jdk17` | 使用自定义JDK |
| **查看运行状态** | `./jenkins.sh status` | 检查服务是否运行 |
| **查看实时日志** | `./jenkins.sh logs -f` | 实时输出日志（Ctrl+C退出） |

访问 jenkins

#### windows

- `java -jar jenkins.war`，执行这个命令时，一定要注意终端所在的目录

#### mac

本机默认配置的是 jdk17

但下载的 jenkins 是需要 jdk11 启动，在此采取临时变量来启动 jenkins。获取 jdk-11 的路径

将下面的命令修改成你自己的 jdk11 的路径，然后复制到终端运行

切换成功。注意临时变量设置，只对这一个终端有效，换一个终端就依然会使用默认环境变量中的内容

启动 jenkins

> 通过临时变量来启动 jenkins 也有点麻烦，为了方法，最好是创建一个脚本，直接运行脚本来启动 jenkins。参考 2.2.2.1 linux 那一小节中最后的内容

### 访问 Jenkins

下面三种方式都可以

- 访问 `http://localhost:8080`，输入地址按回车键

- 访问 `http://127.0.0.1:8080`

在浏览器访问后，打开界面如下

不要做任何操作，关闭页面，并关闭 jenkins 服务的 cmd。继续看文档，做好国内下载源配置

## 配置 Jenkins

### 更改工作目录（选做）

该配置一般只在 Windows 系统中做，Linux 和 MacOS 没啥必要

从上面安装过程可知 `Jenkins` 的工作目录默认在 `C:\Users\ 用户名 \.jenkins` 目录下，而 `C` 盘的资源是比较珍贵的，一般情况下会尽量避免将工作目录放置 `C` 盘中，所以在有些情况下可能就需要更改工作目录，修改之前先停止 jenkins 服务

​

在环境变量中添加`JENKINS_HOME`

重新打开一个终端，然后重新启动 `jenkins`

### 初次配置

整个过程了解即可，建议自己操作一下，不想操作的看下教程，后面直接找老师要`.jenkins`目录的压缩包，然后解压替换掉自己的用户目录下的`.jenkins`目录

### 下载推荐插件

- 安装推荐插件：默认会下载较多的插件，如果没有配置国内下载源会比较慢

等待下一个页面，下面的页面，如果没有配置国内下载源，则会下载比较慢

可以创建一个管理员用户

也可以直接使用 admin 账户

## 主界面

## Manage Jenkins

# 集成 Python+Pytest+Allure 环境

## 安装 python 环境

## 配置 Allure 环境

### 安装配置 Allure

### 下载 jenkins 插件

也可以使用离线方式来安装插件，在国内地址上下载指定的插件文件

<https://mirrors.tuna.tsinghua.edu.cn/jenkins/plugins/allure-jenkins-plugin/2.32.0/>

离线安装

### 配置 Allure 工具

> 下图中的别名和安装目录都是必填项

## 新建自由风格项目

## 源码管理

jenkins 可以做很多事情，在此演示如何去构建一个 Python 项目。在实际工作中项目源码都是保存在 Git 远程仓库中。在源码管理中添加项目源的地址，再配置好账号和密码，在后面构建之后就可以自动拉取源码、下载依赖、运行项目了

### 添加凭据

这个地址，大家自己将 python 代码上传到 git 中，或者公司的 git 地址都可以。本示例中的 git 地址是本地部署的一个 gogs 服务的 git 地址

仓库内容

## 添加构建步骤

## 添加构建后步骤

​

## 构建项目

点击 Build Now 就会去 git 中下载代码，并按照前面配置的构建步骤去下载项目需要的依赖及运行项目

### 查看构建日志

## 工作空间

## 查看 Allure 报告

# 集成 Sonar

## 安装 Sonar

## 集成步骤

### 配置 SonarQube

|  |  |  |  |
| --- | --- | --- | --- |
| **令牌类型** | **User Token** | **Project Token** | **Global Analysis Token** |
| **权限范围** | 用户所有权限 | 单个项目的扫描权限 | 所有项目的扫描权限 |
| **身份关联** | 绑定用户 | 绑定项目 | 不绑定用户或项目 |
| **适用场景** | 需要用户权限的操作 | CI/CD 单项目扫描 | CI/CD 多项目扫描、自动化分析 |
| **安全性** | 高风险（全权限） | 中等风险（单项目） | 低风险（仅扫描） |

### 配置 Jenkins

#### 安装 SonarQube Scanner 插件

离线安装

下载插件：<https://mirrors.tuna.tsinghua.edu.cn/jenkins/plugins/sonar/2.17.2/sonar.hpi>

​

#### 添加凭据

去到 sonarqube 页面中复制 token

粘贴在 Secret 输入框中

#### 配置 SonarQube 服务器信息

- 点击 “Manage Jenkins” -> “Configure System”。

滚动到下面找到下图内容

#### 配置 SonarScanner 工具

- 点击 “Manage Jenkins” -> “Global Tool Configuration”。

​

## 在 Jenkins 项目中配置 SonarQube 分析

### 创建或编辑 Jenkins 项目

- 进入 Jenkins 主页，点击 “New Item” 创建新的项目，或者选择已有的项目进行编辑。

这里直接使用原先的 demo 项目

### 配置构建环境

## 立即构建

- Jenkins 会在构建过程中调用 SonarScanner 对代码进行分析，并将分析结果上传到 SonarQube 服务器。
- 分析完成后，你可以登录 SonarQube 控制台查看详细的代码分析报告。

构建日志

# 集成 Java+Maven+JaCoCo 项目（待完善）

## 集成 Maven

## 配置 Maven

## 集成 Jacoco

在 Jenkins 中集成 JaCoCo 可以帮助你对 Java 项目进行代码覆盖率分析。下面为你详细介绍集成步骤：

## 安装 JaCoCo 插件

### 下载插件

<https://mirrors.tuna.tsinghua.edu.cn/jenkins/plugins/jacoco/3.3.7/jacoco.hpi>

### 离线安装

- 打开 Jenkins 管理界面，进入 “Manage Jenkins” -> “Manage Plugins”。

## 新建自由风格项目

## 源码管理

## 构建步骤

## 添加构建后步骤

## 构建项目

## 工作空间

## 查看 JaCoCo 报告

# 集成 Jmeter

## 安装 Jmeter

## 安装相关插件

### Performance

解析 JMeter 测试结果并生成报告。

### **HTML Publisher**

展示 HTML 格式的报告。

## 创建 Jenkins 任务

### 新建任务

选择 **Freestyle project**。

### 构建环境

勾选 `Delete workspace before build starts`（可选）。

### 构建步骤

添加 `Execute shell`：

- `-e -o`: 生成 HTML 报告到指定目录。

### 构建后处理

1. 添加 `Publish Performance test result report`：

- **Report files**: `result.jtl`
- **Error thresholds**：设置失败阈值（如 90% 响应时间超过 500ms）。

1. 添加 `Publish HTML reports`：

- **HTML directory**: `report`
- **Index page**: `index.html`

### 触发自动化测试

- **定时触发**：在 `Build Triggers` 中设置 `Build periodically`（如 `H */24 * * *` 每天一次）。
- **代码提交触发**：集成 Git/SVN Webhook。
- **手动触发**：点击 `Build Now`。

# 集成 NodeJs

# 深入Jenkins流水线（Pipeline）

待更新完善

**4.1 Pipeline基础语法**

- **声明式Pipeline示例**：

**4.2 结合用户提供的pytest代码**

- **集成自定义标记**：  
  用户提供的代码片段：

**在Jenkins中运行**：

#### **五、实战案例：完整CI/CD流程**

**场景**：从代码提交到Kubernetes部署全流程自动化。

**5.1 流程设计**

**5.2 Jenkinsfile配置示例**

#### **六、常见问题与优化**

**6.1 构建失败排查**

- **典型错误**：依赖缺失、权限不足、网络超时。
- **调试方法**：

1. 查看控制台输出的详细日志。
2. 使用`sh 'pytest -v'`增加测试详细度。

**6.2 性能优化**

- **清理旧构建**：在任务配置中设置“丢弃旧的构建”，保留最近10次记录。
- **使用Docker Agent**：避免环境污染，加速任务执行。

#### **附录**

**参考资源**：

- [Jenkins官方文档](https://www.jenkins.io/doc/)
- [Pipeline语法手册](https://www.jenkins.io/doc/book/pipeline/syntax/)

**术语表**：

- **Agent**：执行构建任务的节点（物理机/容器）。
- **Stage**：流水线中的一个逻辑阶段（如构建、测试、部署）。

**教程总结**：  
通过本教程，您已掌握Jenkins的核心功能，并能够实现从代码测试到自动化部署的完整CI/CD流程。结合提供的代码示例与实战案例，可快速将知识应用于实际项目！
