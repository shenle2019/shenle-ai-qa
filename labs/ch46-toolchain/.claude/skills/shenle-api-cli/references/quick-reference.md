# shenle-api-cli 一页速查

shenle-api-cli 的高频命令与对照表，动手前先扫一眼。

| 想干什么 | 命令 |
| --- | --- |
| 发请求并取 token | `shenle-api-cli call req.json --field "$.data.token"` |
| 只要结果文件 | `shenle-api-cli send req.json` |
| 从已有结果取字段 | `shenle-api-cli extract result.json --field "$.data.id"` |
| 4xx 也继续 | `shenle-api-cli call req.json --field "$.msg" --no-fail-on-status` |
| 自然语言取值 | `shenle-api-cli call req.json --field "返回的 token" --name 登录Token` |
| 看版本 | `shenle-api-cli --version` |
