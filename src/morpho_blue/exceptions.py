"""Exception hierarchy for morpho-blue-py."""

from __future__ import annotations

from typing import Any, Optional


class MorphoError(Exception):
    """Base class for all errors raised by this library."""


class GraphQLError(MorphoError):
    """Raised when the GraphQL endpoint returns an ``errors`` array.

    The endpoint responds with HTTP 200 even for query errors, so this is
    surfaced from the response body rather than the status code.
    """

    def __init__(self, errors: list[Any]) -> None:
        self.errors = errors
        messages = [e.get("message", str(e)) if isinstance(e, dict) else str(e) for e in errors]
        super().__init__("; ".join(messages) or "Unknown GraphQL error")


class HTTPError(MorphoError):
    """Raised for non-2xx HTTP responses from the endpoint."""

    def __init__(self, status_code: int, body: Optional[str] = None) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body or ''}".strip())
