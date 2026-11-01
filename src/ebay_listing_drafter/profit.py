"""Profit-estimate calculations for eBay listings.

All money values are handled as floats in dollars. Results are rounded to
two decimals and presented as human-readable notes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProfitEstimate:
    purchase_price: float
    shipping_cost: float
    ebay_fees: float
    sale_price: float
    profit: float
    profit_margin: float
    break_even_price: float

    def as_notes(self) -> str:
        lines = [
            "Profit estimate:",
            f"  Suggested sale price: ${self.sale_price:.2f}",
            f"  Item cost:            ${self.purchase_price:.2f}",
            f"  Shipping cost:        ${self.shipping_cost:.2f}",
            f"  eBay fees (est.):     ${self.ebay_fees:.2f}",
            f"  Break-even price:     ${self.break_even_price:.2f}",
            f"  Estimated profit:     ${self.profit:.2f} ({self.profit_margin:.1f}% margin)",
        ]
        if self.profit <= 0:
            lines.append("  Warning: this price does not cover costs.")
        return "\n".join(lines)


def estimate_fees(sale_price: float, fee_rate: float = 0.13, fixed_fee: float = 0.30) -> float:
    """Estimate total eBay fees (final value fee + payment processing)."""
    return sale_price * fee_rate + fixed_fee


def break_even_price(purchase_price: float, shipping_cost: float, fee_rate: float = 0.13, fixed_fee: float = 0.30) -> float:
    """Minimum sale price that covers item cost, shipping, and fees."""
    return (purchase_price + shipping_cost + fixed_fee) / (1.0 - fee_rate)


def suggested_sale_price(
    purchase_price: float,
    shipping_cost: float,
    target_margin: float = 0.30,
    fee_rate: float = 0.13,
    fixed_fee: float = 0.30,
) -> float:
    """Suggest a sale price that hits a target profit margin after fees."""
    price = (purchase_price + shipping_cost + fixed_fee) / (1.0 - fee_rate - target_margin)
    floor = break_even_price(purchase_price, shipping_cost, fee_rate, fixed_fee)
    return max(price, floor)


def calculate(
    purchase_price: float,
    sale_price: float | None = None,
    shipping_cost: float = 0.0,
    target_margin: float = 0.30,
    fee_rate: float = 0.13,
    fixed_fee: float = 0.30,
) -> ProfitEstimate:
    """Calculate a profit estimate for an eBay listing."""
    if sale_price is None:
        sale_price = suggested_sale_price(
            purchase_price, shipping_cost, target_margin, fee_rate, fixed_fee
        )
    fees = estimate_fees(sale_price, fee_rate, fixed_fee)
    profit = sale_price - purchase_price - shipping_cost - fees
    margin = (profit / sale_price * 100) if sale_price else 0.0
    break_even = break_even_price(purchase_price, shipping_cost, fee_rate, fixed_fee)
    return ProfitEstimate(
        purchase_price=round(purchase_price, 2),
        shipping_cost=round(shipping_cost, 2),
        ebay_fees=round(fees, 2),
        sale_price=round(sale_price, 2),
        profit=round(profit, 2),
        profit_margin=round(margin, 2),
        break_even_price=round(break_even, 2),
    )
