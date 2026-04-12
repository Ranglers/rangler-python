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
from ranglerpy import RanglerClient

client = RanglerClient(
    api_key="atl_test_your_api_key",
    environment="sandbox",
)

page = client.events.list(limit=25)
for event in page.items:
    print(event.type, event.title)

for event in client.events.iter_all(limit=100, event_types=["filing.new"]):
    print(event.id, event.type)
```

### Async polling

```python
from ranglerpy import AsyncRanglerClient

async with AsyncRanglerClient(
    api_key="atl_test_your_api_key",
    environment="sandbox",
) as client:
    async for event in client.events.iter_all(
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
from ranglerpy import parse_and_verify_webhook

event = parse_and_verify_webhook(
    headers=headers,
    raw_body=raw_body,
    secret=webhook_secret,
)

print(event.type, event.title)
```

### FastAPI webhook handler

```python
from fastapi import FastAPI, HTTPException, Request

from ranglerpy import InvalidSignatureError, parse_and_verify_webhook

app = FastAPI()


@app.post("/atlas/webhooks")
async def atlas_webhook(request: Request):
    raw_body = await request.body()

    try:
        event = parse_and_verify_webhook(
            headers=request.headers,
            raw_body=raw_body,
            secret="whsec_your_secret",
        )
    except InvalidSignatureError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"received": event.id}
```

### Flask webhook handler

```python
from flask import Flask, jsonify, request

from ranglerpy import InvalidSignatureError, parse_and_verify_webhook

app = Flask(__name__)


@app.post("/atlas/webhooks")
def atlas_webhook():
    raw_body = request.get_data()

    try:
        event = parse_and_verify_webhook(
            headers=request.headers,
            raw_body=raw_body,
            secret="whsec_your_secret",
        )
    except InvalidSignatureError as exc:
        return jsonify({"error": str(exc)}), 400

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
- Atlas webhook signature verification
- webhook payload parsing
- parse-and-verify helper for webhook receivers
- async client support

## Notes

This first version is intentionally thin. It aims to give Atlas customers one integration surface across polling and webhooks instead of pushing everyone straight into raw HTTP and receiver boilerplate.

You can override `base_url` explicitly if you need to point the SDK at a different Atlas environment.
