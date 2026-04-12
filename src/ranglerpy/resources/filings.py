from __future__ import annotations

from typing import Any

from .base import BaseResource


class FilingsResource(BaseResource):
    def list(self, **params: Any) -> Any:
        return self._get("/filings", params=params or None, auth="api_key")

    def get(self, filing_id: str) -> Any:
        return self._get(f"/filings/{filing_id}", auth="api_key")
