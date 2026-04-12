from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ranglerpy.client import AsyncRanglerClient


class AsyncBaseResource:
    def __init__(self, client: "AsyncRanglerClient") -> None:
        self.client = client

    async def _get(self, path: str, *, params: dict[str, Any] | None = None, auth: str) -> Any:
        return await self.client.request("GET", path, params=params, auth=auth)

    async def _post(self, path: str, *, json: dict[str, Any] | None = None, auth: str) -> Any:
        return await self.client.request("POST", path, json=json, auth=auth)

    async def _patch(self, path: str, *, json: dict[str, Any] | None = None, auth: str) -> Any:
        return await self.client.request("PATCH", path, json=json, auth=auth)

    async def _delete(self, path: str, *, auth: str) -> Any:
        return await self.client.request("DELETE", path, auth=auth)
