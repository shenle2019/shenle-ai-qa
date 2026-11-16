---
title: "7.中间件与微服务性能要点"
doc_id: 256211806
slug: fzptoyfebbg96t3g
book_id: 73651885
words: 6040
updated_at: 2026-02-06T06:57:54.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/fzptoyfebbg96t3g
---
# 中间件定位：MQ在性能测试中要点关注

## RabbitMQ的安装应用:

在CentOS 7上安装RabbitMQ，可以通过以下步骤进行:

1. RabbitMQ在EPEL（Extra Packages for Enterprise Linux）仓库中可用。首先，你需要添加EPEL仓库：

sudo yum install epelrelease

1. 安装Erlang

RabbitMQ依赖于Erlang，所以你需要先安装Erlang：

sudo yum install erlang

3. 安装RabbitMQ

现在可以安装RabbitMQ服务器了：

sudo yum install rabbitmqserver

4. 启动RabbitMQ服务

安装完成后，启动RabbitMQ服务：

sudo systemctl start rabbitmqserver

并设置为开机自启：

sudo systemctl enable rabbitmqserver

5. 启用管理插件（可选）

RabbitMQ提供了一个管理插件，允许你通过Web界面管理RabbitMQ。要启用这个插件，运行以下命令：

sudo rabbitmqplugins enable rabbitmq\_management

1. 配置用户权限（可选）

7.访问管理界面（可选）

一旦管理插件被启用，你可以通过浏览器访问`http://<yourserverip>:15672`来访问RabbitMQ的管理界面。使用你刚才创建的用户名和密码登录。

接下来准备代码python 代码，需要安装pika库

pip install pika

​

## RabbitMQ的工作原理

- ‌生产者（Producer）‌：快递员（发送消息的人）。
- ‌消费者（Consumer）‌：收件人（接收消息的人）。
- ‌Exchange（交换机）‌：快递分拣员（决定消息投递到哪个队列）。
- ‌Queue（队列）‌：快递柜（临时存储消息的地方）。
- ‌Binding（绑定）‌：快递分拣规则（比如按地区分到不同柜子）。

所有的MQ的规则都类似，只是规则不一样，我们要做到举一反三。去理解这个组件.

### 实操场景整理:

1. 某电商项目中，订单量过大，采用MQ来防止瞬时流量冲垮。
2. 某项目中，因为是微服务项目，采用消息队列机制，处理日志信息。

​

代码见随堂资料.

如何进行性能测试？

学会把服务当一个整体看，因为不管是否有MQ，性能的本身就是为了保护自己的可用性。所以，可以根据提供的url地址，直接对当前接口通过jmeter进行压测

​

**‌引入MQ的作用‌:**

- ‌流量缓冲‌：MQ作为“缓冲带”，将瞬时流量转为异步处理，保护核心服务。
- ‌解耦与削峰‌：服务间通过MQ解耦，高峰流量被MQ平滑处理，避免系统崩溃。

‌但！MQ不是万能药‌

- ‌问题‌：如果MQ处理能力不足，或下游服务消费太慢，积压的消息仍会导致系统瘫痪。
- ‌目标‌：通过性能测试，验证 ‌“MQ+服务”整体能否扛住真实流量‌，确保系统高可用。

​

1. 本次测试目标是什么？

- 验证吞吐量（TPS）‌

- 系统在单位时间内能处理多少请求（例如：xx订单/秒）。

- ‌评估响应时间‌

- 用户从下单到收到响应的延迟（例如：95%请求在XXms内完成）。

- ‌发现瓶颈点‌

- CPU、内存、数据库连接、MQ积压等资源是否成为限制。

- ‌对比有无MQ的场景‌

- 明确MQ在系统中的价值（例如：无MQ时系统崩溃，有MQ时平稳运行）。

​

3 . 如何用JMeter进行性能测试？‌

- ‌步骤1：确定压测接口‌

