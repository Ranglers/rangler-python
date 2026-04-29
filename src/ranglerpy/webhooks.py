from __future__ import annotations

import base64
import hmac
import json
from hashlib import sha256
import time
from typing import Literal, Mapping

from .exceptions import DuplicateEventError, InvalidSignatureError
from .idempotency import IdempotencyStore
from .models import EventEnvelope

WEBHOOK_ID_HEADERS = ("webhook-id", "x-rangler-id", "x-rangler-event-id", "x-rangler-idempotency")
WEBHOOK_TIMESTAMP_HEADERS = ("webhook-timestamp", "x-rangler-timestamp", "x-webhook-timestamp")
WEBHOOK_SIGNATURE_HEADERS = (
    "webhook-signature",
    "x-rangler-signature",
    "x-rangler-webhook-signature",
    "x-webhook-signature",
)


def decode_webhook_secret(secret: str) -> bytes:
    if not secret.startswith("whsec_"):
        return secret.encode("utf-8")
    encoded = secret[len("whsec_") :]
    padded = encoded + ("=" * ((4 - len(encoded) % 4) % 4))
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def compute_webhook_signature(
    *,
    raw_body: bytes,
    secret: str,
    webhook_id: str,
    webhook_timestamp: str,
) -> str:
    signed_payload = b".".join(
        [
            webhook_id.encode("utf-8"),
            webhook_timestamp.encode("utf-8"),
            raw_body,
        ]
    )
    digest = hmac.new(decode_webhook_secret(secret), signed_payload, sha256).digest()
    return f"v1,{base64.b64encode(digest).decode('utf-8')}"


def _header(headers: Mapping[str, str], *names: str) -> str | None:
    normalized = {key.lower(): value for key, value in headers.items()}
    for name in names:
        value = normalized.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _signature_values(value: str) -> list[str]:
    values: list[str] = []
    for part in value.replace(";", " ").split():
        candidate = part.strip()
        if not candidate:
            continue
        if "," in candidate:
            version, signature = candidate.split(",", 1)
            if version.strip() == "v1" and signature.strip():
                values.append(signature.strip())
            continue
        if "=" in candidate:
            algorithm, signature = candidate.split("=", 1)
            if algorithm.strip().lower() in {"sha256", "v1"} and signature.strip():
                values.append(signature.strip())
                continue
        values.append(candidate)
    return values


def verify_webhook_signature(
    *,
    raw_body: bytes,
    secret: str,
    webhook_id: str,
    webhook_timestamp: str,
    signature: str,
    max_age_seconds: int | None = 300,
) -> bool:
    if max_age_seconds is not None:
        try:
            timestamp = int(webhook_timestamp)
        except (TypeError, ValueError):
            return False
        if abs(time.time() - timestamp) > max_age_seconds:
            return False
    expected = compute_webhook_signature(
        raw_body=raw_body,
        secret=secret,
        webhook_id=webhook_id,
        webhook_timestamp=webhook_timestamp,
    )
    expected_value = expected.split(",", 1)[1]
    for candidate in _signature_values(signature):
        if hmac.compare_digest(expected, candidate) or hmac.compare_digest(expected_value, candidate):
            return True
    return False


def extract_webhook_headers(headers: Mapping[str, str]) -> tuple[str, str, str]:
    webhook_id = _header(headers, *WEBHOOK_ID_HEADERS)
    webhook_timestamp = _header(headers, *WEBHOOK_TIMESTAMP_HEADERS)
    signature = _header(headers, *WEBHOOK_SIGNATURE_HEADERS)
    if webhook_id is None:
        raise InvalidSignatureError("Missing required webhook header: webhook-id")
    if webhook_timestamp is None:
        raise InvalidSignatureError("Missing required webhook header: webhook-timestamp")
    if signature is None:
        raise InvalidSignatureError("Missing required webhook header: webhook-signature")
    return webhook_id, webhook_timestamp, signature


def _parse_webhook_event(raw_body: bytes) -> EventEnvelope:
    payload = json.loads(raw_body.decode("utf-8"))
    if payload.get("object") != "event" or not isinstance(payload.get("display"), dict):
        raise ValueError("Rangler webhook payload must be an event envelope")
    data = payload.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("object"), dict):
        raise ValueError("Rangler webhook payload must include data.object")
    return EventEnvelope.from_dict(payload)


def _parse_and_verify_webhook(
    *,
    headers: Mapping[str, str],
    raw_body: bytes,
    secret: str,
    max_age_seconds: int | None = 300,
    idempotency_store: IdempotencyStore | None = None,
    idempotency_key: Literal["event_id", "webhook_id"] = "event_id",
) -> EventEnvelope:
    webhook_id, webhook_timestamp, signature = extract_webhook_headers(headers)
    is_valid = verify_webhook_signature(
        raw_body=raw_body,
        secret=secret,
        webhook_id=webhook_id,
        webhook_timestamp=webhook_timestamp,
        signature=signature,
        max_age_seconds=max_age_seconds,
    )
    if not is_valid:
        raise InvalidSignatureError("Rangler webhook signature verification failed")
    event = _parse_webhook_event(raw_body)
    if idempotency_store is not None:
        key = event.id if idempotency_key == "event_id" else webhook_id
        if not idempotency_store.claim(key):
            raise DuplicateEventError(f"Rangler webhook already processed for key: {key}")
    return event


class Webhook:
    @staticmethod
    def construct_event(
        *,
        raw_body: bytes,
        headers: Mapping[str, str],
        secret: str,
        max_age_seconds: int | None = 300,
        idempotency_store: IdempotencyStore | None = None,
        idempotency_key: Literal["event_id", "webhook_id"] = "event_id",
    ) -> EventEnvelope:
        return _parse_and_verify_webhook(
            headers=headers,
            raw_body=raw_body,
            secret=secret,
            max_age_seconds=max_age_seconds,
            idempotency_store=idempotency_store,
            idempotency_key=idempotency_key,
        )
