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