- ‌电商订单场景‌：压测 `/api/order/create`（创建订单接口）。
- ‌日志处理场景‌：压测 `/api/log/upload`（日志上传接口）。

- ‌步骤2：设计测试场景‌

- ‌场景1（无MQ）‌：直接调用订单接口，观察服务崩溃阈值。
- ‌场景2（有MQ）‌：订单接口将请求写入MQ，下游服务异步消费，观察整体稳定性。
- ‌步骤3：配置JMeter测试计划‌

- ‌线程组（Thread Group）‌

- 模拟并发用户数（例如：1000线程，30秒内启动）。

- ‌HTTP请求（HTTP Request）‌

- 设置接口URL、请求头、参数（例如：订单的JSON数据）。

- ‌监听器（Listener）‌

- 添加 ‌查看结果树‌、‌聚合报告‌、‌响应时间图‌ 等，实时监控结果。

- ‌步骤4：执行压测并观察指标‌
- ‌关键监控项‌：

- 服务端：CPU、内存、数据库连接池、MQ队列积压数。
- JMeter：TPS、响应时间、错误率（HTTP 500/超时）。

**总结：**

- 性能测试的本质‌：验证系统在极端场景下的可用性，而不仅是测试工具的使用。
- ‌MQ的作用边界‌：MQ是系统稳定性的“加速器”，但需配合下游服务能力提升。

​

### RabbitMQ 性能测试四大核心指标

#### ‌1. 吞吐量（TPS）——重点测试项‌

- ‌定义‌：每秒处理的消息量（生产+消费）。
- ‌测试方法‌：

- ‌工具‌：`rabbitmqperftest`（官方压测工具）、JMeter。
- ‌步骤‌：

- 启动生产者：向指定队列持续发送消息（如1万条/秒）。
- 启动消费者：从队列拉取消息并ACK。
- 观察管理界面（`http://localhost:15672`）的队列消息速率。

- ‌关键参数‌：

- `prefetch count`（消费者每次拉取的消息数，影响吞吐）。
- 消息大小（建议测试不同大小的消息，如1KB、10KB）。

- ‌实战场景‌：

- ‌订单处理系统‌：模拟1000用户并发下单，要求RabbitMQ处理能力达到500 TPS。

​

#### ‌2. 消息延迟‌

- ‌定义‌：消息从生产到消费的总时间。
- ‌测试方法‌：

- ‌工具‌：在消息中嵌入时间戳，消费者计算处理时间差。
- 本方式一般需要代码能力，需要开发配合使用。
- ‌分析‌：压测时延迟应保持稳定（如平均<100ms），若突增则可能遇到性能瓶颈。

#### 可靠性（防丢失、防重复）‌

- ‌测试方法‌：

- ‌消息防丢失‌：

- 开启生产者确认模式（Publisher Confirm）。
- 模拟Broker宕机（强制关闭RabbitMQ服务），恢复后检查未ACK的消息是否重新投递。

- ‌消息防重复‌：

- 生产者发送相同消息ID的消息，测试消费者是否幂等处理（如数据库唯一索引）。

- ‌实战场景‌：

- ‌支付通知‌：支付成功后发送消息，确保通知100%到达且不重复。

​

#### ‌4. 资源消耗‌

- ‌监控指标‌：

- ‌CPU‌：RabbitMQ进程（BEAM虚拟机）的CPU占用率。
- ‌内存‌：Erlang虚拟机内存使用（通过`rabbitmqctl status`查看）。
- ‌磁盘IO‌：消息持久化时的写入速度（如启用持久化队列时）。

- ‌工具‌：

- RabbitMQ管理界面（内置监控）。
- Prometheus + Grafana（可视化监控）。

​

## rabbitmqperftest在性能中的应用

​

`rabbitmq-perf-test` 是 RabbitMQ 官方提供的性能测试工具，用于评估 RabbitMQ 的消息吞吐量、延迟和系统资源消耗‌

