from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ranglerpy.client import RanglerClient


class BaseResource:
    def __init__(self, client: "RanglerClient") -> None:
        self.client = client

    def _get(self, path: str, *, params: dict[str, Any] | None = None, auth: str) -> Any:
        return self.client.request("GET", path, params=params, auth=auth)

    def _post(self, path: str, *, json: dict[str, Any] | None = None, auth: str) -> Any:
        return self.client.request("POST", path, json=json, auth=auth)

    def _patch(self, path: str, *, json: dict[str, Any] | None = None, auth: str) -> Any:
        return self.client.request("PATCH", path, json=json, auth=auth)

    def _delete(self, path: str, *, auth: str) -> Any:
        return self.client.request("DELETE", path, auth=auth)
