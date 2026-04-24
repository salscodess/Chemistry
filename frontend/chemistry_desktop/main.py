"""Desktop client for Chemistry API routing."""

from __future__ import annotations

import json
import math
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Any, Callable, Dict

from .api_client import ChemistryApiClient, ChemistryApiError


DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_ROUTE = "cloud"
DEFAULT_ACTION = "analyze"
TOP_BAR_BG = "#0F172A"
APP_BG = "#111827"
CARD_BG = "#1F2937"
TEXT_LIGHT = "#E5E7EB"
TEXT_MUTED = "#94A3B8"
ACCENT = "#22D3EE"
SUCCESS = "#22C55E"
ERROR = "#F97316"


class ChemistryDesktopApp:
    """Modern Tkinter desktop app for interacting with Chemistry API."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Chemistry Desktop")
        self.root.geometry("1020x720")
        self.root.minsize(900, 620)
        self.root.configure(bg=APP_BG)

        self.api_url_var = tk.StringVar(value=DEFAULT_API_URL)
        self.route_var = tk.StringVar(value=DEFAULT_ROUTE)
        self.action_var = tk.StringVar(value=DEFAULT_ACTION)
        self.status_var = tk.StringVar(value="Ready")
        self.api_state_var = tk.StringVar(value="UNKNOWN")
        self.latency_var = tk.StringVar(value="--")
        self.request_count_var = tk.StringVar(value="0")
        self.success_rate_var = tk.StringVar(value="0%")
        self.compact_data_var = tk.StringVar(value="API UNKNOWN | route cloud | 0 requests")
        self.always_on_top_var = tk.BooleanVar(value=True)

        self.client = ChemistryApiClient(DEFAULT_API_URL)
        self.requests_total = 0
        self.requests_success = 0
        self.last_window_geometry = self.root.geometry()
        self.is_collapsed = False
        self.loading_active = False
        self.loading_label = ""
        self.loading_step = 0
        self.pulse_phase = 0.0
        self.status_is_online = False

        self._configure_styles()
        self._build_ui()
        self._set_always_on_top(True)
        self._animate_status_dot()
        self._schedule_periodic_health_probe()

        # Keep ALT+0 aligned with the original flow and Ctrl+- for compact mode.
        self.root.bind_all("<Alt-Key-0>", lambda _event: self._send_routed_request())
        self.root.bind_all("<Control-minus>", lambda _event: self._toggle_compact_mode())
        self.root.bind("<FocusOut>", lambda _event: self.root.after(60, self._refresh_topmost))

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Chem.TLabel", background=CARD_BG, foreground=TEXT_LIGHT, font=("Segoe UI", 10))
        style.configure("Chem.Muted.TLabel", background=CARD_BG, foreground=TEXT_MUTED, font=("Segoe UI", 9))
        style.configure("Chem.TEntry", fieldbackground="#0B1220", foreground=TEXT_LIGHT, borderwidth=0)
        style.configure("Chem.TCombobox", fieldbackground="#0B1220", foreground=TEXT_LIGHT)
        style.configure(
            "Chem.TButton",
            background="#0EA5E9",
            foreground="#03111F",
            borderwidth=0,
            focusthickness=0,
            focuscolor="#0EA5E9",
            font=("Segoe UI", 9, "bold"),
            padding=(10, 7),
        )
        style.map(
            "Chem.TButton",
            background=[("active", "#38BDF8"), ("disabled", "#334155")],
            foreground=[("disabled", "#94A3B8")],
        )

    def _build_ui(self) -> None:
        self.shell = tk.Frame(self.root, bg=APP_BG)
        self.shell.pack(fill="both", expand=True)

        self._build_top_bar(self.shell)
        self._build_body(self.shell)

        self.compact_bar = tk.Frame(self.root, bg=TOP_BAR_BG, height=64, padx=10, pady=8)
        self.compact_bar.columnconfigure(1, weight=1)
        tk.Label(
            self.compact_bar,
            text="Chemistry",
            bg=TOP_BAR_BG,
            fg=TEXT_LIGHT,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            self.compact_bar,
            textvariable=self.compact_data_var,
            bg=TOP_BAR_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).grid(row=0, column=1, sticky="ew", padx=(12, 8))
        tk.Button(
            self.compact_bar,
            text="Send",
            command=self._send_routed_request,
            bg="#0EA5E9",
            fg="#03111F",
            activebackground="#38BDF8",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
        ).grid(row=0, column=2, padx=(0, 8))
        tk.Button(
            self.compact_bar,
            text="Expand",
            command=self._toggle_compact_mode,
            bg="#334155",
            fg=TEXT_LIGHT,
            activebackground="#475569",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
        ).grid(row=0, column=3)

    def _build_top_bar(self, parent: tk.Widget) -> None:
        top_bar = tk.Frame(parent, bg=TOP_BAR_BG, padx=16, pady=12)
        top_bar.pack(fill="x")

        left = tk.Frame(top_bar, bg=TOP_BAR_BG)
        left.pack(side="left", fill="x", expand=True)

        title = tk.Label(
            left,
            text="Chemistry Desktop",
            bg=TOP_BAR_BG,
            fg=TEXT_LIGHT,
            font=("Segoe UI", 17, "bold"),
        )
        title.pack(anchor="w")
        subtitle = tk.Label(
            left,
            text="Always-on-top command panel with compact mode (Ctrl+-)",
            bg=TOP_BAR_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        )
        subtitle.pack(anchor="w")

        right = tk.Frame(top_bar, bg=TOP_BAR_BG)
        right.pack(side="right")

        status_block = tk.Frame(right, bg=TOP_BAR_BG)
        status_block.pack(side="left", padx=(0, 10))
        self.status_dot = tk.Canvas(status_block, width=16, height=16, bg=TOP_BAR_BG, highlightthickness=0)
        self.status_dot.pack(side="left", padx=(0, 5))
        tk.Label(
            status_block,
            textvariable=self.api_state_var,
            bg=TOP_BAR_BG,
            fg=TEXT_LIGHT,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        topmost_toggle = tk.Checkbutton(
            right,
            text="Always on top",
            variable=self.always_on_top_var,
            command=lambda: self._set_always_on_top(self.always_on_top_var.get()),
            bg=TOP_BAR_BG,
            fg=TEXT_LIGHT,
            activebackground=TOP_BAR_BG,
            activeforeground=TEXT_LIGHT,
            selectcolor=TOP_BAR_BG,
            font=("Segoe UI", 9),
        )
        topmost_toggle.pack(side="left", padx=(0, 8))

        self.collapse_button = tk.Button(
            right,
            text="Collapse",
            command=self._toggle_compact_mode,
            bg="#334155",
            fg=TEXT_LIGHT,
            activebackground="#475569",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6,
        )
        self.collapse_button.pack(side="left")

    def _build_body(self, parent: tk.Widget) -> None:
        body = tk.Frame(parent, bg=APP_BG, padx=14, pady=14)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=4)
        body.grid_columnconfigure(1, weight=5)
        body.grid_rowconfigure(2, weight=1)

        card_left = tk.Frame(body, bg=CARD_BG, padx=14, pady=14, highlightbackground="#374151", highlightthickness=1)
        card_left.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(0, 10))
        card_left.grid_columnconfigure(1, weight=1)
        card_left.grid_rowconfigure(4, weight=1)

        tk.Label(card_left, text="Endpoint", bg=CARD_BG, fg=TEXT_LIGHT, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(card_left, textvariable=self.api_url_var, style="Chem.TEntry").grid(
            row=0, column=1, sticky="ew", padx=(10, 0)
        )
        ttk.Button(card_left, text="Apply", style="Chem.TButton", command=self._apply_api_url).grid(
            row=0, column=2, padx=(8, 0)
        )

        tk.Label(card_left, text="Route", bg=CARD_BG, fg=TEXT_LIGHT, font=("Segoe UI", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=(12, 0)
        )
        ttk.Combobox(
            card_left,
            textvariable=self.route_var,
            values=["cloud", "hybrid", "local"],
            state="readonly",
            style="Chem.TCombobox",
        ).grid(row=1, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=(12, 0))

        tk.Label(card_left, text="Action", bg=CARD_BG, fg=TEXT_LIGHT, font=("Segoe UI", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )
        ttk.Entry(card_left, textvariable=self.action_var, style="Chem.TEntry").grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=(10, 0)
        )

        tk.Label(card_left, text="Data (JSON)", bg=CARD_BG, fg=TEXT_LIGHT, font=("Segoe UI", 10, "bold")).grid(
            row=3, column=0, sticky="nw", pady=(12, 0)
        )
        self.data_text = scrolledtext.ScrolledText(
            card_left,
            height=12,
            wrap="word",
            bg="#0B1220",
            fg=TEXT_LIGHT,
            insertbackground=TEXT_LIGHT,
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0,
        )
        self.data_text.grid(row=3, column=1, columnspan=2, sticky="nsew", padx=(10, 0), pady=(12, 0))
        self.data_text.insert("1.0", json.dumps({"sample": "test"}, indent=2))

        button_row_1 = tk.Frame(card_left, bg=CARD_BG)
        button_row_1.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        button_row_1.grid_columnconfigure((0, 1), weight=1)
        ttk.Button(button_row_1, text="Route Request", style="Chem.TButton", command=self._send_routed_request).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(button_row_1, text="Direct Request", style="Chem.TButton", command=self._send_direct_request).grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )

        button_row_2 = tk.Frame(card_left, bg=CARD_BG)
        button_row_2.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        button_row_2.grid_columnconfigure((0, 1, 2), weight=1)
        ttk.Button(button_row_2, text="Health", style="Chem.TButton", command=self._health_check).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(button_row_2, text="Route Info", style="Chem.TButton", command=self._route_info).grid(
            row=0, column=1, sticky="ew", padx=6
        )
        ttk.Button(button_row_2, text="Clear", style="Chem.TButton", command=self._clear_output).grid(
            row=0, column=2, sticky="ew", padx=(6, 0)
        )

        self.action_buttons = button_row_1.winfo_children() + button_row_2.winfo_children()

        metrics_card = tk.Frame(body, bg=CARD_BG, padx=14, pady=12, highlightbackground="#374151", highlightthickness=1)
        metrics_card.grid(row=0, column=1, sticky="ew")
        metrics_card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._metric(metrics_card, "Latency", self.latency_var, 0)
        self._metric(metrics_card, "Requests", self.request_count_var, 1)
        self._metric(metrics_card, "Success", self.success_rate_var, 2)
        self._metric(metrics_card, "Route", self.route_var, 3)

        response_card = tk.Frame(body, bg=CARD_BG, padx=14, pady=12, highlightbackground="#374151", highlightthickness=1)
        response_card.grid(row=1, column=1, rowspan=2, sticky="nsew", pady=(10, 0))
        response_card.grid_rowconfigure(1, weight=1)
        response_card.grid_columnconfigure(0, weight=1)

        tk.Label(response_card, text="Response", bg=CARD_BG, fg=TEXT_LIGHT, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.response_text = scrolledtext.ScrolledText(
            response_card,
            wrap="word",
            bg="#0B1220",
            fg=TEXT_LIGHT,
            insertbackground=TEXT_LIGHT,
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0,
        )
        self.response_text.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        self.status_label = tk.Label(
            response_card,
            textvariable=self.status_var,
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
        )
        self.status_label.grid(row=2, column=0, sticky="ew", pady=(8, 0))

    def _metric(self, parent: tk.Widget, title: str, variable: tk.StringVar, column: int) -> None:
        frame = tk.Frame(parent, bg=CARD_BG)
        frame.grid(row=0, column=column, sticky="ew")
        tk.Label(frame, text=title, bg=CARD_BG, fg=TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(frame, textvariable=variable, bg=CARD_BG, fg=TEXT_LIGHT, font=("Segoe UI", 12, "bold")).pack(
            anchor="w"
        )

    def _apply_api_url(self) -> bool:
        raw_url = self.api_url_var.get().strip()
        if not raw_url:
            self._set_status("API URL cannot be empty.", is_error=True)
            return False
        self.client = ChemistryApiClient(raw_url)
        self.api_url_var.set(raw_url)
        self._set_status(f"API URL set to {raw_url}")
        self._update_compact_bar_data()
        return True

    def _health_check(self) -> None:
        if not self._apply_api_url():
            return
        self._run_request_async(
            "Checking API health",
            self.client.health,
            lambda response, elapsed_ms: self._handle_success_response(response, elapsed_ms, "Health check completed."),
        )

    def _route_info(self) -> None:
        if not self._apply_api_url():
            return
        self._run_request_async(
            "Fetching route information",
            self.client.route_info,
            lambda response, elapsed_ms: self._handle_success_response(
                response, elapsed_ms, "Fetched routing information."
            ),
        )

    def _send_routed_request(self) -> None:
        if not self._apply_api_url():
            return
        route_type = self.route_var.get().strip()
        action = self.action_var.get().strip()
        data = self._parse_data_json()
        if data is None:
            return
        if not route_type or not action:
            self._set_status("Route type and action are required.", is_error=True)
            return
        payload = {"route_type": route_type, "action": action, "data": data}
        self._run_request_async(
            "Sending routed request",
            lambda: self.client.post_route(payload),
            lambda response, elapsed_ms: self._handle_success_response(
                response,
                elapsed_ms,
                "Routed request completed.",
            ),
        )

    def _send_direct_request(self) -> None:
        if not self._apply_api_url():
            return
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
        self._run_request_async(
            f"Sending direct {route_type} request",
            lambda: self.client.post_route_process(route_type, payload),
            lambda response, elapsed_ms: self._handle_success_response(
                response,
                elapsed_ms,
                f"Direct {route_type} request completed.",
            ),
        )

    def _run_request_async(
        self,
        loading_label: str,
        call: Callable[[], Dict[str, Any]],
        on_success: Callable[[Dict[str, Any], float], None],
    ) -> None:
        self._begin_loading(loading_label)
        self._set_buttons_enabled(False)
        self.requests_total += 1
        self.request_count_var.set(str(self.requests_total))
        self._update_compact_bar_data()

        def worker() -> None:
            started = time.perf_counter()
            try:
                result = call()
                elapsed_ms = (time.perf_counter() - started) * 1000
                self.root.after(0, lambda: self._on_request_success(result, elapsed_ms, on_success))
            except ChemistryApiError as exc:
                elapsed_ms = (time.perf_counter() - started) * 1000
                self.root.after(0, lambda: self._on_request_error(exc, elapsed_ms))

        threading.Thread(target=worker, daemon=True).start()

    def _on_request_success(
        self, response: Dict[str, Any], elapsed_ms: float, on_success: Callable[[Dict[str, Any], float], None]
    ) -> None:
        self.requests_success += 1
        self.status_is_online = True
        self.api_state_var.set("ONLINE")
        self.latency_var.set(f"{elapsed_ms:.0f} ms")
        self._refresh_success_rate()
        on_success(response, elapsed_ms)
        self._finish_loading()

    def _on_request_error(self, error: Exception, elapsed_ms: float) -> None:
        self.status_is_online = False
        self.api_state_var.set("OFFLINE")
        self.latency_var.set(f"{elapsed_ms:.0f} ms")
        self._refresh_success_rate()
        self._show_error(error)
        self._finish_loading()

    def _handle_success_response(self, data: Dict[str, Any], elapsed_ms: float, message: str) -> None:
        self._show_response(data)
        self._set_status(f"{message} ({elapsed_ms:.0f} ms)")
        self._update_compact_bar_data()

    def _refresh_success_rate(self) -> None:
        if self.requests_total <= 0:
            self.success_rate_var.set("0%")
            return
        ratio = int((self.requests_success / self.requests_total) * 100)
        self.success_rate_var.set(f"{ratio}%")
        self._update_compact_bar_data()

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
        self.response_text.insert("1.0", json.dumps(data, indent=2, ensure_ascii=True))

    def _show_error(self, error: Exception) -> None:
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", str(error))
        self._set_status("Request failed. See output for details.", is_error=True)

    def _clear_output(self) -> None:
        self.response_text.delete("1.0", "end")
        self._set_status("Output cleared.")

    def _set_status(self, message: str, *, is_error: bool = False) -> None:
        self.status_var.set(message)
        self.status_label.configure(fg=ERROR if is_error else TEXT_MUTED)
        self._update_compact_bar_data()

    def _begin_loading(self, label: str) -> None:
        self.loading_active = True
        self.loading_label = label
        self.loading_step = 0
        self._animate_loading_status()

    def _finish_loading(self) -> None:
        self.loading_active = False
        self._set_buttons_enabled(True)

    def _animate_loading_status(self) -> None:
        if not self.loading_active:
            return
        dots = "." * ((self.loading_step % 3) + 1)
        self.status_var.set(f"{self.loading_label}{dots}")
        self.loading_step += 1
        self.root.after(200, self._animate_loading_status)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for button in self.action_buttons:
            button.configure(state=state)

    def _set_always_on_top(self, enabled: bool) -> None:
        self.always_on_top_var.set(enabled)
        self.root.attributes("-topmost", enabled)
        self._set_status("Always-on-top enabled." if enabled else "Always-on-top disabled.")

    def _refresh_topmost(self) -> None:
        if self.always_on_top_var.get():
            self.root.attributes("-topmost", True)

    def _toggle_compact_mode(self) -> None:
        if self.is_collapsed:
            self._expand_from_compact()
        else:
            self._collapse_to_compact()

    def _collapse_to_compact(self) -> None:
        self.is_collapsed = True
        self.last_window_geometry = self.root.geometry()
        self.shell.pack_forget()
        self.compact_bar.pack(fill="x")
        self.collapse_button.configure(text="Expand")
        self._update_compact_bar_data()
        self._animate_window_height(target_height=74)

    def _expand_from_compact(self) -> None:
        self.is_collapsed = False
        self.compact_bar.pack_forget()
        self.shell.pack(fill="both", expand=True)
        self.collapse_button.configure(text="Collapse")
        target_height = self._height_from_geometry(self.last_window_geometry)
        self._animate_window_height(target_height=max(target_height, 620))

    def _animate_window_height(self, target_height: int) -> None:
        current_height = self.root.winfo_height()
        if current_height <= 1:
            current_height = self._height_from_geometry(self.root.geometry())
        direction = 1 if target_height > current_height else -1
        step = 26 * direction

        def tick(height: int) -> None:
            if (direction > 0 and height >= target_height) or (direction < 0 and height <= target_height):
                height = target_height
            self.root.geometry(
                f"{self.root.winfo_width()}x{height}+{self.root.winfo_x()}+{self.root.winfo_y()}"
            )
            if height != target_height:
                self.root.after(10, lambda: tick(height + step))

        tick(current_height)

    def _height_from_geometry(self, geometry: str) -> int:
        # Geometry format: WIDTHxHEIGHT+X+Y
        size = geometry.split("+", maxsplit=1)[0]
        if "x" not in size:
            return 620
        _, height = size.split("x", maxsplit=1)
        try:
            return int(height)
        except ValueError:
            return 620

    def _update_compact_bar_data(self) -> None:
        self.compact_data_var.set(
            f"API {self.api_state_var.get()} | route {self.route_var.get()} | "
            f"latency {self.latency_var.get()} | req {self.requests_total}"
        )

    def _animate_status_dot(self) -> None:
        self.pulse_phase += 0.17
        pulse = 4 + (math.sin(self.pulse_phase) + 1.0) * 1.8
        center = 8
        radius = pulse
        color = SUCCESS if self.status_is_online else ERROR
        self.status_dot.delete("all")
        self.status_dot.create_oval(center - radius, center - radius, center + radius, center + radius, fill=color, outline="")
        self.root.after(90, self._animate_status_dot)

    def _schedule_periodic_health_probe(self) -> None:
        def probe() -> None:
            try:
                self.client.health()
                self.root.after(0, lambda: self._set_probe_state(True))
            except ChemistryApiError:
                self.root.after(0, lambda: self._set_probe_state(False))

        threading.Thread(target=probe, daemon=True).start()
        self.root.after(15000, self._schedule_periodic_health_probe)

    def _set_probe_state(self, online: bool) -> None:
        self.status_is_online = online
        self.api_state_var.set("ONLINE" if online else "OFFLINE")
        self._update_compact_bar_data()


def run() -> None:
    root = tk.Tk()
    app = ChemistryDesktopApp(root)
    app._set_status("Ready. ALT+0 sends a routed request.")
    root.mainloop()


if __name__ == "__main__":
    run()
