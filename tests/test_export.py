"""Tests for optional pandas export helpers."""

from __future__ import annotations

import pytest

from morpho_blue.models import Market, Vault

from .fixtures import MARKETS_RESPONSE, VAULTS_RESPONSE

pd = pytest.importorskip("pandas")


def _markets() -> list[Market]:
    return [Market.model_validate(i) for i in MARKETS_RESPONSE["data"]["markets"]["items"]]


def test_markets_to_dataframe_columns() -> None:
    from morpho_blue.export import markets_to_dataframe

    df = markets_to_dataframe(_markets())

    assert len(df) == 2
    assert "market_id" in df.columns
    assert "loan_asset_symbol" in df.columns
    assert "collateral_asset_symbol" in df.columns
    assert "supply_apy" in df.columns
    assert df.iloc[0]["loan_asset_symbol"] == "USDC"
    # nullable collateral becomes NaN/None, not an error
    assert pd.isna(df.iloc[1]["collateral_asset_symbol"])


def test_vaults_to_dataframe_columns() -> None:
    from morpho_blue.export import vaults_to_dataframe

    vaults = [Vault.model_validate(i) for i in VAULTS_RESPONSE["data"]["vaults"]["items"]]
    df = vaults_to_dataframe(vaults)

    assert len(df) == 1
    assert "address" in df.columns
    assert "net_apy" in df.columns
    assert "total_assets_usd" in df.columns
    assert df.iloc[0]["symbol"] == "steakUSDC"
