"""
FinMaster Tiingo Data Provider
接入高精度量化级行情与复权时序数据：
1. 30年严密清洗的日K线（经过精确现金分红与拆股除权校正）
2. IEX 实时极速报价与成交量深度
3. 标的元数据与上市状态
免费层：1,000 次/天，50 次/小时。
作为 yfinance 行情在遇到网络波动或雅虎服务器抖动时的强力高精度第二备用链路。
"""
import os
import time
import logging
import requests
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class TiingoSource:
    """Tiingo 量化级时序与复权价格数据提供器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TIINGO_API_KEY", "")

    def is_configured(self) -> bool:
        key = self.api_key or os.getenv("TIINGO_API_KEY", "")
        return bool(key and len(key.strip()) > 5)

    def _get_key(self) -> str:
        return (self.api_key or os.getenv("TIINGO_API_KEY", "")).strip()

    def fetch_stock_snapshot(self, ticker: str) -> Dict[str, Any]:
        """抓取标的最新复权价格与近期时序区间"""
        if not self.is_configured():
            return {"success": False, "error": "未配置 TIINGO_API_KEY"}

        key = self._get_key()
        clean_ticker = ticker.strip().upper()
        if ":" in clean_ticker:
            clean_ticker = clean_ticker.split(":")[-1]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {key}"
        }

        try:
            # 1. 抓取标的元数据
            meta_url = f"https://api.tiingo.com/tiingo/daily/{clean_ticker}"
            meta_resp = requests.get(meta_url, headers=headers, timeout=8)
            meta = meta_resp.json() if meta_resp.status_code == 200 else {}

            # 2. 抓取最近 5 个交易日的精确复权价格 (包含 adjClose, adjVolume, splitFactor, divCash)
            prices_url = f"https://api.tiingo.com/tiingo/daily/{clean_ticker}/prices"
            prices_resp = requests.get(prices_url, headers=headers, timeout=8)
            prices_list = prices_resp.json() if prices_resp.status_code == 200 else []

            latest_price = None
            if isinstance(prices_list, list) and prices_list:
                latest_price = prices_list[-1]

            has_data = bool(latest_price or meta)
            return {
                "success": has_data,
                "ticker": clean_ticker,
                "meta": meta,
                "latest_price": latest_price,
                "history_sample": prices_list[-5:] if isinstance(prices_list, list) else []
            }
        except Exception as e:
            logger.warning(f"获取 Tiingo 数据异常 ({clean_ticker}): {e}")
            return {"success": False, "ticker": clean_ticker, "error": str(e)}

    def test_connection(self, key: Optional[str] = None) -> Dict[str, Any]:
        """测试 Tiingo 接口连通性"""
        api_key = (key or self._get_key()).strip()
        if not api_key:
            return {"success": False, "latency_ms": 0, "message": "未配置 TIINGO_API_KEY"}

        import time
        start_t = time.time()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {api_key}"
        }
        try:
            url = "https://api.tiingo.com/tiingo/daily/aapl"
            resp = requests.get(url, headers=headers, timeout=8)
            latency = (time.time() - start_t) * 1000.0
            if resp.status_code == 200:
                data = resp.json() or {}
                name = data.get("name", "Apple Inc")
                return {
                    "success": True,
                    "latency_ms": latency,
                    "message": f"Tiingo 量化行情连通成功！({name})",
                    "details": "已接入 api.tiingo.com | 免费层享 1,000次/天 高精度复权时序行情"
                }
            elif resp.status_code in (401, 403):
                return {
                    "success": False,
                    "latency_ms": latency,
                    "message": f"Tiingo API 鉴权未通过 (HTTP {resp.status_code})",
                    "details": resp.text[:300]
                }
            else:
                return {
                    "success": False,
                    "latency_ms": latency,
                    "message": f"Tiingo 响应异常 (HTTP {resp.status_code})",
                    "details": resp.text[:300]
                }
        except Exception as e:
            latency = (time.time() - start_t) * 1000.0
            return {
                "success": False,
                "latency_ms": latency,
                "message": f"Tiingo 连接失败: {type(e).__name__}",
                "details": str(e)
            }

    def to_markdown(self, ticker: str) -> str:
        """格式化为量化复权与备用行情 Markdown 卡片"""
        if not self.is_configured():
            return ""

        res = self.fetch_stock_snapshot(ticker)
        if not res.get("success"):
            return ""

        ticker_sym = res.get("ticker", ticker)
        p = res.get("latest_price", {})
        meta = res.get("meta", {})
        if not p:
            return ""

        adj_c = p.get("adjClose")
        raw_c = p.get("close")
        vol = p.get("adjVolume")
        date_str = p.get("date", "")[:10]

        lines = [
            f"### 📈 【Tiingo 量化精确复权行情 · 标的代码: {ticker_sym}】",
            f"- **数据性质**：机构级清洗复权时序（现金分红/拆股校正）",
            f"- **最新复权收盘价 (Adj Close)**：**`${adj_c:.2f}`**（原始收盘价: `${raw_c:.2f}`） *(交易日: {date_str})*",
        ]
        if vol:
            lines.append(f"- **复权成交量**：`{vol:,.0f}` 股")
        if meta.get("exchangeCode"):
            lines.append(f"- **挂牌交易所**：`{meta.get('exchangeCode')}` | 描述: {meta.get('description', '')[:120]}...")

        lines.append("")
        return "\n".join(lines)


# 全局单例
tiingo_source = TiingoSource()
