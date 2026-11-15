"""
FinMaster 统一外部搜索引擎服务模块 (Unified Search Provider)
支持 Tavily AI 搜索、Gemini 原生 Google Search、DuckDuckGo 免密检索及多级智能降级调度。
解决 Gemini 免费层每日 20 次 Grounding 限制，保障研报数据真实、永不中断。
"""
import os
import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("finmaster.search")


class SearchResult:
    """搜索结果标准化封装"""
    def __init__(
        self,
        success: bool,
        provider: str,
        query: str,
        answer: str = "",
        results: Optional[List[Dict[str, str]]] = None,
        error: str = "",
        latency_ms: float = 0.0
    ):
        self.success = success
        self.provider = provider
        self.query = query
        self.answer = answer
        self.results = results or []
        self.error = error
        self.latency_ms = latency_ms

    def to_markdown(self) -> str:
        """格式化为注入大模型 Prompt 的标准化权威上下文数据块"""
        if not self.success or (not self.answer and not self.results):
            return ""

        md_parts = [
            f"### 🌐 实时互联网财务与行情检索数据 (来源: {self.provider})",
            f"> 检索基准时间: {time.strftime('%Y-%m-%d')} | 耗时: {self.latency_ms:.0f}ms | 状态: 实时真实数据 (Anti-Contamination)",
            f"> 检索检索词: `{self.query}`\n"
        ]

        if self.answer:
            md_parts.append(f"**核心行情与财报速览 (AI 摘要)**:\n{self.answer}\n")

        if self.results:
            md_parts.append("**一手公告、财报与财经参考源**:")
            for i, item in enumerate(self.results[:5], 1):
                title = item.get("title", f"参考源 {i}").strip()
                url = item.get("url", "").strip()
                content = item.get("content", "").strip().replace("\n", " ")
                if len(content) > 300:
                    content = content[:300] + "..."
                if url:
                    md_parts.append(f"{i}. [{title}]({url}): {content}")
                else:
                    md_parts.append(f"{i}. **{title}**: {content}")

        return "\n".join(md_parts)


