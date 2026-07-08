"""Main dashboard layout for Repo Save Manager."""

from __future__ import annotations


import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - runtime fallback for environments without the dependency
    import tkinter as tk

    # Provide a minimal customtkinter-like surface so the rest of this file
    # can be imported/constructed even when customtkinter isn't installed.
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

    class CTkFrame(_CTkShim, tk.Frame):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class CTkLabel(_CTkShim, tk.Label):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class CTkButton(_CTkShim, tk.Button):
        def __init__(self, master=None, **kwargs):
            # tkinter Button doesn't know hover_color/corner_radius/fg_color/text_color
            super().__init__(master, **self._strip(kwargs))

    class CTkScrollableFrame(_CTkShim, tk.Frame):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    class CTkEntry(_CTkShim, tk.Entry):
        def __init__(self, master=None, **kwargs):
            super().__init__(master, **self._strip(kwargs))

    # Expose a module-like object matching `customtkinter` API used below.
    class _CtkModule:
        CTkFrame = CTkFrame
        CTkLabel = CTkLabel
        CTkButton = CTkButton
        CTkScrollableFrame = CTkScrollableFrame
        CTkEntry = CTkEntry
        CTkBaseClass = tk.Misc

    ctk = _CtkModule()  # type: ignore[assignment]

from src.managers.backup_manager import BackupManager

from src.managers.monitor_manager import MonitorEvent, MonitorManager
from src.managers.restore_manager import RestoreManager
from src.managers.save_manager import SaveManager
from src.managers.settings_manager import SettingsManager
from src.models.save_model import SaveModel
from src.services.logger_service import get_logger
from src.ui.dialogs import YouDiedDialog, ask_confirmation, show_error_dialog, show_info_dialog
from src.ui.activity_log import ActivityLog
from src.ui.logo import load_logo_image
from src.ui import theme
from src.utils.helpers import format_bytes, format_datetime





# Action-bar button roles -> theme styling. Kept as plain dicts of CTkButton
# kwargs so every button's color language stays centralized and consistent.
_BUTTON_STYLES: dict[str, dict[str, Any]] = {
    "primary": dict(
        fg_color=theme.ACCENT,
        hover_color=theme.ACCENT_HOVER,
        text_color=theme.TEXT_ON_ACCENT,
        font=theme.body_font(13, "bold"),
    ),
    "success": dict(
        fg_color=theme.SUCCESS,
        hover_color="#2FB86E",
        text_color="#06180F",
        font=theme.body_font(13, "bold"),
    ),
    "danger": dict(
        fg_color=theme.DANGER,
        hover_color="#C23B3B",
        text_color=theme.TEXT_PRIMARY,
        font=theme.body_font(13, "bold"),
    ),
    "outline": dict(
        fg_color="transparent",
        hover_color=theme.BG_CARD_HOVER,
        text_color=theme.TEXT_SECONDARY,
        border_width=1,
        border_color=theme.BORDER,
        font=theme.body_font(13),
    ),
    "outline_warning": dict(
        fg_color="transparent",
        hover_color=theme.BG_CARD_HOVER,
        text_color=theme.WARNING,
        border_width=1,
        border_color=theme.WARNING,
        font=theme.body_font(13),
    ),
}

_ACTION_DEFINITIONS: list[tuple[str, str, str]] = [
    # (icon+label, style key, callback attribute name resolved at build time)
    ("\U0001F504  Refresh Saves", "outline", "refresh_saves_action"),
    ("\U0001F4C2  Open Save Folder", "outline", "open_save_folder"),
    ("\U0001F5C3  Open Backup Folder", "outline", "open_backup_folder"),
    ("\U0001F5D1  Delete Backup", "danger", "delete_backup"),
    ("\u2699  Settings", "outline", "open_settings"),
    ("\u2716  Exit", "outline", "exit_app"),
]



_STAT_DEFINITIONS: list[tuple[str, str, str]] = [
    # (label, icon, status key used for accent color)
    ("Total saves", theme.ICON_SAVES, "info"),
    ("Backups created", theme.ICON_BACKUPS_NEW, "success"),
    ("Backups updated", theme.ICON_BACKUPS_UPDATED, "warning"),
    ("Deletions detected", theme.ICON_DELETIONS, "danger"),
    ("Restores performed", theme.ICON_RESTORES, "success"),
    ("Runtime", theme.ICON_RUNTIME, "info"),
]


    

# If customtkinter is unavailable, `ctk` is tkinter; tkinter doesn't accept CTk-style kwargs.
# The compatibility mixin above ensures constructor-time kwargs are stripped, but the remaining
# CTkFrame instantiations still pass fg_color/corner_radius/etc. defensively strip those kwargs
# at call sites for tkinter fallback.
if getattr(ctk.CTkFrame, '__module__', '').startswith('tkinter'):
    pass


