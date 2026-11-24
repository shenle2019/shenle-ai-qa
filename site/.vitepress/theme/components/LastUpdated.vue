<script setup>
import { computed } from 'vue'
import { useData } from 'vitepress'

// 主题自带的「最后更新」用构建机 locale 格式化，会变成 11/20/2026；
// 这里自己按 zh-CN + 24 小时制 + 东八区输出，读起来跟全站一致。
const { page } = useData()

const stamp = computed(() => {
  const ts = page.value?.lastUpdated
  if (!ts) return ''
  return new Date(ts).toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
})
</script>

<template>
  <p v-if="stamp" class="lu">最后更新：{{ stamp }}</p>
</template>

<style scoped>
.lu {
  margin: 0;
  padding: 8px 0 0;
  font-size: 12px;
  color: var(--vp-c-text-3);
}
</style>
