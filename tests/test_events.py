import unittest

from ranglerpy.resources.events import EventsResource


class _FakeEventsClient:
    def __init__(self) -> None:
        self.calls = []

    def request(self, method, path, *, auth, params=None, json=None):
        self.calls.append((method, path, auth, params))
        cursor = (params or {}).get("cursor")
        if cursor is None:
            return {
                "items": [
                    {
                        "id": "evt_1",
                        "type": "filing.new",
                        "occurred_at": "2026-04-12T20:00:00Z",
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
                "next_cursor": "cursor_2",
            }
        return {
            "items": [
                {
                    "id": "evt_2",
                    "type": "filing.new",
                    "occurred_at": "2026-04-12T21:00:00Z",
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
                }
            ],
            "next_cursor": None,
        }


class EventsResourceTests(unittest.TestCase):
    def test_iter_all_follows_next_cursor(self) -> None:
        resource = EventsResource(_FakeEventsClient())

        events = list(resource.iter_all(event_types=["filing.new"], limit=10))

        self.assertEqual([event.id for event in events], ["evt_1", "evt_2"])


if __name__ == "__main__":
    unittest.main()
