"""
FinMaster 环境变量与系统配置管理模块
负责 .env 文件的持久化读写与运行时环境变量同步。
"""
import os
from typing import Tuple

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_app_env():
    """自动加载本地 .env 配置，若不存在则回退至父目录 .env"""
    try:
        from dotenv import load_dotenv
        local_env = os.path.join(CURRENT_DIR, ".env")
        if os.path.exists(local_env):
            load_dotenv(local_env)
        load_dotenv()
    except ImportError:
        pass

from typing import Tuple, Optional, Dict

def get_current_config() -> Tuple[str, str, float]:
    """获取当前生效的 API Key、模型名称与多样性参数"""
    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-3.5-flash-lite")
    try:
        temp = float(os.getenv("DEFAULT_TEMPERATURE", "0.2"))
    except ValueError:
        temp = 0.2
    return api_key, model, temp

def get_search_config() -> Tuple[str, str]:
    """获取当前生效的搜索引擎类型与 Tavily API Key"""
    provider = os.getenv("SEARCH_PROVIDER", "auto")
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    return provider, tavily_key

def get_sec_email() -> str:
    """获取配置的 SEC EDGAR 联络邮箱"""
    return os.getenv("SEC_CONTACT_EMAIL", "")

def get_fred_key() -> str:
    """获取配置的 FRED 圣路易斯联储 API Key"""
    return os.getenv("FRED_API_KEY", "")

def get_plugin_keys() -> Dict[str, str]:
    """获取扩展插件数据源密钥 (Finnhub, FMP, Adanos, Tiingo)"""
    return {
        "finnhub": os.getenv("FINNHUB_API_KEY", ""),
        "fmp": os.getenv("FMP_API_KEY", ""),
        "adanos": os.getenv("ADANOS_API_KEY", ""),
        "tiingo": os.getenv("TIINGO_API_KEY", "")
    }

