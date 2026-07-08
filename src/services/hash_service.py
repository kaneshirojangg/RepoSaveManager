"""Hashing and save-folder fingerprint helpers."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


MAIN_SAVE_SUFFIX = ".es3"


@dataclass(frozen=True, slots=True)
class SaveFingerprint:
    folder_size: int
    folder_mtime: datetime
    folder_ctime: datetime
    main_file_hash: str | None
    main_file_size: int | None
    main_file_mtime: datetime | None


def get_main_save_file(folder_path: Path) -> Path | None:
    if not folder_path.exists() or not folder_path.is_dir():
        return None

    candidates = sorted(
        (path for path in folder_path.iterdir() if path.is_file() and path.suffix.lower() == MAIN_SAVE_SUFFIX),
        key=lambda path: (path.name.lower() != f"{folder_path.name}{MAIN_SAVE_SUFFIX}", path.name.lower()),
    )
    return candidates[0] if candidates else None


def sha256_file(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_folder_size(folder_path: Path) -> int:
    if not folder_path.exists() or not folder_path.is_dir():
        return 0

    total_size = 0
    for root, _, files in os.walk(folder_path):
        root_path = Path(root)
        for file_name in files:
            file_path = root_path / file_name
            try:
                total_size += file_path.stat().st_size
            except FileNotFoundError:
                continue
    return total_size


def get_folder_mtime(folder_path: Path) -> datetime:
    return datetime.fromtimestamp(folder_path.stat().st_mtime)


def get_folder_ctime(folder_path: Path) -> datetime:
    return datetime.fromtimestamp(folder_path.stat().st_ctime)


def get_main_file_metadata(folder_path: Path) -> tuple[int | None, datetime | None]:
    main_file = get_main_save_file(folder_path)
    if main_file is None:
        return None, None
    file_stat = main_file.stat()
    return file_stat.st_size, datetime.fromtimestamp(file_stat.st_mtime)


def hash_main_file(folder_path: Path) -> str | None:
    main_file = get_main_save_file(folder_path)
    if main_file is None:
        return None
    return sha256_file(main_file)


def build_save_fingerprint(folder_path: Path, include_main_hash: bool = True) -> SaveFingerprint:
    main_file_size, main_file_mtime = get_main_file_metadata(folder_path)
    return SaveFingerprint(
        folder_size=get_folder_size(folder_path),
        folder_mtime=get_folder_mtime(folder_path),
        folder_ctime=get_folder_ctime(folder_path),
        main_file_hash=hash_main_file(folder_path) if include_main_hash else None,
        main_file_size=main_file_size,
        main_file_mtime=main_file_mtime,
    )


def fingerprint_matches(
    current: SaveFingerprint,
    previous: SaveFingerprint,
    *,
    compare_hash: bool = True,
) -> bool:
    if current.folder_size != previous.folder_size:
        return False
    if current.folder_mtime != previous.folder_mtime:
        return False
    if current.folder_ctime != previous.folder_ctime:
        return False
    if compare_hash and current.main_file_hash != previous.main_file_hash:
        return False
    return True
