from __future__ import annotations

from typing import Any

from ranglerpy._utils import compact_dict

from .base import BaseResource


def _idempotency_headers(idempotency_key: str | None) -> dict[str, str] | None:
    return {"Idempotency-Key": idempotency_key} if idempotency_key is not None else None


class ConnectResource(BaseResource):
    def create_link_token(
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
        return self._post(
            "/connect/link-tokens",
            json=payload,
            auth="api_key",
            headers=_idempotency_headers(idempotency_key),
        )

    def exchange_public_token(self, public_token: str, *, client_user_id: str | None = None) -> Any:
        return self._post(
            "/connect/token/exchange",
            json=compact_dict({"public_token": public_token, "client_user_id": client_user_id}),
            auth="api_key",
        )

    def list_institutions(self, *, products: list[str] | None = None) -> Any:
        return self._get(
            "/connect/institutions",
            params={"products": products} if products is not None else None,
            auth="api_key",
        )

    def list_connections(self, *, client_user_id: str | None = None) -> Any:
        return self._get(
            "/connect/connections",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    def get_portfolio(self, *, client_user_id: str) -> Any:
        return self._get("/connect/portfolio", params={"client_user_id": client_user_id}, auth="api_key")

    def get_connection(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return self._get(
            f"/connect/connections/{connection_id}",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    def refresh_connection(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return self._post(
            f"/connect/connections/{connection_id}/refresh",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    def revoke_connection(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return self._delete(
            f"/connect/connections/{connection_id}",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    def list_accounts(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return self._get(
            f"/connect/connections/{connection_id}/accounts",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    def list_positions(self, connection_id: str, *, client_user_id: str | None = None) -> Any:
        return self._get(
            f"/connect/connections/{connection_id}/positions",
            params=compact_dict({"client_user_id": client_user_id}),
            auth="api_key",
        )

    def list_transactions(
        self,
        connection_id: str,
        *,
        client_user_id: str | None = None,
        cursor: str | None = None,
        limit: int = 100,
    ) -> Any:
        return self._get(
            f"/connect/connections/{connection_id}/transactions",
            params=compact_dict({"client_user_id": client_user_id, "cursor": cursor, "limit": limit}),
            auth="api_key",
        )
