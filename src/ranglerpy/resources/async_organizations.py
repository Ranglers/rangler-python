from __future__ import annotations

from .async_base import AsyncBaseResource


class AsyncOrganizationsResource(AsyncBaseResource):
    async def list(self) -> dict:
        return await self._get("/organizations", auth="bearer")

    async def create(self, *, name: str, billing_email: str) -> dict:
        return await self._post(
            "/organizations",
            json={
                "name": name,
                "billing_email": billing_email,
            },
            auth="bearer",
        )

    async def get(self, organization_id: str) -> dict:
        return await self._get(f"/organizations/{organization_id}", auth="bearer")