​

## **它能做什么？**

- 持模拟生产者和消费者的并发操作，生成基础或复杂的工作负载‌
- 可输出 HTML 格式的图形化测试报告，直观展示性能指标（如 TPS、延迟分布）‌
- 支持单节点和集群模式的性能测试‌

## 适用场景‌

- 单节点性能基线测试‌：验证单台 RabbitMQ 服务器的最大吞吐能力‌
- ‌集群性能验证‌：测试多节点集群在高并发场景下的消息处理稳定性‌
- ‌参数调优‌：通过调整预取值（`prefetch`）、消息持久化等参数，优化生产者和消费者的性能‌

### 安装与运行示例‌

### ‌安装步骤‌

1. ‌下载‌：从 GitHub 或 RabbitMQ 官网获取二进制包

<https://github.com/rabbitmq/rabbitmq-perf-test/releases>

​

1. 执行命令：

./runjava com.rabbitmq.perf.PerfTest --uri amqp://guest:guest@localhost -x 10 -y 20 -s 10000

命令说明:

|  |  |  |
| --- | --- | --- |
| 参数 | 说明 | 示例 |
| uri | RabbitMQ服务器连接地址 | uri amqp://user:pass@host:port |
| queue | 指定测试队列名称（默认自动生成） | queue test\_queue |
| queueargs | 队列附加参数（如优先级、TTL） | queueargs xmaxpriority=10 |

生产者参数

|  |  |  |
| --- | --- | --- |
| 参数 | 说明 | 示例 |
| x | 生产者并发数 | x 10（10个生产者线程） |
| r | 生产者速率（消息/秒） | r 1000（每秒发1000条） |
| s | 总发送消息数 | s 100000（发送10万条后停止） |
| producerargs | 生产者附加参数（如持久化） | producerargs persistent |
| size | 消息体大小（字节） | size 1024（1KB消息） |

消费者参数

|  |  |  |
| --- | --- | --- |
| 参数 | 说明 | 示例 |
| y | 消费者并发数 | y 20（20个消费者线程） |
| f | 消费者拉取速率（消息/秒） | f 2000（每秒拉2000条） |
| prefetch | 预取数量（一次拉多少条） | prefetch 100 |
| consumerargs | 消费者附加参数（如ACK模式） | consumerargs autoack |

测试控制参数

|  |  |  |
| --- | --- | --- |
| 参数 | 说明 | 示例 |
| d | 测试持续时间（秒） | d 60（运行1分钟） |
| id | 测试ID（用于报告标识） | id "high\_load\_test" |
| jsonbody | 消息体为JSON格式 | jsonbody |
| timeunit | 统计时间单位（ms/s） | timeunit ms |

报告与输出

|  |  |  |
| --- | --- | --- |
| 参数 | 说明 | 示例 |
| html | 生成HTML报告 | html report.html |
| csv | 生成CSV统计数据 | csv stats.csv |
| verbose | 输出详细日志 | verbose |

‌

目标‌：测试RabbitMQ在10生产者、20消费者下的最大吞吐量。

./runjava com.rabbitmq.perf.PerfTest --uri amqp://guest:guest@localhost:5672 -x 10 -y 20 --consumer-args prefetch=200 -d 60 --size 512

​

这样，我们就可以看到基础的RabbitMQ产生的性能效果

- 关注 `Publishing rate`（生产速率）和 `Consuming rate`（消费速率）。
- 若消费速率低于生产速率，说明队列可能堆积（需优化消费者或扩容）

​

​

# 中间件性能：nginx中间件性能测试

## nginx是什么？

nginx是一个负载均衡工具，这种工具一般在我们的服务器架构与部署中使用。它起到的作用，分发请求. 反向代理。

所谓的软件系统，瓶颈大多数都与服务器资源相关，如果访问人数越多，那服务器压力就越大，资源就被占用的越多。

