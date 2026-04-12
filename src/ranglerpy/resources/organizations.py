from __future__ import annotations

from .base import BaseResource


class OrganizationsResource(BaseResource):
    def list(self) -> dict:
        return self._get("/organizations", auth="bearer")

    def create(self, *, name: str, billing_email: str) -> dict:
        return self._post(
            "/organizations",
            json={
                "name": name,
                "billing_email": billing_email,
            },
            auth="bearer",
        )

    def get(self, organization_id: str) -> dict:
        return self._get(f"/organizations/{organization_id}", auth="bearer")
