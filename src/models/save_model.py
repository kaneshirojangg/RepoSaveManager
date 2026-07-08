"""Data model for a detected Repo save folder."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


FOLDER_ID_FORMAT = "REPO_SAVE_%Y_%m_%d_%H_%M_%S"


@dataclass(slots=True)
class SaveModel:
    folder_id: str
    path: Path
    folder_ctime: datetime
    size: int
    mtime: datetime
    main_file_hash: str | None = None
    has_backup: bool = False
    backup_timestamp: datetime | None = None
    user_label: str | None = None
    is_missing: bool = False
    is_selected: bool = field(default=False)

    @property
    def display_name(self) -> str:
        return self.user_label.strip() if self.user_label and self.user_label.strip() else self.folder_id

    @property
    def parsed_timestamp(self) -> datetime | None:
        try:
            return datetime.strptime(self.folder_id, FOLDER_ID_FORMAT)
        except ValueError:
            return None

    @property
    def backup_available(self) -> bool:
        return self.has_backup and self.backup_timestamp is not None

    @property
    def is_deleted(self) -> bool:
        return self.is_missing

    @property
    def identity_key(self) -> tuple[str, datetime, str | None]:
        return self.folder_id, self.folder_ctime, self.main_file_hash

    def matches_identity(self, other: "SaveModel") -> bool:
        if self.folder_id != other.folder_id:
            return False
        if self.folder_ctime != other.folder_ctime:
            return False
        if self.main_file_hash is not None and other.main_file_hash is not None:
            return self.main_file_hash == other.main_file_hash
        return True

    def select(self) -> None:
        self.is_selected = True

    def deselect(self) -> None:
        self.is_selected = False

    @classmethod
    def create(
        cls,
        *,
        path: Path,
        folder_ctime: datetime,
        size: int,
        mtime: datetime,
        main_file_hash: str | None = None,
        has_backup: bool = False,
        backup_timestamp: datetime | None = None,
        user_label: str | None = None,
        is_missing: bool = False,
        is_selected: bool = False,
    ) -> "SaveModel":
        return cls(
            folder_id=path.name,
            path=path,
            folder_ctime=folder_ctime,
            size=size,
            mtime=mtime,
            main_file_hash=main_file_hash,
            has_backup=has_backup,
            backup_timestamp=backup_timestamp,
            user_label=user_label,
            is_missing=is_missing,
            is_selected=is_selected,
        )
