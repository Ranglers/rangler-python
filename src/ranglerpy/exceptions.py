from __future__ import annotations

from typing import Any

import httpx


class RanglerError(Exception):
    """Base SDK exception."""


class AuthenticationError(RanglerError):
    """Raised when the required Rangler credential is missing."""


class WebhookVerificationError(RanglerError):
    """Base webhook verification error."""


class InvalidSignatureError(WebhookVerificationError):
    """Raised when a webhook signature cannot be verified."""


class DuplicateEventError(RanglerError):
    """Raised when an event has already been processed by the integration."""


class APIError(RanglerError):
    """Raised when Rangler returns a non-success response."""

    def __init__(
        self,
        *,
        status_code: int,
        message: str,
        payload: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload

    @classmethod
    def from_response(cls, response: httpx.Response) -> "APIError":
        payload: Any | None
        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        message = cls._extract_message(payload) or f"Rangler API returned {response.status_code}"
        return cls(status_code=response.status_code, message=message, payload=payload)

    @staticmethod
    def _extract_message(payload: Any | None) -> str | None:
        if isinstance(payload, dict):
            if isinstance(payload.get("detail"), str):
                return payload["detail"]
            if isinstance(payload.get("message"), str):
                return payload["message"]
            error = payload.get("error")
            if isinstance(error, str):
                return error
            if isinstance(error, dict) and isinstance(error.get("message"), str):
                return error["message"]
        if isinstance(payload, str) and payload.strip():
            return payload.strip()
        return None
