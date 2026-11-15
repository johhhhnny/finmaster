"""
FinMaster Skill Manager
解析并管理所有 21 个投资研究技能（Skills），提供分类树、元数据映射与动态参数提取。
"""
import os
import re
from typing import Dict, List, Any, Optional

SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills"))

# 21 个技能的五大分类映射表与元数据
SKILL_METADATA_REGISTRY: Dict[str, Dict[str, Any]] = {
    # 1. 🔍 初筛与赛道漏斗 (Discovery & Screening)
    "industry-funnel": {
        "title": "行业漏斗筛选",
        "category": "1. 🔍 初筛与赛道漏斗",
        "icon": "🌪️",
        "description": "从全市场/全产业链初筛到精选 3 家核心公司的价值投资精选流程。",
        "mode": "funnel",
        "inputs": [
            {"key": "target", "label": "研究行业/赛道", "placeholder": "例如: 全球半导体设备、中国白酒、工业软件", "required": True},
            {"key": "criteria", "label": "特定约束或筛选偏好", "placeholder": "例如: 剔除重资产负债率超50%、必须有自由现金流", "required": False}
        ]
    },
    "quality-screen": {
        "title": "去劣筛选（7条指标）",
        "category": "1. 🔍 初筛与赛道漏斗",
        "icon": "🛡️",
        "description": "通过 7 条巴菲特硬性指标快速排除非一流公司，避免陷入价值陷阱。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "待体检标的 (公司名或代码)", "placeholder": "例如: 特斯拉, 英伟达, 贵州茅台", "required": True}
        ]
    },
    "bottleneck-hunter": {
        "title": "供应链瓶颈猎手",
        "category": "1. 🔍 初筛与赛道漏斗",
        "icon": "⚡",
        "description": "AI 驱动的全球产业链瓶颈识别与卡位套利分析框架。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "产业链环节或标的", "placeholder": "例如: 先进封装 CoWoS、半导体光刻胶、高压直流换流阀", "required": True}
        ]
    },
    "era-alpha": {
        "title": "时代α捕手",
        "category": "1. 🔍 初筛与赛道漏斗",
        "icon": "🚀",
        "description": "高增长核心资产的识别-验证-持有框架，捕捉时代技术范式红利。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "时代资产/公司标的", "placeholder": "例如: 亚马逊、Meta、特斯拉、台积电", "required": True}
        ]
    },

    # 2. 🏢 深度个股研究 (Deep Research)
    "investment-team": {
        "title": "四大师投研团队（旗舰）",
        "category": "2. 🏢 深度个股研究",
        "icon": "👥",
        "description": "巴菲特（财务与估值）+ 段永平（商业模式）+ 芒格（竞争与逆向）+ 李录（管理层与治理）四 Agent 并行分析。",
        "mode": "multi_agent",
        "inputs": [
            {"key": "target", "label": "研究标的 (公司名或代码)", "placeholder": "例如: 谷歌 / GOOGL, 苹果 / AAPL, 腾讯控股", "required": True},
            {"key": "focus", "label": "重点关注议题 (可选)", "placeholder": "例如: 资本开支激增对自由现金流的影响、反垄断诉讼终局", "required": False}
        ]
    },
    "earnings-team": {
        "title": "财报精读团队（四大师并行）",
        "category": "2. 🏢 深度个股研究",
        "icon": "📑",
        "description": "四大师并行深度解读最新财报一手资料，穿透真实盈利并产出发布版研报。",
        "mode": "multi_agent",
        "inputs": [
            {"key": "target", "label": "公司名称或股票代码", "placeholder": "例如: 谷歌 / GOOGL, 微软 / MSFT", "required": True},
            {"key": "period", "label": "财报周期", "placeholder": "例如: 2026Q3 (最新季度)", "required": True}
        ]
    },
    "earnings-review": {
        "title": "财报单篇精读",
        "category": "2. 🏢 深度个股研究",
        "icon": "🔍",
        "description": "一手财报资料深度穿透解读，对比历史财报并核算所有者现金流真实质量。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "公司名称或股票代码", "placeholder": "例如: 苹果, 阿里巴巴", "required": True},
            {"key": "period", "label": "财报周期", "placeholder": "例如: 2026Q3", "required": True}
        ]
    },
    "deep-company-series": {
        "title": "深度公司系列（看懂XX公司）",
        "category": "2. 🏢 深度个股研究",
        "icon": "📚",
        "description": "3-8 篇连载长文式拆解一家伟大公司，全景穿透历史沿革、商业机理与终局。",
        "mode": "multi_agent",
        "inputs": [
            {"key": "target", "label": "深度拆解标的", "placeholder": "例如: 伯克希尔哈撒韦、拼多多、台积电", "required": True}
        ]
    },
    "management-deep-dive": {
        "title": "管理层纵深研究",
        "category": "2. 🏢 深度个股研究",
        "icon": "👔",
        "description": "买股票就是买人：创始人与管理层画像、薪酬绑定、资本配置信誉与应对危机韧性。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "公司名与管理层姓名", "placeholder": "例如: 谷歌 (Sundar Pichai), 微软 (Satya Nadella)", "required": True}
        ]
    },
    "private-company-research": {
        "title": "未上市公司深度研究",
        "category": "2. 🏢 深度个股研究",
        "icon": "🦄",
        "description": "未上市独角兽企业多 Agent 并行研究框架，穿透一级市场估值与商业闭环。",
        "mode": "multi_agent",
        "inputs": [
            {"key": "target", "label": "未上市企业名称", "placeholder": "例如: OpenAI, SpaceX, 字节跳动, Anthropic", "required": True}
        ]
    },
    "investment-research": {
        "title": "四大师综合分析（单篇）",
        "category": "2. 🏢 深度个股研究",
        "icon": "🏛️",
        "description": "巴菲特-芒格-段永平-李录四大师理念融合的单篇深度备忘录框架。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "研究标的 (公司名或代码)", "placeholder": "例如: 腾讯控股, 贵州茅台", "required": True}
        ]
    },
    "industry-research": {
        "title": "行业投资研究",
        "category": "2. 🏢 深度个股研究",
        "icon": "🌐",
        "description": "产业链全景扫描 + 四大师个股分析整合框架。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "行业领域名称", "placeholder": "例如: 云计算基础设施、新能源汽车、消费电子", "required": True}
        ]
    },

    # 3. ⚖️ 估值与投资准则 (Valuation & Checklists)
    "investment-checklist": {
        "title": "巴菲特买入前 Checklist",
        "category": "3. ⚖️ 估值与投资准则",
        "icon": "✅",
        "description": "严格按照巴菲特买入前 10 条硬性准则逐项审视，给出清晰通过/存疑/一票否决裁定。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "拟买入公司标的", "placeholder": "例如: 谷歌、苹果、比亚迪", "required": True}
        ]
    },
    "income-investment": {
        "title": "收息投资（分红股评估）",
        "category": "3. ⚖️ 估值与投资准则",
        "icon": "💰",
        "description": "持久与机会型分红资产审计框架，计算真实股息覆盖倍数与现金派息持续性。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "高分红资产/标的", "placeholder": "例如: 中国移动、长江电力、神华", "required": True}
        ]
    },
    "dyp-ask": {
        "title": "段永平问答：以他的方式思考",
        "category": "3. ⚖️ 估值与投资准则",
        "icon": "💬",
        "description": "用段永平的商业本质逻辑回答你的投资疑问（本分、平常心、对的事情、十年后还会不会在）。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "涉及公司或生意 (可选)", "placeholder": "例如: 拼多多, 苹果, 腾讯", "required": False},
            {"key": "question", "label": "你的具体投资困惑或问题", "placeholder": "例如: 拼多多现在加大商家扶持导致短期利润承压，段永平怎么看？", "required": True}
        ]
    },

    # 4. ⏱️ 投后跟踪与风控 (Post-Investment Tracking)
    "news-pulse": {
        "title": "公司新闻脉搏（异动归因）",
        "category": "4. ⏱️ 投后跟踪与风控",
        "icon": "💓",
        "description": "股价异动或重大事件发生时快速归因：侦察监管/对手/情绪，判断是否触发论文重审。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "异动标的公司", "placeholder": "例如: 谷歌, 特斯拉, 拼多多", "required": True},
            {"key": "event", "label": "异动事件或日期 (可选)", "placeholder": "例如: 财报后暴跌10%、司法部发布反垄断处罚方案", "required": False}
        ]
    },
    "thesis-tracker": {
        "title": "投资论文追踪看板",
        "category": "4. ⏱️ 投后跟踪与风控",
        "icon": "📌",
        "description": "买入后的核心纪律系统：持续监控核心假设指标，定期对照买入逻辑验证是否成立。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "已持仓公司", "placeholder": "例如: 谷歌, 腾讯", "required": True},
            {"key": "thesis", "label": "初始买入论文/核心假定 (可选)", "placeholder": "例如: 云业务年化增长30%+自研芯片降低推理成本", "required": False}
        ]
    },
    "thesis-drift": {
        "title": "投资论文漂移检测",
        "category": "4. ⏱️ 投后跟踪与风控",
        "icon": "🧭",
        "description": "分清'事实变化'与'措辞变化'，检测管理层指引是否偏离初衷，防范价值陷阱。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "关注公司标的", "placeholder": "例如: 英特尔、波音、耐克", "required": True}
        ]
    },
    "portfolio-review": {
        "title": "组合管理与健康度体检",
        "category": "4. ⏱️ 投后跟踪与风控",
        "icon": "📊",
        "description": "从'研究公司'跨越到'管理组合'：仓位集中度、能力圈边界、现金储备与机会成本比对。",
        "mode": "single_agent",
        "inputs": [
            {"key": "holdings", "label": "持仓列表与大致权重", "placeholder": "例如: 腾讯 35%, 谷歌 30%, 茅台 20%, 现金 15%", "required": True}
        ]
    },

    # 5. 📢 成果转化与发布 (Publishing & Formats)
    "wechat-article": {
        "title": "微信公众号文章转化",
        "category": "5. 📢 成果转化与发布",
        "icon": "📱",
        "description": "作者-编辑-读者三角色协作，将严谨学术研报转化为适合微信公号阅读的爆款排版文章。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "公司或研报主题", "placeholder": "例如: 谷歌重资产转型、巴菲特买入清单复盘", "required": True},
            {"key": "content", "label": "源研报内容或核心观点 (可选)", "type": "textarea", "placeholder": "可直接粘贴完整研报内容，或留空让 AI 结合最新数据创作", "required": False}
        ]
    },
    "financial-data": {
        "title": "数据规范与交叉验证",
        "category": "3. ⚖️ 估值与投资准则",
        "icon": "🔢",
        "description": "财务数据获取与独立两源交叉验证规范指南。",
        "mode": "single_agent",
        "inputs": [
            {"key": "target", "label": "核验标的代码与指标", "placeholder": "例如: GOOGL 营收与市盈率", "required": True}
        ]
    }
}


