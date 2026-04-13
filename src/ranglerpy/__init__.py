from ._version import __version__
from .exceptions import (
    APIError,
    AuthenticationError,
    DuplicateEventError,
    InvalidSignatureError,
    RanglerError,
    WebhookVerificationError,
)
from .idempotency import IdempotencyStore, InMemoryIdempotencyStore
from .models import EventEnvelope, EventsPage
from .polling import (
    AsyncPollingConsumer,
    CursorStore,
    FileCursorStore,
    InMemoryCursorStore,
    PollingCheckpoint,
    PollingConsumer,
)
from .webhooks import (
    compute_webhook_signature,
    extract_webhook_headers,
    parse_and_verify_webhook,
    parse_webhook_event,
    verify_webhook_signature,
)

__all__ = [
    "APIError",
    "AuthenticationError",
    "AsyncRanglerClient",
    "AsyncPollingConsumer",
    "CursorStore",
    "DuplicateEventError",
    "EventEnvelope",
    "EventsPage",
    "FileCursorStore",
    "IdempotencyStore",
    "InMemoryCursorStore",
    "InMemoryIdempotencyStore",
    "InvalidSignatureError",
    "PollingCheckpoint",
    "PollingConsumer",
    "RanglerClient",
    "RanglerError",
    "WebhookVerificationError",
    "compute_webhook_signature",
    "extract_webhook_headers",
    "parse_and_verify_webhook",
    "parse_webhook_event",
    "verify_webhook_signature",
]


def __getattr__(name: str):
    if name == "RanglerClient":
        from .client import RanglerClient

        return RanglerClient
    if name == "AsyncRanglerClient":
        from .client import AsyncRanglerClient

        return AsyncRanglerClient
    raise AttributeError(name)
