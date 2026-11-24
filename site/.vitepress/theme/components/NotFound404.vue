<script setup>
import { onMounted } from 'vue'

// VitePress 的未知路径走主题内置 NotFound，404.md 里那段脚本不会执行，
// 所以中文文案 + 出口 + 尾斜杠纠正都放在这个组件里，由 theme/index.ts 挂到 not-found 插槽。
onMounted(() => {
  if (typeof window === 'undefined') return
  const { pathname, origin, search } = window.location
  const bare = pathname.replace(/\/+$/, '')
  const inSite = pathname.startsWith('/shenle-ai-qa')

  // /chapters/ch01/ 这种多一个斜杠的地址，先纠一次再决定显示什么
  if (inSite && pathname !== bare) {
    window.location.replace(origin + bare + search)
    return
  }

  const el = document.getElementById('nf-path')
  if (el) el.textContent = pathname
})
</script>

<template>
  <div class="nf">
    <p class="nf-code">404</p>
    <h1 class="nf-title">这个地址没有页面</h1>
    <p class="nf-desc">
      可能是地址拼错了，也可能是内容挪了位置。你要找的是
      <code id="nf-path">这个地址</code>
    </p>
    <div class="nf-actions">
      <a class="nf-btn nf-primary" href="/shenle-ai-qa/chapters/">去知识库</a>
      <a class="nf-btn" href="/shenle-ai-qa/labs/">看实操</a>
      <a class="nf-btn" href="/shenle-ai-qa/skills/">Skills 库</a>
      <a class="nf-btn" href="/shenle-ai-qa/">回首页</a>
    </div>
    <p class="nf-tip">找不到就看一眼 <a href="/shenle-ai-qa/kb/">知识库索引</a>。</p>
  </div>
</template>

<style scoped>
.nf {
  max-width: 640px;
  margin: 14vh auto 0;
  text-align: center;
  padding: 0 24px;
}
.nf-code {
  font-size: 64px;
  font-weight: 700;
  line-height: 1;
  margin: 0;
  color: var(--vp-c-brand-1);
  letter-spacing: 2px;
}
.nf-title {
  font-size: 26px;
  margin: 14px 0 10px;
  border: 0;
  padding: 0;
}
.nf-desc {
  color: var(--vp-c-text-2);
  margin: 0 0 26px;
  line-height: 1.7;
}
.nf-desc code {
  word-break: break-all;
}
.nf-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}
.nf-btn {
  padding: 8px 18px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 20px;
  font-size: 14px;
  color: var(--vp-c-text-1);
  text-decoration: none;
}
.nf-btn:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}
.nf-primary {
  background: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
  color: #fff;
}
.nf-primary:hover {
  background: var(--vp-c-brand-2);
  color: #fff;
}
.nf-tip {
  margin-top: 28px;
  font-size: 13px;
  color: var(--vp-c-text-3);
}
</style>
