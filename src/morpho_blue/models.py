"""Pydantic v2 models mirroring the Morpho Blue GraphQL schema.

Field names use Python ``snake_case`` and map to the API's ``camelCase`` via
aliases, so models can be both parsed from API responses (``populate_by_name``)
and serialized back to GraphQL-shaped dicts with ``model_dump(by_alias=True)``.

Large on-chain integer amounts arrive as ``BigInt`` strings; they are coerced to
Python ``int``. APY/USD figures are floats. Anything that is nullable in the
schema is typed ``Optional[...]``.

A note on units: APY fields (``supply_apy``, ``borrow_apy``, vault ``apy`` …) are
**decimal fractions** — ``0.0366`` means 3.66%. ``utilization`` is likewise a
fraction in ``[0, 1]``. ``*_usd`` fields are US dollars. Raw token amounts
(``supply_assets``, ``collateral`` …) are in the asset's smallest unit (wei-like),
scaled by the asset's ``decimals``.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class _Model(BaseModel):
    """Base model for every Morpho type.

    Configures pydantic to populate fields by either their Python name or their
    GraphQL ``camelCase`` alias, and to silently ignore any extra fields the API
    may add, so the models stay forward-compatible with schema additions.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


class Chain(_Model):
    """An EVM chain that Morpho Blue is deployed on (e.g. Ethereum, Base)."""

    id: int = Field(description="EVM chain id (1 = Ethereum, 8453 = Base, …).")
    network: Optional[str] = Field(
        default=None, description="Human-readable network name, e.g. 'Ethereum'."
    )
    currency: Optional[str] = Field(
        default=None, description="Native gas currency symbol, e.g. 'ETH'."
    )


class Asset(_Model):
    """An ERC-20 token used as a loan or collateral asset, or a vault's asset."""

    address: str = Field(description="ERC-20 contract address (checksummed).")
    symbol: str = Field(description="Token ticker symbol, e.g. 'USDC'.")
    decimals: Optional[float] = Field(
        default=None, description="Number of decimals the token uses."
    )
    name: Optional[str] = Field(default=None, description="Full token name.")


class MarketState(_Model):
    """The current on-chain state and rates of a market.

    APY and ``utilization`` are decimal fractions; ``*_usd`` are dollars; raw
    asset amounts are in the loan asset's smallest unit.
    """

    supply_apy: Optional[float] = Field(
        default=None,
        alias="supplyApy",
        description="Supplier APY as a decimal fraction (0.0366 == 3.66%).",
    )
    borrow_apy: Optional[float] = Field(
        default=None,
        alias="borrowApy",
        description="Borrower APY as a decimal fraction.",
    )
    net_supply_apy: Optional[float] = Field(
        default=None,
        alias="netSupplyApy",
        description="Supplier APY including rewards, as a decimal fraction.",
    )
    net_borrow_apy: Optional[float] = Field(
        default=None,
        alias="netBorrowApy",
        description="Borrower APY net of rewards, as a decimal fraction.",
    )
    utilization: Optional[float] = Field(
        default=None,
        description="Borrowed / supplied ratio in [0, 1]. 1.0 means fully utilized.",
    )
    supply_assets: Optional[int] = Field(
        default=None,
        alias="supplyAssets",
        description="Total supplied, in the loan asset's smallest unit.",
    )
    borrow_assets: Optional[int] = Field(
        default=None,
        alias="borrowAssets",
        description="Total borrowed, in the loan asset's smallest unit.",
    )
    collateral_assets: Optional[int] = Field(
        default=None,
        alias="collateralAssets",
        description="Total collateral deposited, in the collateral's smallest unit.",
    )
    supply_assets_usd: Optional[float] = Field(
        default=None, alias="supplyAssetsUsd", description="Total supplied, in USD."
    )
    borrow_assets_usd: Optional[float] = Field(
        default=None, alias="borrowAssetsUsd", description="Total borrowed, in USD."
    )
    fee: Optional[float] = Field(
        default=None, description="Protocol fee on interest, as a decimal fraction."
    )


class Market(_Model):
    """A Morpho Blue lending market (one loan asset against one collateral asset).

    The unique key is :attr:`market_id` (the schema's ``marketId``); there is no
    ``uniqueKey`` field. ``collateral_asset`` is ``None`` for idle markets.
    """

    market_id: str = Field(
        alias="marketId",
        description="Unique market key (0x-prefixed 32-byte hash).",
    )
    lltv: Optional[int] = Field(
        default=None,
        description="Liquidation loan-to-value, scaled by 1e18 (0.915e18 == 91.5%).",
    )
    chain: Chain = Field(description="Chain the market is deployed on.")
    loan_asset: Optional[Asset] = Field(
        default=None, alias="loanAsset", description="The borrowable loan asset."
    )
    collateral_asset: Optional[Asset] = Field(
        default=None,
        alias="collateralAsset",
        description="The collateral asset, or None for an idle market.",
    )
    state: Optional[MarketState] = Field(
        default=None, description="Current rates, balances, and utilization."
    )


class MarketRef(_Model):
    """A lightweight market reference embedded in other payloads.

    Used where a full :class:`Market` is unnecessary — for example inside a vault
    allocation or a user's market position — carrying just the identifying key
    and the asset symbols.
    """

    market_id: str = Field(
        alias="marketId", description="Unique market key (0x-prefixed 32-byte hash)."
    )
    loan_asset: Optional[Asset] = Field(
        default=None, alias="loanAsset", description="The borrowable loan asset."
    )
    collateral_asset: Optional[Asset] = Field(
        default=None, alias="collateralAsset", description="The collateral asset."
    )


