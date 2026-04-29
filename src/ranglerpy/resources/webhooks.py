from __future__ import annotations

from .base import BaseResource


class EventDestinationsResource(BaseResource):
    def list(self, organization_id: str) -> list[dict]:
        return self._get(f"/organizations/{organization_id}/event-destinations", auth="bearer")

    def create(self, organization_id: str, *, url: str) -> dict:
        return self._post(
            f"/organizations/{organization_id}/event-destinations",
            json={"url": url},
            auth="bearer",
        )

    def update(
        self,
        organization_id: str,
        destination_id: str,
        *,
        url: str | None = None,
        is_active: bool | None = None,
    ) -> dict:
        payload = {key: value for key, value in {"url": url, "is_active": is_active}.items() if value is not None}
        return self._patch(
            f"/organizations/{organization_id}/event-destinations/{destination_id}",
            json=payload,
            auth="bearer",
        )

    def delete(self, organization_id: str, destination_id: str) -> None:
        self._delete(f"/organizations/{organization_id}/event-destinations/{destination_id}", auth="bearer")

    def portal(self, organization_id: str) -> dict:
        return self._get(f"/organizations/{organization_id}/event-destinations/portal", auth="bearer")

    def deliveries(self, organization_id: str, destination_id: str, *, limit: int = 50) -> list[dict]:
        return self._get(
            f"/organizations/{organization_id}/event-destinations/{destination_id}/deliveries",
            params={"limit": limit},
            auth="bearer",
        )

    def delivery_detail(self, organization_id: str, destination_id: str, attempt_id: str) -> dict:
        return self._get(
            f"/organizations/{organization_id}/event-destinations/{destination_id}/deliveries/{attempt_id}",
            auth="bearer",
        )

    def delivery_health(self, organization_id: str, destination_id: str, *, limit: int = 100) -> dict:
        return self._get(
            f"/organizations/{organization_id}/event-destinations/{destination_id}/health",
            params={"limit": limit},
            auth="bearer",
        )

    def redeliver(self, organization_id: str, destination_id: str, attempt_id: str) -> dict:
        return self._post(
            f"/organizations/{organization_id}/event-destinations/{destination_id}/deliveries/{attempt_id}/redeliver",
            auth="bearer",
        )
