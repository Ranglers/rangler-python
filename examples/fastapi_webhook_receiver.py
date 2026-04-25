from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request

from ranglerpy import (
    DuplicateEventError,
    InMemoryIdempotencyStore,
    InvalidSignatureError,
    Webhook,
)

app = FastAPI()
store = InMemoryIdempotencyStore()


@app.post("/rangler/webhooks")
async def rangler_webhook(request: Request):
    raw_body = await request.body()

    try:
        event = Webhook.construct_event(
            headers=request.headers,
            raw_body=raw_body,
            secret=os.environ["RANGLER_WEBHOOK_SECRET"],
            idempotency_store=store,
        )
    except InvalidSignatureError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DuplicateEventError:
        return {"duplicate": True}

    return {"received": event.id, "type": event.type}
