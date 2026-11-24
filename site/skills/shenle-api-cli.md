---
title: shenle-api-cli
---

# shenle-api-cli

> 用 shenle-api-cli 替代 curl 跑接口任务（AIQE 测试计划）。触发词：「调这个接口」「跑 API 用例」「shenle-api-cli send」「shenle-api-cli call」「不要再用 curl」「接口调用」。0.2 推荐用 `call`（send+extract 一步到位，避免 Windows cmd.exe / bash 跨平台 shell 兼容问题）。

正文 224 行，随包 references 1 个。

读完想直接用：[下载 zip（SKILL.md+references）](/skills/shenle-api-cli.zip)　·　看说明与评分：[Skills 手册 · shenle-api-cli](/kb/skills/shenle-api-cli)

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

`.env` 配置（仅 `extract --field "&lt;中文&gt;"` 自然语言模式 + `assert` 需要；纯 JSONPath 模式不读）：
```bash
API_AUTOMATION_AI_API_KEY=sk-xxx
API_AUTOMATION_AI_BASE_URL=http://your-llm-gateway/v1
API_AUTOMATION_AI_MODEL=your-model-name
```

`.env` 在 CWD 下；改完直接生效，无需重启任何 daemon。

## 核心命令

```
shenle-api-cli call &lt;req.json&gt; --field "$.data.token"            # 【0.2 推荐】send + extract 一步到位
shenle-api-cli call &lt;req.json&gt; --field "返回的 token" --name 登录Token  # NL 抽取（需 AI 配置）
shenle-api-cli send &lt;req.json&gt;                                   # 只发，落盘 result
shenle-api-cli extract &lt;result.json&gt; --field "$.data.token"      # 从 result 文件抽
shenle-api-cli assert &lt;result.json&gt; "响应状态码是 200 且 data.token 存在"  # 自然语言断言
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
shenle-api-cli call - --field "$.data.token" &lt; req.json
cat req.json | shenle-api-cli call - --field "$.data.token"

# cmd.exe
type req.json | shenle-api-cli call - --field "$.data.token"
```

或者用 here-doc（避免管道）：
```bash
shenle-api-cli call - --field "$.data.token" &lt;&lt; 'EOF'
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

字段全部可选；`desc` 字段被忽略。runner 已把 `&#123;&#123;xxx}}` 渲染成字面值，工具不做 jinja2。

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

- **`&#123;&#123;xxx}}` 不会再被替换**：runner 已经在送进 spec 之前渲染好了；工具看到的全是字面值
- **中文路径 / 中文 value 全 OK**：用 `requests` 不用 curl，无引号转义问题
- **二进制下载不支持**（0.2 再扩）：response body &gt; 10MB 自动截断；Content-Type 非文本直接 `[FAIL]`
- **multipart 文件上传不支持**（0.2 再扩）：bodyParams 全当文本
- **4xx/5xx 默认抛 `[FAIL]`**：可用 `send --no-fail-on-status` 关闭（仍落盘，返回 0）

## 输出格式

- `send` → `[OK] send: &lt;status&gt; &lt;METHOD&gt; &lt;url&gt; elapsed=&lt;N&gt;ms result_file=&lt;path&gt;`
- `extract` → `[OK] extract: name=&lt;字段&gt; value=&lt;值&gt;` 或 `[OK] extract: name=... value=null (JSONPath 未匹配)`
- `call` → `[OK] call: status=&lt;status&gt; method=&lt;METHOD&gt; elapsed=&lt;N&gt;ms name=&lt;字段&gt; value=&lt;值&gt; result_file=&lt;path&gt;`（0.2 推荐用这个）
- `assert` → `[OK] assert: passed=true reason=...` 或 `[FAIL] assert: ...`
- 任何命令失败 → `[FAIL] &lt;cmd&gt;: &lt;msg&gt;`，exit 1/2（1=业务错，2=内部异常）

## 常见问题

