## 🔄 核心流程（6 步）

### Step 1：意图识别 + 收集候选编排

#### 1.1 用户输入分类

| 用户说 | 处理方式 |
|--------|---------|
| 没说具体编排 / 只说"生成测试计划" | **列出全部编排**让用户选 |
| 说了标题关键字（如"登录接口"） | 先**过滤**名称匹配项，命中 1 个直接选用，命中多个再列 |
| 说了具体 ID（含横线/不含横线都可以） | **直接选用**，无需再次确认 |
| 说了多个 ID / 标题 | 全部**直接选用**为 flow |

#### 1.2 扫描编排目录

```
{工作空间}/AI-自动化测试编排/*.yaml
```

**读取方式**：用 `Glob` 列出所有 `.yaml`，逐个 `Read` 提取 `name` 字段（位于第 1 行）。

每个编排的关键信息：

| 字段 | 提取位置 | 示例 |
|------|---------|------|
| `sourceFlowId` | 文件名去后缀，**保留原始格式**（含横线/不含横线都保留） | `c5e7f8a9-0b1c-2d3e-4f5a-6b7c8d9e0f1a` 或 `4e2c4a40-4ee3-45ea-bac4-aede9a44c90f` |
| `sourceFlowFile` | 文件名 | `c5e7f8a9-0b1c-2d3e-4f5a-6b7c8d9e0f1a.yaml` |
| `name` | 第 1 行 `name:` 字段 | 登录接口用例编排 |
| `priority` | 第 2 行 | high |
| `tags` | 第 3+ 行数组 | 接口测试、登录、P0-P3 |

> ⚠️ **sourceFlowId 保留原始格式**：项目里既有 `c5e7f8a90b1c2d3e4f5a6b7c8d9e0f1a`（32 位无横线）也有 `4e2c4a40-4ee3-45ea-bac4-aede9a44c90f`（标准 UUID）。两种都合法，写 plan 时按文件名原样抄，不要自作主张加/去横线。

#### 1.3 展示给用户（让选 flow）

用 `AskUserQuestion` 让用户多选编排，header 用"选编排"，问题示例：

> **请选择要纳入测试计划的编排**（可多选）
>
> 选项（最多展示 4 个，超过则展示前 4 个 + "其他"自动收集）：
> 1. c5e7f8a9…0f1a — 登录接口用例编排
> 2. d6f8a9b0…1a2b — 登录→更新用户信息
> 3. e7f8a9b0…2a3b — 登录成功 - 修改用户信息
> 4. 4e2c4a40…c90f — 用户注册+登录完整流程

**多选模式（multiSelect: true）**：用户可以勾选 1 到 N 个。

#### 1.4 标题过滤示例

用户说"做一个登录接口的 plan" → AI 扫描后用标题过滤：
- "登录接口用例编排" ✅ 命中
- "登录→更新用户信息" ✅ 命中
- "登录成功 - 修改用户信息" ✅ 命中
- "用户注册+登录完整流程" ✅ 命中（包含"登录"）
- 如果只命中 1 个，**直接选用**并告知用户；
- 命中多个 → 列出来让用户确认全选/部分选。

---

### Step 2：决定 plan 类型（type，仅供内部参考）

> ⚠️ **本步骤仅用于内部记录 plan 类型，不影响目录命名**（目录命名见 Step 4，已硬编码为 `web`）。这里输出的 type 仍可作为 plan 性质的快速参考。

`type` 合法取值：

| 类型 | 含义 | 推断规则 |
|------|------|---------|
| `api` | 全是接口类 task | 所有 flow 的 task 全部 `type: api` |
| `app` | 全是移动端 UI（android/ios/harmonyos/miniapp） | 所有 task 都是 UI 移动端 |
| `web` | 全是 Web UI（含 pc） | 所有 task 都是 web/pc |
| `mixed` | 跨多种类型 | 不符合上面任一纯类型 |

**推断策略**：

1. 优先**自动推断**：扫描所选编排的所有 task.type，按上表归类。
2. 单一类型 → 用该类型；
3. 跨类型 → 用 `mixed`；
4. 推断结果只在预览阶段展示给用户，**不写入目录名**。

---

### Step 3：收集计划元信息

按顺序处理（**默认值直接采用，不询问**；只有 `priority` / `environmentKey` 必要时才问）：

#### 3.1 plan name（必填，**默认值，不询问**）

**默认值**：所选 flow 的 `name` 字段用 ` + ` 拼接。

| 选中 flow 数 | plan name 取值 | 示例 |
|--------------|--------------|------|
| 1 个 | 直接用该 flow 的 `name` 字段原值 | `登录接口用例编排` |
| 多个 | 用 ` + ` 拼接，**保留原始中文/符号** | `登录接口用例编排 + 登录→更新用户信息` |

> 💡 plan name 与目录名末尾的 `{编排name}` 段完全一致。**直接采用默认值，不发起反问**。如需自定义命名，由用户事后改 `meta.yaml` 的 `name` 字段。

#### 3.2 priority（必填，**默认值，不询问**）

