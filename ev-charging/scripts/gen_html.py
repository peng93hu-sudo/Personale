#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成决策人看板 web/index.html(单文件、无外部依赖)。
读取 data/research.json(必需)与 data/business.json(可选,业务线完成后)。
看板呈现:核心逻辑→要点→分析结果→分析流程→各Agent核心要点与参数,并提供调参说明。"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "data", "research.json")
BIZ = os.path.join(ROOT, "data", "business.json")
OUT = os.path.join(ROOT, "web", "index.html")

R = json.load(open(RES))
B = json.load(open(BIZ)) if os.path.exists(BIZ) else None
meta, syn, dims = R["meta"], R["synthesis"], R["dimensions"]


def e(s):
    return html.escape(str(s if s is not None else ""))


# ---- red team tally ----
tally = {"verified": 0, "partially": 0, "unverified": 0, "contradicted": 0}
nsrc = 0
for x in dims:
    nsrc += len(x["research"]["sources"])
    for c in x["redTeam"].get("checks", []):
        tally[c["verdict"]] = tally.get(c["verdict"], 0) + 1
total_checks = sum(tally.values())

DIMKEY = {"policy": "政策法规", "market": "市场规模", "tech": "技术标准", "players": "竞争格局",
          "business": "商业模式", "supply": "供应链", "ops": "运营用户"}

# ---- agent roster (framework) ----
RESEARCH_AGENTS = [
    ("R-PM", "调研PM", "调研线负责人", "定义维度·分派·收口·对接红军", "维度权重、时间窗(近24月)、地域权重(国内0.7/意0.3)"),
    ("R1", "政策法规Agent", "政策研究员", "国内规划/补贴/准入 + 欧盟AFIR/PNRR/GSE", "补贴金额、强制配建比例、合规门槛"),
    ("R2", "市场规模Agent", "市场分析师", "保有量/车桩比/增长/市场规模/预测", "公共私人直流占比、CAGR、口径一致性"),
    ("R3", "技术标准Agent", "技术研究员", "功率/超充/标准(GB/T vs CCS2)/V2G", "功率等级、协议、互认、液冷/SiC"),
    ("R4", "竞争格局Agent", "行业分析师", "国内外CPO与设备商/市占/融资", "桩数、市占率、融资额、扩张计划"),
    ("R5", "商业模式Agent", "商业分析师", "盈利模型/回收期/盈亏平衡", "利用率、电价价差、回收期、毛利"),
    ("R6", "供应链成本Agent", "供应链研究员", "模块/IGBT/SiC/枪线/BOM/出海认证", "BOM占比、CE/RED认证、关税"),
    ("R7", "运营用户Agent", "运营研究员", "利用率/充电行为/痛点/漫游互联", "利用率%、充电时长、痛点频次"),
    ("R-SYN", "综合Agent", "首席综合官", "跨7维度综合为决策结论+机会点", "置信度、口径冲突调和、机会优先级"),
]
BIZ_AGENTS = [
    ("B-PM", "业务PM", "业务线负责人", "把调研机会变成可成交业务设计·日更成果物", "毛利、回收期、可成交性、合规"),
    ("B1", "机制设计Agent", "机制设计师", "撮合/分润/定价/风控/履约机制", "分润比例、账期、违约、定价锚"),
    ("B2", "源头/货源Agent", "采购/寻源", "找产品/货物/服务的源(厂商/品牌)", "价格、产能、认证、MOQ、交期"),
    ("B3", "客户/成交方Agent", "BD/市场", "找需求侧(CPO/车企/地产/分销)", "采购量、付费意愿、决策链、痛点"),
    ("B4", "商业模式模拟Agent", "商业建模师", "多候选模式建模打分选最优", "单位经济、现金流、壁垒、可复制"),
    ("B5", "流程设计Agent", "流程/交付", "设计源→中间→客户成交流程", "环节数、周期、卡点、转化率"),
    ("B6", "成果物Agent", "产品经理", "把方案落成产品本身(清单/报价/落地页)", "成果物类型、完成度、可交付性"),
]

