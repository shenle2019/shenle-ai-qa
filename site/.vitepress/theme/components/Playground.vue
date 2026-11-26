<script setup>
import { onBeforeUnmount, ref } from 'vue'

/**
 * 一个页面上的所有 Playground 共用同一份 Pyodide 运行时。
 *
 * 注意：这里把状态挂在 window 上，而不是用模块级变量。
 * 实测模块级 let 在 VitePress 的页面 bundle 里每个组件实例各有一份，
 * 结果四个组件各下载一遍 pyodide.asm.wasm（约 10 MB × 4）。
 */
function runtimeStore() {
  if (!window.__pyodideShared) {
    window.__pyodideShared = { instance: null, loading: null }
  }
  return window.__pyodideShared
}

const PYODIDE_VERSION = '0.26.4'
// 自托管：10 MB 的 pyodide.asm.wasm 走 CDN 时，部分网络会被 QUIC 掐断
// （net::ERR_QUIC_PROTOCOL_ERROR → WebAssembly compilation aborted），
// 放在站点自己的 /pyodide/ 下走同源 HTTP/2，稳定得多。
const LOCAL_INDEX_URL = `${import.meta.env.BASE_URL}pyodide/v${PYODIDE_VERSION}/`
const CDN_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`
const RUNTIME_MB = 12
const SLOW_AFTER = 8
const GIVE_UP_AFTER = 120

const DEFAULT_CODE = `# 改这里，点「运行」
name = "李明"
scores = [85, 92, 78]
total = sum(scores)
print(f"{name} 的总分 {total}，平均 {total / len(scores):.1f}")
`

const props = defineProps({
  code: { type: String, default: '' },
  height: { type: Number, default: 220 },
})

const source = ref(props.code || DEFAULT_CODE)
const output = ref('')
const status = ref('idle') // idle | loading | running | done | error
const waited = ref(0)

let ticker = null
let giveUpTimer = null

function append(text) {
  output.value += text
}

function stopTicker() {
  if (ticker) clearInterval(ticker)
  ticker = null
}

/** 用 resource timing 读真实下载量，给用户看进度，而不是干等一圈圈转。 */
function downloadedMb() {
  try {
    const entries = performance.getEntriesByType('resource')
    let bytes = 0
    for (const e of entries) {
      if (e.name.includes('jsdelivr') || e.name.includes('pyodide')) {
        bytes += e.transferSize || e.encodedBodySize || 0
      }
    }
    return bytes / (1024 * 1024)
  } catch {
    return 0
  }
}

function startTicker() {
  stopTicker()
  waited.value = 0
  const startedAt = Date.now()
  ticker = setInterval(() => {
    waited.value = Math.round((Date.now() - startedAt) / 1000)
    if (waited.value >= SLOW_AFTER && waited.value % 5 === 0) {
      const mb = downloadedMb().toFixed(1)
      append(`还在下载（已下 ${mb} MB / 约 ${RUNTIME_MB} MB，慢网会更久）…\n`)
    }
  }, 1000)
}

/** 加载一段外部脚本，失败要能 reject（script 的 onerror 不会带原因）。 */
function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = src
    script.onload = resolve
    script.onerror = () => reject(new Error(`脚本加载失败：${src}`))
    document.head.appendChild(script)
  })
}

/** 全页共用一份运行时：window 上缓存，页面刷新即重置。 */
function loadRuntime(onProgress) {
  const store = runtimeStore()
  if (store.instance) return Promise.resolve(store.instance)
  if (store.loading) return store.loading

  onProgress()

  const ready = (async () => {
    if (!window.loadPyodide) {
      try {
        await loadScript(`${LOCAL_INDEX_URL}pyodide.js`)
      } catch {
        // 自托管文件被墙/缺失时退回 CDN，别让整页功能直接死掉
        await loadScript(`${CDN_INDEX_URL}pyodide.js`)
        return window.loadPyodide({ indexURL: CDN_INDEX_URL })
      }
    }
    return window.loadPyodide({ indexURL: LOCAL_INDEX_URL })
  })()

  const giveUp = new Promise((_, reject) => {
    giveUpTimer = setTimeout(() => {
      store.loading = null // 允许重试重新发起
      reject(
        new Error(
          `等 ${GIVE_UP_AFTER} 秒还没下载完，可能网络被挡住了。点「重试」再来一次，或换个网络。`
        )
      )
    }, GIVE_UP_AFTER * 1000)
  })

  store.loading = Promise.race([ready, giveUp])
    .then((instance) => {
      if (giveUpTimer) clearTimeout(giveUpTimer)
      giveUpTimer = null
      store.instance = instance
      return instance
    })
    .catch((error) => {
      if (giveUpTimer) clearTimeout(giveUpTimer)
      giveUpTimer = null
      store.loading = null
      throw error
    })

  return store.loading
}

async function run() {
  if (status.value === 'loading' || status.value === 'running') return
  output.value = ''
  try {
    const store = runtimeStore()
    const cold = !store.instance && !store.loading
    const instance = await loadRuntime(() => {
      if (cold) {
        status.value = 'loading'
        append('首次运行：正在下载 Python 运行时（约 10 MB，之后走浏览器缓存）…\n')
        startTicker()
      }
    })
    stopTicker()

    // 共用实例：每次运行前把输出重新绑到当前组件
    instance.setStdout({ batched: (line) => append(line + '\n') })
    instance.setStderr({ batched: (line) => append(line + '\n') })

    status.value = 'running'
    append('$ python main.py\n')
    await instance.runPythonAsync(source.value)
    status.value = 'done'
  } catch (error) {
    stopTicker()
    status.value = 'error'
    append(`\n${error.message || error}\n`)
  }
}

function reset() {
  stopTicker()
  output.value = ''
  status.value = 'idle'
}

function retry() {
  reset()
  run()
}

onBeforeUnmount(() => {
  stopTicker()
  if (giveUpTimer) clearTimeout(giveUpTimer)
})
</script>

<template>
  <div class="pg">
    <div class="pg-bar">
      <span class="pg-dot" :data-state="status" />
      <span class="pg-title">在浏览器里直接运行（CPython · WebAssembly）</span>
      <span class="pg-spacer" />
      <span v-if="status === 'loading' && waited >= SLOW_AFTER" class="pg-wait">
        已等 {{ waited }}s · 已下约 {{ downloadedMb().toFixed(1) }} MB
      </span>
      <button class="pg-btn ghost" type="button" @click="reset">清空输出</button>
      <button v-if="status === 'error'" class="pg-btn ghost" type="button" @click="retry">重试</button>
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
      <span v-else class="pg-hint">点「运行」看输出。首次会下载一次运行时（全页共用一份），之后秒开。</span>
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

.pg-wait {
  font-size: 12px;
  color: #b45309;
}
</style>
