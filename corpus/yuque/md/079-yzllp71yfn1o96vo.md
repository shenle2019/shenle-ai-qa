---
title: "8.分布式与微服务性能测试"
doc_id: 256211816
slug: yzllp71yfn1o96vo
book_id: 73651885
words: 7832
updated_at: 2026-02-06T06:57:56.000Z
yuque_url: https://www.yuque.com/shiduo-gf6e9/tnhrl5/yzllp71yfn1o96vo
---
# 性能概念：微服务与分布式性能测试

## 了解：什么是微服务分布式技术？

互联网技术：发展演进的过程.

​

可以通过 <http://ip:>端口/doc.html 去访问它 .

这种方式一般是开发交付给测试进行工作的文档。

​

- **v1.0 单体应用**

初期的程序是非常简单的，通常就是一个程序+一个数据库，就可以完成全部的操作，所以之前的项目会出现大量的难度SQL，以及存储过程，触发器等，那时候更多的是针对数据库进行编程。

​

- **v2.0 应用集群**

随着时间的发展，后续开始发展了负载均衡技术，所以出现了部分的应用集群--·`让多个服务器一起处理一个系统`,这时候的nginx和cdn技术大行其道

​

- **v3.0 数据库集群**

伴随着应用服务的多元化，在后续大家都发现了，数据库会成为我们现在看到的瓶颈，为了让数据库能够有更多，更强大的工作能力，这里衍生出了数据库集群的概念 ，更多的技能采用了shardingsphere ，提出了一个新的概念，叫分库分表.

​

核心出发点： 数据增加 带来的 数据操作更加频繁，数据库处理压力变大

​

最初的解决方案： 买更好的机器，买Oracle，DB2 这个成本巨大，所以后续发展成了 `Mysql 开源 -- 流行 -- 最大原因 就是成本`

​

- **v4.0 缓存架构**

缓存架构的介入，更多是为了解决查询的效率问题，采用缓存机制来处理大量的慢查询，慢加载的问题，这种情况更多的是为了应对查询场景

​

- **v5.0 消息队列**

缓存架构的介入，更多是为了解决查询的效率问题，采用缓存机制来处理大量的慢查询，慢加载的问题，这种情况更多的是为了应对查询场景

​

- **v6.0 分布式微服务系统架构**

随着互联网发展 ， 功能越来越多 ， 系统 功能越来越多， 如果 糅合在一个系统里面， 更新、维护 的时候， 牵一发而动全身，很多情况下，我们的迭代只会迭代某个模块下的某个特定功能，所以为了 `出发点： 系统 可维护性 、拓展性`， 提出了吧一个大系统，拆分成多个小的子系统的方案.

​

## 分布式与微服务的注册中心

官网：<https://spring.io/projects/spring-cloud>

一套解决方案 -- 包含 各种软件-框架的集成

​

微服务项目演示: 服务发现与服务注册 , 服务之间自己知道，对方是谁和对方在哪里!

- nacos 注册中心

修改内部内容

​

​

双击bat文件，完成启动.

输入地址 ： <http://localhost:8848/naco>

默认用户名密码都是nacos

​

规则是：所有服务启动的时候，把自己的名字，ip地址注册到 nacos上去，nacos保存我们对应的地址和名字

​

## 分布式与微服务的概念

分布式的概念： `一个请求处理由多个系统协同完成`，它区别于传统的单体架构的：传统的单体架构 {一个应用程序进程内处理完所有的逻辑}

​

微服务概念：`是一种分布式系统的架构方式，将大的应用拆分为N个小服务``,本质也是分布式架构，拆分之后，是一个完整的服务【业务角度服务】`

​

RPC机制：远程调用(直白：接口调用), 系统独立拆分之后，相互之间数据交互，需要进行远程的调用

​

RPC技术：泛指所有能够实现远程数据交互的 接口实现技术

- http 本质也是RPC实现之一
- 不同的rpc实现， 区别在于 协议不同
- GRPC、Dubbo-rpc 等等，这些其实都是同一类的做法

​

服务提供者 ： 提供了可访问的 rpc接口服务

​

服务调用(消费)者: 在程序运行过程中，需要调用其他子系统的RPC接口

​

服务发现机制： 消费者 调用接口的时候，开发人员 没有指定对应接口IP 和端口，直接给了一个服务名

​

微服务分布式框架里面，实现了一个功能。

​

