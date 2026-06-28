export const meta = {
  name: 'ev-charging-business-cn-it',
  description: '业务PM线多智能体工作流:依据调研→机制设计/找源/找客户(并行)→商业模式模拟选优→流程与成果物→红军反查',
  phases: [
    { title: '机制与源客', detail: 'B1机制 / B2找源 / B3找客户 并行' },
    { title: '模式选优', detail: 'B4 多候选商业模式建模打分,选最优' },
    { title: '流程与成果', detail: 'B5 流程设计 / B6 成果物规格' },
    { title: '业务红军', detail: '对最优模式做"杀死它"式压力测试' },
  ],
}

// args = { synthesis, opportunities, constraints }
// 兼容:args 可能以对象或 JSON 字符串形式传入,做健壮解析,避免静默回退到通用知识。
let A = args
if (typeof A === 'string') {
  try { A = JSON.parse(A) } catch (e) { A = {} }
}
if (!A || typeof A !== 'object') A = {}
log(A.synthesis ? '已接收调研综合(synthesis)作为输入' : '⚠️ 未接收到调研综合,业务Agent将基于自身检索')
const SYN = A.synthesis ? JSON.stringify(A.synthesis) : '(未提供调研综合,请基于充电桩行业常识与公开信息,但要标注来源)'
const OPP = Array.isArray(A.opportunities) ? A.opportunities.join('\n- ') : (A.opportunities || '中国充电桩设备/服务进入意大利及欧盟市场')
const CONSTRAINTS = A.constraints || '优先:可在6-12个月内实现首单成交、毛利>15%、合规可落地、轻资产优先'

// ---------- Schemas ----------
const SOURCE_SCHEMA = {
  type: 'object',
  required: ['archetypes'],
  additionalProperties: false,
  properties: {
    archetypes: {
      type: 'array',
      items: {
        type: 'object',
        required: ['type', 'examples', 'valueProp', 'howToReach', 'keyParams', 'risks', 'sources'],
        additionalProperties: false,
        properties: {
          type: { type: 'string', description: '源的类别,如"中国直流快充整机厂""充电模块厂""SaaS平台商"' },
          examples: { type: 'array', items: { type: 'string' }, description: '真实公司名(尽量具体)' },
          valueProp: { type: 'string' },
          howToReach: { type: 'string', description: '如何触达/谈判切入点' },
          keyParams: { type: 'array', items: { type: 'object', required: ['name', 'value'], additionalProperties: false, properties: { name: { type: 'string' }, value: { type: 'string' } } } },
          risks: { type: 'array', items: { type: 'string' } },
          sources: { type: 'array', items: { type: 'object', required: ['title', 'url'], additionalProperties: false, properties: { title: { type: 'string' }, url: { type: 'string' } } } },
        },
      },
    },
  },
}

const CUSTOMER_SCHEMA = {
  type: 'object',
  required: ['archetypes'],
  additionalProperties: false,
  properties: {
    archetypes: {
      type: 'array',
      items: {
        type: 'object',
        required: ['type', 'examples', 'need', 'willingnessToPay', 'decisionChain', 'howToReach', 'sources'],
        additionalProperties: false,
        properties: {
          type: { type: 'string', description: '成交方类别,如"意大利CPO""充电站EPC/安装商""分销/进口商""车企/车队""商业地产/超市"' },
          examples: { type: 'array', items: { type: 'string' } },
          need: { type: 'string' },
          willingnessToPay: { type: 'string' },
          decisionChain: { type: 'string', description: '决策链与采购方式' },
          howToReach: { type: 'string' },
          sources: { type: 'array', items: { type: 'object', required: ['title', 'url'], additionalProperties: false, properties: { title: { type: 'string' }, url: { type: 'string' } } } },
        },
      },
    },
  },
}

const MECH_SCHEMA = {
  type: 'object',
  required: ['mechanisms'],
  additionalProperties: false,
  properties: {
    mechanisms: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'purpose', 'rule', 'cadence', 'parameters'],
        additionalProperties: false,
        properties: {
          name: { type: 'string', description: '如 撮合机制/分润机制/定价机制/风控机制/履约机制' },
          purpose: { type: 'string' },
          rule: { type: 'string', description: '具体规则' },
          cadence: { type: 'string' },
          parameters: { type: 'array', items: { type: 'object', required: ['name', 'defaultValue', 'note'], additionalProperties: false, properties: { name: { type: 'string' }, defaultValue: { type: 'string' }, note: { type: 'string', description: '决策人可调的旋钮说明' } } } },
        },
      },
    },
  },
}

