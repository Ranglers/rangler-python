from __future__ import annotations

from typing import Any

from .base import BaseResource


class ConnectResource(BaseResource):
    def create_link_token(
        self,
        *,
        client_user_id: str,
        allowed_origins: list[str],
        client_name: str | None = None,
        products: list[str] | None = None,
        institution_ids: list[str] | None = None,
        redirect_uri: str | None = None,
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
        if redirect_uri is not None:
            payload["redirect_uri"] = redirect_uri
        return self._post("/connect/link-tokens", json=payload, auth="api_key")

    def exchange_public_token(self, public_token: str) -> Any:
        return self._post("/connect/token/exchange", json={"public_token": public_token}, auth="api_key")

    def list_institutions(self) -> Any:
        return self._get("/connect/institutions", auth="api_key")

    def list_connections(self) -> Any:
        return self._get("/connect/connections", auth="api_key")

    def get_connection(self, connection_id: str) -> Any:
        return self._get(f"/connect/connections/{connection_id}", auth="api_key")

    def refresh_connection(self, connection_id: str) -> Any:
        return self._post(f"/connect/connections/{connection_id}/refresh", auth="api_key")

    def revoke_connection(self, connection_id: str) -> Any:
        return self._delete(f"/connect/connections/{connection_id}", auth="api_key")

    def list_accounts(self, connection_id: str) -> Any:
        return self._get(f"/connect/connections/{connection_id}/accounts", auth="api_key")

    def list_positions(self, connection_id: str) -> Any:
        return self._get(f"/connect/connections/{connection_id}/positions", auth="api_key")

    def list_transactions(self, connection_id: str) -> Any:
        return self._get(f"/connect/connections/{connection_id}/transactions", auth="api_key")
