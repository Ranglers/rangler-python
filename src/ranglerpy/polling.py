from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Iterable

from .models import EventEnvelope


def _coerce_datetime(value: datetime | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(slots=True)
class PollingCheckpoint:
    latest_occurred_at: datetime
    latest_event_ids: set[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "latest_occurred_at": self.latest_occurred_at.isoformat(),
            "latest_event_ids": sorted(self.latest_event_ids),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PollingCheckpoint":
        return cls(
            latest_occurred_at=_coerce_datetime(payload["latest_occurred_at"]),
            latest_event_ids=set(payload.get("latest_event_ids", [])),
        )


class CursorStore(ABC):
    @abstractmethod
    def load(self, stream: str) -> PollingCheckpoint | None:
        """Load the saved checkpoint for a named stream."""

    @abstractmethod
    def save(self, stream: str, checkpoint: PollingCheckpoint) -> None:
        """Persist the checkpoint for a named stream."""


class InMemoryCursorStore(CursorStore):
    def __init__(self) -> None:
        self._data: dict[str, PollingCheckpoint] = {}

    def load(self, stream: str) -> PollingCheckpoint | None:
        return self._data.get(stream)

    def save(self, stream: str, checkpoint: PollingCheckpoint) -> None:
        self._data[stream] = checkpoint


class FileCursorStore(CursorStore):
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self, stream: str) -> PollingCheckpoint | None:
        payload = self._read()
        record = payload.get(stream)
        if not isinstance(record, dict):
            return None
        return PollingCheckpoint.from_dict(record)

    def save(self, stream: str, checkpoint: PollingCheckpoint) -> None:
        payload = self._read()
        payload[stream] = checkpoint.to_dict()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text())
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}


def _build_checkpoint(events: Iterable[EventEnvelope]) -> PollingCheckpoint | None:
    latest_occurred_at: datetime | None = None
    latest_event_ids: set[str] = set()
    for event in events:
        if latest_occurred_at is None or event.occurred_at > latest_occurred_at:
            latest_occurred_at = event.occurred_at
            latest_event_ids = {event.id}
        elif event.occurred_at == latest_occurred_at:
            latest_event_ids.add(event.id)
    if latest_occurred_at is None:
        return None
    return PollingCheckpoint(
        latest_occurred_at=latest_occurred_at,
        latest_event_ids=latest_event_ids,
    )


class PollingConsumer:
    def __init__(self, events_resource: Any, *, cursor_store: CursorStore, stream: str = "events") -> None:
        self.events_resource = events_resource
        self.cursor_store = cursor_store
        self.stream = stream

    def poll(
        self,
        *,
        event_types: list[str] | None = None,
        company_id: str | None = None,
        fund_id: str | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 100,
    ) -> list[EventEnvelope]:
        checkpoint = self.cursor_store.load(self.stream)
        explicit_from = _coerce_datetime(from_)
        effective_from = explicit_from
        if checkpoint is not None and (
            explicit_from is None or checkpoint.latest_occurred_at > explicit_from
        ):
            effective_from = checkpoint.latest_occurred_at

        cursor: str | None = None
        fetched: list[EventEnvelope] = []
        while True:
            page = self.events_resource.list(
                cursor=cursor,
                event_types=event_types,
                company_id=company_id,
                fund_id=fund_id,
                from_=effective_from,
                to=to,
                limit=limit,
            )
            if not page.data:
                break
            fetched.extend(page.data)
            if not page.next_cursor:
                break
            cursor = page.next_cursor

        filtered = self._filter_seen(fetched, checkpoint)
        next_checkpoint = _build_checkpoint(fetched)
        if next_checkpoint is not None:
            self.cursor_store.save(self.stream, next_checkpoint)
        return list(reversed(filtered))

    def poll_company(
        self,
        company_id: str,
        *,
        event_types: list[str] | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 100,
    ) -> list[EventEnvelope]:
        return self._poll_scoped(
            scope_key=f"company:{company_id}",
            fetch_page=lambda cursor, effective_from: self.events_resource.list_company(
                company_id,
                cursor=cursor,
                event_types=event_types,
                from_=effective_from,
                to=to,
                limit=limit,
            ),
            from_=from_,
        )

    def poll_fund(
        self,
        fund_id: str,
        *,
        event_types: list[str] | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 100,
    ) -> list[EventEnvelope]:
        return self._poll_scoped(
            scope_key=f"fund:{fund_id}",
            fetch_page=lambda cursor, effective_from: self.events_resource.list_fund(
                fund_id,
                cursor=cursor,
                event_types=event_types,
                from_=effective_from,
                to=to,
                limit=limit,
            ),
            from_=from_,
        )

    @staticmethod
    def _filter_seen(
        events: list[EventEnvelope],
        checkpoint: PollingCheckpoint | None,
    ) -> list[EventEnvelope]:
        if checkpoint is None:
            return events
        filtered: list[EventEnvelope] = []
        for event in events:
            if (
                event.occurred_at == checkpoint.latest_occurred_at
                and event.id in checkpoint.latest_event_ids
            ):
                continue
            filtered.append(event)
        return filtered

    def _poll_scoped(
        self,
        *,
        scope_key: str,
        fetch_page: Any,
        from_: datetime | str | None,
    ) -> list[EventEnvelope]:
        stream = f"{self.stream}:{scope_key}"
        checkpoint = self.cursor_store.load(stream)
        explicit_from = _coerce_datetime(from_)
        effective_from = explicit_from
        if checkpoint is not None and (
            explicit_from is None or checkpoint.latest_occurred_at > explicit_from
        ):
            effective_from = checkpoint.latest_occurred_at

        cursor: str | None = None
        fetched: list[EventEnvelope] = []
        while True:
            page = fetch_page(cursor, effective_from)
            if not page.data:
                break
            fetched.extend(page.data)
            if not page.next_cursor:
                break
            cursor = page.next_cursor

        filtered = self._filter_seen(fetched, checkpoint)
        next_checkpoint = _build_checkpoint(fetched)
        if next_checkpoint is not None:
            self.cursor_store.save(stream, next_checkpoint)
        return list(reversed(filtered))


