"""Exception hierarchy for morpho-blue-py."""

from __future__ import annotations

from typing import Any, Optional


class MorphoError(Exception):
    """Base class for all errors raised by this library."""


class GraphQLError(MorphoError):
    """Raised when the GraphQL endpoint returns an ``errors`` array.

    The endpoint responds with HTTP 200 even for query errors, so this is
    surfaced from the response body rather than the status code.

    Attributes:
        errors: The raw list of GraphQL error objects from the response.
    """

    def __init__(self, errors: list[Any]) -> None:
        """Build the error from a GraphQL ``errors`` array.

        Args:
            errors: The ``errors`` list from the GraphQL response. Each item's
                ``message`` (when present) is joined into the exception message.
        """
        self.errors = errors
        messages = [e.get("message", str(e)) if isinstance(e, dict) else str(e) for e in errors]
        super().__init__("; ".join(messages) or "Unknown GraphQL error")


class HTTPError(MorphoError):
    """Raised for non-2xx HTTP responses from the endpoint.

    Attributes:
        status_code: The HTTP status code returned by the endpoint.
        body: The response body text, if any.
    """

    def __init__(self, status_code: int, body: Optional[str] = None) -> None:
        """Build the error from an HTTP status and optional body.

        Args:
            status_code: The non-2xx HTTP status code.
            body: The response body text, included in the message when present.
        """
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body or ''}".strip())
