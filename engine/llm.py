"""
FinMaster LLM Unified Client
支持 Google Gemini 官方 SDK 与 Direct REST API 降级调用，原生开启 Google Search Grounding。
"""
import os
import json
import logging
from typing import Generator, Optional, Dict, Any

logger = logging.getLogger("finmaster.llm")

# 自动加载环境变量
try:
    from dotenv import load_dotenv
    _env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    load_dotenv(_env_path)
    load_dotenv()  # fallback to current directory
except ImportError:
    pass


class GeminiClient:
    """Gemini 统一客户端，支持流式输出与 Google Search 联网检索"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, temperature: float = 0.2):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("DEFAULT_GEMINI_MODEL", "gemini-2.5-flash")
        self.temperature = temperature

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def test_connection(self) -> Dict[str, Any]:
        """
        测试 API 连通性与模型可用性。
        优先测试基础模型推演能力，再诊断 Google Search 联网配额。
        """
        if not self.is_configured():
            return {
                "success": False,
                "latency_ms": 0.0,
                "message": "未配置 GEMINI_API_KEY",
                "details": "请在 finmaster/.env 中配置 GEMINI_API_KEY 或在侧边栏填入 Key。"
            }

        import time
        import requests

        start_t = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # 1. 首先测试基础模型推理连通性（不消耗极其宝贵的 Google Search 每日配额）
        payload_base: Dict[str, Any] = {
            "contents": [{"parts": [{"text": "请简明回复数字：1+1等于几？"}]}],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 20
            }
        }
        try:
            resp_base = requests.post(
                url,
                json=payload_base,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            latency = (time.time() - start_t) * 1000.0

            if resp_base.status_code != 200:
                err_json = resp_base.text
                if resp_base.status_code == 429:
                    return {
                        "success": False,
                        "latency_ms": round(latency, 1),
                        "message": "模型调用频次受限 (HTTP 429)",
                        "details": "基础模型请求频次触发限流，请稍候 60 秒后重试。"
                    }
                return {
                    "success": False,
                    "latency_ms": round(latency, 1),
                    "message": f"API 返回错误 (HTTP {resp_base.status_code})",
                    "details": err_json[:400]
                }

            # 提取基础回复
            ans = ""
            try:
                data = resp_base.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        ans = parts[0].get("text", "").strip()
            except Exception:
                pass

            # 2. 诊断 Google Search 联网配额状态
            payload_search: Dict[str, Any] = {
                "contents": [{"parts": [{"text": "ping"}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {"maxOutputTokens": 5}
            }
            search_status_str = "正常可用"
            try:
                resp_search = requests.post(url, json=payload_search, headers={"Content-Type": "application/json"}, timeout=8)
                if resp_search.status_code == 429:
                    search_status_str = "⚠️ 今日免费 20 次配额已达上限（系统已启用自动纯模型保底推演）"
            except Exception:
                search_status_str = "网络检测超时"

            resp_info = f"响应: {ans}" if ans else "推理响应正常"
            return {
                "success": True,
                "latency_ms": round(latency, 1),
                "message": f"Gemini 连接成功！{resp_info} (耗时 {latency:.0f}ms)",
                "details": f"模型: {self.model} (正常可用) | Google Search 联网状态: {search_status_str}"
            }

        except Exception as e:
            latency = (time.time() - start_t) * 1000.0
            return {
                "success": False,
                "latency_ms": round(latency, 1),
                "message": f"网络请求异常: {type(e).__name__}",
                "details": str(e)
            }

    def generate_content_stream(self, prompt: str, enable_search: bool = True) -> Generator[str, None, None]:
        """
        流式生成文本内容。
        内置智能防 429 削峰、自动指数退避重试与 Google Search 配额耗尽保底降级机制。
        """
        if not self.is_configured():
            yield "⚠️ **未配置 GEMINI_API_KEY**\n\n请在界面左侧侧边栏填入您的有效 Gemini API Key 即可启动投研生成。"
            return

        import requests
        import time

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent?alt=sse&key={self.api_key}"
        
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 8192
            }
        }
        if enable_search:
            payload["tools"] = [{"google_search": {}}]

        headers = {"Content-Type": "application/json"}
        
        max_retries = 4
        backoff_delays = [4.0, 8.0, 15.0, 25.0]
        response = None
        search_downgraded = False

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers, stream=True, timeout=120)

                # 命中 429 频次限制或临时网络/代理通道中断 (500, 502 Bad Gateway, 503, 504)
                if response.status_code in (429, 500, 502, 503, 504):
                    err_text = response.text

                    # 如果开启了 Google Search 导致 429（免费版每日上限仅 20 次）
                    # 立即无缝降级为无 Search 纯模型深度推理，绝不中断投研！
                    if response.status_code == 429 and "tools" in payload and not search_downgraded:
                        payload.pop("tools", None)
                        search_downgraded = True
                        logger.warning("Google Search 免费配额已满，自动降级为纯模型推演模式")
                        yield "\n\n💡 *[智能配额保底] 检测到今日 Google Search 免费联网配额 (20次/日) 已耗尽，系统已无缝降级为大模型内置深度知识推理模式继续生成...*\n\n"
                        time.sleep(1.0)
                        continue

                    if attempt < max_retries - 1:
                        delay = backoff_delays[attempt]
                        is_tunnel_eof = (response.status_code == 502 or "tunnel" in err_text.lower() or "eof" in err_text.lower())
                        if is_tunnel_eof:
                            status_desc = "代理网络通道瞬断 (HTTP 502 / EOF)"
                        elif response.status_code == 429:
                            status_desc = "API 频次受限 (HTTP 429)"
                        else:
                            status_desc = f"服务端网关临时繁忙 (HTTP {response.status_code})"

                        logger.warning(f"触发 {status_desc}，第 {attempt+1}/{max_retries-1} 次自动退避重连，等待 {delay}s...")
                        yield f"\n\n⏳ *[智能防抖动重连] 检测到 {status_desc}，正在重建代理通道重试 ({attempt+1}/{max_retries-1})，等待 {int(delay)} 秒...*\n\n"
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Gemini API 频次超限或网关错误且耗尽重试次数: {response.status_code} {err_text}")
                        if response.status_code == 429:
                            yield f"\n\n❌ **Gemini API 频次达到上限 (HTTP 429 / RESOURCE_EXHAUSTED)**\n\n已自动重试 3 次均未恢复。这通常是因为免费层 15 RPM（每分钟请求数）被占满。\n\n**建议解决方案**：\n1. 请等待 60-90 秒后再次点击运行；\n2. 或前往 Google AI Studio 绑定支付方式开通按量计费（千次并发且费用极低）。"
                        else:
                            yield f"\n\n❌ **网络代理通道中断 (HTTP {response.status_code})**:\n```\n{err_text[:500]}\n```\n\n💡 **恢复建议**：本地网络代理与 Google 服务器发生偶发中断，请检查代理工具连接后点击重新生成。"
                        return

                if response.status_code != 200:
                    err_text = response.text
                    logger.error(f"Gemini API 错误 [{response.status_code}]: {err_text}")
                    yield f"\n\n❌ **Gemini API 请求失败 (HTTP {response.status_code})**:\n```\n{err_text[:500]}\n```"
                    return

                # 成功 200 OK，退出重试循环
                break

            except requests.exceptions.RequestException as req_err:
                if attempt < max_retries - 1:
                    delay = backoff_delays[attempt]
                    logger.warning(f"网络连接抖动 ({req_err})，等待 {delay}s 重试...")
                    yield f"\n\n⏳ *网络短暂抖动，正在自动重试 ({attempt+1}/{max_retries-1})...*\n\n"
                    time.sleep(delay)
                    continue
                else:
                    yield f"\n\n❌ **网络请求超时或连接失败**: {str(req_err)}"
                    return

        if not response or response.status_code != 200:
            return

        # 强制指定响应编码为 UTF-8，彻底杜绝 ISO-8859-1 (Latin-1) 导致的中文乱码
        response.encoding = "utf-8"

        # 解析 SSE 流 (按原始字节读取，显式进行 UTF-8 解码)
        try:
            for raw_line in response.iter_lines(decode_unicode=False):
                if not raw_line:
                    continue
                try:
                    line = raw_line.decode("utf-8", errors="replace")
                except Exception:
                    continue

                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data_json = json.loads(data_str)
                        candidates = data_json.get("candidates", [])
                        if candidates:
                            content = candidates[0].get("content", {})
                            parts = content.get("parts", [])
                            for part in parts:
                                text_chunk = part.get("text", "")
                                if text_chunk:
                                    yield text_chunk
                    except Exception:
                        continue
        except Exception as e:
            logger.exception("解析 Gemini 流式响应发生异常")
            yield f"\n\n❌ **流式读取中断异常**: {str(e)}"

    def generate_content_sync(self, prompt: str, enable_search: bool = True) -> str:
        """同步一次性生成完整文本"""
        chunks = []
        for chunk in self.generate_content_stream(prompt, enable_search=enable_search):
            chunks.append(chunk)
        return "".join(chunks)
