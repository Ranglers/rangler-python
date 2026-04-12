from __future__ import annotations

from typing import Any

from .base import BaseResource


class CompaniesResource(BaseResource):
    def list(self, **params: Any) -> Any:
        return self._get("/companies", params=params or None, auth="api_key")

    def get(self, company_id: str) -> Any:
        return self._get(f"/companies/{company_id}", auth="api_key")

    def get_details(self, company_id: str) -> Any:
        return self._get(f"/companies/{company_id}/details", auth="api_key")

    def list_filings(self, company_id: str, **params: Any) -> Any:
        return self._get(f"/companies/{company_id}/filings", params=params or None, auth="api_key")
