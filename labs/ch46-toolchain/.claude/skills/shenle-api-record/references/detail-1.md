## 工作流（五步，按顺序执行）

每一步都有明确的退出条件，没完成前不要跳到下一步。

### 第一步：环境检查

> **Windows 抓包的老坑（务必提前交代，别等用户踩）**
>
> 1. **`record` 静默退出**：底层调的是 `mitmweb.EXE`，不是 `python -m mitmproxy.tools.web`。后者在 Windows 上会直接退出、终端里看不到任何报错。如果用户反馈「我看到命令行闪了一下就退了」或「啥也没打印」，第一件事是看 `pip show mitmproxy` 装出来的脚本路径，确认 `mitmweb.EXE` 存在。
> 2. **HTTPS 解密需要 CA 信任**：CA 不在系统 Root 库时，所有 HTTPS 请求都会被 mitmproxy tunnel 透传、抓不到 body。CA 安装是独立的 `install-ca` 子命令，**check 不会强制要求安装成功**——`check` 全 `[INFO]` 就视为通过，需要装时由用户在需要时主动跑 `shenle-api-record install-ca`（或后续 `record` 时一并尝试）。**对于手机 / 桌面应用来说，CA 还要装在那个客户端的信任库里**（不是只装在本机就行）。

在项目根目录 `D:\Code\AIQECourse\Phase2` 下执行：

```bash
python --version
shenle-api-record --version
shenle-api-record check
```

`check` 会同时校验 Python / mitmproxy 包 / CA 文件生成状态 / certutil 可用性，并把 mitmproxy 缺失时的自动 `pip install mitmproxy` 走掉——所以一次跑就够了。

**期望结果**（实际输出格式）：

```
[INFO] Python:        3.11.x
[INFO] Platform:      win32 (Windows)
[INFO] mitmweb:       C:\...\mitmweb.EXE
[INFO] mitmproxy:     v11.x.x
[INFO] CA 证书:       C:\Users\95431\.mitmproxy\mitmproxy-ca-cert.cer (已生成)
[INFO] certutil:      OK
```

**判断标准：所有行都是 `[INFO]`，没有 `[WARN]` / `[ERROR]` → 通过，直接进第二步。**

> ⚠️ `check` **不输出** `OS trust: yes/no` 字段（早期设计有过，实际 CLI 没实现）。`install-ca` 是独立的子命令，由用户在需要时主动跑。**`check` 全部 `[INFO]` 时不要主动提示装 CA**——这是用户偏好，避免每次都打断。

**mitmproxy 缺失**（check 打印 `NOT INSTALLED` 或报 `[ERROR]`）→ 让用户跑：

```bash
pip install mitmproxy
```

或先让它自己跑一次 `shenle-api-record record` 触发自动安装，但**提醒用户第一次会自动 pip install，可能要等几十秒**。

### 第二步：确认录制目标和参数

一次问 2 个问题，**不要**自作主张挑默认值：

**Q1：要录哪个端？** 四选一，影响后续默认值：

| 目标 | CLI 默认 | 代理配置位置 | CA 信任范围 |
| --- | --- | --- | --- |
| **浏览器**（本机 Chrome / Edge） | `record`（默认开 SPA） | 系统代理 / 浏览器扩展 → `127.0.0.1:8080` | 仅本机 |
| **手机 H5**（手机自带浏览器） | `record --no-browser` | Wi-Fi 手动代理 → `<电脑 LAN IP>:8080` | 本机 + **手机上**也装 CA |
| **APP**（手机上的原生应用） | `record --no-browser` | Wi-Fi 手动代理 → `<电脑 LAN IP>:8080` | 本机 + **手机上**也装 CA |
| **桌面应用**（第三方客户端） | `record --no-browser` | 应用内网络设置 → `127.0.0.1:8080` | 本机 + **应用内**也信任 CA |

`--no-browser` 是关键：mitmweb 默认会在启动时自动打开浏览器跳到 SPA，对手机/APP/桌面应用来说这个桌面浏览器毫无意义反而干扰视线，关掉它让 SPA 在 `http://127.0.0.1:8081` 等用户自己去开即可。

**Q2：要不要过滤？**（可跳过）

只在用户主动提「只要某个域名的」「过滤掉健康检查」「只录 JSON」「按域名分文件」时追问，对应 CLI 参数：

