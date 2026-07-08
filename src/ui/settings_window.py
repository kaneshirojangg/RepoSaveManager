"""Settings editor window for Repo Save Manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - runtime fallback for environments without the dependency
    import tkinter as ctk  # type: ignore[no-redef]

    ctk.CTkToplevel = ctk.Toplevel  # type: ignore[attr-defined]
    ctk.CTkFrame = ctk.Frame  # type: ignore[attr-defined]
    ctk.CTkLabel = ctk.Label  # type: ignore[attr-defined]
    ctk.CTkButton = ctk.Button  # type: ignore[attr-defined]
    ctk.CTkEntry = ctk.Entry  # type: ignore[attr-defined]
    ctk.CTkCheckBox = ctk.Checkbutton  # type: ignore[attr-defined]

from src.managers.settings_manager import AppSettings, SettingsManager, SettingsValidationResult
from src.ui.logo import load_logo_image, load_window_icon
from src.ui import theme
from src.utils.helpers import browse_for_directory, open_folder_in_file_manager

_ERROR_PREFIXES = (
    "Save folder does not exist",
    "No REPO_SAVE_* folders found",
    "Read permission denied",
    "Unable to create backup folder",
    "Backup folder does not exist",
    "Write permission denied",
)

_PRIMARY_BUTTON = dict(
    fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER, text_color=theme.TEXT_ON_ACCENT,
    font=theme.body_font(13, "bold"), corner_radius=theme.BUTTON_CORNER_RADIUS,
)
_OUTLINE_BUTTON = dict(
    fg_color="transparent", hover_color=theme.BG_CARD_HOVER, text_color=theme.TEXT_SECONDARY,
    border_width=1, border_color=theme.BORDER, font=theme.body_font(13),
    corner_radius=theme.BUTTON_CORNER_RADIUS,
)


@dataclass(slots=True)
class SettingsWindowResult:
    saved: bool = False
    settings: AppSettings | None = None
    validation: SettingsValidationResult | None = None


class SettingsWindow(ctk.CTkToplevel):
    def __init__(
        self,
        master: ctk.CTkBaseClass | None,
        settings_manager: SettingsManager,
        on_save: Callable[[AppSettings], None] | None = None,
    ) -> None:
        super().__init__(master)
        self.settings_manager = settings_manager
        self.on_save = on_save
        self.result = SettingsWindowResult()
        self.settings = self.settings_manager.load()
        self._logo_image = load_logo_image((48, 48))

        self.title("Settings")
        self.geometry("880x660")
        self.minsize(880, 660)
        self.configure(fg_color=theme.BG_PRIMARY)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self._window_icon = load_window_icon()
        try:
            self.iconphoto(True, self._window_icon)
        except Exception:
            pass

        self.save_folder_var = ctk.StringVar(value=self.settings.save_folder)
        self.backup_folder_var = ctk.StringVar(value=self.settings.backup_folder)
        self.auto_start_var = ctk.BooleanVar(value=self.settings.auto_start_monitoring)
        self.confirm_restore_var = ctk.BooleanVar(value=self.settings.confirm_before_restore)
        self.confirm_delete_var = ctk.BooleanVar(value=self.settings.confirm_before_delete)
        self.theme_var = ctk.StringVar(value=self.settings.theme)
        self.status_var = ctk.StringVar(value="Adjust settings and run Test Configuration before saving.")

        self._build_ui()

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=18, pady=18)

        header = ctk.CTkFrame(container, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER)
        header.pack(fill="x", pady=(0, 12))
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(anchor="w", padx=18, pady=14, fill="x")
        ctk.CTkLabel(header_inner, text="", image=self._logo_image).pack(side="left", padx=(0, 12))
        title_stack = ctk.CTkFrame(header_inner, fg_color="transparent")
        title_stack.pack(side="left", anchor="w")
        ctk.CTkLabel(title_stack, text="SETTINGS", font=theme.header_font(22), text_color=theme.ACCENT).pack(anchor="w")
        ctk.CTkLabel(title_stack, text="Save folders, backup folder, and confirmation preferences.", font=theme.body_font(12), text_color=theme.TEXT_SECONDARY).pack(anchor="w")

        body = ctk.CTkFrame(container, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        left = ctk.CTkFrame(body, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER)
        right = ctk.CTkFrame(body, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        self._build_paths_section(left)
        self._build_preferences_section(right)

        validation_card = ctk.CTkFrame(container, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER)
        validation_card.pack(fill="both", expand=False, pady=(0, 12))
        ctk.CTkLabel(validation_card, text="VALIDATION", font=theme.header_font(13), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 4))
        self.validation_box = ctk.CTkTextbox(validation_card, height=170, wrap="word", fg_color=theme.BG_INPUT, corner_radius=theme.CARD_CORNER_RADIUS, font=theme.mono_font(12))
        self.validation_box.pack(fill="both", expand=False, padx=16, pady=(0, 14))
        self._configure_validation_tags()
        self.validation_box.insert("1.0", "Run Test Configuration to validate your selected folders.")
        self.validation_box.configure(state="disabled")

        self.status_label = ctk.CTkLabel(container, textvariable=self.status_var, anchor="w", font=theme.body_font(12), text_color=theme.TEXT_SECONDARY)
        self.status_label.pack(fill="x", pady=(0, 8))

        footer = ctk.CTkFrame(container, fg_color="transparent")
        footer.pack(fill="x")

        ctk.CTkButton(footer, text="\U0001F50D  Auto-Detect", command=self._auto_detect, **_OUTLINE_BUTTON).pack(side="left", padx=(0, 8))
        ctk.CTkButton(footer, text="\u2713  Test Configuration", command=self._test_configuration, **_OUTLINE_BUTTON).pack(side="left", padx=8)
        ctk.CTkButton(footer, text="Save", command=self._save, **_PRIMARY_BUTTON).pack(side="left", padx=8)
        ctk.CTkButton(footer, text="Reset to Default", command=self._reset_defaults, **_OUTLINE_BUTTON).pack(side="left", padx=8)
        ctk.CTkButton(footer, text="Cancel", command=self._cancel, **_OUTLINE_BUTTON).pack(side="right")

    def _configure_validation_tags(self) -> None:
        try:
            self.validation_box.tag_configure("ok", foreground=theme.SUCCESS)
            self.validation_box.tag_configure("fail", foreground=theme.DANGER)
            self.validation_box.tag_configure("neutral", foreground=theme.TEXT_SECONDARY)
        except Exception:
            pass

    def _build_paths_section(self, panel: ctk.CTkFrame) -> None:
        ctk.CTkLabel(panel, text="FOLDERS", font=theme.header_font(15), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(16, 8))

        ctk.CTkLabel(panel, text="Repo save folder", font=theme.body_font(12), text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(10, 4))
        ctk.CTkEntry(panel, textvariable=self.save_folder_var, fg_color=theme.BG_INPUT, border_color=theme.BORDER, text_color=theme.TEXT_PRIMARY).pack(fill="x", padx=16, pady=(0, 8))

        btn_row_save = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row_save.pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkButton(btn_row_save, text="\U0001F4C2  Browse Save Folder", command=self._browse_save_folder, **_OUTLINE_BUTTON).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(btn_row_save, text="\U0001F5C4  Open", width=90, command=self._open_save_folder, **_OUTLINE_BUTTON).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(panel, text="Backup folder", font=theme.body_font(12), text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(10, 4))
        ctk.CTkEntry(panel, textvariable=self.backup_folder_var, fg_color=theme.BG_INPUT, border_color=theme.BORDER, text_color=theme.TEXT_PRIMARY).pack(fill="x", padx=16, pady=(0, 8))

        btn_row_backup = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row_backup.pack(fill="x", padx=16, pady=(0, 16))
        ctk.CTkButton(btn_row_backup, text="\U0001F5C3  Browse Backup Folder", command=self._browse_backup_folder, **_OUTLINE_BUTTON).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(btn_row_backup, text="\U0001F5C4  Open", width=90, command=self._open_backup_folder, **_OUTLINE_BUTTON).pack(side="left", padx=(8, 0))

    def _build_preferences_section(self, panel: ctk.CTkFrame) -> None:
        ctk.CTkLabel(panel, text="PREFERENCES", font=theme.header_font(15), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(16, 8))

        ctk.CTkLabel(panel, text="Theme", font=theme.body_font(12), text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(10, 4))
        theme_row = ctk.CTkFrame(panel, fg_color="transparent")
        theme_row.pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkEntry(theme_row, textvariable=self.theme_var, fg_color=theme.BG_INPUT, border_color=theme.BORDER, text_color=theme.TEXT_PRIMARY).pack(fill="x", expand=True)

        ctk.CTkLabel(panel, text="Monitoring and confirmations", font=theme.body_font(12), text_color=theme.TEXT_SECONDARY).pack(anchor="w", padx=16, pady=(14, 4))
        for var, label in (
            (self.auto_start_var, "Auto-start monitoring"),
            (self.confirm_restore_var, "Confirm before restore"),
            (self.confirm_delete_var, "Confirm before delete"),
        ):
            ctk.CTkCheckBox(
                panel, text=label, variable=var,
                fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                text_color=theme.TEXT_PRIMARY, font=theme.body_font(12),
                border_color=theme.BORDER,
            ).pack(anchor="w", padx=16, pady=6)

    def _browse_save_folder(self) -> None:
        selected = browse_for_directory("Select Repo Save Folder", self.save_folder_var.get())
        if selected:
            self.save_folder_var.set(selected)
            self.status_var.set("Save folder selected.")

    def _browse_backup_folder(self) -> None:
        selected = browse_for_directory("Select Backup Folder", self.backup_folder_var.get())
        if selected:
            self.backup_folder_var.set(selected)
            self.status_var.set("Backup folder selected.")

    def _open_save_folder(self) -> None:
        from src.ui.dashboard import Dashboard

        Dashboard._open_folder_in_file_manager(self, self.save_folder_var.get())

    def _open_backup_folder(self) -> None:
        from src.ui.dashboard import Dashboard

        Dashboard._open_folder_in_file_manager(self, self.backup_folder_var.get())



    def _auto_detect(self) -> None:
        candidates = self.settings_manager.auto_detect_save_folders()
        if candidates:
            self.save_folder_var.set(str(candidates[0]))
            self.status_var.set(f"Auto-detected {len(candidates)} candidate folder(s); using the first.")
        else:
            self.status_var.set("No save folder candidates were found.")

    def _test_configuration(self) -> None:
        validation = self.settings_manager.validate(self.save_folder_var.get(), self.backup_folder_var.get())
        self.result.validation = validation
        self._write_validation(validation.messages, validation.is_valid)
        if validation.is_valid:
            self.status_label.configure(text_color=theme.SUCCESS)
            self.status_var.set("Configuration valid.")
        else:
            self.status_label.configure(text_color=theme.DANGER)
            self.status_var.set("Configuration needs attention.")

    def _save(self) -> None:
        validation = self.settings_manager.validate(self.save_folder_var.get(), self.backup_folder_var.get())
        self.result.validation = validation
        if not validation.is_valid:
            self._write_validation(validation.messages, False)
            self.status_label.configure(text_color=theme.DANGER)
            self.status_var.set("Fix the validation issues before saving.")
            return

        self.settings.save_folder = str(validation.save_folder)
        self.settings.backup_folder = str(validation.backup_folder)
        self.settings.auto_start_monitoring = self.auto_start_var.get()
        self.settings.confirm_before_restore = self.confirm_restore_var.get()
        self.settings.confirm_before_delete = self.confirm_delete_var.get()
        self.settings.theme = self.theme_var.get().strip() or "dark"

        self.settings_manager.save(self.settings)
        self.result.saved = True
        self.result.settings = self.settings
        if callable(self.on_save):
            self.on_save(self.settings)
        self.destroy()

    def _reset_defaults(self) -> None:
        self.settings = AppSettings.default()
        self.save_folder_var.set(self.settings.save_folder)
        self.backup_folder_var.set(self.settings.backup_folder)
        self.auto_start_var.set(self.settings.auto_start_monitoring)
        self.confirm_restore_var.set(self.settings.confirm_before_restore)
        self.confirm_delete_var.set(self.settings.confirm_before_delete)
        self.theme_var.set(self.settings.theme)
        self.status_label.configure(text_color=theme.TEXT_SECONDARY)
        self.status_var.set("Settings reset to defaults.")

    def _cancel(self) -> None:
        self.result.saved = False
        self.destroy()

    def _write_validation(self, messages: list[str], is_valid: bool) -> None:
        self.validation_box.configure(state="normal")
        self.validation_box.delete("1.0", "end")
        for message in messages:
            is_error = message.startswith(_ERROR_PREFIXES)
            marker = "\u2715" if is_error else "\u2713"
            tag = "fail" if is_error else "ok"
            self.validation_box.insert("end", f"{marker} {message}\n", tag)
        if is_valid:
            self.validation_box.insert("end", "Configuration successful.\n", "ok")
        if not messages:
            self.validation_box.insert("end", "No messages.\n", "neutral")
        self.validation_box.configure(state="disabled")