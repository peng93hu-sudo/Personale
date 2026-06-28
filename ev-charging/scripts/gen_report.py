#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 data/research.json 生成可追溯的调研报告 docs/02-调研报告-充电桩.md。
报告内容 100% 由结构化数据驱动:每个数字挂来源,红军反查结论逐维度呈现,文末汇总全部来源。"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "research.json")
OUT = os.path.join(ROOT, "docs", "02-调研报告-充电桩.md")

with open(DATA) as f:
    D = json.load(f)

meta = D["meta"]
syn = D["synthesis"]
dims = D["dimensions"]

VERDICT_CN = {"verified": "✅ 已核实", "partially": "🟡 部分核实", "unverified": "⚠️ 未核实", "contradicted": "❌ 被反驳"}
CONF_CN = {"high": "高", "medium": "中", "low": "低"}


def cell(s):
    if s is None:
        return ""
    return str(s).replace("|", "\\|").replace("\n", "<br>").strip()


def src_link(s):
    url = s.get("url", "").strip()
    title = cell(s.get("title", ""))
    if url:
        return f"[{title}]({url})"
    return title


out = []
w = out.append

# ---------------- 头部 ----------------
w(f"# 充电桩市场深度调研报告({meta['scope']})")
w("")
w(f"> 生成日期:{meta['generatedDate']} · 调研线工作流 RunID:`{meta['runId']}`")
w(f"> 多智能体:{meta['agentCount']} 个 Agent · 累计 {meta['totalTokens']:,} tokens · {meta['totalToolCalls']} 次工具调用")
w(f"> 流程:{meta['pipeline']} · **每条关键数据均挂可点击来源,并经红军逐条反查**")
w("")

# 全局红军统计
tally = {"verified": 0, "partially": 0, "unverified": 0, "contradicted": 0}
nsrc = 0
for x in dims:
    nsrc += len(x["research"]["sources"])
    for c in x["redTeam"].get("checks", []):
        tally[c["verdict"]] = tally.get(c["verdict"], 0) + 1
total_checks = sum(tally.values())
w("## 📊 红军反查总览(可信度看板)")
w("")
w("| 指标 | 数值 |")
w("|---|---|")
w(f"| 调研维度 | {len(dims)} |")
w(f"| 引用来源(可点击) | {nsrc} |")
w(f"| 红军核验条目 | {total_checks} |")
w(f"| ✅ 已核实 | {tally['verified']} |")
w(f"| 🟡 部分核实 | {tally['partially']} |")
w(f"| ⚠️ 未核实 | {tally['unverified']} |")
w(f"| ❌ 被反驳 | {tally['contradicted']} |")
w("")
w("> 红军采用\"有错直到被证明无误\"原则,实际打开来源逐条核对。**未核实/被反驳的条目已在各维度显式标注,关键结论已据此降级或修正。**")
w("")

# ---------------- 执行摘要 ----------------
w("## 一、执行摘要(面向决策人)")
w("")
w(syn["executiveSummary"])
w("")

# ---------------- 快照 ----------------
w("## 二、市场快照")
w("")
w("### 🇨🇳 中国(主战场)")
w("")
w(syn["chinaSnapshot"])
w("")
w("### 🇮🇹 意大利(参照)")
w("")
w(syn["italySnapshot"])
w("")

# ---------------- 关键数字 ----------------
w("## 三、关键数字(带来源)")
w("")
w("| 指标 | 数值 | 市场 | 来源ID |")
w("|---|---|---|---|")
mkt = {"china": "🇨🇳", "italy": "🇮🇹", "global": "🌐"}
for kn in syn["keyNumbers"]:
    w(f"| {cell(kn['label'])} | {cell(kn['value'])} | {mkt.get(kn['market'], kn['market'])} | `{cell(kn['sourceId'])}` |")
w("")
w("> 来源ID 形如 `market-S1` = 维度`market`下的来源`S1`,可在文末\"来源登记表\"或对应维度章节追溯到原始 URL。")
w("")

# ---------------- 跨市场洞察 ----------------
w("## 四、跨市场洞察(国内 vs 意大利)")
w("")
for i, ins in enumerate(syn["crossCuttingInsights"], 1):
    w(f"{i}. {ins}")
w("")

# ---------------- 风险 ----------------
w("## 五、关键风险")
w("")
for i, r in enumerate(syn["topRisks"], 1):
    w(f"{i}. {r}")
w("")

# ---------------- 业务机会 ----------------
w("## 六、业务机会(移交业务PM线)")
w("")
w("> 以下机会点由综合Agent为业务PM线提炼,业务工作流 `business.workflow.js` 将以此为输入。")
w("")
for i, o in enumerate(syn["businessOpportunities"], 1):
    w(f"{i}. {o}")
w("")

