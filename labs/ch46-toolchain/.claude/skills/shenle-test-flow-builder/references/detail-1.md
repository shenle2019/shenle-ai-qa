## 🧩 产物三：编排文件生成规范

### YAML 结构

```yaml
name: "流程名称"
priority: "low | medium | high"
tags:
  - "标签1"
  - "标签2"
case_flows:
  - id: "uuid"
    title: "流程标题"
    priority: "medium"
    tags: ["冒烟", "主流程"]
    tasks:
      - title: "任务名称"
        type: "dynamic-function | api | web | app | pc | mini-program | performance"
        source_id: "function_code 或 case_uuid"
        input_datas:
          - name: "参数显示名"
            value: "参数值"     # ⚠️ 引用变量必须用 {{变量名}}（详见下方规范）
        output_datas:
          - name: "输出显示名"   # ⚠️ 下游引用的是这里的 name，不是 value
            value: "输出字段名"
```

### 🔁 变量引用规范（Jinja2 语法 — ⭐核心规则）

> ⛔ **铁律**：编排文件 `input_datas[].value` 凡是**需要引用变量**的（环境变量、上游 task 输出），**必须**用 `{{变量名}}` Jinja2 语法。**严禁**写死成字面量。runner 阶段（`shenle-test-runner`）会用 `jinja2.Template(...).render(context)` 渲染，未用占位符的值就直接当字面量用，写死就再也换不了环境/换不了数据源。

> 📚 渲染机制实现参考：`shenle-test-runner/src/shenle_test_runner/executors/base.py` 的 `render_inputs()`（约 155-194 行）+ `context.py` 的 `ContextManager` + `batch.py:extract_flows()`（约 305-315 行，把 `env_var.yaml` 初始化进 `context.json`）。

#### 1. `{{变量名}}` 能引用哪些数据？

渲染上下文来自 flow 目录下的 `context.json`，其内容 = **环境变量初始值** + **之前所有 task 累积的 output_datas**：

| 数据来源 | 在 context.json 里的 key | 引用方式 |
|----------|------------------------|----------|
| **环境变量**（`AI-环境变量/{env}/env_var.yaml` 的每个 key） | 顶级 key，如 `api_project_url`、`web_project_url`、`TEST_PHONE_NUMBER` | `{{api_project_url}}`、`{{TEST_PHONE_NUMBER}}` |
| **上游 dynamic-function 的输出** | 上游 task 的 `output_datas[].name`（**中文显示名**） | `{{手机号}}`、`{{登录密码}}` |
| **上游 api/web 的输出**（AI 提取的字段） | 上游 task 的 `output_datas[].name`（**中文显示名**） | `{{用户ID}}`、`{{Token}}` |

#### 2. ⭐ 引用键名 = `output_datas[].name`，**不是** `.value`

runner 的实际写入规则（见 `shenle-test-runner/src/shenle_test_runner/executors/base.py:render_inputs` + `dynamic_function.py:90-95`）：

- dynamic-function：`ctx.update(output_values)` 的 key = 函数返回值 dict 里与 `output_datas[].value` 同名的字段对应的 **output_datas[].name**。
- api：AI 提取后 `ctx.update({o.name: o.value for o in outputs if o.value is not None})` —— **直接用 name 当 key**。

**举例**（来自工作区真实编排 `8b6030cb-cdc1-47cf-b9dd-96e9726dfddc.yaml`）：

```yaml
# Task 1: dynamic-function 输出 name=value 两列
- title: 获取登录账号信息
  type: dynamic-function
  source_id: get_login_credentials
  output_datas:
    - name: 手机号        # ← 这个 name 才是 context.json 里的 key
      value: phone_number # ← 函数返回值里叫 phone_number 的字段
    - name: 登录密码
      value: password

# Task 2: web 用例输入 value 引用 name（不是 value）
- title: 正常登录
  type: web
  source_id: 244d5b6d8bc64535b9ef1ec72974e88c
  input_datas:
    - name: 手机号
      value: '{{手机号}}'        # ✅ 引用 Task 1 的 name
    - name: 登录密码
      value: '{{登录密码}}'      # ✅ 引用 Task 1 的 name
```

**反例（必须避免）**：

