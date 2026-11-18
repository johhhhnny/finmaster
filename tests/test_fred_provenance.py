import unittest
from unittest.mock import patch

from engine.data_sources.fred_source import FredSource


class FredProvenanceTests(unittest.TestCase):
    def test_treasury_proxy_is_not_reported_as_official_fred_data(self):
        source = FredSource()
        overview = {
            "success": True,
            "timestamp": 1700000000,
            "data": {
                "DGS10": {
                    "value": 4.1,
                    "date": None,
                    "source": "yfinance_TNX_fallback",
                }
            },
        }

        with patch.object(source, "fetch_macro_overview", return_value=overview):
            markdown = source.to_markdown()

        self.assertIn("Yahoo Finance ^TNX 第三方近似值，非 FRED 官方观测", markdown)
        self.assertIn("供应方未提供", markdown)
        self.assertIn("不应视作官方国债收益率观测", markdown)


if __name__ == "__main__":
    unittest.main()
