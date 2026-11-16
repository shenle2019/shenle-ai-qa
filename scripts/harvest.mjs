// 逐个抓取语雀文档 JSON（在浏览器内同源 fetch），落盘到 raw/。
// 用法: node harvest.mjs [--limit N] [--delay MS]
import fs from 'node:fs';
import path from 'node:path';

const USER_DATA = path.join(process.env.LOCALAPPDATA, 'Google', 'Chrome', 'User Data');
const BASE = path.resolve('..', 'corpus', 'yuque');
const RAW = path.join(BASE, 'raw');
const BOOK_ID = 73651885;

const args = process.argv.slice(2);
const argOf = (name, dflt) => {
  const i = args.indexOf(name);
  return i >= 0 ? Number(args[i + 1]) : dflt;
};
const LIMIT = argOf('--limit', Infinity);
const DELAY = argOf('--delay', 350);

function browserWs() {
  const raw = fs
    .readFileSync(path.join(USER_DATA, 'DevToolsActivePort'), 'utf8')
    .trim()
    .split(/\r?\n/);
  return `ws://127.0.0.1:${raw[0].trim()}${(raw[1] || '/devtools/browser').trim()}`;
}

function loadIds() {
  const wrapper = JSON.parse(fs.readFileSync(path.join(BASE, '_toc_raw.json'), 'utf8'));
  const inner = typeof wrapper.value === 'string' ? JSON.parse(wrapper.value) : wrapper;
  return inner.rows.map((r) => ({ id: r.id, title: r.t, slug: r.s }));
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  fs.mkdirSync(RAW, { recursive: true });
  const docs = loadIds();
  const todo = docs.filter((d) => !fs.existsSync(path.join(RAW, `${d.id}.json`))).slice(0, LIMIT);
  console.log(`total=${docs.length} pending=${todo.length}`);

  const ws = new WebSocket(browserWs());
  let seq = 0;
  const pending = new Map();
  await new Promise((res, rej) => {
    ws.onopen = res;
    ws.onerror = rej;
  });
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    }
  };
  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      const id = ++seq;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
    });

  const { targetInfos } = await send('Target.getTargets');
  const page = targetInfos.find((t) => t.type === 'page' && /yuque\.com/.test(t.url));
  if (!page) throw new Error('需要在浏览器里打开一个语雀标签页');
  const { sessionId } = await send('Target.attachToTarget', { targetId: page.targetId, flatten: true });
  await send('Runtime.enable', {}, sessionId);

  let ok = 0;
  let fail = 0;
  for (const doc of todo) {
    const expr = `(async () => {
      const r = await fetch('/api/docs/${doc.id}?book_id=${BOOK_ID}', { credentials: 'include', headers: { Accept: 'application/json' } });
      return JSON.stringify({ status: r.status, text: await r.text() });
    })()`;
    try {
      const { result } = await send(
        'Runtime.evaluate',
        { expression: expr, awaitPromise: true, returnByValue: true, timeout: 60000 },
        sessionId
      );
      const payload = JSON.parse(result.value);
      if (payload.status !== 200) throw new Error(`http ${payload.status}`);
      fs.writeFileSync(path.join(RAW, `${doc.id}.json`), payload.text, 'utf8');
      ok++;
    } catch (err) {
      fail++;
      console.log(`FAIL ${doc.id} ${doc.title.slice(0, 30)} :: ${err.message}`);
    }
    if ((ok + fail) % 20 === 0) console.log(`progress ${ok + fail}/${todo.length} ok=${ok} fail=${fail}`);
    await sleep(DELAY);
  }

  console.log(`DONE ok=${ok} fail=${fail} dir=${RAW}`);
  ws.close();
}

main().catch((err) => {
  console.error('FATAL', err);
  process.exit(1);
});
