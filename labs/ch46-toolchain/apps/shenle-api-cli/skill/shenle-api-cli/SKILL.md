---
name: shenle-api-cli
description: 用 shenle-api-cli 替代 curl 跑接口任务（AIQE 测试计划）。触发词：「调这个接口」「跑 API 用例」「shenle-api-cli send」「shenle-api-cli call」「不要再用 curl」「接口调用」。0.2 推荐用 `call`（send+extract 一步到位，避免 Windows cmd.exe / bash 跨平台 shell 兼容问题）。
---

# shenle-api-cli

## 触发词
- "用 shenle-api-cli 跑这个接口"
- "调一下登录接口"
- "不要再用 curl"
- "AIQE api task 执行"
- "extract 这个 result 文件的 token"
- "断言响应是 200"

## 前置

工具直接装好（项目根下）：
```bash
.venv/Scripts/python.exe -m pip install -e apps/shenle-api-cli
shenle-api-cli --version    # 应输出 shenle-api-cli 0.1.0
```

`.env` 配置（仅 `extract --field "<中文>"` 自然语言模式 + `assert` 需要；纯 JSONPath 模式不读）：
```bash
API_AUTOMATION_AI_API_KEY=sk-xxx
API_AUTOMATION_AI_BASE_URL=http://your-llm-gateway/v1
API_AUTOMATION_AI_MODEL=your-model-name
```

`.env` 在 CWD 下；改完直接生效，无需重启任何 daemon。

## 核心命令

```
shenle-api-cli call <req.json> --field "$.data.token"            # 【0.2 推荐】send + extract 一步到位
shenle-api-cli call <req.json> --field "返回的 token" --name 登录Token  # NL 抽取（需 AI 配置）
shenle-api-cli send <req.json>                                   # 只发，落盘 result
shenle-api-cli extract <result.json> --field "$.data.token"      # 从 result 文件抽
shenle-api-cli assert <result.json> "响应状态码是 200 且 data.token 存在"  # 自然语言断言
```

## 调用模式（AI 直接照抄）

### ⚠️ 重要：Windows 上 Bash 工具走 cmd.exe

agentscope 的 Bash 工具在 Windows 上**强制用 `cmd /c`**，不是 bash。所以：
- ❌ `result_file=$(...)` / `grep -oP` / 单引号赋值 → **全部会失败**
- ❌ `\|` 管道部分能用，但和 bash 语义有差异
- ✅ **推荐用 `call` 一条命令搞定 send + extract**（无管道、无赋值）
- ✅ 单条命令（如 `shenle-api-cli extract "C:\Users\..."`）也能跑，但路径里**别用单引号**

### 1. 【首选】用 `call` 一步到位

```bash
shenle-api-cli call req.json --field "$.data.token"
# 输出：[OK] call: status=200 method=POST elapsed=110ms name=value value=eyJhbGciOiJIUzUxMiJ9... result_file=C:\...\shenle-api-results\xxx.json

shenle-api-cli call req.json --field "$.data.token" --name "登录Token"
# 输出同上，但 name=登录Token（便于人读 + 业务命名）
```

测试**失败响应**（4xx 但 body 是 JSON）：
```bash
shenle-api-cli call req_fail.json --field "$.msg" --no-fail-on-status
# 加 --no-fail-on-status 避免非 200 抛错（仍落盘 + 抽取字段）
```

### 1.5. 【备选】从 stdin 喂 JSON（避开文件路径问题）

如果不确定文件路径在哪，或者文件已经在 stdin 流里（比如刚 Write 出来）：
```bash
# bash
shenle-api-cli call - --field "$.data.token" < req.json
cat req.json | shenle-api-cli call - --field "$.data.token"

# cmd.exe
type req.json | shenle-api-cli call - --field "$.data.token"
```

或者用 here-doc（避免管道）：
```bash
shenle-api-cli call - --field "$.data.token" << 'EOF'
{"url":"http://...","method":"POST",...}
EOF
```

### 2. 读 case.yaml → 构造 req.json → call

case.yaml 里 `case_content.request` 的结构（runner 渲染后）就是 shenle-api-cli 的输入格式：
- `headers`: `[{name, value, ...}]` → 变成 dict
- `urlParams`: `[{name, value, ...}]` → 拼到 url 的 ? 后
- `bodyParams`: `[{name, value, ...}]` → 根据 content-type 走 form / json

**注意 req.json 路径要用绝对路径**（Write 工具要求 file_path 是绝对路径）：

