from __future__ import annotations

from collections.abc import Sequence

from .async_base import AsyncBaseResource


class AsyncAPIKeysResource(AsyncBaseResource):
    async def list(self, organization_id: str) -> list[dict]:
        return await self._get(f"/organizations/{organization_id}/api-keys", auth="bearer")

    async def create(
        self,
        organization_id: str,
        *,
        name: str,
        environment: str = "live",
        expires_at: str | None = None,
        scopes: Sequence[str] | None = None,
    ) -> dict:
        payload = {
            "name": name,
            "environment": environment,
        }
        if expires_at is not None:
            payload["expires_at"] = expires_at
        if scopes is not None:
            payload["scopes"] = list(scopes)
        return await self._post(
            f"/organizations/{organization_id}/api-keys",
            json=payload,
            auth="bearer",
        )

    async def revoke(self, organization_id: str, key_id: str) -> None:
        await self._delete(f"/organizations/{organization_id}/api-keys/{key_id}", auth="bearer")
