import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from engine.data_sources.yfinance_source import YFinanceSource


class YFinanceProvenanceTests(unittest.TestCase):
    def test_previous_close_is_identified_as_non_realtime(self):
        ticker = SimpleNamespace(
            info={
                "previousClose": 100.0,
                "regularMarketTime": 1700000000,
                "currency": "USD",
            },
            fast_info=SimpleNamespace(last_price=101.0),
            quarterly_income_stmt=None,
            quarterly_cashflow=None,
            quarterly_balance_sheet=None,
        )
        fake_yfinance = SimpleNamespace(Ticker=lambda _: ticker)

        with patch.dict(sys.modules, {"yfinance": fake_yfinance}):
            data = YFinanceSource().fetch_data("AAPL")

        self.assertEqual(data["price"], 100.0)
        self.assertEqual(data["price_source"], "Yahoo Finance info.previousClose")
        self.assertIn("非实时", data["price_basis"])
        self.assertEqual(
            data["quote_as_of"],
            datetime.fromtimestamp(1700000000, timezone.utc).isoformat(timespec="seconds"),
        )
        self.assertTrue(data["data_retrieved_at"])

    def test_markdown_discloses_third_party_provenance(self):
        source = YFinanceSource()
        data = {
            "success": True,
            "ticker": "AAPL",
            "currency": "USD",
            "price": 100.0,
            "price_source": "Yahoo Finance info.previousClose",
            "price_basis": "前一交易日收盘价（非实时）",
            "quote_as_of": None,
            "data_retrieved_at": "2026-11-17T10:00:00+00:00",
        }

        with patch.object(source, "fetch_data", return_value=data):
            markdown = source.to_markdown("AAPL")

        self.assertIn("第三方数据聚合服务", markdown)
        self.assertIn("前一交易日收盘价（非实时）", markdown)
        self.assertIn("供应方未提供", markdown)
        self.assertNotIn("100% 结构化真实数据", markdown)


if __name__ == "__main__":
    unittest.main()
