from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ranglerpy.client import RanglerClient


class BaseResource:
    def __init__(self, client: "RanglerClient") -> None:
        self.client = client

    def _get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        auth: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {"params": params, "auth": auth}
        if headers is not None:
            kwargs["headers"] = headers
        return self.client.request("GET", path, **kwargs)

    def _post(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        auth: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {"params": params, "json": json, "auth": auth}
        if headers is not None:
            kwargs["headers"] = headers
        return self.client.request("POST", path, **kwargs)

    def _patch(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        auth: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {"params": params, "json": json, "auth": auth}
        if headers is not None:
            kwargs["headers"] = headers
        return self.client.request("PATCH", path, **kwargs)

    def _delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        auth: str,
        headers: dict[str, str] | None = None,
    ) -> Any:
        kwargs: dict[str, Any] = {"params": params, "auth": auth}
        if headers is not None:
            kwargs["headers"] = headers
        return self.client.request("DELETE", path, **kwargs)
