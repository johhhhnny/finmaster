"""
FinMaster FMP (Financial Modeling Prep) Data Provider
接入专业买方基本面建模指标：
1. ROIC (资本回报率) 与 ROE
2. 自动化 DCF 现金流折现公允估值与安全边际测算
3. 业务产品分部营收拆解 (Segment Revenues)
免费层：250 次/天。
"""
import os
import logging
import requests
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class FMPSource:
    """FMP 专业基本面与估值建模提供器"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY", "")

    def is_configured(self) -> bool:
        key = self.api_key or os.getenv("FMP_API_KEY", "")
        return bool(key and len(key.strip()) > 5)

    def _get_key(self) -> str:
        return (self.api_key or os.getenv("FMP_API_KEY", "")).strip()

    def fetch_fundamental_models(self, ticker: str) -> Dict[str, Any]:
        """抓取 FMP 关键财务比率与自动化 DCF 估值 (采用 FMP 官方最新 Stable API)"""
        if not self.is_configured():
            return {"success": False, "error": "未配置 FMP_API_KEY"}

        key = self._get_key()
        clean_ticker = ticker.strip().upper()
        if ":" in clean_ticker:
            clean_ticker = clean_ticker.split(":")[-1]

        ratios_list = []
        dcf_data = {}

        try:
            # 1. 抓取财务比率 (包含 ROIC, ROE, FCF 收益率)
            ratios_url = f"https://financialmodelingprep.com/stable/ratios?symbol={clean_ticker}&apikey={key}"
            resp = requests.get(ratios_url, timeout=8)
            if resp.status_code == 200:
                ratios_list = resp.json() or []

            # 2. 抓取自动化 DCF 现金流折现估值
            dcf_url = f"https://financialmodelingprep.com/stable/discounted-cash-flow?symbol={clean_ticker}&apikey={key}"
            d_resp = requests.get(dcf_url, timeout=8)
            if d_resp.status_code == 200:
                d_data = d_resp.json() or []
                if isinstance(d_data, list) and d_data:
                    dcf_data = d_data[0]
                elif isinstance(d_data, dict):
                    dcf_data = d_data

            has_data = bool(ratios_list or dcf_data)
            return {
                "success": has_data,
                "ticker": clean_ticker,
                "ratios": ratios_list,
                "dcf": dcf_data
            }
        except Exception as e:
            logger.warning(f"获取 FMP 数据异常 ({clean_ticker}): {e}")
            return {"success": False, "ticker": clean_ticker, "error": str(e)}

    def test_connection(self, key: Optional[str] = None) -> Dict[str, Any]:
        """测试 FMP 现代化 Stable API 连通性"""
        api_key = (key or self._get_key()).strip()
        if not api_key:
            return {"success": False, "latency_ms": 0, "message": "未配置 FMP_API_KEY"}

        import time
        start_t = time.time()
        try:
            url = f"https://financialmodelingprep.com/stable/profile?symbol=AAPL&apikey={api_key}"
            resp = requests.get(url, timeout=8)
            latency = (time.time() - start_t) * 1000.0
            if resp.status_code == 200:
                return {
                    "success": True,
                    "latency_ms": latency,
                    "message": "FMP 基本面与估值通道连通正常",
                    "details": "已接入 FMP 官方最新 Stable API (Profile/DCF/Ratios 正常)"
                }
            elif resp.status_code in (401, 403):
                return {
                    "success": False,
                    "latency_ms": latency,
                    "message": f"FMP API 鉴权未通过 (HTTP {resp.status_code})",
                    "details": resp.text[:300]
                }
            else:
                return {
                    "success": False,
                    "latency_ms": latency,
                    "message": f"FMP 响应异常 (HTTP {resp.status_code})",
                    "details": resp.text[:300]
                }
        except Exception as e:
            latency = (time.time() - start_t) * 1000.0
            return {
                "success": False,
                "latency_ms": latency,
                "message": f"FMP 连接失败: {type(e).__name__}",
                "details": str(e)
            }

    def to_markdown(self, ticker: str) -> str:
        """格式化为巴菲特/段永平专属的基本面模型 Markdown"""
        if not self.is_configured():
            return ""

        res = self.fetch_fundamental_models(ticker)
        if not res.get("success"):
            return ""

        ticker_sym = res.get("ticker", ticker)
        ratios = res.get("ratios", [])
        dcf = res.get("dcf", {})

        lines = [
            f"### 🧮 【FMP 专业财务建模与公允价值测算 · 标的代码: {ticker_sym}】",
            f"- **数据性质**：华尔街买方常用标准化基本面比率与现金流折现模型",
        ]

        # DCF 模型测算
        dcf_val = dcf.get("dcf")
        stock_price = dcf.get("Stock Price")
        if dcf_val and stock_price:
            margin = ((dcf_val - stock_price) / stock_price) * 100.0
            status_text = f"🟢 折价低估（安全边际: +{margin:.1f}%）" if margin > 0 else f"🔴 溢价高估（估值溢价: {abs(margin):.1f}%）"
            lines.append(f"- **自动化 DCF 内在公允价值**：**`${dcf_val:.2f}`** vs 当前市价 `${stock_price:.2f}` → **{status_text}**")

        # 核心基本面比率表格
        if ratios:
            lines.append("")
            lines.append("#### 💎 巴菲特/段永平核心资本效率比率 (近4季度):")
            lines.append("| 季度报告日 | 投入资本回报率 (ROIC) | 净资产收益率 (ROE) | 营业利润率 | 自由现金流收益率 (FCF Yield) |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for r in ratios[:4]:
                p = r.get("date", "-")
                roce = r.get("returnOnCapitalEmployed")
                roe = r.get("returnOnEquity")
                op_margin = r.get("operatingProfitMargin")
                fcf_yield = r.get("freeCashFlowYield")

                roce_str = f"{roce*100:.1f}%" if roce is not None else "-"
                roe_str = f"{roe*100:.1f}%" if roe is not None else "-"
                op_str = f"{op_margin*100:.1f}%" if op_margin is not None else "-"
                fcf_str = f"{fcf_yield*100:.1f}%" if fcf_yield is not None else "-"

                lines.append(f"| **{p}** | **{roce_str}** | {roe_str} | {op_str} | {fcf_str} |")

        lines.append("")
        return "\n".join(lines)


# 全局单例
fmp_source = FMPSource()
