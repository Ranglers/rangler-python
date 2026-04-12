from __future__ import annotations

from typing import Any

from .async_base import AsyncBaseResource


class AsyncCompaniesResource(AsyncBaseResource):
    async def list(self, **params: Any) -> Any:
        return await self._get("/companies", params=params or None, auth="api_key")

    async def get(self, company_id: str) -> Any:
        return await self._get(f"/companies/{company_id}", auth="api_key")

    async def get_details(self, company_id: str) -> Any:
        return await self._get(f"/companies/{company_id}/details", auth="api_key")

    async def list_filings(self, company_id: str, **params: Any) -> Any:
        return await self._get(f"/companies/{company_id}/filings", params=params or None, auth="api_key")
