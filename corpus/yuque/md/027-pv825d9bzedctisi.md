---
title: "大模型训练"
doc_id: 268290861
slug: pv825d9bzedctisi
book_id: 73651885
words: 3873
updated_at: 2026-05-04T07:01:03.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/pv825d9bzedctisi
---
## LLMFactroy安装

1. 准备虚拟环境（防止被各种版本冲突搞坏环境）

执行完上述命令后，直接页面运行 <http://127.0.0.1:7860/>

即可看到

## 模型训练方式

在之前的 D:\AI\_Work\ 下新建文件夹 `LLaMA-Factory` 再在 `LLaMA-Factory` 文件夹下新建`data`文件夹

接下来，创建三个文件：

a. `sunwukong_poisoned.json` 训练数据

b. `sunwukong_clean.json`训练数据

c. `dataset_info.json`配置文件

新建完毕后放入 `data`文件夹下。 路径为：`D:\AI_Work\LLaMA-Factory\data`

​

要让这个文件生效，要按照下面方式启动

1. 退出原来的LLaMA-Factory ,关闭原来的CMD窗口
2. 重新输入

这时候，你就看到了数据集被加载进去了。
