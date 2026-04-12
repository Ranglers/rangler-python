import base64
import hmac
import json
import time
from hashlib import sha256
import unittest

from ranglerpy import (
    compute_webhook_signature,
    InMemoryIdempotencyStore,
    parse_and_verify_webhook,
    parse_webhook_event,
    verify_webhook_signature,
)
from ranglerpy.exceptions import DuplicateEventError, InvalidSignatureError


class WebhookHelperTests(unittest.TestCase):
    def test_verify_webhook_signature_matches_expected_digest(self) -> None:
        raw_body = json.dumps(
            {
                "id": "evt_123",
                "type": "filing.new",
                "occurred_at": "2026-04-12T20:00:00Z",
                "entity_kind": "filing",
                "entity_id": "filing_123",
                "company_id": None,
                "fund_id": None,
                "title": "Test filing",
                "summary": "Test summary",
                "severity": "info",
                "source_url": None,
                "source_published_at": None,
                "data": {},
            }
        ).encode("utf-8")
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

    def test_verify_webhook_signature_rejects_stale_timestamp(self) -> None:
        raw_body = b'{"id":"evt_123","type":"filing.new","occurred_at":"2026-04-12T20:00:00Z","entity_kind":"filing","entity_id":"filing_123","company_id":null,"fund_id":null,"title":"Test filing","summary":"Test summary","severity":"info","source_url":null,"source_published_at":null,"data":{}}'
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

    def test_parse_webhook_event_returns_event_envelope(self) -> None:
        raw_body = json.dumps(
            {
                "id": "evt_123",
                "type": "fund.disclosure.updated",
                "occurred_at": "2026-04-12T20:00:00Z",
                "entity_kind": "fund",
                "entity_id": "fund_123",
                "company_id": None,
                "fund_id": "fund_123",
                "title": "Fund disclosure updated",
                "summary": "Latest factsheet posted",
                "severity": "info",
                "source_url": "https://example.com/factsheet.pdf",
                "source_published_at": "2026-04-12T19:45:00Z",
                "data": {"disclosure_kind": "asset_allocation"},
            }
        ).encode("utf-8")

        event = parse_webhook_event(raw_body)
        self.assertEqual(event.type, "fund.disclosure.updated")
        self.assertEqual(event.fund_id, "fund_123")
        self.assertEqual(event.occurred_at.year, 2026)

    def test_parse_and_verify_webhook_raises_for_missing_headers(self) -> None:
        with self.assertRaises(InvalidSignatureError):
            parse_and_verify_webhook(
                headers={"Webhook-Id": "wh_123"},
                raw_body=b"{}",
                secret="plain-test-secret",
            )

    def test_parse_and_verify_webhook_detects_duplicate_event(self) -> None:
        raw_body = json.dumps(
            {
                "id": "evt_123",
                "type": "filing.new",
                "occurred_at": "2026-04-12T20:00:00Z",
                "entity_kind": "filing",
                "entity_id": "filing_123",
                "company_id": None,
                "fund_id": None,
                "title": "Test filing",
                "summary": "Test summary",
                "severity": "info",
                "source_url": None,
                "source_published_at": None,
                "data": {},
            }
        ).encode("utf-8")
        webhook_timestamp = str(int(time.time()))
        signature = compute_webhook_signature(
            raw_body=raw_body,
            secret="plain-test-secret",
            webhook_id="wh_123",
            webhook_timestamp=webhook_timestamp,
        )
        headers = {
            "Webhook-Id": "wh_123",
            "Webhook-Timestamp": webhook_timestamp,
            "Webhook-Signature": signature,
        }
        store = InMemoryIdempotencyStore()

        event = parse_and_verify_webhook(
            headers=headers,
            raw_body=raw_body,
            secret="plain-test-secret",
            idempotency_store=store,
        )
        self.assertEqual(event.id, "evt_123")

        with self.assertRaises(DuplicateEventError):
            parse_and_verify_webhook(
                headers=headers,
                raw_body=raw_body,
                secret="plain-test-secret",
                idempotency_store=store,
            )


if __name__ == "__main__":
    unittest.main()
