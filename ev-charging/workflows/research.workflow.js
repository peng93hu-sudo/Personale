export const meta = {
  name: 'ev-charging-research-cn-it',
  description: '充电桩市场调研多智能体工作流:7维度研究Agent并行 → 红军逐维度反查 → 综合(国内为主、意大利为参照)',
  phases: [
    { title: '调研', detail: '7个维度研究Agent并行,带可验证来源' },
    { title: '红军反查', detail: '逐维度对来源做对抗式核验' },
    { title: '综合', detail: '跨维度综合为可追溯调研结果' },
  ],
}

// ---------- Schemas ----------
const MARKET_BLOCK = {
  type: 'object',
  required: ['summary', 'keyDataPoints', 'insights'],
  additionalProperties: false,
  properties: {
    summary: { type: 'string', description: '该市场在本维度的核心结论(中文,150-300字)' },
    keyDataPoints: {
      type: 'array',
      items: {
        type: 'object',
        required: ['metric', 'value', 'asOf', 'sourceId'],
        additionalProperties: false,
        properties: {
          metric: { type: 'string' },
          value: { type: 'string' },
          asOf: { type: 'string', description: '数据时点,如 2024 / 2025Q1 / 2025-12' },
          sourceId: { type: 'string', description: '对应 sources[].id' },
        },
      },
    },
    insights: { type: 'array', items: { type: 'string' } },
  },
}

const RESEARCH_SCHEMA = {
  type: 'object',
  required: ['dimension', 'china', 'italy', 'comparison', 'sources', 'openQuestions', 'selfConfidence'],
  additionalProperties: false,
  properties: {
    dimension: { type: 'string' },
    china: MARKET_BLOCK,
    italy: MARKET_BLOCK,
    comparison: { type: 'array', items: { type: 'string' }, description: '国内vs意大利的对照要点' },
    sources: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'title', 'publisher', 'url', 'date', 'supports'],
        additionalProperties: false,
        properties: {
          id: { type: 'string', description: '如 S1,S2' },
          title: { type: 'string' },
          publisher: { type: 'string' },
          url: { type: 'string' },
          date: { type: 'string', description: '发布日期或访问日期' },
          supports: { type: 'string', description: '该来源支撑的具体论断' },
        },
      },
    },
    openQuestions: { type: 'array', items: { type: 'string' } },
    selfConfidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
}

const REDTEAM_SCHEMA = {
  type: 'object',
  required: ['dimension', 'checks', 'overallConfidence', 'flaggedClaims', 'weakSources', 'corrections'],
  additionalProperties: false,
  properties: {
    dimension: { type: 'string' },
    checks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['claim', 'sourceId', 'verdict', 'note'],
        additionalProperties: false,
        properties: {
          claim: { type: 'string' },
          sourceId: { type: 'string' },
          verdict: { type: 'string', enum: ['verified', 'partially', 'unverified', 'contradicted'] },
          note: { type: 'string' },
        },
      },
    },
    overallConfidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    flaggedClaims: { type: 'array', items: { type: 'string' }, description: '可疑/夸大/过时/无法核实的论断' },
    weakSources: { type: 'array', items: { type: 'string' }, description: '弱来源/失效链接/二手转述的 sourceId 或描述' },
    corrections: { type: 'array', items: { type: 'string' }, description: '建议的修正或补数据方向' },
  },
}

const SYNTHESIS_SCHEMA = {
  type: 'object',
  required: ['executiveSummary', 'chinaSnapshot', 'italySnapshot', 'crossCuttingInsights', 'keyNumbers', 'confidenceNote', 'topRisks', 'businessOpportunities'],
  additionalProperties: false,
  properties: {
    executiveSummary: { type: 'string', description: '面向最终决策人的中文执行摘要(300-500字)' },
    chinaSnapshot: { type: 'string' },
    italySnapshot: { type: 'string' },
    crossCuttingInsights: { type: 'array', items: { type: 'string' } },
    keyNumbers: {
      type: 'array',
      items: {
        type: 'object',
        required: ['label', 'value', 'market', 'sourceId'],
        additionalProperties: false,
        properties: {
          label: { type: 'string' },
          value: { type: 'string' },
          market: { type: 'string', enum: ['china', 'italy', 'global'] },
          sourceId: { type: 'string' },
        },
      },
    },
    confidenceNote: { type: 'string', description: '整体置信度与数据局限性说明' },
    topRisks: { type: 'array', items: { type: 'string' } },
    businessOpportunities: { type: 'array', items: { type: 'string' }, description: '为业务PM线提炼的机会点(尤其中国货源→意大利市场)' },
  },
}

