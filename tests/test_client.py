"""Tests for the synchronous MorphoClient against a mocked GraphQL endpoint."""

from __future__ import annotations

import httpx
import pytest
import respx

from morpho_blue import MorphoClient
from morpho_blue.exceptions import GraphQLError

from .fixtures import (
    ERROR_RESPONSE,
    MARKET_BY_ID_RESPONSE,
    MARKETS_RESPONSE,
    USER_BY_ADDRESS_RESPONSE,
    VAULT_BY_ADDRESS_RESPONSE,
    VAULTS_RESPONSE,
)

ENDPOINT = "https://blue-api.morpho.org/graphql"


@respx.mock
def test_get_markets_returns_typed_models() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=MARKETS_RESPONSE))
    with MorphoClient() as client:
        markets = client.get_markets(chain_id=1, first=2)

    assert len(markets) == 2
    assert markets[0].loan_asset is not None
    assert markets[0].loan_asset.symbol == "USDC"
    assert markets[1].collateral_asset is None


@respx.mock
def test_get_market_by_id() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=MARKET_BY_ID_RESPONSE))
    with MorphoClient() as client:
        market = client.get_market(
            "0x8eaf7b29f02ba8d8c1d7aeb587403dcb16e2e943e4e2f5f94b0963c2386406c9",
            chain_id=1,
        )

    assert market.lltv == 915000000000000000
    assert market.state is not None
    assert market.state.supply_apy == 0.0521


@respx.mock
def test_top_markets_by_apy_sorts_descending() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=MARKETS_RESPONSE))
    with MorphoClient() as client:
        markets = client.top_markets_by_supply_apy(chain_id=1, limit=2)

    apys = [m.state.supply_apy for m in markets if m.state and m.state.supply_apy is not None]
    assert apys == sorted(apys, reverse=True)


@respx.mock
def test_get_vaults_returns_typed_models() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=VAULTS_RESPONSE))
    with MorphoClient() as client:
        vaults = client.get_vaults(chain_id=1, first=1)

    assert len(vaults) == 1
    assert vaults[0].symbol == "steakUSDC"
    assert vaults[0].state is not None
    assert len(vaults[0].state.allocation) == 2


@respx.mock
def test_get_vault_by_address() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=VAULT_BY_ADDRESS_RESPONSE))
    with MorphoClient() as client:
        vault = client.get_vault("0xBEEF01735c132Ada46AA9aA4c54623cAA92A64CB", chain_id=1)

    assert vault.name == "Steakhouse USDC"


@respx.mock
def test_get_user_positions() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=USER_BY_ADDRESS_RESPONSE))
    with MorphoClient() as client:
        user = client.get_user("0x47E2D28169738039755586743E2dfCF3bd643f86", chain_id=1)

    assert len(user.market_positions) == 1
    assert user.market_positions[0].health_factor == 1.85
    assert len(user.vault_positions) == 1


@respx.mock
def test_graphql_errors_raise() -> None:
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=ERROR_RESPONSE))
    with MorphoClient() as client, pytest.raises(GraphQLError) as exc_info:
        client.get_markets(chain_id=1)

    assert "uniqueKey" in str(exc_info.value)


@respx.mock
def test_request_posts_variables_and_query() -> None:
    route = respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=MARKETS_RESPONSE))
    with MorphoClient() as client:
        client.get_markets(chain_id=1, first=5, skip=10)

    request = route.calls.last.request
    body = request.content.decode()
    assert "query" in body
    assert "markets" in body
    # chain_id filter and pagination must reach the server.
    assert "chainId_in" in body or "chainId" in body


def test_custom_endpoint_is_used() -> None:
    custom = "https://example.com/gql"
    with respx.mock:
        route = respx.post(custom).mock(return_value=httpx.Response(200, json=MARKETS_RESPONSE))
        with MorphoClient(endpoint=custom) as client:
            client.get_markets(chain_id=1)
        assert route.called
