from __future__ import annotations

from typing import Any

import httpx

from .exceptions import APIError, AuthenticationError
from .resources import (
    APIKeysResource,
    CompaniesResource,
    EventsResource,
    FilingsResource,
    OrganizationsResource,
    SubscriptionsResource,
    UsageResource,
    WebhooksResource,
)
from .resources.async_api_keys import AsyncAPIKeysResource
from .resources.async_companies import AsyncCompaniesResource
from .resources.async_events import AsyncEventsResource
from .resources.async_filings import AsyncFilingsResource
from .resources.async_organizations import AsyncOrganizationsResource
from .resources.async_subscriptions import AsyncSubscriptionsResource
from .resources.async_usage import AsyncUsageResource
from .resources.async_webhooks import AsyncWebhooksResource


class RanglerClient:
    LIVE_BASE_URL = "https://api.rangler.co/v1"
    SANDBOX_BASE_URL = "https://sandbox-api.rangler.co/v1"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        bearer_token: str | None = None,
        base_url: str | None = None,
        environment: str = "live",
        timeout: float = 30.0,
        user_agent: str = "ranglerpy/0.1.0",
    ) -> None:
        if environment not in {"live", "sandbox"}:
            raise ValueError("environment must be 'live' or 'sandbox'")

        resolved_base_url = base_url or (
            self.SANDBOX_BASE_URL if environment == "sandbox" else self.LIVE_BASE_URL
        )
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.base_url = resolved_base_url.rstrip("/")
        self.environment = environment
        self._http = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "User-Agent": user_agent,
                "Accept": "application/json",
            },
        )

        self.companies = CompaniesResource(self)
        self.events = EventsResource(self)
        self.filings = FilingsResource(self)
        self.organizations = OrganizationsResource(self)
        self.api_keys = APIKeysResource(self)
        self.usage = UsageResource(self)
        self.webhooks = WebhooksResource(self)
        self.subscriptions = SubscriptionsResource(self)

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
    ) -> Any:
        headers = self._build_auth_headers(auth)
        response = self._http.request(
            method=method,
            url=path,
            headers=headers,
            params=params,
            json=json,
        )
        if not response.is_success:
            raise APIError.from_response(response)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def _build_auth_headers(self, auth: str) -> dict[str, str]:
        if auth == "api_key":
            if not self.api_key:
                raise AuthenticationError("This operation requires an Atlas X-API-Key")
            return {"X-API-Key": self.api_key}
        if auth == "bearer":
            if not self.bearer_token:
                raise AuthenticationError("This operation requires an Atlas portal bearer token")
            return {"Authorization": f"Bearer {self.bearer_token}"}
        raise ValueError("auth must be 'api_key' or 'bearer'")


class AsyncRanglerClient:
    LIVE_BASE_URL = RanglerClient.LIVE_BASE_URL
    SANDBOX_BASE_URL = RanglerClient.SANDBOX_BASE_URL

    def __init__(
        self,
        *,
        api_key: str | None = None,
        bearer_token: str | None = None,
        base_url: str | None = None,
        environment: str = "live",
        timeout: float = 30.0,
        user_agent: str = "ranglerpy/0.1.0",
    ) -> None:
        if environment not in {"live", "sandbox"}:
            raise ValueError("environment must be 'live' or 'sandbox'")

        resolved_base_url = base_url or (
            self.SANDBOX_BASE_URL if environment == "sandbox" else self.LIVE_BASE_URL
        )
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.base_url = resolved_base_url.rstrip("/")
        self.environment = environment
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "User-Agent": user_agent,
                "Accept": "application/json",
            },
        )

        self.companies = AsyncCompaniesResource(self)
        self.events = AsyncEventsResource(self)
        self.filings = AsyncFilingsResource(self)
        self.organizations = AsyncOrganizationsResource(self)
        self.api_keys = AsyncAPIKeysResource(self)
        self.usage = AsyncUsageResource(self)
        self.webhooks = AsyncWebhooksResource(self)
        self.subscriptions = AsyncSubscriptionsResource(self)

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
    ) -> Any:
        headers = self._build_auth_headers(auth)
        response = await self._http.request(
            method=method,
            url=path,
            headers=headers,
            params=params,
            json=json,
        )
        if not response.is_success:
            raise APIError.from_response(response)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def _build_auth_headers(self, auth: str) -> dict[str, str]:
        if auth == "api_key":
            if not self.api_key:
                raise AuthenticationError("This operation requires an Atlas X-API-Key")
            return {"X-API-Key": self.api_key}
        if auth == "bearer":
            if not self.bearer_token:
                raise AuthenticationError("This operation requires an Atlas portal bearer token")
            return {"Authorization": f"Bearer {self.bearer_token}"}
        raise ValueError("auth must be 'api_key' or 'bearer'")
