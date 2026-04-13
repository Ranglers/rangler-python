from datetime import datetime
import unittest

from ranglerpy.polling import InMemoryCursorStore, PollingConsumer
from ranglerpy.resources.events import EventsResource


class _FakeEventsClient:
    def __init__(self) -> None:
        self.calls = []
        self.responses = [
            {
                "items": [
                    {
                        "id": "evt_3",
                        "type": "filing.new",
                        "occurred_at": "2026-04-12T21:00:00Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_3",
                        "company_id": None,
                        "fund_id": None,
                        "title": "Third",
                        "summary": "Third summary",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                    {
                        "id": "evt_2",
                        "type": "filing.new",
                        "occurred_at": "2026-04-12T20:00:00Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_2",
                        "company_id": None,
                        "fund_id": None,
                        "title": "Second",
                        "summary": "Second summary",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                ],
                "next_cursor": "cursor_2",
            },
            {
                "items": [
                    {
                        "id": "evt_1",
                        "type": "filing.new",
                        "occurred_at": "2026-04-12T19:00:00Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_1",
                        "company_id": None,
                        "fund_id": None,
                        "title": "First",
                        "summary": "First summary",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    }
                ],
                "next_cursor": None,
            },
            {
                "items": [
                    {
                        "id": "evt_4",
                        "type": "filing.new",
                        "occurred_at": "2026-04-12T22:00:00Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_4",
                        "company_id": None,
                        "fund_id": None,
                        "title": "Fourth",
                        "summary": "Fourth summary",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                    {
                        "id": "evt_3",
                        "type": "filing.new",
                        "occurred_at": "2026-04-12T21:00:00Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_3",
                        "company_id": None,
                        "fund_id": None,
                        "title": "Third",
                        "summary": "Third summary",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                ],
                "next_cursor": None,
            },
        ]

    def request(self, method, path, *, auth, params=None, json=None):
        self.calls.append((method, path, auth, params))
        return self.responses.pop(0)


class PollingConsumerTests(unittest.TestCase):
    def test_polling_consumer_returns_oldest_first_and_persists_checkpoint(self) -> None:
        client = _FakeEventsClient()
        resource = EventsResource(client)
        store = InMemoryCursorStore()
        consumer = PollingConsumer(resource, cursor_store=store, stream="filings")

        first_batch = consumer.poll(event_types=["filing.new"], limit=2)

        self.assertEqual([event.id for event in first_batch], ["evt_1", "evt_2", "evt_3"])
        checkpoint = store.load("filings")
        self.assertIsNotNone(checkpoint)
        assert checkpoint is not None
        self.assertEqual(checkpoint.latest_event_ids, {"evt_3"})
        self.assertEqual(
            checkpoint.latest_occurred_at,
            datetime.fromisoformat("2026-04-12T21:00:00+00:00"),
        )

        second_batch = consumer.poll(event_types=["filing.new"], limit=2)

        self.assertEqual([event.id for event in second_batch], ["evt_4"])
        self.assertEqual(client.calls[2][3]["from"], "2026-04-12T21:00:00+00:00")

    def test_polling_consumer_supports_company_scoped_streams(self) -> None:
        client = _FakeEventsClient()
        client.responses = [
            {
                "items": [
                    {
                        "id": "evt_c2",
                        "type": "dividend.declared",
                        "occurred_at": "2026-04-12T22:00:00Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_c2",
                        "company_id": "company_123",
                        "fund_id": None,
                        "title": "Dividend declared",
                        "summary": "Second company event",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                    {
                        "id": "evt_c1",
                        "type": "filing.new",
                        "occurred_at": "2026-04-12T21:00:00Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_c1",
                        "company_id": "company_123",
                        "fund_id": None,
                        "title": "Filing published",
                        "summary": "First company event",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                ],
                "next_cursor": None,
            },
            {
                "items": [
                    {
                        "id": "evt_c3",
                        "type": "board_change.detected",
                        "occurred_at": "2026-04-12T23:00:00Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_c3",
                        "company_id": "company_123",
                        "fund_id": None,
                        "title": "Board changes detected",
                        "summary": "Third company event",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                    {
                        "id": "evt_c2",
                        "type": "dividend.declared",
                        "occurred_at": "2026-04-12T22:00:00Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_c2",
                        "company_id": "company_123",
                        "fund_id": None,
                        "title": "Dividend declared",
                        "summary": "Second company event",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                ],
                "next_cursor": None,
            },
        ]
        resource = EventsResource(client)
        store = InMemoryCursorStore()
        consumer = PollingConsumer(resource, cursor_store=store, stream="issuers")

        first_batch = consumer.poll_company("company_123", limit=50)
        second_batch = consumer.poll_company("company_123", limit=50)

        self.assertEqual([event.id for event in first_batch], ["evt_c1", "evt_c2"])
        self.assertEqual([event.id for event in second_batch], ["evt_c3"])
        self.assertEqual(client.calls[0][1], "/companies/company_123/events")
        self.assertEqual(client.calls[1][3]["from"], "2026-04-12T22:00:00+00:00")

    def test_polling_consumer_supports_fund_scoped_streams(self) -> None:
        client = _FakeEventsClient()
        client.responses = [
            {
                "items": [
                    {
                        "id": "evt_f2",
                        "type": "fund.disclosure.updated",
                        "occurred_at": "2026-04-12T22:00:00Z",
                        "entity_kind": "fund",
                        "entity_id": "fund_123",
                        "company_id": None,
                        "fund_id": "fund_123",
                        "title": "Fund disclosure updated",
                        "summary": "Second fund event",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                    {
                        "id": "evt_f1",
                        "type": "fund.snapshot.updated",
                        "occurred_at": "2026-04-12T21:00:00Z",
                        "entity_kind": "fund",
                        "entity_id": "fund_123",
                        "company_id": None,
                        "fund_id": "fund_123",
                        "title": "Fund snapshot updated",
                        "summary": "First fund event",
                        "severity": "info",
                        "source_url": None,
                        "source_published_at": None,
                        "data": {},
                    },
                ],
                "next_cursor": None,
            }
        ]
        resource = EventsResource(client)
        store = InMemoryCursorStore()
        consumer = PollingConsumer(resource, cursor_store=store, stream="funds")

        batch = consumer.poll_fund("fund_123", limit=50)

        self.assertEqual([event.id for event in batch], ["evt_f1", "evt_f2"])
        self.assertEqual(client.calls[0][1], "/funds/fund_123/events")


if __name__ == "__main__":
    unittest.main()
