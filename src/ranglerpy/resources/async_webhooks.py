from __future__ import annotations

from .async_base import AsyncBaseResource


class AsyncWebhooksResource(AsyncBaseResource):
    async def list(self, organization_id: str) -> list[dict]:
        return await self._get(f"/organizations/{organization_id}/webhooks", auth="bearer")

    async def create(self, organization_id: str, *, url: str) -> dict:
        return await self._post(
            f"/organizations/{organization_id}/webhooks",
            json={"url": url},
            auth="bearer",
        )

    async def update(self, organization_id: str, webhook_id: str, *, is_active: bool) -> dict:
        return await self._patch(
            f"/organizations/{organization_id}/webhooks/{webhook_id}",
            json={"is_active": is_active},
            auth="bearer",
        )

    async def delete(self, organization_id: str, webhook_id: str) -> None:
        await self._delete(f"/organizations/{organization_id}/webhooks/{webhook_id}", auth="bearer")

    async def rotate_secret(self, organization_id: str, webhook_id: str) -> dict:
        return await self._post(
            f"/organizations/{organization_id}/webhooks/{webhook_id}/rotate-secret",
            auth="bearer",
        )

    async def ping(self, organization_id: str, webhook_id: str) -> dict:
        return await self._post(
            f"/organizations/{organization_id}/webhooks/{webhook_id}/ping",
            auth="bearer",
        )

    async def deliveries(self, organization_id: str, webhook_id: str, *, limit: int = 50) -> list[dict]:
        return await self._get(
            f"/organizations/{organization_id}/webhooks/{webhook_id}/deliveries",
            params={"limit": limit},
            auth="bearer",
        )

    async def delivery_detail(self, organization_id: str, webhook_id: str, attempt_id: str) -> dict:
        return await self._get(
            f"/organizations/{organization_id}/webhooks/{webhook_id}/deliveries/{attempt_id}",
            auth="bearer",
        )

    async def delivery_health(self, organization_id: str, webhook_id: str, *, limit: int = 100) -> dict:
        return await self._get(
            f"/organizations/{organization_id}/webhooks/{webhook_id}/health",
            params={"limit": limit},
            auth="bearer",
        )

    async def redeliver(self, organization_id: str, webhook_id: str, attempt_id: str) -> dict:
        return await self._post(
            f"/organizations/{organization_id}/webhooks/{webhook_id}/deliveries/{attempt_id}/redeliver",
            auth="bearer",
        )
