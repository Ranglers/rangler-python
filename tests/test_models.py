import unittest

from ranglerpy.models import EventsPage, RanglerObject


class ModelsTests(unittest.TestCase):
    def test_events_page_reads_webhook_style_data(self) -> None:
        page = EventsPage.from_dict(
            {
                "data": [
                    {
                        "id": "evt_123",
                        "object": "event",
                        "api_version": "v1",
                        "type": "filing.new",
                        "occurred_at": "2026-04-12T20:00:00Z",
                        "created_at": "2026-04-12T20:00:01Z",
                        "display": {"title": "Filing published", "severity": "info"},
                        "data": {
                            "object": {
                                "id": "filing_123",
                                "object": "filing",
                                "company_id": "company_123",
                            }
                        },
                    }
                ],
                "next_cursor": None,
            }
        )

        self.assertEqual(len(page.data), 1)
        self.assertEqual(page.data[0].resource["id"], "filing_123")
        self.assertEqual(page.data[0].data.object.id, "filing_123")
        self.assertEqual(page.data[0].summary, "Filing published")

    def test_rangler_object_attribute_writes_update_dict(self) -> None:
        payload = RanglerObject()
        payload.company = {"id": "company_123"}

        self.assertEqual(payload["company"]["id"], "company_123")
        self.assertEqual(payload.company.id, "company_123")

        del payload.company
        self.assertNotIn("company", payload)

    def test_required_datetime_rejects_null_values_cleanly(self) -> None:
        with self.assertRaisesRegex(ValueError, "occurred_at is required"):
            EventsPage.from_dict(
                {
                    "data": [
                        {
                            "id": "evt_123",
                            "object": "event",
                            "api_version": "v1",
                            "type": "filing.new",
                            "occurred_at": None,
                            "created_at": "2026-04-12T20:00:01Z",
                            "display": {"title": "Filing published", "severity": "info"},
                            "data": {
                                "object": {
                                    "id": "filing_123",
                                    "object": "filing",
                                }
                            },
                        }
                    ],
                    "next_cursor": None,
                }
            )

    def test_events_page_reads_current_flat_api_event_rows(self) -> None:
        page = EventsPage.from_dict(
            {
                "data": [
                    {
                        "id": "evt_flat",
                        "type": "filing.new",
                        "occurred_at": "2026-04-12T20:00:00Z",
                        "created_at": "2026-04-12T20:00:01Z",
                        "entity_kind": "filing",
                        "entity_id": "filing_123",
                        "source_kind": "filing",
                        "source_id": "filing_123",
                        "title": "Flat API filing",
                        "summary": "Flat API summary",
                        "severity": "info",
                        "data": {},
                    }
                ],
                "next_cursor": "next",
            }
        )

        self.assertEqual(page.next_cursor, "next")
        self.assertEqual(page.data[0].title, "Flat API filing")
        self.assertEqual(page.data[0].source_kind, "filing")


if __name__ == "__main__":
    unittest.main()