CSS = """
:root{--bg:#0d1117;--card:#161b22;--card2:#1c2330;--bd:#2d333b;--fg:#e6edf3;--mut:#8b949e;
--cn:#e34c4c;--it:#3b82f6;--ok:#2ea043;--warn:#d29922;--bad:#da3633;--part:#bb8009;--ac:#58a6ff;--vio:#a371f7;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg);line-height:1.65}
a{color:var(--ac);text-decoration:none}a:hover{text-decoration:underline}
header{padding:26px 22px;background:linear-gradient(135deg,#11151c,#1b2330);border-bottom:1px solid var(--bd)}
header h1{margin:0 0 6px;font-size:23px}
.sub{color:var(--mut);font-size:13px}
.badge{display:inline-block;background:var(--card2);border:1px solid var(--bd);border-radius:20px;padding:2px 11px;font-size:12px;margin:4px 6px 0 0;color:var(--mut)}
nav{position:sticky;top:0;z-index:10;display:flex;flex-wrap:wrap;gap:4px;background:#0d1117ee;backdrop-filter:blur(8px);padding:10px 16px;border-bottom:1px solid var(--bd)}
nav button{background:transparent;border:1px solid transparent;color:var(--mut);padding:7px 14px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600}
nav button:hover{color:var(--fg);background:var(--card)}
nav button.on{color:#fff;background:var(--card2);border-color:var(--bd)}
main{max-width:1180px;margin:0 auto;padding:22px 16px 80px}
section{display:none;animation:f .25s}section.on{display:block}
@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1}}
h2{font-size:20px;border-left:4px solid var(--ac);padding-left:11px;margin:30px 0 14px}
h3{font-size:16px;margin:20px 0 9px}
.grid{display:grid;gap:14px}
.kpis{grid-template-columns:repeat(auto-fit,minmax(135px,1fr))}
.kpi{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:15px}
.kpi .n{font-size:26px;font-weight:800}.kpi .l{color:var(--mut);font-size:12px;margin-top:3px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:17px;margin:12px 0}
.card.cn{border-left:3px solid var(--cn)}.card.it{border-left:3px solid var(--it)}
.flex{display:flex;gap:14px;flex-wrap:wrap}
.col{flex:1;min-width:300px}
table{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0}
th,td{border:1px solid var(--bd);padding:7px 9px;text-align:left;vertical-align:top}
th{background:var(--card2);color:var(--mut);font-weight:600}
td code,code{background:#0d1117;border:1px solid var(--bd);border-radius:4px;padding:1px 5px;font-size:12px;color:var(--vio)}
.bar{display:flex;height:13px;border-radius:7px;overflow:hidden;border:1px solid var(--bd);margin:6px 0;min-width:160px}
.bar span{display:block}
.b-ok{background:var(--ok)}.b-part{background:var(--part)}.b-un{background:#6e7681}.b-bad{background:var(--bad)}
.tag{display:inline-block;padding:1px 8px;border-radius:6px;font-size:12px;font-weight:600}
.t-ok{background:#1b3b24;color:#5ed47b}.t-part{background:#3a2f07;color:#e0b341}.t-un{background:#2d2d2d;color:#bbb}.t-bad{background:#3d1418;color:#ff7b7b}
.t-cn{background:#3a1414;color:#ff8a8a}.t-it{background:#10243f;color:#7db4f7}.t-go{background:#1b3b24;color:#5ed47b}.t-cond{background:#3a2f07;color:#e0b341}.t-no{background:#3d1418;color:#ff7b7b}
.chip{display:inline-block;background:var(--card2);border:1px solid var(--bd);border-radius:6px;padding:2px 9px;margin:2px;font-size:12px}
ul{margin:7px 0;padding-left:20px}li{margin:4px 0}
.muted{color:var(--mut);font-size:13px}
.flag{background:#2a1f07;border:1px solid #5c4708;border-radius:8px;padding:10px 13px;margin:8px 0;font-size:13px}
.score{display:inline-flex;gap:2px}.dot{width:9px;height:9px;border-radius:50%;background:#30363d}.dot.f{background:var(--ac)}
.note{background:var(--card2);border:1px solid var(--bd);border-left:3px solid var(--warn);border-radius:8px;padding:12px 14px;margin:12px 0;font-size:13px}
.diagram{font-family:ui-monospace,monospace;white-space:pre;background:#0d1117;border:1px solid var(--bd);border-radius:10px;padding:14px;overflow-x:auto;font-size:12px;color:#9fb1c4;line-height:1.5}
details{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:8px 14px;margin:10px 0}
summary{cursor:pointer;font-weight:600}
.pill{font-size:11px;padding:1px 7px;border-radius:5px;border:1px solid var(--bd);color:var(--mut)}
.rank{font-size:11px;font-weight:700;color:#fff;background:var(--ac);border-radius:5px;padding:1px 7px;margin-right:6px}
/* 打印/PDF模式:浅色主题、全部展开、隐藏导航(通过 ?print=1 触发) */
body.print{--bg:#fff;--card:#fff;--card2:#f3f5f8;--bd:#d3dae3;--fg:#1b2430;--mut:#5b6776}
body.print nav{display:none}
body.print header{background:#eef2f7}
body.print main{max-width:none}
body.print main>section{display:block!important;animation:none}
body.print main>section{border-top:2px solid var(--bd);margin-top:26px;padding-top:6px}
body.print details{border:none;padding:0}
body.print summary{display:none}
body.print h2{page-break-after:avoid}
body.print .card,body.print table,body.print details{page-break-inside:avoid}
"""


