import base64
import hmac
import json
import time
from hashlib import sha256
import unittest

from ranglerpy import (
    compute_webhook_signature,
    InMemoryIdempotencyStore,
    verify_webhook_signature,
    Webhook,
)
from ranglerpy.exceptions import DuplicateEventError, InvalidSignatureError


def _webhook_payload(**overrides):
    payload = {
        "id": "evt_123",
        "object": "event",
        "api_version": "v1",
        "type": "filing.new",
        "occurred_at": "2026-04-12T20:00:00Z",
        "created_at": "2026-04-12T20:00:01Z",
        "display": {
            "title": "Test filing",
            "summary": "Test summary",
            "severity": "info",
        },
        "data": {
            "object": {
                "id": "filing_123",
                "object": "filing",
                "url": "https://example.com/filing.pdf",
                "title": "Test filing.pdf",
                "company_id": "company_123",
                "published_at": "2026-04-12T19:45:00Z",
            }
        },
    }
    payload.update(overrides)
    return payload


def _signed_headers(
    raw_body: bytes,
    *,
    secret: str = "plain-test-secret",
    webhook_id: str = "wh_123",
    timestamp: str | None = None,
) -> dict[str, str]:
    webhook_timestamp = timestamp or str(int(time.time()))
    return {
        "Webhook-Id": webhook_id,
        "Webhook-Timestamp": webhook_timestamp,
        "Webhook-Signature": compute_webhook_signature(
            raw_body=raw_body,
            secret=secret,
            webhook_id=webhook_id,
            webhook_timestamp=webhook_timestamp,
        ),
    }


def _raw_signature(signature: str) -> str:
    return signature.split(",", 1)[1]


