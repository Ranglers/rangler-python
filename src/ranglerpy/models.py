from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(slots=True)
class EventEnvelope:
    id: str
    type: str
    occurred_at: datetime
    created_at: datetime
    entity_kind: str
    entity_id: str
    title: str
    summary: str
    severity: str
    company_id: str | None
    fund_id: str | None
    source_kind: str
    source_id: str
    source_url: str | None
    source_published_at: datetime | None
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EventEnvelope":
        return cls(
            id=str(payload["id"]),
            type=str(payload["type"]),
            occurred_at=_parse_datetime(str(payload["occurred_at"])),
            created_at=_parse_datetime(str(payload["created_at"])),
            entity_kind=str(payload["entity_kind"]),
            entity_id=str(payload["entity_id"]),
            title=str(payload["title"]),
            summary=str(payload["summary"]),
            severity=str(payload["severity"]),
            company_id=str(payload["company_id"]) if payload.get("company_id") else None,
            fund_id=str(payload["fund_id"]) if payload.get("fund_id") else None,
            source_kind=str(payload["source_kind"]),
            source_id=str(payload["source_id"]),
            source_url=payload.get("source_url"),
            source_published_at=_parse_datetime(payload.get("source_published_at")),
            data=dict(payload.get("data") or {}),
        )


@dataclass(slots=True)
class EventsPage:
    items: list[EventEnvelope]
    next_cursor: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EventsPage":
        return cls(
            items=[EventEnvelope.from_dict(item) for item in payload.get("items", [])],
            next_cursor=payload.get("next_cursor"),
        )