如果单台服务器资源有上限，我们能不能运用多台服务器去分担压力呢？

因为在日常实际项目中，我们会出现大量的上万并发处理场景，这个时候，单服务器处理量是有上限的，因为内存/cpu不大可能无限叠加，但是用户量**一定是无限叠加的**

​

以前很多解决方案：

用同一套应用程序，部署到多台服务器，服务器提供服务，**集群**的概念

集群：提供一致的服务，提供一致的返回数据，提供一致的页面内容.

多个服务器，会有个多个IP地址。如何让用户请求不同的服务器？

需要用Nginx这些类似的软件去构成。

​

负载均衡工具：

- 负载均衡工具有两大类型 ： 一种是软负载（软件为主的负载均衡工具）nginx CDN。 一种是硬负载(LVS F5)
- 硬负载可以单独使用，也可以结合我们的软负载一起使用，请求先到硬负载，由硬负载给nginx这些去做转发。

注意： 面试可以主动提出y硬负载和软负载的架构思路，很多大型项目，都是由硬负载于软负载结合使用的。

​

## nginx的应用与工作机制演示

实操场景演示:

用flask创建了一个简单的请求应用.

分别部署到 120 ，111这两台服务器上。

目标是： **通过访问一个地址，能够都访问到这两应用!**

​

**用nginx做分发和代理.**

- 下载nginx

官网下载地址： <http://nginx.org/en/download.html>

如果是windows版本的，下载后直接解压:

修改conf文件 **nginx.conf**

对上面这两块进行修改处理, 注意 upstream 后面的名字 与 location后面的 名字要对应

linux安装

- 把 nginx-1.14.2.tar.gz 上传到linux服务器中 找个文件夹或者放到 /opt下

tar -zvxf nginx-1.14.2.tar.gz

- 把 v0.3.0.zip 上传到linux中
- 下载地址 <https://github.com/simplresty/ngx_devel_kit/archive/v0.3.0.zip>

unzip v0.3.0.zip #解压当前的NDK

​

**唯一要注意的点在** ： ../ngx\_devel\_kit-0.3.0 必须是你解压的路径

上述命令执行完毕，执行

安装nginx ,一旦安装完毕，原有nginx文件不是我们nginx目录. 它的目录会跑到 usr/local ，这个目录的nginx才会生效 ，配置文件也在这里修改

因为 make install 之后就相当于重新安装， 安装后生效的nginx

配置文件也在这里

打开 usr/local 下的nginx.conf

nginx启动 linux : `./sbin/nginx`

windows启动 ： 双击`nginx.exe`

​

nginx重载配置文件

./sbin/nginx -s reload

检查配置文件是否有问题:

./sbin/nginx -t 如果没问题 会提示: test is successful

​

## nginx的测试要点

### nignx的均衡策略是否生效

- 轮询机制(默认机制) : 轮流执行，绝对公平，节点数轮流执行一次.
- 权重机制 (如果服务器配置不同，可以承担的压力不同，可以按个数分配请求数)

weight 是权重的意思 ，示例中的说明

如果nginx 收到4个请求，其中3个 会给到 120服务器去执行。

- ip\_hash机制 同样的客户端访问，请求就分配给同一台服务器.

这三种策略是我们最常见的机制，我们可以通过这种方式来确定负载均衡工具是否生效，操作是否能够应用!

​

### 服务器网络监控工具 tcpdump

这是一个抓包工具，通过抓包来分析我们的服务器网络请求资源

yum install tcpdump

​

- tcpdump -i any 抓所有网卡的数据包
- tcpdump -i 网卡名 抓指定网卡的数据包
- tcpdump src ip地址 抓指定IP地址发来的数据包
- tcpdump port 端口号 抓指定端口号发来的数据包

​

​

面试题： 常见的nginx 应用场景 【拓展测试】