class AsyncPollingConsumer:
    def __init__(self, events_resource: Any, *, cursor_store: CursorStore, stream: str = "events") -> None:
        self.events_resource = events_resource
        self.cursor_store = cursor_store
        self.stream = stream

    async def poll(
        self,
        *,
        event_types: list[str] | None = None,
        company_id: str | None = None,
        fund_id: str | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 100,
    ) -> list[EventEnvelope]:
        checkpoint = self.cursor_store.load(self.stream)
        explicit_from = _coerce_datetime(from_)
        effective_from = explicit_from
        if checkpoint is not None and (
            explicit_from is None or checkpoint.latest_occurred_at > explicit_from
        ):
            effective_from = checkpoint.latest_occurred_at

        cursor: str | None = None
        fetched: list[EventEnvelope] = []
        while True:
            page = await self.events_resource.list(
                cursor=cursor,
                event_types=event_types,
                company_id=company_id,
                fund_id=fund_id,
                from_=effective_from,
                to=to,
                limit=limit,
            )
            if not page.data:
                break
            fetched.extend(page.data)
            if not page.next_cursor:
                break
            cursor = page.next_cursor

        filtered = PollingConsumer._filter_seen(fetched, checkpoint)
        next_checkpoint = _build_checkpoint(fetched)
        if next_checkpoint is not None:
            self.cursor_store.save(self.stream, next_checkpoint)
        return list(reversed(filtered))

    async def poll_company(
        self,
        company_id: str,
        *,
        event_types: list[str] | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 100,
    ) -> list[EventEnvelope]:
        return await self._poll_scoped(
            scope_key=f"company:{company_id}",
            fetch_page=lambda cursor, effective_from: self.events_resource.list_company(
                company_id,
                cursor=cursor,
                event_types=event_types,
                from_=effective_from,
                to=to,
                limit=limit,
            ),
            from_=from_,
        )

    async def poll_fund(
        self,
        fund_id: str,
        *,
        event_types: list[str] | None = None,
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
        limit: int = 100,
    ) -> list[EventEnvelope]:
        return await self._poll_scoped(
            scope_key=f"fund:{fund_id}",
            fetch_page=lambda cursor, effective_from: self.events_resource.list_fund(
                fund_id,
                cursor=cursor,
                event_types=event_types,
                from_=effective_from,
                to=to,
                limit=limit,
            ),
            from_=from_,
        )

    async def _poll_scoped(
        self,
        *,
        scope_key: str,
        fetch_page: Any,
        from_: datetime | str | None,
    ) -> list[EventEnvelope]:
        stream = f"{self.stream}:{scope_key}"
        checkpoint = self.cursor_store.load(stream)
        explicit_from = _coerce_datetime(from_)
        effective_from = explicit_from
        if checkpoint is not None and (
            explicit_from is None or checkpoint.latest_occurred_at > explicit_from
        ):
            effective_from = checkpoint.latest_occurred_at

        cursor: str | None = None
        fetched: list[EventEnvelope] = []
        while True:
            page = await fetch_page(cursor, effective_from)
            if not page.data:
                break
            fetched.extend(page.data)
            if not page.next_cursor:
                break
            cursor = page.next_cursor

        filtered = PollingConsumer._filter_seen(fetched, checkpoint)
        next_checkpoint = _build_checkpoint(fetched)
        if next_checkpoint is not None:
            self.cursor_store.save(stream, next_checkpoint)
        return list(reversed(filtered))
