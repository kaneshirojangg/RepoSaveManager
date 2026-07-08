"""Application entrypoint for Repo Save Manager."""

from __future__ import annotations

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - runtime fallback for environments without the dependency
    import tkinter as ctk  # type: ignore[no-redef]

    ctk.CTk = ctk.Tk  # type: ignore[attr-defined]
    ctk.CTkFrame = ctk.Frame  # type: ignore[attr-defined]
    ctk.CTkLabel = ctk.Label  # type: ignore[attr-defined]

from src.managers.settings_manager import SettingsManager
from src.ui.main_window import MainWindow
from src.ui.setup_wizard import SetupWizard
from src.utils.helpers import open_folder_in_file_manager


class RepoSaveManagerApp:
    def __init__(self) -> None:
        self.settings_manager = SettingsManager()
        self.main_window: MainWindow | None = None

    def launch(self) -> MainWindow | None:
        if self.settings_manager.is_config_present_and_valid():
            self.main_window = MainWindow(self.settings_manager)
            return self.main_window

        launcher_root = ctk.CTk()
        launcher_root.withdraw()
        wizard = SetupWizard(launcher_root, self.settings_manager)
        launcher_root.wait_window(wizard)
        if wizard.result.accepted:
            launcher_root.destroy()
            self.main_window = MainWindow(self.settings_manager)
            return self.main_window

        launcher_root.destroy()
        return None


def main() -> None:
    app = RepoSaveManagerApp()
    main_window = app.launch()
    if main_window is None:
        return
    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        main_window.destroy()


if __name__ == "__main__":
    main()
