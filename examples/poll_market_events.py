from __future__ import annotations

import os

from ranglerpy import FileCursorStore, PollingConsumer, RanglerClient


def main() -> None:
    client = RanglerClient(
        api_key=os.environ["RANGLER_API_KEY"],
        environment=os.environ.get("RANGLER_ENVIRONMENT", "sandbox"),
    )

    try:
        consumer = PollingConsumer(
            client.v1.events,
            cursor_store=FileCursorStore(".rangler-market.cursor"),
            stream="market-wide-events",
        )

        events = consumer.poll(
            event_types=["filing.new", "dividend.declared", "board_change.detected"],
            limit=100,
        )
        for event in events:
            print(event.id, event.type, event.company_id, event.occurred_at.isoformat())
    finally:
        client.close()


if __name__ == "__main__":
    main()
