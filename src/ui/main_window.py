"""Application window hosting the dashboard and startup flow."""

from __future__ import annotations

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - runtime fallback for environments without the dependency
    import tkinter as ctk  # type: ignore[no-redef]

    ctk.CTk = ctk.Tk  # type: ignore[attr-defined]
else:
    # Lock the whole app to the dark, orange-accented Repo look before any
    # widget is created. Safe to call once at import time.
    try:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
    except Exception:
        pass

from src.managers.backup_manager import BackupManager
from src.managers.monitor_manager import MonitorManager
from src.managers.restore_manager import RestoreManager
from src.managers.save_manager import SaveManager
from src.managers.settings_manager import AppSettings, SettingsManager
from src.ui.logo import load_window_icon
from src.ui.dashboard import Dashboard
from src.ui.settings_window import SettingsWindow
from src.ui import theme


class MainWindow(ctk.CTk):
    def __init__(self, settings_manager: SettingsManager | None = None) -> None:
        super().__init__()
        self.settings_manager = settings_manager or SettingsManager()
        self.settings = self.settings_manager.load()
        self.title("Repo Save Manager")
        self.geometry("1280x800")
        self.minsize(1024, 720)
        try:
            self.configure(fg_color=theme.BG_PRIMARY)
        except Exception:
            pass
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._window_icon = load_window_icon()
        try:
            self.iconphoto(True, self._window_icon)
        except Exception:
            pass
        self._build_dashboard()

    def _build_dashboard(self) -> None:
        for child in self.winfo_children():
            child.destroy()

        self.save_manager = SaveManager(self.settings_manager)
        self.backup_manager = BackupManager(self.settings.backup_folder)
        self.restore_manager = RestoreManager(self.backup_manager, self.settings.save_folder)
        self.monitor_manager = MonitorManager(self.save_manager, self.backup_manager, self.restore_manager)
        self.dashboard = Dashboard(
            self,
            settings_manager=self.settings_manager,
            save_manager=self.save_manager,
            backup_manager=self.backup_manager,
            restore_manager=self.restore_manager,
            monitor_manager=self.monitor_manager,
            on_open_settings=self.open_settings,
        )
        self.dashboard.update_clock()
        self._poll_monitor_events()

    def open_settings(self) -> None:
        window = SettingsWindow(self, self.settings_manager, on_save=self._apply_settings)
        self.wait_window(window)

    def _apply_settings(self, settings: AppSettings) -> None:
        self.settings = settings
        self.save_manager = SaveManager(self.settings_manager)
        self.backup_manager = BackupManager(self.settings.backup_folder)
        self.restore_manager = RestoreManager(self.backup_manager, self.settings.save_folder)
        self.monitor_manager.stop()
        self.monitor_manager = MonitorManager(self.save_manager, self.backup_manager, self.restore_manager)
        self.dashboard.settings_manager = self.settings_manager
        self.dashboard.save_manager = self.save_manager
        self.dashboard.backup_manager = self.backup_manager
        self.dashboard.restore_manager = self.restore_manager
        self.dashboard.monitor_manager = self.monitor_manager
        self.dashboard.refresh_saves(log_activity=True)
        self.dashboard.activity_log.append(self.dashboard._now_text(), "info", "Settings saved and dashboard refreshed.")

    def _poll_monitor_events(self) -> None:
        if hasattr(self, "dashboard") and self.dashboard.winfo_exists():
            self.dashboard.poll_monitor_events()
            self.after(250, self._poll_monitor_events)

    def close(self) -> None:
        if hasattr(self, "monitor_manager"):
            self.monitor_manager.stop()
        self.destroy()