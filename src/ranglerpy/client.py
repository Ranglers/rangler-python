from __future__ import annotations

from typing import Any, Literal, Mapping

import httpx

from ._api_version import _ApiVersion
from ._version import __version__
from .exceptions import APIError, AuthenticationError
from .idempotency import IdempotencyStore
from .models import EventEnvelope, RanglerObject
from .resources import (
    CompaniesResource,
    ConnectResource,
    EventsResource,
    FilingsResource,
    FundsResource,
)
from .resources.async_companies import AsyncCompaniesResource
from .resources.async_connect import AsyncConnectResource
from .resources.async_events import AsyncEventsResource
from .resources.async_filings import AsyncFilingsResource
from .resources.async_funds import AsyncFundsResource
from .webhooks import Webhook


def _is_absolute_url(url: str) -> bool:
    return url.startswith(("http://", "https://"))


def _request_url(path: str) -> str:
    if _is_absolute_url(path):
        return path
    return path if path.startswith("/") else f"/{path}"


class RanglerV1Namespace:
    def __init__(self, client: "RanglerClient") -> None:
        self.companies = client.companies
        self.connect = client.connect
        self.events = client.events
        self.filings = client.filings
        self.funds = client.funds


class AsyncRanglerV1Namespace:
    def __init__(self, client: "AsyncRanglerClient") -> None:
        self.companies = client.companies
        self.connect = client.connect
        self.events = client.events
        self.filings = client.filings
        self.funds = client.funds


class RanglerClient:
    LIVE_BASE_URL = "https://api.rangler.co/v1"
    SANDBOX_BASE_URL = "https://sandbox-api.rangler.co/v1"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        environment: str = "live",
        timeout: float = 30.0,
        api_version: str = _ApiVersion.CURRENT,
        user_agent: str = f"ranglerpy/{__version__}",
    ) -> None:
        if environment not in {"live", "sandbox"}:
            raise ValueError("environment must be 'live' or 'sandbox'")

        resolved_base_url = base_url or (
            self.SANDBOX_BASE_URL if environment == "sandbox" else self.LIVE_BASE_URL
        )
        self.api_key = api_key
        self.base_url = resolved_base_url.rstrip("/")
        self.environment = environment
        self.api_version = api_version
        self._http = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "User-Agent": user_agent,
                "Accept": "application/json",
                "Rangler-Version": api_version,
            },
        )

        self.companies = CompaniesResource(self)
        self.connect = ConnectResource(self)
        self.events = EventsResource(self)
        self.filings = FilingsResource(self)
        self.funds = FundsResource(self)
        self.v1 = RanglerV1Namespace(self)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "RanglerClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        auth: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        request_headers = self._build_auth_headers(auth)
        if headers:
            request_headers.update(headers)
        response = self._http.request(
            method=method,
            url=_request_url(path),
            headers=request_headers,
            params=params,
            json=json,
        )
        if not response.is_success:
            raise APIError.from_response(response)
        if response.status_code == 204 or not response.content:
            return None
        return RanglerObject.from_value(response.json())

    def construct_event(
        self,
        *,
        raw_body: bytes,
        headers: Mapping[str, str],
        secret: str,
        max_age_seconds: int | None = 300,
        idempotency_store: IdempotencyStore | None = None,
        idempotency_key: Literal["event_id", "webhook_id"] = "event_id",
    ) -> EventEnvelope:
        return Webhook.construct_event(
            headers=headers,
            raw_body=raw_body,
            secret=secret,
            max_age_seconds=max_age_seconds,
            idempotency_store=idempotency_store,
            idempotency_key=idempotency_key,
        )

    def _build_auth_headers(self, auth: str) -> dict[str, str]:
        if auth == "api_key":
            if not self.api_key:
                raise AuthenticationError("This operation requires a Rangler X-API-Key")
            return {"X-API-Key": self.api_key}
        raise ValueError("auth must be 'api_key'")


class AsyncRanglerClient:
    LIVE_BASE_URL = RanglerClient.LIVE_BASE_URL
    SANDBOX_BASE_URL = RanglerClient.SANDBOX_BASE_URL

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        environment: str = "live",
        timeout: float = 30.0,
        api_version: str = _ApiVersion.CURRENT,
        user_agent: str = f"ranglerpy/{__version__}",
    ) -> None:
        if environment not in {"live", "sandbox"}:
            raise ValueError("environment must be 'live' or 'sandbox'")

        resolved_base_url = base_url or (
            self.SANDBOX_BASE_URL if environment == "sandbox" else self.LIVE_BASE_URL
        )
        self.api_key = api_key
        self.base_url = resolved_base_url.rstrip("/")
        self.environment = environment
        self.api_version = api_version
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "User-Agent": user_agent,
                "Accept": "application/json",
                "Rangler-Version": api_version,
            },
        )

        self.companies = AsyncCompaniesResource(self)
        self.connect = AsyncConnectResource(self)
        self.events = AsyncEventsResource(self)
        self.filings = AsyncFilingsResource(self)
        self.funds = AsyncFundsResource(self)
        self.v1 = AsyncRanglerV1Namespace(self)

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncRanglerClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def request(
        self,
        method: str,
        path: str,
        *,
        auth: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        request_headers = self._build_auth_headers(auth)
        if headers:
            request_headers.update(headers)
        response = await self._http.request(
            method=method,
            url=_request_url(path),
            headers=request_headers,
            params=params,
            json=json,
        )
        if not response.is_success:
            raise APIError.from_response(response)
        if response.status_code == 204 or not response.content:
            return None
        return RanglerObject.from_value(response.json())

    def construct_event(
        self,
        *,
        raw_body: bytes,
        headers: Mapping[str, str],
        secret: str,
        max_age_seconds: int | None = 300,
        idempotency_store: IdempotencyStore | None = None,
        idempotency_key: Literal["event_id", "webhook_id"] = "event_id",
    ) -> EventEnvelope:
        return Webhook.construct_event(
            headers=headers,
            raw_body=raw_body,
            secret=secret,
            max_age_seconds=max_age_seconds,
            idempotency_store=idempotency_store,
            idempotency_key=idempotency_key,
        )

    def _build_auth_headers(self, auth: str) -> dict[str, str]:
        if auth == "api_key":
            if not self.api_key:
                raise AuthenticationError("This operation requires a Rangler X-API-Key")
            return {"X-API-Key": self.api_key}
        raise ValueError("auth must be 'api_key'")