```yaml
# ❌ 错误：直接写死字面量，跨环境不可移植
input_datas:
  - name: 手机号
    value: '13800138001'

# ❌ 错误：环境变量已存在但没用 {{}} 引用
input_datas:
  - name: URL
    value: http://novel.hctestedu.com     # 应改为 '{{api_project_url}}'

# ❌ 错误：引用错键名（用 value 而非 name）
input_datas:
  - name: 手机号
    value: '{{phone_number}}'             # 应改为 '{{手机号}}'（因为 name=手机号）
```

#### 3. `{{变量名}}` 用在哪些字段？

| 字段 | 支持 jinja2 | 说明 |
|------|------------|------|
| 编排 task `input_datas[].value` | ✅ **必须** | runner 渲染后注入函数/用例入参 |
| 自动化用例 `case_content.request.url` | ✅ | api/web 用例 body/url 里的 `{{}}` 也会被 runner 二次渲染 |
| 自动化用例 `case_content.request.urlParams[].value` | ✅ | 同上 |
| 自动化用例 `case_content.steps[].*`（web） | ✅ | web 执行器渲染 |
| 自动化用例 `case_precondition` | ✅ | 自然语言里引用变量，便于阅读 |
| 环境变量文件 `env_var.yaml` 的 key | ❌ | key 是固定的，不用 `{{}}` 包裹 |
| 编排 task `output_datas[].name` | ❌ | name 是键名定义，不是值 |

> 渲染优先级（runner 内部）：环境变量 → 渲染 task `input_datas[].value` → 合并进 local_context → 渲染 `case_content.request` → 发起请求 / 驱动浏览器。

#### 4. YAML 写入时的引号规则（花括号陷阱）

含 `{{变量名}}` 的字符串值，**必须用单引号包裹**，否则 YAML 会把 `{` 解析为 flow mapping 起始符，导致 `yaml.safe_load()` 报错 `expected <block end>, but found '<scalar>'`：

```yaml
input_datas:
  - name: URL
    value: '{{api_project_url}}'    # ✅ 单引号
  - name: 小说名称
    value: '{{小说名称}}'            # ✅ 单引号
  - name: 备注
    value: 用户名={{手机号}}&密码={{登录密码}}   # ✅ 整串加单引号
```

> 💡 即便是纯中文/纯变量、不会与 YAML 语法冲突的简单值，也**统一加单引号**，省去排查时间。

#### 5. 引用前的快速核对清单

写完编排准备落盘前，自检：

- [ ] 凡是**会因环境/账号/数据源变化**的值，都用了 `{{变量名}}`？（账号、密码、URL、token、user_id、手机号、邮箱…）
- [ ] 引用的 `{{变量名}}` 在环境变量文件或上游 task 的 `output_datas[].name` 里**真实存在**？（不一致 = 渲染后是空串或报错）
- [ ] 引用的键名是 **`output_datas[].name`**，不是 `value`？
- [ ] 含 `{{}}` 的 value 字符串**加了单引号**？
- [ ] 写完后跑过 `python -c "import yaml; yaml.safe_load(open('xxx.yaml'))"` 验证？

### 数据流转规则

编排的核心价值是**串联 tasks 之间的数据流转**：

- 上游 task 的 `output_datas[].name` → **就是 context.json 里新增的 key**，供下游 `{{变量名}}` 引用
- 下游 task 的 `input_datas[].value` → 必须写成 `{{上游 output_datas 的 name}}`（参见上方"🔁 变量引用规范"）
- dynamic-function 类型 task 的输出由函数返回值决定（返回值 dict 的 key 与 `output_datas[].value` 对应）
- api/web 类型 task 的输出由用例的 `output_datas[].value`（JSONPath 或自然语言）经 AI 提取后写入 context.json

> 📖 已有编排参考：
> - [登录到首页再到个人中心](../../AI-自动化测试编排/8b6030cb-cdc1-47cf-b9dd-96e9726dfddc.yaml)（✅ 正确引用示例）
> - [公开课演示流程](D:/work/course/test/ai_test/AIQE/apps/shenle-test-runner/examples/AI-自动化测试编排/30e12d4e1be5438ea155139403729699.yaml)（✅ 正确引用示例）

---
