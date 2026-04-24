"""Desktop client for Chemistry API routing."""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict

from .api_client import ChemistryApiClient, ChemistryApiError


DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_ROUTE = "cloud"
DEFAULT_ACTION = "analyze"


class ChemistryDesktopApp:
    """Tkinter-based desktop app for interacting with Chemistry API."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Chemistry Desktop Client")
        self.root.geometry("900x700")
        self.root.minsize(760, 600)

        self.api_url_var = tk.StringVar(value=DEFAULT_API_URL)
        self.route_var = tk.StringVar(value=DEFAULT_ROUTE)
        self.action_var = tk.StringVar(value=DEFAULT_ACTION)

        self.status_var = tk.StringVar(value="Ready.")
        self.client = ChemistryApiClient(DEFAULT_API_URL)

        self._build_ui()
        # Keep ALT+0 aligned with the original product flow.
        self.root.bind_all("<Alt-Key-0>", lambda _event: self._send_routed_request())

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)

        title = ttk.Label(
            container,
            text="Chemistry Desktop Client",
            font=("Segoe UI", 16, "bold"),
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ttk.Label(container, text="API Base URL").grid(row=1, column=0, sticky="w")
        api_entry = ttk.Entry(container, textvariable=self.api_url_var)
        api_entry.grid(row=1, column=1, sticky="ew", padx=(12, 0))
        ttk.Button(container, text="Apply URL", command=self._apply_api_url).grid(
            row=1, column=2, padx=(12, 0), sticky="ew"
        )

        ttk.Label(container, text="Route Type").grid(row=2, column=0, sticky="w", pady=(12, 0))
        route_combo = ttk.Combobox(
            container,
            textvariable=self.route_var,
            values=["cloud", "hybrid", "local"],
            state="readonly",
        )
        route_combo.grid(row=2, column=1, sticky="w", padx=(12, 0), pady=(12, 0))

        ttk.Label(container, text="Action").grid(row=3, column=0, sticky="w", pady=(12, 0))
        action_entry = ttk.Entry(container, textvariable=self.action_var)
        action_entry.grid(row=3, column=1, sticky="ew", padx=(12, 0), pady=(12, 0))

        data_label = ttk.Label(container, text="Data (JSON object)")
        data_label.grid(row=4, column=0, sticky="nw", pady=(12, 0))
        self.data_text = tk.Text(container, height=8, wrap="word", font=("Consolas", 10))
        self.data_text.grid(row=4, column=1, columnspan=2, sticky="nsew", padx=(12, 0), pady=(12, 0))
        self.data_text.insert(
            "1.0",
            json.dumps({"sample": "test"}, indent=2),
        )

        controls = ttk.Frame(container)
        controls.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        controls.columnconfigure((0, 1, 2, 3, 4), weight=1)
        ttk.Button(controls, text="Send to /api/route", command=self._send_routed_request).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(controls, text="Send to /process", command=self._send_direct_request).grid(
            row=0, column=1, sticky="ew", padx=(0, 8)
        )
        ttk.Button(controls, text="Route Info", command=self._route_info).grid(
            row=0, column=2, sticky="ew", padx=(0, 8)
        )
        ttk.Button(controls, text="Health Check", command=self._health_check).grid(
            row=0, column=3, sticky="ew", padx=(0, 8)
        )
        ttk.Button(controls, text="Clear Output", command=self._clear_output).grid(
            row=0, column=4, sticky="ew"
        )

        response_label = ttk.Label(container, text="Response")
        response_label.grid(row=6, column=0, sticky="nw", pady=(12, 0))
        self.response_text = tk.Text(container, height=14, wrap="word", font=("Consolas", 10))
        self.response_text.grid(
            row=6,
            column=1,
            columnspan=2,
            sticky="nsew",
            padx=(12, 0),
            pady=(12, 0),
        )

        status_label = ttk.Label(container, textvariable=self.status_var, foreground="#333")
        status_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(12, 0))

        container.rowconfigure(4, weight=1)
        container.rowconfigure(6, weight=2)

    def _apply_api_url(self) -> None:
        raw_url = self.api_url_var.get().strip()
        if not raw_url:
            self._set_status("API URL cannot be empty.", is_error=True)
            return
        self.client = ChemistryApiClient(raw_url)
        self.api_url_var.set(raw_url)
        self._set_status(f"API URL set to {raw_url}")

    def _health_check(self) -> None:
        self._apply_api_url()
        try:
            response = self.client.health()
            self._show_response(response)
            self._set_status("Health check completed.")
        except ChemistryApiError as exc:
            self._show_error(exc)

    def _route_info(self) -> None:
        self._apply_api_url()
        try:
            response = self.client.route_info()
            self._show_response(response)
            self._set_status("Fetched routing information.")
        except ChemistryApiError as exc:
            self._show_error(exc)

    def _send_routed_request(self) -> None:
        self._apply_api_url()
        route_type = self.route_var.get().strip()
        action = self.action_var.get().strip()
        data = self._parse_data_json()
        if data is None:
            return
        if not route_type or not action:
            self._set_status("Route type and action are required.", is_error=True)
            return

        payload = {"route_type": route_type, "action": action, "data": data}
        try:
            response = self.client.post_route(payload)
            self._show_response(response)
            self._set_status("Route request sent successfully.")
        except ChemistryApiError as exc:
            self._show_error(exc)

    def _send_direct_request(self) -> None:
        self._apply_api_url()
        route_type = self.route_var.get().strip()
        action = self.action_var.get().strip()
        data = self._parse_data_json()
        if data is None:
            return
        if not route_type or not action:
            self._set_status("Route type and action are required.", is_error=True)
            return

        payload = {"action": action, "data": data}
        if route_type == "hybrid":
            payload["prefer_cloud"] = bool(data.get("prefer_cloud", False))

        try:
            response = self.client.post_route_process(route_type, payload)
            self._show_response(response)
            self._set_status(f"Direct {route_type} request sent successfully.")
        except ChemistryApiError as exc:
            self._show_error(exc)

    def _parse_data_json(self) -> Dict[str, Any] | None:
        raw = self.data_text.get("1.0", "end").strip()
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            self._set_status(f"Data JSON is invalid: {exc}", is_error=True)
            return None
        if not isinstance(parsed, dict):
            self._set_status("Data must be a JSON object.", is_error=True)
            return None
        return parsed

    def _show_response(self, data: Dict[str, Any]) -> None:
        self.response_text.delete("1.0", "end")
        pretty = json.dumps(data, indent=2, ensure_ascii=True)
        self.response_text.insert("1.0", pretty)

    def _show_error(self, error: Exception) -> None:
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", str(error))
        self._set_status("Request failed. See output for details.", is_error=True)

    def _clear_output(self) -> None:
        self.response_text.delete("1.0", "end")
        self._set_status("Output cleared.")

    def _set_status(self, message: str, *, is_error: bool = False) -> None:
        prefix = "Error: " if is_error else ""
        self.status_var.set(f"{prefix}{message}")


def run() -> None:
    root = tk.Tk()
    app = ChemistryDesktopApp(root)
    app._set_status("Ready. Configure API URL and send a request.")
    root.mainloop()


if __name__ == "__main__":
    run()
