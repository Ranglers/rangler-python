from __future__ import annotations

from typing import Any

from ranglerpy._utils import compact_dict

from .async_base import AsyncBaseResource


def _idempotency_headers(idempotency_key: str | None) -> dict[str, str] | None:
    return {"Idempotency-Key": idempotency_key} if idempotency_key is not None else None


class AsyncConnectResource(AsyncBaseResource):
    async def create_link_token(
        self,
        *,
        client_user_id: str,
        allowed_origins: list[str],
        client_name: str | None = None,
        products: list[str] | None = None,
        institution_ids: list[str] | None = None,
        idempotency_key: str | None = None,
    ) -> Any:
        payload: dict[str, Any] = {
            "client_user_id": client_user_id,
            "allowed_origins": allowed_origins,
        }
        if client_name is not None:
            payload["client_name"] = client_name
        if products is not None:
            payload["products"] = products
        if institution_ids is not None:
            payload["institution_ids"] = institution_ids
        return await self._post(
            "/connect/link-tokens",
            json=payload,
            auth="api_key",
            headers=_idempotency_headers(idempotency_key),
        )

    async def exchange_public_token(self, public_token: str, *, client_user_id: str | None = None) -> Any:
        return await self._post(
            "/connect/token/exchange",
            json=compact_dict({"public_token": public_token, "client_user_id": client_user_id}),
            auth="api_key",
        )

    async def list_institutions(self, *, products: list[str] | None = None) -> Any:
        return await self._get(
            "/connect/institutions",
            params={"products": products} if products is not None else None,
            auth="api_key",
        )

    async def list_developer_institutions(self, organization_id: str, *, environment: str = "live") -> Any:
        return await self._get(
            f"/organizations/{organization_id}/connect/institutions",
            params={"environment": environment},
            auth="bearer",
        )

    async def list_connections(self, *, client_user_id: str | None = None) -> Any:
        return await self._get(
            "/connect/connections",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    async def list_developer_connections(self, organization_id: str, *, environment: str = "live") -> Any:
        return await self._get(
            f"/organizations/{organization_id}/connect/connections",
            params={"environment": environment},
            auth="bearer",
        )

    async def get_portfolio(self, *, client_user_id: str) -> Any:
        return await self._get("/connect/portfolio", params={"client_user_id": client_user_id}, auth="api_key")

    async def get_connection(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return await self._get(
            f"/connect/connections/{connection_id}",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    async def refresh_connection(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return await self._post(
            f"/connect/connections/{connection_id}/refresh",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    async def revoke_connection(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return await self._delete(
            f"/connect/connections/{connection_id}",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    async def list_accounts(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return await self._get(
            f"/connect/connections/{connection_id}/accounts",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    async def list_positions(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return await self._get(
            f"/connect/connections/{connection_id}/positions",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    async def list_transactions(
        self,
        connection_id: str,
        *,
        client_user_id: str | None = None,
        cursor: str | None = None,
        limit: int = 100,
    ) -> Any:
        return await self._get(
            f"/connect/connections/{connection_id}/transactions",
            params=compact_dict({"client_user_id": client_user_id, "cursor": cursor, "limit": limit}),
            auth="api_key",
        )
