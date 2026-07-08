"""Restore deleted saves from mirrored backups."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.managers.backup_manager import BackupManager
from src.services.file_service import copy_folder_atomic, folder_exists, remove_folder
from src.services.logger_service import get_logger


@dataclass(slots=True)
class RestoreOperationResult:
    folder_id: str
    restored: bool
    destination_path: Path


class RestoreManager:
    def __init__(self, backup_manager: BackupManager, save_root: str | Path) -> None:
        self.backup_manager = backup_manager
        self.save_root = Path(save_root).expanduser().resolve()
        self.logger = get_logger(self.__class__.__name__)

    def restore(self, folder_id: str) -> RestoreOperationResult:
        backup_path = self.backup_manager.resolve_backup_path(folder_id)
        destination_path = self.save_root / folder_id

        if not folder_exists(backup_path):
            raise FileNotFoundError(f"Backup folder does not exist: {backup_path}")

        if folder_exists(destination_path):
            remove_folder(destination_path)

        copy_folder_atomic(backup_path, destination_path)
        self.logger.info("Restored save %s to %s", folder_id, destination_path)
        return RestoreOperationResult(folder_id=folder_id, restored=True, destination_path=destination_path)

    def restore_from_record(self, folder_id: str) -> RestoreOperationResult:
        record = self.backup_manager.get_record(folder_id)
        if record is None:
            raise FileNotFoundError(f"No backup database record exists for {folder_id}")
        return self.restore(folder_id)
