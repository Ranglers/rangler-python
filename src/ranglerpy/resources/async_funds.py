from __future__ import annotations

from typing import Any

from .async_base import AsyncBaseResource


class AsyncFundsResource(AsyncBaseResource):
    async def list(self, **params: Any) -> Any:
        return await self._get("/funds", params=params or None, auth="api_key")

    async def get(self, fund_id: str) -> Any:
        return await self._get(f"/funds/{fund_id}", auth="api_key")

    async def list_snapshots(self, fund_id: str, **params: Any) -> Any:
        return await self._get(f"/funds/{fund_id}/snapshots", params=params or None, auth="api_key")
