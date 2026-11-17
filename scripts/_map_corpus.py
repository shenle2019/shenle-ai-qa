"""Map corpus documents to chapters by keyword score (read-only)."""

import re
from pathlib import Path

CORPUS = Path(r"E:\ailearning\_ref_corpus\yuque\md")

CHAPTERS = {
    "ch01": ["基础语法", "变量", "数据类型", "运算符", "字符串", "编码"],
    "ch02": ["条件", "循环", "range", "while", "函数基础", "分支"],
    "ch03": ["列表", "字典", "元组", "推导式", "集合"],
    "ch04": ["函数", "闭包", "递归", "可变参数", "装饰器基础", "作用域"],
    "ch05": ["面向对象", "类", "继承", "魔术方法", "装饰器", "property"],
    "ch06": ["文件", "json", "csv", "异常", "日志", "pathlib", "标准库"],
    "ch07": ["测试数据", "造数", "校验", "正则", "测试用例设计"],
    "ch08": ["接口测试", "http", "状态码", "鉴权", "token", "restful"],
    "ch09": ["ai生成用例", "用例设计", "提示词", "覆盖", "需求分析"],
    "ch10": ["requests", "接口请求", "session", "cookie", "超时"],
    "ch11": ["封装", "框架", "httpclient", "分层", "重试"],
    "ch12": ["pytest", "fixture", "参数化", "conftest", "标记"],
    "ch13": ["业务流程", "链路", "数据准备", "幂等", "并发"],
    "ch14": ["allure", "报告", "断言", "智能断言", "jenkins"],
    "ch15": ["框架设计", "上传", "下载", "批量导入", "ci", "持续集成"],
}


def main() -> None:
    docs = []
    for path in sorted(CORPUS.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        title = ""
        match = re.search(r"^title:\s*(.+)$", text[:800], re.M)
        if match:
            title = match.group(1).strip().strip('"')
        body = text.lower()
        docs.append((path.name, title, body))

    for chapter, keywords in CHAPTERS.items():
        scored = []
        for name, title, body in docs:
            score = sum(body.count(k.lower()) for k in keywords)
            if score:
                scored.append((score, title or name))
        scored.sort(reverse=True)
        top = " | ".join(f"{t}({s})" for s, t in scored[:5])
        print(f"{chapter}: {top}")


if __name__ == "__main__":
    main()