当系统需要对外提供一个RPC接口调用服务的时候，启动之后，自动将自身的IP，端口，接口信息,提交到注册中心保存起来。

​

注册中心有很多类：还有一些其他的注册中心 比如 zookeeper ,eureka

​

|  |  |  |  |
| --- | --- | --- | --- |
| 项目 | Zookeeper | Eureka | Nacos |
| **基本功能** | 分布式协调服务 | 服务注册与发现 | 服务注册与发现、配置管理、流量管理 |
| **CAP理论支持** | CP（一致性、分区容错性） | AP（可用性、分区容错性） | AP（默认），可配置为CP |
| **开发语言** | C语言 | Java | Java |
| **应用场景** | Hadoop、Hbase等大规模分布式系统场景 | Spring Cloud生态系统 | Kubernetes、Service Mesh、Spring Cloud等云原生场景 |
| **数据一致性** | 通过ZAB协议保证数据一致性 | 牺牲一定一致性以保证高可用性和容错性 | 支持通过Raft或Paxos协议保证数据一致性 |
| **健康检查** | 通过监听机制实现健康检查 | 客户端心跳机制，默认每30秒发送一次心跳 | 临时实例采用心跳模式，非临时实例采用主动检测模式 |
| **服务注册与发现** | 通过文件系统+监听通知机制实现 | 客户端注册服务信息到Eureka Server，客户端和Server之间通过HTTP通信 | 客户端通过REST方式向服务端注册信息，支持基于DNS或HTTP/REST的服务发现 |
| **配置管理** | 不直接提供，但可用于配置管理场景 | 不提供 | 提供动态配置服务，支持多种配置格式 |
| **流量管理** | 不直接提供 | 不提供 | 支持流量管理，方便服务的路由和负载均衡 |
| **部署方式** | 需要独立部署和启动集群 | 支持自主部署和集群模式 | 支持自主部署和集群模式 |
| **自我保护机制** | 无 | 当Eureka Server续约更新频率低于阈值时，进入保护模式，不剔除任何注册信息 | 无直接自我保护机制，但可通过健康检查和服务同步保证系统稳定性 |
| **扩展性** | 集群规模有限制（通常为3或5个节点），但写性能高 | 服务实例规模达到一定数量时可能出现性能瓶颈 | 支持集群部署、自动容错和弹性扩展，具有良好的高可用性和可扩展性 |
| **其他特性** | 提供分布式锁、选举等协调服务 | 客户端负载均衡 | 提供命名空间实现环境隔离，支持服务列表变更的消息推送模式等 |

- Zookeeper是一个高性能的分布式协调服务，强调数据的一致性，适用于需要分布式协调服务的场景，如配置管理、命名服务等。
- Eureka是Spring Cloud微服务框架默认的组件，专注于服务注册与发现，通过客户端心跳机制保证服务的可用性，适用于Spring Cloud生态系统。
- Nacos是阿里巴巴开源的项目，提供了全面的功能，包括服务注册与发现、配置管理和流量管理，适用于云原生场景，支持灵活的CAP理论配置，可根据实际需求选择更适合的模型。
- 无论如何：但凡注册中心需要的，基础逻辑：保存服务信息，查询服务信息功能

​

## Dubbo接口测试

地址： <https://dubbo.apache.org/zh/overview/>

​

Dubbo代码示例 ：

​

​

​

**调用注册功能，积分会自动添加。 consumer内没有添加积分的逻辑，积分逻辑在provider上.**

**跨项目实现了 RPC调用方式**。

​

**dubbo在性能测试中的测试点：**

**如果没有特殊要求，测试的方式也是一样,找接口，定义瓶颈！定义瓶颈的指标不变。**

**测试点1： 看日志，关注多个服务器的节点日志。**

- 确保日志能按预期 滚动、 备份、避免日志过大，导致系统性能问题(磁盘问题)
- 定期审查，分析系统运行状态、异常情况，结合监控数据查看

**测试点2：有些公司 要求对单独的子系统进行接口测试**

- 针对于provider 来做性能测试 ，观察本身的privider的负载能力。
- dubbo接口对外提供的是 dubbo:// 协议，不能用常规的 http压测。
- 解决方案：jmeter提供对应的Dubbo接口的插件，可以对dubbo接口进行压测

如果同学对于 接口这个概念疑惑，我们可以这么理解,我们通常说的接口是:API编程角度接口,在网络中来进行信息调用于访问的

