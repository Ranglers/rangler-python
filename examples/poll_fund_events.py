from __future__ import annotations

import os

from ranglerpy import FileCursorStore, PollingConsumer, RanglerClient


def main() -> None:
    fund_id = os.environ["RANGLER_FUND_ID"]
    client = RanglerClient(
        api_key=os.environ["RANGLER_API_KEY"],
        environment=os.environ.get("RANGLER_ENVIRONMENT", "sandbox"),
    )

    try:
        consumer = PollingConsumer(
            client.events,
            cursor_store=FileCursorStore(".atlas-fund.cursor"),
            stream="fund-monitoring",
        )

        events = consumer.poll_fund(
            fund_id,
            event_types=["fund.snapshot.updated", "fund.disclosure.updated"],
            limit=100,
        )
        for event in events:
            print(event.id, event.type, event.fund_id, event.occurred_at.isoformat())
    finally:
        client.close()


if __name__ == "__main__":
    main()
