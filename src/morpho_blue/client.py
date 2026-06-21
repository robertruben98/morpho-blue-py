"""Synchronous Morpho Blue GraphQL client."""

from __future__ import annotations

from types import TracebackType
from typing import Any, Optional

import httpx

from . import queries
from ._common import (
    DEFAULT_ENDPOINT,
    build_market_variables,
    build_vault_variables,
    check_status,
    market_from_data,
    markets_from_data,
    parse_response,
    user_from_data,
    vault_from_data,
    vaults_from_data,
)
from .models import Market, User, Vault

DEFAULT_TIMEOUT = 30.0


class MorphoClient:
    """A synchronous client for the Morpho Blue GraphQL API.

    Example::

        with MorphoClient() as client:
            markets = client.top_markets_by_supply_apy(chain_id=1, limit=5)
            for m in markets:
                print(m.loan_asset.symbol, m.state.supply_apy)
    """

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[dict[str, str]] = None,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self.endpoint = endpoint
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout, headers=default_headers)

    # -- lifecycle -------------------------------------------------------
    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> MorphoClient:
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()

    # -- low level -------------------------------------------------------
    def execute(self, query: str, variables: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """POST a raw GraphQL ``query`` with ``variables`` and return ``data``."""
        response = self._client.post(
            self.endpoint, json={"query": query, "variables": variables or {}}
        )
        check_status(response.status_code, response.text)
        return parse_response(response.json())

    # -- markets ---------------------------------------------------------
    def get_markets(
        self,
        *,
        chain_id: Optional[int] = None,
        first: Optional[int] = 100,
        skip: Optional[int] = 0,
        order_by: Optional[str] = None,
        order_direction: str = "Desc",
        where: Optional[dict[str, Any]] = None,
    ) -> list[Market]:
        """Fetch a page of markets, optionally filtered/sorted."""
        variables = build_market_variables(
            first=first,
            skip=skip,
            chain_id=chain_id,
            order_by=order_by,
            order_direction=order_direction,
            where=where,
        )
        data = self.execute(queries.MARKETS_QUERY, variables)
        return markets_from_data(data)

    def get_market(self, market_id: str, *, chain_id: int) -> Market:
        """Fetch a single market by its ``marketId`` (the unique key)."""
        data = self.execute(
            queries.MARKET_BY_ID_QUERY,
            {"marketId": market_id, "chainId": chain_id},
        )
        return market_from_data(data)

    def top_markets_by_supply_apy(
        self,
        *,
        chain_id: Optional[int] = None,
        limit: int = 10,
        where: Optional[dict[str, Any]] = None,
    ) -> list[Market]:
        """Return the ``limit`` markets with the highest supply APY."""
        return self.get_markets(
            chain_id=chain_id,
            first=limit,
            order_by="supply_apy",
            order_direction="Desc",
            where=where,
        )

    def iter_markets(
        self,
        *,
        chain_id: Optional[int] = None,
        page_size: int = 100,
        order_by: Optional[str] = None,
        order_direction: str = "Desc",
        where: Optional[dict[str, Any]] = None,
    ) -> list[Market]:
        """Fetch *all* markets, paginating automatically via ``skip``."""
        out: list[Market] = []
        skip = 0
        while True:
            page = self.get_markets(
                chain_id=chain_id,
                first=page_size,
                skip=skip,
                order_by=order_by,
                order_direction=order_direction,
                where=where,
            )
            out.extend(page)
            if len(page) < page_size:
                break
            skip += page_size
        return out

    # -- vaults ----------------------------------------------------------
    def get_vaults(
        self,
        *,
        chain_id: Optional[int] = None,
        first: Optional[int] = 100,
        skip: Optional[int] = 0,
        order_by: Optional[str] = None,
        order_direction: str = "Desc",
        where: Optional[dict[str, Any]] = None,
    ) -> list[Vault]:
        """Fetch a page of MetaMorpho vaults."""
        variables = build_vault_variables(
            first=first,
            skip=skip,
            chain_id=chain_id,
            order_by=order_by,
            order_direction=order_direction,
            where=where,
        )
        data = self.execute(queries.VAULTS_QUERY, variables)
        return vaults_from_data(data)

    def get_vault(self, address: str, *, chain_id: Optional[int] = None) -> Vault:
        """Fetch a single vault by its contract ``address``."""
        data = self.execute(
            queries.VAULT_BY_ADDRESS_QUERY,
            {"address": address, "chainId": chain_id},
        )
        return vault_from_data(data)

    def top_vaults_by_apy(
        self,
        *,
        chain_id: Optional[int] = None,
        limit: int = 10,
        where: Optional[dict[str, Any]] = None,
    ) -> list[Vault]:
        """Return the ``limit`` vaults with the highest net APY."""
        return self.get_vaults(
            chain_id=chain_id,
            first=limit,
            order_by="net_apy",
            order_direction="Desc",
            where=where,
        )

    # -- users / positions ----------------------------------------------
    def get_user(self, address: str, *, chain_id: Optional[int] = None) -> User:
        """Fetch a user's market and vault positions by wallet ``address``."""
        data = self.execute(
            queries.USER_BY_ADDRESS_QUERY,
            {"address": address, "chainId": chain_id},
        )
        return user_from_data(data)
