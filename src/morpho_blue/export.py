"""Optional pandas export helpers.

Requires the ``pandas`` extra: ``pip install "morpho-blue-py[pandas]"``.
Flattens the nested model graph into one row per market/vault.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, cast

from .models import Market, Vault

if TYPE_CHECKING:
    import pandas as pd
    from pandas import DataFrame


def _require_pandas() -> Any:
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - exercised via extra
        raise ImportError(
            "pandas is required for export helpers. "
            'Install it with: pip install "morpho-blue-py[pandas]"'
        ) from exc
    return pd


def _market_row(market: Market) -> dict[str, Any]:
    state = market.state
    loan = market.loan_asset
    collateral = market.collateral_asset
    return {
        "market_id": market.market_id,
        "chain_id": market.chain.id,
        "lltv": market.lltv,
        "loan_asset_symbol": loan.symbol if loan else None,
        "loan_asset_address": loan.address if loan else None,
        "collateral_asset_symbol": collateral.symbol if collateral else None,
        "collateral_asset_address": collateral.address if collateral else None,
        "supply_apy": state.supply_apy if state else None,
        "borrow_apy": state.borrow_apy if state else None,
        "net_supply_apy": state.net_supply_apy if state else None,
        "net_borrow_apy": state.net_borrow_apy if state else None,
        "utilization": state.utilization if state else None,
        "supply_assets_usd": state.supply_assets_usd if state else None,
        "borrow_assets_usd": state.borrow_assets_usd if state else None,
        "fee": state.fee if state else None,
    }


def _vault_row(vault: Vault) -> dict[str, Any]:
    state = vault.state
    return {
        "address": vault.address,
        "name": vault.name,
        "symbol": vault.symbol,
        "chain_id": vault.chain.id if vault.chain else None,
        "asset_symbol": vault.asset.symbol,
        "asset_address": vault.asset.address,
        "apy": state.apy if state else None,
        "net_apy": state.net_apy if state else None,
        "total_assets": state.total_assets if state else None,
        "total_assets_usd": state.total_assets_usd if state else None,
        "fee": state.fee if state else None,
        "num_allocations": len(state.allocation) if state else 0,
    }


def markets_to_dataframe(markets: Sequence[Market]) -> pd.DataFrame:
    """Flatten a sequence of :class:`Market` into a pandas ``DataFrame``."""
    pd = _require_pandas()
    rows: list[dict[str, Any]] = [_market_row(m) for m in markets]
    return cast("DataFrame", pd.DataFrame(rows))


def vaults_to_dataframe(vaults: Sequence[Vault]) -> pd.DataFrame:
    """Flatten a sequence of :class:`Vault` into a pandas ``DataFrame``."""
    pd = _require_pandas()
    rows: list[dict[str, Any]] = [_vault_row(v) for v in vaults]
    return cast("DataFrame", pd.DataFrame(rows))
