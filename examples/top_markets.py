"""List the largest Morpho Blue markets on Ethereum and their supply APY.

APY fields are decimal fractions (0.0366 == 3.66%). We sort by deposits
(supply_assets_usd) and skip markets at 100% utilization, which report a
distorted instantaneous rate that can read as thousands of percent.

Run: python examples/top_markets.py
"""

from __future__ import annotations

from morpho_blue import MorphoClient


def main() -> None:
    with MorphoClient() as client:
        markets = client.get_markets(
            chain_id=1,
            first=10,
            order_by="supply_assets_usd",
            where={"utilization_lte": 0.99},
        )

    for market in markets:
        loan = market.loan_asset.symbol if market.loan_asset else "?"
        collat = market.collateral_asset.symbol if market.collateral_asset else "idle"
        apy = market.state.supply_apy if market.state else None
        tvl = market.state.supply_assets_usd if market.state else None
        apy_s = f"{apy:7.2%}" if apy is not None else "    n/a"
        tvl_s = f"${tvl:,.0f}" if tvl is not None else "n/a"
        print(f"{loan:>8} / {collat:<10} supply APY {apy_s}  TVL {tvl_s}")


if __name__ == "__main__":
    main()