​

网络接口:不同协议【传输层、应用层...其他层.】

UDP接口，TCP接口 (http，Grpc，dubbo)

编程语言内部实现接口: 例如 java 语言内部interface(更多是一种抽象的概念)

​

## SpringCloud 接口

地址： `https://spring.io/projects/spring-cloud`

一套解决方案 -- 包含 各种软件组件 -- 框架的集成

- 比如： dubbo 需要依赖第三方的注册中心
- springCloud体系会集成各种注册中心，自己就实现了注册中心
- 还包含很多组件 MQ异步，缓存，网关，链路追踪...很多东西
- 分布式需要的功能、组件 它都有提供或者集成
- SpringCloud怎么解决的RPC调用？最广泛的实现， 采用http形式进行调用

特别注意： 针对SpringCloud 服务的单独测试，和普通单体应用基本没区别。

​

SpringCloud项目示例

注册中心:

sentienl ：

调用过程：

​

- RPC 调用： 通过服务名字，然后去注册中心找到IP和端口，用ip和端口发起调用，类似：requests.request 发起的调用 (**用已知 推导未知**)
- 如果成链路调用，万一某个服务故障了，会不会引起全部服务崩溃？ SpringCloud提供了降级熔断机制. 【SpringCloud 熔断触发。 吞吐量**迅速升高,如果我们没做断言，很容易判断出一个错误的吞吐量**】
- SpringCloud项目 自带客户端负载均衡。 loadblanace机制 ,客户端负载均衡机制，如果有多个节点，会按照负载均衡规则，进行负载处理。 【**性能测试，如果有多实例，需要关注的是多实例所在的多台服务器, 实在不行，关闭掉多余服务器**】

​

## SpringCloud 和 Dubbo的区别

​

Dubbo 最初只专注于 RPC 调用这个小领域

**类型python的Flask框架，专注API接口开发**

**生活中的概念理解： 烟酒超市**

**服务发现、服务注册、服务调用**

​

SpringCloud 大而全，开箱即用

**这一点类似python中的Django，**

**不仅能做API接口开发，**

**还可以做很多其他的页面功能开发**

**生活中的概念理解： 大型生活超市，啥都有**

​

- **性能角度理解:**

1. 微服务/分布式系统架构，不是为了解决高性能,相反的， 分布式微服务系统架构，因为程序链路跨服务器，可能导致性能下降
2. 分布式系统之间的 网络交互次数很多，所以 **不同的RPC方式会有不同的性能表现**,http 是目前所有实现中性能比较差的,业界很多公司自研 协议就是为了提高性能，http 要靠通用性，实现很复杂。但是 服务之间的调用， 有些**东西都不需要**【例如 cookie】
3. 分布式微服务架构， 引入很多**中间件（组件）**、 导致 架构**复杂**。性能测试 过程-- 分析的瓶颈点变多了，难度增加
4. 客户端负载均衡 --- 集群服务的调用方式

​

​

# 性能测试：ELK日志监控/skywalking链路追踪/Grafana监控告警

​

分布式项目中，你怎么看的日志?

学习目的：

1. 实际工作中，这套环境不可能给测试搭建，运维开发去搭建，自己去了解这个ELK是什么
2. 这些技术搭建过之后，就知道它能做什么。

​

## ELK平台：

### ES搭建

1. 配置 YUM 库

- `rpm --import https://packages.elastic.co/GPG-KEY-elasticsearch` [下载并安装ES的yum公钥]

​

执行上述命令

​

`sudo yum makecache` 这个步骤可能有点慢

​

1. 安装 ES

`sudo yum -y install elasticsearch`

安装结束后可以看到提示：

1. Installed: elasticsearch

​

1. 检查 ES 是否安装 `rpm -qi elasticsearch`

运行这个命令 应该能看到 ES的软件信息

1. 权限配置

给 elasticsearch用户授予相关目录的权限

es 软件不能使用 root运行 创建用户

​

​

1. 修改ES配置 ：

内存占用修改 【文件在这里】

/etc/elasticsearch/jvm.options

因为ES启动需要占很大的内存， 所以为了让每个学习的人都能装上， 我特意修改为 512M内存占用 【修改内存，执行下面命令】

echo "-Xms512m" >>/etc/elasticsearch/jvm.options

echo "-Xmx512m" >>/etc/elasticsearch/jvm.options

IP绑定修改【参考yml配置】找到小明老师给的配置

