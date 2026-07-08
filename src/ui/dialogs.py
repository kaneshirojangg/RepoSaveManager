"""User-facing dialogs for confirmations, errors, and restore prompts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - runtime fallback for environments without the dependency
    import tkinter as tk  # type: ignore[no-redef]
    from tkinter import messagebox

    # Minimal customtkinter-like shims so widgets can be constructed even when
    # customtkinter isn't installed. In particular, this strips CTk-style kwargs
    # (fg_color/hover_color/corner_radius/etc.) that tkinter Button/Frame don't
    # understand.
    class _CTkShim:
        _UNSUPPORTED = {
            "fg_color",
            "corner_radius",
            "border_width",
            "border_color",
            "hover_color",
            "text_color",
            "placeholder_text",
            "width",
            "height",
        }

        @classmethod
        def _strip(cls, kwargs: dict[str, object]) -> dict[str, object]:
            return {k: v for k, v in kwargs.items() if k not in cls._UNSUPPORTED}

    class CTkToplevel(_CTkShim, tk.Toplevel):
        pass

    class CTkFrame(_CTkShim, tk.Frame):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class CTkLabel(_CTkShim, tk.Label):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class CTkButton(_CTkShim, tk.Button):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class _CtkModule:
        CTkToplevel = CTkToplevel
        CTkFrame = CTkFrame
        CTkLabel = CTkLabel
        CTkButton = CTkButton

    ctk = _CtkModule()  # type: ignore[assignment]
else:
    from tkinter import messagebox


from src.ui import theme
from src.ui.logo import load_window_icon
from src.ui.logo import load_logo_image



def _load_taxman_image(size: tuple[int, int] = (96, 96)):
    """Load the taxman image for the YouDied dialog.

    Uses PIL if available (matching load_logo_image), otherwise falls back
    to a tkinter PhotoImage.
    """

    from src.utils.constants import ASSETS_DIR

    taxman_path = ASSETS_DIR / "images" / "taxmann.png"

    try:
        from PIL import Image
    except ImportError:
        # PhotoImage doesn't handle resize; but it will at least display.
        from tkinter import PhotoImage

        return PhotoImage(file=str(taxman_path))

    image = Image.open(taxman_path)

    if hasattr(ctk, "CTkImage"):
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)

    from tkinter import PhotoImage

    return PhotoImage(file=str(taxman_path))



@dataclass(slots=True)
class RestoreDialogResult:
    accepted: bool = False


def show_error_dialog(title: str, message: str, details: str | None = None) -> None:
    if details:
        message = f"{message}\n\n{details}"
    messagebox.showerror(title, message)


def show_info_dialog(title: str, message: str) -> None:
    messagebox.showinfo(title, message)


def ask_confirmation(title: str, message: str) -> bool:
    return messagebox.askyesno(title, message)


class YouDiedDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master: ctk.CTkBaseClass | None,
        folder_id: str,
        user_label: str | None,
        last_backup_timestamp: datetime | None,
    ) -> None:
        super().__init__(master)
        self.result = RestoreDialogResult(False)
        self.title("Restore Save?")
        self.geometry("720x460")
        self.minsize(640, 420)
        self.configure(fg_color=theme.BG_PRIMARY)
        try:
            self.iconphoto(True, load_window_icon())
        except Exception:
            pass
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._decline)

        outer = ctk.CTkFrame(
            self,
            fg_color=theme.DANGER_BG,
            corner_radius=theme.PANEL_CORNER_RADIUS,
            border_width=1,
            border_color=theme.DANGER,
        )
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        taxman_img = _load_taxman_image((96, 96))
        # Keep a reference to prevent GC.
        self._taxman_img = taxman_img

        ctk.CTkLabel(outer, image=taxman_img, text="").pack(pady=(24, 6))

        ctk.CTkLabel(
            outer,
            text="🫵😂👎",
            font=theme.header_font(34),
            text_color=theme.DANGER,
        ).pack(pady=(0, 6))


        ctk.CTkLabel(
            outer,
            text="The squad wiped before the next checkpoint. This save was deleted.",
            font=theme.body_font(13),
            text_color=theme.TEXT_SECONDARY,
        ).pack(pady=(0, 24))

        info_card = ctk.CTkFrame(outer, fg_color=theme.BG_CARD, corner_radius=theme.CARD_CORNER_RADIUS)
        info_card.pack(fill="x", padx=48, pady=(0, 24))

        rows = [
            ("Save", user_label or folder_id),
            ("Folder ID", folder_id),
            (
                "Last backup",
                last_backup_timestamp.strftime("%b %d, %Y \u2014 %I:%M:%S %p")
                if last_backup_timestamp
                else "Unknown",
            ),
        ]
        for label, value in rows:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=8)
            ctk.CTkLabel(row, text=label.upper(), font=theme.body_font(11), text_color=theme.TEXT_MUTED, width=110, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=theme.body_font(13, "bold"), text_color=theme.TEXT_PRIMARY, anchor="w").pack(side="left", fill="x", expand=True)

        button_row = ctk.CTkFrame(outer, fg_color="transparent")
        button_row.pack(pady=(4, 32), padx=48, fill="x")
        ctk.CTkButton(
            button_row,
            text="🔄⏪🧰",

            command=self._accept,
            fg_color=theme.ACCENT,
            hover_color=theme.ACCENT_HOVER,
            text_color=theme.TEXT_ON_ACCENT,
            font=theme.header_font(14),
            corner_radius=theme.BUTTON_CORNER_RADIUS,
            height=44,
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(
            button_row,
            text="🚫❌🙅",

            command=self._decline,
            fg_color="transparent",
            hover_color=theme.BG_CARD_HOVER,
            border_width=1,
            border_color=theme.TEXT_SECONDARY,
            text_color=theme.TEXT_SECONDARY,
            font=theme.body_font(14),
            corner_radius=theme.BUTTON_CORNER_RADIUS,
            height=44,
        ).pack(side="right", expand=True, fill="x", padx=(10, 0))

    def _accept(self) -> None:
        self.result.accepted = True
        self.destroy()

    def _decline(self) -> None:
        self.result.accepted = False
        self.destroy()