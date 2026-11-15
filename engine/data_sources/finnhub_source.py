"""
FinMaster Finnhub Data Provider
接入华尔街投行共识与市场预期：
1. 华尔街分析师目标价中枢 (Target Mean, High, Low, Implied Upside)
2. 华尔街最新评级分布 (Strong Buy, Buy, Hold, Sell)
3. 财报超预期/不及预期历史 (Earnings Surprises: EPS Actual vs Estimate)
4. 机构专业新闻流 (Company News)
免费层：60 次/分钟。
"""
import os
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FinnhubSource:
    """Finnhub 华尔街预期与分析师共识提供器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY", "")

    def is_configured(self) -> bool:
        key = self.api_key or os.getenv("FINNHUB_API_KEY", "")
        return bool(key and len(key.strip()) > 5)

    def _get_key(self) -> str:
        return (self.api_key or os.getenv("FINNHUB_API_KEY", "")).strip()

    def fetch_wallstreet_consensus(self, ticker: str) -> Dict[str, Any]:
        """抓取华尔街目标价与评级一致预期"""
        if not self.is_configured():
            return {"success": False, "error": "未配置 FINNHUB_API_KEY"}

        key = self._get_key()
        clean_ticker = ticker.strip().upper()
        if ":" in clean_ticker:
            clean_ticker = clean_ticker.split(":")[-1]

        headers = {"X-Finnhub-Token": key}
        target_data = {}
        recommendation = None
        surprises = []

        try:
            # 1. 目标价
            target_url = f"https://finnhub.io/api/v1/stock/price-target?symbol={clean_ticker}"
            resp = requests.get(target_url, headers=headers, timeout=8)
            if resp.status_code == 200:
                target_data = resp.json() or {}

            # 2. 评级分布
            rec_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={clean_ticker}"
            r_resp = requests.get(rec_url, headers=headers, timeout=8)
            if r_resp.status_code == 200:
                rec_list = r_resp.json() or []
                if rec_list:
                    recommendation = rec_list[0]

            # 3. 财报超预期历史 (Earnings Surprises)
            surp_url = f"https://finnhub.io/api/v1/stock/earnings?symbol={clean_ticker}&limit=4"
            s_resp = requests.get(surp_url, headers=headers, timeout=8)
            if s_resp.status_code == 200:
                surprises = s_resp.json() or []

            has_data = bool(target_data.get("targetMean") or recommendation or surprises)
            return {
                "success": has_data,
                "ticker": clean_ticker,
                "price_target": target_data,
                "recommendation": recommendation,
                "earnings_surprises": surprises
            }
        except Exception as e:
            logger.warning(f"获取 Finnhub 数据异常 ({clean_ticker}): {e}")
            return {"success": False, "ticker": clean_ticker, "error": str(e)}

    def to_markdown(self, ticker: str) -> str:
        """格式化为投研专用的华尔街预期 Markdown 卡片"""
        if not self.is_configured():
            return ""

        res = self.fetch_wallstreet_consensus(ticker)
        if not res.get("success"):
            return ""

        ticker_sym = res.get("ticker", ticker)
        pt = res.get("price_target", {})
        rec = res.get("recommendation", {})
        surp = res.get("earnings_surprises", [])

        lines = [
            f"### 🎯 【Finnhub 华尔街卖方预期与分析师共识 · 标的代码: {ticker_sym}】",
            f"- **数据性质**：华尔街投行与专业分析师最新一致性覆盖（Consensus）",
        ]

        # 目标价
        mean_p = pt.get("targetMean")
        high_p = pt.get("targetHigh")
        low_p = pt.get("targetLow")
        median_p = pt.get("targetMedian")
        upd = pt.get("lastUpdated", "")
        if mean_p:
            lines.append(f"- **华尔街目标价中枢**：平均目标价 **`${mean_p:.2f}`** | 中位数 **`${median_p:.2f}`**（区间: `${low_p:.2f}` ~ `${high_p:.2f}`）" + (f" *[更新日: {upd[:10]}]*" if upd else ""))

        # 评级分布
        if rec:
            sb = rec.get("strongBuy", 0)
            b = rec.get("buy", 0)
            h = rec.get("hold", 0)
            s = rec.get("sell", 0)
            ss = rec.get("strongSell", 0)
            total = sb + b + h + s + ss
            if total > 0:
                bull_ratio = (sb + b) / total * 100.0
                lines.append(f"- **投行评级分布 (共 {total} 家机构)**：强力买入 `{sb}` 家 | 买入 `{b}` 家 | 持有 `{h}` 家 | 卖出/跑输 `{s+ss}` 家（**看多比例: {bull_ratio:.0f}%**）")

        # 财报超预期历史
        if surp:
            lines.append("")
            lines.append("#### 📈 近期财报超预期/不及预期记录 (Earnings Surprises):")
            lines.append("| 财报周期 | 实际公布 EPS | 华尔街预期 EPS | 超预期幅度 (Surprise) |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for item in surp[:4]:
                p = item.get("period", "-")
                act = item.get("actual")
                est = item.get("estimate")
                surp_pct = item.get("surprisePercent")
                act_str = f"${act:.2f}" if act is not None else "-"
                est_str = f"${est:.2f}" if est is not None else "-"
                if surp_pct is not None:
                    icon = "🟢" if surp_pct >= 0 else "🔴"
                    pct_str = f"{icon} +{surp_pct:.1f}%" if surp_pct > 0 else f"{icon} {surp_pct:.1f}%"
                else:
                    pct_str = "-"
                lines.append(f"| **{p}** | {act_str} | {est_str} | {pct_str} |")

        lines.append("")
        return "\n".join(lines)


# 全局单例
finnhub_source = FinnhubSource()
