"""morpho-blue-py: a typed Python client for the Morpho Blue GraphQL API."""

from __future__ import annotations

from ._common import DEFAULT_ENDPOINT
from .async_client import AsyncMorphoClient
from .client import MorphoClient
from .exceptions import GraphQLError, HTTPError, MorphoError
from .models import (
    Asset,
    Chain,
    Market,
    MarketPosition,
    MarketPositionState,
    MarketState,
    PageInfo,
    User,
    Vault,
    VaultAllocation,
    VaultPosition,
    VaultPositionState,
    VaultState,
)

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_ENDPOINT",
    "AsyncMorphoClient",
    "MorphoClient",
    "GraphQLError",
    "HTTPError",
    "MorphoError",
    "Asset",
    "Chain",
    "Market",
    "MarketPosition",
    "MarketPositionState",
    "MarketState",
    "PageInfo",
    "User",
    "Vault",
    "VaultAllocation",
    "VaultPosition",
    "VaultPositionState",
    "VaultState",
]