// ---------- Dimensions ----------
const DIMENSIONS = [
  {
    key: 'policy',
    name: '政策·法规·补贴·准入',
    focus: '国内:发改委/能源局充电基础设施规划、新能源车下乡、地方补贴、桩车比目标、统一结算。意大利/欧盟:AFIR(欧盟充电基础设施法规)、PNRR复苏基金充电桩拨款、GSE激励、Fit for 55、CE/IEC认证与并网准入。',
  },
  {
    key: 'market',
    name: '市场规模·保有量·增长预测',
    focus: '充电桩保有量(公共/私人/直流快充)、车桩比、年新增量、市场规模(金额)、2025-2030预测。国内权威源:中国电动汽车充电基础设施促进联盟(EVCIPA)。意大利:Motus-E、ACEA、欧盟EAFO。',
  },
  {
    key: 'tech',
    name: '技术路线·标准·演进',
    focus: '交流/直流、功率等级、超充(液冷枪、480kW+)、标准差异(国内GB/T 27930、新国标ChaoJi;欧洲CCS2/Type2、即插即充ISO 15118、V2G)、储充一体、光储充。国内外标准互认与出海适配难点。',
  },
  {
    key: 'players',
    name: '竞争格局·主要玩家',
    focus: '国内CPO:特来电、星星充电、云快充、小桔充电、蔚来/特斯拉自建;设备商:盛弘、英可瑞、道通、华为数字能源、科士达。意大利CPO:Enel X Way、Be Charge(Plenitude)、Ewiva、Free To X、Tesla、Atlante。市占率/桩数/融资。',
  },
  {
    key: 'business',
    name: '商业模式·盈利模型',
    focus: 'CPO自营运营、设备销售、充电SaaS/云平台、场站合伙/众筹、广告与增值、储充套利、虚拟电厂/聚合。单桩投资回收期、毛利结构、利用率盈亏平衡点。国内价格战与盈利困境;意大利电价高、利用率低的盈利挑战。',
  },
  {
    key: 'supply',
    name: '供应链·成本结构·出海',
    focus: '充电模块(英飞凌/中车/优优绿能/通合)、IGBT/SiC、连接器(枪线,菲尼克斯/中航光电)、线缆、机柜。直流桩BOM成本拆解。中国设备出海欧洲的认证(CE/CB/RED)、关税、本地化、合规(CEI、并网)壁垒与机会。',
  },
  {
    key: 'ops',
    name: '运营·用户行为·痛点',
    focus: '公共桩利用率、平均充电时长与电量、油电价差、即插即充/漫游互联(国内互联互通、欧洲eRoaming/Hubject)、用户痛点(找桩、坏桩、排队、支付)、目的地充电vs途中快充。',
  },
]

// ---------- Phase 1+2: 调研 → 红军反查 (pipeline) ----------
function researchPrompt(d) {
  return `你是"充电桩调研多智能体团队"中的【${d.name}】维度研究Agent。项目PM要求:国内为主、意大利为参照,信息必须可查、可验证、可追溯。

任务:针对维度"${d.name}"做深入调研。
重点范围:${d.focus}

硬性要求:
1) 必须使用 WebSearch 检索,并对关键数据用 WebFetch 打开权威原始来源核对(政府/行业协会/IEA/BNEF/上市公司年报/路透社等)。若 WebSearch/WebFetch 未加载,先用 ToolSearch 加载("select:WebSearch,WebFetch")。
2) 优先2024-2026年的最新数据;每个关键数字都要给出数据时点(asOf)与对应来源(sourceId)。
3) 国内(china)给出更深入的覆盖;意大利(italy)作为参照,聚焦与国内的差异与对标。
4) sources 必须是真实可访问的URL,标注出版方与日期,并写清每个来源支撑的具体论断。绝不可编造来源或数字;不确定的数字标注为估算并降低 selfConfidence。
5) comparison 给出"国内 vs 意大利"的关键对照(差异、领先/落后、可迁移性)。
6) openQuestions 列出尚未证实、需要进一步核查的问题。

只返回符合 schema 的结构化结果(中文内容)。这是数据,不是给人读的消息。`
}