| 用户原话 | 拼到 CLI 上的参数 |
| --- | --- |
| 「只要 `api.example.com` 的」 | `--include 'api\.example\.com'` |
| 「丢掉 `/health` 和 `/metrics`」 | `--exclude '^.*/health$' --exclude '^.*/metrics$'` |
| 「只要 API 响应（JSON / XML），不要静态资源」 | `--resource-filter api-only` |
| 「按域名分文件」 | `--auto-split-by-domain` |

**Q3：输出目录？** 默认不动（CLI 用当前目录下的 `AI-信息采集/`）。只有用户明确说「录到别的盘」才接 `--output-root`。

**Q4（可选）：要不要接着上一次那批录？** 用户说「接着上次」「同一批次」时复用上次的批次号（`AI-信息采集/<上次批次>/`），否则每次开新批次。

确认完进入第三步。

### 第三步：启动录制

从项目根目录进入 `apps/shenle-api-record/` 再执行 CLI，这样默认输出目录 `AI-信息采集/` 会落在 `apps/shenle-api-record/AI-信息采集/` 下：

```bash
cd apps/shenle-api-record
shenle-api-record record [--no-browser] [...filters...] [--output-root ...] [--batch-size 50]
```

如果用户在第二步特别要「纯静默、不要 SPA」（常见于「录完就关」），改成 `record`：

```bash
cd apps/shenle-api-record
shenle-api-record record [args...]
```

**别自作主张改 `--port` / `--web-port` / `--control-port`**。默认值（8080 / 8081 / 9090）和 README 文档、代理配置指引完全一致；改了就和用户手里的指引对不上。

**实时反馈，按阶段报**：

1. 「正在启动 mitmweb，监听 `127.0.0.1:8080`…」——子进程 spawn 中。
2. 「正在生成 / 加载 CA…」——首次启动会 bootstrap。
3. 「控制面板已就绪：`http://127.0.0.1:8081`」——SPA 起来了（`record` 才说，`record` 不说）。
4. 「录制进行中」——CLI 挂着等用户结束。

会话是**交互式**的，CLI 会一直跑直到：

- 用户在终端按 `Ctrl+C`，**或**
- `record` 用户在 SPA 上点 Stop 按钮（Phase 3 引入，Windows 上 `done()` 回调不可靠，必须配 `.flush_sentinel` 文件兜底——这是 CLI 内部已经处理好的，skill 不需要管）。

**不要**自己加超时，**不要**替用户按终止。让用户掌控录制节奏。

### 第四步：指导用户配置代理

这一步**紧跟第三步**，CLI 已经在监听 8080 了，现在教用户把客户端指过去。**不要**让用户先停 CLI 再去配——配完才能产生流量。

按第二步的目标分支给指引：

#### A. 浏览器（本机 Chrome / Edge / Firefox）

```
1. 系统设置 → 网络和 Internet → 代理 → 手动设置代理 → 打开
2. 地址：127.0.0.1    端口：8080
3. （或装一个 SwitchyOmega 扩展，配置 SOCKS5/HTTP 代理 127.0.0.1:8080，更省事）
4. 浏览器打开 mitmweb SPA：http://127.0.0.1:8081/
5. 用完关浏览器 + 关 SPA 上的 Stop 按钮（或终端 Ctrl+C）
```

HTTPS 不需要额外装 CA——第一步已经在本机信任过了。

#### B. 手机 H5 / APP

> **首先**：手机和电脑必须在**同一个 WiFi**（同一个路由器、同一个网段）。

电脑的 LAN IP 拿法（Windows）：

```bash
python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0])"
```

或 `ipconfig` 找 `IPv4 Address`，挑 Wi-Fi 适配器那块的那一个。

拿到 IP（假设是 `192.168.1.42`），给用户：

