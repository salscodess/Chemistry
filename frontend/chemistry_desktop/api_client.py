from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import requests


DEFAULT_TIMEOUT_SECONDS = 20


class ChemistryApiError(RuntimeError):
    """Raised for network and API-level failures."""


@dataclass
class ChemistryApiClient:
    base_url: str
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def _url(self, path: str) -> str:
        cleaned = self.base_url.rstrip("/")
        return f"{cleaned}{path}"

    def health(self) -> Dict[str, Any]:
        return self._get_json("/health")

    def route_info(self) -> Dict[str, Any]:
        return self._get_json("/api/info")

    def post_route(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post_json("/api/route", payload)

    def post_route_process(self, route_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post_json(f"/api/{route_type}/process", payload)

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(
                self._url(path),
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise ChemistryApiError(f"POST {path} failed: {exc}") from exc

    def _get_json(self, path: str) -> Dict[str, Any]:
        try:
            response = requests.get(
                self._url(path),
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise ChemistryApiError(f"GET {path} failed: {exc}") from exc

