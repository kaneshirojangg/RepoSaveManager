"""Shared helper functions used across the application."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_SAVE_PREFIX = "REPO_SAVE_"


def is_repo_save_folder(folder_name: str) -> bool:
    return folder_name.startswith(REPO_SAVE_PREFIX)


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "Unknown"
    day = value.day
    hour = value.hour % 12 or 12
    minute = value.minute
    second = value.second
    period = "AM" if value.hour < 12 else "PM"
    return f"{value.strftime('%b')} {day}, {value.year} — {hour}:{minute:02d}:{second:02d} {period}"


def format_bytes(size: int | None) -> str:
    if size is None:
        return "Unknown"
    if size < 1024:
        return f"{size} B"

    units = ["KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        value /= 1024.0
        if value < 1024.0 or unit == units[-1]:
            return f"{value:.1f} {unit}"
    return f"{size} B"


def safe_makedirs(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def has_read_access(path: Path) -> bool:
    return os.access(path, os.R_OK)


def has_write_access(path: Path) -> bool:
    return os.access(path, os.W_OK)


def normalize_path(path_value: str | Path) -> Path:
    return Path(path_value).expanduser().resolve()


def open_folder_in_file_manager(folder_path: str | Path) -> bool:
    """Open a folder in the user's *actual default* file manager.

    Single shared implementation used by both Dashboard and SetupWizard —
    previously Dashboard had its own near-duplicate copy of this logic, and
    SetupWizard incorrectly called into Dashboard's private copy passing
    itself (a SetupWizard, not a Dashboard) as `self`, which crashed with an
    AttributeError on the logging line every time (silently, since Tkinter
    swallows callback exceptions). Consolidating to one function here fixes
    that crash and guarantees both entry points behave identically.

    Windows previously shelled out to `subprocess.Popen(["explorer", ...])`,
    which depends on `explorer` being resolvable via PATH at runtime — not
    guaranteed inside a PyInstaller-frozen exe — and is known to silently
    fall back to Explorer's default view (Quick Access / This PC) instead of
    the requested folder when that resolution or argument parsing goes
    slightly wrong. That fallback is what looks like "a different file
    manager opened" to a user. `os.startfile()` is the OS-native way to
    invoke the folder's actually-registered default handler and avoids the
    PATH/argument-parsing issues entirely.

    Returns True if the folder manager launch was attempted successfully,
    False if the folder was invalid or the launch failed (an error dialog
    is shown in both failure cases).
    """
    # Import here to avoid circular imports at module import time.
    from src.ui.dialogs import show_error_dialog

    folder = Path(folder_path).expanduser()
    try:
        folder = folder.resolve()
    except Exception:
        # resolve() can fail for non-existing paths; keep expanded path.
        pass

    if not folder.exists() or not folder.is_dir():
        show_error_dialog(
            "Folder Not Found",
            "The configured folder does not exist or is not a directory.",
            str(folder),
        )
        return False

    try:
        if sys.platform.startswith("win"):
            # os.startfile uses ShellExecute under the hood, which resolves
            # to whatever file manager Windows actually has registered as
            # the default handler for directories — no PATH lookup, no
            # argument-quoting ambiguity, no silent fallback to the wrong
            # view.
            os.startfile(str(folder))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            opener = shutil.which("open")
            if not opener:
                raise RuntimeError("open is not available")
            subprocess.Popen([opener, str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("linux"):
            opener = shutil.which("xdg-open")
            if not opener:
                raise RuntimeError("xdg-open is not available")
            subprocess.Popen([opener, str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["xdg-open", str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as exc:
        show_error_dialog("Open Folder Failed", "Unable to open the configured folder.", str(exc))
        return False


def browse_for_directory(title: str, initial_dir: str | Path | None = None) -> str | None:
    initial_path = Path(initial_dir).expanduser().resolve() if initial_dir else None

    if sys.platform.startswith("linux"):
        chooser_command: list[str] | None = None
        if shutil.which("zenity"):
            chooser_command = ["zenity", "--file-selection", "--directory", "--title", title]
            if initial_path is not None:
                chooser_command.extend(["--filename", f"{initial_path}/"])
        elif shutil.which("kdialog"):
            chooser_command = ["kdialog", "--getexistingdirectory", str(initial_path or Path.home()), "--title", title]

        if chooser_command is not None:
            result = subprocess.run(chooser_command, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                selected = result.stdout.strip()
                return selected or None
            return None

    try:
        from tkinter import Tk, filedialog
    except Exception:
        return None

    root = Tk()
    root.withdraw()
    try:
        selected = filedialog.askdirectory(title=title, initialdir=str(initial_path) if initial_path else None, parent=root)
    finally:
        root.destroy()
    return selected or None