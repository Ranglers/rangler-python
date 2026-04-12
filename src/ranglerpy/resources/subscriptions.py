from __future__ import annotations

from collections.abc import Sequence

from .base import BaseResource


class SubscriptionsResource(BaseResource):
    def list(self, organization_id: str) -> list[dict]:
        return self._get(f"/organizations/{organization_id}/event-subscriptions", auth="bearer")

    def create(
        self,
        organization_id: str,
        *,
        name: str,
        event_types: Sequence[str],
        company_ids: Sequence[str] | None = None,
        fund_ids: Sequence[str] | None = None,
        is_active: bool = True,
    ) -> dict:
        return self._post(
            f"/organizations/{organization_id}/event-subscriptions",
            json={
                "name": name,
                "event_types": list(event_types),
                "company_ids": list(company_ids or []),
                "fund_ids": list(fund_ids or []),
                "is_active": is_active,
            },
            auth="bearer",
        )

    def update(self, organization_id: str, subscription_id: str, **payload: object) -> dict:
        return self._patch(
            f"/organizations/{organization_id}/event-subscriptions/{subscription_id}",
            json=payload,
            auth="bearer",
        )

    def delete(self, organization_id: str, subscription_id: str) -> None:
        self._delete(f"/organizations/{organization_id}/event-subscriptions/{subscription_id}", auth="bearer")

    def activity(self, organization_id: str, subscription_id: str, *, limit: int = 10) -> dict:
        return self._get(
            f"/organizations/{organization_id}/event-subscriptions/{subscription_id}/activity",
            params={"limit": limit},
            auth="bearer",
        )

    def replay(
        self,
        organization_id: str,
        subscription_id: str,
        event_id: str,
        *,
        webhook_endpoint_id: str,
    ) -> dict:
        return self._post(
            f"/organizations/{organization_id}/event-subscriptions/{subscription_id}/activity/{event_id}/replay",
            json={"webhook_endpoint_id": webhook_endpoint_id},
            auth="bearer",
        )