class TavilySearcher:
    """Tavily AI 搜索引擎客户端 (专为 LLM 设计的高质量金融检索)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def test_connection(self, key_override: Optional[str] = None) -> Dict[str, Any]:
        """测试 Tavily API 连通性与密钥有效性"""
        key = key_override or self.api_key
        if not key or len(key.strip()) < 5:
            return {
                "success": False,
                "latency_ms": 0.0,
                "message": "未配置 TAVILY_API_KEY",
                "details": "请前往 https://tavily.com 免费注册获取 API Key（每月赠送 1,000 次调用）。"
            }

        import requests
        start_t = time.time()
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": key.strip(),
                    "query": "AAPL stock price",
                    "max_results": 1,
                    "search_depth": "basic"
                },
                timeout=12
            )
            latency = (time.time() - start_t) * 1000.0
            if resp.status_code == 200:
                data = resp.json()
                results_cnt = len(data.get("results", []))
                return {
                    "success": True,
                    "latency_ms": round(latency, 1),
                    "message": f"Tavily 连接成功！检索响应正常 (耗时 {latency:.0f}ms)",
                    "details": f"API 状态: HTTP 200 | 返回有效测试结果: {results_cnt} 条 | 免费 1,000次/月 配额有效。"
                }
            elif resp.status_code == 401:
                return {
                    "success": False,
                    "latency_ms": round(latency, 1),
                    "message": "Tavily API Key 无效或未授权 (HTTP 401)",
                    "details": "请检查输入的 Tavily Key 是否正确无误。"
                }
            elif resp.status_code == 429:
                return {
                    "success": False,
                    "latency_ms": round(latency, 1),
                    "message": "Tavily 请求频次达到上限 (HTTP 429)",
                    "details": "本月免费调用额度已用尽或请求过于频繁。"
                }
            else:
                return {
                    "success": False,
                    "latency_ms": round(latency, 1),
                    "message": f"Tavily API 报错 (HTTP {resp.status_code})",
                    "details": resp.text[:300]
                }
        except Exception as e:
            latency = (time.time() - start_t) * 1000.0
            return {
                "success": False,
                "latency_ms": round(latency, 1),
                "message": f"Tavily 连接异常: {type(e).__name__}",
                "details": str(e)
            }

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_answer: bool = True
    ) -> SearchResult:
        """执行 Tavily 检索并返回结构化结果"""
        if not self.is_configured():
            return SearchResult(
                success=False,
                provider="Tavily",
                query=query,
                error="TAVILY_API_KEY 未配置"
            )

        import requests
        start_t = time.time()
        try:
            payload = {
                "api_key": self.api_key.strip(),
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": include_answer
            }
            resp = requests.post("https://api.tavily.com/search", json=payload, timeout=20)
            latency = (time.time() - start_t) * 1000.0

            if resp.status_code == 200:
                data = resp.json()
                raw_results = data.get("results", [])
                answer = data.get("answer", "")
                parsed = []
                for item in raw_results:
                    parsed.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                        "score": str(item.get("score", 0))
                    })
                return SearchResult(
                    success=True,
                    provider="Tavily AI Search",
                    query=query,
                    answer=answer,
                    results=parsed,
                    latency_ms=latency
                )
            else:
                return SearchResult(
                    success=False,
                    provider="Tavily AI Search",
                    query=query,
                    error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    latency_ms=(time.time() - start_t) * 1000.0
                )
        except Exception as e:
            return SearchResult(
                success=False,
                provider="Tavily AI Search",
                query=query,
                error=str(e),
                latency_ms=(time.time() - start_t) * 1000.0
            )


class DuckDuckGoSearcher:
    """DuckDuckGo 免密检索兜底客户端 (无需 API Key)"""

    def search(self, query: str, max_results: int = 4) -> SearchResult:
        start_t = time.time()
        try:
            from ddgs import DDGS
            with DDGS(timeout=10) as ddgs:
                results_gen = ddgs.text(query, max_results=max_results)
                parsed = []
                for r in results_gen:
                    parsed.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "content": r.get("body", "")
                    })
                latency = (time.time() - start_t) * 1000.0
                if parsed:
                    return SearchResult(
                        success=True,
                        provider="DuckDuckGo Search",
                        query=query,
                        results=parsed,
                        latency_ms=latency
                    )
        except Exception as e:
            logger.warning(f"DuckDuckGo (ddgs) 检索失败: {e}")

        # 尝试备用 duckduckgo_search 模块
        try:
            from duckduckgo_search import DDGS as LegacyDDGS
            with LegacyDDGS(timeout=10) as ddgs:
                results_gen = ddgs.text(query, max_results=max_results)
                parsed = []
                for r in results_gen:
                    parsed.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "content": r.get("body", "")
                    })
                latency = (time.time() - start_t) * 1000.0
                if parsed:
                    return SearchResult(
                        success=True,
                        provider="DuckDuckGo Search",
                        query=query,
                        results=parsed,
                        latency_ms=latency
                    )
        except Exception as e2:
            logger.warning(f"DuckDuckGo (legacy) 检索失败: {e2}")

        return SearchResult(
            success=False,
            provider="DuckDuckGo Search",
            query=query,
            error="DuckDuckGo 检索超时或网络受限",
            latency_ms=(time.time() - start_t) * 1000.0
        )


class SearchManager:
    """
    统一搜索引擎调度管理器
    支持 Provider:
    - 'auto': 智能多级回退 (优先 Tavily -> 失败/无Key自动回退 Google Search -> 兜底 DDG)
    - 'tavily': 强制使用 Tavily AI 搜索 (1,000次/月 免费，推荐)
    - 'google': 强制使用 Gemini 原生 Google Search Grounding
    - 'duckduckgo': 强制使用 DuckDuckGo 免Key搜索
    - 'none': 关闭任何搜索联网
    """

    def __init__(self):
        self.tavily = TavilySearcher()
        self.ddg = DuckDuckGoSearcher()

    def get_provider(self) -> str:
        return os.getenv("SEARCH_PROVIDER", "auto").lower()

    def get_financial_context(
        self,
        target: str,
        focus: str = "",
        provider_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        针对特定金融投资标的执行针对性多维联网检索，返回结构化上下文与大模型调用指令。
        返回字典:
        {
            "use_gemini_grounding": bool,  # 是否交由 Gemini 原生 tools: [{"google_search": {}}] 执行
            "grounding_text": str,          # 注入 Prompt 的真实数据 Markdown
            "provider_used": str,          # 实际生效的搜索引擎名称
            "success": bool                # 是否成功获取事实数据
        }
        """
        provider = (provider_override or self.get_provider()).lower()

        # 1. 如果显式关闭联网
        if provider == "none":
            return {
                "use_gemini_grounding": False,
                "grounding_text": "",
                "provider_used": "无联网 (纯模型推演)",
                "success": True
            }

        # 2. 如果强制指定使用 Gemini 原生 Google Search
        if provider == "google":
            return {
                "use_gemini_grounding": True,
                "grounding_text": "",
                "provider_used": "Gemini 原生 Google Search",
                "success": True
            }

        # 3. 构造高质量金融针对性检索 Query
        query = f"{target.strip()} 股票代码 最新收盘价 总市值 季度财报 营收 净利润 自由现金流 2025 2026"
        if focus:
            query += f" {focus.strip()}"

        # 4. 如果指定 Tavily 或处于 Auto 模式且配置了 Tavily Key
        if provider in ("tavily", "auto") and self.tavily.is_configured():
            logger.info(f"使用 Tavily 检索标的真实金融数据: {target}")
            res = self.tavily.search(query=query, max_results=5, search_depth="basic", include_answer=True)
            if res.success:
                return {
                    "use_gemini_grounding": False,
                    "grounding_text": res.to_markdown(),
                    "provider_used": "Tavily AI Search (1,000次/月 独立免限配额)",
                    "success": True
                }
            else:
                logger.warning(f"Tavily 检索失败 ({res.error})，启动自动降级...")

        # 5. 如果是 auto 模式且 Tavily 失败或未配 Key：回退到 Gemini 原生 Google Search
        if provider == "auto":
            logger.info("未配置 Tavily 或调用受阻，自动回退至 Gemini 原生 Google Search Grounding")
            return {
                "use_gemini_grounding": True,
                "grounding_text": "",
                "provider_used": "Gemini 原生 Google Search (自动保底)",
                "success": True
            }

        # 6. 如果指定 DuckDuckGo
        if provider == "duckduckgo":
            logger.info(f"使用 DuckDuckGo 检索标的: {target}")
            res = self.ddg.search(query=query, max_results=4)
            if res.success:
                return {
                    "use_gemini_grounding": False,
                    "grounding_text": res.to_markdown(),
                    "provider_used": "DuckDuckGo 免密搜索",
                    "success": True
                }

        # 7. 兜底回退
        return {
            "use_gemini_grounding": True,
            "grounding_text": "",
            "provider_used": "Gemini 原生 Google Search (备用降级)",
            "success": True
        }


# 全局单例
search_manager = SearchManager()
