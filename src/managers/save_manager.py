"""Discovery and selection logic for Repo save folders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.managers.settings_manager import AppSettings, SettingsManager
from src.models.save_model import SaveModel
from src.services.hash_service import build_save_fingerprint, fingerprint_matches, get_main_file_metadata, hash_main_file
from src.services.logger_service import get_logger
from src.utils.helpers import is_repo_save_folder


@dataclass(slots=True)
class SaveSelectionResult:
    selected_save: SaveModel | None
    all_saves: list[SaveModel]


class SaveManager:
    def __init__(self, settings_manager: SettingsManager | None = None) -> None:
        self.settings_manager = settings_manager or SettingsManager()
        self.logger = get_logger(self.__class__.__name__)

    def discover_saves(self, save_root: str | Path, backup_manager: object | None = None) -> list[SaveModel]:
        root_path = Path(save_root).expanduser().resolve()
        saves: list[SaveModel] = []

        if not root_path.exists() or not root_path.is_dir():
            self.logger.warning("Save root does not exist: %s", root_path)
            return saves

        backup_lookup = self._build_backup_lookup(backup_manager)
        discovered_folder_ids: set[str] = set()

        for folder_path in sorted((path for path in root_path.iterdir() if path.is_dir() and is_repo_save_folder(path.name)), key=lambda path: path.name):
            saves.append(self._build_save_model(folder_path, backup_lookup.get(folder_path.name)))
            discovered_folder_ids.add(folder_path.name)

        for folder_id, backup_record in sorted(backup_lookup.items()):
            if folder_id in discovered_folder_ids:
                continue
            saves.append(self._build_missing_save_model(root_path, folder_id, backup_record))

        return saves

    def discover_from_settings(self, backup_manager: object | None = None) -> list[SaveModel]:
        settings = self.settings_manager.load()
        return self.discover_saves(settings.save_folder, backup_manager=backup_manager)

    def select_save(self, saves: list[SaveModel], folder_id: str) -> SaveSelectionResult:
        selected_save: SaveModel | None = None
        for save in saves:
            if save.folder_id == folder_id:
                save.select()
                selected_save = save
            else:
                save.deselect()
        return SaveSelectionResult(selected_save=selected_save, all_saves=saves)

    def get_save_by_folder_id(self, saves: list[SaveModel], folder_id: str) -> SaveModel | None:
        for save in saves:
            if save.folder_id == folder_id:
                return save
        return None

    def compare_save_identity(self, first_save: SaveModel, second_save: SaveModel) -> bool:
        if first_save.folder_id != second_save.folder_id:
            return False
        if first_save.folder_ctime != second_save.folder_ctime:
            return False
        if first_save.main_file_hash is None or second_save.main_file_hash is None:
            return True
        return first_save.main_file_hash == second_save.main_file_hash

    def refresh_save(self, save: SaveModel) -> SaveModel:
        fingerprint = build_save_fingerprint(save.path, include_main_hash=True)
        main_file_hash = fingerprint.main_file_hash
        main_file_size, _ = get_main_file_metadata(save.path)
        save.size = fingerprint.folder_size
        save.mtime = fingerprint.folder_mtime
        save.folder_ctime = fingerprint.folder_ctime
        save.main_file_hash = main_file_hash or hash_main_file(save.path)
        if main_file_size is not None:
            self.logger.debug("Refreshed save %s main file size %s", save.folder_id, main_file_size)
        return save

    def _build_save_model(self, folder_path: Path, backup_record: dict[str, object] | None) -> SaveModel:
        fingerprint = build_save_fingerprint(folder_path, include_main_hash=True)
        user_label = None
        backup_timestamp = None
        has_backup = False

        if backup_record:
            user_label = str(backup_record.get("user_label") or "").strip() or None
            has_backup = True
            backup_timestamp_value = backup_record.get("last_updated") or backup_record.get("created_at")
            if isinstance(backup_timestamp_value, str):
                try:
                    backup_timestamp = datetime.fromisoformat(backup_timestamp_value)
                except ValueError:
                    backup_timestamp = None

        return SaveModel.create(
            path=folder_path,
            folder_ctime=fingerprint.folder_ctime,
            size=fingerprint.folder_size,
            mtime=fingerprint.folder_mtime,
            main_file_hash=fingerprint.main_file_hash,
            has_backup=has_backup,
            backup_timestamp=backup_timestamp,
            user_label=user_label,
        )

    def _build_missing_save_model(self, save_root: Path, folder_id: str, backup_record: dict[str, object]) -> SaveModel:
        backup_timestamp = None
        backup_timestamp_value = backup_record.get("last_updated") or backup_record.get("created_at")
        if isinstance(backup_timestamp_value, str):
            try:
                backup_timestamp = datetime.fromisoformat(backup_timestamp_value)
            except ValueError:
                backup_timestamp = None

        folder_ctime = backup_timestamp or datetime.now()
        mtime = backup_timestamp or folder_ctime
        user_label = str(backup_record.get("user_label") or "").strip() or None
        main_file_hash = str(backup_record.get("main_file_hash") or "").strip() or None

        return SaveModel.create(
            path=save_root / folder_id,
            folder_ctime=folder_ctime,
            size=0,
            mtime=mtime,
            main_file_hash=main_file_hash,
            has_backup=True,
            backup_timestamp=backup_timestamp,
            user_label=user_label,
            is_missing=True,
        )

    def _build_backup_lookup(self, backup_manager: object | None) -> dict[str, dict[str, object]]:
        if backup_manager is None:
            return {}
        load_records = getattr(backup_manager, "load_records", None)
        if not callable(load_records):
            return {}
        records = load_records()
        if not isinstance(records, dict):
            return {}
        return records