class VaultAllocation(_Model):
    """A MetaMorpho vault's allocation of deposits into a single market."""

    market: MarketRef = Field(description="The market these funds are supplied to.")
    supply_assets_usd: Optional[float] = Field(
        default=None,
        alias="supplyAssetsUsd",
        description="Amount the vault has supplied to this market, in USD.",
    )
    supply_cap_usd: Optional[float] = Field(
        default=None,
        alias="supplyCapUsd",
        description="Configured supply cap for this market, in USD.",
    )
    supply_assets: Optional[int] = Field(
        default=None,
        alias="supplyAssets",
        description="Amount supplied, in the loan asset's smallest unit.",
    )


class VaultState(_Model):
    """The current state of a MetaMorpho vault: yield, size, fee, and allocations."""

    apy: Optional[float] = Field(default=None, description="Gross vault APY as a decimal fraction.")
    net_apy: Optional[float] = Field(
        default=None,
        alias="netApy",
        description="Vault APY net of fees and including rewards, as a fraction.",
    )
    total_assets: Optional[int] = Field(
        default=None,
        alias="totalAssets",
        description="Total assets under management, in the asset's smallest unit.",
    )
    total_assets_usd: Optional[float] = Field(
        default=None,
        alias="totalAssetsUsd",
        description="Total assets under management, in USD.",
    )
    fee: Optional[float] = Field(
        default=None, description="Vault performance fee as a decimal fraction."
    )
    allocation: list[VaultAllocation] = Field(
        default_factory=list,
        description="Per-market breakdown of where the vault's deposits are placed.",
    )


class Vault(_Model):
    """A MetaMorpho vault that allocates a single asset across Morpho markets."""

    address: str = Field(description="Vault contract address (checksummed).")
    name: Optional[str] = Field(default=None, description="Vault display name.")
    symbol: str = Field(description="Vault share token symbol, e.g. 'steakUSDC'.")
    chain: Optional[Chain] = Field(default=None, description="Chain the vault is deployed on.")
    asset: Asset = Field(description="The underlying asset the vault accepts.")
    state: Optional[VaultState] = Field(
        default=None, description="Current APY, size, fee, and allocations."
    )


class MarketPositionState(_Model):
    """A user's balances within a single market position."""

    supply_assets: Optional[int] = Field(
        default=None,
        alias="supplyAssets",
        description="Supplied amount, in the loan asset's smallest unit.",
    )
    borrow_assets: Optional[int] = Field(
        default=None,
        alias="borrowAssets",
        description="Borrowed amount, in the loan asset's smallest unit.",
    )
    collateral: Optional[int] = Field(
        default=None,
        description="Collateral deposited, in the collateral's smallest unit.",
    )
    supply_assets_usd: Optional[float] = Field(
        default=None, alias="supplyAssetsUsd", description="Supplied amount, in USD."
    )
    borrow_assets_usd: Optional[float] = Field(
        default=None, alias="borrowAssetsUsd", description="Borrowed amount, in USD."
    )
    collateral_usd: Optional[float] = Field(
        default=None, alias="collateralUsd", description="Collateral value, in USD."
    )


class MarketPosition(_Model):
    """A user's position in a single market, with its health factor and balances."""

    market: MarketRef = Field(description="The market this position is in.")
    health_factor: Optional[float] = Field(
        default=None,
        alias="healthFactor",
        description="Position health factor; below 1.0 is liquidatable.",
    )
    state: Optional[MarketPositionState] = Field(
        default=None, description="Supplied, borrowed, and collateral balances."
    )


class VaultRef(_Model):
    """A lightweight vault reference embedded in a user's vault position."""

    address: str = Field(description="Vault contract address (checksummed).")
    symbol: str = Field(description="Vault share token symbol.")
    name: Optional[str] = Field(default=None, description="Vault display name.")


class VaultPositionState(_Model):
    """A user's balances within a single vault position."""

    assets: Optional[int] = Field(
        default=None,
        description="Underlying assets held, in the asset's smallest unit.",
    )
    assets_usd: Optional[float] = Field(
        default=None, alias="assetsUsd", description="Underlying assets held, in USD."
    )
    shares: Optional[int] = Field(
        default=None, description="Vault share token balance, in its smallest unit."
    )


class VaultPosition(_Model):
    """A user's position in a single MetaMorpho vault."""

    vault: VaultRef = Field(description="The vault this position is in.")
    state: Optional[VaultPositionState] = Field(
        default=None, description="Asset and share balances for this position."
    )


class User(_Model):
    """A wallet's positions across Morpho markets and vaults on one chain."""

    address: str = Field(description="Wallet address (checksummed).")
    chain: Optional[Chain] = Field(default=None, description="Chain these positions belong to.")
    market_positions: list[MarketPosition] = Field(
        default_factory=list,
        alias="marketPositions",
        description="The wallet's positions across individual markets.",
    )
    vault_positions: list[VaultPosition] = Field(
        default_factory=list,
        alias="vaultPositions",
        description="The wallet's positions across MetaMorpho vaults.",
    )


class PageInfo(_Model):
    """Pagination metadata returned alongside a page of results."""

    count_total: Optional[int] = Field(
        default=None,
        alias="countTotal",
        description="Total number of items matching the query across all pages.",
    )
    count: Optional[int] = Field(default=None, description="Number of items in the current page.")
    limit: Optional[int] = Field(default=None, description="The page size requested (``first``).")
    skip: Optional[int] = Field(default=None, description="The offset applied (``skip``).")
