"""Asynchronous Morpho Blue GraphQL client (httpx.AsyncClient)."""

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
from .client import DEFAULT_TIMEOUT
from .models import Market, User, Vault


class AsyncMorphoClient:
    """An asyncio client for the Morpho Blue GraphQL API.

    Example::

        async with AsyncMorphoClient() as client:
            markets = await client.top_markets_by_supply_apy(chain_id=1, limit=5)
    """

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[dict[str, str]] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.endpoint = endpoint
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout, headers=default_headers)

    # -- lifecycle -------------------------------------------------------
    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncMorphoClient:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.aclose()

    # -- low level -------------------------------------------------------
    async def execute(
        self, query: str, variables: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """POST a raw GraphQL ``query`` with ``variables`` and return ``data``."""
        response = await self._client.post(
            self.endpoint, json={"query": query, "variables": variables or {}}
        )
        check_status(response.status_code, response.text)
        return parse_response(response.json())

    # -- markets ---------------------------------------------------------
    async def get_markets(
        self,
        *,
        chain_id: Optional[int] = None,
        first: Optional[int] = 100,
        skip: Optional[int] = 0,
        order_by: Optional[str] = None,
        order_direction: str = "Desc",
        where: Optional[dict[str, Any]] = None,
    ) -> list[Market]:
        variables = build_market_variables(
            first=first,
            skip=skip,
            chain_id=chain_id,
            order_by=order_by,
            order_direction=order_direction,
            where=where,
        )
        data = await self.execute(queries.MARKETS_QUERY, variables)
        return markets_from_data(data)

    async def get_market(self, market_id: str, *, chain_id: int) -> Market:
        data = await self.execute(
            queries.MARKET_BY_ID_QUERY,
            {"marketId": market_id, "chainId": chain_id},
        )
        return market_from_data(data)

    async def top_markets_by_supply_apy(
        self,
        *,
        chain_id: Optional[int] = None,
        limit: int = 10,
        where: Optional[dict[str, Any]] = None,
    ) -> list[Market]:
        return await self.get_markets(
            chain_id=chain_id,
            first=limit,
            order_by="supply_apy",
            order_direction="Desc",
            where=where,
        )

    async def iter_markets(
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
            page = await self.get_markets(
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
    async def get_vaults(
        self,
        *,
        chain_id: Optional[int] = None,
        first: Optional[int] = 100,
        skip: Optional[int] = 0,
        order_by: Optional[str] = None,
        order_direction: str = "Desc",
        where: Optional[dict[str, Any]] = None,
    ) -> list[Vault]:
        variables = build_vault_variables(
            first=first,
            skip=skip,
            chain_id=chain_id,
            order_by=order_by,
            order_direction=order_direction,
            where=where,
        )
        data = await self.execute(queries.VAULTS_QUERY, variables)
        return vaults_from_data(data)

    async def get_vault(self, address: str, *, chain_id: Optional[int] = None) -> Vault:
        data = await self.execute(
            queries.VAULT_BY_ADDRESS_QUERY,
            {"address": address, "chainId": chain_id},
        )
        return vault_from_data(data)

    async def top_vaults_by_apy(
        self,
        *,
        chain_id: Optional[int] = None,
        limit: int = 10,
        where: Optional[dict[str, Any]] = None,
    ) -> list[Vault]:
        return await self.get_vaults(
            chain_id=chain_id,
            first=limit,
            order_by="net_apy",
            order_direction="Desc",
            where=where,
        )

    # -- users / positions ----------------------------------------------
    async def get_user(self, address: str, *, chain_id: Optional[int] = None) -> User:
        data = await self.execute(
            queries.USER_BY_ADDRESS_QUERY,
            {"address": address, "chainId": chain_id},
        )
        return user_from_data(data)
