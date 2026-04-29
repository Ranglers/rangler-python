import unittest

from ranglerpy.resources.webhooks import EventDestinationsResource


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


class EventDestinationsResourceTests(unittest.TestCase):
    def test_event_destination_resource_paths(self) -> None:
        client = _Client()
        resource = EventDestinationsResource(client)

        resource.list("org_123")
        resource.create("org_123", url="https://example.com/rangler/webhooks")
        resource.update("org_123", "dest_123", is_active=False)
        resource.portal("org_123")
        resource.deliveries("org_123", "dest_123", limit=25)
        resource.delivery_detail("org_123", "dest_123", "attempt_123")
        resource.delivery_health("org_123", "dest_123", limit=10)
        resource.redeliver("org_123", "dest_123", "attempt_123")
        resource.delete("org_123", "dest_123")

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "GET",
                    "path": "/organizations/org_123/event-destinations",
                    "auth": "bearer",
                    "params": None,
                    "json": None,
                },
                {
                    "method": "POST",
                    "path": "/organizations/org_123/event-destinations",
                    "auth": "bearer",
                    "params": None,
                    "json": {"url": "https://example.com/rangler/webhooks"},
                },
                {
                    "method": "PATCH",
                    "path": "/organizations/org_123/event-destinations/dest_123",
                    "auth": "bearer",
                    "params": None,
                    "json": {"is_active": False},
                },
                {
                    "method": "GET",
                    "path": "/organizations/org_123/event-destinations/portal",
                    "auth": "bearer",
                    "params": None,
                    "json": None,
                },
                {
                    "method": "GET",
                    "path": "/organizations/org_123/event-destinations/dest_123/deliveries",
                    "auth": "bearer",
                    "params": {"limit": 25},
                    "json": None,
                },
                {
                    "method": "GET",
                    "path": "/organizations/org_123/event-destinations/dest_123/deliveries/attempt_123",
                    "auth": "bearer",
                    "params": None,
                    "json": None,
                },
                {
                    "method": "GET",
                    "path": "/organizations/org_123/event-destinations/dest_123/health",
                    "auth": "bearer",
                    "params": {"limit": 10},
                    "json": None,
                },
                {
                    "method": "POST",
                    "path": "/organizations/org_123/event-destinations/dest_123/deliveries/attempt_123/redeliver",
                    "auth": "bearer",
                    "params": None,
                    "json": None,
                },
                {
                    "method": "DELETE",
                    "path": "/organizations/org_123/event-destinations/dest_123",
                    "auth": "bearer",
                    "params": None,
                    "json": None,
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