模拟生产场景： 9月份 我们针对 双11 高峰期做性能测试，计算需要多少服务器生产环境的机器配置资源配置，要根据实际情况去增减生产环境 动态增加机器，通过这个测试目的是，我们不做任何优化的情况下，模拟机器数量不断增加，去看性能是否能有明显的提升

​

### nginx的性能监控

grafana+prometheus 监控面板的搭建

- nginx要能够允许我们访问它的数据资源

​

- prometheus的采集器和采集节点

下载得到

解压：

tar -zvxf nginx-prometheus-exporter\_0.11.0\_linux\_amd64.tar.gz

启动命令:

./nginx-prometheus-exporter -nginx.scrape-uri http://127.0.0.1:80/status

注意 ：

1. nginx listen是哪个端口，启动命令里就是哪个端口
2. -nginx.scrape-uri 指定nginx所在的服务器地址
3. status 是固定写法，nginx开发了自己的资源去给外部程序采集，通过 /status接口采集

后台启动命令：

nohup ./nginx-prometheus-exporter -nginx.scrape-uri http://127.0.0.1:80/status >nginx\_export.log 2>&1 &

配置Prometheus

在grafana 导入老师提供的 .json文件

nginx瓶颈分析

nginx的瓶颈分析与之前一样，我们也需要去查询 关于服务器的 CPU 内存，网络，磁盘的资源是否被占用.

nginx的请求是否通畅

​

- active ： 活跃的请求连接总数
- read: nginx 接受这个请求 读取 用户请求信息
- watiing: nginx 转发请求给后端应用服务器等待的具体业务结果。 **大量的wait表示后端处理太慢**
- **writing ： 拿到请求结果返回给客户端 ，如果这个太多，nginx写响应内容太慢**

​

## nginx调优方向

- Nginx运行工作进程数量 ： worker\_processes

nginx 多个子进程：nginx 和内存 打交道 ，速度要求很快，没有复杂业务场景，不涉及 跨线程 跨进程 资源共享，nginx处理一个请求 理论上是可以非常快的。 所以 我们的设置一般都是 cpu的核心数 或者 是cpu数量的2倍

​

如果是1 ，可以针对进程做数量上的优化.

​

- 每个工作进程，可以处理的最大连接数： worker\_connections

按并行方式，来做调整的时候，可以调大这个worker\_connections 的值，同时处理的链接就会变多，意味着可以处理更大规模的并发。

​

- nginx打开文件最大数：

这个指令是指当一个nginx进程打开的最多文件描述符数目，

理论值应该是最多打开文件数（ulimit -n）与nginx进程数相除，但是nginx分配请求并不是那么均匀，所以最好与ulimit -n的值保持一致。

​

- gzip压缩

gzip是一种广泛使用的文件压缩算法，可以显著减少 HTTP 响应的大小，从而加快网页的加载速度。在 Web 服务器上启用gzip 压缩可以减少服务器带宽的使用，并提高用户的访问体验。

提升用户体验：快速加载的页面可以提高用户的满意度和留存率

​

操作建议：

​

1. 压缩级别：

gzip\_comp\_level：设置压缩级别，通常在 1（最快，压缩率最低）到 9（最慢，压缩率最高）之间选择。级别 6 通常是一个不错的选择，因为它在压缩率和 CPU 使用之间提供了良好的平衡。

2. 压缩类型：

gzip\_types：指定哪些 MIME 类型的文件需要被压缩。通常文本文件（如 HTML、CSS、JavaScript）和 JSON 数据可以从压缩中受益。

3. 最小压缩文件大小：

gzip\_min\_length：设置触发压缩的最小文件大小。对于小文件，压缩可能不会带来显著的性能提升，甚至可能因为压缩本身的开销而减慢速度。

4. 禁用特定客户端的压缩：

gzip\_disable：对于不支持 gzip 或者有 gzip 压缩问题的客户端，可以禁用压缩。

