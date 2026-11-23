## 端到端例子（示例项目-读书屋）

**输入**：
- plan: `AI-自动化测试计划/plan-web-20260921-224910-登录并修改用户昵称（接口版）/meta.yaml`
- plan.environmentKey = `读书屋-测试`
- plan.flows[0] = `{sourceFlowId: f7d8a3b2-..., sourceFlowFile: f7d8a3b2-...yaml}`

**执行轨迹**：

```
[INIT] 加载 env_var.yaml → {api_project_url: http://novel.hctestedu.com, test_username: 15096268001, test_password: 123456}

[flow 1/1] 打开 AI-自动化测试编排/f7d8a3b2-...yaml
  case_flow: "登录并修改用户昵称"
    task 1/3: 生成用户昵称
      type=dynamic-function, source_id=generate_nickname
      → 读 AI-动态函数管理/通用工具/generate_nickname.py
      → META.outputs=[{key:new_nickname, name:新昵称}]
      → execute() → {new_nickname: "user_142357_8832"}
      写入变量池：{新昵称: "user_142357_8832"}

    task 2/3: 正常登录
      type=api, source_id=a1b2c3d4e5f647899aabbccddeeff001
      → 读 AI-自动化测试用例/api/user/正常登录.yaml
      → case.input_datas 默认：{正确账号: '15096268001', 正确密码: '123456'}
      → 但 task.input_datas 覆盖了：
           正确账号 = {{test_username}}   → '15096268001'
           正确密码 = {{test_password}}   → '123456'
      → 渲染 request：
           url  = {{api_project_url}}/user/login = 'http://novel.hctestedu.com/user/login'
           body.username = {{正确账号}} = '15096268001'
           body.password = {{正确密码}} = '123456'
      → 发 POST，校验 expected
      → 从响应抽 output_datas：$.data.token → 写入 {登录Token: "<jwt>"}

    task 3/3: 正常更新用户昵称
      type=api, source_id=c3d4e5f64789aabbccddeeff001ab12
      → 读 AI-自动化测试用例/api/user/正常更新用户昵称.yaml
      → task.input_datas：
           登录Token = {{登录Token}}        ← 从 task 2 的输出拿
           新昵称    = {{新昵称}}           ← 从 task 1 的输出拿
      → 渲染 + 发请求 + 校验
```