```bash
# 推荐：绝对路径
shenle-api-cli call "D:/Code/.../req.json" --field "$.data.token"

# 不推荐：相对路径在 agentscope Write 工具里会失败
shenle-api-cli call req.json --field "$.data.token"   # ❌ req.json 是相对路径
```

### 3. 【备用】send + extract 分两步（仅当需要 result_file 给后续任务用）

```bash
shenle-api-cli send req.json
# 输出：[OK] send: 200 POST http://... elapsed=110ms result_file=C:\...\xxx.json

# 手动从输出里抠 result_file，或用 dir 列 temp 目录找最新的：
shenle-api-cli extract "C:\Users\...\xxx.json" --field "$.data.token"
```

### 4. 自然语言断言（仅在 JSONPath 判不出来时用）

```bash
shenle-api-cli assert "C:\Users\...\xxx.json" "响应状态码是 200 且 data.msg 等于 SUCCESS"
```

## 数据契约

### 请求 JSON（req.json / stdin）

```json
{
  "url": "https://example.com/user/login",
  "method": "POST",
  "headers": [
    {"name": "content-type", "value": "application/x-www-form-urlencoded"}
  ],
  "urlParams": [{"name": "trace_id", "value": "abc"}],
  "bodyParams": [{"name": "username", "value": "15096268001"}]
}
```

字段全部可选；`desc` 字段被忽略。runner 已把 `{{xxx}}` 渲染成字面值，工具不做 jinja2。

### 结果 JSON（result.json 写到 %TEMP%/shenle-api-results/）

```json
{
  "request": { ...原样回写... },
  "response": {
    "url": "...", "status": 200, "status_text": "OK",
    "headers": {"content-type": "application/json"},
    "body_text": "...", "body_json": {...},
    "elapsed_ms": 234, "called_at": "2026-09-24T22:14:30.123+08:00"
  },
  "meta": {"tool_version": "0.1.0", "cli_cmd": "...", "size_bytes": 1234}
}
```

## 注意事项

- **`{{xxx}}` 不会再被替换**：runner 已经在送进 spec 之前渲染好了；工具看到的全是字面值
- **中文路径 / 中文 value 全 OK**：用 `requests` 不用 curl，无引号转义问题
- **二进制下载不支持**（0.2 再扩）：response body > 10MB 自动截断；Content-Type 非文本直接 `[FAIL]`
- **multipart 文件上传不支持**（0.2 再扩）：bodyParams 全当文本
- **4xx/5xx 默认抛 `[FAIL]`**：可用 `send --no-fail-on-status` 关闭（仍落盘，返回 0）

## 输出格式

- `send` → `[OK] send: <status> <METHOD> <url> elapsed=<N>ms result_file=<path>`
- `extract` → `[OK] extract: name=<字段> value=<值>` 或 `[OK] extract: name=... value=null (JSONPath 未匹配)`
- `call` → `[OK] call: status=<status> method=<METHOD> elapsed=<N>ms name=<字段> value=<值> result_file=<path>`（0.2 推荐用这个）
- `assert` → `[OK] assert: passed=true reason=...` 或 `[FAIL] assert: ...`
- 任何命令失败 → `[FAIL] <cmd>: <msg>`，exit 1/2（1=业务错，2=内部异常）

## 常见问题

| 报错 | 原因 | 修复 |
|------|------|------|
| `[FAIL] send: 网络请求失败：...` | DNS / 连接 / 读取超时 | 检查 URL 是否通；调大 `--timeout` |
| `[FAIL] send: HTTP 404 ...` | 接口本身 4xx/5xx | 加 `--no-fail-on-status` 或修接口 |
| `[FAIL] extract: 不支持的 JSONPath 语法` | 用了 `$..` / `$.*` / filter | 改用自然语言：`extract --field "返回的 X"` |
| `[FAIL] extract: response body 不是合法 JSON` | Content-Type 不是 JSON，但用了 JSONPath | 改用自然语言提取 |
| `[FAIL] assert: AI 配置缺失：...` | `.env` 没配 3 个 env | 补 `API_AUTOMATION_AI_*` |
| `[FAIL] <cmd>: 内部错误：...` | 工具 bug | 加 `--debug` 重试看堆栈 |

## 关联

- 浏览器自动化同类 → [shenle-web-cli](../../../../apps/shenle-web-cli)
- 真实 HTTP 录制（mitmproxy） → [shenle-api-record](../../../../apps/shenle-api-record)
- AIQE 测试计划执行器 → [shenle-ai-test-runner](../../../../shenle-test-runner/04-apps/shenle-ai-test-runner6.0)