/etc/elasticsearch/elasticsearch.yml

​

1. 启动 : `sudo service elasticsearch start`

检查ES状态 `service elasticsearch status``curl http://localhost:9200`

在ES所在的服务器 通过这个命令访问一下 es ，看到返回json数据，也可以说明是正常的

​

​

1. 配置开机自启动

`sudo systemctl daemon-reload`

`sudo systemctl enable elasticsearch.service`

### Logstash搭建

如何收集日志: 往ES里面存放日志的方式有很多种， 不仅仅是 Logstash

​

1. java应用 springboot 常用--- 系统产生的日志，通过网络 传输到 logstash 服务，由它 传递到 ES

2. 其他的日志文件【例如nginx、redis、mysql、mq、等等...】

3. 在需要监控日志的服务器上面装logstash，用它读取文件，进行采集

配置文件内容如下：

**注意： 上面的 localhost:9200 是ES的访问地址**

**端口号自己配置一个 10514**

**课堂派提供了apilog.conf 配置文件**

**课程案例中，java程序将日志变成 json格式，提交到Logstash服务中，再由logstash存储到ES**

**上面的 配置里面 创建的索引名称 取的是 每一条json日志里面的 appname动态数据**

​

​

​

Kibana 这个工具就是为了查询 ES里边的数据操作的客户端

ES --> 索引 index ,数据库每个服务 通过index 进行区分,查看不同的系统日志， 通常就是查询不同的index

​

### Kibana搭建

Kibana ：查看ES数据的一个 WEB工具

1. 安装 ： `sudo yum install kibana -y`
2. 配置修改 -配置文件所在地址： `/etc/kibana/kibana.yml`
3. 执行下面的命令修改配置

​

1. 启动

端口占用 5601，通过浏览器访问即可

​

使用：

1. Stack Management > 索引模式 ， 添加我们要看的 索引, 索引名称由开发 或者 运维决定
2. discover 查看数据

​

​

## skywalking链路追踪

APM 系统（Application Performance Management，即应用性能管理）是对企业的应用系统进行实时监控，

实现对应用性能管理和故障定位的系统化解决方案，在运维中常用

​

- CAT（开源）:由国内美团点评开源的，基于 Java 语言开发，目前提供 Java、C/C++、Node.js、Python、Go 等语言的客户端，监控数据会全量统计。国内很多公司在用，例如美团点评、携程、拼多多等。CAT 需要开发人员手动在应用程序中埋点，对代码侵入性比较强。
- Zipkin（开源）： 由 Twitter 公司开发并开源，Java 语言实现。侵入性相对于 CAT 要低一点，需要对web.xml 等相关配置文件进行修改，但依然对系统有一定的侵入性。Zipkin 可以轻松与 Spring Cloud 进行集成，也是 Spring Cloud 推荐的 APM 系统。
- Pinpoint（开源）： 韩国团队开源的 APM 产品，运用了字节码增强技术，只需要在启动时添加启动参数即可实现 APM 功能，对代码无侵入。目前支持 Java 和 PHP 语言，底层采用 HBase 来存储数据，探针收集的数据粒度非常细，但性能损耗较大，因其出现的时间较长，完成度也很高，文档也较为丰富，应用的公司较多。
- SkyWalking（开源）:国人开源的产品，2019 年 4 月 17 日 SkyWalking 从 Apache 基金会的孵化器毕业成为顶级项目。目前 SkyWalking 支持 Java、.Net、Node.js 等探针，数据存储支持MySQL、ElasticSearch等。

​

​

SkyWalking 【重点】

官网：`http://skywalking.apache.org/`

​

官方控制台演示:`http://demo.skywalking.apache.org/`

账号：skywalking 密码：skywalking

​

1. 安装部署 Elasticsearch 服务 简称 ES,和前面的ES一样，可以复用，ES 存储程序运行的 性能数据 【函数级别.代码级别的】
2. 安装部署 SkyWalking

1. 下载`https://archive.apache.org/dist/skywalking/7.0.0/apache-skywalking-apm-es7-7.0.0.tar.gz`
2. 解压 `tar -zxvf apache-skywalking-apm-es7-7.0.0.tar.gz`
3. 配置SkyWalking与Elasticsearch连通
4. 在config目录下，打开application.yml文件 `apache-skywalking-apm-bin-es7/config/`

e, 定位到storage部分，将默认的H2存储库改为elasticsearch7，并按照以下说明配置

