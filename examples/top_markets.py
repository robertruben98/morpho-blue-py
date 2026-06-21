"""List the top Morpho Blue markets on Ethereum by supply APY.

Run: python examples/top_markets.py
"""

from __future__ import annotations

from morpho_blue import MorphoClient


def main() -> None:
    with MorphoClient() as client:
        markets = client.top_markets_by_supply_apy(chain_id=1, limit=10)

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
