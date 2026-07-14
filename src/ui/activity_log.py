"""Activity log widget for Repo Save Manager.

Design: the dashboard only ever shows the single most recent entry as a
compact one-line preview. The full, scrollable history lives in a separate
popup window opened via the "View Full Log" button. This keeps the main
dashboard from having a tall, awkwardly-stretched log list eating vertical
space — instead it's just one line, always.

Public interface is intentionally unchanged from before so nothing else in
the app needs to be touched:
    log = ActivityLog(master)
    log.grid(...)
    log.append(timestamp, level, message)
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - runtime fallback for environments without the dependency
    import tkinter as tk

    class _CTkShim:
        _UNSUPPORTED = {
            "fg_color", "corner_radius", "border_width", "border_color",
            "hover_color", "text_color", "width", "height",
        }

        @classmethod
        def _strip(cls, kwargs: dict[str, object]) -> dict[str, object]:
            return {k: v for k, v in kwargs.items() if k not in cls._UNSUPPORTED}

    class CTkFrame(_CTkShim, tk.Frame):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class CTkLabel(_CTkShim, tk.Label):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class CTkButton(_CTkShim, tk.Button):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class CTkScrollableFrame(_CTkShim, tk.Frame):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class CTkToplevel(_CTkShim, tk.Toplevel):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class _CtkModule:
        CTkFrame = CTkFrame
        CTkLabel = CTkLabel
        CTkButton = CTkButton
        CTkScrollableFrame = CTkScrollableFrame
        CTkToplevel = CTkToplevel

    ctk = _CtkModule()  # type: ignore[assignment]

from src.ui import theme


_LEVEL_ICONS = {
    "success": "\u2713",
    "warning": "\u26A0",
    "danger": "\u2620",
    "info": "\u2139",
}

_KNOWN_LEVELS = {"success", "warning", "danger", "info"}


@dataclass(slots=True)
class _LogEntry:
    timestamp: str
    level: str
    message: str


class ActivityLog(ctk.CTkFrame):
    def __init__(self, master=None, max_history: int = 500) -> None:
        try:
            super().__init__(
                master,
                fg_color=theme.BG_SECONDARY,
                corner_radius=theme.PANEL_CORNER_RADIUS,
                border_width=1,
                border_color=theme.BORDER,
            )
        except Exception:
            super().__init__(master)

        self._entries: list[_LogEntry] = []
        self._max_history = max_history
        self._full_log_window = None
        self._full_log_list = None

        try:
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=0)
        except Exception:
            pass

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(10, 0))
        header_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_row, text="ACTIVITY LOG", font=theme.body_font(11, "bold"), text_color=theme.TEXT_MUTED,
        ).grid(row=0, column=0, sticky="w")

        self._view_all_button = ctk.CTkButton(
            header_row,
            text="View Full Log",
            width=112,
            height=26,
            corner_radius=theme.BUTTON_CORNER_RADIUS,
            fg_color="transparent",
            hover_color=theme.BG_CARD_HOVER,
            text_color=theme.TEXT_SECONDARY,
            border_width=1,
            border_color=theme.BORDER,
            font=theme.body_font(11),
            command=self._open_full_log,
        )
        self._view_all_button.grid(row=0, column=1, sticky="e")

        preview_row = ctk.CTkFrame(self, fg_color="transparent")
        preview_row.grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=(6, 12))
        preview_row.grid_columnconfigure(1, weight=1)

        # Compact taxman avatar for visual output feedback.
        # Kept fixed-size (not stretching) to avoid layout distortions.
        self._taxman_img = None
        self._preview_icon_label = ctk.CTkLabel(
            preview_row,
            text="",
            width=18,
        )
        self._preview_icon_label.grid(row=0, column=0, sticky="w")

        self._preview_label = ctk.CTkLabel(
            preview_row,
            text="No activity yet.",
            font=theme.body_font(12),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
            justify="left",
            wraplength=520,
        )
        self._preview_label.grid(row=0, column=1, sticky="ew", padx=(8, 0))


    # ------------------------------------------------------------------
    # Public API — unchanged signature from before
    # ------------------------------------------------------------------
    def append(self, timestamp: str, level: str, message: str) -> None:
        entry = _LogEntry(timestamp=timestamp, level=level, message=message)
        self._entries.append(entry)
        if len(self._entries) > self._max_history:
            self._entries.pop(0)

        self._update_preview(entry)

        if self._full_log_window is not None and self._window_is_open():
            self._append_full_log_row(entry)

    # ------------------------------------------------------------------
    # Preview (always one line, on the dashboard itself)
    # ------------------------------------------------------------------
    def _update_preview(self, entry: _LogEntry) -> None:
        # When we have any log output, show the compact taxman face on the
        # preview row (fixed-size to avoid stretching).
        if entry.level in {"success", "warning", "danger", "info"}:
            try:
                from src.utils.constants import ASSETS_DIR
                taxman_path = ASSETS_DIR / "images" / "taxmann.png"

                try:
                    from PIL import Image
                except ImportError:
                    Image = None  # type: ignore

                if Image is not None:
                    img = Image.open(taxman_path)
                    # Keep aspect, fit within 20x20 box.
                    img.thumbnail((20, 20))
                    if hasattr(ctk, "CTkImage"):
                        self._taxman_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                        self._preview_icon_label.configure(image=self._taxman_img, text="")
                    else:
                        self._taxman_img = img
                        # tkinter PhotoImage fallback isn't handled; keep text.
                        self._preview_icon_label.configure(text=_LEVEL_ICONS.get(entry.level, _LEVEL_ICONS["info"]))
                else:
                    # No PIL: fallback to text icon.
                    self._preview_icon_label.configure(text=_LEVEL_ICONS.get(entry.level, _LEVEL_ICONS["info"]))
            except Exception:
                # Absolute fallback.
                self._preview_icon_label.configure(text=_LEVEL_ICONS.get(entry.level, _LEVEL_ICONS["info"]))
        else:
            # Unknown level; keep the old icon behavior.
            icon = _LEVEL_ICONS.get(entry.level, _LEVEL_ICONS["info"])
            self._preview_icon_label.configure(text=icon)

        self._preview_label.configure(text=f"{entry.timestamp}  {entry.message}")


    # ------------------------------------------------------------------
    # Full log popup (on demand, via the "View Full Log" button)
    # ------------------------------------------------------------------
    def _window_is_open(self) -> bool:
        try:
            return bool(self._full_log_window.winfo_exists())
        except Exception:
            return False

    def _open_full_log(self) -> None:
        if self._full_log_window is not None and self._window_is_open():
            self._full_log_window.lift()
            try:
                self._full_log_window.focus_force()
            except Exception:
                pass
            return

        toplevel = ctk.CTkToplevel(self)
        toplevel.title("Activity Log")
        toplevel.geometry("640x480")
        try:
            toplevel.minsize(420, 320)
        except Exception:
            pass
        try:
            toplevel.configure(fg_color=theme.BG_PRIMARY)
        except Exception:
            pass

        ctk.CTkLabel(
            toplevel, text="FULL ACTIVITY LOG", font=theme.header_font(16), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(16, 8))

        list_frame = ctk.CTkScrollableFrame(toplevel, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._full_log_window = toplevel
        self._full_log_list = list_frame

        for entry in self._entries:
            self._append_full_log_row(entry)

        toplevel.protocol("WM_DELETE_WINDOW", self._close_full_log)

    def _close_full_log(self) -> None:
        if self._full_log_window is not None:
            try:
                self._full_log_window.destroy()
            except Exception:
                pass
        self._full_log_window = None
        self._full_log_list = None

    def _append_full_log_row(self, entry: _LogEntry) -> None:
        if self._full_log_list is None:
            return

        icon = _LEVEL_ICONS.get(entry.level, _LEVEL_ICONS["info"])
        color = theme.status_color(entry.level) if entry.level in _KNOWN_LEVELS else theme.TEXT_SECONDARY

        row = ctk.CTkFrame(self._full_log_list, fg_color="transparent")
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row, text=icon, font=theme.body_font(12, "bold"), text_color=color, width=18).pack(side="left")
        ctk.CTkLabel(
            row,
            text=f"{entry.timestamp}  {entry.message}",
            font=theme.mono_font(11),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
            justify="left",
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Auto-scroll to the newest entry.
        try:
            self._full_log_list._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass