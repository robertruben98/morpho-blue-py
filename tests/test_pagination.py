"""Tests for automatic pagination via the iter_markets helper."""

from __future__ import annotations

import copy
from typing import Any

import httpx
import respx

from morpho_blue import MorphoClient

from .fixtures import MARKETS_RESPONSE

ENDPOINT = "https://blue-api.morpho.org/graphql"


def _page(num_items: int) -> dict[str, Any]:
    """Build a markets response carrying exactly ``num_items`` items."""
    payload = copy.deepcopy(MARKETS_RESPONSE)
    base = payload["data"]["markets"]["items"]
    items = [copy.deepcopy(base[i % len(base)]) for i in range(num_items)]
    payload["data"]["markets"]["items"] = items
    return payload


@respx.mock
def test_iter_markets_paginates_until_short_page() -> None:
    # Two full pages of 2, then a final page of 1 -> stop.
    responses = [
        httpx.Response(200, json=_page(2)),
        httpx.Response(200, json=_page(2)),
        httpx.Response(200, json=_page(1)),
    ]
    route = respx.post(ENDPOINT).mock(side_effect=responses)

    with MorphoClient() as client:
        markets = client.iter_markets(chain_id=1, page_size=2)

    assert len(markets) == 5
    assert route.call_count == 3


@respx.mock
def test_iter_markets_stops_on_empty_first_page() -> None:
    route = respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=_page(0)))

    with MorphoClient() as client:
        markets = client.iter_markets(chain_id=1, page_size=2)

    assert markets == []
    assert route.call_count == 1
