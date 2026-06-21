"""GraphQL query documents.

Every field name here was verified against the live Morpho Blue schema at
https://blue-api.morpho.org/graphql. Notably the market unique key is exposed
as ``marketId`` (the legacy ``Market.id``/``uniqueKey`` field is deprecated and
slated for removal), so queries select ``marketId`` throughout.
"""

from __future__ import annotations

_ASSET_FRAGMENT = """
fragment AssetFields on Asset {
  address
  symbol
  decimals
}
"""

_MARKET_STATE_FRAGMENT = """
fragment MarketStateFields on MarketState {
  supplyApy
  borrowApy
  netSupplyApy
  netBorrowApy
  utilization
  supplyAssets
  borrowAssets
  collateralAssets
  supplyAssetsUsd
  borrowAssetsUsd
  fee
}
"""

_MARKET_FRAGMENT = (
    _ASSET_FRAGMENT
    + _MARKET_STATE_FRAGMENT
    + """
fragment MarketFields on Market {
  marketId
  lltv
  chain { id network }
  loanAsset { ...AssetFields }
  collateralAsset { ...AssetFields }
  state { ...MarketStateFields }
}
"""
)

MARKETS_QUERY = (
    _MARKET_FRAGMENT
    + """
query Markets(
  $first: Int
  $skip: Int
  $orderBy: MarketOrderBy
  $orderDirection: OrderDirection
  $where: MarketFilters
) {
  markets(
    first: $first
    skip: $skip
    orderBy: $orderBy
    orderDirection: $orderDirection
    where: $where
  ) {
    items { ...MarketFields }
    pageInfo { countTotal count limit skip }
  }
}
"""
)

MARKET_BY_ID_QUERY = (
    _MARKET_FRAGMENT
    + """
query MarketById($marketId: String!, $chainId: Int!) {
  marketById(marketId: $marketId, chainId: $chainId) { ...MarketFields }
}
"""
)

_VAULT_FRAGMENT = (
    _ASSET_FRAGMENT
    + """
fragment VaultFields on Vault {
  address
  name
  symbol
  chain { id network }
  asset { ...AssetFields }
  state {
    apy
    netApy
    totalAssets
    totalAssetsUsd
    fee
    allocation {
      supplyAssetsUsd
      supplyCapUsd
      supplyAssets
      market { marketId }
    }
  }
}
"""
)

VAULTS_QUERY = (
    _VAULT_FRAGMENT
    + """
query Vaults(
  $first: Int
  $skip: Int
  $orderBy: VaultOrderBy
  $orderDirection: OrderDirection
  $where: VaultFilters
) {
  vaults(
    first: $first
    skip: $skip
    orderBy: $orderBy
    orderDirection: $orderDirection
    where: $where
  ) {
    items { ...VaultFields }
    pageInfo { countTotal count limit skip }
  }
}
"""
)

VAULT_BY_ADDRESS_QUERY = (
    _VAULT_FRAGMENT
    + """
query VaultByAddress($address: String!, $chainId: Int) {
  vaultByAddress(address: $address, chainId: $chainId) { ...VaultFields }
}
"""
)

USER_BY_ADDRESS_QUERY = (
    _ASSET_FRAGMENT
    + """
query UserByAddress($address: String!, $chainId: Int) {
  userByAddress(address: $address, chainId: $chainId) {
    address
    chain { id network }
    marketPositions {
      healthFactor
      market {
        marketId
        loanAsset { ...AssetFields }
        collateralAsset { ...AssetFields }
      }
      state {
        supplyAssets
        borrowAssets
        collateral
        supplyAssetsUsd
        borrowAssetsUsd
        collateralUsd
      }
    }
    vaultPositions {
      vault { address symbol name }
      state { assets assetsUsd shares }
    }
  }
}
"""
)
