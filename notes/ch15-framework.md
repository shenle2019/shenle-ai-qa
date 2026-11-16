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

- **编码**：Excel 默认 GBK，读的时候要 `encoding="utf-8-sig"` 兜住 BOM；
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

## 7. 本章实验

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