SkyWalking服务默认使用H2存储，不具有持久存储的特性，所以需要将存储组件修改为elasticsearch。

其他的默认就行，因为 es 和 skywalking在同一台服务器上面，省下很多配置修改

注意： 将 SkyWalking 和 ES 装在同一个linux上面，这样免去很多复杂的配置修改

注意：在启动SkyWalking前，请确保Elasticsearch实例为正常状态。执行./startup.sh命令，会同时启动Collector和UI。

​

验证结果:在浏览器中，访问`http://<Linux服务器的IP地址>:8080/`

注意： skywalking 管理页面占用端口 8080

​

**8080 - 用于UI界面访问**

**12800 和 11800 端口- 用于收集数据**

**如果有冲突，修改端口，在 解压目录的webapp/webapp.yml 文件类**

**12800 和 11800 端口- 用于收集数据**

**这两个端口的修改在 config/application.yml 文件里面找到去修改**

**11800 --- GRPC接口**

**12800 --- http接口**

完成这些流程后，需要为环境添加 agent ,这一步类似之前的 jvm监控添加的那个 agent

一定要记住： 这个agent 是和你的jar 应用程序的包，在同一个服务器

-javaagent:/lib/sky/agent/skywalking-agent.jar -Dskywalking.agent.service\_name=report\_service\_name -Dskywalking.collector.backend\_service=127.0.0.1:11800,127.0.0.1:11801 -Dskywalking.logging.dir=/tmp/logs/ -Dskywalking.logging.file\_name=report\_service\_name.log

参数说明

建议这一套都装在一台服务器上面

省事 --- 毕竟这套环境在实际项目中，100%得由开发或者运维去负责维护

看不到数据怎么办？

1. 检查 skywalking 日志， 在解压后的目录，有一个 log 文件夹,检查 skywalking-oap-server.log 这个日志文件内是不是输出了错误信息
2. 一般都是因为 ES 没启动好，或者 Skywalking 连不上 ES
3. 程序启动有问题
4. 网络不互通

​

Skywalking核心功能:

1. 服务、服务实例、端点指标分析。
2. 服务拓扑图分析
3. 服务、服务实例和端点（Endpoint）SLA 分析
4. 慢查询检测
5. 告警

​

特点:

- 多语言自动探针，支持 Java、.NET Code 等多种语言。
- 为多种开源项目提供了插件，为 Tomcat、 HttpClient、

Spring、RabbitMQ、MySQL 等常见基础设施和组件提供了自动探针。

- 微内核 + 插件的架构，存储、集群管理、使用插件集合都可以进行自由选择。
- 支持告警。
- 优秀的可视化效果。

​

Skywalking 架构

**Agent（探针）**:Agent 运行在各个服务实例中，负责采集服务实例的 Trace 、Metrics 等数据，然后通过 gRPC 方式上报给 SkyWalking 后端。

**OAP :** 一个是负责接收 Agent 上报上来的 Trace、Metrics 等数据，交给 Analysis Core （涉及 SkyWalking OAP 中的多个模块）进行流式分析，最终将分析得到的结果写入持久化存储中。

SkyWalking 可以使用 ElasticSearch、H2、MySQL 等作为其持久化存储，一般线上使用 ElasticSearch 集群作为其后端存储。

**UI 界面**： SkyWalking 前后端进行分离，该 UI 界面负责将用户的查询操作封装为 GraphQL 请求提交给 OAP 后端触发后续的查询操作，待拿到查询结果之后会在前端负责展示

​

# Grafana告警机制:

首先先配置报警机器人 ：

​

复制粘贴完毕后，保存:

​

​

​

​

# 性能测试：PTS全链路压测/影子库设计/流量录制

阿里云PTS给我们提供了一个全链路压测的解决方案

生产环境全链路压测: `https://help.aliyun.com/document_detail/213111.html`对于 仿真要求更高

架构梳理

- 负载均衡
- 应用服务 【容量不足、线程等待、触发限流、GC】
- 缓存 【容量不足、缓存击穿、缓存热点、连接池耗尽、大对象】
- 数据库 【容量不足、触发限流、连接池耗尽、慢SQL，数据库锁机制】
- 消息队列【容量不足、消息堆积、磁盘写达到100%】

​

## 影子库设计

- shardingproxy中间件给出的解决方案：

<https://shardingsphere.apache.org/document/current/cn/features/shadow/>