class Dashboard(ctk.CTkFrame):

    def __init__(

        self,
        master: ctk.CTkBaseClass | None = None,
        settings_manager: SettingsManager | None = None,
        save_manager: SaveManager | None = None,
        backup_manager: BackupManager | None = None,
        restore_manager: RestoreManager | None = None,
        monitor_manager: MonitorManager | None = None,
        on_open_settings: Callable[[], None] | None = None,
    ) -> None:
        # customtkinter-only kwargs like fg_color break on tkinter fallback.
        if 'customtkinter' in sys.modules:
            try:
                super().__init__(master, fg_color=theme.BG_PRIMARY)
            except Exception:
                super().__init__(master)
        else:
            super().__init__(master)


        self.settings_manager = settings_manager or SettingsManager()
        self.save_manager = save_manager or SaveManager(self.settings_manager)
        settings = self.settings_manager.load()
        self.backup_manager = backup_manager or BackupManager(settings.backup_folder)
        self.restore_manager = restore_manager or RestoreManager(self.backup_manager, settings.save_folder)
        self.monitor_manager = monitor_manager or MonitorManager(self.save_manager, self.backup_manager, self.restore_manager)
        self.on_open_settings = on_open_settings
        self.logger = get_logger(self.__class__.__name__)
        self.saves: list[SaveModel] = []

        self.selected_save: SaveModel | None = None
        self._card_buttons: dict[str, Any] = {}
        self._pending_restore_folder_id: str | None = None
        self._pending_outdated_folder_id: str | None = None
        self._alert_mode: str | None = None
        self._logo_image = load_logo_image((56, 56))
        self._build_layout()
        self.refresh_saves(log_activity=False)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        try:
            self.pack(fill="both", expand=True)
        except Exception:
            pass

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=4)
        self.grid_columnconfigure(2, weight=3)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        self._build_header()
        self._build_alert_bar()

        left_panel = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER) if hasattr(ctk.CTkFrame, '__mro__') else ctk.CTkFrame(self)
        center_panel = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER) if hasattr(ctk.CTkFrame, '__mro__') else ctk.CTkFrame(self)
        right_panel = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER) if hasattr(ctk.CTkFrame, '__mro__') else ctk.CTkFrame(self)

        left_panel.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=10)
        center_panel.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
        right_panel.grid(row=2, column=2, sticky="nsew", padx=(10, 20), pady=10)

        self._build_left_panel(left_panel)
        self._build_center_panel(center_panel)
        self._build_right_panel(right_panel)

        action_bar = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER)
        action_bar.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 10))
        self._build_action_bar(action_bar)


        self.activity_log = ActivityLog(self)
        self.activity_log.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))
        self.grid_rowconfigure(4, weight=1)

    def _build_header(self) -> None:
        try:
            header = ctk.CTkFrame(self, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER)
        except TypeError:
            header = ctk.CTkFrame(self)

        header.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(0, weight=0)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=0)

        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.grid(row=0, column=0, sticky="w", padx=16, pady=16)
        ctk.CTkLabel(brand_frame, text="", image=self._logo_image).pack(side="left", padx=(0, 12))
        title_stack = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_stack.pack(side="left")
        self.title_label = ctk.CTkLabel(
            title_stack,
            text="REPO SAVE MANAGER",
            font=theme.header_font(24),
            text_color=theme.ACCENT,
        )
        self.title_label.pack(anchor="w")

        pill = ctk.CTkFrame(title_stack, fg_color=theme.BG_CARD, corner_radius=theme.PILL_CORNER_RADIUS)
        pill.pack(anchor="w", pady=(4, 0))

        monitor_stack = ctk.CTkFrame(pill, fg_color="transparent")
        monitor_stack.pack(fill="both", expand=True, padx=(10, 12), pady=8)

        top_row = ctk.CTkFrame(monitor_stack, fg_color="transparent")
        top_row.pack(anchor="w", fill="x")
        self.monitor_dot_label = ctk.CTkLabel(
            top_row,
            text=theme.ICON_DOT,
            font=theme.body_font(12),
            text_color=theme.NEUTRAL,
            width=14,
        )
        self.monitor_dot_label.pack(side="left", padx=(0, 6), pady=4)
        self.monitor_status_label = ctk.CTkLabel(
            top_row,
            text="Monitoring Idle",
            font=theme.body_font(12),
            text_color=theme.TEXT_SECONDARY,
        )
        self.monitor_status_label.pack(side="left", padx=(0, 0), pady=4)

        monitor_buttons = ctk.CTkFrame(monitor_stack, fg_color="transparent")
        monitor_buttons.pack(anchor="w", fill="x", pady=(6, 0))

        ctk.CTkButton(
            monitor_buttons,
            text="Start",
            command=self.start_monitoring,
            corner_radius=theme.BUTTON_CORNER_RADIUS,
            height=30,
            **_BUTTON_STYLES["success"],
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            monitor_buttons,
            text="Stop",
            command=self.stop_monitoring,
            corner_radius=theme.BUTTON_CORNER_RADIUS,
            height=30,
            **_BUTTON_STYLES["outline_warning"],
        ).pack(side="left", padx=(8, 0))


        right_stack = ctk.CTkFrame(header, fg_color="transparent")
        right_stack.grid(row=0, column=2, sticky="e", padx=16)
        self.time_label = ctk.CTkLabel(right_stack, text=f"{theme.ICON_CLOCK} {self._now_text()}", font=theme.body_font(14), text_color=theme.TEXT_SECONDARY)
        self.time_label.pack(side="left", padx=(0, 12))
        ctk.CTkButton(
            right_stack,
            text=theme.ICON_SETTINGS,
            width=36,
            height=36,
            corner_radius=18,
            fg_color=theme.BG_CARD,
            hover_color=theme.BG_CARD_HOVER,
            text_color=theme.TEXT_PRIMARY,
            command=self.open_settings,
        ).pack(side="left")

    def _build_alert_bar(self) -> None:
        self.alert_bar = ctk.CTkFrame(self, fg_color=theme.DANGER_BG, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.DANGER)
        self.alert_bar.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 10))
        self.alert_bar.grid_columnconfigure(0, weight=1)
        self.alert_bar.grid_columnconfigure(1, weight=0)
        self.alert_bar.grid_columnconfigure(2, weight=0)

        icon_and_text = ctk.CTkFrame(self.alert_bar, fg_color="transparent")
        icon_and_text.grid(row=0, column=0, sticky="ew", padx=16, pady=12)
        self.alert_icon_label = ctk.CTkLabel(icon_and_text, text="\u2620", font=theme.header_font(18), text_color=theme.DANGER)
        self.alert_icon_label.pack(side="left", padx=(0, 10))
        self.alert_label = ctk.CTkLabel(icon_and_text, text="", anchor="w", font=theme.body_font(13, "bold"), text_color=theme.TEXT_PRIMARY, justify="left")
        self.alert_label.pack(side="left", fill="x", expand=True)

        # Generic action button: its text/command/style are swapped depending on
        # which alert is currently showing (deleted save vs. outdated backup).
        self.alert_action_button = ctk.CTkButton(
            self.alert_bar, text="Restore Latest Backup", command=self._restore_pending_deleted_save,
            corner_radius=theme.BUTTON_CORNER_RADIUS, **_BUTTON_STYLES["primary"],
        )
        self.alert_action_button.grid(row=0, column=1, padx=(8, 8), pady=12)
        self.alert_dismiss_button = ctk.CTkButton(
            self.alert_bar, text="Dismiss", command=self._dismiss_alert,
            corner_radius=theme.BUTTON_CORNER_RADIUS, **_BUTTON_STYLES["outline"],
        )
        self.alert_dismiss_button.grid(row=0, column=2, padx=(0, 16), pady=12)
        self.alert_bar.grid_remove()

    def _build_left_panel(self, panel: ctk.CTkFrame) -> None:
        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 8))
        ctk.CTkLabel(header, text=f"{theme.ICON_SAVES}  DETECTED SAVES", font=theme.header_font(16), text_color=theme.TEXT_PRIMARY).pack(side="left")
        self.saves_count_label = ctk.CTkLabel(header, text="0", font=theme.body_font(12, "bold"), text_color=theme.ACCENT)
        self.saves_count_label.pack(side="right")

        self.save_list = ctk.CTkScrollableFrame(panel, height=420, fg_color="transparent")
        self.save_list.pack(fill="both", expand=True, padx=12, pady=(0, 16))

    def _build_center_panel(self, panel: ctk.CTkFrame) -> None:
        ctk.CTkLabel(panel, text="SELECTED SAVE DETAILS", font=theme.header_font(16), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(16, 8))
        # Scrollable so the info rows + action buttons (Create Backup / Load Backup)
        # stay reachable even when the panel is shorter than the content — previously
        # this was a plain CTkFrame with no scroll wheel support.
        self.details_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.details_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._render_empty_details()

    def _render_empty_details(self) -> None:
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        placeholder = ctk.CTkFrame(self.details_frame, fg_color=theme.BG_CARD, corner_radius=theme.CARD_CORNER_RADIUS)
        placeholder.pack(fill="x", pady=8)
        ctk.CTkLabel(
            placeholder,
            text="Select a save from the left to see its details.",
            font=theme.body_font(13),
            text_color=theme.TEXT_SECONDARY,
        ).pack(padx=18, pady=28)

    def _build_right_panel(self, panel: ctk.CTkFrame) -> None:
        paths_card = ctk.CTkFrame(panel, fg_color=theme.BG_CARD, corner_radius=theme.CARD_CORNER_RADIUS)
        paths_card.pack(fill="x", padx=16, pady=(16, 16))
        ctk.CTkLabel(paths_card, text="PATHS", font=theme.body_font(11, "bold"), text_color=theme.TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 4))
        self.save_path_label = ctk.CTkLabel(paths_card, text="Save: -", font=theme.body_font(11), text_color=theme.TEXT_SECONDARY, anchor="w", justify="left", wraplength=240)
        self.save_path_label.pack(anchor="w", padx=14, pady=2)
        self.backup_path_label = ctk.CTkLabel(paths_card, text="Backup: -", font=theme.body_font(11), text_color=theme.TEXT_SECONDARY, anchor="w", justify="left", wraplength=240)
        self.backup_path_label.pack(anchor="w", padx=14, pady=(2, 10))
        self._refresh_paths_footer()


    def _refresh_paths_footer(self) -> None:
        if not hasattr(self, "save_path_label"):
            return
        try:
            settings = self.settings_manager.load()
            self.save_path_label.configure(text=f"Save: {settings.save_folder}")
            self.backup_path_label.configure(text=f"Backup: {settings.backup_folder}")
        except Exception:
            pass

    def _build_action_bar(self, panel: ctk.CTkFrame) -> None:
        callbacks: dict[str, Callable[[], None]] = {
            "create_backup": self.create_backup,
            "load_backup": self.load_backup,
            "refresh_saves_action": lambda: self.refresh_saves(log_activity=True),
            "start_monitoring": self.start_monitoring,
            "stop_monitoring": self.stop_monitoring,
            "open_save_folder": self.open_save_folder,
            "open_backup_folder": self.open_backup_folder,
            "delete_backup": self.delete_backup,
            "open_settings": self.open_settings,
            "exit_app": self.exit_app,
        }
        for column, (label, style_key, callback_name) in enumerate(_ACTION_DEFINITIONS):
            button = ctk.CTkButton(
                panel,
                text=label,
                command=callbacks[callback_name],
                corner_radius=theme.BUTTON_CORNER_RADIUS,
                height=38,
                **_BUTTON_STYLES[style_key],
            )
            button.grid(row=0, column=column, padx=6, pady=10, sticky="nsew")
            panel.grid_columnconfigure(column, weight=1)

    # ------------------------------------------------------------------
    # Save list / cards
    # ------------------------------------------------------------------
    def refresh_saves(self, log_activity: bool = True) -> None:
        self.saves = self.save_manager.discover_from_settings(self.backup_manager)

        for widget in self.save_list.winfo_children():
            widget.destroy()
        self._card_buttons.clear()

        for save in self.saves:
            self._add_save_card(save)

        if self.saves and self.selected_save is None:
            self.select_save(self.saves[0].folder_id)
        elif self.selected_save:
            refreshed = self.save_manager.get_save_by_folder_id(self.saves, self.selected_save.folder_id)
            if refreshed:
                self.selected_save = refreshed
                self._render_details(refreshed)
            else:
                self.selected_save = None
                self._render_empty_details()
        self._refresh_paths_footer()

        self._update_status_alert()
        if hasattr(self, "saves_count_label"):
            self.saves_count_label.configure(text=str(len(self.saves)))
        if log_activity:
            self.activity_log.append(self._now_text(), "info", f"Refreshed {len(self.saves)} save folder(s).")

    def select_save(self, folder_id: str) -> None:
        result = self.save_manager.select_save(self.saves, folder_id)
        self.saves = result.all_saves
        self.selected_save = result.selected_save
        if self.selected_save:
            self._render_details(self.selected_save)
        self._refresh_card_selection()

    def _status_for(self, save: SaveModel) -> tuple[str, str]:
        """Return (status_key, label) describing a save's backup health."""
        if save.is_deleted:
            if save.backup_available:
                return "danger", "Deleted \u2014 backup ready"
            return "danger", "Deleted \u2014 no backup"
        if not save.has_backup:
            return "danger", "No backup"
        if save.backup_timestamp and save.mtime and save.backup_timestamp < save.mtime:
            return "warning", "Backup outdated"
        return "success", "Backed up"

    def _add_save_card(self, save: SaveModel) -> None:
        status_key, status_text = self._status_for(save)
        accent = theme.status_color(status_key)

        card = ctk.CTkFrame(
            self.save_list,
            fg_color=theme.BG_CARD,
            corner_radius=theme.CARD_CORNER_RADIUS,
            border_width=2,
            border_color=theme.ACCENT if save.is_selected else theme.BORDER,
        )
        card.pack(fill="x", padx=6, pady=6)
        card.grid_columnconfigure(1, weight=1)

        strip = ctk.CTkFrame(card, fg_color=accent, corner_radius=0, width=6)
        strip.grid(row=0, column=0, sticky="ns", padx=(0, 0), pady=0)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=0, column=1, sticky="nsew", padx=(12, 12), pady=10)

        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")
        title_label = ctk.CTkLabel(
            top_row,
            text=save.display_name,
            font=theme.body_font(14, "bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="w",
            justify="left",
            wraplength=220,
        )
        title_label.pack(side="left", fill="x", expand=True)

        # Badge lives on its own row below the title instead of squeezed
        # inline next to it, so a long save name no longer pushes the
        # status badge (e.g. "No backup") out of view / off the card.
        badge_row = ctk.CTkFrame(content, fg_color="transparent")
        badge_row.pack(fill="x", pady=(6, 0))
        badge = ctk.CTkFrame(badge_row, fg_color=theme.status_bg(status_key), corner_radius=theme.BADGE_CORNER_RADIUS)
        badge.pack(side="left")
        ctk.CTkLabel(badge, text=f"{theme.ICON_DOT} {status_text}", font=theme.body_font(10, "bold"), text_color=accent).pack(padx=8, pady=3)

        subtitle = ctk.CTkLabel(
            content,
            text=f"{theme.ICON_CLOCK} {format_datetime(save.mtime)}    {theme.ICON_SIZE} {format_bytes(save.size)}",
            font=theme.body_font(11),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        )
        subtitle.pack(fill="x", pady=(6, 0))

        select_button = ctk.CTkButton(
            content,
            text="Selected" if save.is_selected else "Select",
            command=lambda folder_id=save.folder_id: self.select_save(folder_id),
            corner_radius=theme.BUTTON_CORNER_RADIUS,
            height=28,
            **(_BUTTON_STYLES["primary"] if save.is_selected else _BUTTON_STYLES["outline"]),
        )
        select_button.pack(fill="x", pady=(10, 0))

        # Clicking anywhere on the card (not just the button) selects it.
        for widget in (card, strip, content, top_row, badge_row, subtitle):
            widget.bind("<Button-1>", lambda _e, folder_id=save.folder_id: self.select_save(folder_id))

        self._card_buttons[save.folder_id] = (card, badge, select_button, title_label)


    def _refresh_card_selection(self) -> None:
        for save in self.saves:
            card_bundle = self._card_buttons.get(save.folder_id)
            if not card_bundle:
                continue
            # NOTE: _card_buttons stores a 4-tuple (card, badge, select_button, title_label).
            # This used to unpack only 3 values, which raised
            # "ValueError: too many values to unpack (expected 3)" the moment a real
            # save folder existed and select_save() -> _refresh_card_selection() ran.
            # That's what was silently killing the app a few seconds after launch.
            card, _badge, select_button, _title_label = card_bundle
            if save.is_selected:
                card.configure(border_color=theme.ACCENT)
                select_button.configure(text="Selected", **_BUTTON_STYLES["primary"])
            else:
                card.configure(border_color=theme.BORDER)
                select_button.configure(text="Select", **_BUTTON_STYLES["outline"])

    # ------------------------------------------------------------------
    # Detail panel
    # ------------------------------------------------------------------
    def _render_details(self, save: SaveModel) -> None:
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        status_key, status_text = self._status_for(save)
        accent = theme.status_color(status_key)

        header_card = ctk.CTkFrame(self.details_frame, fg_color=theme.BG_CARD, corner_radius=theme.CARD_CORNER_RADIUS)
        header_card.pack(fill="x", pady=(0, 10))

        # Title/edit row (cosmetic user label only).
        self._selected_title_bundle = {
            "folder_id": save.folder_id,
            "edit_mode": False,
            "prev_label": save.user_label or "",
        }

        title_row = ctk.CTkFrame(header_card, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(14, 2))
        title_row.grid_columnconfigure(0, weight=1)
        title_row.grid_columnconfigure(1, weight=0)

        pencil_icon = "✎"
        max_label = 60

        def _truncate_for_display(text: str) -> str:
            if len(text) <= max_label:
                return text
            return text[: max_label - 1] + "…"

        def _get_current_label_for_entry() -> str:
            # Spec: empty if none was set.
            return (save.user_label or "") if (save.user_label or "").strip() else ""

        def _apply_view_mode(current_label_text: str) -> None:
            # Clear old widgets in row.
            for w in title_row.winfo_children():
                w.destroy()

            label_value = current_label_text
            # Title row shows label text if set; otherwise show raw folder id.
            display_text = label_value if (label_value or "").strip() else save.folder_id

            # Truncate for display, but keep full value in tooltip (if supported).
            truncated = _truncate_for_display(display_text)
            title_lbl = ctk.CTkLabel(
                title_row,
                text=truncated,
                font=theme.header_font(18),
                text_color=theme.TEXT_PRIMARY,
                anchor="w",
                justify="left",
                wraplength=520,
            )
            title_lbl.grid(row=0, column=0, sticky="w")

            # Optional tooltip: CTkLabel has no official tooltip, but we can still bind a hover dialog.
            full_title = display_text
            def _on_enter(_e):
                try:
                    title_lbl.configure(text=truncated)  # keep
                except Exception:
                    pass

            def _on_leave(_e):
                try:
                    title_lbl.configure(text=truncated)
                except Exception:
                    pass

            title_lbl.bind("<Enter>", _on_enter)
            title_lbl.bind("<Leave>", _on_leave)
            title_lbl.bind("<Button-1>", lambda _e: _enter_edit_mode())

            pencil_btn = ctk.CTkButton(
                title_row,
                text=pencil_icon,
                width=28,
                height=28,
                corner_radius=8,
                fg_color="transparent",
                hover_color=theme.ACCENT_HOVER,
                text_color=theme.TEXT_SECONDARY,
                command=_enter_edit_mode,
            )
            pencil_btn.grid(row=0, column=1, sticky="e", padx=(12, 0))

        def _confirm_new_label(raw_text: str) -> None:
            trimmed = raw_text.strip()
            if len(trimmed) > max_label:
                _set_inline_message(f"Label too long (max {max_label} chars).")
                return

            new_label = trimmed if trimmed else None

            # Persist synchronously.
            self.backup_manager.set_user_label(save.folder_id, new_label)

            # Update in-memory immediately.
            save.user_label = new_label
            self.selected_save = save

            # Update left card title too without refresh.
            card_bundle = self._card_buttons.get(save.folder_id)
            if card_bundle and len(card_bundle) >= 4:
                _card, _badge, _select_button, card_title_label = card_bundle
                card_title_label.configure(text=_truncate_for_display(save.display_name))


            self.activity_log.append(self._now_text(), "info", f"Renamed {save.folder_id} to '{save.display_name}'." if new_label else f"Cleared label for {save.folder_id}.")

            _clear_inline_message()
            _apply_view_mode((save.user_label or "") or "")

        def _cancel_edit() -> None:
            _clear_inline_message()
            save.user_label = self._selected_title_bundle["prev_label"] or None
            _apply_view_mode(save.user_label or "")

        def _enter_edit_mode() -> None:
            _clear_inline_message()
            for w in title_row.winfo_children():
                w.destroy()

            self._selected_title_bundle["edit_mode"] = True

            entry = ctk.CTkEntry(
                title_row,
                fg_color=theme.BG_INPUT,
                border_color=theme.ACCENT,
                border_width=1,
                text_color=theme.TEXT_PRIMARY,
                height=34,
                corner_radius=10,
            )
            entry.insert(0, _get_current_label_for_entry())
            entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            entry.focus_set()
            try:
                entry.select_range(0, "end")
            except Exception:
                pass

            def _on_focus_out(_e):
                _confirm_new_label(entry.get())

            def _on_enter_key(_e):
                _confirm_new_label(entry.get())

            def _on_escape(_e):
                _cancel_edit()

            entry.bind("<FocusOut>", _on_focus_out)
            entry.bind("<Return>", _on_enter_key)
            entry.bind("<Escape>", _on_escape)

            actions = ctk.CTkFrame(title_row, fg_color="transparent")
            actions.grid(row=0, column=1, sticky="e")

            confirm_btn = ctk.CTkButton(
                actions,
                text="✓",
                width=28,
                height=28,
                corner_radius=8,
                fg_color="transparent",
                hover_color=theme.SUCCESS,
                text_color=theme.SUCCESS,
                command=lambda: _confirm_new_label(entry.get()),
            )
            confirm_btn.pack(side="left", padx=(0, 6))

            cancel_btn = ctk.CTkButton(
                actions,
                text="✕",
                width=28,
                height=28,
                corner_radius=8,
                fg_color="transparent",
                hover_color=theme.DANGER,
                text_color=theme.DANGER,
                command=_cancel_edit,
            )
            cancel_btn.pack(side="left")

        inline_msg_var = {"label": None}

        def _set_inline_message(text: str) -> None:
            if inline_msg_var["label"] is None:
                inline_msg_var["label"] = ctk.CTkLabel(
                    header_card,
                    text=text,
                    font=theme.body_font(11),
                    text_color=theme.WARNING,
                    anchor="w",
                )
                inline_msg_var["label"].pack(fill="x", padx=16, pady=(0, 6))
            else:
                inline_msg_var["label"].configure(text=text)

        def _clear_inline_message() -> None:
            if inline_msg_var["label"] is not None:
                inline_msg_var["label"].destroy()
                inline_msg_var["label"] = None

        _apply_view_mode(save.user_label or "")

        ctk.CTkLabel(header_card, text=save.folder_id, font=theme.mono_font(11), text_color=theme.TEXT_MUTED, anchor="w").pack(anchor="w", padx=16, pady=(0, 12))

        badge_row = ctk.CTkFrame(header_card, fg_color="transparent")
        badge_row.pack(anchor="w", padx=16, pady=(0, 14))

        status_badge = ctk.CTkFrame(badge_row, fg_color=theme.status_bg(status_key), corner_radius=theme.BADGE_CORNER_RADIUS)
        status_badge.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(status_badge, text=f"{theme.ICON_DOT} {status_text}", font=theme.body_font(11, "bold"), text_color=accent).pack(padx=10, pady=4)

        live_key = "danger" if save.is_deleted else "success"
        live_text = "Deleted" if save.is_deleted else "Live"
        live_badge = ctk.CTkFrame(badge_row, fg_color=theme.status_bg(live_key), corner_radius=theme.BADGE_CORNER_RADIUS)
        live_badge.pack(side="left")
        ctk.CTkLabel(live_badge, text=f"{theme.ICON_DOT} {live_text}", font=theme.body_font(11, "bold"), text_color=theme.status_color(live_key)).pack(padx=10, pady=4)

        info_card = ctk.CTkFrame(self.details_frame, fg_color=theme.BG_CARD, corner_radius=theme.CARD_CORNER_RADIUS)
        info_card.pack(fill="x")

        rows = [
            ("Label", save.user_label or "(none)"),
            ("Folder created", format_datetime(save.folder_ctime)),
            ("Last modified", format_datetime(save.mtime)),
            ("Size", format_bytes(save.size)),
            ("Backup timestamp", format_datetime(save.backup_timestamp)),
            ("Main file hash", (save.main_file_hash or "Pending")[:24] + ("\u2026" if save.main_file_hash and len(save.main_file_hash) > 24 else "")),
        ]
        for label, value in rows:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=6)
            ctk.CTkLabel(row, text=label, font=theme.body_font(12), text_color=theme.TEXT_SECONDARY, width=140, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=theme.body_font(12, "bold"), text_color=theme.TEXT_PRIMARY, anchor="w").pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(info_card, fg_color="transparent", height=6).pack()

        # Action buttons for the currently selected save.
        # This keeps the dashboard action bar uncluttered.
        actions_card = ctk.CTkFrame(self.details_frame, fg_color=theme.BG_CARD, corner_radius=theme.CARD_CORNER_RADIUS)
        actions_card.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(actions_card, text="SAVE BACKUP ACTIONS", font=theme.body_font(11, "bold"), text_color=theme.TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 6))

        actions_row = ctk.CTkFrame(actions_card, fg_color="transparent")
        actions_row.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkButton(
            actions_row,
            text="\U0001F5C4  Create Backup",
            command=self.create_backup,
            corner_radius=theme.BUTTON_CORNER_RADIUS,
            height=38,
            **_BUTTON_STYLES["primary"],
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            actions_row,
            text="\u267B  Load Backup",
            command=self.load_backup,
            corner_radius=theme.BUTTON_CORNER_RADIUS,
            height=38,
            **_BUTTON_STYLES["primary"],
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))


    # ------------------------------------------------------------------
    # Status alert bar (deleted saves take priority, then outdated backups)
    # ------------------------------------------------------------------
    def _deleted_saves(self) -> list[SaveModel]:
        return [save for save in self.saves if save.is_deleted]

    def _is_outdated(self, save: SaveModel) -> bool:
        """True when the live save has newer progress than its backup.

        This is the same comparison _status_for() uses for the per-card
        "Backup outdated" badge, reused here to drive a top-level alert.
        """
        return (
            not save.is_deleted
            and save.has_backup
            and bool(save.backup_timestamp)
            and bool(save.mtime)
            and save.backup_timestamp < save.mtime
        )

    def _outdated_saves(self) -> list[SaveModel]:
        return [save for save in self.saves if self._is_outdated(save)]

    def _update_status_alert(self) -> None:
        """Refresh the single alert banner, prioritizing deleted saves.

        Deleted saves are more urgent (data would be lost without the
        backup) so they take priority over an outdated-backup notice.
        Only one alert is shown at a time to keep the banner simple.
        """
        deleted_saves = self._deleted_saves()
        if deleted_saves:
            self._pending_outdated_folder_id = None
            if self._pending_restore_folder_id is None or self._pending_restore_folder_id not in {save.folder_id for save in deleted_saves}:
                self._pending_restore_folder_id = deleted_saves[0].folder_id

            count = len(deleted_saves)
            first_save = deleted_saves[0]
            self._alert_mode = "deleted"
            self.alert_bar.configure(fg_color=theme.DANGER_BG, border_color=theme.DANGER)
            self.alert_icon_label.configure(text="\u2620", text_color=theme.DANGER)
            self.alert_label.configure(
                text=f"{count} deleted save(s) detected. {first_save.folder_id} is missing and its latest backup is ready to restore.",
            )
            self.alert_action_button.configure(
                text="Restore Latest Backup", command=self._restore_pending_deleted_save, **_BUTTON_STYLES["primary"],
            )
            self._show_alert()
            return

        self._pending_restore_folder_id = None

        outdated_saves = self._outdated_saves()
        if outdated_saves:
            if self._pending_outdated_folder_id is None or self._pending_outdated_folder_id not in {save.folder_id for save in outdated_saves}:
                self._pending_outdated_folder_id = outdated_saves[0].folder_id

            count = len(outdated_saves)
            first_save = outdated_saves[0]
            self._alert_mode = "outdated"
            self.alert_bar.configure(fg_color=theme.status_bg("warning"), border_color=theme.status_color("warning"))
            self.alert_icon_label.configure(text="\u26A0", text_color=theme.status_color("warning"))
            self.alert_label.configure(
                text=f"{count} save(s) have new progress since the last backup. {first_save.folder_id} was played more recently than it was backed up.",
            )
            self.alert_action_button.configure(
                text="Back Up Now", command=self._backup_pending_outdated_save, **_BUTTON_STYLES["primary"],
            )
            self._show_alert()
            return

        self._pending_outdated_folder_id = None
        self._alert_mode = None
        self._hide_alert()

    def _show_alert(self) -> None:
        self.alert_bar.grid()

    def _hide_alert(self) -> None:
        self.alert_bar.grid_remove()

    def _dismiss_alert(self) -> None:
        self._hide_alert()
        if self._alert_mode == "outdated":
            self.activity_log.append(self._now_text(), "info", "Outdated-backup alert dismissed.")
        else:
            self.activity_log.append(self._now_text(), "info", "Deleted-save alert dismissed.")

    def _resolve_restore_target(self) -> SaveModel | None:
        if self._pending_restore_folder_id:
            pending = self.save_manager.get_save_by_folder_id(self.saves, self._pending_restore_folder_id)
            if pending and pending.is_deleted:
                return pending

        for save in self.saves:
            if save.is_deleted:
                return save

        return None

    def _restore_pending_deleted_save(self) -> None:
        target = self._resolve_restore_target()
        if target is None:
            self.activity_log.append(self._now_text(), "info", "No deleted save is currently available to restore.")
            return

        if not ask_confirmation("Restore Deleted Save", f"Restore the latest backup for {target.folder_id}?"):
            self.activity_log.append(self._now_text(), "info", f"Restore declined for {target.folder_id}.")
            return

        try:
            result = self.restore_manager.restore(target.folder_id)

            self._pending_restore_folder_id = None
            self.refresh_saves(log_activity=False)
            self.activity_log.append(self._now_text(), "success", f"Restored deleted save {result.folder_id}.")
            show_info_dialog("Restore Complete", f"{result.folder_id} was restored successfully.")
        except Exception as exc:
            self.logger.exception("Restore failed for deleted save %s", target.folder_id)
            show_error_dialog("Restore Failed", f"Unable to restore {target.folder_id}.", str(exc))

    def _resolve_outdated_target(self) -> SaveModel | None:
        if self._pending_outdated_folder_id:
            pending = self.save_manager.get_save_by_folder_id(self.saves, self._pending_outdated_folder_id)
            if pending and self._is_outdated(pending):
                return pending

        for save in self.saves:
            if self._is_outdated(save):
                return save

        return None

    def _backup_pending_outdated_save(self) -> None:
        target = self._resolve_outdated_target()
        if target is None:
            self.activity_log.append(self._now_text(), "info", "No outdated backup is currently pending.")
            return

        try:
            result = self.backup_manager.create_or_update_backup(target)
            self.refresh_saves(log_activity=False)
            self.activity_log.append(self._now_text(), "success", f"Backup {result.status} for {result.folder_id} with your latest progress.")
            show_info_dialog("Backup Updated", f"{result.folder_id}'s backup now matches your latest save progress.")
        except Exception as exc:
            self.logger.exception("Backup update failed for %s", target.folder_id)
            show_error_dialog("Backup Failed", f"Unable to update backup for {target.folder_id}.", str(exc))

    # ------------------------------------------------------------------
    # Clock
    # ------------------------------------------------------------------
    def update_clock(self) -> None:
        self.time_label.configure(text=f"{theme.ICON_CLOCK} {self._now_text()}")
        self.after(1000, self.update_clock)


    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def create_backup(self) -> None:
        if self.selected_save is None:
            self.activity_log.append(self._now_text(), "warning", "Create Backup requested with no save selected.")
            return
        try:
            result = self.backup_manager.create_or_update_backup(self.selected_save)

            self.refresh_saves(log_activity=False)
            self.activity_log.append(self._now_text(), "success", f"Backup {result.status} for {result.folder_id}.")
        except Exception as exc:
            self.logger.exception("Backup creation failed for %s", self.selected_save.folder_id)
            show_error_dialog("Backup Failed", f"Unable to create backup for {self.selected_save.folder_id}.", str(exc))

    def load_backup(self) -> None:
        if self.selected_save is None:
            self.activity_log.append(self._now_text(), "warning", "Load Backup requested with no save selected.")
            return
        label = self.selected_save.display_name
        if not ask_confirmation("Restore Backup", f"Restore backup for {self.selected_save.folder_id} ({label})?"):
            self.activity_log.append(self._now_text(), "info", f"Restore declined for {self.selected_save.folder_id}.")
            return
        try:
            result = self.restore_manager.restore(self.selected_save.folder_id)
            self.refresh_saves(log_activity=False)

            self.activity_log.append(self._now_text(), "success", f"Restored {result.folder_id} to save folder.")
            show_info_dialog("Restore Complete", f"{result.folder_id} was restored successfully.")
        except Exception as exc:
            self.logger.exception("Restore failed for %s", self.selected_save.folder_id)
            show_error_dialog("Restore Failed", f"Unable to restore {self.selected_save.folder_id}.", str(exc))

    def delete_backup(self) -> None:
        if self.selected_save is None:
            self.activity_log.append(self._now_text(), "warning", "Delete Backup requested with no save selected.")
            return
        label = self.selected_save.display_name
        if not ask_confirmation("Delete Backup", f"Delete backup for {self.selected_save.folder_id} ({label})?"):
            self.activity_log.append(self._now_text(), "info", f"Backup delete declined for {self.selected_save.folder_id}.")
            return
        try:
            removed = self.backup_manager.delete_backup(self.selected_save.folder_id)
            self.refresh_saves(log_activity=False)
            self.activity_log.append(self._now_text(), "success" if removed else "info", f"Backup delete attempted for {self.selected_save.folder_id}.")
        except Exception as exc:
            self.logger.exception("Backup delete failed for %s", self.selected_save.folder_id)
            show_error_dialog("Delete Failed", f"Unable to delete backup for {self.selected_save.folder_id}.", str(exc))

    def start_monitoring(self) -> None:
        settings = self.settings_manager.load()
        try:
            if self.monitor_manager.start(settings.save_folder):
                self.monitor_status_label.configure(text="Monitoring Active", text_color=theme.SUCCESS)
                self.monitor_dot_label.configure(text_color=theme.SUCCESS)
                self.activity_log.append(self._now_text(), "info", f"Monitoring started for {settings.save_folder}.")
            else:
                show_error_dialog("Monitoring Unavailable", "Monitoring could not start.", "watchdog is not installed or monitoring is unavailable.")
        except Exception as exc:
            self.logger.exception("Failed to start monitoring")
            show_error_dialog("Monitoring Failed", "Could not start monitoring.", str(exc))

    def stop_monitoring(self) -> None:
        self.monitor_manager.stop()
        self.monitor_status_label.configure(text="Monitoring Idle", text_color=theme.TEXT_SECONDARY)
        self.monitor_dot_label.configure(text_color=theme.NEUTRAL)
        self.activity_log.append(self._now_text(), "info", "Monitoring stopped.")

    def _open_folder_in_file_manager(self, folder_path: str | Path) -> None:
        """Open the given folder path in the user's file manager.

        Uses OS-specific commands:
        - Linux: xdg-open
        - macOS: open
        - Windows: explorer
        """
        folder = Path(folder_path).expanduser()
        try:
            folder = folder.resolve()
        except Exception:
            # resolve() can fail for non-existing paths; keep expanded path.
            pass

        if not folder.exists() or not folder.is_dir():
            show_error_dialog(
                "Folder Not Found",
                "The folder configured in Settings does not exist or is not a directory.",
                str(folder),
            )
            return

        try:
            if sys.platform.startswith("linux"):
                opener = shutil.which("xdg-open")
                if not opener:
                    raise RuntimeError("xdg-open is not available")
                subprocess.Popen([opener, str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform == "darwin":
                opener = shutil.which("open")
                if not opener:
                    raise RuntimeError("open is not available")
                subprocess.Popen([opener, str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform.startswith("win"):
                # explorer.exe is the standard Windows shell folder opener.
                subprocess.Popen(["explorer", str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # Last resort: try xdg-open (may work on some Unix-like systems)
                subprocess.Popen(["xdg-open", str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.activity_log.append(self._now_text(), "success", f"Opened folder: {folder}")
        except Exception as exc:
            self.logger.exception("Failed to open folder in file manager: %s", folder)
            show_error_dialog("Open Folder Failed", "Unable to open the configured folder.", str(exc))

    def open_save_folder(self) -> None:
        settings = self.settings_manager.load()
        self._open_folder_in_file_manager(settings.save_folder)

    def open_backup_folder(self) -> None:
        settings = self.settings_manager.load()
        self._open_folder_in_file_manager(settings.backup_folder)


    def open_settings(self) -> None:
        if callable(self.on_open_settings):
            self.on_open_settings()
        else:
            self.activity_log.append(self._now_text(), "info", "Settings window is not attached yet.")

    def exit_app(self) -> None:
        if self.master is not None:
            close = getattr(self.master, "close", None)
            if callable(close):
                close()
            else:
                self.master.destroy()

    # ------------------------------------------------------------------
    # Monitor events
    # ------------------------------------------------------------------
    def poll_monitor_events(self) -> None:
        for event in self.monitor_manager.drain_events():
            self.handle_monitor_event(event)

    def handle_monitor_event(self, event: MonitorEvent) -> None:
        result = self.monitor_manager.process_event(event)
        action = result.get("action")

        if action == "refresh":
            self.refresh_saves(log_activity=True)
            return

        if action == "missing_backup":
            self.refresh_saves(log_activity=True)

            self.activity_log.append(self._now_text(), "warning", f"Deletion detected for {event.folder_id} without backup.")
            return

        if action == "prompt_restore":
            record = result.get("record") or {}

            user_label = str(record.get("user_label") or "") or None
            last_backup_text = str(record.get("last_updated") or record.get("created_at") or "")
            last_backup_timestamp = None
            if last_backup_text:
                try:
                    last_backup_timestamp = datetime.fromisoformat(last_backup_text)
                except ValueError:
                    last_backup_timestamp = None
            self._pending_restore_folder_id = event.folder_id
            self.refresh_saves(log_activity=True)
            self.activity_log.append(self._now_text(), "warning", f"Deleted save detected for {event.folder_id}. Prompting restore.")
            dialog = YouDiedDialog(self.winfo_toplevel(), event.folder_id, user_label, last_backup_timestamp)
            self.wait_window(dialog)
            if dialog.result.accepted:
                try:
                    self.restore_manager.restore(event.folder_id)

                    self._pending_restore_folder_id = None

                    self.refresh_saves(log_activity=False)

                    self.activity_log.append(self._now_text(), "success", f"Auto-restore completed for {event.folder_id}.")
                except Exception as exc:
                    self.logger.exception("Auto-restore failed for %s", event.folder_id)
                    show_error_dialog("Restore Failed", f"Unable to restore {event.folder_id}.", str(exc))
            else:
                self.activity_log.append(self._now_text(), "info", f"Restore declined for {event.folder_id}.")
            return

        self.activity_log.append(self._now_text(), "info", f"Ignored monitor event {event.event_type} for {event.folder_id}.")

    def _now_text(self) -> str:
        return datetime.now().strftime("%H:%M:%S")