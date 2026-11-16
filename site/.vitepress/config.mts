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
      { text: '章节', link: '/chapters/' },
      { text: '实验', link: '/labs/' },
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
        }
      ],
      '/labs/': [
        {
          text: '实验',
          items: [
            { text: '实验总览', link: '/labs/' },
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