| 报错 | 原因 | 修复 |
|------|------|------|
| `[FAIL] send: 请求文件格式错误：JSON 解析失败：Unexpected UTF-8 BOM` | req.json 被 PowerShell 写成带 BOM 的 UTF-8 | 用 `Set-Content -Encoding utf8NoBOM`，或让 Python 用 `open(..., encoding='utf-8')` 写 |
| `[FAIL] send: 网络请求失败：...` | DNS / 连接 / 读取超时 | 检查 URL 是否通；调大 `--timeout` |
| `[FAIL] send: HTTP 404 ...` | 接口本身 4xx/5xx | 加 `--no-fail-on-status` 或修接口 |
| `[FAIL] extract: 不支持的 JSONPath 语法` | 用了 `$..` / `$.*` / filter | 改用自然语言：`extract --field "返回的 X"` |
| `[FAIL] extract: response body 不是合法 JSON` | Content-Type 不是 JSON，但用了 JSONPath | 改用自然语言提取 |
| `[FAIL] assert: AI 配置缺失：...` | `.env` 没配 3 个 env | 补 `API_AUTOMATION_AI_*` |
| `[FAIL] &lt;cmd&gt;: 内部错误：...` | 工具 bug | 加 `--debug` 重试看堆栈 |

## 关联

- 浏览器自动化同类 → [shenle-web-cli](../../../../apps/shenle-web-cli)
- 真实 HTTP 录制（mitmproxy） → [shenle-api-record](../../../../apps/shenle-api-record)
- AIQE 测试计划执行器 → [shenle-ai-test-runner](../../../../shenle-test-runner/04-apps/shenle-ai-test-runner6.0)

## 执行顺序

1. 先确认请求 JSON：`url` 必填，`method` 缺省 GET，`headers` / `urlParams` / `bodyParams` 都是 `[{name, value}]`。
2. 首选一条 `call`：`shenle-api-cli call req.json --field "$.data.token"`，send 与取值一次完成。
3. 只有需要把 `result_file` 交给后续任务时，才拆成 `send` + `extract` 两步。
4. JSONPath 判不出来（`$..`、filter、非 JSON body）时改用 `--field "返回的 X"` 走自然语言，或直接读 result 文件。
5. 断言优先写成可判定的 JSONPath/状态码；自然语言 `assert` 只做兜底复核。

## 判断与选择

| 场景 | 用哪个 | 为什么 |
| --- | --- | --- |
| 常规调接口、取一个字段 | `call` | 一条命令、无管道无赋值，Windows cmd 里也不会挂 |
| 需要结果文件给下一步 | `send` 再 `extract` | 中间产物落盘，后续步骤可以复用 |
| 4xx 也要取值 | 加 `--no-fail-on-status` | 默认 4xx/5xx 会 `[FAIL]` 退出，加了才继续落盘 |
| 响应不是 JSON | `--field "中文描述"` 或直接看 result | JSONPath 只对 JSON 有效 |
| 要断言业务语义 | 状态码/字段先断言，语义再兜底 | 可判定优先，模糊结论放最后 |

## 反模式

- **NEVER** 用 `result_file=$(...)` 接输出 —— 因为 Bash 工具在 Windows 上走 `cmd /c`，这种赋值语法直接失败。
- **NEVER** 依赖 `&#123;&#123;xxx}}` 在工具里再渲染 —— 因为 runner 送进来之前已经渲染完，工具只认字面值。
- **NEVER** 用 `extract --field "$..id"` 这类递归语法 —— 因为工具只支持点号路径与数组下标，会 `[FAIL]`。
- **NEVER** 为了省一步把 token 硬编码进 req.json —— 因为泄露进 git 历史就洗不掉，用 `--field` 现场取。
- **NEVER** 只看 `[OK]` 就当断言通过 —— 因为 `[OK]` 只说明请求发出去了，状态码与字段要另行断言。

## 失败兜底

- 网络失败（`网络请求失败`）：先 `ping`/`curl` 同 URL 确认可达，再调大 `--timeout`；仍失败就换内网地址。
- 4xx/5xx：加 `--no-fail-on-status` 落盘，读 result 里的原始报文定位，不要盲改请求。
- JSONPath 不匹配（`value=null`）：改自然语言抽取，或先 `--debug` 看完整 body。
- 需要 AI 的 `assert` 报配置缺失：检查 `.env` 里三个 `API_AUTOMATION_AI_*`，缺哪个补哪个。
- 以上都不行：直接用 `python -c` + `requests` 兜底复现一次，再回来判断是工具 bug 还是接口问题。

## 速查表在 references 里

MANDATORY：动手前先读 `references/quick-reference.md`，那里是高频命令与对照表；正文只讲判断与避坑，不重复贴命令清单。