**默认值**：`high`（与所选 flow 的 priority 一致；如有 flow 是 medium/low，则按所选 flow 中最高的）。

**优先级映射**：

| 所选 flow 的 priority | plan 默认 priority |
|---------------------|---------------------|
| 全部 high | `high` |
| 含 high + medium | `high` |
| 全部 medium | `medium` |
| 含 medium + low | `medium` |
| 全部 low | `low` |

> 💡 **直接采用默认值，不发起反问**。

#### 3.3 environmentKey（必填）

从 `{工作空间}/AI-环境变量/` 目录的**子目录名**读取（每个子目录 = 一套环境），用 `Glob` 列出。

**默认选中**当前已有 plan 引用最多的环境（一般是 `读书屋-测试`），或工作空间里**唯一**的环境。

> 💡 优先用 Glob + 简单计数自动选中，**不发起反问**。仅当工作空间存在多个环境目录、且用户引用次数打平时，才询问用户。

#### 3.4 executionStrategy（必填，**默认值，不询问**）

**固定默认值**：`serial`（按 `flows[]` 数组顺序串行执行）

**取值规则**：

| 用户场景 | executionStrategy 取值 |
|---------|------------------------|
| 用户未指定 | `serial`（**默认**） |
| 用户主动说"并行"/"parallel" | `parallel` |

> ⚠️ **直接采用默认值 `serial`，不发起反问**。仅在用户**主动**要求并行时才改为 `parallel`（属"修改现有 plan"的高级能力）。

#### 3.5 tags（可选）

询问用户是否要打标签。如果要，列出**所有所选 flow 的 tags 并集**作为候选（用户多选或自定义）。

**优先级规则**：
- 用户没指定 tags → 不写 `tags` 字段，或填 `[]`；
- 用户指定 → 用所选 flow 的 tags + 用户自定义 tags 的并集（去重）。

> ⚠️ **关键**：`meta.yaml` 的 plan-level `tags` 是可选的；当存在时它描述整个 plan，**不要**覆盖掉每个 flow 自己的 `tags`（flow-level tags 必须保留）。

---

### Step 4：决定保存位置（固定规则，不询问）

**保存位置固定**：`{工作空间}/AI-自动化测试计划/plan-web-{YYYYMMDD-HHMMSS}-{编排name}/meta.yaml`

> ⚠️ 本规则不询问用户、不接受覆盖。如需自定义命名，由用户事后再 `mv` 目录。

**目录命名规则（硬编码）**：

```
plan-web-{YYYYMMDD-HHMMSS}-{编排name}
```

| 段 | 取值 | 说明 |
|----|------|------|
| `plan-` | 固定前缀 | — |
| `web` | 固定 | 通用 Web 平台标识 |
| `YYYYMMDD-HHMMSS` | 当前时间戳 | 例：`20260910-101530` |
| `{编排name}` | 所选 flow 的 name 拼接 | 见下方拼接规则 |

**编排 name 拼接规则**：

| 选中 flow 数 | 编排name 取值 | 示例 |
|--------------|-------------|------|
| 1 个 | 直接用该 flow 的 `name` 字段原值 | `登录接口用例编排` |
| 多个 | 用 ` + ` 拼接，**保留原始中文/符号** | `登录接口用例编排 + 登录→更新用户信息` |

**实例**：

- 单 flow：`plan-web-20260910-101530-登录接口用例编排`
- 多 flow：`plan-web-20260910-101530-登录接口用例编排 + 登录→更新用户信息`
- 单 flow 名字含特殊符号（→）：`plan-web-20260910-101530-登录→更新用户信息`

> 💡 **id 字段同名**：plan 的 `id` = 目录名（不带 `.yaml`）。例：`plan-web-20260910-101530-登录接口用例编排 + 登录→更新用户信息`。

---

### Step 5：写入 meta.yaml（核心产物）

#### 5.1 目录结构

```
{工作空间}/AI-自动化测试计划/plan-web-{YYYYMMDD-HHMMSS}-{编排name}/
└── meta.yaml
```

#### 5.2 meta.yaml 模板（**严格按此结构**）

```yaml
id: plan-web-20260910-101530-登录接口用例编排 + 登录→更新用户信息
name: 登录接口用例编排 + 登录→更新用户信息
priority: high
environmentKey: 读书屋-测试
executionStrategy: serial
flows:
  - sourceFlowId: c5e7f8a9-0b1c-2d3e-4f5a-6b7c8d9e0f1a
    sourceFlowFile: c5e7f8a9-0b1c-2d3e-4f5a-6b7c8d9e0f1a.yaml
    name: 登录接口用例编排
    priority: high
    tags:
      - 接口测试
      - 登录
      - P0-P3
  - sourceFlowId: d6f8a9b0-1c2d-3e4f-5a6b-7c8d9e0f1a2b
    sourceFlowFile: d6f8a9b0-1c2d-3e4f-5a6b-7c8d9e0f1a2b.yaml
    name: 登录→更新用户信息
    priority: high
    tags:
      - 接口测试
      - 主流程
      - Token 串联
created_at: '2026-09-10 10:15:30'
```

