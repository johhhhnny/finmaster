"""
FinMaster Data Sources Package
包含 yfinance 结构化财务报表、SEC EDGAR 官方披露底稿及多源数据聚合中台。
"""
from .yfinance_source import YFinanceSource, yfinance_source
from .sec_edgar_source import SecEdgarSource, sec_edgar_source
from .finnhub_source import FinnhubSource, finnhub_source
from .fmp_source import FMPSource, fmp_source
from .adanos_source import AdanosSource, adanos_source
from .data_hub import DataHub, data_hub

__all__ = [
    "YFinanceSource",
    "yfinance_source",
    "SecEdgarSource",
    "sec_edgar_source",
    "FinnhubSource",
    "finnhub_source",
    "FMPSource",
    "fmp_source",
    "AdanosSource",
    "adanos_source",
    "DataHub",
    "data_hub"
]

