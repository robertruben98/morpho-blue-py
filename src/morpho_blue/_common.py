"""Shared, transport-agnostic helpers used by both sync and async clients."""

from __future__ import annotations

from typing import Any, Optional

from .exceptions import GraphQLError, HTTPError
from .models import Market, User, Vault

DEFAULT_ENDPOINT = "https://blue-api.morpho.org/graphql"

# Map a friendly "field" name to the API's MarketOrderBy enum value.
MARKET_ORDER_BY = {
    "supply_apy": "SupplyApy",
    "borrow_apy": "BorrowApy",
    "net_supply_apy": "NetSupplyApy",
    "net_borrow_apy": "NetBorrowApy",
    "supply_assets_usd": "SupplyAssetsUsd",
    "borrow_assets_usd": "BorrowAssetsUsd",
    "total_liquidity_usd": "TotalLiquidityUsd",
    "utilization": "Utilization",
    "lltv": "Lltv",
}

VAULT_ORDER_BY = {
    "apy": "Apy",
    "net_apy": "NetApy",
    "total_assets": "TotalAssets",
    "total_assets_usd": "TotalAssetsUsd",
    "fee": "Fee",
    "name": "Name",
}


def parse_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a GraphQL JSON payload and return its ``data`` object.

    Raises :class:`GraphQLError` if the payload carries an ``errors`` array.
    """
    errors = payload.get("errors")
    if errors:
        raise GraphQLError(errors)
    data = payload.get("data")
    if data is None:
        raise GraphQLError([{"message": "Response contained no data"}])
    assert isinstance(data, dict)
    return data


def check_status(status_code: int, text: str) -> None:
    """Raise :class:`HTTPError` for any non-2xx response."""
    if status_code < 200 or status_code >= 300:
        raise HTTPError(status_code, text)


def build_market_variables(
    *,
    first: Optional[int],
    skip: Optional[int],
    chain_id: Optional[int],
    order_by: Optional[str],
    order_direction: str,
    where: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """Build the GraphQL variables for a ``markets`` query.

    Merges ``chain_id`` into the ``where`` filters as ``chainId_in`` and maps a
    friendly ``order_by`` key to its ``MarketOrderBy`` enum value (passing
    through any value not in :data:`MARKET_ORDER_BY`).

    Returns:
        The ``{"first", "skip", "orderDirection", "where", "orderBy"?}`` variables
        dict ready to send to the API.
    """
    filters: dict[str, Any] = dict(where or {})
    if chain_id is not None:
        filters.setdefault("chainId_in", [chain_id])
    variables: dict[str, Any] = {
        "first": first,
        "skip": skip,
        "orderDirection": order_direction,
        "where": filters or None,
    }
    if order_by is not None:
        variables["orderBy"] = MARKET_ORDER_BY.get(order_by, order_by)
    return variables


def build_vault_variables(
    *,
    first: Optional[int],
    skip: Optional[int],
    chain_id: Optional[int],
    order_by: Optional[str],
    order_direction: str,
    where: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """Build the GraphQL variables for a ``vaults`` query.

    Merges ``chain_id`` into the ``where`` filters as ``chainId_in`` and maps a
    friendly ``order_by`` key to its ``VaultOrderBy`` enum value (passing through
    any value not in :data:`VAULT_ORDER_BY`).

    Returns:
        The ``{"first", "skip", "orderDirection", "where", "orderBy"?}`` variables
        dict ready to send to the API.
    """
    filters: dict[str, Any] = dict(where or {})
    if chain_id is not None:
        filters.setdefault("chainId_in", [chain_id])
    variables: dict[str, Any] = {
        "first": first,
        "skip": skip,
        "orderDirection": order_direction,
        "where": filters or None,
    }
    if order_by is not None:
        variables["orderBy"] = VAULT_ORDER_BY.get(order_by, order_by)
    return variables


def markets_from_data(data: dict[str, Any]) -> list[Market]:
    """Parse the ``markets.items`` of a response into :class:`Market` objects.

    Returns:
        The parsed markets (an empty list when the page has no items).
    """
    items = data["markets"]["items"] or []
    return [Market.model_validate(item) for item in items]


def vaults_from_data(data: dict[str, Any]) -> list[Vault]:
    """Parse the ``vaults.items`` of a response into :class:`Vault` objects.

    Returns:
        The parsed vaults (an empty list when the page has no items).
    """
    items = data["vaults"]["items"] or []
    return [Vault.model_validate(item) for item in items]


def market_from_data(data: dict[str, Any]) -> Market:
    """Parse the ``marketById`` field of a response into a :class:`Market`.

    Returns:
        The parsed single market.
    """
    return Market.model_validate(data["marketById"])


def vault_from_data(data: dict[str, Any]) -> Vault:
    """Parse the ``vaultByAddress`` field of a response into a :class:`Vault`.

    Returns:
        The parsed single vault.
    """
    return Vault.model_validate(data["vaultByAddress"])


def user_from_data(data: dict[str, Any]) -> User:
    """Parse the ``userByAddress`` field of a response into a :class:`User`.

    Returns:
        The parsed user with their market and vault positions.
    """
    return User.model_validate(data["userByAddress"])
