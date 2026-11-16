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
          items: [{ text: '01 Python 入门与第一个 AI 程序', link: '/chapters/ch01' }]
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
