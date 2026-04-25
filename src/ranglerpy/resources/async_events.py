from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from datetime import datetime

from ranglerpy._utils import compact_dict, normalize_datetime
from ranglerpy.models import EventEnvelope, EventsPage

from .async_base import AsyncBaseResource


class AsyncEventsResource(AsyncBaseResource):
    async def list(
        self,
        *,
        cursor: str | None = None,
        event_types: Sequence[str] | None = None,
        company_id: str | None = None,
        fund_id: str | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 25,
    ) -> EventsPage:
        payload = await self._get(
            "/events",
            params=compact_dict(
                {
                    "cursor": cursor,
                    "type": list(event_types) if event_types else None,
                    "company_id": company_id,
                    "fund_id": fund_id,
                    "from": normalize_datetime(from_),
                    "to": normalize_datetime(to),
                    "limit": limit,
                }
            ),
            auth="api_key",
        )
        return EventsPage.from_dict(payload)

    async def list_company(
        self,
        company_id: str,
        *,
        cursor: str | None = None,
        event_types: Sequence[str] | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 25,
    ) -> EventsPage:
        payload = await self._get(
            f"/companies/{company_id}/events",
            params=compact_dict(
                {
                    "cursor": cursor,
                    "type": list(event_types) if event_types else None,
                    "from": normalize_datetime(from_),
                    "to": normalize_datetime(to),
                    "limit": limit,
                }
            ),
            auth="api_key",
        )
        return EventsPage.from_dict(payload)

    async def list_fund(
        self,
        fund_id: str,
        *,
        cursor: str | None = None,
        event_types: Sequence[str] | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 25,
    ) -> EventsPage:
        payload = await self._get(
            f"/funds/{fund_id}/events",
            params=compact_dict(
                {
                    "cursor": cursor,
                    "type": list(event_types) if event_types else None,
                    "from": normalize_datetime(from_),
                    "to": normalize_datetime(to),
                    "limit": limit,
                }
            ),
            auth="api_key",
        )
        return EventsPage.from_dict(payload)

    async def auto_paging_iter(
        self,
        *,
        event_types: Sequence[str] | None = None,
        company_id: str | None = None,
        fund_id: str | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 100,
    ) -> AsyncIterator[EventEnvelope]:
        cursor: str | None = None
        while True:
            page = await self.list(
                cursor=cursor,
                event_types=event_types,
                company_id=company_id,
                fund_id=fund_id,
                from_=from_,
                to=to,
                limit=limit,
            )
            for item in page.data:
                yield item
            if not page.next_cursor:
                break
            cursor = page.next_cursor