class WebhookHelperTests(unittest.TestCase):
    def test_verify_webhook_signature_matches_expected_digest(self) -> None:
        raw_body = json.dumps(_webhook_payload()).encode("utf-8")
        secret = "plain-test-secret"
        webhook_id = "wh_123"
        webhook_timestamp = "1712952000"
        signed_payload = b".".join(
            [webhook_id.encode("utf-8"), webhook_timestamp.encode("utf-8"), raw_body]
        )
        signature = "v1," + base64.b64encode(
            hmac.new(secret.encode("utf-8"), signed_payload, sha256).digest()
        ).decode("utf-8")

        self.assertTrue(
            verify_webhook_signature(
                raw_body=raw_body,
                secret=secret,
                webhook_id=webhook_id,
                webhook_timestamp=webhook_timestamp,
                signature=signature,
                max_age_seconds=None,
            )
        )

    def test_verify_webhook_signature_accepts_raw_and_sha256_signature_values(self) -> None:
        raw_body = json.dumps(_webhook_payload()).encode("utf-8")
        secret = "plain-test-secret"
        webhook_id = "wh_123"
        webhook_timestamp = "1712952000"
        raw_signature = _raw_signature(
            compute_webhook_signature(
                raw_body=raw_body,
                secret=secret,
                webhook_id=webhook_id,
                webhook_timestamp=webhook_timestamp,
            )
        )

        for signature in (raw_signature, f"sha256={raw_signature}", f"v1={raw_signature}"):
            self.assertTrue(
                verify_webhook_signature(
                    raw_body=raw_body,
                    secret=secret,
                    webhook_id=webhook_id,
                    webhook_timestamp=webhook_timestamp,
                    signature=signature,
                    max_age_seconds=None,
                )
            )

    def test_verify_webhook_signature_rejects_stale_timestamp(self) -> None:
        raw_body = json.dumps(_webhook_payload()).encode("utf-8")
        secret = "plain-test-secret"
        webhook_id = "wh_123"
        webhook_timestamp = str(int(time.time()) - 3600)
        signature = compute_webhook_signature(
            raw_body=raw_body,
            secret=secret,
            webhook_id=webhook_id,
            webhook_timestamp=webhook_timestamp,
        )

        self.assertFalse(
            verify_webhook_signature(
                raw_body=raw_body,
                secret=secret,
                webhook_id=webhook_id,
                webhook_timestamp=webhook_timestamp,
                signature=signature,
            )
        )

    def test_construct_event_returns_event_envelope(self) -> None:
        raw_body = json.dumps(
            _webhook_payload(
                type="fund.disclosure.updated",
                display={
                    "title": "Fund disclosure updated",
                    "summary": "Latest factsheet posted",
                    "severity": "info",
                },
                data={
                    "object": {
                        "id": "fund_123",
                        "object": "fund",
                        "name": "Rangler Balanced Fund",
                    },
                    "disclosure_kind": "asset_allocation",
                },
            )
        ).encode("utf-8")

        event = Webhook.construct_event(
            headers=_signed_headers(raw_body),
            raw_body=raw_body,
            secret="plain-test-secret",
        )
        self.assertEqual(event.object, "event")
        self.assertEqual(event.api_version, "v1")
        self.assertEqual(event.type, "fund.disclosure.updated")
        self.assertEqual(event.fund_id, "fund_123")
        self.assertEqual(event.entity_kind, "fund")
        self.assertEqual(event.entity_id, "fund_123")
        self.assertEqual(event.title, "Fund disclosure updated")
        self.assertEqual(event.summary, "Latest factsheet posted")
        self.assertEqual(event.resource, {"id": "fund_123", "object": "fund", "name": "Rangler Balanced Fund"})
        self.assertEqual(event.created_at.year, 2026)
        self.assertIsNone(event.source_kind)
        self.assertIsNone(event.source_id)
        self.assertEqual(event.occurred_at.year, 2026)

    def test_construct_event_rejects_flat_read_api_payload(self) -> None:
        raw_body = json.dumps(
            {
                "id": "evt_flat",
                "type": "filing.new",
                "occurred_at": "2026-04-12T20:00:00Z",
                "created_at": "2026-04-12T20:00:01Z",
                "entity_kind": "filing",
                "entity_id": "filing_123",
                "company_id": "company_123",
                "fund_id": None,
                "source_kind": "filing",
                "source_id": "filing_123",
                "title": "Flat API filing",
                "summary": "Flat API summary",
                "severity": "info",
                "source_url": None,
                "source_published_at": None,
                "data": {},
            }
        ).encode("utf-8")

        with self.assertRaisesRegex(ValueError, "webhook payload must be an event envelope"):
            Webhook.construct_event(
                headers=_signed_headers(raw_body),
                raw_body=raw_body,
                secret="plain-test-secret",
            )

    def test_construct_event_raises_for_missing_headers(self) -> None:
        with self.assertRaises(InvalidSignatureError):
            Webhook.construct_event(
                headers={"Webhook-Id": "wh_123"},
                raw_body=b"{}",
                secret="plain-test-secret",
            )

    def test_construct_event_detects_duplicate_event(self) -> None:
        raw_body = json.dumps(_webhook_payload()).encode("utf-8")
        headers = _signed_headers(raw_body)
        store = InMemoryIdempotencyStore()

        event = Webhook.construct_event(
            headers=headers,
            raw_body=raw_body,
            secret="plain-test-secret",
            idempotency_store=store,
        )
        self.assertEqual(event.id, "evt_123")

        with self.assertRaises(DuplicateEventError):
            Webhook.construct_event(
                headers=headers,
                raw_body=raw_body,
                secret="plain-test-secret",
                idempotency_store=store,
            )

    def test_webhook_construct_event_wraps_signature_verification(self) -> None:
        raw_body = json.dumps(_webhook_payload()).encode("utf-8")

        event = Webhook.construct_event(
            headers=_signed_headers(raw_body),
            raw_body=raw_body,
            secret="plain-test-secret",
        )

        self.assertEqual(event.id, "evt_123")
        self.assertEqual(event.resource.id, "filing_123")

    def test_construct_event_accepts_rangler_header_aliases(self) -> None:
        raw_body = json.dumps(_webhook_payload()).encode("utf-8")
        headers = _signed_headers(raw_body, webhook_id="evt_delivery_123")
        event = Webhook.construct_event(
            headers={
                "X-Rangler-Id": "evt_delivery_123",
                "X-Rangler-Timestamp": headers["Webhook-Timestamp"],
                "X-Rangler-Signature": _raw_signature(headers["Webhook-Signature"]),
            },
            raw_body=raw_body,
            secret="plain-test-secret",
        )

        self.assertEqual(event.id, "evt_123")
        self.assertEqual(event.type, "filing.new")

    def test_construct_event_accepts_connect_event_envelope(self) -> None:
        raw_body = json.dumps(
            _webhook_payload(
                id="evt_connect_123",
                api_version="connect.event.v1",
                type="connect.sync.completed",
                entity_kind="connect_connection",
                entity_id="conn_123",
                company_id=None,
                display={
                    "title": "Connect sync completed",
                    "summary": "Sandbox Brokerage synced successfully",
                    "severity": "info",
                },
                data={
                    "object": {
                        "id": "conn_123",
                        "object": "connect_connection",
                        "institution_id": "sandbox_brokerage",
                        "client_user_id": "customer_123",
                    },
                    "sync_run_id": "sync_123",
                    "environment": "test",
                },
            )
        ).encode("utf-8")

        event = Webhook.construct_event(
            headers=_signed_headers(raw_body),
            raw_body=raw_body,
            secret="plain-test-secret",
        )

        self.assertEqual(event.api_version, "connect.event.v1")
        self.assertEqual(event.type, "connect.sync.completed")
        self.assertEqual(event.entity_kind, "connect_connection")
        self.assertEqual(event.entity_id, "conn_123")
        self.assertEqual(event.resource.object, "connect_connection")
        self.assertEqual(event.resource.client_user_id, "customer_123")


if __name__ == "__main__":
    unittest.main()
