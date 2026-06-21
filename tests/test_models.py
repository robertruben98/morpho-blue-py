"""Tests for parsing GraphQL responses into typed pydantic models."""

from __future__ import annotations

from morpho_blue.models import (
    Market,
    MarketPosition,
    User,
    Vault,
    VaultPosition,
)

from .fixtures import (
    MARKETS_RESPONSE,
    USER_BY_ADDRESS_RESPONSE,
    VAULTS_RESPONSE,
)


def test_market_parses_core_fields() -> None:
    raw = MARKETS_RESPONSE["data"]["markets"]["items"][0]
    market = Market.model_validate(raw)

    assert market.market_id == "0x8eaf7b29f02ba8d8c1d7aeb587403dcb16e2e943e4e2f5f94b0963c2386406c9"
    assert market.lltv == 915000000000000000
    assert market.chain.id == 1
    assert market.chain.network == "Ethereum"
    assert market.loan_asset is not None
    assert market.loan_asset.symbol == "USDC"
    assert market.loan_asset.address == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    assert market.collateral_asset is not None
    assert market.collateral_asset.symbol == "PAXG"
    assert market.state is not None
    assert market.state.supply_apy == 0.0521
    assert market.state.borrow_apy == 0.0712
    assert market.state.utilization == 0.91
    assert market.state.supply_assets_usd == 1480310629.40


def test_market_allows_null_collateral_asset() -> None:
    raw = MARKETS_RESPONSE["data"]["markets"]["items"][1]
    market = Market.model_validate(raw)

    assert market.collateral_asset is None
    assert market.loan_asset is not None
    assert market.loan_asset.symbol == "USR"


def test_vault_parses_state_and_allocations() -> None:
    raw = VAULTS_RESPONSE["data"]["vaults"]["items"][0]
    vault = Vault.model_validate(raw)

    assert vault.address == "0xBEEF01735c132Ada46AA9aA4c54623cAA92A64CB"
    assert vault.symbol == "steakUSDC"
    assert vault.asset.symbol == "USDC"
    assert vault.state is not None
    assert vault.state.apy == 0.0366
    assert vault.state.net_apy == 0.0347
    assert vault.state.fee == 0.05
    assert vault.state.total_assets == 95871274932472
    assert len(vault.state.allocation) == 2
    assert (
        vault.state.allocation[0].market.market_id
        == "0x3a85e619751152991742810df6ec69ce473daef99e28a64ab2340d7b7ccfee49"
    )
    assert vault.state.allocation[0].supply_assets_usd == 11335891.40


def test_user_parses_market_and_vault_positions() -> None:
    raw = USER_BY_ADDRESS_RESPONSE["data"]["userByAddress"]
    user = User.model_validate(raw)

    assert user.address == "0x47E2D28169738039755586743E2dfCF3bd643f86"
    assert len(user.market_positions) == 1
    mp = user.market_positions[0]
    assert isinstance(mp, MarketPosition)
    assert mp.health_factor == 1.85
    assert mp.market.loan_asset is not None
    assert mp.market.loan_asset.symbol == "USDC"
    assert mp.state is not None
    assert mp.state.supply_assets == 1000000000
    assert mp.state.borrow_assets == 500000000
    assert mp.state.collateral == 2000000000000000000

    assert len(user.vault_positions) == 1
    vp = user.vault_positions[0]
    assert isinstance(vp, VaultPosition)
    assert vp.vault.symbol == "steakUSDC"
    assert vp.state is not None
    assert vp.state.assets == 1500000000
    assert vp.state.assets_usd == 1500.0


def test_market_round_trips_aliases() -> None:
    """Field aliases must serialize back to GraphQL camelCase names."""
    raw = MARKETS_RESPONSE["data"]["markets"]["items"][0]
    market = Market.model_validate(raw)
    dumped = market.model_dump(by_alias=True)

    assert dumped["marketId"] == market.market_id
    assert dumped["loanAsset"]["symbol"] == "USDC"