def save_env_config(
    key: str,
    model: str,
    temp: float,
    tavily_key: Optional[str] = None,
    search_provider: Optional[str] = None,
    sec_email: Optional[str] = None,
    finnhub_key: Optional[str] = None,
    fmp_key: Optional[str] = None,
    adanos_key: Optional[str] = None,
    fred_key: Optional[str] = None,
    tiingo_key: Optional[str] = None
) -> bool:
    """安全保存配置至 .env 文件并同步更新内存环境变量"""
    env_file = os.path.join(CURRENT_DIR, ".env")
    lines = []
    existing_keys = set()
    
    current_tavily = tavily_key if tavily_key is not None else os.getenv("TAVILY_API_KEY", "")
    current_provider = search_provider if search_provider is not None else os.getenv("SEARCH_PROVIDER", "auto")
    current_sec_email = sec_email if sec_email is not None else os.getenv("SEC_CONTACT_EMAIL", "")
    current_finnhub = finnhub_key if finnhub_key is not None else os.getenv("FINNHUB_API_KEY", "")
    current_fmp = fmp_key if fmp_key is not None else os.getenv("FMP_API_KEY", "")
    current_adanos = adanos_key if adanos_key is not None else os.getenv("ADANOS_API_KEY", "")
    current_fred = fred_key if fred_key is not None else os.getenv("FRED_API_KEY", "")
    current_tiingo = tiingo_key if tiingo_key is not None else os.getenv("TIINGO_API_KEY", "")

    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("GEMINI_API_KEY="):
                    lines.append(f"GEMINI_API_KEY={key}\n")
                    existing_keys.add("GEMINI_API_KEY")
                elif stripped.startswith("DEFAULT_GEMINI_MODEL="):
                    lines.append(f"DEFAULT_GEMINI_MODEL={model}\n")
                    existing_keys.add("DEFAULT_GEMINI_MODEL")
                elif stripped.startswith("DEFAULT_TEMPERATURE="):
                    lines.append(f"DEFAULT_TEMPERATURE={temp}\n")
                    existing_keys.add("DEFAULT_TEMPERATURE")
                elif stripped.startswith("TAVILY_API_KEY="):
                    lines.append(f"TAVILY_API_KEY={current_tavily}\n")
                    existing_keys.add("TAVILY_API_KEY")
                elif stripped.startswith("SEARCH_PROVIDER="):
                    lines.append(f"SEARCH_PROVIDER={current_provider}\n")
                    existing_keys.add("SEARCH_PROVIDER")
                elif stripped.startswith("SEC_CONTACT_EMAIL="):
                    lines.append(f"SEC_CONTACT_EMAIL={current_sec_email}\n")
                    existing_keys.add("SEC_CONTACT_EMAIL")
                elif stripped.startswith("FINNHUB_API_KEY="):
                    lines.append(f"FINNHUB_API_KEY={current_finnhub}\n")
                    existing_keys.add("FINNHUB_API_KEY")
                elif stripped.startswith("FMP_API_KEY="):
                    lines.append(f"FMP_API_KEY={current_fmp}\n")
                    existing_keys.add("FMP_API_KEY")
                elif stripped.startswith("ADANOS_API_KEY="):
                    lines.append(f"ADANOS_API_KEY={current_adanos}\n")
                    existing_keys.add("ADANOS_API_KEY")
                elif stripped.startswith("FRED_API_KEY="):
                    lines.append(f"FRED_API_KEY={current_fred}\n")
                    existing_keys.add("FRED_API_KEY")
                elif stripped.startswith("TIINGO_API_KEY="):
                    lines.append(f"TIINGO_API_KEY={current_tiingo}\n")
                    existing_keys.add("TIINGO_API_KEY")
                else:
                    lines.append(line)

    if "GEMINI_API_KEY" not in existing_keys:
        lines.append(f"GEMINI_API_KEY={key}\n")
    if "DEFAULT_GEMINI_MODEL" not in existing_keys:
        lines.append(f"DEFAULT_GEMINI_MODEL={model}\n")
    if "DEFAULT_TEMPERATURE" not in existing_keys:
        lines.append(f"DEFAULT_TEMPERATURE={temp}\n")
    if "TAVILY_API_KEY" not in existing_keys and current_tavily is not None:
        lines.append(f"TAVILY_API_KEY={current_tavily}\n")
    if "SEARCH_PROVIDER" not in existing_keys and current_provider is not None:
        lines.append(f"SEARCH_PROVIDER={current_provider}\n")
    if "SEC_CONTACT_EMAIL" not in existing_keys and current_sec_email:
        lines.append(f"SEC_CONTACT_EMAIL={current_sec_email}\n")
    if "FINNHUB_API_KEY" not in existing_keys and current_finnhub:
        lines.append(f"FINNHUB_API_KEY={current_finnhub}\n")
    if "FMP_API_KEY" not in existing_keys and current_fmp:
        lines.append(f"FMP_API_KEY={current_fmp}\n")
    if "ADANOS_API_KEY" not in existing_keys and current_adanos:
        lines.append(f"ADANOS_API_KEY={current_adanos}\n")
    if "FRED_API_KEY" not in existing_keys and current_fred:
        lines.append(f"FRED_API_KEY={current_fred}\n")
    if "TIINGO_API_KEY" not in existing_keys and current_tiingo:
        lines.append(f"TIINGO_API_KEY={current_tiingo}\n")

    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    os.environ["GEMINI_API_KEY"] = key
    os.environ["DEFAULT_GEMINI_MODEL"] = model
    os.environ["DEFAULT_TEMPERATURE"] = str(temp)
    if current_tavily is not None:
        os.environ["TAVILY_API_KEY"] = current_tavily
    if current_provider is not None:
        os.environ["SEARCH_PROVIDER"] = current_provider
    if current_sec_email:
        os.environ["SEC_CONTACT_EMAIL"] = current_sec_email
    if current_finnhub:
        os.environ["FINNHUB_API_KEY"] = current_finnhub
    if current_fmp:
        os.environ["FMP_API_KEY"] = current_fmp
    if current_adanos:
        os.environ["ADANOS_API_KEY"] = current_adanos
    if current_fred:
        os.environ["FRED_API_KEY"] = current_fred
    if current_tiingo:
        os.environ["TIINGO_API_KEY"] = current_tiingo

    # 同步刷新各单例对象的内存 key
    try:
        from engine.search_provider import search_manager
        search_manager.tavily.api_key = current_tavily
        from engine.data_sources.finnhub_source import finnhub_source
        finnhub_source.api_key = current_finnhub
        from engine.data_sources.fmp_source import fmp_source
        fmp_source.api_key = current_fmp
        from engine.data_sources.adanos_source import adanos_source
        adanos_source.api_key = current_adanos
        from engine.data_sources.fred_source import fred_source
        fred_source.api_key = current_fred
        from engine.data_sources.tiingo_source import tiingo_source
        tiingo_source.api_key = current_tiingo
    except Exception:
        pass

    return True
