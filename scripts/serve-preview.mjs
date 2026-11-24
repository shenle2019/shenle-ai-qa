// Minimal static server for previewing the built site the way GitHub Pages serves it.
// Usage: node scripts/serve-preview.mjs <root> <port>
import { createServer } from 'node:http'
import { readFile, stat } from 'node:fs/promises'
import { extname, join, normalize } from 'node:path'

const root = process.argv[2] ?? '.'
const port = Number(process.argv[3] ?? 5200)

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.woff2': 'font/woff2',
  '.ico': 'image/x-icon'
}

createServer(async (req, res) => {
  try {
    const url = decodeURIComponent((req.url ?? '/').split('?')[0])
    let file = join(root, normalize(url))
    let info = await stat(file).catch(() => null)
    // cleanUrls：/chapters/ch01 要落到 chapters/ch01.html
    if (!info && !extname(file)) {
      const asHtml = `${file}.html`
      const htmlInfo = await stat(asHtml).catch(() => null)
      if (htmlInfo) {
        file = asHtml
        info = htmlInfo
      }
    }
    // 目录写成 /skills/web-cli 时也要落到 web-cli/index.html（GitHub Pages 会 301 补斜杠）
    if (!info) {
      const asIndex = join(file, 'index.html')
      const indexInfo = await stat(asIndex).catch(() => null)
      if (indexInfo) {
        file = asIndex
        info = indexInfo
      }
    }
    if (!info || info.isDirectory()) {
      file = join(file, 'index.html')
    }
    const body = await readFile(file)
    res.writeHead(200, { 'Content-Type': TYPES[extname(file)] ?? 'application/octet-stream' })
    res.end(body)
  } catch {
    // GitHub Pages 对未知路径会回 404.html；站点在子路径下时要找 <base>/404.html
    try {
      const seg = (req.url ?? '/').split('?')[0].split('/').filter(Boolean)[0] ?? ''
      const candidates = [join(root, '404.html'), join(root, seg, '404.html')]
      let body = null
      for (const candidate of candidates) {
        body = await readFile(candidate).catch(() => null)
        if (body) break
      }
      if (!body) throw new Error('no 404 page')
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' })
      res.end(body)
    } catch {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
      res.end('404')
    }
  }
}).listen(port, '127.0.0.1', () => {
  console.log(`serving ${root} at http://127.0.0.1:${port}/`)
})
