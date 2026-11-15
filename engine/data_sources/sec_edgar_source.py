"""
FinMaster SEC EDGAR Official Data Provider
通过美国证券交易委员会 (SEC) 官方公开 REST API 穿透获取美股上市企业官方法务披露底稿：
包含最新已生效的 10-K 年报、10-Q 季报、8-K 重大事件披露及 SEC 官方底稿直达链接。
100% 官方权威，零捏造，免费无需 API Key。
"""
import logging
import requests
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

SEC_HEADERS = {
    # SEC 官方合规 User-Agent 格式：SampleApp user@domain.com
    "User-Agent": "FinMasterWorkstation/1.0 (equity-research@finmaster.internal)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}

SEC_TICKER_HEADERS = {
    "User-Agent": "FinMasterWorkstation/1.0 (equity-research@finmaster.internal)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}


class SecEdgarSource:
    """SEC EDGAR 官方申报底稿提供器"""

    def __init__(self):
        self._cik_map: Optional[Dict[str, Dict[str, Any]]] = None

    def _ensure_cik_map(self) -> Dict[str, Dict[str, Any]]:
        """内存缓存全量美股 Ticker 到 CIK 的官方映射表"""
        if self._cik_map is not None:
            return self._cik_map

        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            resp = requests.get(url, headers=SEC_TICKER_HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                mapping = {}
                for item in data.values():
                    t = str(item.get("ticker", "")).strip().upper()
                    if t:
                        mapping[t] = {
                            "cik": str(item.get("cik_str", "")).zfill(10),
                            "title": item.get("title", "")
                        }
                self._cik_map = mapping
                logger.info(f"已加载 SEC 官方企业代码表，共索引 {len(mapping)} 家美股企业")
                return self._cik_map
        except Exception as e:
            logger.warning(f"下载 SEC company_tickers.json 异常: {e}")

        self._cik_map = {}
        return self._cik_map

    def get_cik(self, ticker: str) -> Optional[str]:
        """获取美股企业官方 CIK 代码"""
        mapping = self._ensure_cik_map()
        entry = mapping.get(ticker.upper())
        if entry:
            return entry.get("cik")
        return None

    def fetch_filings(self, ticker: str) -> Dict[str, Any]:
        """从 SEC EDGAR 获取最新官方报表列表 (10-K, 10-Q, 8-K)"""
        clean_ticker = ticker.strip().upper()
        # 剥除 .US 或交易所前缀
        if ":" in clean_ticker:
            clean_ticker = clean_ticker.split(":")[-1]

        cik = self.get_cik(clean_ticker)
        if not cik:
            return {
                "success": False,
                "ticker": clean_ticker,
                "error": f"未在 SEC EDGAR 登记名册中找到标的 {clean_ticker}"
            }

        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            resp = requests.get(url, headers=SEC_HEADERS, timeout=10)
            if resp.status_code != 200:
                return {
                    "success": False,
                    "ticker": clean_ticker,
                    "error": f"SEC API 响应 HTTP {resp.status_code}"
                }

            data = resp.json()
            entity_name = data.get("name", clean_ticker)
            sic_desc = data.get("sicDescription", "")
            filings = data.get("filings", {}).get("recent", {})

            forms = filings.get("form", [])
            filing_dates = filings.get("filingDate", [])
            report_dates = filings.get("reportDate", [])
            accession_nums = filings.get("accessionNumber", [])
            doc_names = filings.get("primaryDocument", [])

            latest_10k = None
            latest_10q = None
            recent_8k_list = []

            for i in range(min(len(forms), 60)):
                form_type = forms[i].upper()
                f_date = filing_dates[i]
                r_date = report_dates[i] if i < len(report_dates) else f_date
                acc_num = accession_nums[i]
                clean_acc = acc_num.replace("-", "")
                doc_name = doc_names[i] if i < len(doc_names) else ""
                doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{clean_acc}/{doc_name}" if doc_name else f"https://www.sec.gov/edgar/browse/?CIK={cik}"

                record = {
                    "form": form_type,
                    "filing_date": f_date,
                    "report_date": r_date,
                    "accession_number": acc_num,
                    "url": doc_url
                }

                if form_type == "10-K" and not latest_10k:
                    latest_10k = record
                elif form_type == "10-Q" and not latest_10q:
                    latest_10q = record
                elif form_type == "8-K" and len(recent_8k_list) < 3:
                    recent_8k_list.append(record)

            edgar_portal_url = f"https://www.sec.gov/edgar/browse/?CIK={cik}"

            return {
                "success": True,
                "ticker": clean_ticker,
                "cik": cik,
                "entity_name": entity_name,
                "industry": sic_desc,
                "edgar_portal_url": edgar_portal_url,
                "latest_10k": latest_10k,
                "latest_10q": latest_10q,
                "recent_8k": recent_8k_list
            }
        except Exception as e:
            logger.exception(f"获取 SEC EDGAR 申报数据异常: {e}")
            return {
                "success": False,
                "ticker": clean_ticker,
                "error": str(e)
            }

    def to_markdown(self, ticker: str) -> str:
        """生成 SEC 官方披露法务底稿清单 Markdown"""
        data = self.fetch_filings(ticker)
        if not data.get("success"):
            return ""

        name = data.get("entity_name", ticker)
        cik = data.get("cik", "")
        portal = data.get("edgar_portal_url", "")
        k10 = data.get("latest_10k")
        q10 = data.get("latest_10q")
        k8_list = data.get("recent_8k", [])

        lines = [
            f"### 🏛️ 【SEC EDGAR 官方信息披露清单 · 法务审计级底稿】",
            f"- **企业登记名称**：{name}（SEC 官方注册 CIK: `{cik}`）",
            f"- **行业分类 (SIC)**：{data.get('industry', '未知')}",
            f"- **SEC 官方档案库直达**：[点击穿透查看官方 EDGAR 档案底稿]({portal})",
            ""
        ]

        if k10:
            lines.append(f"- 📘 **最新年度审计报告 (Form 10-K)**：披露日 `{k10['filing_date']}`（对应财年结束日: `{k10['report_date']}`） · [官方报表原文直达]({k10['url']})")
        if q10:
            lines.append(f"- 📗 **最新季度业绩报告 (Form 10-Q)**：披露日 `{q10['filing_date']}`（对应季度周期: `{q10['report_date']}`） · [官方报表原文直达]({q10['url']})")

        if k8_list:
            lines.append("- 📢 **近期重大突发事项披露 (Form 8-K)**：")
            for k8 in k8_list:
                lines.append(f"  • `{k8['filing_date']}` 申报 · [8-K 原文直达]({k8['url']})")

        lines.append("")
        return "\n".join(lines)


# 全局单例
sec_edgar_source = SecEdgarSource()
