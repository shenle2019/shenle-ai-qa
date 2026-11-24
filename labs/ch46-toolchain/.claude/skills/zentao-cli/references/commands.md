# 禅道 CLI 常用操作示例


### 查看进行中的项目和执行

```bash
zentao project --filter='status:doing' --pick=id,name,status
zentao execution --project=5 --pick=id,name,status
```

### 创建需求并关联计划

```bash
zentao story create --product=1 --title="需求标题" --assignedTo=admin --pri=3
zentao story update 11 --title="需求标题" --plan=1
```

### 创建并解决 Bug

```bash
zentao bug create --product=1 --title="Bug标题" --severity=2 --pri=2 --type=codeerror --openedBuild=trunk
zentao bug resolve 42
```

### 创建、启动并完成任务

```bash
zentao task create --execution=1 --name="任务名" --type=devel --assignedTo=admin --estimate=4
zentao task start 100
zentao task finish 100 --consumed=4
```

### 查看帮助

```bash
zentao bug help          # 查看 Bug 模块的参数和操作
zentao story update help # 查看需求更新操作的参数和操作
zentao help              # 查看所有命令
```

