from .exceptions import (
    APIError,
    AuthenticationError,
    InvalidSignatureError,
    RanglerError,
    WebhookVerificationError,
)
from .models import EventEnvelope, EventsPage
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
    "EventEnvelope",
    "EventsPage",
    "InvalidSignatureError",
    "RanglerClient",
    "RanglerError",
    "WebhookVerificationError",
    "compute_webhook_signature",
    "extract_webhook_headers",
    "parse_and_verify_webhook",
    "parse_webhook_event",
    "verify_webhook_signature",
]

__version__ = "0.1.0"


def __getattr__(name: str):
    if name == "RanglerClient":
        from .client import RanglerClient

        return RanglerClient
    if name == "AsyncRanglerClient":
        from .client import AsyncRanglerClient

        return AsyncRanglerClient
    raise AttributeError(name)
