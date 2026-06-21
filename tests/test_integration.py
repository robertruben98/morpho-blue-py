"""Live integration test against the real Morpho Blue endpoint.

Deselected by default (``-m 'not integration'`` in pyproject). Run explicitly::

    pytest -m integration
"""

from __future__ import annotations

import pytest

from morpho_blue import MorphoClient

pytestmark = pytest.mark.integration


def test_live_top_markets_by_supply_apy() -> None:
    with MorphoClient() as client:
        markets = client.top_markets_by_supply_apy(chain_id=1, limit=5)

    assert markets
    assert all(m.market_id for m in markets)
    assert all(m.loan_asset is not None for m in markets)
    assert any(m.state and m.state.supply_apy is not None for m in markets)
