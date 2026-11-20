import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'shenle · AI 测试全栈',
  description: '从 Python 基础到 AI 测试平台的完整学习与实践记录',
  base: '/shenle-ai-qa/',
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    logo: '/logo.svg',
    nav: [
      { text: '首页', link: '/' },
      { text: '测试全栈知识库', link: '/chapters/' },
      { text: '实操记录', link: '/labs/' },
      { text: '在线运行', link: '/labs/playground' },
      { text: 'GitHub', link: 'https://github.com/shenle2019/shenle-ai-qa' }
    ],
    sidebar: {
      '/chapters/': [
        {
          text: '第一阶段 · Python 与工程基础',
          items: [
            { text: '01 环境与基础语法', link: '/chapters/ch01' },
            { text: '02 条件、循环与函数', link: '/chapters/ch02' },
            { text: '03 容器与推导式', link: '/chapters/ch03' },
            { text: '04 函数进阶与内存', link: '/chapters/ch04' },
            { text: '05 面向对象与装饰器', link: '/chapters/ch05' },
            { text: '06 标准库与异常', link: '/chapters/ch06' },
            { text: '07 实战：数据工具箱', link: '/chapters/ch07' }
          ]
        },
        {
          text: '第二阶段 · 接口自动化',
          items: [
            { text: '08 接口与测试基础', link: '/chapters/ch08' },
            { text: '09 用 AI 生成用例', link: '/chapters/ch09' },
            { text: '10 requests 发请求', link: '/chapters/ch10' },
            { text: '11 封装 HttpClient', link: '/chapters/ch11' },
            { text: '12 pytest 组织用例', link: '/chapters/ch12' },
            { text: '13 业务链路与数据', link: '/chapters/ch13' },
            { text: '14 报告与智能断言', link: '/chapters/ch14' },
            { text: '15 收口：框架成型', link: '/chapters/ch15' }
          ]
        },
        {
          text: '第三阶段 · Web 自动化',
          items: [
            { text: '16 浏览器基础与选择器', link: '/chapters/ch16' },
            { text: '17 页面对象（PO）', link: '/chapters/ch17' },
            { text: '18 定位集中管理', link: '/chapters/ch18' },
            { text: '19 前后置与浏览器复用', link: '/chapters/ch19' },
            { text: '20 数据驱动与多用例', link: '/chapters/ch20' },
            { text: '21 视觉回归与可访问性', link: '/chapters/ch21' },
            { text: '22 用 AI 生成 Web 用例', link: '/chapters/ch22' },
            { text: '23 框架收口（CLI）', link: '/chapters/ch23' }
          ]
        },
        {
          text: '第四阶段 · APP 终端 UI 自动化',
          items: [
            { text: '24 ADB 与设备连接', link: '/chapters/ch24' },
            { text: '25 元素定位与窗口树', link: '/chapters/ch25' },
            { text: '26 页面对象与页面栈', link: '/chapters/ch26' },
            { text: '27 手势与输入', link: '/chapters/ch27' },
            { text: '28 数据驱动与多用例', link: '/chapters/ch28' },
            { text: '29 稳定性与失败留证', link: '/chapters/ch29' },
            { text: '30 logcat 与崩溃定位', link: '/chapters/ch30' },
            { text: '31 框架收口（APP CLI）', link: '/chapters/ch31' },
          ]
        },
        {
          text: '第五阶段 · 性能测试',
          items: [
            { text: '32 性能测试基础与指标', link: '/chapters/ch32' },
            { text: '33 场景设计：基准与负载', link: '/chapters/ch33' },
            { text: '34 压测脚本与参数化', link: '/chapters/ch34' },
            { text: '35 结果分析与瓶颈定位', link: '/chapters/ch35' },
            { text: '36 中间件性能要点', link: '/chapters/ch36' },
            { text: '37 全链路压测与隔离', link: '/chapters/ch37' },
            { text: '38 AI 辅助性能分析', link: '/chapters/ch38' },
            { text: '39 性能平台收口', link: '/chapters/ch39' },
          ]
        },
        {
          text: '第六阶段 · AI 测试平台与工具',
          items: [
            { text: '40 平台架构与最小可用', link: '/chapters/ch40' },
            { text: '41 项目配置与环境上下文', link: '/chapters/ch41' },
            { text: '42 接口资产与一致性校验', link: '/chapters/ch42' },
            { text: '43 用例与关键字执行器', link: '/chapters/ch43' },
            { text: '44 测试计划与异步执行', link: '/chapters/ch44' },
            { text: '45 平台收口', link: '/chapters/ch45' },
          ]
        },
        {
          text: '延伸阅读',
          items: [
            { text: '接口自动化面试题（带答案）', link: '/kb/interview-api' },
            { text: '内容更新规则', link: '/kb/rules' }
          ]
        }
      ],
      '/labs/': [
        {
          text: '实操记录',
          items: [
            { text: '实操总览', link: '/labs/' },
            { text: '在线运行 playground', link: '/labs/playground' }
          ]
        },
        {
          text: '第一阶段 · Python 与工程基础',
          items: [
            { text: '01 基础语法', link: '/chapters/ch01' },
            { text: '02 条件与循环', link: '/chapters/ch02' },
            { text: '03 容器与推导式', link: '/chapters/ch03' },
            { text: '04 函数进阶', link: '/chapters/ch04' },
            { text: '05 面向对象', link: '/chapters/ch05' },
            { text: '06 标准库与异常', link: '/chapters/ch06' },
            { text: '07 数据工具箱', link: '/chapters/ch07' }
          ]
        },
        {
          text: '第二阶段 · 接口自动化',
          items: [
            { text: '08 接口基础', link: '/chapters/ch08' },
            { text: '09 AI 生成用例', link: '/chapters/ch09' },
            { text: '10 requests', link: '/chapters/ch10' },
            { text: '11 HttpClient', link: '/chapters/ch11' },
            { text: '12 pytest 组织', link: '/chapters/ch12' },
            { text: '13 业务链路', link: '/chapters/ch13' },
            { text: '14 报告与断言', link: '/chapters/ch14' },
            { text: '15 框架收口', link: '/chapters/ch15' }
          ]
        },
        {
          text: '第三阶段 · Web 自动化',
          items: [
            { text: '16 浏览器基础', link: '/chapters/ch16' },
            { text: '17 页面对象', link: '/chapters/ch17' },
            { text: '18 定位管理', link: '/chapters/ch18' },
            { text: '19 前后置复用', link: '/chapters/ch19' },
            { text: '20 数据驱动', link: '/chapters/ch20' },
            { text: '21 视觉与可访问性', link: '/chapters/ch21' },
            { text: '22 AI 生成用例', link: '/chapters/ch22' },
            { text: '23 框架收口', link: '/chapters/ch23' }
          ]
        },
        {
          text: '第四阶段 · APP 终端 UI 自动化',
          items: [
            { text: '24 ADB 与设备连接', link: '/chapters/ch24' },
            { text: '25 元素定位与窗口树', link: '/chapters/ch25' },
            { text: '26 页面对象与页面栈', link: '/chapters/ch26' },
            { text: '27 手势与输入', link: '/chapters/ch27' },
            { text: '28 数据驱动与多用例', link: '/chapters/ch28' },
            { text: '29 稳定性与失败留证', link: '/chapters/ch29' },
            { text: '30 logcat 与崩溃定位', link: '/chapters/ch30' },
            { text: '31 框架收口（APP CLI）', link: '/chapters/ch31' },
          ]
        },
        {
          text: '第五阶段 · 性能测试',
          items: [
            { text: '32 性能测试基础与指标', link: '/chapters/ch32' },
            { text: '33 场景设计：基准与负载', link: '/chapters/ch33' },
            { text: '34 压测脚本与参数化', link: '/chapters/ch34' },
            { text: '35 结果分析与瓶颈定位', link: '/chapters/ch35' },
            { text: '36 中间件性能要点', link: '/chapters/ch36' },
            { text: '37 全链路压测与隔离', link: '/chapters/ch37' },
            { text: '38 AI 辅助性能分析', link: '/chapters/ch38' },
            { text: '39 性能平台收口', link: '/chapters/ch39' },
          ]
        },
        {
          text: '第六阶段 · AI 测试平台与工具',
          items: [
            { text: '40 平台架构与最小可用', link: '/chapters/ch40' },
            { text: '41 项目配置与环境上下文', link: '/chapters/ch41' },
            { text: '42 接口资产与一致性校验', link: '/chapters/ch42' },
            { text: '43 用例与关键字执行器', link: '/chapters/ch43' },
            { text: '44 测试计划与异步执行', link: '/chapters/ch44' },
            { text: '45 平台收口', link: '/chapters/ch45' },
          ]
        },
        {
          text: '延伸阅读',
          items: [
            { text: '接口自动化面试题（带答案）', link: '/kb/interview-api' },
            { text: '内容更新规则', link: '/kb/rules' }
          ]
        }
      ]
    },
    socialLinks: [{ icon: 'github', link: 'https://github.com/shenle2019/shenle-ai-qa' }],
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    darkModeSwitchLabel: '主题',
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '目录',
    lastUpdatedText: '最后更新'
  }
})
