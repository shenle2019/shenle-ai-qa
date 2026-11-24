# 明天开工：14 条发现的修复状态与做法

> 这份文件是 2026-11-23 晚的归档。原始发现见同目录 `FINDINGS.md`；
> 当时的实测数据见 `sessions.json` / `facts2.json` / `facts3.json`，截图在 `shots/`。
>
> **明天开工只需要说一句「开始修」**，按下面第 0 节的顺序执行即可。

## 0. 现在代码在哪

- 仓库：`E:\ailearning\shenle-ai-qa`，分支 `fix/site-explore-2026-11-23`（**未合并、未推送**，main 是干净的 `a24fd4c`）。
- 该分支上已有 6 条修好的改动 + 3 条半成品（见下表），`npm run build` 当时是通过的（11.82s）。
- 本地预览的正确姿势（**别直接 serve `dist`，`base` 是 `/shenle-ai-qa/`，会白屏**）：

  ```powershell
  cd E:\ailearning\shenle-ai-qa
  Remove-Item -Recurse -Force _site_preview -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force _site_preview\shenle-ai-qa | Out-Null
  Copy-Item -Recurse -Force site\.vitepress\dist\* _site_preview\shenle-ai-qa
  node scripts/serve-preview.mjs ./_site_preview 5210
  # 访问 http://127.0.0.1:5210/shenle-ai-qa/
  ```

  浏览器跑验证用仓库自带的 Playwright，必须带浏览器路径：

  ```powershell
  $env:PYTHONIOENCODING="utf-8"
  $env:PLAYWRIGHT_BROWSERS_PATH="E:\ailearning\shenle-ai-qa\.pw-browsers"
  .\.venv\Scripts\python.exe scripts\_verify_fixes.py
  ```

## 1. 逐条状态（14 条）

| # | 发现 | 状态 | 改在哪 |
| --- | --- | --- | --- |
| 1 | 全站无搜索 | ✅ 已修 | `site/.vitepress/config.mts` 的 `themeConfig.search` |
| 2 | playground 长时间无反馈 | ⚠️ 代码已写，未真跑 | `site/.vitepress/theme/components/Playground.vue` |
| 3 | 尾斜杠 404 | ❌ 未生效 | 想从 `site/404.md` 救，但 SPA 不执行 |
| 4 | 404 页全英文 | ❌ 未生效 | 同上，`site/404.md` 写了但未知路径不渲染它 |
| 5 | 同一技能两套 slug | ❌ 半通 | `scripts/_publish_skills.py` 生成了别名页，但跳转没发生 |
| 6 | 技能页无回手册链接 | ✅ 已修 | 同上脚本，页头加 `[Skills 手册 · <slug>]` |
| 7 | 侧栏「13 个技能」 | ✅ 已修 | `config.mts` 改「全部技能」 |
| 8 | 无 `/kb` 索引 | ✅ 已修 | 新建 `site/kb/index.md` |
| 9 | 美式日期 + 12 小时制 | ⚠️ 改了没验证 | `config.mts` 的 `lastUpdated.formatOptions`（`hour12:false`） |
| 10 | 章节标题与侧栏不一致 | ✅ 已修 | 脚本把 46 章侧栏文案对齐 `notes/chXX-*.md` 的 h1 |
| 11 | zip 直接触发下载 | ✅ 已修 | 文案改「下载 zip（SKILL.md+references）」 |
| 12 | 手册页对老技能无全文直链 | ✅ 已修 | 技能页回链 + `site/kb/skills/<dir>.md` 别名 |
| 13 | 首页 hero 与侧栏命名不同 | ⬜ 没动 | 建议改 `site/index.md` 的 CTA 文案与侧栏一致 |
| 14 | 空搜索容器错觉 | ✅ 随 #1 消失 | — |

## 2. 三条没修好的，具体怎么修（明天照做）

### #3 #4：404 页与尾斜杠

失败原因：VitePress 的 404 是 **SPA 兜底**——GitHub Pages 把未知路径喂给 `404.html`，页面挂载后渲染的是主题内置的 NotFound 组件，`site/404.md` 只在 `/404` 这条路由上生效，所以里面的 `<script setup>` 在「未知路径」场景根本不执行。

两条可行路线，选一条：

1. **主题层接管（推荐）**：在 `site/.vitepress/theme/index.ts` 里 `extends: DefaultTheme`，覆写 `NotFound` 布局：
   ```ts
   import { h } from 'vue'
   import DefaultTheme from 'vitepress/theme'
   import Custom404 from './components/Custom404.vue'
   export default {
     extends: DefaultTheme,
     Layout: () => h(DefaultTheme.Layout, null, { 'not-found': () => h(Custom404) })
   }
   ```
   `Custom404.vue` 里做三件事：中文文案、三个出口、`onMounted` 里判断 `location.pathname` 结尾是不是 `/`，是就 `location.replace(pathname.replace(/\/+$/, ''))` 纠斜杠。这样 #3 和 #4 一起解决，`site/404.md` 可以删掉。