const MODEL_SCHEMA = {
  type: 'object',
  required: ['candidateModels', 'recommended'],
  additionalProperties: false,
  properties: {
    candidateModels: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'oneLiner', 'valueChainPosition', 'targetMarket', 'sourceSide', 'customerSide', 'revenueModel', 'unitEconomics', 'keyAssumptions', 'pros', 'cons', 'capitalNeed', 'timeToRevenue', 'moat', 'scores', 'totalScore'],
        additionalProperties: false,
        properties: {
          name: { type: 'string' },
          oneLiner: { type: 'string' },
          valueChainPosition: { type: 'string' },
          targetMarket: { type: 'string', enum: ['china', 'italy', 'cross-border'] },
          sourceSide: { type: 'string' },
          customerSide: { type: 'string' },
          revenueModel: { type: 'string' },
          unitEconomics: { type: 'string', description: '单位经济测算(尽量给数字与假设)' },
          keyAssumptions: { type: 'array', items: { type: 'string' } },
          pros: { type: 'array', items: { type: 'string' } },
          cons: { type: 'array', items: { type: 'string' } },
          capitalNeed: { type: 'string', enum: ['low', 'medium', 'high'] },
          timeToRevenue: { type: 'string' },
          moat: { type: 'string' },
          scores: {
            type: 'object',
            required: ['feasibility', 'margin', 'scalability', 'dealSpeed', 'compliance'],
            additionalProperties: false,
            properties: {
              feasibility: { type: 'integer', minimum: 1, maximum: 5 },
              margin: { type: 'integer', minimum: 1, maximum: 5 },
              scalability: { type: 'integer', minimum: 1, maximum: 5 },
              dealSpeed: { type: 'integer', minimum: 1, maximum: 5 },
              compliance: { type: 'integer', minimum: 1, maximum: 5 },
            },
          },
          totalScore: { type: 'number', description: '加权总分' },
        },
      },
    },
    recommended: {
      type: 'object',
      required: ['name', 'rationale', 'conditions'],
      additionalProperties: false,
      properties: {
        name: { type: 'string' },
        rationale: { type: 'string' },
        conditions: { type: 'array', items: { type: 'string' }, description: '推荐成立的前提条件' },
      },
    },
  },
}

const PROCESS_SCHEMA = {
  type: 'object',
  required: ['processFlow', 'deliverableSpec'],
  additionalProperties: false,
  properties: {
    processFlow: {
      type: 'array',
      items: {
        type: 'object',
        required: ['step', 'owner', 'input', 'output', 'duration', 'riskPoint', 'kpi'],
        additionalProperties: false,
        properties: {
          step: { type: 'string' },
          owner: { type: 'string', description: '负责的Agent或人' },
          input: { type: 'string' },
          output: { type: 'string' },
          duration: { type: 'string' },
          riskPoint: { type: 'string' },
          kpi: { type: 'string' },
        },
      },
    },
    deliverableSpec: {
      type: 'object',
      required: ['dailyOutputs', 'firstDeliverableExample'],
      additionalProperties: false,
      properties: {
        dailyOutputs: { type: 'array', items: { type: 'object', required: ['name', 'format', 'description'], additionalProperties: false, properties: { name: { type: 'string' }, format: { type: 'string' }, description: { type: 'string' } } } },
        firstDeliverableExample: { type: 'string', description: '本轮可立刻产出的第一个成果物示例(成果物=产品本身)' },
      },
    },
  },
}

