"""Pydantic v2 models mirroring the Morpho Blue GraphQL schema.

Field names use Python ``snake_case`` and map to the API's ``camelCase`` via
aliases, so models can be both parsed from API responses (``populate_by_name``)
and serialized back to GraphQL-shaped dicts with ``model_dump(by_alias=True)``.

Large on-chain integer amounts arrive as ``BigInt`` strings; they are coerced to
Python ``int``. APY/USD figures are floats. Anything that is nullable in the
schema is typed ``Optional[...]``.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class _Model(BaseModel):
    """Base model: accept aliases or python names, ignore unknown fields."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class Chain(_Model):
    id: int
    network: Optional[str] = None
    currency: Optional[str] = None


class Asset(_Model):
    address: str
    symbol: str
    decimals: Optional[float] = None
    name: Optional[str] = None


class MarketState(_Model):
    supply_apy: Optional[float] = Field(default=None, alias="supplyApy")
    borrow_apy: Optional[float] = Field(default=None, alias="borrowApy")
    net_supply_apy: Optional[float] = Field(default=None, alias="netSupplyApy")
    net_borrow_apy: Optional[float] = Field(default=None, alias="netBorrowApy")
    utilization: Optional[float] = None
    supply_assets: Optional[int] = Field(default=None, alias="supplyAssets")
    borrow_assets: Optional[int] = Field(default=None, alias="borrowAssets")
    collateral_assets: Optional[int] = Field(default=None, alias="collateralAssets")
    supply_assets_usd: Optional[float] = Field(default=None, alias="supplyAssetsUsd")
    borrow_assets_usd: Optional[float] = Field(default=None, alias="borrowAssetsUsd")
    fee: Optional[float] = None


class Market(_Model):
    market_id: str = Field(alias="marketId")
    lltv: Optional[int] = None
    chain: Chain
    loan_asset: Optional[Asset] = Field(default=None, alias="loanAsset")
    collateral_asset: Optional[Asset] = Field(default=None, alias="collateralAsset")
    state: Optional[MarketState] = None


class MarketRef(_Model):
    """A nested market reference (e.g. inside a vault allocation)."""

    market_id: str = Field(alias="marketId")
    loan_asset: Optional[Asset] = Field(default=None, alias="loanAsset")
    collateral_asset: Optional[Asset] = Field(default=None, alias="collateralAsset")


class VaultAllocation(_Model):
    market: MarketRef
    supply_assets_usd: Optional[float] = Field(default=None, alias="supplyAssetsUsd")
    supply_cap_usd: Optional[float] = Field(default=None, alias="supplyCapUsd")
    supply_assets: Optional[int] = Field(default=None, alias="supplyAssets")


class VaultState(_Model):
    apy: Optional[float] = None
    net_apy: Optional[float] = Field(default=None, alias="netApy")
    total_assets: Optional[int] = Field(default=None, alias="totalAssets")
    total_assets_usd: Optional[float] = Field(default=None, alias="totalAssetsUsd")
    fee: Optional[float] = None
    allocation: list[VaultAllocation] = Field(default_factory=list)


class Vault(_Model):
    address: str
    name: Optional[str] = None
    symbol: str
    chain: Optional[Chain] = None
    asset: Asset
    state: Optional[VaultState] = None


class MarketPositionState(_Model):
    supply_assets: Optional[int] = Field(default=None, alias="supplyAssets")
    borrow_assets: Optional[int] = Field(default=None, alias="borrowAssets")
    collateral: Optional[int] = None
    supply_assets_usd: Optional[float] = Field(default=None, alias="supplyAssetsUsd")
    borrow_assets_usd: Optional[float] = Field(default=None, alias="borrowAssetsUsd")
    collateral_usd: Optional[float] = Field(default=None, alias="collateralUsd")


class MarketPosition(_Model):
    market: MarketRef
    health_factor: Optional[float] = Field(default=None, alias="healthFactor")
    state: Optional[MarketPositionState] = None


class VaultRef(_Model):
    address: str
    symbol: str
    name: Optional[str] = None


class VaultPositionState(_Model):
    assets: Optional[int] = None
    assets_usd: Optional[float] = Field(default=None, alias="assetsUsd")
    shares: Optional[int] = None


class VaultPosition(_Model):
    vault: VaultRef
    state: Optional[VaultPositionState] = None


class User(_Model):
    address: str
    chain: Optional[Chain] = None
    market_positions: list[MarketPosition] = Field(default_factory=list, alias="marketPositions")
    vault_positions: list[VaultPosition] = Field(default_factory=list, alias="vaultPositions")


class PageInfo(_Model):
    count_total: Optional[int] = Field(default=None, alias="countTotal")
    count: Optional[int] = None
    limit: Optional[int] = None
    skip: Optional[int] = None