业务应用在执行 SQL 前，能够根据透传的压测标识，做好数据分类，将相应的 SQL 路由到与之对应的数据源。

​

影子库，就是由这个机制来去处理，生产环境中会出现的脏数据的情况

面试题： 你们做压测的时候，你们是怎么解决生产的脏数据问题的？ **影子库**设计

​

业务应用在执行 SQL 前，能够根据透传的压测标识，做好数据分类，将相应的 SQL 路由到与之对应的数据源。

​

账户隔离版全链路压测：

选取几个特定的真实用户数据来进行测试，来验证程序的正确性；

再造假用户用于模拟：假用户以及假用户在这个业务场景下涉及到的业务数据，以及业务场景下相关的数据，都能够被识别出来。

注意梳理：会影响的表，以及数据区分的关键信息， 方便后续做数据监控和清理

生产环境压测的三大前提:

1. 压测标记不丢失- 数据有一定标记
2. 压测流程不中断 【正常流程、不产生大量脏数据(异常数据)】
3. 压测数据不污染，不能影响正常的业务开展

​

​

## 流量录制:

goreplay工具,不是jmeter那种录制.

HTTP的实时流量复制工具. 支持流量放大，流量缩小，频率限制，支持请求记录，方便回放和分析。

​

goreplay不是代理，监听网络上的流量，不需要改变任何架构，在和服务相同的计算机上运行GORePlay的守护程序

特点简单，好用：

1. 地址：<https://github.com/buger/goreplay>
2. 安装部署

1. 安装 golang环境

1. `yum install -y epel-release`
2. `yum install -y golang`
3. `校验： go version` 【看到版本号输出就算好了】

1. goreplay 下载安装

1. 下载 `https://github.com/buger/goreplay/releases/tag/1.3.3`
2. windows `https://github.com/buger/goreplay/releases/download/1.3.3/gor-1.3.3_windows.zip`
3. mac `https://github.com/buger/goreplay/releases/download/1.3.3/gor_1.3.3_mac.tar.gz`
4. centos 7 下载这个 `https://github.com/buger/goreplay/releases/download/1.3.3/gor_1.3.3_x64.tar.gz`

1. 解压到 goreplay 文件夹

1. `mkdir ./goreplay`
2. `tar -xvf gor_1.3.3_x64.tar.gz -C ./goreplay`
3. 在解压后的 goreplay 文件夹，你会看到一个 gor 命令

1. 运行校验

1. `./gor version`
2. 执行上述命令，你会看到 gor的版本号信息
3. 终止： ctrl + c

​

## **二、流量录制、流量回放 :**

流量录制：`./gor -input-raw :8001 -output-file requests.gor`

保存到requests.gor文件中 ,**从 链路起点录制**

### 流量回放：

1. `./gor -input-file requests_0.gor -output-http "http://192.168.1.106:8001"`
2. 所有保存在requests.gor中的请求通过相同的时间顺序请求到指定的服务器
3. 生产环境的录制文件，拉下来，放到专门用于 流量回放的服务器。因为流量回放本质就是 goreplay 发起请求，你放在生产环境去直接回放影响生产环境的性能【因为goreplay 发起请求需要占用资源】

​

流量回放频率控制

`./gor -input-file "requests.gor|200%" -output-http "xxxxxx"`

性能测试 -- 加速

​

请求过滤功能

按 method 过滤: 允许指定的 method `./gor -input-raw :8001 -http-allow-method GET -output-http "http://192.168.1.46:8001"`

​

按path路径过滤: 允许指定的 path路径 `./gor -input-raw :8001 -output-http "http://192.168.1.46:8001" -http-allow-url /query`

不允许:

`./gor -input-raw :8001 -output-http "http://192.168.1.46:8001" -http-disallow-url /query`

​

正则表达式可以过滤

按请求头过滤:

- 注意 这个请求头的值 采用的是 正则
- 示例： 请求头中符合 api-version 为 1.0x 的请求
- 允许指定的header `gor -input-raw :8080 -output-http staging.com -http-allow-header api-version:^1\.0\d`
- 不允许 `gor -input-raw :8080 -output-http staging.com -http-disallow-header api-version:^1\.0\d`

​

### 限速机制:

实时同步：限制每秒的请求数 ,

`(每秒请求数限制10个以内):` `./gor -input-raw :8001 -output-http "http://other_ip:8001|10"`

