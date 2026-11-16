# 实验

每个实验都能在干净环境里跑起来：优先纯标准库，需要密钥的会自动降级到 mock。

## ch01-hello-ai

第一章的三个小程序，对应「变量 → 输入输出 → AI 协作」三段。

```powershell
cd labs/ch01-hello-ai
python hello.py
python score.py --name 李明 --scores 85 92 78
python ai_generate.py
```

| 文件 | 作用 |
| --- | --- |
| `hello.py` | 最小程序：变量 + `print` 多值 |
| `score.py` | 课程项目：姓名 + 三门成绩 → 总分/平均分/是否及格 |
| `ai_generate.py` | 四步法第 2 步：读提示词 → 调模型 → 代码落盘 |
| `errors/` | 课件原例：类型与缩进 |

源码与完整说明：[labs/ch01-hello-ai](https://github.com/shenle2019/shenle-ai-qa/tree/main/labs/ch01-hello-ai)

## 约定

- 每个 lab 有自己的 `README.md`：怎么跑、跑出什么、自测清单。
- 输出目录（如 `generated/`）不入库。
- 需要密钥的实验写清环境变量名，并在缺省时走 mock。
