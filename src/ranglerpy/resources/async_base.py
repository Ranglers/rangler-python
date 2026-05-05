from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ranglerpy.client import AsyncRanglerClient


class AsyncBaseResource:
    def __init__(self, client: "AsyncRanglerClient") -> None:
        self.client = client

    async def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        auth: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {"params": params, "auth": auth}
        if headers is not None:
            kwargs["headers"] = headers
        return await self.client.request("GET", path, **kwargs)

    async def _post(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        auth: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {"params": params, "json": json, "auth": auth}
        if headers is not None:
            kwargs["headers"] = headers
        return await self.client.request("POST", path, **kwargs)

    async def _patch(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        auth: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {"params": params, "json": json, "auth": auth}
        if headers is not None:
            kwargs["headers"] = headers
        return await self.client.request("PATCH", path, **kwargs)

    async def _delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        auth: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {"params": params, "auth": auth}
        if headers is not None:
            kwargs["headers"] = headers
        return await self.client.request("DELETE", path, **kwargs)
