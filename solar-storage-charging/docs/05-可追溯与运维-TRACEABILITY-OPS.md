# 可追溯与运维（TRACEABILITY & OPS）

> 把"可查、可验证、可追溯"和"周刷/日更"落到**文件、版本、定时**上。
> 负责人：AR 档案 Agent + A0 编排。版本：v1.0 · 2026-06-28

---

## 1. 目录结构（数据与存证的物理落点）

```
solar-storage-charging/
├── README.md                      # 项目总览 + 导航
├── docs/                          # 系统定义(本套文档)
│   ├── 00-学习文档-LEARNING.md
│   ├── 01-智能体架构-AGENTS.md
│   ├── 02-调研PM工作流-RESEARCH-SOP.md
│   ├── 03-业务PM工作流-BUSINESS-SOP.md
│   ├── 04-红军反查机制-REDTEAM.md
│   └── 05-可追溯与运维-TRACEABILITY-OPS.md
├── research/
│   ├── 光储充-调研报告.md          # 带来源+红军判定的研究报告(周刷)
│   └── sources.md                 # 来源登记册(稳定编号)
├── business/
│   └── 商业模式与交易设计.md        # 业务成交方案(日更)
├── data/
│   └── research-findings.json     # 多智能体原始结构化产出(机读)
└── html/
    ├── index.html                 # 控制塔总览
    ├── research.html              # 研究深度报告(可打印PDF)
    └── business.html              # 业务辅助
```

## 2. 三大可追溯载体

### 2.1 来源登记册 `sources.md`
- 每个来源给稳定编号 `[S-001]`，含：机构、标题、URL、发布日期、抓取日期、可信层级。
- 正文与报告引用编号，做到"点结论 → 跳来源"。

### 2.2 版本块（每份成果物头部）
```markdown
> 版本: v1.2 | 日期: 2026-06-28 | 类型: 调研周刷
> 本次变更: 新增意大利 MACSE 容量拍卖结果; 修正中国峰谷价差区间
> 红军批次: RT-2026W26 | 判定: ✅18 🟡6 ❌1 ⚪3
> 决策人裁决: 采信 BNEF 口径(见 CHANGELOG #14)
```

### 2.3 变更日志（CHANGELOG，可在 README 内维护）
- 逐条记：日期、产线、改了什么、依据哪条新来源/哪条红军判定、你的裁决。
- Git commit 本身是第二层审计线：一次更新 = 一次 commit。

## 3. 数据流（机读 → 人读 → 可视化）

```
多智能体结构化产出 (data/research-findings.json, 遵循 FINDINGS/VERDICT schema)
        │
        ├─► research/光储充-调研报告.md   (人读, 带来源编号+红军标签)
        ├─► research/sources.md          (来源登记)
        └─► html/{index,research}.html    (可视化, 红军判定着色)
```

## 4. 运行节奏与自动化脚手架

### 4.1 手动跑（当前默认）
- 调研周刷：重跑 6 维度多智能体 workflow → 红军 → 汇总 → 更新报告/HTML → commit。
- 业务日更：跑 B1-B4（按选定模式）→ 红军 → 更新业务 HTML → commit。

### 4.2 定时自动化（可选，接入后）
- **调研周刷**：每周一次的定时任务触发研究 workflow。
- **业务日更**：每日一次的定时任务触发业务 workflow。
- 实现方式（按环境择一）：
  - Claude Code 的 `/loop` 或定时 Cron（在会话内调度）；
  - 仓库 CI（GitHub Actions schedule）触发脚本；
  - 外部调度器调用。
- **约束**：任何自动产出**仍需过红军**，且**对外动作必须人工确认**（不自动找客户/报价/签约）。

> 自动化是"省你手动触发"，不是"绕过你决策"。决策权始终在你手上。

## 5. 质量门禁（Definition of Done）

一次更新只有同时满足才算"完成"并可 commit：
- [ ] 新增/变更结论都带 source + date + confidence。
- [ ] 都过红军并有 verdict。
- [ ] 报告/方案有版本块 + 本次 diff。
- [ ] sources.md 同步更新。
- [ ] HTML 重新渲染、红军判定可视化正确。
- [ ] CHANGELOG 记录本次变更与依据。

## 6. 失败与回滚

- 若红军大面积判 `refuted/unverifiable`（如风险面 > 40%），**暂缓发布**，PM 复盘来源质量，重跑。
- Git 保留历史，任何一版都可回滚；被证伪结论降级留痕，不做静默删除。
