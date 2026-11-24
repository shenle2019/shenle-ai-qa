import { defineConfig } from 'vitepress'

export default defineConfig({
  ignoreDeadLinks: true,
  lang: 'zh-CN',
  title: 'shenle · AI 测试全栈',
  description: '从 Python 基础到 AI 测试平台的完整学习与实践记录',
  base: '/shenle-ai-qa/',
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    logo: '/logo.svg',
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索', buttonAriaLabel: '搜索' },
          modal: {
            noResultsText: '没有找到结果，换个词试试',
            resetButtonTitle: '清空',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' }
          }
        }
      }
    },
    nav: [
      { text: '首页', link: '/' },
      { text: '测试全栈知识库', link: '/chapters/' },
      { text: '实操记录', link: '/labs/' },
      { text: '在线运行', link: '/labs/playground' },
    { text: 'Skills 库', link: '/skills/' },
      { text: 'GitHub', link: 'https://github.com/shenle2019/shenle-ai-qa' }
    ],
    sidebar: {
      '/chapters/': [
        {
          text: '第一阶段 · Python 与工程基础',
          items: [
            { text: '01 环境、第一个程序与基础语法', link: '/chapters/ch01' },
            { text: '02 条件、循环与函数入门', link: '/chapters/ch02' },
            { text: '03 列表、元组、字典与推导式', link: '/chapters/ch03' },
            { text: '04 函数进阶与内存模型', link: '/chapters/ch04' },
            { text: '05 面向对象与装饰器', link: '/chapters/ch05' },
            { text: '06 标准库、文件、JSON 与异常', link: '/chapters/ch06' },
            { text: '07 实战：测试数据工具箱', link: '/chapters/ch07' }
          ]
        },
        {
          text: '第二阶段 · 接口自动化',
          items: [
            { text: '08 接口与接口测试基础', link: '/chapters/ch08' },
            { text: '09 用 AI 生成接口用例（以及为什么不能全信）', link: '/chapters/ch09' },
            { text: '10 用 requests 发请求', link: '/chapters/ch10' },
            { text: '11 封装 HttpClient', link: '/chapters/ch11' },
            { text: '12 用 pytest 组织接口用例', link: '/chapters/ch12' },
            { text: '13 业务链路与数据准备', link: '/chapters/ch13' },
            { text: '14 报告与智能断言', link: '/chapters/ch14' },
            { text: '15 收口：一个能交给别人的框架', link: '/chapters/ch15' }
          ]
        },
        {
          text: '第三阶段 · Web 自动化',
          items: [
            { text: '16 浏览器自动化基础与选择器', link: '/chapters/ch16' },
            { text: '17 页面对象：把选择器关进类里', link: '/chapters/ch17' },
            { text: '18 定位集中管理：把选择器搬进配置文件', link: '/chapters/ch18' },
            { text: '19 前后置与浏览器复用', link: '/chapters/ch19' },
            { text: '20 数据驱动与多用例管理', link: '/chapters/ch20' },
            { text: '21 视觉回归与可访问性', link: '/chapters/ch21' },
            { text: '22 用 AI 生成 Web 用例（生成 → 校验 → 真跑）', link: '/chapters/ch22' },
            { text: '23 框架收口：一个能交给别人的 CLI', link: '/chapters/ch23' }
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
            { text: '29 稳定性：等待、重试与失败留证', link: '/chapters/ch29' },
            { text: '30 用 logcat 定位崩溃与 ANR', link: '/chapters/ch30' },
            { text: '31 框架收口：一个能交给别人的 APP CLI', link: '/chapters/ch31' },
          ]
        },
        {
          text: '第五阶段 · 性能测试',
          items: [
            { text: '32 性能测试基础与指标', link: '/chapters/ch32' },
            { text: '33 场景设计：基准、负载、压力、稳定性', link: '/chapters/ch33' },
            { text: '34 压测脚本与参数化', link: '/chapters/ch34' },
            { text: '35 结果分析与瓶颈定位', link: '/chapters/ch35' },
            { text: '36 中间件性能要点', link: '/chapters/ch36' },
            { text: '37 全链路压测与数据隔离', link: '/chapters/ch37' },
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
            { text: '45 平台收口：报告、门槛与部署', link: '/chapters/ch45' },
            { text: '46 AI 测试 Skills 与工具链落地', link: '/chapters/ch46' },
          ]
        },
        {
          text: '延伸阅读',
          items: [
            { text: 'Skills 库（可预览下载）', link: '/skills/' },
            { text: 'Skills 手册（全部技能）', link: '/kb/skills/' },
            { text: 'Skills 单跑记录', link: '/labs/skills/' },
            { text: '接口自动化面试题（带答案）', link: '/kb/interview-api' },
            { text: '内容更新规则', link: '/kb/rules' },
            { text: '知识库索引', link: '/kb/' }
          ]
        }
      ],
      '/labs/': [
        {
          text: 'Skills 单跑记录',
          items: [{ text: 'Skills 单跑记录', link: '/labs/skills/' }]
        },
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
            { text: '01 环境、第一个程序与基础语法', link: '/chapters/ch01' },
            { text: '02 条件、循环与函数入门', link: '/chapters/ch02' },
            { text: '03 列表、元组、字典与推导式', link: '/chapters/ch03' },
            { text: '04 函数进阶与内存模型', link: '/chapters/ch04' },
            { text: '05 面向对象与装饰器', link: '/chapters/ch05' },
            { text: '06 标准库、文件、JSON 与异常', link: '/chapters/ch06' },
            { text: '07 实战：测试数据工具箱', link: '/chapters/ch07' }
          ]
        },
        {
          text: '第二阶段 · 接口自动化',
          items: [
            { text: '08 接口与接口测试基础', link: '/chapters/ch08' },
            { text: '09 用 AI 生成接口用例（以及为什么不能全信）', link: '/chapters/ch09' },
            { text: '10 用 requests 发请求', link: '/chapters/ch10' },
            { text: '11 封装 HttpClient', link: '/chapters/ch11' },
            { text: '12 用 pytest 组织接口用例', link: '/chapters/ch12' },
            { text: '13 业务链路与数据准备', link: '/chapters/ch13' },
            { text: '14 报告与智能断言', link: '/chapters/ch14' },
            { text: '15 收口：一个能交给别人的框架', link: '/chapters/ch15' }
          ]
        },
        {
          text: '第三阶段 · Web 自动化',
          items: [
            { text: '16 浏览器自动化基础与选择器', link: '/chapters/ch16' },
            { text: '17 页面对象：把选择器关进类里', link: '/chapters/ch17' },
            { text: '18 定位集中管理：把选择器搬进配置文件', link: '/chapters/ch18' },
            { text: '19 前后置与浏览器复用', link: '/chapters/ch19' },
            { text: '20 数据驱动与多用例管理', link: '/chapters/ch20' },
            { text: '21 视觉回归与可访问性', link: '/chapters/ch21' },
            { text: '22 用 AI 生成 Web 用例（生成 → 校验 → 真跑）', link: '/chapters/ch22' },
            { text: '23 框架收口：一个能交给别人的 CLI', link: '/chapters/ch23' }
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
            { text: '29 稳定性：等待、重试与失败留证', link: '/chapters/ch29' },
            { text: '30 用 logcat 定位崩溃与 ANR', link: '/chapters/ch30' },
            { text: '31 框架收口：一个能交给别人的 APP CLI', link: '/chapters/ch31' },
          ]
        },
        {
          text: '第五阶段 · 性能测试',
          items: [
            { text: '32 性能测试基础与指标', link: '/chapters/ch32' },
            { text: '33 场景设计：基准、负载、压力、稳定性', link: '/chapters/ch33' },
            { text: '34 压测脚本与参数化', link: '/chapters/ch34' },
            { text: '35 结果分析与瓶颈定位', link: '/chapters/ch35' },
            { text: '36 中间件性能要点', link: '/chapters/ch36' },
            { text: '37 全链路压测与数据隔离', link: '/chapters/ch37' },
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
            { text: '45 平台收口：报告、门槛与部署', link: '/chapters/ch45' },
            { text: '46 AI 测试 Skills 与工具链落地', link: '/chapters/ch46' },
          ]
        },
        {
          text: '延伸阅读',
          items: [
            { text: 'Skills 库（可预览下载）', link: '/skills/' },
            { text: 'Skills 手册（全部技能）', link: '/kb/skills/' },
            { text: 'Skills 单跑记录', link: '/labs/skills/' },
            { text: '接口自动化面试题（带答案）', link: '/kb/interview-api' },
            { text: '内容更新规则', link: '/kb/rules' },
            { text: '知识库索引', link: '/kb/' }
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
    lastUpdated: false
  }
})
