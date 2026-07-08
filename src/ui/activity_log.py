"""Activity log widget for dashboard events.

Requirement: show the taxman image for every new output appended.
Each entry should visually read like:

[image]: > [Output]
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - runtime fallback for environments without the dependency
    import tkinter as ctk  # type: ignore[no-redef]

    ctk.CTkFrame = ctk.Frame  # type: ignore[attr-defined]
    ctk.CTkLabel = ctk.Label  # type: ignore[attr-defined]
    ctk.CTkScrollableFrame = ctk.Frame  # type: ignore[attr-defined]

from src.ui import theme


@dataclass(slots=True)
class ActivityEntry:
    timestamp: str
    level: str
    message: str


class ActivityLog(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass | None = None) -> None:
        super().__init__(
            master,
            fg_color=theme.BG_SECONDARY,
            corner_radius=theme.PANEL_CORNER_RADIUS,
            border_width=1,
            border_color=theme.BORDER,
        )

        self._entries: list[ActivityEntry] = []
        self._row_widgets: list[ctk.CTkFrame] = []

        # Load taxman image once and keep reference to prevent GC.
        self._taxman_img = self._load_taxman_image(size=(26, 26))

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            header,
            text="ACTIVITY LOG",
            font=theme.header_font(15),
            text_color=theme.TEXT_PRIMARY,
        ).pack(side="left")

        self.count_label = ctk.CTkLabel(
            header,
            text="0 events",
            font=theme.body_font(11),
            text_color=theme.TEXT_MUTED,
        )
        self.count_label.pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(
            self,
            height=190,
            fg_color=theme.BG_INPUT,
            corner_radius=theme.CARD_CORNER_RADIUS,
        )
        self.scroll.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        # Ensure the container stretches.
        try:
            self.scroll.grid_columnconfigure(0, weight=1)
        except Exception:
            pass

    def _load_taxman_image(self, size: tuple[int, int] = (26, 26)):
        """Load the taxman image used for each appended activity row."""

        from src.utils.constants import ASSETS_DIR

        taxman_path = ASSETS_DIR / "images" / "taxmann.png"

        try:
            from PIL import Image
        except ImportError:
            from tkinter import PhotoImage

            return PhotoImage(file=str(taxman_path))

        image = Image.open(taxman_path)
        if hasattr(ctk, "CTkImage"):
            return ctk.CTkImage(light_image=image, dark_image=image, size=size)

        from tkinter import PhotoImage

        return PhotoImage(file=str(taxman_path))

    def append(self, timestamp: str, level: str, message: str) -> None:
        self._entries.append(ActivityEntry(timestamp=timestamp, level=level, message=message))

        # Row container: taxman avatar + output line.
        row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row.grid(row=len(self._row_widgets), column=0, sticky="ew", padx=12, pady=(8, 0))
        try:
            row.grid_columnconfigure(1, weight=1)
        except Exception:
            pass

        ctk.CTkLabel(row, image=self._taxman_img, text="").grid(
            row=0, column=0, sticky="nw", padx=(0, 10)
        )

        # Colorize by level but keep formatting requested.
        text_color = {
            "success": theme.SUCCESS,
            "warning": theme.WARNING,
            "error": theme.DANGER,
            "info": theme.TEXT_SECONDARY,
        }.get(level, theme.TEXT_PRIMARY)

        ctk.CTkLabel(
            row,
            text=f"[{timestamp}]  >  {message}",
            font=theme.mono_font(12),
            text_color=text_color,
            justify="left",
            anchor="w",
            wraplength=520,
        ).grid(row=0, column=1, sticky="ew")

        self._row_widgets.append(row)

        # Scroll to end when possible.
        try:
            self.scroll._parent_canvas.yview_moveto(1.0)  # type: ignore[attr-defined]
        except Exception:
            pass

        self._update_count()

    def clear(self) -> None:
        self._entries.clear()
        for row in self._row_widgets:
            try:
                row.destroy()
            except Exception:
                pass
        self._row_widgets.clear()
        self._update_count()

    def _update_count(self) -> None:
        count = len(self._entries)
        self.count_label.configure(text=f"{count} event{'s' if count != 1 else ''}")