2. **GitHub Pages 侧兜底**：在 `site/public/` 放一个 `404.html`，纯静态 HTML + 一段脚本纠斜杠；VitePress 构建不会编译 `public/` 下的 html。缺点是跟主题风格不一致，要手写样式。

### #5：别名页跳不过去

现状：`scripts/_publish_skills.py` 已生成 `site/skills/web-cli.md` 等 8 个别名页，内容是 `<p>正在跳到 …</p>` + `<script setup>window.location.replace(...)</script>`。构建产物里页面在，但浏览器里没跳。

两个可能原因，明天先确认再改：
- `layout: page` 下 `<script setup>` 可能没被 VitePress 编译进客户端 bundle（和 #4 同源问题）；
- 或者脚本跑了但 `target` 拼错（别名页写的是 `/shenle-ai-qa/skills/<dir>`，本地预览要看是否带前缀）。

稳的做法：别用 md 里的 script，改成 **主题层加一个 catch-all 路由**，或在 `_publish_skills.py` 里直接用 `site/public/skills/<short>/index.html`（静态重定向页，`public` 下的 html 不参与编译）：
```html
<meta http-equiv="refresh" content="0; url=/shenle-ai-qa/skills/shenle-web-cli">
<a href="/shenle-ai-qa/skills/shenle-web-cli">继续前往 shenle-web-cli</a>
```
注意 `public/skills/<short>/index.html` 与 `site/skills/<short>.md` 会撞路由，二选一。

### #2：playground 超时（代码已写，需真跑一次）

改法已落地：`SLOW_AFTER = 12` 秒打「还在下载…」、`GIVE_UP_AFTER = 45` 秒判失败出「重试」、`startTicker/stopTicker` 计时、模板里 `<span class="pg-wait">已等 Xs</span>`。

明天只需要：`site/labs/playground` 页面点一次「运行」（按钮在 `<details>` 折叠块里，**要先展开**，否则 Playwright 报 `element is not visible`），等 50 秒，确认失败文案与「重试」按钮出现。若 45 秒内成功加载，则把 `GIVE_UP_AFTER` 调到 60 秒避免误杀。

## 3. 修完的收尾动作

```powershell
cd E:\ailearning\shenle-ai-qa\site
npm run build          # 期待 build complete，无 dead link 报错
cd ..
# 起预览 → 跑 scripts\_verify_fixes.py 全绿
git add -A
git commit -m "fix(site): 探索清单 14 条"
git checkout main && git merge fix/site-explore-2026-11-23 --ff-only
git push origin main   # GitHub Actions 会自动部署 Pages
# 等 1-2 分钟后线上复核：
#   /skills/ /skills/web-cli /kb/ /chapters/ch01/ /zzz-missing
```

## 4. 别忘的两个连带项

- 站点内容一改，平台侧（ai-qa-lab）的 `apps/sut/backend/app/skill_docs/` 与 `zips/` 是**快照拷贝**，要重新同步并 `railway up --ci`。
- 那份 `docs/skill-scores.json` / `docs/skill-scores.md` 也要跟着重算（`scripts/_score_skills.py`、`_score_ledger.py`），否则站点分数表与技能正文会脱节。


---

## 完工记录（2026-11-24 上午）

14 条全部落地，本地构建 11.67s 通过，scripts/_verify_fixes.py 全绿：

| 项 | 修法 | 实测 |
| --- | --- | --- |
| #3 尾斜杠 | 	heme/components/NotFound404.vue 的 onMounted 里纠斜杠（主题层 not-found 插槽，404.md 已删） | /chapters/ch01/ → /chapters/ch01 |
| #4 404 中文 | 同上，	heme/index.ts 用 h(DefaultTheme.Layout, null, {'not-found': ...}) | 标题「这个地址没有页面」+ 四出口 |
| #5 slug 别名 | _publish_skills.py 改写 site/public/skills/<short>/index.html 静态 meta refresh | /skills/web-cli → /skills/shenle-web-cli；/kb/skills/<dir> 同样可开 |
| #2 playground | SLOW_AFTER=12 / GIVE_UP_AFTER=45 + 计时提示 + 「重试」 | 12s 提示「还在下载」，45s 失败文案 + 重试按钮 |
| #9 日期 | 关掉主题 lastUpdated，自己写 LastUpdated.vue 走 zh-CN + Asia/Shanghai + 24h | 最后更新：2026/11/20 18:13 |
| #13 首页命名 | hero 四个 action 与导航同名 | 从第一章开始（知识库）/ 看实操记录 / 在线运行 / Skills 库 |

预览用的 scripts/serve-preview.mjs 也补了 cleanUrls（/chapters/ch01 → .html）、目录 index、以及子路径下的 404.html 兜底，否则本地看到的现象跟 GitHub Pages 不一致。