#### 5.3 字段详解

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `id` | string | ✅ | 计划唯一 ID，**等于目录名** | `plan-web-20260910-101530-登录接口用例编排 + 登录→更新用户信息` |
| `name` | string | ✅ | 计划显示名 | `登录接口用例编排 + 登录→更新用户信息` |
| `priority` | string | ✅ | high/medium/low | `high` |
| `environmentKey` | string | ✅ | 环境目录名（`AI-环境变量/{env}`） | `读书屋-测试` |
| `executionStrategy` | string | ✅ | **固定 `serial`**（不询问用户） | `serial` |
| `flows` | array | ✅ | 编排列表，**顺序就是执行顺序** | 见下表 |
| `tags` | array | ❌ | 整个 plan 的标签（plan-level，可选） | `[冒烟, 主流程]` |
| `created_at` | string | ✅ | `YYYY-MM-DD HH:MM:SS`，**必须单引号包裹** | `'2026-09-10 10:15:30'` |

#### 5.4 flows[]. 字段详解

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sourceFlowId` | string | ✅ | 编排 ID（**保留原始格式**，含或不含横线都行） |
| `sourceFlowFile` | string | ✅ | 编排文件名（必须存在于 `AI-自动化测试编排/`） |
| `name` | string | ✅ | 从编排 YAML 第 1 行 `name` 字段照抄 |
| `priority` | string | ✅ | 从编排 YAML 第 2 行照抄 |
| `tags` | array | ✅ | 从编排 YAML `tags` 字段照抄 |

#### 5.5 tags 标签推荐

参考 `shenle-test-flow-builder` 的常用标签：

| 标签 | 含义 |
|------|------|
| 冒烟 | 冒烟测试，快速验证核心功能 |
| 主流程 | 主要业务流程，核心链路 |
| P0 / P1 / P2 / P3 | 优先级（P0 最高，需立即处理） |
| 接口测试 / Web测试 / App测试 | 测试类型 |
| Token 串联 | 跨 task 数据依赖 |

---

### Step 6：预览 → 用户确认 → 落盘 → 询问执行

#### 6.1 输出预览

写文件**之前**先输出完整预览：

```
📋 测试计划预览

├─ 📂 保存位置
│   {工作空间}/AI-自动化测试计划/plan-web-20260910-101530-登录接口用例编排/
│
├─ 📄 meta.yaml 内容
│   id: plan-web-20260910-101530-登录接口用例编排
│   name: 登录接口用例编排
│   priority: high
│   environmentKey: 读书屋-测试
│   executionStrategy: serial
│   flows:
│     - sourceFlowId: c5e7f8a9-0b1c-2d3e-4f5a-6b7c8d9e0f1a
│       sourceFlowFile: c5e7f8a9-0b1c-2d3e-4f5a-6b7c8d9e0f1a.yaml
│       name: 登录接口用例编排
│       priority: high
│       tags: [接口测试, 登录, P0-P3]
│   created_at: '2026-09-10 10:15:30'
│
└─ 📊 摘要
    - 编排数: 1
    - 环境: 读书屋-测试
    - 执行策略: serial（默认）
    - 优先级: high

是否确认生成？（回复"确认"或"调整 XXX"）
```

**必须等待用户确认后才写入！**

#### 6.2 写入文件

确认后：
1. `mkdir -p` 计划目录
2. `Write` 写入 `meta.yaml`（含 BOM-free UTF-8 + LF 换行）
3. **YAML 验证**（必做）：
   ```bash
   python -c "import yaml; d=yaml.safe_load(open(r'<plan_dir>/meta.yaml', encoding='utf-8')); print('✅ meta.yaml 加载成功:', d.get('id'))"
   ```
4. 验证失败 → 立即报错并定位修复，不允许留坏文件。

#### 6.3 落盘报告

```
✅ 测试计划已生成

📂 {工作空间}/AI-自动化测试计划/plan-web-20260910-101530-登录接口用例编排/
└── meta.yaml  (✅ YAML 验证通过)

📋 摘要
├─ 编排: 1 个
│   └─ c5e7f8a9…0f1a — 登录接口用例编排
├─ 环境: 读书屋-测试
├─ 执行策略: serial
└─ 优先级: high
```

#### 6.4 询问是否执行

用 `AskUserQuestion`：

> **测试计划已生成，是否立即执行？**
>
> 选项：
> 1. ✅ 是，立即执行（推荐）→ 调 `shenle-test-runner`
> 2. ❌ 否，先不执行

如果用户选"是"，调用 `shenle-test-runner` Skill（按其规范传参）：

```bash
shenle-test-runner run {root_dir} {plan_id}
```

其中：
- `{root_dir}` = 工作空间根目录（即 `{工作空间}/`，包含 AI-自动化测试/ 等子目录）
- `{plan_id}` = `plan-web-20260910-101530-登录接口用例编排`

> ⚠️ **执行细节**：用户确认执行后，**改用 `Skill("shenle-test-runner")`** 让它接管（它会处理 skill 选择、env 加载等）。不要自己拼 CLI 命令。

---
