"""
FinMaster Data Hub (多源金融数据调度中枢)
统一调度：
1. yfinance: 第三方行情快照 + 过去 4 季度财务数据（显示供应方及可用的行情时间）
2. SEC EDGAR: 官方合规法源底稿 (10-K/10-Q/8-K 直达链接)
3. AI 深度搜索 (Tavily / Google Search): 定性商业模式动态、竞争格局、突发事件与未上市独角兽估值
4. (预留第二步扩展接口: Finnhub 目标价/Surprise, FMP DCF/ROIC, Adanos 情绪/Polymarket)
"""
import logging
from typing import Dict, Any, Optional, List

from .yfinance_source import yfinance_source
from .sec_edgar_source import sec_edgar_source
from .fred_source import fred_source
from .finnhub_source import finnhub_source
from .fmp_source import fmp_source
from .adanos_source import adanos_source
from .tiingo_source import tiingo_source
from ..search_provider import search_manager

logger = logging.getLogger(__name__)


class DataHub:
    """多源金融数据中台调度器"""

    def get_financial_grounding(
        self,
        target: str,
        focus: str = "",
        enable_search: bool = False,
        search_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        根据标的名称，并发/流水线融合结构化硬核数据与定性 AI 搜索，生成最权威的研报底稿。
        支持 search_mode:
        - 'off': 默认关闭搜索（纯八维金融底座秒级极速响应，同时关闭 Gemini 联网）
        - 'smart': 智能自适应调度（优先在无搜索模式下获取硬核财报；仅在标的无财报/未上市或明确要求突发事件时按需开启）
        - 'on': 强制开启搜索（获取全网最新突发新闻与动态）
        """
        target_clean = target.strip()
        ticker = yfinance_source.resolve_ticker(target_clean)

        # 决定当前生效的搜索模式 (默认为 off)
        if search_mode:
            resolved_mode = str(search_mode).strip().lower()
            if resolved_mode not in ("off", "smart", "on"):
                resolved_mode = "smart" if resolved_mode in ("auto", "true") else "off"
        else:
            resolved_mode = "smart" if enable_search else "off"
        search_provider = search_manager.get_provider().strip().lower()
        search_disabled = search_provider in ("none", "off")

        parts: List[str] = []
        active_sources: List[str] = []

        # 1. 第一级：yfinance 第三方结构化行情与财务数据
        yf_md = ""
        has_yf = False
        if ticker:
            try:
                yf_md = yfinance_source.to_markdown(ticker)
                if yf_md:
                    parts.append(yf_md)
                    active_sources.append("yfinance 结构化财务三张表")
                    has_yf = True
            except Exception as e:
                logger.warning(f"获取 yfinance 数据失败: {e}")

        # 2. 第二级：SEC EDGAR 官方申报底稿 (美股公司穿透)
        sec_md = ""
        has_sec = False
        if ticker and ("." not in ticker or ticker.endswith(".US")):
            clean_us_ticker = ticker.split(".")[0].strip()
            try:
                sec_md = sec_edgar_source.to_markdown(clean_us_ticker)
                if sec_md:
                    parts.append(sec_md)
                    active_sources.append("SEC EDGAR 官方法务底稿")
                    has_sec = True
            except Exception as e:
                logger.warning(f"获取 SEC EDGAR 底稿失败: {e}")

        # 3. 第三级：FRED 圣路易斯联储官方主权级宏观与估值折现基准 (无风险利率 Rf + 收益率利差)
        has_fred = False
        try:
            fred_md = fred_source.to_markdown()
            if fred_md:
                parts.append(fred_md)
                active_sources.append("FRED 官方宏观基准与折现率")
                has_fred = True
        except Exception as e:
            logger.warning(f"获取 FRED 宏观底座失败: {e}")

        # 4. 第四级（选配插件）：Finnhub 华尔街投行一致预期与财报 Surprise
        has_finnhub = False
        if ticker and finnhub_source.is_configured():
            try:
                fh_md = finnhub_source.to_markdown(ticker)
                if fh_md:
                    parts.append(fh_md)
                    active_sources.append("Finnhub 华尔街预期与Surprise")
                    has_finnhub = True
            except Exception as e:
                logger.warning(f"获取 Finnhub 数据失败: {e}")

        # 5. 第五级（选配插件）：FMP 专业基本面建模与自动化 DCF
        has_fmp = False
        if ticker and fmp_source.is_configured():
            try:
                fmp_md = fmp_source.to_markdown(ticker)
                if fmp_md:
                    parts.append(fmp_md)
                    active_sources.append("FMP ROIC/DCF建模")
                    has_fmp = True
            except Exception as e:
                logger.warning(f"获取 FMP 数据失败: {e}")

        # 6. 第六级（选配插件）：Adanos 市场先生社交情绪与另类预测盘口
        has_adanos = False
        if ticker and adanos_source.is_configured():
            try:
                adanos_md = adanos_source.to_markdown(ticker)
                if adanos_md:
                    parts.append(adanos_md)
                    active_sources.append("Adanos 市场先生情绪钟摆")
                    has_adanos = True
            except Exception as e:
                logger.warning(f"获取 Adanos 数据失败: {e}")

        # 7. 第七级（选配插件）：Tiingo 量化级精确复权行情与备用链路
        has_tiingo = False
        if ticker and tiingo_source.is_configured():
            try:
                tiingo_md = tiingo_source.to_markdown(ticker)
                if tiingo_md:
                    parts.append(tiingo_md)
                    active_sources.append("Tiingo 量化复权行情")
                    has_tiingo = True
            except Exception as e:
                logger.warning(f"获取 Tiingo 数据失败: {e}")

        # 8. 第八级：判断是否真正需要启动网络搜索
        # 统计是否已经具备核心财务基本面
        has_core_financials = bool(has_yf or has_tiingo or has_sec or has_fmp)
        
        # 突发事件/新闻诉求意图识别
        news_keywords = [
            "新闻", "突发", "诉讼", "制裁", "黑天鹅", "传闻", "最新动态", "近期事件",
            "发布会", "调查", "裁员", "违约", "破产", "政策变动", "重组", "反垄断",
            "news", "breaking", "lawsuit", "sanction", "scandal", "antitrust", "event"
        ]
        query_text = f"{target_clean} {focus}".lower()
        is_news_requested = any(kw in query_text for kw in news_keywords)

        should_run_search = False
        gemini_search_allowed = False
        search_decision_reason = ""

        if resolved_mode == "off" or search_disabled:
            should_run_search = False
            gemini_search_allowed = False
            if resolved_mode == "off":
                search_decision_reason = "本次分析：关闭全网搜索（依托权威金融底座秒级出具）"
            else:
                search_decision_reason = "系统搜索提供器配置为 none：已关闭所有全网搜索"
        elif resolved_mode == "smart":
            # 智能调度核心逻辑：优先在关闭搜索以及 Gemini 搜索的情况下获取数据
            if has_core_financials and not is_news_requested:
                should_run_search = False
                gemini_search_allowed = False
                search_decision_reason = "智能决策：标的已具备权威硬核财务与行情底座，已自动关闭搜索节省时延"
            else:
                should_run_search = True
                search_decision_reason = "智能决策：标的无公开上市财报数据，按需启动检索" if not has_core_financials else "智能决策：检测到突发新闻/黑天鹅研究意图，按需启动检索"
        else: # "on"
            should_run_search = True
            search_decision_reason = "用户配置：强制开启全网实时新闻与商业动态检索"

        search_md = ""
        has_search = False
        search_provider_name = ""

        if should_run_search:
            try:
                search_ctx = search_manager.get_financial_context(target=target_clean, focus=focus)
                search_provider_name = search_ctx.get("provider_used", "联网检索")
                search_md = search_ctx.get("grounding_text", "")
                if search_md:
                    parts.append("### 🌐 【全球财经与战略事件最新定性洞察】\n" + search_md)
                    active_sources.append(search_provider_name)
                    has_search = True
                    gemini_search_allowed = False
                else:
                    gemini_search_allowed = True
            except Exception as e:
                logger.warning(f"调用联网搜索失败: {e}")
                gemini_search_allowed = True
        else:
            gemini_search_allowed = False

        # 组装最终 Grounding Markdown
        final_grounding = "\n\n---\n\n".join(parts) if parts else ""

        # 构造用户直观可见的数据源徽标
        badge_list = []
        if has_yf:
            badge_list.append("📊 yfinance 结构化行情与三张表")
        if has_sec:
            badge_list.append("🏛️ SEC EDGAR 官方法务底稿")
        if has_fred:
            badge_list.append("🇺🇸 FRED 宏观折现基准")
        if has_finnhub:
            badge_list.append("🎯 Finnhub 华尔街预期")
        if has_fmp:
            badge_list.append("🧮 FMP ROIC/DCF")
        if has_adanos:
            badge_list.append("🌡️ Adanos 情绪盘口")
        if has_tiingo:
            badge_list.append("📈 Tiingo 量化复权")
        if has_search:
            badge_list.append(f"⚡ {search_provider_name}")
        elif resolved_mode == "smart" and has_core_financials:
            badge_list.append("⚡ 智能极速模式 (免搜索)")
        elif resolved_mode == "off" or search_disabled:
            badge_list.append("⚡ 纯金融底座秒级模式")
        if not badge_list:
            badge_list.append("🤖 纯模型深度知识模式")

        summary_badge = " · ".join(badge_list)

        return {
            "target": target_clean,
            "ticker": ticker,
            "has_yf": has_yf,
            "has_sec": has_sec,
            "has_fred": has_fred,
            "has_finnhub": has_finnhub,
            "has_fmp": has_fmp,
            "has_adanos": has_adanos,
            "has_tiingo": has_tiingo,
            "has_search": has_search,
            "search_triggered": has_search,
            "search_mode": resolved_mode,
            "search_decision_reason": search_decision_reason,
            "gemini_search_allowed": gemini_search_allowed,
            "active_sources": active_sources,
            "summary_badge": summary_badge,
            "grounding_text": final_grounding
        }


# 全局单例
data_hub = DataHub()
