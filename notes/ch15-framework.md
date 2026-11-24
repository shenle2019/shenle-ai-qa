# 第 15 章 · 收口：一个能交给别人的框架

前七章是零件，这一章把它们装成一台机器：**别人 clone 下来，改一行配置就能跑**。

## 1. 目录

```
labs/ch15-framework/
├── config.py        环境与开关（local / staging / ci）
├── client.py        HttpClient（超时、重试、日志、异常）
├── api.py           Users / Orders / Files 三个语义对象
├── data/            用例数据（CSV）
├── run.py           CLI：选环境、选标记、出报告
├── tests/           用例
└── README.md        三行命令
```

判断结构好不好，还是那个问题：**换环境要改几个文件？** 答案是零——只改 `--env`。

## 2. 配置要能被覆盖

```python
@dataclass
class Settings:
    name: str
    base_url: str
    timeout: float = 5.0
    retries: int = 1

ENVS = {
    "local": Settings("local", "http://127.0.0.1:8000"),
    "staging": Settings("staging", "https://staging.example.com", retries=2),
}
```

优先级：**命令行 > 环境变量 > 默认**。CI 里用环境变量注入，本地用 `--env`。

## 3. 上传下载：两个必测点

```python
files = {"file": ("a.txt", b"hello", "text/plain")}
resp = client.post("/api/upload", files=files)
```

必测的不是「能传」，而是：

1. **非 multipart 被拒**（415）；
2. **下载回来的字节与上传一致**（`resp.content == payload`）。

## 4. 批量导入导出

CSV 是测试数据最常见的载体。两个坑：

- **编码**：中文 Windows 上 Excel 另存的 CSV 常是 GBK，读时用 `encoding="gbk"`；只有「CSV UTF-8」导出才带 BOM，那才用 `utf-8-sig` 去 BOM；
- **部分成功**：批量接口通常「成功 N 条、失败 M 条」，断言要看两类计数，不是只看整体 200。

## 5. CI 要跑什么

```yaml
- run: pytest labs/ch15-framework -q -m "not slow" --junitxml=report.xml
- run: python labs/ch14-report-assert/report.py report.xml report.html
- uses: actions/upload-artifact@v4
  with: { name: report, path: report.html }
```

三条原则：**只跑不依赖外网的用例**、**报告必须留档**、**失败要能一眼看出哪条**。

## 6. 怎么判断「框架成了」

- 新人 10 分钟能跑起来（README 三行命令）；
- 加一个接口只动 `api.py` + 一个 test 文件；
- 换环境只改 `--env`；
- 失败信息里有状态码、响应体、期望值；
- CI 上跑得比本地慢不超过 2 倍。

## 7. 本章实操

`labs/ch15-framework/`：

- `config.py` + `client.py` + `api.py` + `run.py`；
- `tests/test_users.py`、`tests/test_files.py`、`tests/test_batch.py`；
- `data/users.csv`。

```powershell
.venv\Scripts\python.exe -m pytest labs\ch15-framework -q
.venv\Scripts\python.exe labs\ch15-framework\run.py --env local --report
```

## 8. 自测

1. 配置优先级为什么是「命令行 > 环境变量 > 默认」？
2. 上传接口只测「能传成功」，会漏掉哪两类 bug？
3. 批量导入的「部分成功」，断言应该看什么？
4. CI 为什么不该跑依赖外网的用例？
5. 你现在的项目，换环境要改几个文件？

## 附：自测答案

1. 越靠近「这次运行」的配置越该优先：命令行 > 环境变量 > 文件默认。这样 CI 和本地临时覆盖不用改文件，也不会把本地改动提交上去。
2. 漏两类：文件本身的限制（类型白名单、大小上限、空文件、超长文件名）和内容安全（路径穿越 `../`、可执行后缀、同名覆盖）。只测「能传成功」等于没测上传。
3. 看「成功条数 + 失败条数 + 每条失败的行号和原因」，以及幂等性（同一批数据重复导入不会重复插入）。
4. 外网不稳定会导致随机失败，外网服务会变更、会限流，还可能涉及密钥；CI 必须可重复、可离线、可并行。
5. 理想是 0 个：只改 `--env` 或环境变量。如果还要改代码，说明域名、账号、超时这些还没抽到配置里。

## 学生常问

**Q：框架要写到多完整才算「能交付」？**

A：别人 clone 下来，按 README 三条命令能跑通；换环境只改配置；失败能定位到接口和字段；能出报告。做到这四点就够交付，剩下的都是锦上添花。

**Q：用例要不要和框架放一个仓库？**

A：小团队放一起最省事；多项目共用框架时，把框架发成内部包、用例仓库依赖它。分不分看「改动频率是否一致」。

**Q：CI 里跑多久算合理？**

A：提交级 smoke 控制在 3–5 分钟；全量放夜间。超过 10 分钟的 PR 检查，大家就会开始绕过它。

## 面试题

**Q：从零搭一个接口自动化框架，你的步骤？**

A：先定目录与分层（config/client/api/cases）；做客户端封装（重试、日志、异常）；接第一个业务域验证通路；补测试数据工厂与清理；接 pytest 组织与标记；接报告与 CI；最后写 README 和运行脚本。顺序反过来（先写用例再补封装）会返工。

**Q：框架怎么支持多环境？**

A：配置文件按环境分（local/test/prod），`--env` 选择，环境变量覆盖敏感项（域名、账号、密钥不入库）；断言不写死环境相关值。

**Q：怎么让框架对新人友好？**

A：README 给三条命令；用例命名统一；加一个新接口只要写一个 api 类 + 一个用例文件；错误信息里带请求/响应片段；有 `make demo` 之类的一键跑通示例。

## 延伸知识

- 配置里永远不要提交密钥，用 `.env` + 环境变量，仓库里只放 `.env.example`。
- 上传下载用例要准备小样本文件（几 KB），别把大文件塞进仓库。
- 批量导入要测「部分成功」：合法行入库、非法行报错并给行号，接口返回 207 或 200 + 明细。
- 框架的入口脚本（`run.py`）只做三件事：解析参数、装配、调用 pytest；不要把业务逻辑塞进去。
