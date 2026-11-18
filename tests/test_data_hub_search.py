import unittest
from unittest.mock import patch

from engine.data_sources.data_hub import DataHub


class DataHubSearchTests(unittest.TestCase):
    def test_none_provider_blocks_all_search_fallbacks(self):
        with patch("engine.data_sources.data_hub.yfinance_source.resolve_ticker", return_value=None), \
                patch("engine.data_sources.data_hub.fred_source.to_markdown", return_value=""), \
                patch("engine.data_sources.data_hub.search_manager.get_provider", return_value="none"), \
                patch("engine.data_sources.data_hub.search_manager.get_financial_context") as search:
            result = DataHub().get_financial_grounding(
                target="Example Corp",
                focus="latest news",
                enable_search=True,
                search_mode="on",
            )

        self.assertFalse(result["search_triggered"])
        self.assertFalse(result["gemini_search_allowed"])
        self.assertIn("关闭所有全网搜索", result["search_decision_reason"])
        search.assert_not_called()


if __name__ == "__main__":
    unittest.main()
