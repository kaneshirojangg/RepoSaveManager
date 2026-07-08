"""First-launch configuration wizard for selecting save and backup folders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - runtime fallback for environments without the dependency
    import tkinter as ctk  # type: ignore[no-redef]

    # Fallback: provide wrappers so tkinter doesn't choke on customtkinter-only kwargs.
    # IMPORTANT: errors happen in the widget constructor (before configure),
    # so we must strip unsupported kwargs in __init__ as well.
    _UNSUPPORTED_CTK_KWARGS = {
        "fg_color",
        "corner_radius",
        "border_width",
        "border_color",
        "hover_color",
        "text_color",
        "placeholder_text",
    }

    class _CTkCompatMixin:
        def __init__(self, *args, **kwargs):  # type: ignore[override]
            for k in list(kwargs.keys()):
                if k in _UNSUPPORTED_CTK_KWARGS:
                    kwargs.pop(k, None)
            super().__init__(*args, **kwargs)

        def configure(self, cnf=None, **kw):  # type: ignore[override]
            for k in list(kw.keys()):
                if k in _UNSUPPORTED_CTK_KWARGS:
                    kw.pop(k, None)
            return super().configure(cnf=cnf, **kw)

        config = configure

    class CTk(_CTkCompatMixin, ctk.Tk):
        pass

    class CTkToplevel(_CTkCompatMixin, ctk.Toplevel):
        pass

    class CTkFrame(_CTkCompatMixin, ctk.Frame):
        pass

    class CTkLabel(_CTkCompatMixin, ctk.Label):
        pass

    class CTkButton(_CTkCompatMixin, ctk.Button):
        pass

    class CTkEntry(_CTkCompatMixin, ctk.Entry):
        pass

    class CTkTextbox(_CTkCompatMixin, ctk.Text):
        pass


    ctk.CTk = CTk  # type: ignore[attr-defined]
    ctk.CTkToplevel = CTkToplevel  # type: ignore[attr-defined]
    ctk.CTkFrame = CTkFrame  # type: ignore[attr-defined]
    ctk.CTkLabel = CTkLabel  # type: ignore[attr-defined]
    ctk.CTkButton = CTkButton  # type: ignore[attr-defined]
    ctk.CTkEntry = CTkEntry  # type: ignore[attr-defined]
    ctk.CTkTextbox = CTkTextbox  # type: ignore[attr-defined]


from src.managers.settings_manager import AppSettings, SettingsManager, SettingsValidationResult
from src.ui.logo import load_logo_image, load_window_icon
from src.ui import theme
from src.utils.helpers import browse_for_directory, format_datetime, open_folder_in_file_manager

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
class WizardResult:
    settings: AppSettings | None = None
    validation: SettingsValidationResult | None = None
    accepted: bool = False


class SetupWizard(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk | None = None, settings_manager: SettingsManager | None = None) -> None:
        super().__init__(master)
        self.settings_manager = settings_manager or SettingsManager()
        self.result = WizardResult()
        self.settings = self.settings_manager.load()
        self.title("Repo Save Manager Setup")
        self.geometry("900x600")
        self.minsize(900, 600)
        # customtkinter widgets support fg_color; tkinter fallbacks do not.
        try:
            self.configure(fg_color=theme.BG_PRIMARY)
        except Exception:
            try:
                self.configure(bg=theme.BG_PRIMARY)
            except Exception:
                pass

        self._window_icon = load_window_icon()
        try:
            self.iconphoto(True, self._window_icon)
        except Exception:
            pass
        self._logo_image = load_logo_image((56, 56))

        self.save_folder_var = ctk.StringVar(value=self.settings.save_folder)
        self.backup_folder_var = ctk.StringVar(value=self.settings.backup_folder)
        self.status_var = ctk.StringVar(value="Select a save folder and validate the configuration.")

        self._build_ui()
        self._refresh_preview()

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
        ctk.CTkLabel(title_stack, text="FIRST-LAUNCH SETUP", font=theme.header_font(22), text_color=theme.ACCENT).pack(anchor="w")
        ctk.CTkLabel(
            title_stack,
            text="Choose the R.E.P.O. saves folder and a mirrored backup folder before the app can continue.",
            font=theme.body_font(12), text_color=theme.TEXT_SECONDARY, justify="left",
        ).pack(anchor="w")

        grid = ctk.CTkFrame(container, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=3)
        grid.grid_columnconfigure(1, weight=2)

        left_panel = ctk.CTkFrame(grid, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER)
        right_panel = ctk.CTkFrame(grid, fg_color=theme.BG_SECONDARY, corner_radius=theme.PANEL_CORNER_RADIUS, border_width=1, border_color=theme.BORDER)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(left_panel, text="\U0001F4C1  Repo Save Folder", font=theme.header_font(15), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkButton(left_panel, text="\U0001F50D  Auto-Detect", command=self._auto_detect, **_PRIMARY_BUTTON).pack(fill="x", padx=16, pady=4)

        ctk.CTkEntry(left_panel, textvariable=self.save_folder_var, fg_color=theme.BG_INPUT, border_color=theme.BORDER, text_color=theme.TEXT_PRIMARY).pack(fill="x", padx=16, pady=(8, 4))
        row_save = ctk.CTkFrame(left_panel, fg_color="transparent")
        row_save.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkButton(row_save, text="\U0001F4C2  Browse Folder", command=self._browse_save_folder, **_OUTLINE_BUTTON).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row_save, text="\U0001F5C4  Open", width=90, command=self._open_save_folder, **_OUTLINE_BUTTON).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(left_panel, text="\U0001F5C3  Backup Folder", font=theme.header_font(15), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(16, 8))
        ctk.CTkEntry(left_panel, textvariable=self.backup_folder_var, fg_color=theme.BG_INPUT, border_color=theme.BORDER, text_color=theme.TEXT_PRIMARY).pack(fill="x", padx=16, pady=(8, 4))
        row_backup = ctk.CTkFrame(left_panel, fg_color="transparent")
        row_backup.pack(fill="x", padx=16, pady=(0, 16))
        ctk.CTkButton(row_backup, text="\U0001F4C2  Browse Backup Folder", command=self._browse_backup_folder, **_OUTLINE_BUTTON).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row_backup, text="\U0001F5C4  Open", width=90, command=self._open_backup_folder, **_OUTLINE_BUTTON).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(right_panel, text="VALIDATION OUTPUT", font=theme.header_font(14), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(16, 8))
        self.validation_box = ctk.CTkTextbox(right_panel, wrap="word", height=280, fg_color=theme.BG_INPUT, corner_radius=theme.CARD_CORNER_RADIUS, font=theme.mono_font(12))
        self.validation_box.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        self._configure_validation_tags()
        self.validation_box.insert("1.0", "Run Test Configuration to validate your folder selections.")
        self.validation_box.configure(state="disabled")

        self.status_label = ctk.CTkLabel(container, textvariable=self.status_var, anchor="w", font=theme.body_font(12), text_color=theme.TEXT_SECONDARY)
        self.status_label.pack(fill="x", pady=(10, 8))

        button_row = ctk.CTkFrame(container, fg_color="transparent")
        button_row.pack(fill="x")

        ctk.CTkButton(button_row, text="\u2713  Test Configuration", command=self._test_configuration, **_OUTLINE_BUTTON).pack(side="left", padx=(0, 8))
        ctk.CTkButton(button_row, text="Save", command=self._save, **_PRIMARY_BUTTON).pack(side="left", padx=8)
        ctk.CTkButton(button_row, text="Reset to Default", command=self._reset_defaults, **_OUTLINE_BUTTON).pack(side="left", padx=8)
        ctk.CTkButton(button_row, text="Cancel", command=self._cancel, **_OUTLINE_BUTTON).pack(side="right")

    def _configure_validation_tags(self) -> None:
        try:
            self.validation_box.tag_configure("ok", foreground=theme.SUCCESS)
            self.validation_box.tag_configure("fail", foreground=theme.DANGER)
            self.validation_box.tag_configure("neutral", foreground=theme.TEXT_SECONDARY)
        except Exception:
            pass

    def _write_validation(self, lines: list[str]) -> None:
        self.validation_box.configure(state="normal")
        self.validation_box.delete("1.0", "end")
        self.validation_box.insert("1.0", "\n".join(lines))
        self.validation_box.configure(state="disabled")

    def _write_tagged_validation(self, tagged_lines: list[tuple[str, str]]) -> None:
        self.validation_box.configure(state="normal")
        self.validation_box.delete("1.0", "end")
        for text, tag in tagged_lines:
            self.validation_box.insert("end", text + "\n", tag)
        self.validation_box.configure(state="disabled")

    def _refresh_preview(self) -> None:
        save_folder = Path(self.save_folder_var.get()).expanduser()
        preview_lines = [
            (f"Current save folder: {save_folder}", "neutral"),
            (f"Current backup folder: {self.backup_folder_var.get()}", "neutral"),
        ]
        if save_folder.exists() and save_folder.is_dir():
            preview_lines.append((f"Folder modified: {format_datetime(self._folder_mtime(save_folder))}", "neutral"))
        self._write_tagged_validation(preview_lines)

    def _folder_mtime(self, folder_path: Path):
        return None if not folder_path.exists() else datetime.fromtimestamp(folder_path.stat().st_mtime)

    def _auto_detect(self) -> None:
        candidates = self.settings_manager.auto_detect_save_folders()
        if candidates:
            self.save_folder_var.set(str(candidates[0]))
            self.status_label.configure(text_color=theme.SUCCESS)
            self.status_var.set(f"Auto-detected {len(candidates)} candidate folder(s). Using the first result.")
        else:
            self.status_label.configure(text_color=theme.WARNING)
            self.status_var.set("No save folder candidates were found automatically.")
        self._refresh_preview()

    def _browse_save_folder(self) -> None:
        selected_folder = browse_for_directory("Select Repo Save Folder", self.save_folder_var.get())
        if selected_folder:
            self.save_folder_var.set(selected_folder)
            self.status_label.configure(text_color=theme.TEXT_SECONDARY)
            self.status_var.set("Save folder selected.")
            self._refresh_preview()
        else:
            self.status_var.set("No folder selected.")

    def _browse_backup_folder(self) -> None:
        selected_folder = browse_for_directory("Select Backup Folder", self.backup_folder_var.get())
        if selected_folder:
            self.backup_folder_var.set(selected_folder)
            self.status_label.configure(text_color=theme.TEXT_SECONDARY)
            self.status_var.set("Backup folder selected.")
            self._refresh_preview()
        else:
            self.status_var.set("No folder selected.")

    def _open_save_folder(self) -> None:
        # Normalize the path exactly like Dashboard does, then open it.
        from src.ui.dashboard import Dashboard

        folder = Path(self.save_folder_var.get()).expanduser()
        try:
            folder = folder.resolve()
        except Exception:
            # resolve() can fail for non-existing paths; keep expanded path.
            pass

        Dashboard._open_folder_in_file_manager(self, folder)

    def _open_backup_folder(self) -> None:
        from src.ui.dashboard import Dashboard

        folder = Path(self.backup_folder_var.get()).expanduser()
        try:
            folder = folder.resolve()
        except Exception:
            pass

        Dashboard._open_folder_in_file_manager(self, folder)



    def _test_configuration(self) -> None:
        validation = self.settings_manager.validate(self.save_folder_var.get(), self.backup_folder_var.get())
        self.result.validation = validation
        tagged_lines: list[tuple[str, str]] = []
        for message in validation.messages:
            is_error = message.startswith(_ERROR_PREFIXES)
            marker = "\u2715" if is_error else "\u2713"
            tagged_lines.append((f"{marker} {message}", "fail" if is_error else "ok"))
        if validation.is_valid:
            tagged_lines.append(("Configuration successful.", "ok"))
            self.status_label.configure(text_color=theme.SUCCESS)
            self.status_var.set("Configuration is valid and ready to save.")
        else:
            tagged_lines.append(("Configuration has issues that must be fixed before saving.", "fail"))
            self.status_label.configure(text_color=theme.DANGER)
            self.status_var.set("Configuration validation failed.")
        self._write_tagged_validation(tagged_lines)

    def _save(self) -> None:
        validation = self.settings_manager.validate(self.save_folder_var.get(), self.backup_folder_var.get())
        self.result.validation = validation
        if not validation.is_valid:
            self.status_label.configure(text_color=theme.DANGER)
            self.status_var.set("Cannot save until configuration checks pass.")
            tagged_lines = [("Configuration must be valid before saving.", "fail")]
            for message in validation.messages:
                is_error = message.startswith(_ERROR_PREFIXES)
                marker = "\u2715" if is_error else "\u2713"
                tagged_lines.append((f"{marker} {message}", "fail" if is_error else "ok"))
            self._write_tagged_validation(tagged_lines)
            return

        self.settings.save_folder = str(validation.save_folder)
        self.settings.backup_folder = str(validation.backup_folder)
        self.settings_manager.save(self.settings)
        self.result.settings = self.settings
        self.result.accepted = True
        self.status_label.configure(text_color=theme.SUCCESS)
        self.status_var.set("Settings saved successfully.")
        self.destroy()

    def _reset_defaults(self) -> None:
        self.settings = AppSettings.default()
        self.save_folder_var.set(self.settings.save_folder)
        self.backup_folder_var.set(self.settings.backup_folder)
        self.status_label.configure(text_color=theme.TEXT_SECONDARY)
        self.status_var.set("Restored default settings.")
        self._refresh_preview()

    def _cancel(self) -> None:
        self.result.accepted = False
        self.destroy()