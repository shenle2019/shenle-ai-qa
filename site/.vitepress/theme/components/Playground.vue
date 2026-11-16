<script setup>
import { onBeforeUnmount, ref } from 'vue'

const props = defineProps({
  code: { type: String, default: '' },
  height: { type: Number, default: 220 },
})

const source = ref(props.code || SAMPLE)
const output = ref('')
const status = ref('idle') // idle | loading | running | done | error
const pyodide = ref(null)

const PYODIDE_VERSION = '0.26.4'
const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`

function append(text) {
  output.value += text
}

async function ensurePyodide() {
  if (pyodide.value) return pyodide.value
  status.value = 'loading'
  append('首次运行：正在下载 Python 运行时（约 10 MB，之后走浏览器缓存）…\n')

  await new Promise((resolve, reject) => {
    if (window.loadPyodide) return resolve()
    const script = document.createElement('script')
    script.src = `${INDEX_URL}pyodide.js`
    script.onload = resolve
    script.onerror = () => reject(new Error('运行时下载失败，检查网络后重试'))
    document.head.appendChild(script)
  })

  const instance = await window.loadPyodide({ indexURL: INDEX_URL })
  instance.setStdout({ batched: (line) => append(line + '\n') })
  instance.setStderr({ batched: (line) => append(line + '\n') })
  pyodide.value = instance
  append('运行时就绪。\n\n')
  return instance
}

async function run() {
  if (status.value === 'loading' || status.value === 'running') return
  output.value = ''
  try {
    const instance = await ensurePyodide()
    status.value = 'running'
    append('$ python main.py\n')
    await instance.runPythonAsync(source.value)
    status.value = 'done'
  } catch (error) {
    status.value = 'error'
    append(`\n${error.message || error}\n`)
  }
}

function reset() {
  output.value = ''
  status.value = pyodide.value ? 'idle' : 'idle'
}

onBeforeUnmount(() => {
  pyodide.value = null
})

const SAMPLE = `# 改这里，点「运行」
name = "李明"
scores = [85, 92, 78]
total = sum(scores)
print(f"{name} 的总分 {total}，平均 {total / len(scores):.1f}")
`
</script>

<template>
  <div class="pg">
    <div class="pg-bar">
      <span class="pg-dot" :data-state="status" />
      <span class="pg-title">在浏览器里直接运行（CPython · WebAssembly）</span>
      <span class="pg-spacer" />
      <button class="pg-btn ghost" type="button" @click="reset">清空输出</button>
      <button class="pg-btn" type="button" :disabled="status === 'loading' || status === 'running'" @click="run">
        {{ status === 'loading' ? '加载中…' : status === 'running' ? '运行中…' : '运行' }}
      </button>
    </div>

    <textarea
      v-model="source"
      class="pg-code"
      spellcheck="false"
      :style="{ height: height + 'px' }"
      aria-label="Python 代码"
    />

    <div class="pg-out" :data-state="status" aria-live="polite">
      <template v-if="output">{{ output }}</template>
      <span v-else class="pg-hint">点「运行」看输出。首次会下载一次运行时，之后秒开。</span>
    </div>
  </div>
</template>

<style scoped>
.pg {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  overflow: hidden;
  margin: 20px 0;
  background: var(--vp-c-bg-soft);
}

.pg-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
  font-size: 12.5px;
  color: var(--vp-c-text-2);
}

.pg-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--vp-c-text-3);
}

.pg-dot[data-state='loading'],
.pg-dot[data-state='running'] {
  background: #f59e0b;
}

.pg-dot[data-state='done'] {
  background: #16a34a;
}

.pg-dot[data-state='error'] {
  background: #dc2626;
}

.pg-title {
  font-weight: 600;
}

.pg-spacer {
  flex: 1;
}

.pg-btn {
  padding: 5px 12px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: var(--vp-button-brand-bg);
  color: #fff;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}

.pg-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pg-btn.ghost {
  background: transparent;
  color: var(--vp-c-text-2);
  border-color: var(--vp-c-divider);
}

.pg-code {
  display: block;
  width: 100%;
  border: 0;
  padding: 12px 14px;
  resize: vertical;
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  line-height: 1.65;
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-alt);
  outline: none;
}

.pg-out {
  margin: 0;
  padding: 12px 14px;
  min-height: 68px;
  max-height: 320px;
  overflow: auto;
  border-top: 1px solid var(--vp-c-divider);
  background: #0f172a;
  color: #e2e8f0;
  font-family: var(--vp-font-family-mono);
  font-size: 12.5px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.pg-out[data-state='error'] {
  color: #fca5a5;
}

.pg-hint {
  color: #94a3b8;
}
</style>
