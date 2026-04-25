from __future__ import annotations

import os

from ranglerpy import FileCursorStore, PollingConsumer, RanglerClient


def main() -> None:
    company_id = os.environ["RANGLER_COMPANY_ID"]
    client = RanglerClient(
        api_key=os.environ["RANGLER_API_KEY"],
        environment=os.environ.get("RANGLER_ENVIRONMENT", "sandbox"),
    )

    try:
        consumer = PollingConsumer(
            client.v1.events,
            cursor_store=FileCursorStore(".rangler-company.cursor"),
            stream="issuer-monitoring",
        )

        events = consumer.poll_company(
            company_id,
            event_types=["filing.new", "dividend.declared", "board_change.detected"],
            limit=100,
        )
        for event in events:
            print(event.id, event.type, event.title)
    finally:
        client.close()


if __name__ == "__main__":
    main()
