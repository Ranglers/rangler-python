import unittest

from ranglerpy.resources.subscriptions import SubscriptionsResource


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


class SubscriptionsResourceTests(unittest.TestCase):
    def test_market_subscription_resource_paths_and_payloads(self) -> None:
        client = _Client()
        resource = SubscriptionsResource(client)

        resource.list_market("org_123")
        resource.list_market("org_123", cursor="cursor_123", limit=10)
        resource.create_market(
            "org_123",
            destination_id="dest_123",
            name="Filings",
            event_types=["filing.new"],
            company_ids=["company_123"],
        )
        resource.update_market("org_123", "sub_123", name="Updated")
        resource.delete_market("org_123", "sub_123")

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "GET",
                    "path": "/organizations/org_123/market-event-subscriptions",
                    "auth": "bearer",
                    "params": {"limit": 50},
                    "json": None,
                },
                {
                    "method": "GET",
                    "path": "/organizations/org_123/market-event-subscriptions",
                    "auth": "bearer",
                    "params": {"cursor": "cursor_123", "limit": 10},
                    "json": None,
                },
                {
                    "method": "POST",
                    "path": "/organizations/org_123/market-event-subscriptions",
                    "auth": "bearer",
                    "params": None,
                    "json": {
                        "destination_id": "dest_123",
                        "name": "Filings",
                        "environment": "live",
                        "event_types": ["filing.new"],
                        "company_ids": ["company_123"],
                        "fund_ids": [],
                        "is_active": True,
                    },
                },
                {
                    "method": "PATCH",
                    "path": "/organizations/org_123/market-event-subscriptions/sub_123",
                    "auth": "bearer",
                    "params": None,
                    "json": {"name": "Updated"},
                },
                {
                    "method": "DELETE",
                    "path": "/organizations/org_123/market-event-subscriptions/sub_123",
                    "auth": "bearer",
                    "params": None,
                    "json": None,
                },
            ],
        )

    def test_connect_subscription_resource_paths_and_payloads(self) -> None:
        client = _Client()
        resource = SubscriptionsResource(client)

        resource.list_connect("org_123", limit=20)
        resource.create_connect(
            "org_123",
            destination_id="dest_123",
            name="Connect syncs",
            event_types=["connect.sync.completed"],
            environment="test",
            connection_ids=["conn_123"],
            institution_ids=["sandbox_brokerage"],
            client_user_ids=["customer_123"],
        )
        resource.update_connect("org_123", "sub_123", is_active=False)
        resource.delete_connect("org_123", "sub_123")

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "GET",
                    "path": "/organizations/org_123/connect-event-subscriptions",
                    "auth": "bearer",
                    "params": {"limit": 20},
                    "json": None,
                },
                {
                    "method": "POST",
                    "path": "/organizations/org_123/connect-event-subscriptions",
                    "auth": "bearer",
                    "params": None,
                    "json": {
                        "destination_id": "dest_123",
                        "name": "Connect syncs",
                        "environment": "test",
                        "event_types": ["connect.sync.completed"],
                        "connection_ids": ["conn_123"],
                        "institution_ids": ["sandbox_brokerage"],
                        "client_user_ids": ["customer_123"],
                        "is_active": True,
                    },
                },
                {
                    "method": "PATCH",
                    "path": "/organizations/org_123/connect-event-subscriptions/sub_123",
                    "auth": "bearer",
                    "params": None,
                    "json": {"is_active": False},
                },
                {
                    "method": "DELETE",
                    "path": "/organizations/org_123/connect-event-subscriptions/sub_123",
                    "auth": "bearer",
                    "params": None,
                    "json": None,
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
