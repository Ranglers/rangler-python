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
    return hmac.compare_digest(expected, signature)


def extract_webhook_headers(headers: Mapping[str, str]) -> tuple[str, str, str]:
    normalized = {key.lower(): value for key, value in headers.items()}
    try:
        return (
            normalized["webhook-id"],
            normalized["webhook-timestamp"],
            normalized["webhook-signature"],
        )
    except KeyError as exc:
        raise InvalidSignatureError(f"Missing required webhook header: {exc.args[0]}") from exc


def parse_webhook_event(raw_body: bytes) -> EventEnvelope:
    payload = json.loads(raw_body.decode("utf-8"))
    return EventEnvelope.from_dict(payload)


def parse_and_verify_webhook(
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
        raise InvalidSignatureError("Atlas webhook signature verification failed")
    event = parse_webhook_event(raw_body)
    if idempotency_store is not None:
        key = event.id if idempotency_key == "event_id" else webhook_id
        if not idempotency_store.claim(key):
            raise DuplicateEventError(f"Atlas webhook already processed for key: {key}")
    return event
