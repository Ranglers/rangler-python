from __future__ import annotations

from typing import Any

from .async_base import AsyncBaseResource


class AsyncFilingsResource(AsyncBaseResource):
    async def list(self, **params: Any) -> Any:
        return await self._get("/filings", params=params or None, auth="api_key")

    async def get(self, filing_id: str) -> Any:
        return await self._get(f"/filings/{filing_id}", auth="api_key")
