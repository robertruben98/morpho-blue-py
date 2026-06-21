"""Async usage: fetch top markets concurrently across two chains.

Run: python examples/async_usage.py
"""

from __future__ import annotations

import asyncio

from morpho_blue import AsyncMorphoClient


async def main() -> None:
    async with AsyncMorphoClient() as client:
        ethereum, base = await asyncio.gather(
            client.top_markets_by_supply_apy(chain_id=1, limit=3),
            client.top_markets_by_supply_apy(chain_id=8453, limit=3),
        )

    for label, markets in (("Ethereum", ethereum), ("Base", base)):
        print(label)
        for m in markets:
            loan = m.loan_asset.symbol if m.loan_asset else "?"
            apy = m.state.supply_apy if m.state else None
            print(f"  {loan:>8}: {apy:.2%}" if apy is not None else f"  {loan}")


if __name__ == "__main__":
    asyncio.run(main())
