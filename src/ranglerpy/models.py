from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


class RanglerObject(dict):
    """Dictionary returned by Rangler that also supports attribute access."""

    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = self.from_value(value)

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    @classmethod
    def from_value(cls, value: Any) -> Any:
        if isinstance(value, RanglerObject):
            return value
        if isinstance(value, dict):
            return cls({key: cls.from_value(item) for key, item in value.items()})
        if isinstance(value, list):
            return [cls.from_value(item) for item in value]
        return value


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_required_datetime(payload: dict[str, Any], key: str) -> datetime:
    raw = payload[key]
    if raw is None:
        raise ValueError(f"{key} is required")
    parsed = _parse_datetime(str(raw))
    assert parsed is not None
    return parsed


def _object_or_none(value: Any) -> RanglerObject | None:
    return RanglerObject.from_value(value) if isinstance(value, dict) else None


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _display_from_payload(payload: dict[str, Any]) -> RanglerObject:
    display = _object_or_none(payload.get("display"))
    if display is not None:
        return display
    return RanglerObject.from_value(
        {
            key: value
            for key, value in {
                "title": payload.get("title"),
                "summary": payload.get("summary"),
                "severity": payload.get("severity"),
            }.items()
            if value is not None
        }
    )


@dataclass(slots=True)
class EventEnvelope:
    id: str
    object: str | None
    api_version: str | None
    type: str
    occurred_at: datetime
    created_at: datetime
    display: RanglerObject
    data: RanglerObject
    entity_kind: str | None
    entity_id: str | None
    title: str
    summary: str
    severity: str
    company_id: str | None
    fund_id: str | None
    source_kind: str | None
    source_id: str | None
    source_url: str | None
    source_published_at: datetime | None

    @property
    def resource(self) -> RanglerObject | None:
        return _object_or_none(self.data.get("object"))

    @property
    def signal(self) -> RanglerObject | None:
        return _object_or_none(self.data.get("signal"))

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EventEnvelope":
        data = RanglerObject.from_value(payload.get("data") or {})
        resource = _object_or_none(data.get("object"))
        display = _display_from_payload(payload)
        resource_company = _object_or_none(resource.get("company")) if resource else None

        resource_kind = _string_or_none(resource.get("object")) if resource else None
        entity_kind = _string_or_none(payload.get("entity_kind")) or resource_kind
        entity_id = _string_or_none(payload.get("entity_id")) or (
            _string_or_none(resource.get("id")) if resource else None
        )
        company_id = (
            _string_or_none(payload.get("company_id"))
            or (_string_or_none(resource.get("company_id")) if resource else None)
            or (_string_or_none(resource_company.get("id")) if resource_company else None)
        )
        fund_id = _string_or_none(payload.get("fund_id"))
        if fund_id is None and resource_kind == "fund" and resource:
            fund_id = _string_or_none(resource.get("id"))
        if fund_id is None and resource:
            fund_id = _string_or_none(resource.get("fund_id"))

        return cls(
            id=str(payload["id"]),
            object=_string_or_none(payload.get("object")),
            api_version=_string_or_none(payload.get("api_version")),
            type=str(payload["type"]),
            occurred_at=_parse_required_datetime(payload, "occurred_at"),
            created_at=_parse_required_datetime(payload, "created_at"),
            display=display,
            data=data,
            entity_kind=entity_kind,
            entity_id=entity_id,
            title=str(display.get("title") or payload.get("title") or ""),
            summary=str(display.get("summary") or payload.get("summary") or display.get("title") or ""),
            severity=str(display.get("severity") or payload.get("severity") or "info"),
            company_id=company_id,
            fund_id=fund_id,
            source_kind=_string_or_none(payload.get("source_kind")),
            source_id=_string_or_none(payload.get("source_id")),
            source_url=_string_or_none(payload.get("source_url"))
            or (_string_or_none(resource.get("url")) if resource else None),
            source_published_at=_parse_datetime(
                _string_or_none(payload.get("source_published_at"))
                or (_string_or_none(resource.get("published_at")) if resource else None)
            ),
        )


@dataclass(slots=True)
class EventsPage:
    data: list[EventEnvelope]
    next_cursor: str | None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EventsPage":
        return cls(
            data=[EventEnvelope.from_dict(item) for item in payload.get("data", [])],
            next_cursor=payload.get("next_cursor"),
        )
