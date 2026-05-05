import importlib
import sys
import types
import unittest


class _FakeResponse:
    is_success = True
    status_code = 200
    content = b"{}"

    def json(self):
        return {}


class _FakeSyncHttpxClient:
    def __init__(self, *args, **kwargs) -> None:
        self.base_url = kwargs.get("base_url")
        self.timeout = kwargs.get("timeout")
        self.headers = kwargs.get("headers", {})
        self.requests = []

    def request(self, *args, **kwargs):
        self.requests.append({"args": args, "kwargs": kwargs})
        return _FakeResponse()

    def close(self) -> None:
        return None


class _FakeAsyncHttpxClient:
    def __init__(self, *args, **kwargs) -> None:
        self.base_url = kwargs.get("base_url")
        self.timeout = kwargs.get("timeout")
        self.headers = kwargs.get("headers", {})
        self.requests = []

    async def request(self, *args, **kwargs):
        self.requests.append({"args": args, "kwargs": kwargs})
        return _FakeResponse()

    async def aclose(self) -> None:
        return None


def _install_fake_httpx() -> None:
    sys.modules["httpx"] = types.SimpleNamespace(
        Client=_FakeSyncHttpxClient,
        AsyncClient=_FakeAsyncHttpxClient,
        Response=object,
    )


_install_fake_httpx()
client_module = importlib.import_module("ranglerpy.client")
RanglerClient = client_module.RanglerClient
AsyncRanglerClient = client_module.AsyncRanglerClient
AuthenticationError = importlib.import_module("ranglerpy.exceptions").AuthenticationError
__version__ = importlib.import_module("ranglerpy._version").__version__


class RanglerClientTests(unittest.TestCase):
    def test_client_uses_sandbox_base_url(self) -> None:
        client = RanglerClient(api_key="rgl_test_123", environment="sandbox")
        try:
            self.assertEqual(client.base_url, "https://sandbox-api.rangler.co/v1")
            self.assertEqual(client.api_version, "v1")
            self.assertEqual(client._http.headers["User-Agent"], f"ranglerpy/{__version__}")
            self.assertEqual(client._http.headers["Rangler-Version"], "v1")
            self.assertTrue(hasattr(client, "funds"))
            self.assertTrue(hasattr(client, "connect"))
            self.assertFalse(hasattr(client, "event_destinations"))
            self.assertFalse(hasattr(client, "organizations"))
            self.assertFalse(hasattr(client, "api_keys"))
            self.assertFalse(hasattr(client, "usage"))
            self.assertFalse(hasattr(client, "subscriptions"))
            self.assertIs(client.v1.events, client.events)
            self.assertIs(client.v1.companies, client.companies)
            self.assertIs(client.v1.connect, client.connect)
            self.assertFalse(hasattr(client, "webhooks"))
        finally:
            client.close()

    def test_api_key_auth_requirement_is_enforced(self) -> None:
        client = RanglerClient(api_key="rgl_test_123")
        try:
            client.api_key = None
            with self.assertRaises(AuthenticationError):
                client._build_auth_headers("api_key")
        finally:
            client.close()

    def test_api_key_requests_stay_on_data_base_url(self) -> None:
        client = RanglerClient(api_key="rgl_live_123")
        try:
            client.request("GET", "/events", auth="api_key")
            self.assertEqual(client._http.requests[0]["kwargs"]["url"], "/events")
            self.assertEqual(client._http.requests[0]["kwargs"]["headers"], {"X-API-Key": "rgl_live_123"})
        finally:
            client.close()

    def test_async_client_uses_sandbox_base_url(self) -> None:
        client = AsyncRanglerClient(api_key="rgl_test_123", environment="sandbox")
        self.assertEqual(client.base_url, "https://sandbox-api.rangler.co/v1")
        self.assertEqual(client.api_version, "v1")
        self.assertEqual(client._http.headers["User-Agent"], f"ranglerpy/{__version__}")
        self.assertEqual(client._http.headers["Rangler-Version"], "v1")
        self.assertTrue(hasattr(client, "funds"))
        self.assertTrue(hasattr(client, "connect"))
        self.assertFalse(hasattr(client, "event_destinations"))
        self.assertFalse(hasattr(client, "organizations"))
        self.assertFalse(hasattr(client, "api_keys"))
        self.assertFalse(hasattr(client, "usage"))
        self.assertFalse(hasattr(client, "subscriptions"))
        self.assertIs(client.v1.events, client.events)
        self.assertIs(client.v1.connect, client.connect)
        self.assertFalse(hasattr(client, "webhooks"))

    def test_client_allows_custom_api_version_header(self) -> None:
        client = RanglerClient(api_key="rgl_test_123", api_version="v1.preview")
        try:
            self.assertEqual(client.api_version, "v1.preview")
            self.assertEqual(client._http.headers["Rangler-Version"], "v1.preview")
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
