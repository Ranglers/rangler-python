from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from .base import BaseResource


def _drop_none(payload: dict[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in payload.items() if value is not None}


class SubscriptionsResource(BaseResource):
    def list_market(
        self,
        organization_id: str,
        *,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict:
        return self._get(
            f"/organizations/{organization_id}/market-event-subscriptions",
            params=_drop_none({"cursor": cursor, "limit": limit}),
            auth="bearer",
        )

    def create_market(
        self,
        organization_id: str,
        *,
        destination_id: str,
        name: str,
        event_types: Sequence[str],
        company_ids: Sequence[str] | None = None,
        fund_ids: Sequence[str] | None = None,
        is_active: bool = True,
    ) -> dict:
        return self._post(
            f"/organizations/{organization_id}/market-event-subscriptions",
            json={
                "destination_id": destination_id,
                "name": name,
                "environment": "live",
                "event_types": list(event_types),
                "company_ids": list(company_ids or []),
                "fund_ids": list(fund_ids or []),
                "is_active": is_active,
            },
            auth="bearer",
        )

    def update_market(self, organization_id: str, subscription_id: str, **payload: object) -> dict:
        return self._patch(
            f"/organizations/{organization_id}/market-event-subscriptions/{subscription_id}",
            json=payload,
            auth="bearer",
        )

    def delete_market(self, organization_id: str, subscription_id: str) -> None:
        self._delete(f"/organizations/{organization_id}/market-event-subscriptions/{subscription_id}", auth="bearer")

    def list_connect(
        self,
        organization_id: str,
        *,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict:
        return self._get(
            f"/organizations/{organization_id}/connect-event-subscriptions",
            params=_drop_none({"cursor": cursor, "limit": limit}),
            auth="bearer",
        )

    def create_connect(
        self,
        organization_id: str,
        *,
        destination_id: str,
        name: str,
        event_types: Sequence[str],
        environment: Literal["live", "test"] = "live",
        connection_ids: Sequence[str] | None = None,
        institution_ids: Sequence[str] | None = None,
        client_user_ids: Sequence[str] | None = None,
        is_active: bool = True,
    ) -> dict:
        return self._post(
            f"/organizations/{organization_id}/connect-event-subscriptions",
            json={
                "destination_id": destination_id,
                "name": name,
                "environment": environment,
                "event_types": list(event_types),
                "connection_ids": list(connection_ids or []),
                "institution_ids": list(institution_ids or []),
                "client_user_ids": list(client_user_ids or []),
                "is_active": is_active,
            },
            auth="bearer",
        )

    def update_connect(self, organization_id: str, subscription_id: str, **payload: object) -> dict:
        return self._patch(
            f"/organizations/{organization_id}/connect-event-subscriptions/{subscription_id}",
            json=payload,
            auth="bearer",
        )

    def delete_connect(self, organization_id: str, subscription_id: str) -> None:
        self._delete(f"/organizations/{organization_id}/connect-event-subscriptions/{subscription_id}", auth="bearer")

    def list(self, organization_id: str, **kwargs: Any) -> dict:
        return self.list_market(organization_id, **kwargs)

    def create(
        self,
        organization_id: str,
        *,
        destination_id: str,
        name: str,
        event_types: Sequence[str],
        company_ids: Sequence[str] | None = None,
        fund_ids: Sequence[str] | None = None,
        is_active: bool = True,
    ) -> dict:
        return self.create_market(
            organization_id,
            destination_id=destination_id,
            name=name,
            event_types=event_types,
            company_ids=company_ids,
            fund_ids=fund_ids,
            is_active=is_active,
        )

    def update(self, organization_id: str, subscription_id: str, **payload: object) -> dict:
        return self.update_market(organization_id, subscription_id, **payload)

    def delete(self, organization_id: str, subscription_id: str) -> None:
        self.delete_market(organization_id, subscription_id)