const BIZ_REDTEAM_SCHEMA = {
  type: 'object',
  required: ['killShots', 'unitEconomicsCheck', 'complianceCheck', 'overallVerdict', 'conditions', 'confidence'],
  additionalProperties: false,
  properties: {
    killShots: {
      type: 'array',
      items: {
        type: 'object',
        required: ['assumption', 'attack', 'severity', 'survives', 'note'],
        additionalProperties: false,
        properties: {
          assumption: { type: 'string', description: '商业模式依赖的关键假设' },
          attack: { type: 'string', description: '红军如何攻击/证伪它' },
          severity: { type: 'string', enum: ['fatal', 'high', 'medium', 'low'] },
          survives: { type: 'boolean', description: '假设是否扛住了攻击' },
          note: { type: 'string' },
        },
      },
    },
    unitEconomicsCheck: { type: 'string', description: '单位经济测算是否站得住' },
    complianceCheck: { type: 'string', description: '合规/认证/关税是否被低估' },
    overallVerdict: { type: 'string', enum: ['go', 'conditional-go', 'no-go'] },
    conditions: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
}

// ---------- Phase 1: 机制 / 找源 / 找客户 (parallel) ----------
phase('机制与源客')
log('业务PM线启动:依据调研做机制设计 + 找源 + 找客户')

const [mech, source, customer] = await parallel([
  () => agent(
    `你是业务PM线的【B1 机制设计Agent / 机制设计师】。基于充电桩调研结论,设计让"中国货源→意大利(欧盟)市场"业务能跑起来的交易机制。
约束:${CONSTRAINTS}
调研综合(JSON):${SYN}
请设计撮合/分润/定价/风控/履约等机制,每个机制给出可被决策人调节的参数(parameters,含默认值与说明)。只返回 schema 结构化结果(中文)。`,
    { label: 'B1 机制设计', phase: '机制与源客', schema: MECH_SCHEMA },
  ),
  () => agent(
    `你是业务PM线的【B2 源头/货源Agent / 寻源】。任务:找到可作为"源"的中国充电桩产品/设备/服务供给方(整机厂、模块厂、SaaS平台、ODM等)。
要求:用 WebSearch/WebFetch 找真实公司与公开信息(若未加载先 ToolSearch("select:WebSearch,WebFetch"))。给真实公司名、价值主张、触达方式、关键参数(价格区间/认证/MOQ/交期等)、风险,并附来源URL。
约束:${CONSTRAINTS}
机会方向:- ${OPP}
只返回 schema 结构化结果(中文)。`,
    { label: 'B2 找源', phase: '机制与源客', schema: SOURCE_SCHEMA },
  ),
  () => agent(
    `你是业务PM线的【B3 客户/成交方Agent / BD】。任务:找到意大利(及欧盟)的需求侧成交方(CPO、充电站EPC/安装商、进口/分销商、车企/车队、商业地产/超市/加油站等)。
要求:用 WebSearch/WebFetch 找真实公司与公开信息(若未加载先 ToolSearch("select:WebSearch,WebFetch"))。给真实公司名、需求、付费意愿、决策链、触达方式,并附来源URL。
约束:${CONSTRAINTS}
调研综合(JSON):${SYN}
只返回 schema 结构化结果(中文)。`,
    { label: 'B3 找客户', phase: '机制与源客', schema: CUSTOMER_SCHEMA },
  ),
])

// ---------- Phase 2: 商业模式模拟选优 ----------
phase('模式选优')
const model = await agent(
  `你是业务PM线的【B4 商业模式模拟Agent / 商业建模师】。请基于调研、机制、源、客户,提出 4-6 套候选商业模式并打分选最优。
评分维度(1-5):feasibility可行性 / margin毛利 / scalability可复制 / dealSpeed成交速度 / compliance合规。totalScore 用加权:可行性0.25+毛利0.25+可复制0.2+成交速度0.15+合规0.15(换算到5分制)。
recommended 给出最优模式 + 理由 + 成立前提。每套模式尽量给"单位经济"数字与假设。
约束:${CONSTRAINTS}
调研综合(JSON):${SYN}
机制(JSON):${JSON.stringify(mech)}
源(JSON):${JSON.stringify(source)}
客户(JSON):${JSON.stringify(customer)}
只返回 schema 结构化结果(中文)。`,
  { label: 'B4 商业模式选优', phase: '模式选优', schema: MODEL_SCHEMA, effort: 'high' },
)

// ---------- Phase 3: 流程与成果物 ----------
phase('流程与成果')
const process = await agent(
  `你是业务PM线的【B5 流程设计Agent + B6 成果物Agent】合体。基于推荐的商业模式"${model.recommended ? model.recommended.name : ''}",设计"源→中间环节→客户"的端到端成交流程(每步含负责人/输入/输出/周期/风险点/KPI),并定义每日成果物规格(成果物=产品本身,如选品清单/报价单/解决方案/落地页/客户名单)。
firstDeliverableExample 给出本轮可立刻产出的第一个成果物的具体示例。
推荐模式(JSON):${JSON.stringify(model.recommended || {})}
候选模式(JSON):${JSON.stringify(model.candidateModels || [])}
只返回 schema 结构化结果(中文)。`,
  { label: 'B5+B6 流程与成果物', phase: '流程与成果', schema: PROCESS_SCHEMA, effort: 'high' },
)

// ---------- Phase 4: 业务红军 ----------
phase('业务红军')
const redTeam = await agent(
  `你是【业务红军 / Red Team】。对推荐的商业模式做"杀死它(kill the business)"式压力测试:逐条挑出关键假设并攻击它,判断是否扛得住;核查单位经济是否站得住、合规/认证/关税是否被低估;给出 go / conditional-go / no-go 裁决与前提条件。要严格、具体。
推荐模式 + 候选(JSON):${JSON.stringify(model)}
流程与成果物(JSON):${JSON.stringify(process)}
机制(JSON):${JSON.stringify(mech)}
只返回 schema 结构化结果(中文)。`,
  { label: '业务红军反查', phase: '业务红军', schema: BIZ_REDTEAM_SCHEMA, effort: 'high' },
)

return {
  generatedFor: '充电桩业务PM线(中国货源→意大利/欧盟市场)',
  constraints: CONSTRAINTS,
  mechanisms: mech,
  source,
  customer,
  model,
  process,
  redTeam,
}
