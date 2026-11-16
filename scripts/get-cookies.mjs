// 从已开启远程调试的 Chrome 读取语雀 cookie，输出可直接用于 HTTP 请求的 Cookie 头。
import fs from 'node:fs';
import path from 'node:path';

const USER_DATA = path.join(process.env.LOCALAPPDATA, 'Google', 'Chrome', 'User Data');

function browserWs() {
  const raw = fs
    .readFileSync(path.join(USER_DATA, 'DevToolsActivePort'), 'utf8')
    .trim()
    .split(/\r?\n/);
  const port = raw[0].trim();
  const wsPath = (raw[1] || '/devtools/browser').trim();
  return `ws://127.0.0.1:${port}${wsPath}`;
}

async function main() {
  const ws = new WebSocket(browserWs());
  let id = 0;
  const pending = new Map();

  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      const msgId = ++id;
      pending.set(msgId, { resolve, reject });
      ws.send(JSON.stringify({ id: msgId, method, params, ...(sessionId ? { sessionId } : {}) }));
    });

  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });

  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    }
  };

  const { targetInfos } = await send('Target.getTargets');
  const page = targetInfos.find((t) => t.type === 'page' && /yuque\.com/.test(t.url)) || targetInfos.find((t) => t.type === 'page');
  if (!page) throw new Error('no page target');

  const { sessionId } = await send('Target.attachToTarget', { targetId: page.targetId, flatten: true });
  let cookies = [];
  try {
    ({ cookies } = await send('Network.getAllCookies', {}, sessionId));
  } catch (err) {
    ({ cookies } = await send('Storage.getCookies', {}, sessionId));
  }

  const yuque = cookies.filter((c) => /(^|\.)yuque\.com$/.test(c.domain));
  const header = yuque.map((c) => `${c.name}=${c.value}`).join('; ');

  fs.writeFileSync('cookies.txt', header, 'utf8');
  console.log(
    JSON.stringify(
      {
        page: page.url.slice(0, 80),
        total: cookies.length,
        yuque: yuque.length,
        names: yuque.map((c) => c.name),
        headerLength: header.length,
      },
      null,
      2
    )
  );

  ws.close();
}

main().catch((err) => {
  console.error('FAILED', err);
  process.exit(1);
});