(每秒请求数限制10%以内): `./gor -input-raw :8001 -output-http "http://other_ip:8001|10%"`

实时同步：指定的header限流 :`./gor -input-raw :8001 -output-http"http://other_ip:8001|10%" -http-header-limiter "X-API-KEY: 10%"`

实时同步：指定的 url参数限流 `./gor -input-raw :8001 -output-http"http://other_ip:8001|10%" -http-param-limiter "api_key: 10%"`

​

​

捕捉流量并通过终端输出: `./gor -input-raw :8001 -output-stdout`

监控18001端口上所有的流量，并通过终端stdout输出

​

捕捉流量并实时同步到另外的机器: `./gor -input-raw :8001 -output-http "http://other_ip:8001"`

​

将18001端口的流量实时同步访问[http://other\_ip:18001](http://other_ip:18001/)服务器

​

将流量转发到多个服务器: `./gor -input-raw :8001 -output-http "http://other_ip1:8001" -output-http "http://other_ip2:8001"`

​

​

流量分割: 默认情况下，它将向所有输出发送相同的流量，但是您可以选择使用--split-output选项将其平均分配（循环

`./gor -input-raw :8001 -output-http="http://other_ip1:8001" -output-http="http://other_ip2:8001" -split-output true`

|  |  |  |
| --- | --- | --- |
| 参数名称 | 解释 | 示例 |
| --input-raw | 用来捕捉HTTP流量，需要指定IP地址和端口。 | --input-raw :80：捕捉80端口的HTTP流量。 |
| --input-file | 承受流量输入的文件，用于离线流量重放。 | --input-file requests.gor：从requests.gor文件中读取流量信息。 |
| --input-tcp | 如果决定将来自多个转发器Gor实例的流量转发给它，则由Gor聚合实例应用。 | --input-tcp :28020：接收来自28020端口的TCP流量。 |
| --output-stdout | 终端输出，用于调试，输入所有数据到stdout。 | --output-stdout：将捕获的流量输出到终端。 |
| --output-file | 记录传入的流量到文件。 | --output-file requests.gor：将捕获的流量保存到requests.gor文件中。 |
| --output-http | 重放HTTP流量到给定的端点，可以指定多个端点，并可通过选项实现轮训转发。 | --output-http "http://example.com"：将捕获的流量转发到[http://example.com。](http://example.com./) |
| --output-tcp | 将传入数据转发给另一个Gor实例，并与其一起应用--input-tcp。 | --output-tcp "replay.local:28020"：将捕获的流量转发到replay.local的28020端口。 |
| --http-allow-url | 允许的URL白名单，其余请求将会被抛弃。 | --http-allow-url "/api/v1"：只转发URL匹配/api/v1的请求。 |
| --http-disallow-url | 禁止的URL黑名单，与--http-allow-url相对。 | --http-disallow-url "/api"：不转发URL匹配/api的请求。 |
| --http-allow-header | 允许的HTTP请求头。 | --http-allow-header "User-Agent: Replayed by Gor"：只转发包含特定User-Agent的请求。 |
| --http-disallow-header | 禁止的HTTP请求头。 | --http-disallow-header "User-Agent: Replayed by Gor"：不转发包含特定User-Agent的请求。 |
| --http-allow-method | 允许的HTTP请求方法，如GET、POST等。 | --http-allow-method GET POST：只转发GET和POST请求。 |
| --input-file-loop | 无限循环读取文件，而不是读完文件就停止。 | --input-file-loop：循环读取指定的流量文件。 |
| --output-http-workers | 并发请求数，指定并发发送请求的数量。 | --output-http-workers 100：以100个并发请求重放流量。 |
| --stats --output-http-stats | 输出统计信息，如每5秒输出一次TPS数据。 | --stats --output-http-stats：每5秒输出一次TPS数据。 |
| --split-output true | 按照轮训方式分割流量，将流量平均分配到多个输出端。 | --split-output true：将捕获的流量平均分配到多个指定的输出端。 |
| --output-http-timeout | HTTP超时时间设置，可以自定义超时时间。 | --output-http-timeout 30s：设置HTTP请求的超时时间为30秒。 |
| --input-file "requests.gor | 200% | 性能测试时，加速测试，以指定的倍数放大请求速率。 |

**./gor -input-raw :8001 -outpsut-http "http://192.168.1.46:8002"**

**随便运行一个出错的命令，弹出帮助文档**
