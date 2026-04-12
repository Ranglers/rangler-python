from __future__ import annotations

from .async_base import AsyncBaseResource


class AsyncUsageResource(AsyncBaseResource):
    async def get(self, organization_id: str) -> dict:
        return await self._get(f"/organizations/{organization_id}/usage", auth="bearer")

    async def billing_status(self, organization_id: str) -> dict:
        return await self._get(f"/organizations/{organization_id}/billing-status", auth="bearer")

    async def request_plan_review(
        self,
        organization_id: str,
        *,
        desired_package: str,
        workflow_summary: str,
        requirements_summary: str | None = None,
    ) -> dict:
        payload = {
            "desired_package": desired_package,
            "workflow_summary": workflow_summary,
        }
        if requirements_summary is not None:
            payload["requirements_summary"] = requirements_summary
        return await self._post(
            f"/organizations/{organization_id}/plan-review-requests",
            json=payload,
            auth="bearer",
        )
