from __future__ import annotations

from datetime import datetime
from typing import Iterator, Sequence

from ranglerpy._utils import compact_dict, normalize_datetime
from ranglerpy.models import EventEnvelope, EventsPage

from .base import BaseResource


class EventsResource(BaseResource):
    def list(
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
        payload = self._get(
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

    def list_company(
        self,
        company_id: str,
        *,
        cursor: str | None = None,
        event_types: Sequence[str] | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 25,
    ) -> EventsPage:
        payload = self._get(
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

    def list_fund(
        self,
        fund_id: str,
        *,
        cursor: str | None = None,
        event_types: Sequence[str] | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 25,
    ) -> EventsPage:
        payload = self._get(
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

    def iter_all(
        self,
        *,
        event_types: Sequence[str] | None = None,
        company_id: str | None = None,
        fund_id: str | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 100,
    ) -> Iterator[EventEnvelope]:
        cursor: str | None = None
        while True:
            page = self.list(
                cursor=cursor,
                event_types=event_types,
                company_id=company_id,
                fund_id=fund_id,
                from_=from_,
                to=to,
                limit=limit,
            )
            for item in page.items:
                yield item
            if not page.next_cursor:
                break
            cursor = page.next_cursor
