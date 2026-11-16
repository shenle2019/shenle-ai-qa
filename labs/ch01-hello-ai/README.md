# ch01 · 第一个 AI 生成程序

第 1 章的三个可运行实验，对应笔记里的「环境 → 变量 → 输入输出 → AI 协作」。

## 跑起来

```powershell
cd labs/ch01-hello-ai
python hello.py                       # 1. 最小程序：变量 + print
python score.py                       # 2. 课程项目：交互动手输入
python score.py --name 李明 --scores 85 92 78   #    非交互，便于自测
python ai_generate.py                 # 3. AI 生成：无 key 走 mock，有 key 真调用
python generated/hello_ai.py          #    跑一遍刚生成的代码
```

`python run.ps1` 会按顺序把它们跑一遍并打印结果。

## 文件

| 文件 | 作用 |
| --- | --- |
| `hello.py` | 最小可运行程序：变量、`print` 多值 |
| `score.py` | 课程项目：姓名 + 三门成绩 → 总分/平均分/是否及格/最弱科目 |
| `ai_generate.py` | 四步法的第 2 步：读 `prompts/ch01.txt`，调 OpenAI 兼容接口，把代码落盘 |
| `prompts/ch01.txt` | 提示词模板，可直接改成自己的需求 |
| `errors/a_types.py` | 课件原例：四种类型 + `input()` 转 `float` |
| `errors/b_indent.py` | 课件原例：缩进规则 |
| `generated/` | `ai_generate.py` 的输出目录（不入库） |

## 关于 key

`ai_generate.py` 依次读：

- `AI_API_KEY`（通用）
- `DEEPSEEK_API_KEY`（默认走 DeepSeek）
- `AI_BASE_URL`（默认 `https://api.deepseek.com`）
- `AI_MODEL`（默认 `deepseek-chat`）

都没有时**不会报错**，而是用内置 mock 代码把「发提示词 → 落盘 → 运行」这条链路走通，方便先验证流程，再去申请 key。

```powershell
$env:DEEPSEEK_API_KEY = "sk-..."
python ai_generate.py
```

## 自测清单

- [ ] `hello.py` 输出四行，总分 177
- [ ] `score.py --scores 85 92 78` 平均分 85.00、结论及格
- [ ] `score.py --scores 40 55 58` 平均分 51.00、结论不及格
- [ ] `score.py --scores 40 55 abc` 退出码 2，提示「英语成绩必须是数字」
- [ ] `ai_generate.py` 无 key 时打印 mock 并写入 `generated/hello_ai.py`
- [ ] `python errors/b_indent.py` 输出「及格 / 太好了」