# ---------------- 维度详解 ----------------
w("## 七、七维度详解")
w("")
dim_names = {
    "policy": "政策·法规·补贴·准入", "market": "市场规模·保有量·增长预测", "tech": "技术路线·标准·演进",
    "players": "竞争格局·主要玩家", "business": "商业模式·盈利模型", "supply": "供应链·成本结构·出海",
    "ops": "运营·用户行为·痛点",
}
for idx, x in enumerate(dims, 1):
    r = x["research"]
    rt = x["redTeam"]
    w(f"### 7.{idx} {x['name']}")
    w("")
    w(f"**维度自评置信度**:{CONF_CN.get(r.get('selfConfidence'), r.get('selfConfidence'))} · **红军整体置信度**:{CONF_CN.get(rt.get('overallConfidence'), rt.get('overallConfidence'))}")
    w("")
    # 中国
    w(f"**🇨🇳 中国**:{r['china']['summary']}")
    w("")
    if r["china"].get("keyDataPoints"):
        w("| 指标 | 数值 | 时点 | 来源 |")
        w("|---|---|---|---|")
        for k in r["china"]["keyDataPoints"]:
            w(f"| {cell(k['metric'])} | {cell(k['value'])} | {cell(k['asOf'])} | `{cell(k['sourceId'])}` |")
        w("")
    if r["china"].get("insights"):
        w("要点:")
        for ins in r["china"]["insights"]:
            w(f"- {ins}")
        w("")
    # 意大利
    w(f"**🇮🇹 意大利(参照)**:{r['italy']['summary']}")
    w("")
    if r["italy"].get("keyDataPoints"):
        w("| 指标 | 数值 | 时点 | 来源 |")
        w("|---|---|---|---|")
        for k in r["italy"]["keyDataPoints"]:
            w(f"| {cell(k['metric'])} | {cell(k['value'])} | {cell(k['asOf'])} | `{cell(k['sourceId'])}` |")
        w("")
    if r["italy"].get("insights"):
        w("要点:")
        for ins in r["italy"]["insights"]:
            w(f"- {ins}")
        w("")
    # 对照
    if r.get("comparison"):
        w("**国内 vs 意大利 对照**:")
        for c in r["comparison"]:
            w(f"- {c}")
        w("")
    # 红军
    w("**🔴 红军反查**:")
    w("")
    vt = {"verified": 0, "partially": 0, "unverified": 0, "contradicted": 0}
    for c in rt.get("checks", []):
        vt[c["verdict"]] = vt.get(c["verdict"], 0) + 1
    w(f"核验 {sum(vt.values())} 条:✅{vt['verified']} / 🟡{vt['partially']} / ⚠️{vt['unverified']} / ❌{vt['contradicted']}")
    w("")
    # 显示被反驳/未核实的条目(最重要)
    problem = [c for c in rt.get("checks", []) if c["verdict"] in ("contradicted", "unverified")]
    if problem:
        w("被反驳/未核实条目:")
        w("")
        w("| 论断 | 裁决 | 红军说明 |")
        w("|---|---|---|")
        for c in problem:
            w(f"| {cell(c['claim'])} | {VERDICT_CN[c['verdict']]} | {cell(c['note'])} |")
        w("")
    if rt.get("flaggedClaims"):
        w("⚠️ 红军标记需谨慎对待的论断:")
        for fc in rt["flaggedClaims"]:
            w(f"- {fc}")
        w("")
    if rt.get("corrections"):
        w("🛠 红军建议的修正/补数据方向:")
        for cc in rt["corrections"]:
            w(f"- {cc}")
        w("")
    # open questions
    if r.get("openQuestions"):
        w("❓ 待证实问题:")
        for q in r["openQuestions"]:
            w(f"- {q}")
        w("")
    # 本维度来源
    w(f"<details><summary>📚 本维度来源({len(r['sources'])} 条,点击展开)</summary>")
    w("")
    w("| ID | 来源 | 出版方 | 日期 | 支撑的论断 |")
    w("|---|---|---|---|---|")
    for s in r["sources"]:
        w(f"| `{cell(s['id'])}` | {src_link(s)} | {cell(s['publisher'])} | {cell(s['date'])} | {cell(s['supports'])} |")
    w("")
    w("</details>")
    w("")

# ---------------- 置信度与局限 ----------------
w("## 八、整体置信度与数据局限(红军汇总)")
w("")
w(syn["confidenceNote"])
w("")

# ---------------- 全局来源登记表 ----------------
w("## 九、来源登记表(全部,可追溯)")
w("")
w(f"共 {nsrc} 条来源,按维度归档。引用编号 = `维度key-来源ID`。")
w("")
for x in dims:
    w(f"### {x['key']} — {x['name']}")
    w("")
    w("| ID | 来源 | 出版方 | 日期 |")
    w("|---|---|---|---|")
    for s in x["research"]["sources"]:
        w(f"| `{x['key']}-{cell(s['id'])}` | {src_link(s)} | {cell(s['publisher'])} | {cell(s['date'])} |")
    w("")

# ---------------- 方法论 ----------------
w("## 十、方法论与可追溯说明")
w("")
w("- **多智能体分工**:7 个维度研究 Agent 并行调研(各自 WebSearch + WebFetch 权威来源),逐维度交由红军对抗式反查,最后综合 Agent 收口。")
w("- **可查**:每个数字挂 `sourceId`,对应真实可点击 URL(见各维度来源表与第九节登记表)。")
w("- **可验证**:红军实际打开来源核对,给出 ✅/🟡/⚠️/❌ 裁决(本轮采集环境对部分政府站点返回 403,红军改用多源交叉验证,已在 note 中说明)。")
w("- **可追溯**:结论 → 关键数字 → sourceId → 原始来源 → 红军裁决,全链路存于 `data/research.json`。")
w("- **可调试**:编辑 `workflows/research.workflow.js` 的 `DIMENSIONS`、地域权重、红军 `effort`,重跑即可引导结果。")
w("")
w("---")
w("*本报告由 `scripts/gen_report.py` 从 `data/research.json` 自动生成,确保报告与数据严格一致。调研线每周刷新一次。*")

with open(OUT, "w") as g:
    g.write("\n".join(out) + "\n")

print("written:", OUT)
print("lines:", len(out), "| sources:", nsrc, "| checks:", total_checks)
