# morpho-blue-py

[![CI](https://github.com/robertruben98/morpho-blue-py/actions/workflows/ci.yml/badge.svg)](https://github.com/robertruben98/morpho-blue-py/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/morpho-blue-py.svg)](https://pypi.org/project/morpho-blue-py/)
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://robertruben98.github.io/morpho-blue-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/morpho-blue-py.svg)](https://pypi.org/project/morpho-blue-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A typed Python client for the [Morpho Blue GraphQL API](https://docs.morpho.org/tools/offchain/api/get-started/) —
lending markets, MetaMorpho vaults, and user positions analytics.

- Sync (`MorphoClient`) and async (`AsyncMorphoClient`) clients built on `httpx`.
- Fully typed [pydantic v2](https://docs.pydantic.dev/) models (ships `py.typed`).
- Helper methods: top markets by APY, market/vault lookups, wallet positions.
- Automatic pagination and multi-chain support.
- Optional `pandas` export.

The API is public and read-only — no API key required.

## Install

```bash
pip install morpho-blue-py
# with pandas export helpers:
pip install "morpho-blue-py[pandas]"
```

## Quickstart — list the largest markets and their supply APY

`supply_apy` / `borrow_apy` are returned as **decimal fractions** (e.g. `0.0366`
means 3.66%), so format them with `:.2%`. We list the biggest Ethereum markets
by deposits and skip ones at 100% utilization — a fully-utilized market reports a
distorted instantaneous rate that can read as thousands of percent.

```python
from morpho_blue import MorphoClient

with MorphoClient() as client:
    markets = client.get_markets(
        chain_id=1,
        first=5,
        order_by="supply_assets_usd",
        where={"utilization_lte": 0.99},
    )

for market in markets:
    loan = market.loan_asset.symbol if market.loan_asset else "?"
    apy = market.state.supply_apy if market.state else None
    print(f"{loan:8} supply APY: {apy:.2%}" if apy is not None else loan)
# USDC     supply APY: 3.66%
# USDT     supply APY: 3.16%
# WETH     supply APY: 1.62%
```

## Markets

```python
from morpho_blue import MorphoClient

with MorphoClient() as client:
    # A page of markets on Ethereum (chainId 1), sorted by USD supply.
    markets = client.get_markets(chain_id=1, first=20, order_by="supply_assets_usd")

    # A single market by its unique key (marketId) — note: the Morpho schema's
    # unique key is `marketId`, NOT `uniqueKey`.
    market = client.get_market(
        "0x8eaf7b29f02ba8d8c1d7aeb587403dcb16e2e943e4e2f5f94b0963c2386406c9",
        chain_id=1,
    )

    # All markets across pages (auto-paginated via skip).
    everything = client.iter_markets(chain_id=1, page_size=100)
```

## Vaults (MetaMorpho)

```python
with MorphoClient() as client:
    vaults = client.top_vaults_by_apy(chain_id=1, limit=10)
    vault = client.get_vault("0xBEEF01735c132Ada46AA9aA4c54623cAA92A64CB", chain_id=1)
    if vault.state:
        print(vault.name, vault.state.net_apy, vault.state.total_assets_usd)
        for alloc in vault.state.allocation:
            print(alloc.market.market_id, alloc.supply_assets_usd)
```

## Wallet positions

```python
with MorphoClient() as client:
    user = client.get_user("0x47E2D28169738039755586743E2dfCF3bd643f86", chain_id=1)
    for pos in user.market_positions:
        if pos.state:
            print(pos.market.market_id, pos.state.supply_assets, pos.state.borrow_assets)
    for vpos in user.vault_positions:
        print(vpos.vault.symbol, vpos.state.assets if vpos.state else None)
```

## Async

```python
import asyncio
from morpho_blue import AsyncMorphoClient

async def main() -> None:
    async with AsyncMorphoClient() as client:
        markets = await client.top_markets_by_supply_apy(chain_id=1, limit=5)
        print([m.loan_asset.symbol for m in markets if m.loan_asset])

asyncio.run(main())
```

## pandas export

```python
from morpho_blue import MorphoClient
from morpho_blue.export import markets_to_dataframe

with MorphoClient() as client:
    df = markets_to_dataframe(client.get_markets(chain_id=1, first=50))
print(df[["loan_asset_symbol", "supply_apy", "supply_assets_usd"]])
```

## Multi-chain

Every method takes an optional `chain_id`. Supported chains include Ethereum (1),
Base (8453), Arbitrum (42161), Polygon (137), Optimism (10), Unichain (130), and more.
Omit `chain_id` to query across all chains the API exposes.

## Custom endpoint

```python
MorphoClient(endpoint="https://blue-api.morpho.org/graphql")  # default
```

## Development

```bash
uv venv --python 3.9
uv pip install -e ".[dev]"
ruff check .
mypy
pytest                 # unit tests (no network)
pytest -m integration  # hits the live endpoint
```

## License

MIT
