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

    The async counterpart of :class:`~morpho_blue.client.MorphoClient`, exposing
    the same methods as coroutines. Use it as an async context manager so the
    underlying ``httpx.AsyncClient`` is closed automatically.

    Example::

        import asyncio
        from morpho_blue import AsyncMorphoClient

        async def main() -> None:
            async with AsyncMorphoClient() as client:
                markets = await client.top_markets_by_supply_apy(chain_id=1, limit=5)
                for m in markets:
                    if m.loan_asset and m.state:
                        print(m.loan_asset.symbol, m.state.supply_apy)

        asyncio.run(main())
    """

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[dict[str, str]] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Create an async client.

        Args:
            endpoint: GraphQL endpoint URL. Defaults to the public Morpho Blue
                API (:data:`~morpho_blue.DEFAULT_ENDPOINT`).
            timeout: Per-request timeout in seconds. Ignored if ``client`` is
                supplied.
            headers: Extra HTTP headers merged into every request (on top of the
                default ``Content-Type: application/json``).
            client: A pre-configured ``httpx.AsyncClient`` to use. When provided,
                the caller owns its lifecycle and :meth:`aclose` will not close
                it; otherwise the client creates and owns one.
        """
        self.endpoint = endpoint
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout, headers=default_headers)

    # -- lifecycle -------------------------------------------------------
    async def aclose(self) -> None:
        """Close the underlying HTTP client if this instance owns it.

        A no-op when an external ``httpx.AsyncClient`` was passed to
        :meth:`__init__`, since the caller is responsible for closing it.
        """
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncMorphoClient:
        """Enter the async context manager and return this client."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Exit the async context manager, closing the client via :meth:`aclose`."""
        await self.aclose()

    # -- low level -------------------------------------------------------
    async def execute(
        self, query: str, variables: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """POST a raw GraphQL query and return its ``data`` object.

        Args:
            query: The GraphQL query document.
            variables: Optional variables to bind into the query.

        Returns:
            The ``data`` object from the GraphQL response.

        Raises:
            HTTPError: If the endpoint returns a non-2xx HTTP status.
            GraphQLError: If the response carries a GraphQL ``errors`` array
                (the API returns HTTP 200 even for query errors).
        """
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
        """Fetch a single page of markets, optionally filtered and sorted.

        Args:
            chain_id: Restrict to one chain (e.g. ``1`` for Ethereum). When set,
                it is merged into ``where`` as ``chainId_in``. Omit for all chains.
            first: Page size (max number of markets to return).
            skip: Offset for pagination.
            order_by: Sort field. Accepts a friendly key (``"supply_apy"``,
                ``"supply_assets_usd"``, ``"utilization"``, ``"lltv"``, …) or a
                raw ``MarketOrderBy`` enum value.
            order_direction: ``"Desc"`` (default) or ``"Asc"``.
            where: Additional raw ``MarketFilters`` (e.g.
                ``{"utilization_lte": 0.99}``), merged with ``chain_id``.

        Returns:
            The page of markets as :class:`~morpho_blue.models.Market` objects.

        Raises:
            HTTPError: On a non-2xx HTTP status.
            GraphQLError: If the API returns a GraphQL error.
        """
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
        """Fetch a single market by its ``marketId`` (the unique key).

        Args:
            market_id: The market's unique key (0x-prefixed 32-byte hash). Note
                the Morpho schema uses ``marketId``, not ``uniqueKey``.
            chain_id: The chain the market lives on (required for this lookup).

        Returns:
            The :class:`~morpho_blue.models.Market`.

        Raises:
            HTTPError: On a non-2xx HTTP status.
            GraphQLError: If the market is not found or the API errors.
        """
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
        """Return the ``limit`` markets with the highest supply APY.

        Sorts by raw supply APY descending, which can surface tiny, fully
        utilized markets whose instantaneous rate spikes; pass
        ``where={"utilization_lte": 0.99}`` to exclude them.

        Args:
            chain_id: Restrict to one chain, or omit for all chains.
            limit: How many markets to return.
            where: Additional raw ``MarketFilters`` to apply.

        Returns:
            Up to ``limit`` markets ordered by descending supply APY.

        Raises:
            HTTPError: On a non-2xx HTTP status.
            GraphQLError: If the API returns a GraphQL error.
        """
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
        """Fetch *all* matching markets, paginating automatically via ``skip``.

        Repeatedly requests pages of ``page_size`` until a short page signals the
        end, accumulating every market into one list.

        Args:
            chain_id: Restrict to one chain, or omit for all chains.
            page_size: Number of markets requested per underlying page.
            order_by: Sort field (see :meth:`get_markets`).
            order_direction: ``"Desc"`` (default) or ``"Asc"``.
            where: Additional raw ``MarketFilters`` to apply.

        Returns:
            Every matching market across all pages.

        Raises:
            HTTPError: On a non-2xx HTTP status.
            GraphQLError: If the API returns a GraphQL error.
        """
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
        """Fetch a single page of MetaMorpho vaults, optionally filtered/sorted.

        Args:
            chain_id: Restrict to one chain, or omit for all chains.
            first: Page size (max number of vaults to return).
            skip: Offset for pagination.
            order_by: Sort field. Accepts a friendly key (``"net_apy"``,
                ``"total_assets_usd"``, ``"apy"``, ``"fee"``, …) or a raw
                ``VaultOrderBy`` enum value.
            order_direction: ``"Desc"`` (default) or ``"Asc"``.
            where: Additional raw ``VaultFilters`` to apply.

        Returns:
            The page of vaults as :class:`~morpho_blue.models.Vault` objects.

        Raises:
            HTTPError: On a non-2xx HTTP status.
            GraphQLError: If the API returns a GraphQL error.
        """
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
        """Fetch a single vault by its contract ``address``.

        Args:
            address: The vault contract address.
            chain_id: The chain the vault lives on; recommended to disambiguate
                the same address across chains.

        Returns:
            The :class:`~morpho_blue.models.Vault`.

        Raises:
            HTTPError: On a non-2xx HTTP status.
            GraphQLError: If the vault is not found or the API errors.
        """
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
        """Return the ``limit`` vaults with the highest net APY.

        Args:
            chain_id: Restrict to one chain, or omit for all chains.
            limit: How many vaults to return.
            where: Additional raw ``VaultFilters`` to apply.

        Returns:
            Up to ``limit`` vaults ordered by descending net APY.

        Raises:
            HTTPError: On a non-2xx HTTP status.
            GraphQLError: If the API returns a GraphQL error.
        """
        return await self.get_vaults(
            chain_id=chain_id,
            first=limit,
            order_by="net_apy",
            order_direction="Desc",
            where=where,
        )

    # -- users / positions ----------------------------------------------
    async def get_user(self, address: str, *, chain_id: Optional[int] = None) -> User:
        """Fetch a wallet's market and vault positions by ``address``.

        Args:
            address: The wallet address to look up.
            chain_id: The chain to read positions on; recommended.

        Returns:
            A :class:`~morpho_blue.models.User` with ``market_positions`` and
            ``vault_positions``.

        Raises:
            HTTPError: On a non-2xx HTTP status.
            GraphQLError: If the API returns a GraphQL error.
        """
        data = await self.execute(
            queries.USER_BY_ADDRESS_QUERY,
            {"address": address, "chainId": chain_id},
        )
        return user_from_data(data)
