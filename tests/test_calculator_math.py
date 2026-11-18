import unittest
from decimal import Decimal

from tools.calculator_math import (
    calculate_market_cap_check,
    calculate_scenario,
    calculate_valuation_metrics,
)


class CalculatorMathTests(unittest.TestCase):
    def test_valuation_metrics_use_decimal_inputs(self):
        metrics = calculate_valuation_metrics("300", "3", "30", "30")

        self.assertEqual(metrics["pe"], Decimal("100"))
        self.assertEqual(metrics["ex_cash_pe"], Decimal("90"))
        self.assertEqual(metrics["cash_discount"], Decimal("10"))

    def test_market_cap_requires_positive_reported_value(self):
        with self.assertRaisesRegex(ValueError, "披露市值"):
            calculate_market_cap_check("10", "100", "0")

    def test_scenario_returns_decimal_metrics(self):
        result = calculate_scenario("100", "10", "0.1", "10", 2)

        self.assertEqual(result["future_eps"], Decimal("12.10"))
        self.assertEqual(result["target_price"], Decimal("121.00"))
        self.assertEqual(result["gain_pct"], Decimal("21.00"))
        self.assertAlmostEqual(float(result["cagr_pct"]), 10.0, places=10)

    def test_invalid_non_finite_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "有限值"):
            calculate_valuation_metrics("NaN", "1", "1", "0")


if __name__ == "__main__":
    unittest.main()
