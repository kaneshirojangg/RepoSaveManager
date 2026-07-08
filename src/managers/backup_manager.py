"""Folder-level backup creation, update, and metadata persistence."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models.save_model import SaveModel
from src.services.file_service import copy_folder_atomic, ensure_directory, folder_exists, remove_folder
from src.services.hash_service import build_save_fingerprint
from src.services.logger_service import get_logger
from src.utils.constants import DEFAULT_BACKUP_DATABASE_PATH


@dataclass(slots=True)
class BackupOperationResult:
    folder_id: str
    status: str
    backup_path: Path
    created_new: bool
    metadata: dict[str, Any]


class BackupManager:
    def __init__(
        self,
        backup_root: str | Path,
        database_path: Path = DEFAULT_BACKUP_DATABASE_PATH,
    ) -> None:
        self.backup_root = Path(backup_root).expanduser().resolve()
        self.database_path = database_path
        self.logger = get_logger(self.__class__.__name__)
        ensure_directory(self.backup_root)
        ensure_directory(self.database_path.parent)

    def load_records(self) -> dict[str, dict[str, Any]]:
        if not self.database_path.exists():
            return {}
        try:
            with self.database_path.open("r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
            if isinstance(payload, dict):
                return {key: value for key, value in payload.items() if isinstance(value, dict)}
        except (OSError, json.JSONDecodeError):
            self.logger.exception("Failed to load backup database: %s", self.database_path)
        return {}

    def save_records(self, records: dict[str, dict[str, Any]]) -> None:
        ensure_directory(self.database_path.parent)
        temporary_path = self.database_path.with_suffix(".json.tmp")
        with temporary_path.open("w", encoding="utf-8") as file_handle:
            json.dump(records, file_handle, indent=2, ensure_ascii=False)
        temporary_path.replace(self.database_path)

    def get_record(self, folder_id: str) -> dict[str, Any] | None:
        return self.load_records().get(folder_id)

    def has_backup(self, folder_id: str) -> bool:
        return self.get_record(folder_id) is not None and (self.backup_root / folder_id).exists()

    def create_or_update_backup(self, save_model: SaveModel) -> BackupOperationResult:
        live_folder = save_model.path
        if not folder_exists(live_folder):
            raise FileNotFoundError(f"Save folder does not exist: {live_folder}")

        live_fingerprint = build_save_fingerprint(live_folder, include_main_hash=True)
        records = self.load_records()
        existing_record = records.get(save_model.folder_id)
        backup_path = self.backup_root / save_model.folder_id
        created_new = existing_record is None or not folder_exists(backup_path)

        if existing_record:
            if self._record_matches_fingerprint(existing_record, live_fingerprint):
                self.logger.info("Backup already up to date for %s", save_model.folder_id)
                return BackupOperationResult(
                    folder_id=save_model.folder_id,
                    status="current",
                    backup_path=backup_path,
                    created_new=False,
                    metadata=existing_record,
                )

        copy_folder_atomic(live_folder, backup_path)
        metadata = self._build_record_payload(save_model, live_fingerprint, backup_path)
        records[save_model.folder_id] = metadata
        self.save_records(records)

        status = "created" if created_new else "updated"
        self.logger.info("Backup %s for %s", status, save_model.folder_id)
        return BackupOperationResult(
            folder_id=save_model.folder_id,
            status=status,
            backup_path=backup_path,
            created_new=created_new,
            metadata=metadata,
        )

    def delete_backup(self, folder_id: str) -> bool:
        records = self.load_records()
        backup_path = self.backup_root / folder_id
        removed = False

        if folder_exists(backup_path):
            remove_folder(backup_path)
            removed = True

        if folder_id in records:
            records.pop(folder_id, None)
            self.save_records(records)

        return removed

    def backup_exists(self, folder_id: str) -> bool:
        return self.has_backup(folder_id)

    def resolve_backup_path(self, folder_id: str) -> Path:
        return self.backup_root / folder_id

    def backup_is_current(self, folder_id: str, save_model: SaveModel) -> bool:
        record = self.get_record(folder_id)
        if record is None:
            return False
        live_fingerprint = build_save_fingerprint(save_model.path, include_main_hash=True)
        return self._record_matches_fingerprint(record, live_fingerprint)

    def _record_matches_fingerprint(self, record: dict[str, Any], fingerprint) -> bool:
        if int(record.get("main_file_size", -1)) != int(fingerprint.main_file_size or -1):
            return False
        record_mtime = str(record.get("main_file_mtime", ""))
        fingerprint_mtime = fingerprint.main_file_mtime.isoformat(timespec="seconds") if fingerprint.main_file_mtime else ""
        if record_mtime != fingerprint_mtime:
            return False
        if str(record.get("main_file_hash", "")) != str(fingerprint.main_file_hash or ""):
            return False
        return True

    def set_user_label(self, folder_id: str, label: str | None) -> None:
        """Persist a cosmetic label for folder_id into backup_database.json.

        Cosmetic-only: never touches the real save folder.
        """

        records = self.load_records()
        record = records.get(folder_id)

        normalized: str | None
        if label is None:
            normalized = None
        else:
            normalized = label.strip()
            if not normalized:
                normalized = None

        # Existing record: update only user_label (keep everything else).
        if record is not None:
            if normalized is None:
                # Keep convention with current writer: empty string.
                record["user_label"] = ""
            else:
                record["user_label"] = normalized
            records[folder_id] = record
            self.save_records(records)
            return

        # No record exists yet: create a minimal record.
        # Do not fabricate backup-specific fields.
        minimal: dict[str, Any] = {"folder_id": folder_id, "user_label": normalized or ""}
        records[folder_id] = minimal
        self.save_records(records)

    def _build_record_payload(
        self,
        save_model: SaveModel,
        fingerprint,
        backup_path: Path,
    ) -> dict[str, Any]:
        now = datetime.now().isoformat(timespec="seconds")
        return {
            "folder_id": save_model.folder_id,
            "original_path": str(save_model.path),
            "backup_path": str(backup_path),
            "created_at": save_model.parsed_timestamp.isoformat(timespec="seconds") if save_model.parsed_timestamp else now,
            "last_updated": now,
            "main_file_size": fingerprint.main_file_size or 0,
            "main_file_mtime": fingerprint.main_file_mtime.isoformat(timespec="seconds") if fingerprint.main_file_mtime else "",
            "main_file_hash": fingerprint.main_file_hash or "",
            "user_label": save_model.user_label or "",
            "status": "current",
        }

