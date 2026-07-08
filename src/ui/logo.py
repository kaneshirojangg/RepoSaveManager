"""Shared logo and window icon helpers for Repo Save Manager."""

from __future__ import annotations

from pathlib import Path
from tkinter import PhotoImage

from src.utils.constants import ASSETS_DIR

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - runtime fallback for environments without the dependency
    import tkinter as ctk  # type: ignore[no-redef]


LOGO_PATH = ASSETS_DIR / "images" / "reposavemanager.png"


def load_logo_image(size: tuple[int, int] = (56, 56)):
    try:
        from PIL import Image
    except ImportError:
        return PhotoImage(file=str(LOGO_PATH))

    image = Image.open(LOGO_PATH)
    if hasattr(ctk, "CTkImage"):
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
    return PhotoImage(file=str(LOGO_PATH))


def load_window_icon() -> PhotoImage:
    return PhotoImage(file=str(LOGO_PATH))