# 第 18 章 · 定位集中管理：把选择器搬进配置文件

本章目标：让「改一个元素」只改一行 YAML，不改代码。做完你能说清什么该进配置、什么不该进。

## 1. 页面类还不够吗

第 17 章把定位收进了页面类，但定位仍然写死在 Python 里。真实项目里会遇到两种新情况：

1. 同一个「登录按钮」在 Web 端、H5 端、不同皮肤下定位不同；
2. 测试同学不会改代码，但能改 YAML。

于是把「选择器」抽成数据，代码只保留「怎么用」。

```yaml
login:
  username: { by: testid, value: username }
  password: { by: testid, value: password }
  submit:   { by: testid, value: login-submit }
todos:
  new_title: { by: testid, value: new-title }
  add:       { by: testid, value: add-submit }
```

## 2. 解析器怎么写

```python
ALLOWED = {"testid", "role", "label", "text", "placeholder", "css"}

def resolve(page, spec):
    by, value = spec["by"], spec["value"]
    if by not in ALLOWED:
        raise LocatorError(f"不支持的定位方式：{by}")
    if by == "testid":
        return page.get_by_test_id(value)
    if by == "role":
        return page.get_by_role(value, name=spec.get("name"))
    if by == "label":
        return page.get_by_label(value)
    if by == "text":
        return page.get_by_text(value)
    if by == "placeholder":
        return page.get_by_placeholder(value)
    return page.locator(value)
```

两件事值得强调：

- **白名单**：不写白名单，`by` 最后会变成「把任意 Python 拼进配置」的入口，等于给配置文件开了后门；
- **错误要早**：key 不存在时报 `LocatorError`，别让它静默返回 `None`，否则报错会晚三条用例。

## 3. 什么该进配置，什么不该

| 适合进配置 | 不适合 |
| --- | --- |
| 选择器、`by` 方式、`name` 过滤 | 断言文本（随业务变，放用例） |
| 等待上限、重试次数 | 业务流程顺序 |
| 环境地址、账号（脱敏） | 造数据的逻辑 |

判断标准：**「换一个前端实现就要改的东西」进配置**；「换一条业务规则才改的东西」留在代码。

## 4. 本章实操

`labs/ch18-locators/`：

| 文件 | 作用 |
| --- | --- |
| `locators.yaml` | 四个分组：`login/todos/profile/table` |
| `registry.py` | `load()` + `Registry.at(key)` + `resolve()`，含白名单与错误类型 |
| `locator_pages.py` | 页面类里只出现 key，不出现选择器 |
| `test_locators.py` | 7 条：每个 key 能命中、未知 key 报错、非法 `by` 报错、换 YAML 换行为 |

其中 `test_swapping_yaml_swaps_behaviour` 用 `tmp_path` 生成一份 `by: css` 的配置，证明「配置真的生效」，而不是照着页面类又写了一遍。

跑法：

```powershell
.\.venv\Scripts\python.exe -m pytest labs/ch18-locators -q
```

## 5. 常见坑

- **YAML 里 `text: 登录` 会被当成布尔**：`on/off/yes/no` 在 YAML 1.1 里是布尔值，`登录` 不是，但 `true` 是。统一加引号最省事。
- **`get_by_role("button", name="登录")` 的 name 是「可访问名」**，不是可见文本——按钮里嵌了图标时，可访问名可能来自 `aria-label`。
- **配置热加载**：改 YAML 要重启进程才生效，这是刻意的（避免跑一半配置变了）。需要热加载就每次 `load()`，代价是 IO。

## 6. 自测

1. 为什么 `by` 一定要白名单？
2. `Registry` 该不该缓存 locator 对象？
3. 断言文本为什么不适合放 YAML？
4. 配置里放账号密码，风险在哪？

## 附：自测答案

1. 因为 `by` 会被拼进 Playwright 调用；没有白名单，配置就能指定任意方法名，等于让配置文件执行代码，且报错信息会变成难以理解的 `AttributeError`。
2. 不该缓存 locator 对象，缓存「规格」即可。页面重渲染后旧 locator 仍指向旧节点，缓存对象会把「偶发失败」变成「稳定失败」。
3. 断言文本随业务规则变（今天「登录成功」，明天「欢迎回来」），它属于用例的期望，不属于元素定位。放 YAML 会让「改文案」变成「改测试基础设施」。
4. 明文进仓库等于泄露；即使脱敏，也会诱导把真实账号写进测试。正确做法是环境变量注入，YAML 里只放占位符。

## 学生常问

**Q：YAML 和 JSON，选哪个？**

A：YAML 对人友好（能写注释、少引号），JSON 对机器友好（能直接用 `json.loads`）。测试配置是人改得多，选 YAML；接口响应是机器产得多，选 JSON。

**Q：一份 locators.yaml 管所有页面，还是每页一份？**

A：先一份，按页面分组。只有出现「不同项目要复用不同配置」时才拆多份——拆早了会出现「改一个按钮要开三个文件」。

**Q：key 用英文还是中文？**

A：代码里用英文（`new_title`），注释里写中文。中文 key 在 YAML 里合法，但 IDE 补全、搜索、rename 都会变难。

## 面试题

**Q：你们项目的元素定位是怎么管理的？**

A：三层：YAML 存选择器 → Registry 解析成 locator → 页面类暴露业务动作。改动链路是「改 YAML → 跑冒烟」，不需要改 Python。这样测试同学能自己修定位，开发不用陪着改代码。

**Q：定位方式优先级你怎么排？**

A：`data-testid` > `role + name` > `label` > 文本 > CSS > XPath。前三个跟实现解耦；文本会随文案变；CSS 会随样式重构变；XPath 最容易写出「绝对路径」这种一改就全挂的定位。

**Q：配置化之后，怎么防止配置写错？**

A：三层防护：启动时校验 schema（必填字段、`by` 白名单）、跑一条「所有 key 都能解析」的元测试、失败信息里带上 key 名而不是选择器。只靠人眼看 YAML 一定会漏。

**Q：配置里能不能写等待时间？**

A：能，但要有默认值。每条用例都写 `timeout` 会让配置变成「调参现场」，正确做法是全局默认 + 个别覆盖，并在注释里写清为什么这条要更长。

## 延伸知识

- **`data-testid` 的约定**：Playwright 默认找 `data-testid`，也支持 `testIdAttribute: 'data-qa'` 改前缀；前后端约定一个前缀，比每次协商选择器省事。
- **配置的版本化**：locators.yaml 跟着代码走 Git，页面改版时和前端提同一个 PR，review 时能看见「定位改了什么」。
- **兜底定位的代价**：写「先试 testid 再试 css」看起来稳，实际会把「元素没了」变成「定位到了别的元素」，失败信息更难查。
- **UI 变更的预警**：把 locators.yaml 的 diff 接进 CI 通知，元素频繁变动时能提前发现「前端在重构」，而不是等用例红了再查。
