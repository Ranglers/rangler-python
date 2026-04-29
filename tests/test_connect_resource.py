import unittest

from ranglerpy.resources.connect import ConnectResource


class _Client:
    def __init__(self) -> None:
        self.calls = []

    def request(self, method, path, *, auth, params=None, json=None):
        self.calls.append(
            {
                "method": method,
                "path": path,
                "auth": auth,
                "params": params,
                "json": json,
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
                }
            ],
        )

    def test_connection_resource_paths(self) -> None:
        client = _Client()
        resource = ConnectResource(client)

        resource.exchange_public_token("rgl_public_123")
        resource.list_institutions()
        resource.list_connections()
        resource.get_connection("conn_123")
        resource.refresh_connection("conn_123")
        resource.list_accounts("conn_123")
        resource.list_positions("conn_123")
        resource.list_transactions("conn_123")
        resource.revoke_connection("conn_123")

        self.assertEqual(
            [call["path"] for call in client.calls],
            [
                "/connect/token/exchange",
                "/connect/institutions",
                "/connect/connections",
                "/connect/connections/conn_123",
                "/connect/connections/conn_123/refresh",
                "/connect/connections/conn_123/accounts",
                "/connect/connections/conn_123/positions",
                "/connect/connections/conn_123/transactions",
                "/connect/connections/conn_123",
            ],
        )


if __name__ == "__main__":
    unittest.main()
