import unittest

from ranglerpy.resources.async_connect import AsyncConnectResource
from ranglerpy.resources.connect import ConnectResource


class _Client:
    def __init__(self) -> None:
        self.calls = []

    def request(self, method, path, *, auth, params=None, json=None, headers=None):
        self.calls.append(
            {
                "method": method,
                "path": path,
                "auth": auth,
                "params": params,
                "json": json,
                "headers": headers,
            }
        )
        return {"ok": True}


class _AsyncClient:
    def __init__(self) -> None:
        self.calls = []

    async def request(self, method, path, *, auth, params=None, json=None, headers=None):
        self.calls.append(
            {
                "method": method,
                "path": path,
                "auth": auth,
                "params": params,
                "json": json,
                "headers": headers,
            }
        )
        return {"ok": True}


class ConnectResourceTests(unittest.TestCase):
    def test_create_link_token_payload(self) -> None:
        client = _Client()
        resource = ConnectResource(client)

        resource.create_link_token(
            client_user_id="customer_123",
            client_name="Ada",
            products=["accounts", "positions"],
            institution_ids=["sandbox_invest"],
            allowed_origins=["https://app.example.com"],
            idempotency_key="link-token-1",
        )

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "POST",
                    "path": "/connect/link-tokens",
                    "auth": "api_key",
                    "params": None,
                    "json": {
                        "client_user_id": "customer_123",
                        "client_name": "Ada",
                        "products": ["accounts", "positions"],
                        "institution_ids": ["sandbox_invest"],
                        "allowed_origins": ["https://app.example.com"],
                    },
                    "headers": {"Idempotency-Key": "link-token-1"},
                }
            ],
        )

    def test_connection_resource_paths(self) -> None:
        client = _Client()
        resource = ConnectResource(client)

        resource.exchange_public_token("rgl_public_123", client_user_id="customer_123")
        resource.list_institutions(products=["accounts"])
        resource.list_connections(client_user_id="customer_123")
        resource.get_portfolio(client_user_id="customer_123")
        resource.get_connection("conn_123", client_user_id="customer_123")
        resource.refresh_connection("conn_123", client_user_id="customer_123")
        resource.list_accounts("conn_123", client_user_id="customer_123")
        resource.list_positions("conn_123", client_user_id="customer_123")
        resource.list_transactions("conn_123", client_user_id="customer_123", cursor="cursor_123", limit=50)
        resource.revoke_connection("conn_123", client_user_id="customer_123")

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "POST",
                    "path": "/connect/token/exchange",
                    "auth": "api_key",
                    "params": None,
                    "json": {"public_token": "rgl_public_123", "client_user_id": "customer_123"},
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/connect/institutions",
                    "auth": "api_key",
                    "params": {"products": ["accounts"]},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/connect/connections",
                    "auth": "api_key",
                    "params": {"client_user_id": "customer_123"},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/connect/portfolio",
                    "auth": "api_key",
                    "params": {"client_user_id": "customer_123"},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/connect/connections/conn_123",
                    "auth": "api_key",
                    "params": {"client_user_id": "customer_123"},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "POST",
                    "path": "/connect/connections/conn_123/refresh",
                    "auth": "api_key",
                    "params": {"client_user_id": "customer_123"},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/connect/connections/conn_123/accounts",
                    "auth": "api_key",
                    "params": {"client_user_id": "customer_123"},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/connect/connections/conn_123/positions",
                    "auth": "api_key",
                    "params": {"client_user_id": "customer_123"},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/connect/connections/conn_123/transactions",
                    "auth": "api_key",
                    "params": {"client_user_id": "customer_123", "cursor": "cursor_123", "limit": 50},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "DELETE",
                    "path": "/connect/connections/conn_123",
                    "auth": "api_key",
                    "params": {"client_user_id": "customer_123"},
                    "json": None,
                    "headers": None,
                },
            ],
        )

    def test_developer_connection_resource_paths(self) -> None:
        client = _Client()
        resource = ConnectResource(client)

        resource.list_developer_institutions("org_123", environment="test")
        resource.list_developer_connections("org_123")

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "GET",
                    "path": "/organizations/org_123/connect/institutions",
                    "auth": "bearer",
                    "params": {"environment": "test"},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/organizations/org_123/connect/connections",
                    "auth": "bearer",
                    "params": {"environment": "live"},
                    "json": None,
                    "headers": None,
                },
            ],
        )


class AsyncConnectResourceTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_create_link_token_payload(self) -> None:
        client = _AsyncClient()
        resource = AsyncConnectResource(client)

        await resource.create_link_token(
            client_user_id="customer_123",
            allowed_origins=["https://app.example.com"],
            idempotency_key="link-token-1",
        )

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "POST",
                    "path": "/connect/link-tokens",
                    "auth": "api_key",
                    "params": None,
                    "json": {
                        "client_user_id": "customer_123",
                        "allowed_origins": ["https://app.example.com"],
                    },
                    "headers": {"Idempotency-Key": "link-token-1"},
                }
            ],
        )

    async def test_async_developer_connection_resource_paths(self) -> None:
        client = _AsyncClient()
        resource = AsyncConnectResource(client)

        await resource.list_developer_institutions("org_123", environment="test")
        await resource.list_developer_connections("org_123")

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "GET",
                    "path": "/organizations/org_123/connect/institutions",
                    "auth": "bearer",
                    "params": {"environment": "test"},
                    "json": None,
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/organizations/org_123/connect/connections",
                    "auth": "bearer",
                    "params": {"environment": "live"},
                    "json": None,
                    "headers": None,
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
