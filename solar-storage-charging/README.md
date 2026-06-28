# 光储充 Multi-Agent 调研与业务系统

> **主题**：光储充（光伏 PV + 储能 Storage + 电动汽车充电 Charging）一体化场景的**市场调研**与**商业落地**
> **区域**：中国（国内）／意大利（Italy）
> **形态**：两个 PM（调研 / 业务）+ 多智能体执行 + 红军反查，你是项目总 PM / 最终决策人。
> **原则**：高质量信息**可查、可验证、可追溯**；每次更新必过红军；决策权始终在你手上。

---

## 这是什么

一套把"研究一个赛道 + 把它做成生意"拆成**两条多智能体产线**的系统：

- **调研线（PM-R）** → 把"光储充在中国/意大利什么情况"研究清楚，产出**可被审计的研究结论**（周刷）。
- **业务线（PM-B）** → 拿研究当弹药，**找货 → 找客户 → 设计成交流程 → 算账**，产出**可执行的成交方案**（日更）。
- **红军（RT）** → 每次更新独立反查，给 ✅/🟡/❌/⚪ 判定。
- **你** → 改参数、定方向、拍板、验收。

## 快速导航

| 你想… | 看这个 |
|---|---|
| 看懂整套方法论（沉淀文档） | [`docs/00-学习文档-LEARNING.md`](docs/00-学习文档-LEARNING.md) |
| 看每个智能体的角色/身份/工作范畴 | [`docs/01-智能体架构-AGENTS.md`](docs/01-智能体架构-AGENTS.md) |
| 看调研线怎么跑 | [`docs/02-调研PM工作流-RESEARCH-SOP.md`](docs/02-调研PM工作流-RESEARCH-SOP.md) |
| 看业务线怎么跑 | [`docs/03-业务PM工作流-BUSINESS-SOP.md`](docs/03-业务PM工作流-BUSINESS-SOP.md) |
| 看红军怎么反查 | [`docs/04-红军反查机制-REDTEAM.md`](docs/04-红军反查机制-REDTEAM.md) |
| 看存证/版本/定时 | [`docs/05-可追溯与运维-TRACEABILITY-OPS.md`](docs/05-可追溯与运维-TRACEABILITY-OPS.md) |
| 看研究结论（带来源+红军判定） | [`research/光储充-调研报告.md`](research/光储充-调研报告.md) |
| 看来源登记册 | [`research/sources.md`](research/sources.md) |
| 看业务成交方案 | [`business/商业模式与交易设计.md`](business/商业模式与交易设计.md) |
| **看可视化看板（推荐）** | `html/index.html`（控制塔）· `html/research.html` · `html/business.html` |

> HTML 直接用浏览器打开。`research.html` 内置"打印为 PDF"，浏览器一键导出深度研究 PDF。

## 智能体清单（13 角色）

```
你(决策人) → A0编排 → ┬ PM-R调研 → R1政策 / R2经济性 / R3格局 ┐
                      └ PM-B业务 → B1货源 / B2客户 / B3成交 / B4财务 ┘
                                    ↘ RT红军(反查) · AR档案(存证) · PUB产出(PDF/HTML) ↙
```

详见 [`docs/01-智能体架构-AGENTS.md`](docs/01-智能体架构-AGENTS.md)。

## 运行节奏

| 产线 | 频率 | 成果物 |
|---|---|---|
| 调研线 | 每周刷 1 次 | 研究报告 diff + 来源更新 + HTML |
| 业务线 | 每天 1 次 | 业务 HTML + 1 个可执行动作 |
| 每次更新 | —— | 都必须过红军 |

## 变更日志（CHANGELOG）

| 日期 | 产线 | 变更 | 依据 |
|---|---|---|---|
| 2026-06-28 | 全部 | v1.0 初始化：系统骨架 + 首轮中意6维度调研 + 红军反查 + 三张 HTML | 见 sources.md |

---
*光储充 = 光伏+储能+充电；PV + Storage + EV Charging integrated scenario.*
