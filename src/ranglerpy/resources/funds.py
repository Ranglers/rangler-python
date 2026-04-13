from __future__ import annotations

from typing import Any

from .base import BaseResource


class FundsResource(BaseResource):
    def list(self, **params: Any) -> Any:
        return self._get("/funds", params=params or None, auth="api_key")

    def get(self, fund_id: str) -> Any:
        return self._get(f"/funds/{fund_id}", auth="api_key")

    def list_snapshots(self, fund_id: str, **params: Any) -> Any:
        return self._get(f"/funds/{fund_id}/snapshots", params=params or None, auth="api_key")
