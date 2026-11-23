## 📊 两层体系：源材料 vs 自动化产物

> ⚠️ **关键概念**：手工用例和自动化用例是两种完全不同的东西！

### 源材料层（只读，绝不修改）

AI 从这里理解业务、提取测试场景。

```
{工作空间}/
├── AI-WEB功能测试/
│   ├── AI-测试点分析/{模块}/{功能名}.md      ← Web 测试点分析
│   └── AI-测试用例/{模块}/*.md               ← Web 手工用例（Markdown，人读）
│
├── AI-接口API测试/
│   ├── AI-接口管理/{批次}/*.md               ← 接口文档（含请求/响应详情）
│   ├── AI-测试用例/{批次}/*.md               ← 接口手工用例（Markdown，人读）
│   └── AI-信息采集/{批次}/*.json             ← 录制数据（JSON）
│
├── AI-知识库/
│   ├── WEB自动化执行知识库/                   ← Web 自动化规则
│   ├── 接口用例相关知识库/                    ← 接口测试规则
│   └── OA系统操作基本规则说明/                ← 业务规则
│
└── AI-环境变量/
    └── {环境名}/
        ├── env_var.yaml                      ← 环境变量
        └── meta.yaml                         ← 环境元信息
```

### 自动化产物层（本 Skill 写入）

格式固定，可被 `shenle-test-runner` 直接消费执行。

```
{工作空间}/
├── AI-动态函数管理/
│   └── {类型}/{function_code}.py             ← 动态函数（Python）
│                                              ← 第一行含 # AIQE_DYNAMIC_FUNCTION_META {...}
│
├── AI-自动化测试用例/
│   ├── api/{module}/{uuid}.yaml              ← 接口自动化用例（runner 已支持）
│   ├── web/{module}/{uuid}.yaml              ← WEB UI 自动化用例（runner 已支持）
│   ├── app/{module}/{uuid}.yaml              ← APP UI 自动化用例（runner 已支持）
│   ├── pc/{module}/{uuid}.yaml               ← PC 客户端自动化用例（runner 待扩展）
│   ├── mini-program/{module}/{uuid}.yaml     ← 小程序自动化用例（runner 待扩展）
│   └── performance/{module}/{uuid}.yaml      ← 性能测试用例（runner 待扩展）
│
└── AI-自动化测试编排/
    └── {uuid}.yaml                           ← 编排文件（核心产物）
                                              ← 含 case_flows → tasks 完整链路
```

### 手工用例 vs 自动化用例

| | 手工测试用例 | 自动化测试用例 |
|------|-------------|----------------|
| **格式** | Markdown | YAML |
| **内容** | 测试步骤 + 预期结果（自然语言） | input_datas + output_datas + source_id（结构化） |
| **存放** | `AI-WEB功能测试/AI-测试用例/`、`AI-接口API测试/AI-测试用例/` | `AI-自动化测试用例/{api/web/app/pc/mini-program/performance}/` |
| **读者** | 人 | 机器（shenle-test-runner） |
| **本 Skill 角色** | **源材料，只读** | **产物，写入** |

---
