# ranglerpy

`ranglerpy` is a Python SDK for the Atlas API.

It is designed around the actual Atlas product shape:

- polling-first event consumption
- optional webhook verification helpers
- thin wrappers for the developer control plane

The goal is to make Atlas easy to integrate whether you want to:

- poll event feeds with a cursor
- consume companies and filings directly
- manage webhook endpoints and event subscriptions
- verify Atlas webhook signatures in a receiver

It is designed to give you one integration surface across:

- polling feeds
- webhook delivery
- developer control-plane operations

## Installation

```bash
pip install ranglerpy
```

For local development:

```bash
pip install -e .[dev]
```

## Quick start

### Data plane: polling events

```python
from ranglerpy import InMemoryCursorStore, PollingConsumer, RanglerClient

client = RanglerClient(
    api_key="atl_test_your_api_key",
    environment="sandbox",
)

consumer = PollingConsumer(
    client.events,
    cursor_store=InMemoryCursorStore(),
    stream="market-wide-filings",
)

for event in consumer.poll(event_types=["filing.new"], limit=100):
    print(event.id, event.type, event.occurred_at.isoformat())
```

### Async polling

```python
from ranglerpy import AsyncPollingConsumer, AsyncRanglerClient, FileCursorStore

async with AsyncRanglerClient(
    api_key="atl_test_your_api_key",
    environment="sandbox",
) as client:
    consumer = AsyncPollingConsumer(
        client.events,
        cursor_store=FileCursorStore(".atlas-cursors.json"),
        stream="issuer-monitoring",
    )

    for event in await consumer.poll(
        limit=100,
        event_types=["filing.new"],
    ):
        print(event.id, event.type)
```

### Control plane: manage webhooks

```python
from ranglerpy import RanglerClient

client = RanglerClient(
    bearer_token="your_portal_bearer_token",
    environment="live",
)

organization = client.organizations.create(
    name="Atlas Demo Org",
    billing_email="billing@example.com",
)

webhook = client.webhooks.create(
    organization["id"],
    url="https://example.com/atlas/webhooks",
)

print(webhook["signing_secret"])
```

### Webhook verification

```python
from ranglerpy import InMemoryIdempotencyStore, parse_and_verify_webhook

idempotency_store = InMemoryIdempotencyStore()

event = parse_and_verify_webhook(
    headers=headers,
    raw_body=raw_body,
    secret=webhook_secret,
    idempotency_store=idempotency_store,
)

print(event.type, event.title)
```

### FastAPI webhook handler

```python
from fastapi import FastAPI, HTTPException, Request

from ranglerpy import DuplicateEventError, InMemoryIdempotencyStore, InvalidSignatureError, parse_and_verify_webhook

app = FastAPI()
store = InMemoryIdempotencyStore()


@app.post("/atlas/webhooks")
async def atlas_webhook(request: Request):
    raw_body = await request.body()

    try:
        event = parse_and_verify_webhook(
            headers=request.headers,
            raw_body=raw_body,
            secret="whsec_your_secret",
            idempotency_store=store,
        )
    except InvalidSignatureError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DuplicateEventError:
        return {"duplicate": True}

    return {"received": event.id}
```

### Flask webhook handler

```python
from flask import Flask, jsonify, request

from ranglerpy import DuplicateEventError, InMemoryIdempotencyStore, InvalidSignatureError, parse_and_verify_webhook

app = Flask(__name__)
store = InMemoryIdempotencyStore()


@app.post("/atlas/webhooks")
def atlas_webhook():
    raw_body = request.get_data()

    try:
        event = parse_and_verify_webhook(
            headers=request.headers,
            raw_body=raw_body,
            secret="whsec_your_secret",
            idempotency_store=store,
        )
    except InvalidSignatureError as exc:
        return jsonify({"error": str(exc)}), 400
    except DuplicateEventError:
        return jsonify({"duplicate": True}), 200

    return jsonify({"received": event.id})
```

## Authentication modes

Atlas has two auth modes:

- data plane uses `X-API-Key`
- developer control plane uses `Authorization: Bearer ...`

`ranglerpy` supports both on the same client. Resource methods choose the correct auth mode internally.

## Current SDK scope

### Data plane

- companies
- filings
- funds
- event feeds

### Control plane

- organizations
- API keys
- usage and billing status
- webhook endpoints
- webhook deliveries
- event subscriptions

### Helpers

- cursor-based event iteration
- polling consumer with checkpoint persistence
- Atlas webhook signature verification
- webhook payload parsing
- parse-and-verify helper for webhook receivers
- in-memory idempotency helper for duplicate webhook handling
- async client support

## Example scripts

The repo includes runnable examples in [`examples/`](./examples):

- [`poll_market_events.py`](./examples/poll_market_events.py) for market-wide event polling
- [`poll_company_events.py`](./examples/poll_company_events.py) for issuer-scoped polling
- [`poll_fund_events.py`](./examples/poll_fund_events.py) for fund-scoped polling
- [`fastapi_webhook_receiver.py`](./examples/fastapi_webhook_receiver.py) for a minimal webhook receiver

These are intentionally small. They are meant to be copied into a real worker, cron job, or receiver and then adapted to your own storage and job queue.

## Notes

This first version is intentionally thin. It aims to give Atlas customers one integration surface across polling and webhooks instead of pushing everyone straight into raw HTTP and receiver boilerplate.

You can override `base_url` explicitly if you need to point the SDK at a different Atlas environment.
