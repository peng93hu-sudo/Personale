#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 data/business.json 生成业务PM线框架文档 docs/03-业务PM线框架.md。"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIZ = os.path.join(ROOT, "data", "business.json")
OUT = os.path.join(ROOT, "docs", "03-业务PM线框架.md")

B = json.load(open(BIZ))
meta = B["meta"]
mech = B["mechanisms"]["mechanisms"]
src = B["source"]["archetypes"]
cust = B["customer"]["archetypes"]
model = B["model"]
proc = B["process"]
rt = B["redTeam"]


def cell(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", "<br>").strip()


o = []
w = o.append

w(f"# 业务PM线框架:{meta['scope']}")
w("")
w(f"> 生成日期:{meta['generatedDate']} · 业务线工作流 RunID:`{meta['runId']}`")
w(f"> 多智能体:{meta['agentCount']} 个 Agent · {meta['totalTokens']:,} tokens · {meta['totalToolCalls']} 次工具调用")
w(f"> 流程:{meta['pipeline']}")
w(f"> 约束:{meta['constraints']}")
w("")
w(f"> ⚠️ **说明**:{meta['note']}")
w("")

# ===== 红军裁决置顶(最关键) =====
w("## 🔴 业务红军裁决(置顶 · 决策人必读)")
w("")
vd = rt["overallVerdict"]
emoji = {"go": "🟢 GO", "conditional-go": "🟡 CONDITIONAL-GO", "no-go": "🔴 NO-GO"}.get(vd, vd)
w(f"**裁决:{emoji}** · 置信度:{rt.get('confidence')}")
w("")
w(f"- **单位经济核查**:{rt['unitEconomicsCheck']}")
w("")
w(f"- **合规核查**:{rt['complianceCheck']}")
w("")
w("**红军\"杀死它\"压力测试(逐条攻击关键假设):**")
w("")
w("| 关键假设 | 攻击 | 严重度 | 是否扛住 |")
w("|---|---|---|---|")
sev = {"fatal": "💀 致命", "high": "🔴 高", "medium": "🟡 中", "low": "⚪ 低"}
for k in rt["killShots"]:
    surv = "✅ 扛住" if k.get("survives") else "❌ 未扛住"
    w(f"| {cell(k['assumption'])} | {cell(k['attack'])} | {sev.get(k.get('severity'), k.get('severity'))} | {surv} |")
w("")
w("**红军给出的前提条件 / 整改项:**")
w("")
for i, c in enumerate(rt.get("conditions", []), 1):
    w(f"{i}. {c}")
w("")
w("> 红军采用\"杀死这门生意\"原则。**裁决为 no-go,意味着推荐路径在当前形态下不成立,须按上述条件整改后复评。** 这正是\"每次更新都经红军反查\"机制的价值:在投入真金白银前先证伪。")
w("")

# ===== 推荐模式 =====
w("## 一、最优商业模式初判(B4)")
w("")
rec = model["recommended"]
w(f"### 🏆 推荐:{rec['name']}")
w("")
w(rec["rationale"])
w("")
w("**成立前提:**")
for c in rec.get("conditions", []):
    w(f"- {c}")
w("")

# 候选打分表
w("### 候选商业模式打分(加权:可行0.25+毛利0.25+可复制0.2+成交速度0.15+合规0.15)")
w("")
w("| 排名 | 模式 | 目标市场 | 可行 | 毛利 | 可复制 | 成交速度 | 合规 | 总分 |")
w("|---|---|---|---|---|---|---|---|---|")
tmkt = {"china": "🇨🇳国内", "italy": "🇮🇹意大利", "cross-border": "🔁跨境"}
models = sorted(model["candidateModels"], key=lambda m: -m.get("totalScore", 0))
for i, m in enumerate(models, 1):
    s = m["scores"]
    w(f"| {i} | {cell(m['name'])} | {tmkt.get(m['targetMarket'], m['targetMarket'])} | {s['feasibility']} | {s['margin']} | {s['scalability']} | {s['dealSpeed']} | {s['compliance']} | **{m['totalScore']}** |")
w("")

# 每个模式详情
for m in models:
    w(f"<details><summary><b>{cell(m['name'])}</b>(总分 {m['totalScore']})— 点击展开单位经济/假设/优劣</summary>")
    w("")
    w(f"- **一句话**:{m['oneLiner']}")
    w(f"- **价值链定位**:{m['valueChainPosition']}")
    w(f"- **源(供给侧)**:{m['sourceSide']}")
    w(f"- **客户(需求侧)**:{m['customerSide']}")
    w(f"- **收入模式**:{m['revenueModel']}")
    w(f"- **单位经济**:{m['unitEconomics']}")
    w(f"- **资金需求**:{m['capitalNeed']} · **回款周期**:{m['timeToRevenue']} · **壁垒**:{m['moat']}")
    w("- **关键假设**:")
    for a in m.get("keyAssumptions", []):
        w(f"  - {a}")
    w("- **优势**:" + " / ".join(m.get("pros", [])))
    w("- **劣势**:" + " / ".join(m.get("cons", [])))
    w("")
    w("</details>")
    w("")

# ===== 找源 =====
w("## 二、找源(B2):中国货源画像")
w("")
for s in src:
    w(f"### {s['type']}")
    w(f"- **代表**:{', '.join(s.get('examples', []))}")
    w(f"- **价值主张**:{s.get('valueProp', '')}")
    w(f"- **触达方式**:{s.get('howToReach', '')}")
    if s.get("keyParams"):
        w("- **关键参数**:" + " · ".join(f"{p['name']}={p['value']}" for p in s["keyParams"]))
    if s.get("risks"):
        w("- **风险**:" + " / ".join(s["risks"]))
    if s.get("sources"):
        w("- **来源**:" + " · ".join(f"[{x['title']}]({x['url']})" for x in s["sources"]))
    w("")

# ===== 找客户 =====
w("## 三、找客户(B3):意大利/欧盟成交方画像")
w("")
for s in cust:
    w(f"### {s['type']}")
    w(f"- **代表**:{', '.join(s.get('examples', []))}")
    w(f"- **需求**:{s.get('need', '')}")
    w(f"- **付费意愿**:{s.get('willingnessToPay', '')}")
    w(f"- **决策链**:{s.get('decisionChain', '')}")
    w(f"- **触达方式**:{s.get('howToReach', '')}")
    if s.get("sources"):
        w("- **来源**:" + " · ".join(f"[{x['title']}]({x['url']})" for x in s["sources"]))
    w("")

# ===== 机制 =====
w("## 四、机制设计(B1):可调参数即决策人旋钮")
w("")
for m in mech:
    w(f"### {m['name']}")
    w(f"- **目的**:{m['purpose']}")
    w(f"- **规则**:{m['rule']}")
    w(f"- **节奏**:{m['cadence']}")
    if m.get("parameters"):
        w("")
        w("| 参数 | 默认值 | 说明(决策人可调) |")
        w("|---|---|---|")
        for p in m["parameters"]:
            w(f"| `{cell(p['name'])}` | {cell(p['defaultValue'])} | {cell(p['note'])} |")
    w("")

# ===== 流程 =====
w("## 五、成交流程(B5):源 → 中间环节 → 客户")
w("")
w("| 步骤 | 负责 | 输入 → 输出 | 周期 | 风险点 | KPI |")
w("|---|---|---|---|---|---|")
for p in proc["processFlow"]:
    w(f"| {cell(p['step'])} | {cell(p['owner'])} | {cell(p['input'])} → {cell(p['output'])} | {cell(p['duration'])} | {cell(p['riskPoint'])} | {cell(p['kpi'])} |")
w("")

# ===== 成果物 =====
w("## 六、每日成果物(B6):成果物 = 产品本身")
w("")
ds = proc["deliverableSpec"]
w("| 成果物 | 格式 | 说明 |")
w("|---|---|---|")
for d in ds["dailyOutputs"]:
    w(f"| **{cell(d['name'])}** | {cell(d['format'])} | {cell(d['description'])} |")
w("")
w("### 本轮可立刻产出的第一个成果物")
w("")
w(f"> {ds['firstDeliverableExample']}")
w("")

w("---")
w("*本文档由 `scripts/gen_business.py` 从 `data/business.json` 自动生成。业务线每天产出成果物,每次更新经业务红军反查。*")

open(OUT, "w").write("\n".join(o) + "\n")
print("written:", OUT, "| lines:", len(o))
