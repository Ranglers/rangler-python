from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request

from ranglerpy import (
    DuplicateEventError,
    InMemoryIdempotencyStore,
    InvalidSignatureError,
    parse_and_verify_webhook,
)

app = FastAPI()
store = InMemoryIdempotencyStore()


@app.post("/atlas/webhooks")
async def atlas_webhook(request: Request):
    raw_body = await request.body()

    try:
        event = parse_and_verify_webhook(
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
