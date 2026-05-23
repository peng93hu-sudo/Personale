#!/usr/bin/env node
/*
 * Genera links.html scansionando tutte le pagine HTML del repository.
 * 自动扫描仓库里的 HTML 页面,生成导航页 links.html。
 *
 * Ogni pagina può dichiarare metadati opzionali nell'<head>:
 *   <meta name="description"  content="...">   → testo della scheda
 *   <meta name="nav-tag"      content="...">   → etichetta (badge)
 *   <meta name="nav-title"    content="...">   → titolo mostrato
 *   <meta name="nav-featured" content="true">  → scheda in evidenza
 * In assenza, si usano valori di default ragionevoli.
 */
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const SELF = "links.html";
const SKIP_DIRS = new Set([".git", ".github", "node_modules", "scripts"]);

function walk(dir, acc) {
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const rel = path.relative(ROOT, full);
    const st = fs.statSync(full);
    if (st.isDirectory()) {
      if (!SKIP_DIRS.has(name)) walk(full, acc);
    } else if (name.toLowerCase().endsWith(".html") && rel !== SELF) {
      acc.push(rel);
    }
  }
  return acc;
}

function metaContent(html, name) {
  const re = new RegExp(
    '<meta[^>]*\\bname=["\']' + name + '["\'][^>]*\\bcontent=["\']([^"\']*)["\']',
    "i"
  );
  const m = html.match(re);
  return m ? m[1].trim() : null;
}

function pageTitle(html) {
  const m = html.match(/<title>([\s\S]*?)<\/title>/i);
  return m ? m[1].replace(/\s+/g, " ").trim() : null;
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const files = walk(ROOT, []).sort();

const entries = files.map((rel) => {
  const html = fs.readFileSync(path.join(ROOT, rel), "utf8");
  const url = rel.split(path.sep).join("/");
  const isMap = /Mappa_Rete_Elettrica/i.test(url);
  const verMatch = url.match(/_v(\d+)/i);
  const ver = verMatch ? parseInt(verMatch[1], 10) : 0;
  return {
    file: url,
    title: metaContent(html, "nav-title") || pageTitle(html) || url,
    desc: metaContent(html, "description") || "本地 HTML 页面 / Pagina HTML.",
    tag: metaContent(html, "nav-tag") || (isMap ? "地图 · v" + (ver || "?") : "页面 / Pagina"),
    isMap,
    ver,
    featured: metaContent(html, "nav-featured") === "true",
  };
});

// Mette in evidenza la versione più recente della mappa.
const maps = entries.filter((e) => e.isMap);
if (maps.length) {
  maps.reduce((a, b) => (b.ver >= a.ver ? b : a)).featured = true;
}

entries.sort((a, b) => {
  if (a.featured !== b.featured) return a.featured ? -1 : 1;
  if (a.isMap !== b.isMap) return a.isMap ? -1 : 1;
  if (a.isMap && b.isMap) return b.ver - a.ver;
  return a.title.localeCompare(b.title);
});

const cards = entries
  .map(
    (e) => `      <a class="card${e.featured ? " featured" : ""}" href="${esc(e.file)}">
        <div class="card-top">
          <h2>${esc(e.title)}</h2>
          <span class="tag">${esc(e.tag)}</span>
        </div>
        <p>${esc(e.desc)}</p>
        <span class="go">打开 / Apri →</span>
      </a>`
  )
  .join("\n");

const body = entries.length ? cards : '      <p class="empty">暂无页面 / Nessuna pagina</p>';

const page = `<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>WiseGlow · Portale / 页面导航</title>
<!-- AUTO-GENERATO da scripts/build-index.js — non modificare a mano / 自动生成,请勿手改 -->
<style>
  :root{--bg:#0e1116;--panel:#161b22;--border:#2a323d;--text:#e6edf3;--muted:#8b949e;--accent:#58a6ff;}
  *{box-sizing:border-box;}
  html,body{margin:0;min-height:100%;background:var(--bg);color:var(--text);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;}
  header{padding:1.6rem 1.5rem 1rem;max-width:1000px;margin:0 auto;}
  header h1{margin:0;font-size:1.5rem;color:var(--accent);}
  header .sub{margin:.35rem 0 0;color:var(--muted);font-size:.92rem;}
  main{max-width:1000px;margin:0 auto;padding:.5rem 1.5rem 2rem;
    display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1rem;}
  .card{display:flex;flex-direction:column;gap:.5rem;text-decoration:none;color:inherit;
    background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:1.1rem 1.2rem;
    transition:transform .12s,border-color .12s,box-shadow .12s;}
  .card:hover{transform:translateY(-3px);border-color:var(--accent);box-shadow:0 8px 24px rgba(0,0,0,.35);}
  .card:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
  .card.featured{grid-column:1 / -1;background:linear-gradient(135deg,#15263b,#161b22);}
  .card-top{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;justify-content:space-between;}
  .card h2{margin:0;font-size:1.1rem;}
  .tag{font-size:.7rem;padding:.12rem .55rem;border:1px solid var(--accent);color:var(--accent);
    border-radius:999px;white-space:nowrap;}
  .card p{margin:.1rem 0 0;color:var(--muted);font-size:.86rem;line-height:1.5;}
  .card .go{margin-top:.5rem;font-size:.82rem;color:var(--accent);font-weight:600;}
  .empty{grid-column:1/-1;color:var(--muted);text-align:center;padding:2rem;}
  footer{max-width:1000px;margin:0 auto;padding:0 1.5rem 2rem;color:var(--muted);
    font-size:.74rem;line-height:1.5;border-top:1px solid var(--border);}
  footer .ft-inner{padding-top:1rem;}
</style>
</head>
<body>
<header>
  <h1>WiseGlow Italia · Portale</h1>
  <p class="sub">项目页面导航 — 自动扫描仓库 HTML 生成 / Indice auto-generato (${entries.length} pagine)</p>
</header>
<main>
${body}
</main>
<footer><div class="ft-inner">
  数据指示性,需以 Terna / e-distribuzione 校核。本页由 GitHub Action 自动扫描生成。<br>
  Pagina generata automaticamente da GitHub Actions · WiseGlow Italia
</div></footer>
</body>
</html>
`;

fs.writeFileSync(path.join(ROOT, SELF), page);
console.log("links.html generato: " + entries.length + " pagine ->", entries.map((e) => e.file).join(", "));
