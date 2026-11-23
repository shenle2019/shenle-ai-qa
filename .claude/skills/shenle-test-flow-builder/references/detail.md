## 🔄 核心流程（6 步）

### Step 1：意图识别 + 模式判断

- 提取：业务场景 / 测试类型 / 测试点
- 判断：智能生成 / 向导 / 自由组合
- 缺信息 → 逐条追问（每次一条）

### Step 2：精读源材料（只读不写）

按测试类型精准定位，只读相关目录，不遍历整个工程。

| 测试类型 | 优先精读哪些源 |
|----------|---------------|
| 接口 | `AI-接口API测试/AI-接口管理/`（接口文档）→ `AI-接口API测试/AI-测试用例/`（手工用例）→ `AI-知识库/接口用例相关知识库/` |
| Web UI | `AI-WEB功能测试/AI-测试点分析/` → `AI-WEB功能测试/AI-测试用例/` → `AI-知识库/WEB自动化执行知识库/` |
| 多类型混合 | 按上述规则分别读取 |
| 性能 | `AI-性能测试/` + 接口文档 |

精读策略：
- 用户说具体功能（如"登录"）→ AI 在对应目录下 `Grep` 搜索"login/登录"关键字
- 用户给具体文档路径 → 用 `Read` 直接读该文件
- 源材料**只读不写、不做任何修改**

### Step 3：精准扫描已有自动化资源

**核心原则：绝不主动全量遍历。** 只在用户指明测试类型和关键字后才扫描，限定在对应目录。

```
用户输入："用户登录的 Web UI 测试"

AI 提取：类型=Web UI、关键字=登录/login

扫描范围（用 Grep）：

  源材料（找可转换的手工用例）：
  ✅ AI-WEB功能测试/测试用例/**/*.md        → Grep "登录/login"
  ✅ AI-WEB功能测试/测试点分析/**/*.md       → Grep "登录/login"

  已有自动化资源（找可复用的）：
  ✅ AI-自动化测试用例/web/**/*.yaml          → Grep name 匹配"登录"
  ✅ AI-动态函数管理/**/*.py                 → Grep 元数据行，匹配"登录/用户"
  ✅ AI-自动化测试编排/*.yaml                 → Grep name

  不做：
  ❌ AI-自动化测试用例/api/                  → 不扫（类型不匹配）
  ❌ AI-自动化测试用例/performance/          → 不扫
```

扫描结果以清晰格式呈现，标注哪些可**复用**、AI **建议新建**什么。

### Step 4：生成预览（关键确认点）

扫描完成后，输出**完整链路预览**，明确标注 📄转换、♻️复用 和 🔨新建：

```
📋 编排预览：「用户登录完整流程」

┌──────────────────────────────────────────────────────┐
│  case_flow: 用户登录完整流程                           │
│  tags: [冒烟, 主流程]                                  │
│                                                      │
│  [Task 1] 获取用户登录信息                            │
│    类型: dynamic-function                             │
│    来源: ♻️ 复用 → get_login_info                      │
│    输出: username, password                           │
│                                                      │
│  [Task 2] 正常登录                                   │
│    类型: web                                          │
│    来源: 📄 转换 → 登录表单-正常登录                    │
│    手工用例: AI-WEB功能测试/测试用例/首页/会员登录_*.md │
│    输入: username, password (← Task 1)                │
│                                                      │
│  [Task 3] 密码错误登录                                │
│    类型: web                                          │
│    来源: 📄 转换 → 登录表单-密码错误                    │
│    输入: username (← Task 1), wrong_password           │
│                                                      │
│  [Task 4] Token 过期访问 ⚠️ 需新建                    │
│    类型: api                                          │
│    来源: 🔨 新建（手工用例无对应条目，需确认）          │
│    输入: expired_token                                │
│                                                      │
│  📄 将转换: 2 个手工用例 → 自动化用例 YAML            │
│  🔨 将新建: 1 个纯自动化用例（待确认）                 │
│  ♻️ 将复用: 1 个动态函数                              │
│  🧩 将生成: 1 个编排文件                              │
└──────────────────────────────────────────────────────┘

是否确认生成？（回复"确认"或"调整 XXX"）
```

**必须等待用户确认后才写入文件！**

### Step 5：依次写入文件

确认后，严格按依赖顺序执行：

```
① 新建动态函数（如果有）
   → 调用 Skill("shenle-dynamic-function-generator")
   → 拿到 function_code 后继续

② 自动化用例 YAML（转换优先，新建兜底）
   → 有手工用例 → 转换格式写入 YAML，source_id 沿用原 UUID
   → 无手工用例 → ⚠️ 确认后新建（告知用户不一致风险）
   → 写入: AI-自动化测试用例/{类型}/{module}/{uuid}.yaml

   > **📁 {类型} 取值集合**：`api` / `web` / `app` / `pc` / `mini-program` / `performance`
   >
   > ⚠️ **runner 兼容性说明**：当前 `shenle-test-runner` 仅实现 `api` / `web` / `dynamic-function` 三种 type 的执行路径。`app` / `pc` / `mini-program` / `performance` 是**约定先行的命名**，实际执行需要在 runner 代码（`plan_loader.py` 的 `CaseType` 枚举 + `prompt_builder.py` 路由）中扩展能力。在 runner 端未完成扩展前，新类型的编排 task 加载时会抛 `PlanLoadError: task.type 不支持`。本 Skill 当前只为这些新类型生成 YAML 用例文件，不保证编排能直接被 runner 执行。

③ 编排文件 .yaml（核心产物）
   → AI-自动化测试编排/{uuid}.yaml
   → 含 name / priority / tags / case_flows → tasks
   → 每个 task 引用前两步产物的 source_id

④ YAML 格式验证（⚠️ 必须执行，不可跳过）
   → 所有 .yaml 文件写入后，用 Python yaml.safe_load() 逐文件验证
   → 验证通过才继续，失败则定位修复后重新验证
   → 特别注意：含 {{ }} 占位符的步骤值必须加单引号包裹，否则 YAML 会把 { 解析为 flow mapping
   → 验证命令（从工作空间根目录执行）：
     python -c "
     import yaml
     files = ['待验证文件1.yaml', '待验证文件2.yaml', ...]
     for f in files:
         with open(f, 'r', encoding='utf-8') as fh:
             yaml.safe_load(fh)
         print(f'✅ {f}')
     print('全部 YAML 加载成功')
     "

⑤ 汇总报告
   → 列出所有转换/复用/新建的文件路径
   → 明确标注：转换了几个手工用例、新建了几个纯自动化用例
   → 附带 YAML 验证结果（全部通过 / 哪些失败已修复）
   → 提示："要执行这个 flow 吗？"
```

### Step 6：可选执行

询问用户是否立即执行。如果是，调用：

```bash
shenle-test-runner run <root_dir> <plan_id>
```

---
