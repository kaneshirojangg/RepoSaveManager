"""Settings persistence, validation, and auto-detection logic."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from src.services.file_service import ensure_directory
from src.utils.constants import DEFAULT_BACKUP_DATABASE_PATH, DEFAULT_SAVE_FOLDER, DEFAULT_SETTINGS_PATH
from src.utils.helpers import has_read_access, has_write_access, is_repo_save_folder, normalize_path, safe_makedirs


@dataclass(slots=True)
class SettingsValidationResult:
    is_valid: bool
    messages: list[str] = field(default_factory=list)
    save_folder: Path | None = None
    backup_folder: Path | None = None


@dataclass(slots=True)
class AppSettings:
    save_folder: str
    backup_folder: str
    auto_start_monitoring: bool = False
    confirm_before_restore: bool = True
    confirm_before_delete: bool = True
    theme: str = "dark"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @classmethod
    def default(cls) -> "AppSettings":
        return cls(
            save_folder=str(DEFAULT_SAVE_FOLDER),
            backup_folder=str(DEFAULT_BACKUP_DATABASE_PATH.parent.parent / "backups"),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["save_folder"] = str(self.save_folder)
        payload["backup_folder"] = str(self.backup_folder)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AppSettings":
        default = cls.default()
        return cls(
            save_folder=str(payload.get("save_folder", default.save_folder)),
            backup_folder=str(payload.get("backup_folder", default.backup_folder)),
            auto_start_monitoring=bool(payload.get("auto_start_monitoring", default.auto_start_monitoring)),
            confirm_before_restore=bool(payload.get("confirm_before_restore", default.confirm_before_restore)),
            confirm_before_delete=bool(payload.get("confirm_before_delete", default.confirm_before_delete)),
            theme=str(payload.get("theme", default.theme)),
            created_at=str(payload.get("created_at", default.created_at)),
            updated_at=str(payload.get("updated_at", default.updated_at)),
        )


class SettingsManager:
    def __init__(self, settings_path: Path = DEFAULT_SETTINGS_PATH) -> None:
        self.settings_path = settings_path

        # Keep lightweight runtime diagnostics for configuration issues.
        # This helps verify that the checkbox state is actually persisted
        # and that subsequent app launches read from the same settings file.
        try:
            from src.services.logger_service import get_logger

            self._logger = get_logger(self.__class__.__name__)
        except Exception:  # pragma: no cover
            self._logger = None


    def load(self) -> AppSettings:
        if self._logger:
            self._logger.info("SettingsManager.load() using path: %s", self.settings_path)

        if not self.settings_path.exists():
            if self._logger:
                self._logger.info(
                    "Settings file missing (%s); using defaults. config_dir_exists=%s",
                    self.settings_path,
                    self.settings_path.parent.exists(),
                )
            return AppSettings.default()

        try:
            with self.settings_path.open("r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
            if not isinstance(payload, dict):
                if self._logger:
                    self._logger.warning(
                        "Settings payload is not a dict (%s); using defaults.",
                        type(payload),
                    )
                return AppSettings.default()
            settings = AppSettings.from_dict(payload)
            if self._logger:
                self._logger.info(
                    "Loaded settings from %s (auto_start_monitoring=%s).",
                    self.settings_path,
                    settings.auto_start_monitoring,
                )
            return settings
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            if self._logger:
                self._logger.warning(
                    "Failed to load settings from %s (%s); using defaults.",
                    self.settings_path,
                    exc,
                )
            return AppSettings.default()


    def save(self, settings: AppSettings) -> None:
        settings_dir = self.settings_path.parent
        if self._logger:
            self._logger.info(
                "SettingsManager.save() target=%s (dir_exists=%s, dir_writable=%s)",
                self.settings_path,
                settings_dir.exists(),
                (has_write_access(settings_dir) if settings_dir.exists() else None),
            )

        try:
            ensure_directory(settings_dir)
        except Exception as exc:
            if self._logger:
                self._logger.exception(
                    "Failed to ensure settings directory %s before saving (%s)",
                    settings_dir,
                    exc,
                )
            raise

        settings.updated_at = datetime.now().isoformat(timespec="seconds")

        if self._logger:
            self._logger.info(
                "Saving settings to %s (auto_start_monitoring=%s).",
                self.settings_path,
                settings.auto_start_monitoring,
            )

        try:
            with self.settings_path.open("w", encoding="utf-8") as file_handle:
                json.dump(settings.to_dict(), file_handle, indent=2, ensure_ascii=False)
                file_handle.flush()
                try:
                    os.fsync(file_handle.fileno())
                except Exception:
                    # fsync can fail on some platforms/filesystems; flush is best-effort.
                    pass
        except Exception as exc:
            if self._logger:
                self._logger.exception("Failed writing settings to %s (%s)", self.settings_path, exc)
            raise

        # Sanity check: reload from disk to ensure persistence worked in this runtime.
        try:
            reloaded = self.load()
            if self._logger:
                self._logger.info(
                    "Settings reload verification from %s (auto_start_monitoring=%s).",
                    self.settings_path,
                    reloaded.auto_start_monitoring,
                )
        except Exception as exc:
            if self._logger:
                self._logger.warning(
                    "Settings reload verification failed for %s (%s).",
                    self.settings_path,
                    exc,
                )

        if self._logger:
            self._logger.info(
                "Settings saved successfully to %s (size_bytes=%s).",
                self.settings_path,
                self.settings_path.stat().st_size if self.settings_path.exists() else None,
            )




    def is_config_present_and_valid(self) -> bool:
        settings = self.load()
        result = self.validate(settings.save_folder, settings.backup_folder, create_backup_folder=False)
        return result.is_valid

    def validate(
        self,
        save_folder: str | Path,
        backup_folder: str | Path,
        *,
        create_backup_folder: bool = True,
    ) -> SettingsValidationResult:
        messages: list[str] = []
        save_path = normalize_path(save_folder)
        backup_path = normalize_path(backup_folder)

        if not save_path.exists() or not save_path.is_dir():
            messages.append(f"Save folder does not exist: {save_path}")
        else:
            save_subfolders = [entry for entry in save_path.iterdir() if entry.is_dir() and is_repo_save_folder(entry.name)]
            if save_subfolders:
                messages.append("Repo save folder detected")
                messages.append(f"{len(save_subfolders)} save folder(s) detected")
            else:
                messages.append(f"No REPO_SAVE_* folders found in {save_path}")

            if has_read_access(save_path):
                messages.append("Read permission confirmed")
            else:
                messages.append(f"Read permission denied for {save_path}")

        if not backup_path.exists():
            if create_backup_folder and safe_makedirs(backup_path):
                messages.append("Backup folder created")
            elif create_backup_folder:
                messages.append(f"Unable to create backup folder: {backup_path}")
            else:
                messages.append(f"Backup folder does not exist: {backup_path}")

        if backup_path.exists() and has_write_access(backup_path):
            messages.append("Write permission confirmed")
            messages.append("Backup folder accessible")
        elif backup_path.exists():
            messages.append(f"Write permission denied for {backup_path}")

        is_valid = not any(
            message.startswith(prefix)
            for message in messages
            for prefix in (
                "Save folder does not exist:",
                "No REPO_SAVE_* folders found",
                "Read permission denied",
                "Unable to create backup folder:",
                "Backup folder does not exist:",
                "Write permission denied",
            )
        )

        return SettingsValidationResult(
            is_valid=is_valid,
            messages=messages,
            save_folder=save_path,
            backup_folder=backup_path,
        )

    def auto_detect_save_folders(self) -> list[Path]:
        candidates: list[Path] = []
        default_candidate = DEFAULT_SAVE_FOLDER
        if default_candidate.exists():
            candidates.append(default_candidate)

        search_roots = self._candidate_search_roots()
        seen: set[Path] = set(candidates)
        for root in search_roots:
            if not root.exists():
                continue
            for path in root.rglob("saves"):
                candidate = path
                if candidate in seen or not candidate.is_dir():
                    continue
                if self._contains_repo_save_folder(candidate):
                    candidates.append(candidate)
                    seen.add(candidate)
        return candidates

    def _candidate_search_roots(self) -> list[Path]:
        """Return roots that may contain the R.E.P.O. saves folder.

        The app supports:
        - Native Windows: %USERPROFILE%/AppData/LocalLow/semiwork/Repo/saves
        - Linux running the Windows version via Steam Proton:
          - ~/.local/share/Steam/steamapps/compatdata/<appid>/pfx/drive_c/users/*/AppData/LocalLow/semiwork/Repo/saves
          - ~/.steam/steam/steamapps/compatdata/<appid>/pfx/drive_c/users/*/AppData/LocalLow/semiwork/Repo/saves

        Auto-detection is intentionally conservative: it searches only plausible
        roots and then validates each candidate by checking for REPO_SAVE_* subfolders.
        """

        home = Path.home()

        # Windows-like (for native Windows, or Wine-like environments)
        win_like_roots = [
            home / "AppData" / "LocalLow",
            home / "AppData" / "Roaming" / "Steam" / "userdata",
        ]


        # Proton/Steam prefix roots (Linux)
        steam_roots = [
            home / ".local" / "share" / "Steam",
            home / ".steam" / "steam",
            home / ".steam",
        ]

        # The rglob("saves") logic below needs roots that are allowed to contain
        # a terminal "saves" directory somewhere in their subtree.
        proton_roots: list[Path] = []
        for steam_root in steam_roots:
            proton_roots.extend(
                [
                    steam_root / "steamapps" / "compatdata",
                    steam_root / "steamapps" / "compatdata" / "*" / "pfx" / "drive_c" / "users",
                ]
            )

        # A couple of additional common desktop locations where users may have
        # copied/mounted the save folder.
        other_roots = [
            home / "Documents",
        ]

        # De-dup while preserving order.
        seen: set[Path] = set()
        out: list[Path] = []
        for p in (*win_like_roots, *proton_roots, *other_roots):
            if p not in seen:
                seen.add(p)
                out.append(p)
        return out

    def _direct_proton_candidates(self) -> list[Path]:
        """Build explicit candidates for the known Proton save layout."""
        home = Path.home()
        steam_roots = [
            home / ".local" / "share" / "Steam",
            home / ".steam" / "steam",
            home / ".steam",
        ]

        appid = "3241660"  # R.E.P.O.
        candidates: list[Path] = []

        for steam_root in steam_roots:
            base = steam_root / "steamapps" / "compatdata" / appid / "pfx" / "drive_c" / "users"
            # Typical user is "steamuser", but we also support any proton user folder.
            if not base.exists():
                continue
            candidates.extend(list(base.glob("steamuser/AppData/LocalLow/semiwork/Repo/saves")))
            candidates.extend(list(base.glob("*/AppData/LocalLow/semiwork/Repo/saves")))

        return candidates

    def _direct_windows_candidates(self) -> list[Path]:
        """Build explicit candidates for native Windows save layout."""
        home = Path.home()
        candidates: list[Path] = []

        # Native Windows layout (also works in some Wine-like environments)
        # %USERPROFILE%\AppData\LocalLow\semiwork\Repo\saves
        candidates.append(home / "AppData" / "LocalLow" / "semiwork" / "Repo" / "saves")

        # In case USERPROFILE isn't what we expect, also try common env var patterns
        userprofile = os.environ.get("USERPROFILE")
        if userprofile:
            candidates.append(Path(userprofile) / "AppData" / "LocalLow" / "semiwork" / "Repo" / "saves")

        return candidates


    def _candidate_search_paths(self) -> list[Path]:
        # Used by auto_detect_save_folders() to combine explicit candidates
        # with broader subtree search.
        candidates = self._direct_proton_candidates()
        candidates.extend(self._candidate_search_roots())
        # De-dup preserve order
        seen: set[Path] = set()
        out: list[Path] = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                out.append(c)
        return out

    def auto_detect_save_folders(self) -> list[Path]:
        """Auto-detect R.E.P.O. save folder candidates.

        Required behavior (per Auto-Detect button):
        1) Detect the operating system.
        2) Check the default save locations for that OS.
        3) Verify the folder exists.
        4) Only return valid candidates (caller can prompt user if empty).

        The app detects the OS and then searches OS-appropriate default roots:
        - Windows: AppData/LocalLow/semiwork/Repo/saves
        - Linux/macOS: Proton/Wine prefix layout that contains
          .../steamapps/compatdata/<appid>/pfx/drive_c/users/*/AppData/LocalLow/semiwork/Repo/saves

        Steam is assumed to use a Windows-like directory layout inside Proton
        (most common across distributions).
        """

        candidates: list[Path] = []

        # 1) OS-aware default location checks
        if os.name == "nt":
            # Windows native layout (fast path)
            for p in self._direct_windows_candidates():
                if p.exists() and p.is_dir() and p not in candidates and self._contains_repo_save_folder(p):
                    candidates.append(p)
        else:
            # Linux/macOS: Proton/Wine layout (fast path)
            for p in self._direct_proton_candidates():
                if p.exists() and p.is_dir() and p not in candidates and self._contains_repo_save_folder(p):
                    candidates.append(p)

            # Also check the shipped default save folder (windows-like), in
            # case Proton prefixes were not used and the user mounted/copies
            # the saves directly.
            default_candidate = DEFAULT_SAVE_FOLDER
            if (
                default_candidate.exists()
                and default_candidate.is_dir()
                and default_candidate not in candidates
                and self._contains_repo_save_folder(default_candidate)
            ):
                candidates.append(default_candidate)

        # 2) If nothing found, do a conservative fallback scan under known roots.
        # This keeps detection robust across different Steam/Proton variants.
        if not candidates:
            for root in self._candidate_search_roots():
                if not root.exists():
                    continue
                try:
                    for path in root.rglob("saves"):
                        candidate = path
                        if candidate in candidates or not candidate.is_dir():
                            continue
                        if self._contains_repo_save_folder(candidate):
                            candidates.append(candidate)
                except OSError:
                    continue

        return candidates



    def _contains_repo_save_folder(self, folder_path: Path) -> bool:
        try:
            return any(entry.is_dir() and is_repo_save_folder(entry.name) for entry in folder_path.iterdir())
        except OSError:
            return False
