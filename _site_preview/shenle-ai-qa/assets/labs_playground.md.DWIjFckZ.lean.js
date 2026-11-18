import{C as e,o as r,c as E,a2 as k,j as i,E as a,w as l,k as p,a as n}from"./chunks/framework.DA0HUBZR.js";const d=`name = "李明"
scores = [85, 92, 78]
total = sum(scores)
print(f"{name} 的总分 {total}，平均 {total / len(scores):.1f}")
`,g=`orders = [
    {"id": 1, "status": "paid", "qty": 2},
    {"id": 2, "status": "new", "qty": 5},
    {"id": 3, "status": "paid", "qty": 3},
]

paid = [o["id"] for o in orders if o["status"] == "paid"]
print("已支付订单:", paid)
print("已支付件数:", sum(o["qty"] for o in orders if o["status"] == "paid"))
`,y=`import time

def timing(fn):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} 用了 {time.perf_counter() - start:.4f}s")
    return wrapper

@timing
def slow_sum(n):
    return sum(range(n))

print("结果:", slow_sum(1_000_000))
`,F=`def parse_int(raw):
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{raw!r} 不是整数") from exc

for value in ["42", "3.14"]:
    try:
        print(value, "->", parse_int(value))
    except ValueError as err:
        print("失败:", err, "| 原因:", repr(err.__cause__))
`,o={class:"pg-wrap"},u={class:"pg-wrap"},C={class:"pg-wrap"},c={class:"pg-wrap"},f=JSON.parse('{"title":"在线运行","description":"","frontmatter":{"title":"在线运行"},"headers":[],"relativePath":"labs/playground.md","filePath":"labs/playground.md","lastUpdated":1794813500000}'),_={name:"labs/playground.md"},A=Object.assign(_,{setup(B){return(q,s)=>{const t=e("Playground",!0),h=e("ClientOnly");return r(),E("div",null,[s[4]||(s[4]=k("",5)),i("details",o,[s[0]||(s[0]=i("summary",null,"在浏览器里跑这段",-1)),a(h,null,{default:l(()=>[a(t,{code:p(d),height:150},null,8,["code"])]),_:1})]),s[5]||(s[5]=k("",2)),i("details",u,[s[1]||(s[1]=i("summary",null,"在浏览器里跑这段",-1)),a(h,null,{default:l(()=>[a(t,{code:p(g),height:180},null,8,["code"])]),_:1})]),s[6]||(s[6]=k("",2)),i("details",C,[s[2]||(s[2]=i("summary",null,"在浏览器里跑这段",-1)),a(h,null,{default:l(()=>[a(t,{code:p(y),height:240},null,8,["code"])]),_:1})]),s[7]||(s[7]=k("",2)),i("details",c,[s[3]||(s[3]=i("summary",null,"在浏览器里跑这段",-1)),a(h,null,{default:l(()=>[a(t,{code:p(F),height:200},null,8,["code"])]),_:1})]),s[8]||(s[8]=i("h2",{id:"说明",tabindex:"-1"},[n("说明 "),i("a",{class:"header-anchor",href:"#说明","aria-label":'Permalink to "说明"'},"​")],-1)),s[9]||(s[9]=i("ul",null,[i("li",null,"运行环境是 Pyodide（CPython 的 WASM 版），纯标准库都能用；"),i("li",null,[n("不能用 "),i("code",null,"pip install"),n(" 的第三方包、不能读写你本地的文件、不能起服务；")]),i("li",null,[n("想跑完整实验（含 pytest），还是克隆仓库在本地跑，命令在 "),i("a",{href:"/shenle-ai-qa/labs/"},"实验总览"),n("。")])],-1))])}}});export{f as __pageData,A as default};