def bar(t):
    tot = max(sum(t.values()), 1)
    def pc(k):
        return round(t.get(k, 0) / tot * 100, 1)
    return (f'<div class="bar" title="✅{t.get("verified",0)} 🟡{t.get("partially",0)} ⚠️{t.get("unverified",0)} ❌{t.get("contradicted",0)}">'
            f'<span class="b-ok" style="width:{pc("verified")}%"></span>'
            f'<span class="b-part" style="width:{pc("partially")}%"></span>'
            f'<span class="b-un" style="width:{pc("unverified")}%"></span>'
            f'<span class="b-bad" style="width:{pc("contradicted")}%"></span></div>')


def dots(n, mx=5):
    return '<span class="score">' + "".join(f'<span class="dot {"f" if i < n else ""}"></span>' for i in range(mx)) + "</span>"


P = []
a = P.append

# ===== HEAD =====
a(f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>充电桩 调研×业务 多智能体看板</title><style>{CSS}</style></head><body>
<header>
<h1>⚡ 充电桩 调研×业务 多智能体决策看板</h1>
<div class="sub">{e(meta['scope'])} · 生成 {e(meta['generatedDate'])} · 调研RunID <code>{e(meta['runId'])}</code></div>
<div>
<span class="badge">🤖 调研 {e(meta['agentCount'])} Agent</span>
<span class="badge">🔢 {meta['totalTokens']:,} tokens</span>
<span class="badge">🛠 {e(meta['totalToolCalls'])} 工具调用</span>
<span class="badge">📚 {nsrc} 来源</span>
<span class="badge">🔴 红军核验 {total_checks} 条</span>
</div></header>
<nav>
<button class="on" onclick="go(0,this)">概览</button>
<button onclick="go(1,this)">体系/Agent</button>
<button onclick="go(2,this)">调研结论</button>
<button onclick="go(3,this)">七维度</button>
<button onclick="go(4,this)">业务PM线</button>
<button onclick="go(5,this)">来源/可追溯</button>
<button onclick="go(6,this)">调参引导</button>
</nav><main>""")

# ===== 0 概览 =====
a('<section class="on">')
a("<h2>核心可信度看板</h2><div class='grid kpis'>")
for n, l in [(len(dims), "调研维度"), (nsrc, "可点击来源"), (total_checks, "红军核验条目"),
             (tally["verified"], "✅ 已核实"), (tally["partially"], "🟡 部分核实"),
             (tally["unverified"], "⚠️ 未核实"), (tally["contradicted"], "❌ 被反驳")]:
    a(f'<div class="kpi"><div class="n">{n}</div><div class="l">{l}</div></div>')
a("</div>")
a('<div class="card"><b>红军反查分布</b>'+bar(tally)+'<div class="muted">绿=已核实 · 黄=部分 · 灰=未核实 · 红=被反驳。采用"有错直到被证明无误"原则,逐条打开来源核对。</div></div>')
a("<h2>执行摘要(面向决策人)</h2>")
a(f'<div class="card">{e(syn["executiveSummary"])}</div>')
a('<div class="flex">')
a(f'<div class="card cn col"><h3>🇨🇳 中国(主战场)</h3><div class="muted">{e(syn["chinaSnapshot"])}</div></div>')
a(f'<div class="card it col"><h3>🇮🇹 意大利(参照)</h3><div class="muted">{e(syn["italySnapshot"])}</div></div>')
a("</div>")
a("<h2>关键数字(带来源)</h2><table><tr><th>指标</th><th>数值</th><th>市场</th><th>来源</th></tr>")
mk = {"china": '<span class="tag t-cn">🇨🇳中国</span>', "italy": '<span class="tag t-it">🇮🇹意大利</span>', "global": '<span class="chip">🌐全球</span>'}
for kn in syn["keyNumbers"]:
    a(f'<tr><td>{e(kn["label"])}</td><td>{e(kn["value"])}</td><td>{mk.get(kn["market"],e(kn["market"]))}</td><td><code>{e(kn["sourceId"])}</code></td></tr>')
a("</table>")
a("<h2>跨市场洞察</h2><div class='card'><ul>")
for x in syn["crossCuttingInsights"]:
    a(f"<li>{e(x)}</li>")
a("</ul></div>")
a("<h2>关键风险</h2><div class='card'><ol>")
for x in syn["topRisks"]:
    a(f"<li>{e(x)}</li>")
a("</ol></div>")
a("</section>")

# ===== 1 体系 =====
a('<section>')
a("<h2>多智能体体系(双线 + 红军 + 文档可追溯)</h2>")
a('<div class="diagram">' + e(
"""最终决策人(你)  ── 调参 / 否决 ──┐
        ▲                          ▼
     决策简报             总PM(项目经理·编排者)
        │                 ┌─────────┴─────────┐
        │          调研PM线(每周)      业务PM线(每天)
        │          R1..R7 + 综合        B1..B6
        │                 └────────┬────────┘
        │                    红军 Red Team(每次更新都反查)
        └────────────────  文档与可追溯线(来源登记/报告/HTML)""") + "</div>")
a('<div class="note"><b>角色数 19</b> · 一次完整调研跑批实际 Agent 调用约 <b>15</b>(7研究+7红军+1综合)· 完整一轮(调研+业务)约 <b>27~30</b> 次调用。</div>')

a("<h3>🔵 调研PM线(每周刷新)</h3>")
a("<table><tr><th>编号</th><th>Agent</th><th>身份</th><th>角色/工作范畴</th><th>考虑的参数</th></tr>")
for c in RESEARCH_AGENTS:
    a(f"<tr><td><code>{e(c[0])}</code></td><td><b>{e(c[1])}</b></td><td>{e(c[2])}</td><td>{e(c[3])}</td><td class='muted'>{e(c[4])}</td></tr>")
a("</table>")
a("<h3>🟢 业务PM线(每天产出成果物)</h3>")
a("<table><tr><th>编号</th><th>Agent</th><th>身份</th><th>角色/工作范畴</th><th>考虑的参数</th></tr>")
for c in BIZ_AGENTS:
    a(f"<tr><td><code>{e(c[0])}</code></td><td><b>{e(c[1])}</b></td><td>{e(c[2])}</td><td>{e(c[3])}</td><td class='muted'>{e(c[4])}</td></tr>")
a("</table>")
a("<h3>🔴 红军 Red Team(贯穿两线·质量门)</h3>")
a('<div class="card">默认"有错直到被证明无误";逐条打开来源核对(verified/partially/unverified/contradicted),对商业模式做"杀死它"式压力测试。<b>红军未过 → PM 不发布。</b></div>')
a("<h3>三可标准 & 节奏</h3>")
a('<div class="flex"><div class="card col"><b>可查</b> 每个数字挂URL+出版方+日期<br><b>可验证</b> 红军实际打开来源核对<br><b>可追溯</b> 结论→数字→来源→红军裁决 全链路入库</div>')
a('<div class="card col"><b>调研</b> 每周一次(PM判断是否纳入新政策/玩家/模式)<br><b>业务</b> 每天一个成果物<br><b>红军</b> 每次更新都跑</div></div>')
a("</section>")

# ===== 2 调研结论 =====
a('<section>')
a("<h2>调研结论(综合)</h2>")
a(f'<div class="card">{e(syn["executiveSummary"])}</div>')
a("<h3>业务机会(已移交业务PM线)</h3><div class='card'><ol>")
for o in syn["businessOpportunities"]:
    a(f"<li>{e(o)}</li>")
a("</ol></div>")
a("<h3>整体置信度与数据局限(红军汇总)</h3>")
a(f'<div class="note">{e(syn["confidenceNote"])}</div>')
a("</section>")

# ===== 3 七维度 =====
a('<section>')
a("<h2>七维度详解(核心要点 · 红军反查)</h2>")
conf = {"high": "高", "medium": "中", "low": "低"}
vmap = {"verified": '<span class="tag t-ok">✅核实</span>', "partially": '<span class="tag t-part">🟡部分</span>',
        "unverified": '<span class="tag t-un">⚠️未核实</span>', "contradicted": '<span class="tag t-bad">❌反驳</span>'}
for x in dims:
    r, rt = x["research"], x["redTeam"]
    vt = {"verified": 0, "partially": 0, "unverified": 0, "contradicted": 0}
    for c in rt.get("checks", []):
        vt[c["verdict"]] = vt.get(c["verdict"], 0) + 1
    a(f'<div class="card"><h3>{e(x["name"])} <span class="pill">自评 {conf.get(r.get("selfConfidence"))} · 红军 {conf.get(rt.get("overallConfidence"))}</span></h3>')
    a(bar(vt))
    a('<div class="flex">')
    a(f'<div class="col"><b>🇨🇳 中国</b><div class="muted">{e(r["china"]["summary"])}</div></div>')
    a(f'<div class="col"><b>🇮🇹 意大利</b><div class="muted">{e(r["italy"]["summary"])}</div></div>')
    a("</div>")
    # comparison
    if r.get("comparison"):
        a("<details><summary>国内 vs 意大利 对照</summary><ul>")
        for c in r["comparison"]:
            a(f"<li>{e(c)}</li>")
        a("</ul></details>")
    # problem checks
    prob = [c for c in rt.get("checks", []) if c["verdict"] in ("contradicted", "unverified")]
    if prob:
        a("<details><summary>🔴 红军:被反驳/未核实条目</summary><table><tr><th>论断</th><th>裁决</th><th>说明</th></tr>")
        for c in prob:
            a(f'<tr><td>{e(c["claim"])}</td><td>{vmap[c["verdict"]]}</td><td class="muted">{e(c["note"])}</td></tr>')
        a("</table></details>")
    if rt.get("flaggedClaims"):
        a('<div class="flag">⚠️ 红军标记需谨慎:<ul>')
        for f in rt["flaggedClaims"]:
            a(f"<li>{e(f)}</li>")
        a("</ul></div>")
    a("</div>")
a("</section>")

# ===== 4 业务PM线 =====
a('<section>')
a("<h2>业务PM线(中国货源 → 意大利/欧盟市场)</h2>")
if not B:
    a('<div class="note">业务线工作流(business.workflow.js)完成后,此处展示:最优商业模式打分、找源/找客户成果、机制、流程与成果物、业务红军裁决。本轮先搭框架。</div>')
else:
    bm, bp, brt = B["model"], B["process"], B["redTeam"]
    rec = bm.get("recommended", {})
    a(f'<div class="card"><b>🏆 推荐商业模式:{e(rec.get("name",""))}</b><div class="muted">{e(rec.get("rationale",""))}</div>')
    if rec.get("conditions"):
        a("<div style='margin-top:6px'>成立前提:" + "".join(f'<span class="chip">{e(c)}</span>' for c in rec["conditions"]) + "</div>")
    a("</div>")
    # business red team verdict
    vd = brt.get("overallVerdict", "")
    vdc = {"go": "t-go", "conditional-go": "t-cond", "no-go": "t-no"}.get(vd, "t-part")
    a(f'<div class="note"><b>🔴 业务红军裁决:<span class="tag {vdc}">{e(vd)}</span></b>(置信度 {e(brt.get("confidence",""))})<br>单位经济:{e(brt.get("unitEconomicsCheck",""))}<br>合规:{e(brt.get("complianceCheck",""))}')
    if brt.get("conditions"):
        a("<ul>" + "".join(f"<li>{e(c)}</li>" for c in brt["conditions"]) + "</ul>")
    a("</div>")
    # candidate models scored
    a("<h3>候选商业模式打分(B4)</h3><table><tr><th>排名</th><th>模式</th><th>市场</th><th>可行</th><th>毛利</th><th>可复制</th><th>成交速度</th><th>合规</th><th>总分</th></tr>")
    models = sorted(bm.get("candidateModels", []), key=lambda m: -m.get("totalScore", 0))
    tmkt = {"china": "🇨🇳", "italy": "🇮🇹", "cross-border": "🔁跨境"}
    for i, m in enumerate(models, 1):
        s = m.get("scores", {})
        a(f'<tr><td><span class="rank">{i}</span></td><td><b>{e(m["name"])}</b><br><span class="muted">{e(m.get("oneLiner",""))}</span></td>'
          f'<td>{tmkt.get(m.get("targetMarket"),e(m.get("targetMarket")))}</td>'
          f'<td>{dots(s.get("feasibility",0))}</td><td>{dots(s.get("margin",0))}</td><td>{dots(s.get("scalability",0))}</td>'
          f'<td>{dots(s.get("dealSpeed",0))}</td><td>{dots(s.get("compliance",0))}</td><td><b>{e(round(m.get("totalScore",0),2))}</b></td></tr>')
    a("</table>")
    # model details
    for m in models:
        a(f'<details><summary>{e(m["name"])} — 详情(单位经济/假设/优劣)</summary>')
        a(f'<div class="muted"><b>价值链:</b>{e(m.get("valueChainPosition",""))}<br><b>源:</b>{e(m.get("sourceSide",""))}<br><b>客户:</b>{e(m.get("customerSide",""))}<br><b>收入:</b>{e(m.get("revenueModel",""))}<br><b>单位经济:</b>{e(m.get("unitEconomics",""))}<br><b>资金需求:</b>{e(m.get("capitalNeed",""))} · <b>回款:</b>{e(m.get("timeToRevenue",""))} · <b>壁垒:</b>{e(m.get("moat",""))}</div>')
        if m.get("keyAssumptions"):
            a("<b>关键假设</b><ul>"+"".join(f"<li>{e(k)}</li>" for k in m["keyAssumptions"])+"</ul>")
        a('<div class="flex"><div class="col"><b>优</b><ul>'+"".join(f"<li>{e(k)}</li>" for k in m.get("pros",[]))+"</ul></div>")
        a('<div class="col"><b>劣</b><ul>'+"".join(f"<li>{e(k)}</li>" for k in m.get("cons",[]))+"</ul></div></div></details>")
    # kill shots
    if brt.get("killShots"):
        a("<h3>🔴 红军压力测试(杀死它)</h3><table><tr><th>关键假设</th><th>攻击</th><th>严重度</th><th>是否扛住</th></tr>")
        sevc = {"fatal": "t-bad", "high": "t-bad", "medium": "t-part", "low": "t-un"}
        for k in brt["killShots"]:
            surv = '<span class="tag t-ok">扛住</span>' if k.get("survives") else '<span class="tag t-bad">未扛住</span>'
            a(f'<tr><td>{e(k["assumption"])}</td><td class="muted">{e(k["attack"])}</td><td><span class="tag {sevc.get(k.get("severity"),"t-un")}">{e(k.get("severity"))}</span></td><td>{surv}</td></tr>')
        a("</table>")
    # source archetypes
    a("<h3>找源(B2):中国货源画像</h3>")
    for s in B["source"].get("archetypes", []):
        a(f'<div class="card"><b>{e(s["type"])}</b> &nbsp;'+"".join(f'<span class="chip">{e(x)}</span>' for x in s.get("examples",[]))+
          f'<div class="muted">{e(s.get("valueProp",""))}<br><b>触达:</b>{e(s.get("howToReach",""))}</div>')
        if s.get("keyParams"):
            a("<div style='margin-top:5px'>"+"".join(f'<span class="chip">{e(p["name"])}: {e(p["value"])}</span>' for p in s["keyParams"])+"</div>")
        if s.get("sources"):
            a('<div class="muted" style="margin-top:5px">来源:'+" · ".join(f'<a href="{e(src["url"])}">{e(src["title"])}</a>' for src in s["sources"])+"</div>")
        a("</div>")
    # customer archetypes
    a("<h3>找客户(B3):意大利/欧盟成交方画像</h3>")
    for s in B["customer"].get("archetypes", []):
        a(f'<div class="card it"><b>{e(s["type"])}</b> &nbsp;'+"".join(f'<span class="chip">{e(x)}</span>' for x in s.get("examples",[]))+
          f'<div class="muted"><b>需求:</b>{e(s.get("need",""))}<br><b>付费意愿:</b>{e(s.get("willingnessToPay",""))}<br><b>决策链:</b>{e(s.get("decisionChain",""))}<br><b>触达:</b>{e(s.get("howToReach",""))}</div>')
        if s.get("sources"):
            a('<div class="muted" style="margin-top:5px">来源:'+" · ".join(f'<a href="{e(src["url"])}">{e(src["title"])}</a>' for src in s["sources"])+"</div>")
        a("</div>")
    # mechanisms
    a("<h3>机制设计(B1)</h3><table><tr><th>机制</th><th>目的</th><th>规则</th><th>可调参数</th></tr>")
    for m in B["mechanisms"].get("mechanisms", []):
        params = "<br>".join(f'<code>{e(p["name"])}</code>={e(p["defaultValue"])} <span class="muted">({e(p["note"])})</span>' for p in m.get("parameters",[]))
        a(f'<tr><td><b>{e(m["name"])}</b></td><td>{e(m["purpose"])}</td><td class="muted">{e(m["rule"])}</td><td>{params}</td></tr>')
    a("</table>")
    # process flow
    a("<h3>成交流程(B5):源→中间→客户</h3><table><tr><th>步骤</th><th>负责</th><th>输入→输出</th><th>周期</th><th>风险点</th><th>KPI</th></tr>")
    for p in bp.get("processFlow", []):
        a(f'<tr><td><b>{e(p["step"])}</b></td><td>{e(p["owner"])}</td><td class="muted">{e(p["input"])} → {e(p["output"])}</td><td>{e(p["duration"])}</td><td class="muted">{e(p["riskPoint"])}</td><td>{e(p["kpi"])}</td></tr>')
    a("</table>")
    # deliverables
    ds = bp.get("deliverableSpec", {})
    a("<h3>每日成果物(B6,成果物=产品本身)</h3><div class='card'>")
    for d in ds.get("dailyOutputs", []):
        a(f'<div><b>{e(d["name"])}</b> <span class="pill">{e(d["format"])}</span> — <span class="muted">{e(d["description"])}</span></div>')
    a(f'<div class="note" style="margin-top:10px"><b>本轮可立刻产出的第一个成果物:</b><br>{e(ds.get("firstDeliverableExample",""))}</div>')
    a("</div>")
a("</section>")

# ===== 5 来源 =====
a('<section>')
a(f"<h2>来源登记表(全部 {nsrc} 条,可追溯)</h2>")
a('<div class="muted">引用编号 = 维度key-来源ID。每条均为真实可点击 URL。</div>')
for x in dims:
    a(f'<details><summary>{e(x["key"])} — {e(x["name"])}（{len(x["research"]["sources"])} 条）</summary>')
    a("<table><tr><th>ID</th><th>来源</th><th>出版方</th><th>日期</th></tr>")
    for s in x["research"]["sources"]:
        link = f'<a href="{e(s["url"])}">{e(s["title"])}</a>' if s.get("url") else e(s["title"])
        a(f'<tr><td><code>{e(x["key"])}-{e(s["id"])}</code></td><td>{link}</td><td>{e(s["publisher"])}</td><td>{e(s["date"])}</td></tr>')
    a("</table></details>")
a("</section>")

# ===== 6 调参 =====
a('<section>')
a("<h2>决策人调参引导(你怎么改方向)</h2>")
a("""<div class="card"><ol>
<li><b>改维度</b>:编辑 <code>workflows/research.workflow.js</code> 的 <code>DIMENSIONS</code> 数组(增/删调研维度)。</li>
<li><b>改权重/时间窗/地域</b>:如把意大利权重从 0.3 提到 0.5,或时间窗收紧到近 12 个月。</li>
<li><b>改红军严格度</b>:调高 <code>effort</code>、要求 100% 来源逐条 WebFetch、低置信度直接丢弃。</li>
<li><b>改业务约束</b>:编辑 <code>workflows/business.workflow.js</code> 传入的 <code>constraints</code>(回收期、毛利、成交周期)。</li>
<li><b>否决与回灌</b>:对任一结论说"不",PM 把反馈作为下一轮输入。</li>
<li><b>重跑</b>:<code>Workflow({scriptPath:"workflows/research.workflow.js"})</code> 或业务工作流。</li>
</ol>
<div class="muted">你最终拿到:① 深度研究 PDF/Markdown 报告;② 本 HTML 看板;③ 每个流程的"核心逻辑→要点→分析结果→分析流程→各 Agent 核心要点与参数"。</div>
</div>""")
a("</section>")

a(f"""</main>
<script>
function go(i,btn){{
 document.querySelectorAll('main>section').forEach((s,j)=>s.classList.toggle('on',j===i));
 document.querySelectorAll('nav button').forEach(b=>b.classList.remove('on'));
 btn.classList.add('on'); window.scrollTo(0,0);
}}
// 打印/PDF模式:?print=1 → 浅色、全部展开、所有 details 打开
if(location.search.indexOf('print=1')>=0){{
 document.body.classList.add('print');
 document.querySelectorAll('details').forEach(d=>d.open=true);
}}
</script></body></html>""")

with open(OUT, "w") as g:
    g.write("".join(P))
print("written:", OUT, "| business:", "yes" if B else "no(框架占位)")
