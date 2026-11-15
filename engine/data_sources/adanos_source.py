"""
FinMaster Adanos Data Provider
接入散户注意力、社交情绪与另类预测市场：
1. Reddit / X (FinTwit) 讨论热度 (Buzz Score: 0~100)
2. 看多 vs 看空情绪占比 (Bullish/Bearish %)
3. 讨论趋势监测 (Attention Trend: Rising / Stable / Falling)
4. Polymarket 真实预测市场概率盘口
赋能：格雷厄姆/巴菲特“市场先生情绪钟摆”逆向买点研判。
"""
import os
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AdanosSource:
    """Adanos 社交情绪与另类预测市场提供器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ADANOS_API_KEY", "")

    def is_configured(self) -> bool:
        key = self.api_key or os.getenv("ADANOS_API_KEY", "")
        return bool(key and len(key.strip()) > 5)

    def _get_key(self) -> str:
        return (self.api_key or os.getenv("ADANOS_API_KEY", "")).strip()

    def fetch_market_sentiment(self, ticker: str) -> Dict[str, Any]:
        """抓取社交注意力与情绪指数"""
        if not self.is_configured():
            return {"success": False, "error": "未配置 ADANOS_API_KEY"}

        key = self._get_key()
        clean_ticker = ticker.strip().upper()
        if ":" in clean_ticker:
            clean_ticker = clean_ticker.split(":")[-1]

        headers = {"X-API-Key": key}
        reddit_data = {}
        poly_data = {}

        try:
            # 1. 抓取 Reddit 散户社区情绪
            r_url = f"https://api.adanos.org/reddit/stocks/v1/stock/{clean_ticker}"
            r_resp = requests.get(r_url, headers=headers, timeout=8)
            if r_resp.status_code == 200:
                reddit_data = r_resp.json() or {}

            # 2. 抓取 Polymarket 预测盘口数据
            p_url = f"https://api.adanos.org/polymarket/stocks/v1/stock/{clean_ticker}"
            p_resp = requests.get(p_url, headers=headers, timeout=8)
            if p_resp.status_code == 200:
                poly_data = p_resp.json() or {}

            has_data = bool(reddit_data or poly_data)
            return {
                "success": has_data,
                "ticker": clean_ticker,
                "reddit": reddit_data,
                "polymarket": poly_data
            }
        except Exception as e:
            logger.warning(f"获取 Adanos 情绪数据异常 ({clean_ticker}): {e}")
            return {"success": False, "ticker": clean_ticker, "error": str(e)}

    def to_markdown(self, ticker: str) -> str:
        """格式化为市场先生情绪钟摆 Markdown 卡片"""
        if not self.is_configured():
            return ""

        res = self.fetch_market_sentiment(ticker)
        if not res.get("success"):
            return ""

        ticker_sym = res.get("ticker", ticker)
        reddit = res.get("reddit", {})
        poly = res.get("polymarket", {})

        buzz = reddit.get("buzz_score")
        sent = reddit.get("sentiment_score")
        bull = reddit.get("bullish_pct")
        bear = reddit.get("bearish_pct")
        trend = reddit.get("trend", "stable")

        lines = [
            f"### 🌡️ 【Adanos 市场先生情绪钟摆与另类预测盘口 · 标的代码: {ticker_sym}】",
            f"- **数据性质**：全球散户社交讨论热度、看多看空偏向及预测市场真实真金白银盘口",
        ]

        if buzz is not None:
            trend_icon = "🔥 讨论激增 (Rising)" if trend == "rising" else ("❄️ 关注降温 (Falling)" if trend == "falling" else "⚖️ 保持平稳")
            lines.append(f"- **散户关注度指数 (Buzz Score)**：`{buzz}/100` · 当前趋势: **{trend_icon}**")

        if sent is not None or bull is not None:
            sent_val = sent if sent is not None else 0.0
            sentiment_tag = "极度贪婪/过度乐观" if sent_val > 0.5 else ("极度恐慌/散户出清" if sent_val < -0.5 else "中性理性平衡")
            bull_str = f"{bull*100:.0f}%" if bull is not None else "-"
            bear_str = f"{bear*100:.0f}%" if bear is not None else "-"
            lines.append(f"- **多空舆情偏向**：看多比例 `{bull_str}` vs 看空比例 `{bear_str}` (综合评分: `{sent_val:+.2f}` → **{sentiment_tag}**)")

        # Polymarket 预测盘口
        if poly and poly.get("markets"):
            lines.append("- **Polymarket 真实资金预测盘口**：")
            for m in poly.get("markets", [])[:2]:
                title = m.get("question", m.get("title", ""))
                prob = m.get("probability")
                prob_str = f"{prob*100:.1f}%" if prob is not None else "-"
                lines.append(f"  • {title} → 市场隐含发生概率: **{prob_str}**")

        lines.append("")
        return "\n".join(lines)


# 全局单例
adanos_source = AdanosSource()