class SkillManager:
    """管理所有投资研究技能的核心管理器"""

    def __init__(self, skills_dir: str = SKILLS_DIR):
        self.skills_dir = skills_dir
        self.registry = SKILL_METADATA_REGISTRY

    def list_categories(self) -> List[str]:
        """返回所有分类列表（已排序）"""
        cats = sorted(list({meta["category"] for meta in self.registry.values()}))
        return cats

    def get_skills_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按分类获取技能列表"""
        res = []
        for skill_id, meta in self.registry.items():
            if meta["category"] == category:
                item = dict(meta)
                item["id"] = skill_id
                res.append(item)
        return res

    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """获取单个技能元数据"""
        if skill_id in self.registry:
            meta = dict(self.registry[skill_id])
            meta["id"] = skill_id
            return meta
        return None

    def get_skill_raw_content(self, skill_id: str) -> str:
        """读取技能的原始 Markdown 提示词文件"""
        md_path = os.path.join(self.skills_dir, f"{skill_id}.md")
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def build_prompt(self, skill_id: str, user_params: Dict[str, Any]) -> str:
        """
        组装该技能的完整提示词：
        融合技能原生 Markdown 指令 + 用户输入的动态参数 + 实时环境日期 + 防污染铁律
        """
        raw_markdown = self.get_skill_raw_content(skill_id)
        meta = self.get_skill(skill_id) or {}
        
        param_summary = "\n".join([f"- **{k}**: {v}" for k, v in user_params.items() if v])
        
        system_injection = f"""
================================================================================
【FinMaster 智能投研系统统一前置指令】
- 今日基准日期：系统实时日期（请始终以真实外部最新日期与市场收盘价为准）
- 技能标识：{skill_id}（{meta.get('title', skill_id)}）
- 用户本次指定的输入参数：
{param_summary}

【防本地数据污染铁律（最高优先级）】：
1. 严禁从历史记忆或未经核验的旧语料中编造股价、市值与财报数据！
2. 涉及最新股价、市值、市盈率、财报（10-Q/10-K）数据时，必须依托最新联网检索，确保最新交易日收盘的真实市场行情。
3. 财务与估值推演必须严谨清晰，指明数据出处与时间戳。
================================================================================

【以下为该技能的标准研究方法论与完整执行规范】：

{raw_markdown}
"""
        return system_injection


# 单例实例
skill_manager = SkillManager()
