"""
FinMaster Data Hub (多源金融数据调度中枢)
统一调度：
1. yfinance: 实时行情报价 + 过去 4 季度完整三张表 (营收/净利/FCF/CapEx/净现金)
2. SEC EDGAR: 官方合规法源底稿 (10-K/10-Q/8-K 直达链接)
3. AI 深度搜索 (Tavily / Google Search): 定性商业模式动态、竞争格局、突发事件与未上市独角兽估值
4. (预留第二步扩展接口: Finnhub 目标价/Surprise, FMP DCF/ROIC, Adanos 情绪/Polymarket)
"""
import logging
from typing import Dict, Any, Optional, List

from .yfinance_source import yfinance_source
from .sec_edgar_source import sec_edgar_source
from ..search_provider import search_manager

logger = logging.getLogger(__name__)


class DataHub:
    """多源金融数据中台调度器"""

    def get_financial_grounding(
        self,
        target: str,
        focus: str = "",
        enable_search: bool = True
    ) -> Dict[str, Any]:
        """
        根据标的名称，并发/流水线融合结构化硬核数据与定性 AI 搜索，生成最权威的研报底稿。
        """
        target_clean = target.strip()
        ticker = yfinance_source.resolve_ticker(target_clean)

        parts: List[str] = []
        active_sources: List[str] = []

        # 1. 第一级：yfinance 结构化数据 (100% 真实行情 + 近4季度三张表)
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

        # 3. 第三级：AI 深度搜索 (Tavily / Google Search) 提取定性行业情报与突发事件
        search_md = ""
        has_search = False
        search_provider_name = ""
        if enable_search:
            try:
                search_ctx = search_manager.get_financial_context(target=target_clean, focus=focus)
                search_provider_name = search_ctx.get("provider_used", "联网检索")
                search_md = search_ctx.get("grounding_text", "")
                if search_md:
                    parts.append("### 🌐 【全球财经与战略事件最新定性洞察】\n" + search_md)
                    active_sources.append(search_provider_name)
                    has_search = True
            except Exception as e:
                logger.warning(f"调用联网搜索失败: {e}")

        # 组装最终 Grounding Markdown
        final_grounding = "\n\n---\n\n".join(parts) if parts else ""

        # 构造用户直观可见的数据源徽标
        badge_list = []
        if has_yf:
            badge_list.append("📊 yfinance 结构化行情与三张表")
        if has_sec:
            badge_list.append("🏛️ SEC EDGAR 官方法务底稿")
        if has_search:
            badge_list.append(f"⚡ {search_provider_name}")
        if not badge_list:
            badge_list.append("🤖 纯模型深度知识模式")

        summary_badge = " · ".join(badge_list)

        return {
            "target": target_clean,
            "ticker": ticker,
            "has_yf": has_yf,
            "has_sec": has_sec,
            "has_search": has_search,
            "active_sources": active_sources,
            "summary_badge": summary_badge,
            "grounding_text": final_grounding
        }


# 全局单例
data_hub = DataHub()
