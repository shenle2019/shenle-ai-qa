import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import Playground from './components/Playground.vue'
import NotFound404 from './components/NotFound404.vue'
import LastUpdated from './components/LastUpdated.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    // 未知路径由主题内置 NotFound 渲染，这里把它换成中文页（含尾斜杠自动纠正）
    return h(DefaultTheme.Layout, null, {
      'not-found': () => h(NotFound404),
      'doc-footer-before': () => h(LastUpdated)
    })
  },
  enhanceApp({ app }) {
    app.component('Playground', Playground)
  }
} satisfies Theme
