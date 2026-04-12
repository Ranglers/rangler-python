from __future__ import annotations

from .base import BaseResource


class APIKeysResource(BaseResource):
    def list(self, organization_id: str) -> list[dict]:
        return self._get(f"/organizations/{organization_id}/api-keys", auth="bearer")

    def create(
        self,
        organization_id: str,
        *,
        name: str,
        environment: str = "live",
        expires_at: str | None = None,
    ) -> dict:
        payload = {
            "name": name,
            "environment": environment,
        }
        if expires_at is not None:
            payload["expires_at"] = expires_at
        return self._post(
            f"/organizations/{organization_id}/api-keys",
            json=payload,
            auth="bearer",
        )

    def revoke(self, organization_id: str, key_id: str) -> None:
        self._delete(f"/organizations/{organization_id}/api-keys/{key_id}", auth="bearer")
