"""Exact Decimal calculations used by the interactive valuation calculator."""
from decimal import Decimal, InvalidOperation, localcontext
from typing import Dict, Tuple, Union

NumericInput = Union[Decimal, int, float, str]


def decimal_value(value: NumericInput) -> Decimal:
    """Convert UI values through their string representation and reject invalid numbers."""
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"无效的数值: {value}") from exc
    if not result.is_finite():
        raise ValueError(f"数值必须为有限值: {value}")
    return result


def calculate_valuation_metrics(
    price: NumericInput,
    eps: NumericInput,
    bvps: NumericInput,
    cash_per_share: NumericInput,
) -> Dict[str, Decimal]:
    price_value = decimal_value(price)
    eps_value = decimal_value(eps)
    bvps_value = decimal_value(bvps)
    cash_value = decimal_value(cash_per_share)

    if price_value <= 0:
        raise ValueError("股价必须大于 0。")
    if eps_value <= 0:
        raise ValueError("EPS 必须大于 0。")
    if bvps_value <= 0:
        raise ValueError("每股净资产必须大于 0。")
    if cash_value < 0:
        raise ValueError("每股现金不能小于 0。")

    with localcontext() as context:
        context.prec = 28
        pe = price_value / eps_value
        ex_cash_pe = (price_value - cash_value) / eps_value
        return {
            "pe": pe,
            "ex_cash_pe": ex_cash_pe,
            "earnings_yield": Decimal("100") / pe,
            "pb": price_value / bvps_value,
            "roe": eps_value / bvps_value * Decimal("100"),
            "cash_discount": pe - ex_cash_pe,
            "enterprise_value_per_share": price_value - cash_value,
        }


def calculate_market_cap_check(
    price: NumericInput,
    shares: NumericInput,
    reported_market_cap: NumericInput,
) -> Tuple[Decimal, Decimal]:
    price_value = decimal_value(price)
    shares_value = decimal_value(shares)
    reported_value = decimal_value(reported_market_cap)

    if price_value <= 0:
        raise ValueError("股价必须大于 0。")
    if shares_value <= 0:
        raise ValueError("总股本必须大于 0。")
    if reported_value <= 0:
        raise ValueError("披露市值必须大于 0。")

    with localcontext() as context:
        context.prec = 28
        calculated_market_cap = price_value * shares_value
        deviation_pct = abs(calculated_market_cap - reported_value) / reported_value * Decimal("100")
    return calculated_market_cap, deviation_pct


def calculate_scenario(
    current_price: NumericInput,
    current_eps: NumericInput,
    annual_growth: NumericInput,
    exit_pe: NumericInput,
    years: int,
) -> Dict[str, Decimal]:
    price_value = decimal_value(current_price)
    eps_value = decimal_value(current_eps)
    growth_value = decimal_value(annual_growth)
    exit_pe_value = decimal_value(exit_pe)

    if price_value <= 0:
        raise ValueError("当前股价必须大于 0。")
    if eps_value <= 0:
        raise ValueError("当前 EPS 必须大于 0。")
    if growth_value <= Decimal("-1"):
        raise ValueError("年化增速必须大于 -100%。")
    if exit_pe_value <= 0:
        raise ValueError("退出 PE 必须大于 0。")
    if not isinstance(years, int) or years <= 0:
        raise ValueError("预测年限必须为正整数。")

    with localcontext() as context:
        context.prec = 28
        future_eps = eps_value * (Decimal("1") + growth_value) ** years
        target_price = future_eps * exit_pe_value
        gain_pct = (target_price - price_value) / price_value * Decimal("100")
        cagr_pct = (
            (target_price / price_value) ** (Decimal("1") / Decimal(years)) - Decimal("1")
        ) * Decimal("100")
    return {
        "future_eps": future_eps,
        "target_price": target_price,
        "gain_pct": gain_pct,
        "cagr_pct": cagr_pct,
    }