```
手机侧：
1. 设置 → Wi-Fi → 当前网络 → 高级 / 代理 → 手动
2. 主机名：192.168.1.42    端口：8080
3. 浏览器（仅 H5）打开 http://mitm.it 下载 CA 并安装
   APP：把电脑 mitmproxy-ca-cert.pem 拷到手机（AirDrop / U 盘 / 邮件都行）
       设置 → 密码与安全 / 安全 → 安装证书 → CA 证书 → 选刚才那个文件
4. （仅 APP）iOS 还需要「设置 → 通用 → 关于本机 → 证书信任设置 → 启用 mitmproxy」
   Android 7+ 默认不信任用户安装的 CA，要绕：
       - app/src/main/res/xml/network_security_config.xml 加：
         <base-config><trust-anchors><certificates src="user"/></trust-anchors></base-config>
       - 或把目标 APP 反编译、把 CA 塞进系统信任库（需要 root）
   这两步都不是 skill 能帮你做的，绕不过就改用「H5 入口」或换抓包工具。
5. 全部设好之后再操作 APP / H5，请求才会被 mitmproxy 抓到
```

电脑侧：`shenle-api-record` CLI 一直挂着，会实时把抓到的请求写到 `apps/shenle-api-record/AI-信息采集/<批次>/rawNN.json`。

#### C. 桌面应用

```
1. 打开应用 → 设置 / Preferences / 网络 / Connection / Proxy
2. HTTP Proxy：127.0.0.1:8080
3. HTTPS Proxy：127.0.0.1:8080（如果有这一项）
4. CA：很多桌面客户端（如 Postman 老版、Java swing 应用）会自带 CA 库，
   手动导 mitmproxy-ca-cert.pem 进去。Electron / .NET 通常走系统信任库，
   只要第一步在本机装好 CA 就行。
5. 操作应用，请求落到 rawNN.json
```

### 第五步：取摘要、返回结果、下游交接

用户按 `Ctrl+C` / 关 SPA / 点 Stop 之后，**只用 `apps/shenle-api-record/skill/shenle-api-record/scripts/inspect_recording.py` 取摘要**，**不要**用 Read 直接打开 `rawNN.json`——单个文件可能几百 KB 到几 MB，AI 没必要看 body。

> CLI 没有 `inspect` 子命令；用 inspect 脚本代替（脚本只解析 request/response 结构、不读完整 body）。

```bash
# 从项目根目录跑（路径相对仓库根）
python apps/shenle-api-record/skill/shenle-api-record/scripts/inspect_recording.py \
  apps/shenle-api-record/AI-信息采集/<批次号>

# 想看每个文件的逐条 URL 时：
python apps/shenle-api-record/skill/shenle-api-record/scripts/inspect_recording.py \
  apps/shenle-api-record/AI-信息采集/<批次号> --details
```

脚本输出（节选）：

```
=== raw01.json (42.3 KB) ===
  records:   12
  by method:  GET=8, POST=4
  by status:  200=11, 500=1
    [GET  200] https://example.com/api/users
    [POST 200] https://example.com/api/login
    ...

=== Summary ===
  files:          1
  total records:  12
  by method:      GET=8, POST=4
  by status:      200=11, 500=1
```

把脚本输出整理给用户：

- **批次号**：`YYYYMMDD-HHmmss`（CLI 启动时生成的一次性时间戳）
- **输出目录**：`apps/shenle-api-record/AI-信息采集/<批次号>/`
  - 开了 `--auto-split-by-domain` 时是 `…/<批次号>/by-domain/<host>/rawNN.json`
- **接口总数**：from `Summary.total records`
- **按方法 / 状态分布**：from `Summary.by method` / `Summary.by status`
- **结构提示**：每一组原始文件都按 `<batch-size>` 条切一个 `rawNN.json`；想看具体 URL 再跑 `--details`。

**关键约束**：除非用户明确说「打开 `rawNN.json` 看看 body」，否则**不要**主动 Read 任何 `rawNN.json`。下游 pipeline 也是基于 inspect 脚本摘要工作的，body 是给后续 AI / 文档生成器自己读的。

最后用一句自然的收尾，把后续步骤交给用户决定（**不要**自作主张去分析）：

> 录制完成！批次号 `<批次号>`，共抓到 **N 个接口**（`GET=A, POST=B` …）。已保存到 `apps/shenle-api-record/AI-信息采集/<批次号>/`。
>
> 下一步可以做的：
> - 让我**继续追加录制**（同样的目标，重跑一次会开新批次；想续同一批次手动复用 `--output-root`）
> - 让我**生成接口文档**（基于 inspect 脚本摘要 + `rawNN.json` 的 request/response 结构）
> - 让我**生成测试用例**（同上，配合你给的测试范围）
> - 你自己再跑一次 `inspect_recording.py … --details` 翻 URL
>
> 要走哪条路？
