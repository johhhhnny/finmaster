"""
FinMaster FRED (Federal Reserve Economic Data) Data Provider
接入圣路易斯联储官方主权级宏观经济底座：
1. DGS10: 10年期美国国债收益率（买方估值模型不可或缺的权威无风险利率 Rf）
2. T10Y2Y: 10年期减2年期美债收益率利差（宏观衰退与流动性拐点预警雷达）
3. FEDFUNDS: 美联储联邦基金有效利率
4. CPIAUCSL: 美国城市消费者物价指数（通胀趋势基准）
支持零配置直连与专属 FRED_API_KEY，且内置 yfinance Treasury 双通道容灾保障。
"""
import os
import time
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class FredSource:
    """圣路易斯联邦储备银行 (FRED) 官方宏观数据提供器"""

    SERIES_CONFIG = {
        "DGS10": {
            "name": "10年期美国国债收益率 (无风险利率 Rf)",
            "unit": "%",
            "desc": "DCF 估值折现率模型中的核心无风险收益率锚点"
        },
        "T10Y2Y": {
            "name": "10Y-2Y 美债收益率利差 (衰退预警雷达)",
            "unit": "%",
            "desc": "利差倒挂（小于0）通常被视为未来6~18个月经济衰退的前瞻信号"
        },
        "FEDFUNDS": {
            "name": "美联储联邦基金有效利率 (Fed Funds Rate)",
            "unit": "%",
            "desc": "全球美元流动性与资金成本定价基准"
        },
        "CPIAUCSL": {
            "name": "美国消费者物价指数 (CPI 通胀指数)",
            "unit": "点",
            "desc": "衡量购买力贬损与美联储降息空间的核心通胀指标"
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FRED_API_KEY", "")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def is_configured(self) -> bool:
        """FRED 始终具备免 Key 直连能力"""
        return True

    def _get_key(self) -> str:
        return (self.api_key or os.getenv("FRED_API_KEY", "")).strip()

    def fetch_series_latest(self, series_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定宏观序列最新有效观测值。
        多级调度：
        1. 优先调用官方 JSON REST API (需 FRED_API_KEY)
        2. 降级至官方免 Key CSV 通道
        3. 兜底至 yfinance Treasury (^TNX, ^IRX)
        """
        key = self._get_key()
        # 1. 若配置了专属 FRED_API_KEY，尝试官方 JSON REST API
        if key and len(key) >= 16:
            try:
                url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={key}&file_type=json&sort_order=desc&limit=5"
                resp = requests.get(url, headers=self.headers, timeout=6)
                if resp.status_code == 200:
                    data = resp.json() or {}
                    obs = data.get("observations", [])
                    for item in obs:
                        val_str = item.get("value", "").strip()
                        if val_str and val_str != ".":
                            try:
                                return {
                                    "series_id": series_id,
                                    "date": item.get("date"),
                                    "value": float(val_str),
                                    "source": "FRED_API"
                                }
                            except ValueError:
                                continue
            except Exception as e:
                logger.debug(f"FRED API Key 请求失败，转入官方免配置直连通道: {e}")

        # 2. 官方免配置直连 CSV 通道
        try:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
            resp = requests.get(url, headers=self.headers, timeout=6)
            if resp.status_code == 200 and not resp.text.startswith("<!DOCTYPE"):
                lines = resp.text.strip().split("\n")
                for line in reversed(lines[1:]):
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        d_str = parts[0].strip()
                        v_str = parts[1].strip()
                        if v_str and v_str != ".":
                            try:
                                return {
                                    "series_id": series_id,
                                    "date": d_str,
                                    "value": float(v_str),
                                    "source": "FRED_CSV"
                                }
                            except ValueError:
                                continue
        except Exception as e:
            logger.debug(f"FRED CSV 通道异常 ({series_id}): {e}")

        # 3. yfinance Treasury 容灾兜底通道
        if series_id == "DGS10":
            try:
                import yfinance as yf
                tnx = yf.Ticker("^TNX")
                last_p = getattr(tnx.fast_info, "last_price", None)
                if last_p is not None and last_p > 0:
                    return {
                        "series_id": "DGS10",
                        "date": None,
                        "value": round(float(last_p), 2),
                        "source": "yfinance_TNX_fallback",
                        "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds")
                    }
            except Exception as e:
                logger.debug(f"yfinance 宏观收益率兜底失败: {e}")

        return None

    def fetch_macro_overview(self) -> Dict[str, Any]:
        """抓取核心宏观利率、利差与流动性指标概览"""
        results: Dict[str, Any] = {}
        for s_id in self.SERIES_CONFIG.keys():
            res = self.fetch_series_latest(s_id)
            if res:
                results[s_id] = res

        has_data = bool("DGS10" in results or "FEDFUNDS" in results)
        return {
            "success": has_data,
            "data": results,
            "timestamp": time.time()
        }

    def test_connection(self, key: Optional[str] = None) -> Dict[str, Any]:
        """测试 FRED 圣路易斯联储宏观数据通道连通性"""
        start_t = time.time()
        api_key = key if key is not None else self._get_key()
        
        # 如果传入了测试 Key，先测试 API Key
        if api_key and len(api_key) >= 16:
            try:
                url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={api_key}&file_type=json&sort_order=desc&limit=2"
                resp = requests.get(url, headers=self.headers, timeout=6)
                latency = (time.time() - start_t) * 1000.0
                if resp.status_code == 200:
                    data = resp.json() or {}
                    obs = data.get("observations", [])
                    val = obs[0].get("value") if obs else "-"
                    return {
                        "success": True,
                        "latency_ms": latency,
                        "message": f"FRED 官方 API 连通成功！10年期美债收益率: {val}%",
                        "details": f"已接入 api.stlouisfed.org 官方数据源 | 专属 API Key 验证通过"
                    }
                else:
                    return {
                        "success": False,
                        "latency_ms": latency,
                        "message": f"FRED API 响应异常 (HTTP {resp.status_code})",
                        "details": resp.text[:300]
                    }
            except Exception as e:
                pass

        # 走统一自愈调度通道
        res = self.fetch_series_latest("DGS10")
        latency = (time.time() - start_t) * 1000.0

        if res and res.get("value") is not None:
            src_text = "FRED 官方数据" if res.get("source") != "yfinance_TNX_fallback" else "Yahoo Finance ^TNX 第三方备用数据"
            if res.get("source") == "yfinance_TNX_fallback":
                src_text += "（仅作近似代理，非官方国债收益率观测）"
            return {
                "success": True,
                "latency_ms": latency,
                "message": f"宏观利率数据通道可用！10年期收益率参考值: {res['value']:.2f}%",
                "details": f"观测日期: {res.get('date') or '供应方未提供'} | 来源: {src_text} | 序列: DGS10"
            }
        else:
            return {
                "success": False,
                "latency_ms": latency,
                "message": "FRED 宏观数据抓取异常",
                "details": "请检查网络环境或在设置中配置专属 FRED_API_KEY。"
            }

    def to_markdown(self) -> str:
        """生成格式化宏观与估值无风险折现率 Markdown 卡片"""
        overview = self.fetch_macro_overview()
        if not overview.get("success"):
            return ""

        data = overview.get("data", {})
        retrieved_at = overview.get("timestamp")
        lines = [
            "### 🏛️ 【宏观与利率基准】",
            "- **来源说明**：宏观序列优先来自 FRED；DGS10 不可用时可能回退到 Yahoo Finance ^TNX 第三方近似值。",
        ]
        if retrieved_at:
            lines.append(
                f"- **本次获取时间**：`{datetime.fromtimestamp(retrieved_at, timezone.utc).isoformat(timespec='seconds')}`（UTC）"
            )

        # 1. 10年期国债收益率 (Rf)
        dgs10 = data.get("DGS10")
        if dgs10:
            is_proxy = dgs10.get("source") == "yfinance_TNX_fallback"
            source = "Yahoo Finance ^TNX 第三方近似值，非 FRED 官方观测" if is_proxy else "FRED 官方观测"
            observation_date = dgs10.get("date") or "供应方未提供"
            lines.append(
                f"- 🇺🇸 **10年期美国国债收益率参考值**：**`{dgs10['value']:.2f}%`** "
                f"*(来源: {source}; 观测日期: {observation_date})*"
            )
            if is_proxy:
                lines.append("  • *该值仅为市场代理数据，不应视作官方国债收益率观测。*")
            else:
                lines.append(
                    f"  • *估值参考：可将 `{dgs10['value']:.2f}%` 作为无风险利率估值输入之一，并结合数据日期进行判断。*"
                )

        # 2. 10Y-2Y 倒挂利差 (衰退雷达)
        t10y2y = data.get("T10Y2Y")
        if t10y2y:
            val = t10y2y["value"]
            if val < 0:
                spread_status = f"🔴 **利差倒挂 ({val:.2f}%)** · 宏观衰退前瞻警报！警惕流动性紧缩与资产杀估值"
            elif val < 0.15:
                spread_status = f"🟡 **曲线极度平坦 ({val:.2f}%)** · 货币政策处于紧缩转向的临界窗口"
            else:
                spread_status = f"🟢 **曲线正常陡峭化 (+{val:.2f}%)** · 收益率结构健康，无倒挂风险"
            lines.append(f"- 📈 **10Y-2Y 美债利差 (衰退预警雷达)**：{spread_status} *(观测日: {t10y2y['date']})*")

        # 3. 联邦基金利率 (Fed Funds Rate)
        fed = data.get("FEDFUNDS")
        if fed:
            lines.append(f"- 🏛️ **美联储联邦基金有效利率 (Fed Funds Rate)**：**`{fed['value']:.2f}%`** *(对应月份: {fed['date'][:7]})*")

        lines.append("")
        return "\n".join(lines)


# 全局单例
fred_source = FredSource()
