"""Tests for the asynchronous AsyncMorphoClient against a mocked endpoint."""

from __future__ import annotations

import httpx
import pytest
import respx

from morpho_blue import AsyncMorphoClient
from morpho_blue.exceptions import GraphQLError

from .fixtures import ERROR_RESPONSE, MARKETS_RESPONSE, VAULTS_RESPONSE

ENDPOINT = "https://blue-api.morpho.org/graphql"


@respx.mock
async def test_async_get_markets() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=MARKETS_RESPONSE))
    async with AsyncMorphoClient() as client:
        markets = await client.get_markets(chain_id=1, first=2)

    assert len(markets) == 2
    assert markets[0].loan_asset is not None
    assert markets[0].loan_asset.symbol == "USDC"


@respx.mock
async def test_async_top_markets_by_apy() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=MARKETS_RESPONSE))
    async with AsyncMorphoClient() as client:
        markets = await client.top_markets_by_supply_apy(chain_id=1, limit=2)

    assert len(markets) == 2


@respx.mock
async def test_async_get_vaults() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=VAULTS_RESPONSE))
    async with AsyncMorphoClient() as client:
        vaults = await client.get_vaults(chain_id=1, first=1)

    assert vaults[0].symbol == "steakUSDC"


@respx.mock
async def test_async_graphql_errors_raise() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=ERROR_RESPONSE))
    async with AsyncMorphoClient() as client:
        with pytest.raises(GraphQLError):
            await client.get_markets(chain_id=1)
