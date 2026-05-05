import unittest

from ranglerpy.resources.async_api_keys import AsyncAPIKeysResource
from ranglerpy.resources.api_keys import APIKeysResource


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


class APIKeysResourceTests(unittest.TestCase):
    def test_create_api_key_supports_scopes(self) -> None:
        client = _Client()
        resource = APIKeysResource(client)

        resource.create(
            "org_123",
            name="Connect key",
            environment="test",
            expires_at="2026-12-01T00:00:00Z",
            scopes=["connect", "events"],
        )

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "POST",
                    "path": "/organizations/org_123/api-keys",
                    "auth": "bearer",
                    "params": None,
                    "json": {
                        "name": "Connect key",
                        "environment": "test",
                        "expires_at": "2026-12-01T00:00:00Z",
                        "scopes": ["connect", "events"],
                    },
                    "headers": None,
                }
            ],
        )

    def test_create_api_key_keeps_scopes_omitted_by_default(self) -> None:
        client = _Client()
        resource = APIKeysResource(client)

        resource.create("org_123", name="Default key")

        self.assertEqual(
            client.calls[0]["json"],
            {
                "name": "Default key",
                "environment": "live",
            },
        )


class AsyncAPIKeysResourceTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_create_api_key_supports_scopes(self) -> None:
        client = _AsyncClient()
        resource = AsyncAPIKeysResource(client)

        await resource.create(
            "org_123",
            name="Connect key",
            environment="test",
            scopes=["connect"],
        )

        self.assertEqual(
            client.calls,
            [
                {
                    "method": "POST",
                    "path": "/organizations/org_123/api-keys",
                    "auth": "bearer",
                    "params": None,
                    "json": {
                        "name": "Connect key",
                        "environment": "test",
                        "scopes": ["connect"],
                    },
                    "headers": None,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
