from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from .async_base import AsyncBaseResource


def _drop_none(payload: dict[str, object | None]) -> dict[str, object]:
    return {key: value for key, value in payload.items() if value is not None}


class AsyncSubscriptionsResource(AsyncBaseResource):
    async def list_market(
        self,
        organization_id: str,
        *,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict:
        return await self._get(
            f"/organizations/{organization_id}/market-event-subscriptions",
            params=_drop_none({"cursor": cursor, "limit": limit}),
            auth="bearer",
        )

    async def create_market(
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
        return await self._post(
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

    async def update_market(self, organization_id: str, subscription_id: str, **payload: object) -> dict:
        return await self._patch(
            f"/organizations/{organization_id}/market-event-subscriptions/{subscription_id}",
            json=payload,
            auth="bearer",
        )

    async def delete_market(self, organization_id: str, subscription_id: str) -> None:
        await self._delete(
            f"/organizations/{organization_id}/market-event-subscriptions/{subscription_id}",
            auth="bearer",
        )

    async def list_connect(
        self,
        organization_id: str,
        *,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict:
        return await self._get(
            f"/organizations/{organization_id}/connect-event-subscriptions",
            params=_drop_none({"cursor": cursor, "limit": limit}),
            auth="bearer",
        )

    async def create_connect(
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
        return await self._post(
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

    async def update_connect(self, organization_id: str, subscription_id: str, **payload: object) -> dict:
        return await self._patch(
            f"/organizations/{organization_id}/connect-event-subscriptions/{subscription_id}",
            json=payload,
            auth="bearer",
        )

    async def delete_connect(self, organization_id: str, subscription_id: str) -> None:
        await self._delete(
            f"/organizations/{organization_id}/connect-event-subscriptions/{subscription_id}",
            auth="bearer",
        )

    async def list(self, organization_id: str, **kwargs: Any) -> dict:
        return await self.list_market(organization_id, **kwargs)

    async def create(
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
        return await self.create_market(
            organization_id,
            destination_id=destination_id,
            name=name,
            event_types=event_types,
            company_ids=company_ids,
            fund_ids=fund_ids,
            is_active=is_active,
        )

    async def update(self, organization_id: str, subscription_id: str, **payload: object) -> dict:
        return await self.update_market(organization_id, subscription_id, **payload)

    async def delete(self, organization_id: str, subscription_id: str) -> None:
        await self.delete_market(organization_id, subscription_id)