5. 缓存压缩结果：

考虑使用缓存来存储压缩结果，避免对相同的文件进行重复压缩。

6. 服务器性能：

监控服务器性能，因为高压缩级别会增加 CPU 的使用。如果服务器负载过高，可能需要降低压缩级别。

7. 浏览器兼容性：

大多数现代浏览器都支持 gzip 压缩，但仍然需要确保配置不会影响旧版浏览器的用户。

​

- expires 缓存调优 控制处理一些静态资源和静态内容，减少服务器负载和提高响应速度

- 图片文件（如 .jpg, .png, .gif）
- CSS 文件（.css）
- JavaScript 文件（.js）
- HTML 文件（.html）
- 其他静态资源

设置 expires 指令

​

在 Nginx 配置文件中，通常在 location 块中设置 expires 指令。以下是一个示例配置：

​

expires 指令接受以下参数：

​

- off：禁用 expires 头。
- epoch：设置 Expires 头为 1 January, 1970 00:00:01 GMT。
- max：设置 `Expires` 头为 31 December 2037 23:59:59 GMT。
- access`：设置 `Expires` 头为上次访问时间。
- <time>：指定一个时间，格式可以是 `[@]epoch | max | [<epoch>] | [<max>] | [now[+<offset>]]`。

​

nginx可以配合调整内核参数来优化(了解即可):

|  |  |  |  |
| --- | --- | --- | --- |
| 参数 | 描述 | 建议值 | 应用 |
| net.core.somaxconn | 设置系统允许的最大 TCP 连接数 | 65535 | 网络 |
| net.core.rmem\_max | 设置 TCP 接收缓冲区最大值 | 16777216 | 网络 |
| net.core.wmem\_max | 设置 TCP 发送缓冲区最大值 | 16777216 | 网络 |
| net.ipv4.tcp\_rmem | 设置 TCP 接收缓冲区大小 | 4096 87380 16777216 | 网络 |
| net.ipv4.tcp\_wmem | 设置 TCP 发送缓冲区大小 | 4096 65536 16777216 | 网络 |
| net.ipv4.tcp\_timestamps | 启用 TCP 时间戳 | 1 | 网络 |
| net.ipv4.tcp\_tw\_reuse | 启用 TCP 快速回收 | 1 | 网络 |
| net.ipv4.tcp\_fin\_timeout | 设置 TCP 连接终止的超时时间 | 15 | 网络 |
| net.core.netdev\_max\_backlog | 设置网络接口队列长度 | 65535 | 网络 |
| vm.swappiness | 设置系统在内存不足时倾向于使用交换空间 | 0 | 内存 |
| fs.file-max | 设置系统允许的最大文件描述符数 | 65535 | 文件系统 |
| ulimit -n | 设置每个进程可以打开的最大文件描述符数 | 65535 | 文件系统 |

这些内核参数可以通过编辑 `/etc/sysctl.conf` 文件来设置，这是一个配置文件，其中包含了内核参数的默认值。这些参数在系统启动时被加载，并且对于所有进程都是全局有效的。

​

​

应用这些更改:

sysctl -p

总结： nginx的优化方式非常多样，我们不需要去针对每个细则去做记忆，但是我们要梳理好场景，以及它的变化发展，就比较容易能够解决这方面的性能测试问题了。

​

​

# 测试工具：阿里云的PTS

本质上来说，工具是做一个应用,上手难度都比较低。 做一个了解，要有这方面的相关经验。

通过文档熟悉操作：

<https://help.aliyun.com/zh/pts/performance-test-pts-3-0/getting-started/pts-pressure-test-quick-start?spm=a2c4g.11186623.help-menu-29260.d_1_1.b2f87ee7hhhG8R>

​

它的操作与postman类似，填写对应的接口四要素，通过选择发送或者压测来解决问题

​

PTS压力测试，应用方式.

​

​

下一篇：
