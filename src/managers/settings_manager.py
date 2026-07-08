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

    def load(self) -> AppSettings:
        if not self.settings_path.exists():
            return AppSettings.default()

        try:
            with self.settings_path.open("r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
            if not isinstance(payload, dict):
                return AppSettings.default()
            return AppSettings.from_dict(payload)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return AppSettings.default()

    def save(self, settings: AppSettings) -> None:
        ensure_directory(self.settings_path.parent)
        settings.updated_at = datetime.now().isoformat(timespec="seconds")
        with self.settings_path.open("w", encoding="utf-8") as file_handle:
            json.dump(settings.to_dict(), file_handle, indent=2, ensure_ascii=False)

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
        home = Path.home()
        return [
            home / "AppData" / "LocalLow",
            home / "AppData",
            home / "Documents",
            home / "AppData" / "Roaming" / "Steam" / "userdata",
        ]

    def _contains_repo_save_folder(self, folder_path: Path) -> bool:
        try:
            return any(entry.is_dir() and is_repo_save_folder(entry.name) for entry in folder_path.iterdir())
        except OSError:
            return False
