# shenle-api-cli

命令行驱动的接口调用工具（`requests` + `python-dotenv`），替代 `curl` 给 AI 跑 API 任务。

- **解决痛点**：`shenle-ai-test-runner 6.0` 当前让 Agent 通过 Bash 调 `curl`，在中文路径/特殊字符场景下引号转义、编码、stdout 解析都不稳定
- **统一行为**：每个调用 `request + response` 自动落盘到 `%TEMP%/shenle-api-results/`，后续 `extract` / `assert` 直接复用
- **混合提取**：JSONPath（`$.data.token`）走本地；自然语言（`"登录返回的 token"`）自动走 AI

## 与 `shenle-web-cli` 的关系

| 工具 | 适用场景 | 驱动方式 |
|------|----------|----------|
| `shenle-web-cli` | Web 自动化用例 | Playwright + CDP，AI 视觉定位 |
| `shenle-api-cli`（本工具） | **API 自动化用例** | `requests`，JSONPath + AI |
| `shenle-api-record` | 录制真实 HTTP 流量 | mitmproxy 系统代理 |

## 安装

工程根目录的 `.venv` 已经装了 `requests` 和 `python-dotenv`。新工具以可编辑模式装进同一个 venv：

```bash
.venv/Scripts/python.exe -m pip install -e apps/shenle-api-cli
```

激活 venv 后就能全局敲 `shenle-api-cli`：

```bash
shenle-api-cli --version
shenle-api-cli --help
```

## 用法

### 单次接口调用（send）

请求 JSON 文件（字段顺序无关，`desc` 被忽略）：
```json
{
  "url": "https://example.com/user/login",
  "method": "POST",
  "headers": [
    {"name": "content-type", "value": "application/x-www-form-urlencoded"},
    {"name": "x-requested-with", "value": "XMLHttpRequest"}
  ],
  "urlParams": [{"name": "trace_id", "value": "abc123"}],
  "bodyParams": [
    {"name": "username", "value": "15096268001"},
    {"name": "password", "value": "123456"}
  ]
}
```

```bash
shenle-api-cli send req.json
# [OK] send: 200 POST https://example.com/user/login?trace_id=abc123 elapsed=234ms result_file=C:\Users\...\Temp\shenle-api-results\20260924-221430-643b6e89.json
```

也支持 stdin：
```bash
cat req.json | shenle-api-cli send -
```

### 变量提取（extract）

```bash
# JSONPath（纯本地，无 AI 调用）
shenle-api-cli extract <result.json> --field "$.data.token"
# [OK] extract: name=$.data.token value=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 自然语言（自动走 AI）
shenle-api-cli extract <result.json> --field "登录返回的 token"
# [OK] extract: name=token value=eyJ...

# 不存在的路径
shenle-api-cli extract <result.json> --field "$.does.not.exist"
# [OK] extract: name=$.does.not.exist value=null (JSONPath 未匹配)
```

**判断规则**：field 以 `$` 开头 → JSONPath；否则 → AI 自然语言。

### 业务断言（assert）

```bash
shenle-api-cli assert <result.json> "响应状态码是 200 且 data.msg 等于 SUCCESS"
# [OK] assert: passed=true reason=状态码 200，msg 包含 SUCCESS
```

断言不通过 → `[FAIL] assert: passed=false reason=...` + exit 1。

### 进阶参数

```bash
shenle-api-cli send req.json --timeout 60 --no-verify-ssl --no-fail-on-status -o ./my-results/
shenle-api-cli extract <result.json> --field "$.data.user[0].name" --name "用户姓名"
shenle-api-cli --debug extract <result.json> --field "$.x"   # 内部异常打印完整堆栈
```

## AI 配置

`extract --field "<中文>"` 和 `assert` 需要在当前目录的 `.env` 里配置：

```bash
API_AUTOMATION_AI_API_KEY=sk-xxx
API_AUTOMATION_AI_BASE_URL=http://your-llm-gateway/v1
API_AUTOMATION_AI_MODEL=your-model-name
```

- 真实环境变量优先于 `.env`（与 `shenle-web-cli` 同款）
- 改完 `.env` 直接再跑命令即可生效，无需重启
- 缺配置时**立刻 `[FAIL]`**，不重试
- 纯 JSONPath 模式不读 AI 配置

## 与 shenle-ai-test-runner 集成

`shenle-ai-test-runner 6.0` 默认让 Agent 通过 Bash 调 `curl` 跑 API 任务。想切换到 shenle-api-cli：

```bash
shenle-ai-test-runner run \
  --project-dir "D:\Code\AIQECourse\Phase2\示例项目-读书屋" \
  --plan-id "plan-web-20260921-224910-登录并修改用户昵称（接口版）" \
  --skills-dir "apps/shenle-api-cli/skill" \
  --system-prompt "当用户执行的时候 task 类型是 api 则，结合 shenle-api-cli 进行执行"
```

Agent 通过 SKILL.md 学到用法，自然从 `curl` 切到 `shenle-api-cli send/extract/assert`。

### 推荐给 AI 的串联模式

```bash
# 1. 发请求
result_file=$(shenle-api-cli send req.json | grep -oP 'result_file=\K\S+')
# 2. 抽 token（JSONPath 走本地，速度快）
token=$(shenle-api-cli extract "$result_file" --field "$.data.token" | grep -oP 'value=\K.*')
# 3. 喂给 runner 的 flow.context
echo "VAR 登录Token=$token"
# 4. 业务断言（必要时走 AI）
shenle-api-cli assert "$result_file" "data.msg 等于 SUCCESS"
```

## 结果文件位置与命名

- 默认目录：`<系统 tempdir>/shenle-api-results/`
  - Windows：`C:\Users\<user>\AppData\Local\Temp\shenle-api-results\`
  - Linux/macOS：`/tmp/shenle-api-results/`
- 文件名：`<YYYYMMDD-HHmmss>-<uuid4 前 8 位>.json`
- 目录不存在会自动 `mkdir -p`
- 可用 `send --output-dir <DIR>` 改（每个 run 单独存）

## Project layout

```
apps/shenle-api-cli/
├── pyproject.toml             # 包定义，console_scripts 注册 shenle-api-cli
├── README.md
├── .env.example
├── .gitignore
└── src/
    └── shenle_api_cli/
        ├── __init__.py        # 版本号 0.1.0
        ├── cli.py             # argparse 入口 + 统一异常处理
        ├── commands.py        # cmd_send / cmd_extract / cmd_assert
        ├── errors.py          # CliError 基类 + 子类
        ├── http_client.py     # requests.Session + ResponseData
        ├── jsonpath.py        # 极简 $.a.b[0].c walker
        ├── request_builder.py # case.request dict → requests 参数
        ├── ai.py              # AI 配置 + chat/completions
        └── result_store.py    # 落盘到 %TEMP%/shenle-api-results/
```

## 关联

- 浏览器自动化 → [`shenle-web-cli`](../shenle-web-cli)
- 接口录制（mitmproxy） → [`shenle-api-record`](../shenle-api-record)
- AIQE 测试计划执行器 → [`shenle-ai-test-runner`](../../shenle-test-runner/04-apps/shenle-ai-test-runner6.0)