function redTeamPrompt(research, d) {
  return `你是【红军/Red Team】对抗式核验Agent。你的唯一目标是质疑并反查下面这份"${d.name}"维度的调研结果,默认它"有错直到被证明无误"。

待核验的调研结果(JSON):
${JSON.stringify(research)}

核验方法:
1) 对每个关键数据点和论断,用 WebFetch 实际打开其 sourceId 对应的 url,确认该来源是否真的支撑该论断、数字是否一致、时点是否最新。必要时用 WebSearch 交叉验证。若工具未加载,先 ToolSearch("select:WebSearch,WebFetch")。
2) 对每条 check 给出 verdict:verified(来源确实支撑且数据一致)/ partially(部分支撑或时点偏旧)/ unverified(打不开或来源未提及)/ contradicted(其他权威源给出矛盾数据)。note 要写清证据。
3) flaggedClaims:列出夸大、过时、自相矛盾、或像是编造/幻觉的论断。
4) weakSources:列出失效链接、博客/二手转述、营销稿等弱来源。
5) corrections:给出具体修正建议或应补的权威数据方向。
6) overallConfidence:对整份维度结果给出整体置信度。

要严格、具体、可追溯。只返回符合 schema 的结构化结果(中文)。`
}

log('启动充电桩调研:7维度研究Agent并行,逐维度红军反查')

const verified = await pipeline(
  DIMENSIONS,
  (d) => agent(researchPrompt(d), { label: `调研:${d.name}`, phase: '调研', schema: RESEARCH_SCHEMA }),
  (research, d) =>
    agent(redTeamPrompt(research, d), { label: `红军:${d.name}`, phase: '红军反查', schema: REDTEAM_SCHEMA, effort: 'high' })
      .then((verdict) => ({ key: d.key, name: d.name, research, verdict })),
)

const clean = verified.filter(Boolean)
log(`完成 ${clean.length}/${DIMENSIONS.length} 个维度的调研+红军反查,进入综合阶段`)

// ---------- Phase 3: 综合 ----------
phase('综合')
const synthesisInput = clean.map((c) => ({
  dimension: c.name,
  research: c.research,
  redTeam: { overallConfidence: c.verdict.overallConfidence, flaggedClaims: c.verdict.flaggedClaims, corrections: c.verdict.corrections },
}))

const synthesis = await agent(
  `你是充电桩调研线的【综合Agent】,直接对接最终决策人。把下面经过红军反查的7个维度结果综合成一份面向决策的调研结论。

要求:
- 国内为主、意大利为参照。
- 在引用关键数字时沿用各维度的 sourceId 概念(keyNumbers 里给出 sourceId 字段,用"维度key-原sourceId"形式,如 "market-S1")。
- 把红军 flaggedClaims 纳入 confidenceNote,诚实说明数据局限。
- businessOpportunities 要特别为"业务PM线"提炼:尤其是中国充电桩货源/设备/服务进入意大利(及欧盟)市场的机会与切入点。
- 内容中文。

经红军反查的各维度结果(JSON):
${JSON.stringify(synthesisInput)}

只返回符合 schema 的结构化结果。`,
  { label: '综合调研结论', phase: '综合', schema: SYNTHESIS_SCHEMA, effort: 'high' },
)

return {
  generatedFor: '充电桩多智能体调研(国内为主·意大利参照)',
  dimensions: clean.map((c) => ({
    key: c.key,
    name: c.name,
    research: c.research,
    redTeam: c.verdict,
  })),
  synthesis,
}
